# TECLA AMB MIDI

# =============================================================================
# IMPORTACIONES DE LIBRERÍAS
# =============================================================================
import time
import random
import math
import board
import pwmio
import usb_midi
import digitalio
import analogio
from adafruit_midi import MIDI
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange

# =============================================================================
# CONFIGURACIÓN DE HARDWARE - ENTRADAS/SALIDAS
# =============================================================================

# Configuración MIDI y PWM
midi = MIDI(midi_out=usb_midi.ports[1], out_channel=0)
pwm1 = pwmio.PWMOut(board.GP0, frequency=440, duty_cycle=80, variable_frequency=True)
pwm2 = pwmio.PWMOut(board.GP2, frequency=440, duty_cycle=80, variable_frequency=True)
pwm3 = pwmio.PWMOut(board.GP22, frequency=440, duty_cycle=80, variable_frequency=True)

# Salida jack
out_jack = digitalio.DigitalInOut(board.GP1)
out_jack.direction = digitalio.Direction.OUTPUT
out_jack.value = False

# =============================================================================
# CONFIGURACIÓN DE BOTONES - ENTRADAS DIGITALES
# =============================================================================

# Botones de la cruceta (navegación principal)
boton_crueta_1 = digitalio.DigitalInOut(board.GP13)  # Subir octava
boton_crueta_1.direction = digitalio.Direction.INPUT
boton_crueta_1.pull = digitalio.Pull.DOWN

boton_crueta_2 = digitalio.DigitalInOut(board.GP14)  # Bajar octava
boton_crueta_2.direction = digitalio.Direction.INPUT
boton_crueta_2.pull = digitalio.Pull.DOWN

boton_crueta_3 = digitalio.DigitalInOut(board.GP15)  # Loop mode anterior
boton_crueta_3.direction = digitalio.Direction.INPUT
boton_crueta_3.pull = digitalio.Pull.DOWN

boton_crueta_4 = digitalio.DigitalInOut(board.GP3)   # Loop mode siguiente
boton_crueta_4.direction = digitalio.Direction.INPUT
boton_crueta_4.pull = digitalio.Pull.DOWN

# Botones extras (funciones especiales)
boton_extra_1 = digitalio.DigitalInOut(board.GP5)    # Cambiar configuración
boton_extra_1.direction = digitalio.Direction.INPUT
boton_extra_1.pull = digitalio.Pull.DOWN

boton_extra_2 = digitalio.DigitalInOut(board.GP4)    # Reset/parada total
boton_extra_2.direction = digitalio.Direction.INPUT
boton_extra_2.pull = digitalio.Pull.DOWN

# Lista de todos los botones para acceso fácil
buttons = [
    boton_crueta_1, boton_crueta_2, boton_crueta_3, 
    boton_crueta_4, boton_extra_1, boton_extra_2
]

# =============================================================================
# CONFIGURACIÓN DE POTENCIÓMETROS - ENTRADAS ANALÓGICAS
# =============================================================================

# Potenciómetros (slider, CV2/LDR, CV1/POTE)
pote_velocidad = analogio.AnalogIn(board.GP26)  # Slider - control principal de tempo
pote_analog_2 = analogio.AnalogIn(board.GP27)   # CV2/LDR - parámetros musicales
pote_analog_1 = analogio.AnalogIn(board.GP28)   # CV1/POTE - control de rango/tensión

potes = [pote_analog_1, pote_analog_2, pote_velocidad]  # Índices: 0, 1, 2

# =============================================================================
# CONFIGURACIÓN DE LEDs - SALIDAS VISUALES
# =============================================================================

led_1 = digitalio.DigitalInOut(board.GP10)  # Indicador freq1 activa (!= 0)
led_1.direction = digitalio.Direction.OUTPUT
led_1.value = False

led_2 = digitalio.DigitalInOut(board.GP6)  # LED que reproduce out_jack.value
led_2.direction = digitalio.Direction.OUTPUT
led_2.value = False

led_3 = digitalio.DigitalInOut(board.GP8)  # Indicador de modo activo / display config
led_3.direction = digitalio.Direction.OUTPUT
led_3.value = False

led_4 = digitalio.DigitalInOut(board.GP9)  # Indicador freq2 activa (!= 0)
led_4.direction = digitalio.Direction.OUTPUT
led_4.value = False

led_5 = digitalio.DigitalInOut(board.GP7) # Indicador duty activo (!= 0)
led_5.direction = digitalio.Direction.OUTPUT
led_5.value = False

