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
        """Configurar potenciòmetres"""
        self.pote_velocidad = analogio.AnalogIn(board.GP26)  # Slider
        self.pote_analog_2 = analogio.AnalogIn(board.GP27)   # CV2/LDR
        self.pote_analog_1 = analogio.AnalogIn(board.GP28)   # CV1/POTE BPM
        
        self.potes = [self.pote_analog_1, self.pote_analog_2, self.pote_velocidad]
    
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
        Sistema NOU: 1 LED per cada opció de configuració
        LED actiu = paràmetre seleccionat (cfg.configout)
        LED2 EXCLUSIU per Gate/BPM - NO s'usa per configs
        """
        # Apagar tots primer (excepte LED2 si gate actiu)
        for i, led in enumerate(self.leds):
            if i != 1:  # No tocar LED2 (índex 1)
                led.value = False
        
        # Encendre el LED corresponent al configout actual
        if cfg.configout == 0:  # Loop Mode
            self.led_1.value = True
        elif cfg.configout == 1:  # Duty1
            self.led_3.value = True
        elif cfg.configout == 2:  # Duty2
            self.led_4.value = True
        elif cfg.configout == 3:  # Duty3
            self.led_5.value = True
        elif cfg.configout == 4:  # Harmònic base (PWM1)
            self.led_6.value = True
        elif cfg.configout == 5:  # Harmònic PWM2
            self.led_7.value = True
        elif cfg.configout == 6:  # Harmònic PWM3
            self.led_6.value = True
            self.led_7.value = True
        elif cfg.configout == 7:  # CV1 Range
            self.led_3.value = True
            self.led_6.value = True
        elif cfg.configout == 8:  # CV2 Range
            self.led_4.value = True
            self.led_7.value = True
        
        # LED2 SEMPRE controlat exclusivament pel gate (no es toca aquí)
        # El gate s'actualitza automàticament via RTOS i midi_handler
    
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
        if mode == 0:
            self.led_6.value, self.led_3.value, self.led_7.value = False, False, False
        elif mode == 1:
            self.led_6.value, self.led_3.value, self.led_7.value = False, False, False
        elif mode == 2:
            self.led_6.value, self.led_3.value, self.led_7.value = False, False, True
        elif mode == 3:
            self.led_6.value, self.led_3.value, self.led_7.value = False, True, False
        elif mode == 4:
            self.led_6.value, self.led_3.value, self.led_7.value = False, True, True
        elif mode == 5:
            self.led_6.value, self.led_3.value, self.led_7.value = True, False, False
        elif mode == 6:
            self.led_6.value, self.led_3.value, self.led_7.value = True, False, True
        elif mode == 7:
            self.led_6.value, self.led_3.value, self.led_7.value = True, True, False
        elif mode == 8:
            self.led_6.value, self.led_3.value, self.led_7.value = True, True, True
    
    def display_configuration_mode(self, cfg):
        """Mostra el valor del paràmetre configurat en LEDs 6, 3, 7"""
        if cfg.configout == 0:
            # Loop mode (0-8)
            self._display_value(cfg.loop_mode, 8)
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
            # Harmonic base (0-8)
            self._display_value(cfg.freqharm_base, 8)
        elif cfg.configout == 5:
            # Harmonic1 (0-8)
            self._display_value(cfg.freqharm1, 8)
        elif cfg.configout == 6:
            # Harmonic2 (0-8)
            self._display_value(cfg.freqharm2, 8)
        elif cfg.configout == 7:
            # CV1 range (0-4)
            self._display_value(cfg.cv1_range_config, 4)
        elif cfg.configout == 8:
            # CV2 range (0-4)
            self._display_value(cfg.cv2_range_config, 4)
    
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
