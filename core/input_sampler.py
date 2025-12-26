# =============================================================================
# INPUT SAMPLER - Mostreig asíncron d'inputs amb buffer
# =============================================================================
import time


class InputSampler:
    """
    Mostreig asíncron d'inputs analògics amb buffer.
    
    Redueix lectures ADC de ~1500/s a 100/s per millorar estabilitat del clock.
    Els valors es guarden en un buffer i es retornen instantàniament sense ADC.
    """
    
    def __init__(self, hardware, config):
        """
        Inicialitza el sampler amb referències al hardware i configuració.
        
        Args:
            hardware: Instància de TeclaHardware
            config: Mòdul de configuració global
        """
        self.hw = hardware
        self.cfg = config
        
        # Buffer d'inputs (valors calibrats i llestos per usar)
        self.x_buffered = 0.0  # CV1 (pote) - calibrat
        self.y_buffered = 0.0  # CV2 (LDR) - calibrat
        self.z_buffered = 0.0  # Slider (BPM) - NO calibrat (sempre 0-3.3V)
        
        # Control temporal
        self.last_sample_time = 0.0
        self.sample_interval = 0.010  # 10ms = 100Hz (vs ~500-1000Hz abans)
        
        # Fer primera lectura immediata per evitar valors 0
        self._read_adc_values()
    
    def _read_adc_values(self):
        """
        Llegeix valors dels ADCs i actualitza el buffer.
        PRIVAT: Només cridat internament per update().
        
        IMPORTANT: Els valors CV1 i CV2 es CLAMPEN (limiten) al rang calibrat.
        Cada mode després farà la seva pròpia normalització amb normalize().
        """
        # Lectura raw dels 3 ADCs
        z_raw = self.hw.get_voltage(self.hw.slider)      # Slider GP28 - BPM
        x_raw = self.hw.get_voltage(self.hw.cv1_pote)    # CV1 GP26
        y_raw = self.hw.get_voltage(self.hw.cv2_ldr)     # CV2 GP27
        
        # CLAMPAR CV1 i CV2 al rang calibrat (no normalitzar!)
        # Els modes després faran normalize(x, cv1_min, cv1_max) ells mateixos
        x_clamped = max(self.cfg.cv1_min, min(self.cfg.cv1_max, x_raw))
        y_clamped = max(self.cfg.cv2_min, min(self.cfg.cv2_max, y_raw))
        
        # Guardar al buffer (ATÒMIC: assignació simple)
        self.x_buffered = x_clamped
        self.y_buffered = y_clamped
        self.z_buffered = z_raw  # Slider no es calibra
    
    def update(self, current_time):
        """
        Actualitza el buffer si ha passat l'interval de mostreig.
        
        Args:
            current_time: Temps actual (time.monotonic())
        
        Returns:
            True si s'ha fet lectura ADC, False altrament
        """
        if current_time - self.last_sample_time >= self.sample_interval:
            self._read_adc_values()
            self.last_sample_time = current_time
            return True
        
        return False
    
    def get_inputs(self):
        """
        Retorna els valors buffered (INSTANT, sense ADC).
        
        Returns:
            Tuple (x, y, z) amb valors calibrats (x, y) i raw (z)
        """
        return self.x_buffered, self.y_buffered, self.z_buffered
    
    def force_update(self):
        """
        Força una lectura ADC immediata (per inicialització o casos especials).
        """
        self._read_adc_values()
        self.last_sample_time = time.monotonic()