led_6 = digitalio.DigitalInOut(board.GP11) # Indicador de modo activo / display config
led_6.direction = digitalio.Direction.OUTPUT
led_6.value = False

led_7 = digitalio.DigitalInOut(board.GP12) # Indicador de modo activo / display config
led_7.direction = digitalio.Direction.OUTPUT
led_7.value = False

leds = [led_1, led_2, led_3, led_4, led_5, led_6, led_7]

print("Configuración de pines completada:")
print("6 botones: GP13, GP14, GP15, GP3, GP5, GP4")
print("3 potenciómetros: GP26, GP27, GP28") 
print("7 LEDs: GP6, GP7, GP8, GP9, GP10, GP11, GP12")
print("1 OUT: GP1")

# =============================================================================
# VARIABLES GLOBALES DEL SISTEMA
# =============================================================================

# Control de octava y modos especiales
octava = 0        # Rango: -1 a 8
kidmos = 0        # Contador para modos especiales
caos = 0          # Modo caótico (0=normal, 1=caótico)
led_parada = 0
rio_base = 64
modo_parada = False


# Estados del sistema
loop_mode = 0     # Modo de operación actual (0-8)
configout = 0     # Configuración de salida (0=loop, 1=duty, 2=freq1, 3=freq2)

# Control de armonías y duty cycles
dutyharm = 0      # Tipo de duty cycle para armónicos (0-7)
freqharm1 = 0     # Primer intervalo armónico (0-8)  
freqharm2 = 0     # Segundo intervalo armónico (0-8)

# Variables de tiempo y secuencia
iteration = 0     # Contador general de iteraciones
position = 0      # Posición en secuencias rítmicas
playing_notes = set()  # Conjunto de notas activas

# Control de visualización
show_config_mode = False  # Modo de visualización de configuración
config_display_timer = 0  # Temporizador para modo visualización

# Estados para algoritmos específicos
state_harmony = {
    'previous_note': 60,
    'last_profile': 0,
    'last_tension': 0,
    'initialized': False
}

state = {
    'last_note_time': 0,
    'arp_index': 0,
    'chord_index': 0,
    'current_progression': [],
    'active_notes': set(),
    'initialized': False,
    'current_scale': []
}

# =============================================================================
# CONFIGURACIÓN DE POTENCIÓMETROS - RANGOS Y ESCALAS
# =============================================================================

pot_min, pot_max = 0.0, 3.3
step = (pot_max - pot_min) / 127.0        # Escala completa MIDI (0-127)
step_melo = (pot_max - pot_min) / 10.0    # Escala melódica
step_control = (pot_max - pot_min) / 50.0 # Control general
step_nota = (pot_max - pot_min) / 23.0    # Notas musicales
step_ritme = (pot_max - pot_min) / 36.0   # Ritmos y patrones
step_duty = (pot_max - pot_min) / 65535.0 # Duty cycle PWM

# =============================================================================
# ANIMACIÓN DE INICIO - SECUENCIA DE LEDs (3 segundos)
# =============================================================================

def animacion_inicio():
    """Animación de bienvenida de 3 segundos al iniciar el sistema"""
    print("🎹 Iniciando CHIPTUNE")

    
    led_2.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_1.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_7.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_3.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_6.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_7.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_4.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_5.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    time.sleep(0.2)  # Pausa breve con todos encendidos
    led_5.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_6.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_7.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_4.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_3.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_1.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    time.sleep(0.2)  # Pausa breve con todos encendidos    
    led_2.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.10)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.10)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.10)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.10)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.10)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = False
    time.sleep(0.05)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.05)  # 150ms entre LEDs
    led_1.value = True
    led_7.value = True
    led_3.value = True
    led_6.value = True
    led_7.value = True
    led_4.value = True
    led_5.value = True
    time.sleep(0.15)  # 150ms entre LEDs
    led_2.value = False
    led_1.value = False
    led_7.value = False
    led_3.value = False
    led_6.value = False
    led_4.value = False
    led_5.value = False
    time.sleep(0.15)  # 150ms entre LEDs
    led_2.value = True
    time.sleep(0.3)  # 150ms entre LEDs
    led_2.value = False
    # FASE 3: Secuencia de patrones binarios (1 segundo)

# =============================================================================
# FUNCIONES DE PROCESAMIENTO DE SEÑALES ANALÓGICAS
# =============================================================================

