# =============================================================================
# CONVERSIONS MUSICALS - TECLA
# =============================================================================

def midi_to_frequency(midi_note):
    """Convierte nota MIDI a frecuencia en Hz"""
    return round(440 * (2 ** ((midi_note - 69) / 12)))

def midi_to_note_name(midi_note):
    """Convierte nota MIDI a nombre de nota (ej: 60 -> C4) amb protecció"""
    # Protecció rang MIDI
    if midi_note < 0 or midi_note > 127:
        return "ERR"
    if midi_note == 0:
        return "---"
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note_index = midi_note % 12
    return f"{note_names[note_index]}{octave}"

def apply_harmonic_interval(note, harmonic_type):
    """Aplica intervalo armónico a nota MIDI"""
    harmonic_intervals = {
        0: 0,    # Unísono - 0 semitons
        1: 1,    # Segona menor - 1 semitó
        2: 2,    # Segona major - 2 semitons
        3: 3,    # Tercera menor - 3 semitons
        4: 4,    # Tercera major - 4 semitons
        5: 5,    # Quarta justa - 5 semitons
        6: 6,    # Trítono - 6 semitons
        7: 7,    # Quinta justa - 7 semitons
        8: 8,    # Sisena menor - 8 semitons
        9: 9,    # Sisena major - 9 semitons
        10: 10,  # Sèptima menor - 10 semitons
        11: 11,  # Sèptima major - 11 semitons
        12: 12   # Octava - 12 semitons
    }
    
    harmonic = harmonic_intervals.get(harmonic_type, 0)
    nota_modificada = note + harmonic
    
    if nota_modificada >= 127:
        nota_modificada = note
    
    return nota_modificada

def map_value(value, in_min, in_max, out_min, out_max):
    """Mapea un valor de un rango a otro amb protecció de divisió"""
    if in_max == in_min:
        return (out_min + out_max) / 2.0
    return out_min + (float(value - in_min) * (out_max - out_min) / (in_max - in_min))


def normalize(value, in_min, in_max):
    """Retorna un valor normalitzat 0-1 dins un rang"""
    if in_max <= in_min:
        return 0.5
    clamped = max(in_min, min(in_max, value))
    return (clamped - in_min) / (in_max - in_min)

def voltage_to_bpm(
    voltage,
    pot_min=0.0,
    pot_max=3.3,
    bpm_min=20,
    bpm_max=220,
    curve=1.0,
):
    """Converteix voltatge a BPM amb calibratge, corba i límits configurables"""
    norm = normalize(voltage, pot_min, pot_max)
    norm = max(0.0, min(1.0, norm))
    if curve != 1.0:
        norm = norm ** curve
    return bpm_min + (bpm_max - bpm_min) * norm

def bpm_to_sleep_time(bpm):
    """Convierte BPM a tiempo de sleep en segundos"""
    return 30.0 / bpm


def smooth_value(previous, new, alpha=0.2):
    """Filtre de primer ordre per estabilitzar lectures"""
    if previous is None:
        return new
    alpha = max(0.0, min(1.0, alpha))
    return (alpha * new) + ((1.0 - alpha) * previous)

# Funcions de processament de voltatge amb calibració
def get_voltage_calibrated(voltage, cv_min, cv_max):
    """
    Clamp voltatge al rang CV configurat
    
    Args:
        voltage: Voltatge llegit (0-3.3V)
        cv_min: Mínim del rang CV (normalment 0.0V)
        cv_max: Màxim del rang CV (0.5V, 1.0V, 1.5V, 2.5V o 3.3V)
    
    Returns:
        Voltatge clamped dins el rang [cv_min, cv_max]
        Si voltage > cv_max, retorna cv_max
        Si voltage < cv_min, retorna cv_min
    """
    return max(cv_min, min(cv_max, voltage))

def get_voltage_percentage(voltage, cv_min, cv_max):
    """
    Retorna el percentatge (0-100) del voltatge dins el rang CV
    
    Args:
        voltage: Voltatge llegit (0-3.3V)
        cv_min: Mínim del rang CV
        cv_max: Màxim del rang CV
    
    Returns:
        Percentatge 0-100 dins el rang, clamped para evitar valores >100%.
        Ejemplo:
        - Rango 0-1V: 1V = 100%, 2V = 100% (clamped)
        - Rango 0-2V: 1V = 50%, 2V = 100%, 3V = 100% (clamped)
        Esto asegura que loop modes reciban valores consistentes sin salirse de rango.
    """
    clamped = get_voltage_calibrated(voltage, cv_min, cv_max)
    if cv_max - cv_min == 0:
        return 0
    percentage = int(((clamped - cv_min) / (cv_max - cv_min)) * 100)
    return max(0, min(100, percentage))  # Clamp adicional a 0-100%

def steps(voltage, cv_min=0.0, cv_max=3.3):
    """Escala voltatge calibrat a rang MIDI 0-127
    
    Args:
        voltage: Voltatge **ja calibrat** (dins del rang cv_min-cv_max)
        cv_min: Mínim del rang CV (default 0.0V)
        cv_max: Màxim del rang CV (default 3.3V, pot ser 0.5V, 1.0V, etc.)
    
    Returns:
        Valor 0-127 escalar segons el rang CV
    """
    if cv_max <= cv_min:
        return 64  # Valor mig si rang invàlid
    step = (cv_max - cv_min) / 127.0
    value = round((voltage - cv_min) / step)
    return max(0, min(127, value))


def steps_melo(voltage, cv_min=0.0, cv_max=3.3):
    """Escala voltatge calibrat per paràmetres melòdics (0-10)"""
    if cv_max <= cv_min:
        return 5
    step_melo = (cv_max - cv_min) / 10.0
    value = round((voltage - cv_min) / step_melo)
    return max(0, min(10, value))


def steps_escala(voltage, cv_min=0.0, cv_max=3.3):
    """Escala voltatge calibrat per paràmetres d'escala (0-6)"""
    if cv_max <= cv_min:
        return 3
    step_escala = (cv_max - cv_min) / 6.0
    value = round((voltage - cv_min) / step_escala)
    return max(0, min(6, value))


def steps_control(voltage, cv_min=0.0, cv_max=3.3):
    """Escala voltatge calibrat per control general (0-50)"""
    if cv_max <= cv_min:
        return 25
    step_control = (cv_max - cv_min) / 50.0
    value = round((voltage - cv_min) / step_control)
    return max(0, min(50, value))


def steps_nota(voltage, cv_min=0.0, cv_max=3.3):
    """Escala voltatge calibrat per selecció de notes (0-23)"""
    if cv_max <= cv_min:
        return 12
    step_nota = (cv_max - cv_min) / 23.0
    value = round((voltage - cv_min) / step_nota)
    return max(0, min(23, value))


def steps_ritme(voltage, cv_min=0.0, cv_max=3.3):
    """Escala voltatge calibrat per paràmetres rítmics (0-36)"""
    if cv_max <= cv_min:
        return 18
    step_ritme = (cv_max - cv_min) / 36.0
    value = round((voltage - cv_min) / step_ritme)
    return max(0, min(36, value))
