# =============================================================================
# CONFIGURACIÓ DE HARDWARE - TECLA
# =============================================================================
import board
import busio
import digitalio
import analogio
import pwmio
import usb_midi
from adafruit_midi import MIDI
from adafruit_ssd1306 import SSD1306_I2C

class TeclaHardware:
    """Gestió centralitzada de tot el hardware del TECLA"""
    
    def __init__(self):
        # MIDI
        self.midi = MIDI(midi_out=usb_midi.ports[1], out_channel=0)
        
        # PWM outputs - PWM1 i PWM3 invertits
        self.pwm1 = pwmio.PWMOut(board.GP22, frequency=440, duty_cycle=80, variable_frequency=True)  # Era GP0
        self.pwm2 = pwmio.PWMOut(board.GP2, frequency=440, duty_cycle=80, variable_frequency=True)   # No canvia
        self.pwm3 = pwmio.PWMOut(board.GP0, frequency=440, duty_cycle=80, variable_frequency=True)   # Era GP22
        
        # Jack output
        self.out_jack = digitalio.DigitalInOut(board.GP1)
        self.out_jack.direction = digitalio.Direction.OUTPUT
        self.out_jack.value = False
        
        # Buttons
        self._setup_buttons()
        
        # Potenciòmetres
        self._setup_pots()
        
        # LEDs
        self._setup_leds()
        
        # Display OLED
        self._setup_display()
    
    def _setup_buttons(self):
        """Configurar botons de control"""
        self.boton_crueta_1 = self._create_button(board.GP13)
        self.boton_crueta_2 = self._create_button(board.GP14)
        self.boton_crueta_3 = self._create_button(board.GP15)
        self.boton_crueta_4 = self._create_button(board.GP3)
        self.boton_extra_1 = self._create_button(board.GP5)
        self.boton_extra_2 = self._create_button(board.GP4)
        
        self.buttons = [
            self.boton_crueta_1, self.boton_crueta_2, self.boton_crueta_3,
            self.boton_crueta_4, self.boton_extra_1, self.boton_extra_2
        ]
    
    def _create_button(self, pin):
        """Crear botó amb pull-down"""
        btn = digitalio.DigitalInOut(pin)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.DOWN
        return btn
    
    def _setup_pots(self):
        """Configurar potenciòmetres amb mapatge correcte"""
        self.slider = analogio.AnalogIn(board.GP28)      # Slider: GP28 (velocitat/BPM)
        self.cv1_pote = analogio.AnalogIn(board.GP26)    # CV1 Pote: GP26 (paràmetre 1, calibrable)
        self.cv2_ldr = analogio.AnalogIn(board.GP27)     # CV2 LDR: GP27 (paràmetre 2, calibrable)
        
        # Noms legacy per compatibilitat (DEPRECATED - usar slider, cv1_pote, cv2_ldr)
        self.pote_velocidad = self.slider
        self.pote_analog_1 = self.cv1_pote  
        self.pote_analog_2 = self.cv2_ldr
        
        self.potes = [self.cv1_pote, self.cv2_ldr, self.slider]
    
    def _setup_leds(self):
        """Configurar LEDs indicadors"""
        led_pins = [board.GP10, board.GP6, board.GP8, board.GP9, 
                    board.GP7, board.GP11, board.GP12]
        
        self.leds = []
        for pin in led_pins:
            led = digitalio.DigitalInOut(pin)
            led.direction = digitalio.Direction.OUTPUT
            led.value = False
            self.leds.append(led)
        
        # Referències individuals per accessibilitat
        self.led_1, self.led_2, self.led_3, self.led_4 = self.leds[0:4]
        self.led_5, self.led_6, self.led_7 = self.leds[4:7]
    
    def _setup_display(self):
        """Configurar pantalla OLED"""
        i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
        self.display = SSD1306_I2C(128, 64, i2c, addr=0x3C)
        self.display.fill(0)
        self.display.show()
    
    def get_voltage(self, pin):
        """Llegir voltatge d'un pin analògic (0-3.3V)"""
        return (pin.value * 3.3) / 65536
    
    def all_leds_off(self):
        """Apaga tots els LEDs"""
        for led in self.leds:
            led.value = False
    
    def update_config_led_indicators(self, cfg):
        """
        Sistema de LEDs de configuració:
        - LED2 (GP6) EXCLUSIU per Gate - NO s'usa per configs
        - configout=0 (Mode): Cap LED encès
        - configout=1 (Duty1): LED3 encès
        - configout=2 (Duty2): LED4 encès
        - configout=3 (Duty3): LED5 encès
        - configout=4 (H1): LED6 encès
        - configout=5 (H2): LED7 encès
        - configout=6 (H3): LED1 encès
        """
        # Apagar tots primer (excepte LED2 si gate actiu)
        for i, led in enumerate(self.leds):
            if i != 1:  # No tocar LED2 (índex 1)
                led.value = False
        
        # Encendre el LED corresponent al configout actual
        if cfg.configout == 0:  # Mode - Cap LED
            pass  # Tots apagats
        elif cfg.configout == 1:  # Duty1
            self.led_3.value = True
        elif cfg.configout == 2:  # Duty2
            self.led_4.value = True
        elif cfg.configout == 3:  # Duty3
            self.led_5.value = True
        elif cfg.configout == 4:  # Harmònic 1
            self.led_6.value = True
        elif cfg.configout == 5:  # Harmònic 2
            self.led_7.value = True
        elif cfg.configout == 6:  # Harmònic 3
            self.led_1.value = True
        
        # LED2 SEMPRE controlat exclusivament pel gate (no es toca aquí)
        # El gate s'actualitza automàticament via RTOS i midi_handler
    
    def update_dynamic_leds(self, cfg, current_time):
        """Sistema d'animació de LEDs DESACTIVAT per estabilitat.
        
        Només LED2 (gate) està actiu - controlat per rtos.py i midi_handler.py
        Els altres LEDs es gestionen únicament per update_config_led_indicators()
        """
        # Mantenir tots els LEDs apagats excepte els de configuració
        # Eliminem animacions, pulsos i càlculs complexos per millorar rendiment
        pass
    
    def led_idle_animation(self, step):
        """
        Animació idle per mode stop - Knight Rider
        step: comptador d'animació (0-11)
        LED2 NO s'inclou (exclusiu per gate)
        """
        # Apagar LEDs (excepte LED2)
        for i, led in enumerate(self.leds):
            if i != 1:  # Preservar LED2
                led.value = False
        
        # Knight Rider: LED va i ve (sense LED2)
        sequence = [0, 2, 3, 4, 5, 6, 5, 4, 3, 2]  # Salta LED2 (índex 1)
        if step < len(sequence):
            self.leds[sequence[step]].value = True
    
    def led_startup_animation(self):
        """Animació d'inici del sistema"""
        import time
        
        # Seqüència 1: Tots els LEDs en cascada (endavant)
        for led in self.leds:
            led.value = True
            time.sleep(0.08)
        
        time.sleep(0.15)
        
        # Seqüència 2: Apagar en cascada (enrere)
        for led in reversed(self.leds):
            led.value = False
            time.sleep(0.08)
        
        time.sleep(0.1)
        
        # Seqüència 3: Flash tots 2 vegades
        for _ in range(2):
            self.all_leds_on()
            time.sleep(0.1)
            self.all_leds_off()
            time.sleep(0.1)
    
    def update_config_indicators(self, cfg):
        """Actualitza LEDs que indiquen paràmetres actius"""
        self.led_5.value = (cfg.duty1 != 50 or cfg.duty2 != 50 or cfg.duty3 != 50)
        self.led_1.value = (cfg.freqharm1 != 0)
        self.led_4.value = (cfg.freqharm2 != 0)
    
    def update_loop_mode_indicators(self, cfg):
        """Actualitza LEDs 6, 3, 7 per mostrar loop_mode en binari"""
        mode = cfg.loop_mode
        
        # MODE 0: LEDs ALEATORIS cada 0.5s
        if mode == 0:
            import time
            import random
            # Seed basat en temps (canvia cada 0.5s)
            seed = int(time.monotonic() / 0.5)
            random.seed(seed)
            
            # Tirar dau per cada LED (7 LEDs)
            # LEDs: led_1(GP10), led_2(GP6), led_3(GP8), led_4(GP9), led_5(GP7), led_6(GP11), led_7(GP12)
            self.led_1.value = (random.randint(0, 1) == 1)
            self.led_2.value = (random.randint(0, 1) == 1)
            self.led_3.value = (random.randint(0, 1) == 1)
            self.led_4.value = (random.randint(0, 1) == 1)
            self.led_5.value = (random.randint(0, 1) == 1)
            self.led_6.value = (random.randint(0, 1) == 1)
            self.led_7.value = (random.randint(0, 1) == 1)
            return
        
        # ALTRES MODES: Patró binari normal
        patterns = {
            1: (False, False, True),   # Fractal
            2: (False, True, False),   # Riu
            3: (False, True, True),    # Tempesta
            4: (True, False, False),   # Harmonia
            5: (True, False, True),    # Bosc
            6: (True, True, False),    # Escala CV
            7: (True, True, True),     # Euclidia
            8: (False, False, False),  # Cosmos (final)
        }

        if mode not in patterns:
            mode = 0

        led6, led3, led7 = patterns.get(mode, (False, False, False))
        self.led_6.value = led6
        self.led_3.value = led3
        self.led_7.value = led7
    
    def display_configuration_mode(self, cfg):
        """Mostra el valor del paràmetre configurat en LEDs 6, 3, 7"""
        if cfg.configout == 0:
            # Loop mode (0-14)
            self._display_value(cfg.loop_mode, 14)
        elif cfg.configout == 1:
            # Duty1 (1-99)
            self._display_value(cfg.duty1, 99)
        elif cfg.configout == 2:
            # Duty2 (1-99)
            self._display_value(cfg.duty2, 99)
        elif cfg.configout == 3:
            # Duty3 (1-99)
            self._display_value(cfg.duty3, 99)
        elif cfg.configout == 4:
            # Harmonic base (0-12)
            self._display_value(cfg.freqharm_base, 12)
        elif cfg.configout == 5:
            # Harmonic1 (0-12)
            self._display_value(cfg.freqharm1, 12)
        elif cfg.configout == 6:
            # Harmonic2 (0-12)
            self._display_value(cfg.freqharm2, 12)
    
    def _display_value(self, value, max_value):
        """Mostra un valor normalitzat en LEDs 6, 3, 7 (binari 0-7)"""
        normalized = int((value / max_value) * 7)
        self.led_6.value = (normalized & 4) != 0  # Bit 2
        self.led_3.value = (normalized & 2) != 0  # Bit 1
        self.led_7.value = (normalized & 1) != 0  # Bit 0
    
    def all_leds_on(self):
        """Encendre tots els LEDs"""
        for led in self.leds:
            led.value = True

# Instància singleton (opcional, per accés global)
_hardware_instance = None

def get_hardware():
    """Obté la instància singleton del hardware"""
    global _hardware_instance
    if _hardware_instance is None:
        _hardware_instance = TeclaHardware()
    return _hardware_instance