def get_voltage(pin):
    """Convierte valor ADC a voltaje (0-3.3V)"""
    return (pin.value * 3.3) / 65536

def steps(voltage):
    """Escala voltaje a rango MIDI 0-127"""
    return round((voltage - pot_min) / step)

def steps_melo(voltage):
    """Escala voltaje para parámetros melódicos"""
    return round((voltage - pot_min) / step_melo)

def steps_control(voltage):
    """Escala voltaje para control general"""
    return round((voltage - pot_min) / step_control)

def steps_nota(voltage):
    """Escala voltaje para selección de notas"""
    return round((voltage - pot_min) / step_nota)

def steps_ritme(voltage):
    """Escala voltaje para parámetros rítmicos"""
    return round((voltage - pot_min) / step_ritme)

def steps_duty(voltage):
    """Escala voltaje para duty cycle PWM"""
    return round((voltage - pot_min) / step_duty)

def map_value(value, in_min, in_max, out_min, out_max):
    """Mapea un valor de un rango a otro"""
    return out_min + (float(value - in_min) * (out_max - out_min) / (in_max - in_min))

def boton_presionado(boton, tiempo_espera=0.05, tiempo_post_accion=0.3):
    """Verifica si un botón fue presionado con debounce y pausa adicional"""
    if boton.value:
        time.sleep(tiempo_espera)
        if boton.value:
            time.sleep(tiempo_post_accion)  # Pausa después de la acción
            return True
    return False



# =============================================================================
# FUNCIONES DE GENERACIÓN MUSICAL
# =============================================================================

