# =============================================================================
# MIDI & PWM HANDLER - TECLA
# =============================================================================
import time
from adafruit_midi.note_on import NoteOn
from music.converters import midi_to_frequency, apply_harmonic_interval
from core.config import get_gate_duration_for_mode, duty_percent_to_cycle

class MidiHandler:
    """Gestió de notes MIDI i PWM amb sistema RTOS i duty cycles individuals"""
    
    def __init__(self, hardware, config):
        self.hw = hardware
        self.cfg = config
    
    def play_note_full(self, note, play, octava, periode, duty=0, freq1=0, freq2=0):
        """
        Reprodueix una nota completa amb MIDI, PWM i control visual - SISTEMA RTOS
        
        Args:
            note: Nota MIDI (0-127)
            play: 0=silencio, 1=tocar
            octava: Octava actual
            periode: Duració de la nota
            duty: DEPRECATED - Ara s'usen cfg.duty1/2/3 individuals
            freq1: Primer harmònic (0-8)
            freq2: Segon harmònic (0-8)
        """
        self.cfg.nota_actual = note
        current_time = time.monotonic()
        
        # Silencio: apagar gate inmediatament
        if play == 0 or note == 0:
            self.hw.out_jack.value = False
            self.hw.led_2.value = False
            self.cfg.gate_active = False
            self.cfg.nota_tocada_ara = False
            return
        
        # Marcar que s'ha tocat nota (per raig caos)
        self.cfg.nota_tocada_ara = True
        
        # --- Gate/Trigger temporal (RTOS) - Proporcional al BPM ---
        # Usar sleep_time actual del potenciòmetre per sincronització perfecta
        period_real = getattr(self.cfg, 'current_sleep_time', 0.3)  # Default 0.3s si no existeix
        gate_duration = get_gate_duration_for_mode(self.cfg.loop_mode, period_real)
        
        self.hw.out_jack.value = True
        self.hw.led_2.value = True
        self.cfg.gate_active = True
        self.cfg.gate_off_time = current_time + gate_duration
        
        # --- Nota MIDI amb duració programada ---
        self.hw.midi.send(NoteOn(note, 100))
        self.cfg.playing_notes.add(note)
        
        note_duration = periode / 200.0
        note_off_time = current_time + note_duration
        self.cfg.note_off_schedule[note] = note_off_time
        
        # --- Armònics i PWM ---
        freq0 = getattr(self.cfg, "freqharm_base", 0)
        note1 = apply_harmonic_interval(note, freq0)
        note2 = apply_harmonic_interval(note, freq1)
        note3 = apply_harmonic_interval(note, freq2)

        base_freq = midi_to_frequency(note1)
        freq2_val = midi_to_frequency(note2)
        freq3_val = midi_to_frequency(note3)
        
        # Aplicar duty cycles individuals (1-99% → 0-65535)
        duty_cycle1 = duty_percent_to_cycle(self.cfg.duty1)
        duty_cycle2 = duty_percent_to_cycle(self.cfg.duty2)
        duty_cycle3 = duty_percent_to_cycle(self.cfg.duty3)
        
        # Aplicar a PWM
        self.hw.pwm1.frequency = base_freq
        self.hw.pwm2.frequency = freq2_val
        self.hw.pwm3.frequency = freq3_val
        self.hw.pwm1.duty_cycle = duty_cycle1
        self.hw.pwm2.duty_cycle = duty_cycle2
        self.hw.pwm3.duty_cycle = duty_cycle3
