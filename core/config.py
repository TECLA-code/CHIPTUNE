# =============================================================================
# CONFIGURACIÓ GLOBAL - TECLA Professional
# =============================================================================

# Control de octava i modes especials
octava = 0
octava_anterior = 0  # Guarda la octava anterior al activar el modo caos
caos = 0
caos_note = 0
rio_base = 64

# Estats del sistema
loop_mode = 0
configout = 0  # 0=mode, 1=cicle1, 2=cicle2, 3=cicle3, 4=harm_base, 5=harm1, 6=harm2, 7=cv1_range, 8=cv2_range
last_interaction_time = 0.0

# Control de polsació llarga botons
button_hold_times = [0.0] * 6  # Temps inici polsació per cada botó
button_long_press_triggered = [False] * 6  # Si polsació llarga activada
show_full_summary = False  # Mostrar resum complet (Extra1 mantingut)

# Control d'harmonies i cicles de treball
duty1 = 50  # Cicle de treball PWM1 (1-99%)
duty2 = 50  # Cicle de treball PWM2 (1-99%)
duty3 = 50  # Cicle de treball PWM3 (1-99%)
freqharm_base = 0  # Harmònic aplicat a la portadora (PWM1)
freqharm1 = 0      # Harmònic aplicat a PWM2
freqharm2 = 0      # Harmònic aplicat a PWM3
cv1_range_config = 0  # CV1: 0=3.3V, 1=2.5V, 2=1.5V, 3=1.0V, 4=0.5V
cv2_range_config = 0  # CV2: 0=3.3V, 1=2.5V, 2=1.5V, 3=1.0V, 4=0.5V

# Sistema d'acceleració exponencial per configuració
config_acceleration = 1  # Factor d'acceleració (1, 2, 4, 8)
config_hold_time = 0.0   # Temps que porta premut el botó

def duty_percent_to_cycle(percent):
    """Converteix duty cycle de percentatge (1-99) a valor PWM (655-64880)"""
    return int((percent / 100.0) * 65535)

# Variables de temps i seqüència
iteration = 0
position = 0
playing_notes = set()
nota_actual = 0
nota_tocada_ara = False  # Per raig caos només quan nota sonag no bloquejant
last_note_time = 0.0
next_note_time = 0.0
last_button_check = 0.0
last_display_update = 0.0
last_input_sample = 0.0  # Nueva variable para muestreo desacoplado
current_sleep_time = 0.3  # Període actual entre notes segons BPM (actualitzat cada iteració)
x, y, z = 0.0, 0.0, 0.0  # Variables globales para inputs
cx, cy = 0.0, 0.0  # Coordenadas para Mandelbrot
bpm = 120  # BPM actual

# Animació LEDs idle
led_idle_step = 0
last_led_animation_time = 0.0

# Debouncing mejorado (11ms per evitar rebotes)
button_debounce_time = [0] * 6
debounce_delay = 0.011  # 11ms en lloc de 10ms

# Mode calibratge
calibration_mode = False

# CV input ranges (calibrables per CV1 i CV2 independents)
cv1_min, cv1_max = 0.0, 3.3
cv2_min, cv2_max = 0.0, 3.3

# Presets de rangs CV segons cv1/cv2_range_config
CV_RANGE_PRESETS = {
    0: (0.0, 3.3, "0-3.3V"),   # Full range
    1: (0.0, 2.5, "0-2.5V"),   # Eurorack
    2: (0.0, 1.5, "0-1.5V"),   # Low voltage
    3: (0.0, 1.0, "0-1.0V"),   # Very low
    4: (0.0, 0.5, "0-0.5V"),   # Minimal
}

def apply_cv1_range_preset():
    """Aplica el preset de rang CV1"""
    global cv1_min, cv1_max
    min_v, max_v, _ = CV_RANGE_PRESETS[cv1_range_config]
    cv1_min = min_v
    cv1_max = max_v