def generar_ritmo_euclideo(pulsos, pasos):
    """Genera patrón rítmico euclidiano"""
    if pasos <= 0:
        return [0]
    if pulsos > pasos:
        pulsos = pasos
    grupos = [[1] for _ in range(pulsos)] + [[0] for _ in range(pasos - pulsos)]
    while len(grupos) > 1:
        nuevos_grupos = []
        for i in range(0, len(grupos) // 2):
            nuevos_grupos.append(grupos[i] + grupos[-(i + 1)])
        if len(grupos) % 2 == 1:
            nuevos_grupos.append(grupos[len(grupos) // 2])
        grupos = nuevos_grupos
    return [item for sublist in grupos for item in sublist]

def mandelbrot_to_midi(cx, cy, max_iter=200):
    """Convierte coordenadas Mandelbrot a nota MIDI"""
    x, y = 0.0, 0.0
    iteration = 0
    while x*x + y*y <= 4 and iteration < max_iter:
        x_new = x*x - y*y + cx
        y = 2*x*y + cy
        x = x_new
        iteration += 1
    return iteration % 60 + 32

def sinusoidal_value_2(iteration, ampli, base_frequency):
    """Genera valor sinusoidal para modulación"""
    min_value, max_value = 0, 127
    amplitude = ampli / 2
    offset = (max_value + min_value) / 2
    modulated_frequency = base_frequency * (1 + 63/255)  # 63 es valor fijo
    phase = iteration * modulated_frequency
    value = amplitude * math.sin(phase) + offset
    return max(min(round(value), max_value), min_value)

def harmonic_next_note(x, y, previous_note=0):
    """Genera siguiente nota basada en armonía"""
    intervals = {
        0: [3, 4, 7, 12],    # Consonantes básicas
        1: [2, 5, 9, 16],    # Intervalos justos extendidos
        2: [1, 6, 11, 19],   # Tensiones moderadas
        3: [8, 14, 17, 23],  # Intervalos compuestos
        4: [10, 15, 20, 24], # Tensiones fuertes
        5: [13, 18, 21, 22]  # Cromatismos y clusters
    }
    
    harmonic_profile = min(x // 21, 5)
    tension = min(y // 32, 3)
    selected_interval = intervals[harmonic_profile][tension]
    direction = 1 if (x ^ y) % 2 else -1
    base_note = previous_note + (direction * selected_interval)
    harmonic_variation = int((x % 16) - (y % 16))
    final_note = (base_note + harmonic_variation) % 128
    return max(0, min(final_note, 127))

# =============================================================================
# FUNCIONES DE GESTIÓN DE NOTAS MIDI
# =============================================================================

def midi_to_frequency(midi_note):
    """Convierte nota MIDI a frecuencia en Hz"""
    return round(440 * (2 ** ((midi_note - 69) / 12)))

def apply_harmonic_interval(note, harmonic_type):
    """Aplica intervalo armónico a nota MIDI"""
    
    if harmonic_type == 0:
        harmonic = 0
    elif harmonic_type == 1:
        harmonic = 12
    elif harmonic_type == 2:
        harmonic = 7
    elif harmonic_type == 3:
        harmonic = 5
    elif harmonic_type == 4:
        harmonic = 4
    elif harmonic_type == 5:
        harmonic = 3
    elif harmonic_type == 6:
        harmonic = 9
    elif harmonic_type == 7:
        harmonic = 10
    nota_modificada = note + harmonic
    if nota_modificada >= 127:
        nota_modificada = note
    return nota_modificada

def adjust_frequency(freq):
    """Ajusta frecuencia al rango audible"""
    while freq < 20:
        freq *= 2
    while freq > 20000:
        freq = int(freq / 2)
    return freq

def play_note_full(note, play, octava, periode, duty=dutyharm, freq1=freqharm1, freq2=freqharm2):
    """Reproduce nota con todos los parámetros de sonido"""
    if play == 0:
        # Silencio - jack ACTIVO
        out_jack.value = True
        led_2.value = True  # LED2 refleja out_jack.value
        midi.send(NoteOn(note, 0))
        playing_notes.add(note)
        time.sleep(periode/50)
        midi.send(NoteOff(note, 0))
    else:
        # Nota activa - jack DESACTIVADO
        out_jack.value = False
        led_2.value = False  # LED2 refleja out_jack.value
        midi.send(NoteOn(note, 100))
        playing_notes.add(note)
        time.sleep(periode/50)
        midi.send(NoteOff(note, 100))
        out_jack.value = True  # Reactivar jack
        led_2.value = True    # LED2 refleja out_jack.value
        
        # Aplicar armónicos
        note1 = note
        note2 = apply_harmonic_interval(note, freq1)
        note3 = apply_harmonic_interval(note, freq2)
        
        # Convertir a frecuencias
        base_freq = midi_to_frequency(note1)
        freq2_val = midi_to_frequency(note2)
        freq3_val = midi_to_frequency(note3)
        
        # Configuraciones de duty cycle predefinidas
        if duty == 0:
            duty_cycle1=int(32768)
            duty_cycle2=int(32768)
            duty_cycle3=int(32768)
        elif duty == 1:
            duty_cycle1=int(32768)
            duty_cycle2=int(26214)
            duty_cycle3=int(19661)
        elif duty == 2:
            duty_cycle1=int(45875)
            duty_cycle2=int(32768)
            duty_cycle3=int(16384)
        elif duty == 3:
            duty_cycle1=int(52428)
            duty_cycle2=int(39321)
            duty_cycle3=int(26214)
        elif duty == 4:
            duty_cycle1=int(26214)
            duty_cycle2=int(19661)
            duty_cycle3=int(13107)
        elif duty == 5:
            duty_cycle1=int(49152)
            duty_cycle2=int(32768)
            duty_cycle3=int(8192)
        elif duty == 6:
            duty_cycle1=int(39321)
            duty_cycle2=int(32768)
            duty_cycle3=int(26214)
        elif duty == 7:
            duty_cycle1=int(65000)
            duty_cycle2=int(16384)
            duty_cycle3=int(4096)
       
        # Aplicar frecuencias y duty cycles
        pwm1.frequency = base_freq
        pwm2.frequency = freq2_val
        pwm3.frequency = freq3_val
        pwm1.duty_cycle = duty_cycle1
        pwm2.duty_cycle = duty_cycle2  
        pwm3.duty_cycle = duty_cycle3

def stop_note(nota_actual):
    """Detiene una nota específica"""
    midi.send(NoteOff(nota_actual, 100))

def stop_all_notes():
    """Detiene todas las notas activas"""
    for note in playing_notes:
        midi.send(NoteOff(note, 0))
    playing_notes.clear()

# =============================================================================
# FUNCIONES DE VISUALIZACIÓN CON LEDs
# =============================================================================

def update_config_indicators():
    """Actualiza LEDs que indican configuraciones no por defecto"""
    # LED5 se enciende si dutyharm no es 0
    led_5.value = (dutyharm != 0)
    # LED1 se enciende si freqharm1 no es 0  
    led_1.value = (freqharm1 != 0)
    # LED4 se enciende si freqharm2 no es 0
    led_4.value = (freqharm2 != 0)

def display_configuration_mode():
    """Muestra la configuración actual en los LEDs 6, 3, 7"""
    # Apagar LEDs de display temporalmente
    led_6.value = False
    led_3.value = False  
    led_7.value = False
    
    if configout == 0:  # Mostrar loop_mode
        display_value(loop_mode, 8)  # loop_mode va de 0-8
    elif configout == 1:  # Mostrar dutyharm
        display_value(dutyharm, 7)   # dutyharm va de 0-7
    elif configout == 2:  # Mostrar freqharm1
        display_value(freqharm1, 8)  # freqharm1 va de 0-8
    elif configout == 3:  # Mostrar freqharm2
        display_value(freqharm2, 8)  # freqharm2 va de 0-8

def display_value(value, max_value):
    """Muestra un valor en los LEDs 6, 3, 7 usando codificación binaria"""
    # Normalizar valor a rango 0-7 para display con 3 LEDs
    normalized_value = int((value / max_value) * 7)
    
    # Mostrar en binario con LEDs 6, 3, 7 (bit2, bit1, bit0)
    led_6.value = (normalized_value & 4) != 0  # Bit 2 (valor 4)
    led_3.value = (normalized_value & 2) != 0  # Bit 1 (valor 2)  
    led_7.value = (normalized_value & 1) != 0  # Bit 0 (valor 1)

def update_loop_mode_indicators():
    """Actualiza LEDs indicadores del loop_mode actual (comportamiento original)"""
    if loop_mode == 1:
        led_6.value, led_7.value, led_3.value = False, False, False
    elif loop_mode == 2:
        led_6.value, led_7.value, led_3.value = False, False, True
    elif loop_mode == 3:
        led_6.value, led_7.value, led_3.value = False, True, False
    elif loop_mode == 4:
        led_6.value, led_7.value, led_3.value = False, True, True
    elif loop_mode == 5:
        led_6.value, led_7.value, led_3.value = True, False, False
    elif loop_mode == 6:
        led_6.value, led_7.value, led_3.value = True, False, True
    elif loop_mode == 7:
        led_6.value, led_7.value, led_3.value = True, True, False
    elif loop_mode == 8:
        led_6.value, led_7.value, led_3.value = True, True, True
    else:  # loop_mode == 0
        led_6.value, led_7.value, led_3.value = False, False, False



# =============================================================================
# LOOP PRINCIPAL
# =============================================================================

print("Sistema iniciado. Listo para operar.")

# Ejecutar animación de inicio
animacion_inicio()
while True:
    # =========================================================================
    # LECTURA DE SENSORES Y CONFIGURACIÓN INICIAL
    # =========================================================================
    
    # Leer valores de potenciómetros
    pot_values = [get_voltage(pote) for pote in potes]
    x, y, z = pot_values  # x=slider, y=CV2/LDR, z=CV1/POTE
    
    # Generar ritmo euclidiano base
    ritmo = generar_ritmo_euclideo(steps_ritme(y), steps_ritme(z)+1)
    to = random.randint(0, 1)  # Estado aleatorio para modo caótico
    
    # Coordenadas para fractales
    cx = map_value(potes[1].value, 0, 65535, -1.5, 1.5)
    cy = map_value(potes[2].value, 0, 65535, -1.5, 1.5)
    
    # Control del temporizador de visualización
    if show_config_mode:
        config_display_timer += 1
        if config_display_timer > 50:  # Mostrar configuración por ~5 segundos
            show_config_mode = False
            config_display_timer = 0

    # Apagar todo si estamos en modo 0
    if loop_mode == 0:
        duty_cycle = 0
        out_jack.value = False
        led_2.value = False
        pwm1.duty_cycle = duty_cycle
        pwm2.duty_cycle = duty_cycle
        pwm3.duty_cycle = duty_cycle
        led_parada=led_parada + 1
        if led_parada == 1:
            led_1.value = True
            led_7.value = False  
            led_3.value = False
            led_6.value = False
            led_4.value = False
            led_5.value = False
        elif led_parada == 2:
            led_1.value = False
            led_7.value = True  
            led_3.value = False
            led_6.value = False
            led_4.value = False
            led_5.value = False
        elif led_parada == 3:
            led_1.value = False
            led_7.value = False  
            led_3.value = True
            led_6.value = False
            led_4.value = False
            led_5.value = False
        elif led_parada == 4:
            led_1.value = False
            led_7.value = False  
            led_3.value = False
            led_6.value = True
            led_4.value = False
            led_5.value = False
        elif led_parada == 5:
            led_1.value = False
            led_7.value = False  
            led_3.value = False
            led_6.value = False
            led_4.value = True
            led_5.value = False
        elif led_parada == 6:
            led_1.value = False
            led_7.value = False  
            led_3.value = False
            led_6.value = False
            led_4.value = False
            led_5.value = True
            led_parada = 0
        time.sleep(0.10)  # 150ms entre LEDs


    # =========================================================================
    # GESTIÓN DE BOTONES - CONTROL DE INTERFAZ
    # =========================================================================

    # Botón EXTRA 1 - Cambiar configuración de salida y activar visualización
    if boton_presionado(boton_extra_1):
        configout = (configout + 1) % 4
        config_names = ["Loopmode", "Duty Harmonics", "Freq1 Harmonics", "Freq2 Harmonics"]
        print(config_names[configout])
        
        show_config_mode = True
        config_display_timer = 0

    # Botón EXTRA 2 - Parada total y reset
    if boton_presionado(boton_extra_2):
        loop_mode = 0
        stop_all_notes()
        iteration = 0
        caos = 0
        print("⏹️  ATURAT TOTAL - Sistema reiniciat")
        for led in leds:
            led.value = False

    # Botón CRUETA 1 - Subir octava
    if boton_presionado(boton_crueta_1):
        if octava < 8:
            octava += 1
            print(f"Octava pujada a {octava}")
            kidmos = caos = 0
        else:
            print(f"Ja estàs a l'octava máxima (8). {kidmos} {caos}")
            kidmos += 1
            if kidmos >= 5: kidmos = caos = 0
            elif kidmos >= 3: caos = 1

    # Botón CRUETA 2 - Bajar octava
    if boton_presionado(boton_crueta_2):
        if octava > 0:
            octava -= 1
            print(f"Octava baixada a {octava}")
            kidmos = caos = 0
        else:
            print(f"Ja estàs a l'octava mínima (0). {kidmos} {caos}")
            kidmos += 1
            if kidmos >= 5: kidmos = caos = 0
            elif kidmos >= 3: caos = 1

    # Botón CRUETA 3 - Modo anterior
    if boton_presionado(boton_crueta_3):
        if configout == 0:
            loop_mode = (loop_mode - 1)
            if loop_mode < 1:
                loop_mode = 8
        elif configout == 1:  # Duty harmonics
            dutyharm = (dutyharm - 1) % 8
        elif configout == 2:  # Freq1 harmonics
            freqharm1 = (freqharm1 - 1) % 9
        elif configout == 3:  # Freq2 harmonics
            freqharm2 = (freqharm2 - 1) % 9


        show_config_mode = True
        config_display_timer = 0
        stop_all_notes()

    # Botón CRUETA 4 - Modo siguiente
    if boton_presionado(boton_crueta_4):
        if configout == 0:
            loop_mode = (loop_mode + 1)
            if loop_mode > 8:
                loop_mode = 1
        elif configout == 1:  # Duty harmonics
            dutyharm = (dutyharm + 1) % 8
        elif configout == 2:  # Freq1 harmonics
            freqharm1 = (freqharm1 + 1) % 9
        elif configout == 3:  # Freq2 harmonics
            freqharm2 = (freqharm2 + 1) % 9


        show_config_mode = True
        config_display_timer = 0
        stop_all_notes()


    # =========================================================================
    # ACTUALIZACIÓN DE VISUALIZACIÓN CON LEDs
    # =========================================================================
    
    if show_config_mode:
        # Modo de visualización de configuración activo
        display_configuration_mode()
    else:
        # Modo normal - mostrar indicadores de loop_mode
        update_loop_mode_indicators()
    
    # Siempre actualizar indicadores de configuraciones no por defecto
    update_config_indicators()


    # =========================================================================
    # MODOS DE OPERACIÓN (LOOP MODES)
    # =========================================================================

    # LOOP 1: MANDELBROT - Generación fractal
    if loop_mode == 1:  # AMBIENTE - Fractal
        tempo_raw = steps_melo(x)
        tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)
        note = mandelbrot_to_midi(cx, cy)
        play_note_full(note, 1, octava, tempo * 50, dutyharm, freqharm1, freqharm2)
        print(f"[Fractal] Nota: {note}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}")



    # LOOP 2: RIO - Flujo continuo con variaciones
    elif loop_mode == 2:  # AMBIENTE - Río
        tempo_raw = steps_melo(x)
        tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)
        corriente = steps_control(y) / 25
        turbulencia = steps(z)
        rio_time = time.time()

        rio_base = (rio_base + corriente) % 127
        wave = math.sin(rio_time * 0.8) * (corriente * 0.5)
        ripple = math.cos(rio_time * 2.2) * (turbulencia * 0.3)
        random_offset = random.uniform(-corriente * 0.2, turbulencia * 0.2)

        nota_rio = int(max(0, min(127, rio_base + wave + ripple - random_offset * 2)))
        play_note_full(nota_rio, 1, octava, tempo * 50, dutyharm, freqharm1, freqharm2)
        print(f"[Río] Nota: {nota_rio}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}")



    # LOOP 3: TORMENTA - Efectos atmosféricos
    elif loop_mode == 3:
        escala_tormenta = [0, 3, 5, 7, 10]
        fuerza_viento = steps(x)
        intensidad_lluvia = steps_control(y)
        frecuencia_rayos = steps_melo(z)
        
        efecto_viento = max(0, min(63, int(fuerza_viento * 0.5)))
        nota_base = 12 * min(octava, 10) + int(intensidad_lluvia * 0.48)
        nota_base = max(0, min(127, nota_base))
        
        # Generar rayos aleatorios
        if random.randint(0, 1000) < (frecuencia_rayos * 100):
            direccion = 1 if random.random() > 0.3 else -1
            for i, intervalo in enumerate(escala_tormenta[::direccion]):
                multiplicador = max(1, min(3, (i+1)))
                nota_relampago = nota_base + (intervalo * direccion * multiplicador)
                nota_relampago = max(0, min(127, nota_relampago))
                play_note_full(nota_relampago, 1, octava, 
                             max(0.01, 0.05 - (frecuencia_rayos * 0.003)) * 50, dutyharm, freqharm1, freqharm2)
        else:
            # Patrón de lluvia
            variacion_lluvia = random.randint(-2 + frecuencia_rayos, 2 + frecuencia_rayos)
            nota_lluvia = max(0, min(127, nota_base + variacion_lluvia))
            play_note_full(nota_lluvia, 1, octava, 
                         max(0.01, 0.05 * (1 - (fuerza_viento/127))) * 50, dutyharm, freqharm1, freqharm2)
            time.sleep(max(0.01, 0.3 * (1.0 - (intensidad_lluvia / 50) * 0.9 + 0.1) * 0.9))

    # LOOP 4: ARMONÍA - Progresiones armónicas
    elif loop_mode == 4:  # MELODICO - Armonía
        tempo_raw = steps_melo(x)
        tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)
        if not state_harmony['initialized']:
            state_harmony.update({'previous_note': 60, 'last_profile': 0, 'last_tension': 0, 'initialized': True})

        x_param = steps_melo(y) % 128
        y_param = steps_melo(z) % 128
        new_note = harmonic_next_note(x_param, y_param, state_harmony['previous_note'])

        state_harmony.update({
            'previous_note': new_note,
            'last_profile': min(x_param // 21, 5),
            'last_tension': min(y_param // 32, 3)
        })

        play = 1 if iteration % 2 == 0 else 0
        play_note_full(new_note, play, octava, tempo * 50, dutyharm, freqharm1, freqharm2)

        if any(btn.value for btn in buttons):
            state_harmony.update({'previous_note': 60, 'last_profile': 0, 'last_tension': 0})
            stop_all_notes()

        print(f"[Armonía] Nota: {new_note}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}")



    # LOOP 5: MATEMÁTICO PRO - Arpegios complejos
    elif loop_mode == 5:  # MELODICO - Arpegio progresivo
        try:
            tempo_raw = steps_melo(x)
            tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)

            if not state['initialized']:
                state.update({
                    'current_progression': [], 'active_notes': set(),
                    'arp_index': 0, 'chord_index': 0, 
                    'current_scale': [], 'initialized': True
                })

            if any(btn.value for btn in buttons):
                raise KeyboardInterrupt

            octava_actual = octava * 12
            tipo_acorde = steps_nota(y) % 5
            progresion_pattern = steps_ritme(z) % 4
            direccion_arpegio = -1 if z > 2.0 else 1

            escalas = [[0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]]
            escala_actual = escalas[progresion_pattern % 2]
            patrones_progresion = [[0, 4, 5, 3], [0, 5, 3, 4], [0, 2, 3, 5], [0, 5, 7, 4]]

            if not state['current_progression'] or (time.monotonic() - state['last_note_time'] > tempo * 4):
                progression = patrones_progresion[progresion_pattern]
                state['current_progression'] = [
                    octava_actual + escala_actual[g % len(escala_actual)] + 12 * (g // len(escala_actual))
                    for g in progression
                ]
                state['chord_index'] = state['arp_index'] = 0

            elapsed_time = time.monotonic() - state['last_note_time']
            if elapsed_time >= tempo:
                acordes = [[0, 4, 7], [0, 3, 7], [0, 5, 7], [0, 3, 6], [0, 4, 8]]
                fib_sequence = (0, 1, 1, 2, 3, 5, 8, 13, 21)
                fib_offset = fib_sequence[state['arp_index'] % 9] % 12

                nota_base = state['current_progression'][state['chord_index']]
                notas_acorde = [max(0, min(127, nota_base + n + fib_offset)) for n in acordes[tipo_acorde]]
                notas_ordenadas = notas_acorde[::direccion_arpegio]
                nota_actual = notas_ordenadas[state['arp_index'] % len(notas_ordenadas)]

                play = 1 if state['arp_index'] % 2 == 0 else 0
                play_note_full(nota_actual, play, octava, tempo * 50, dutyharm, freqharm1, freqharm2)
                state['active_notes'].add(nota_actual)

                state['arp_index'] += 1
                if state['arp_index'] >= len(notas_ordenadas) * 2:
                    state['chord_index'] = (state['chord_index'] + 1) % len(state['current_progression'])
                    state['arp_index'] = 0
                    for n in state['active_notes']:
                        stop_note(n)
                    state['active_notes'].clear()

                state['last_note_time'] = time.monotonic()
                print(f"[Arpegio] Nota: {nota_actual}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}")

        except KeyboardInterrupt:
            for n in state['active_notes']:
                stop_note(n)
            state.update({'initialized': False, 'active_notes': set(), 'current_progression': []})


    # LOOP 6: ALEATORIO RITMICO - Aleatorio con margenes
    elif loop_mode == 6:  # RITMICO - Aleatorio
        tempo_raw = steps_melo(x)
        tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)
        if steps(z) > steps(y):
            random_note = random.randint(0, 127)
        else:
            random_note = random.randint(steps(z), steps(y))

        play = random.choice([0, 1])
        play_note_full(random_note, play, octava, tempo * 50, dutyharm, freqharm1, freqharm2)
        print(f"[Aleatorio] Nota: {random_note}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}")


    elif loop_mode == 7:  # RITMICO - Euclidiano
        tempo_raw = steps_melo(x)
        tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)
        if position >= steps_ritme(z):
            position = 0

        ritmo = generar_ritmo_euclideo(steps_ritme(y), steps_ritme(z) + 1)
        to_play = ritmo[position]
        nota_base = max(0, (octava * 12) + random.randint(-3, 3) if position > 0 else 0)

        play_note_full(nota_base, to_play, octava, tempo * 50, dutyharm, freqharm1, freqharm2)
        print(f"[Euclidiano] Nota: {nota_base}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}")
        position += 1

    elif loop_mode == 8:  # MODO DEFINITIVO - Cosmos
        tempo_raw = steps_melo(x)
        tempo = map_value(tempo_raw, 0, 127, 0.3, 0.05)
        fractal_note = mandelbrot_to_midi(cx, cy)
        sinusoidal_note = int(sinusoidal_value_2(iteration, steps(z), steps(y) * 2 / 100))
        armonica = harmonic_next_note(steps_melo(y), steps_melo(z), fractal_note)

        base_note = (fractal_note + sinusoidal_note + armonica) // 3
        base_note = max(0, min(127, base_note))

        ritmo = generar_ritmo_euclideo(steps_ritme(y), steps_ritme(z) + 1)
        to_play = ritmo[iteration % len(ritmo)]
        play = 1 if iteration % 2 == 0 else 0
        final_play = play * to_play

        play_note_full(base_note, final_play, octava, tempo * 50, dutyharm, freqharm1, freqharm2)
        print(f"[Cosmos] Nota: {base_note}, CVs: x={x:.2f}, y={y:.2f}, z={z:.2f}, Duty={dutyharm}, Freq1={freqharm1}, Freq2={freqharm2}, Ritmo={to_play}, Melódico={play}")
        iteration = (iteration + 1) % 60000
