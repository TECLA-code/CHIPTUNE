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
        0: 0,   # Unísono
        1: 12,  # Octava
        2: 7,   # Quinta
        3: 5,   # Cuarta
        4: 4,   # Tercera Mayor
        5: 3,   # Tercera menor
        6: 9,   # Sexta Mayor
        7: 10,  # Séptima
        8: 6    # Tritono
    }
    
    harmonic = harmonic_intervals.get(harmonic_type, 0)
    nota_modificada = note + harmonic
    
    if nota_modificada >= 127:
        nota_modificada = note
    
    return nota_modificada

def map_value(value, in_min, in_max, out_min, out_max):
    """Mapea un valor de un rango a otro"""
    return out_min + (float(value - in_min) * (out_max - out_min) / (in_max - in_min))

def voltage_to_bpm(voltage, pot_min=0.0, pot_max=3.3):
    """Convierte voltaje a BPM (20-220 BPM)"""
    return map_value(voltage, pot_min, pot_max, 20, 220)

def bpm_to_sleep_time(bpm):
    """Convierte BPM a tiempo de sleep en segundos"""
    return 30.0 / bpm

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

def steps(voltage, pot_min=0.0, pot_max=3.3):
    """Escala voltaje a rango MIDI 0-127 (amb clipping)"""
    step = (pot_max - pot_min) / 127.0
    value = round((voltage - pot_min) / step)
    return max(0, min(127, value))  # Clipping MIDI segur

def steps_melo(voltage, pot_min=0.0, pot_max=3.3):
    """Escala voltaje para parámetros melódicos (0-10)"""
    step_melo = (pot_max - pot_min) / 10.0
    value = round((voltage - pot_min) / step_melo)
    return max(0, min(10, value))

def steps_escala(voltage, pot_min=0.0, pot_max=3.3):
    """Escala voltaje para parámetros escala (0-6)"""
    step_escala = (pot_max - pot_min) / 6.0
    value = round((voltage - pot_min) / step_escala)
    return max(0, min(6, value))

def steps_control(voltage, pot_min=0.0, pot_max=3.3):
    """Escala voltaje para control general (0-50)"""
    step_control = (pot_max - pot_min) / 50.0
    value = round((voltage - pot_min) / step_control)
    return max(0, min(50, value))

def steps_nota(voltage, pot_min=0.0, pot_max=3.3):
    """Escala voltaje para selección de notas (0-23)"""
    step_nota = (pot_max - pot_min) / 23.0
    value = round((voltage - pot_min) / step_nota)
    return max(0, min(23, value))

def steps_ritme(voltage, pot_min=0.0, pot_max=3.3):
    """Escala voltaje para parámetros rítmicos (0-36)"""
    step_ritme = (pot_max - pot_min) / 36.0
    value = round((voltage - pot_min) / step_ritme)
    return max(0, min(36, value))