def apply_cv2_range_preset():
    """Aplica el preset de rang CV2"""
    global cv2_min, cv2_max
    min_v, max_v, _ = CV_RANGE_PRESETS[cv2_range_config]
    cv2_min = min_v
    cv2_max = max_v

# Control de visualització optimitzat
show_config_mode = False
config_display_timer = 0

# Estats per algorismes específics
state_harmony = {
    'previous_note': 60,
    'last_profile': 0,
    'last_tension': 0,
    'initialized': False
}

# Mode 9: Tracker programable - Configuració
# Notes i gates (solo OFF=0, ON=50)
sequencer_pattern = [60] * 32  # Array de notes MIDI (0-127)
sequencer_gate = [0] * 32      # Array de gates (0=OFF, 50=ON)
sequencer_length = 16          # Longitud actual del patró (8-32)
sequencer_note_pot = 1         # Potenciómetro activo para notas (1=CV1, 2=CV2)

# Estat de reproducció
sequencer_play_position = 0    # Posició de reproducció actual
sequencer_edit_position = 0    # Posició d'edició actual
sequencer_mode_active = False  # Si estem al tracker (bloqueig de mode)
sequencer_page = 0             # Pàgina actual (0=edició, 1=longitud, 2=info)

# Estat d'edició de notes
sequencer_note_edit_mode = False  # Si estem editant una nota
sequencer_pending_note = 60       # Nota temporal en edició

# Constants per a valors de gate (solo OFF y ON)
SEQUENCER_GATE_OFF = 0    # Nota apagada
SEQUENCER_GATE_ON = 50   # Nota encendida

# Rangs i escales per conversió de voltatge
pot_min, pot_max = 0.0, 3.3
step = (pot_max - pot_min) / 127.0
step_melo = (pot_max - pot_min) / 10.0
step_escala = (pot_max - pot_min) / 6.0
step_control = (pot_max - pot_min) / 50.0
step_nota = (pot_max - pot_min) / 23.0
step_ritme = (pot_max - pot_min) / 36.0

# Sistema RTOS - Control de Gate/Trigger temporal
gate_active = False
gate_off_time = 0.0
gate_duration = 0.020  # Duració variable segons mode
note_off_schedule = {}

# Gate percentatges per cada loop mode (% del període entre notes)
# Això assegura que el gate és proporcional al BPM
GATE_PERCENTAGES = {
    0: 0.05,   # Pausa - 5% del període
    1: 0.10,   # Fractal - 10% (atac ràpid)
    2: 0.20,   # Riu - 20% (fluid, sostingut)
    3: 0.08,   # Tempesta - 8% (molt ràpid, percussiu)
    4: 0.15,   # Harmonia - 15% (mig, musical)
    5: 0.18,   # Bosc - 18% (orgànic)
    6: 0.12,   # Escala - 12% (precís)
    7: 0.10,   # Euclidia - 10% (rítmic)
    8: 0.14,   # Cosmos - 14% (espacial)
    9: 0.15,   # Sequencer - 15% (controlat)
}

# Límits de gate per seguretat (en segons)
GATE_MIN_DURATION = 0.005  # 5ms mínim (sempre perceptible)
GATE_MAX_DURATION = 0.200  # 200ms màxim (evita gates eternament llargs a BPM baixos)

def get_gate_duration_for_mode(mode, period):
    """
    Retorna la duració del gate proporcional al període entre notes
    
    Args:
        mode: Mode musical actiu (0-8)
        period: Període entre notes en segons (sleep_time)
    
    Returns:
        Duració del gate en segons, limitada entre GATE_MIN i GATE_MAX
    """
    percentage = GATE_PERCENTAGES.get(mode, 0.10)
    gate_duration = period * percentage
    
    # Limitar entre mínim i màxim per seguretat
    gate_duration = max(GATE_MIN_DURATION, min(GATE_MAX_DURATION, gate_duration))
    
    return gate_duration
