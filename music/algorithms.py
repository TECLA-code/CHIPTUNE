# =============================================================================
# ALGORITMES MUSICALS - TECLA
# =============================================================================
import math
import random

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
    modulated_frequency = base_frequency * (1 + 63/255)
    phase = iteration * modulated_frequency
    value = amplitude * math.sin(phase) + offset
    return max(min(round(value), max_value), min_value)

def harmonic_next_note(x, y, previous_note=0):
    """Genera siguiente nota basada en armonía"""
    intervals = {
        0: [3, 4, 7, 12],
        1: [2, 5, 9, 16],
        2: [1, 6, 11, 19],
        3: [8, 14, 17, 23],
        4: [10, 15, 20, 24],
        5: [13, 18, 21, 22]
    }
    
    harmonic_profile = min(x // 21, 5)
    tension = min(y // 32, 3)
    selected_interval = intervals[harmonic_profile][tension]
    direction = 1 if (x ^ y) % 2 else -1
    base_note = previous_note + (direction * selected_interval)
    harmonic_variation = int((x % 16) - (y % 16))
    final_note = (base_note + harmonic_variation) % 128
    return max(0, min(final_note, 127))
