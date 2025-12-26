# =============================================================================
# MIDI & PWM HANDLER - TECLA
# =============================================================================
import time
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from music.converters import midi_to_frequency, apply_harmonic_interval
from core.config import (
    get_gate_duration_for_mode,
    duty_percent_to_cycle,
    NOTE_OFF_MIN_DURATION,
    NOTE_OFF_MAX_DURATION,
    NOTE_OFF_DEFAULT_RATIO,
)

ALL_NOTES_OFF_CC = 123


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
            self._stop_note_immediate(note)
            return
        
        
        # Marcar que s'ha tocat nota (per raig caos)
        self.cfg.nota_tocada_ara = True
        
        # --- Gate/Trigger temporal (RTOS) ---
        # IMPORTANT: 'periode' vé en mil·lisegons dels modes (ex: sleep_time * 500)
        gate_duration = get_gate_duration_for_mode(self.cfg.loop_mode, periode)
        
        # Apagar gate anterior ABANS d'encendre el nou (evita overlapping)
        if self.cfg.gate_active:
            self.hw.out_jack.value = False
            self.hw.led_2.value = False
            self.cfg.gate_active = False
        
        # Encendre gate nou
        self.hw.out_jack.value = True
        self.hw.led_2.value = True
        self.cfg.gate_active = True
        self.cfg.gate_duration = gate_duration
        self.cfg.gate_off_time = current_time + gate_duration
        
        # --- Nota MIDI amb duració programada ---
        try:
            self.hw.midi.send(NoteOn(note, 100))
        except Exception as exc:  # pragma: no cover - runtime safeguard
            self._handle_midi_error(exc)
            self._stop_note_immediate(note, suppress_midi=True)
            return

        self.cfg.playing_notes.add(note)

        note_duration = gate_duration * NOTE_OFF_DEFAULT_RATIO
        note_duration = max(NOTE_OFF_MIN_DURATION, min(NOTE_OFF_MAX_DURATION, note_duration))
        self.cfg.note_off_schedule[note] = current_time + note_duration
        
        # --- Armònics i PWM ---
        freq0 = getattr(self.cfg, "freqharm_base", 0)
        
        # PWM1: Aplicar harmònics o apagar si play=0
        if play == 0 or note == 0:
            base_freq = 440  # Freqüència dummy
            duty_cycle1 = 0  # APAGAR PWM1
        else:
            note1 = apply_harmonic_interval(note, freq0)
            base_freq = midi_to_frequency(note1)
            duty_cycle1 = duty_percent_to_cycle(self.cfg.duty1)
        
        # PWM2: Aplicar harmònics o apagar si play=0
        if play == 0 or note == 0:
            freq2_val = 440  # Freqüència dummy
            duty_cycle2 = 0  # APAGAR PWM2
        else:
            note2 = apply_harmonic_interval(note, freq1)
            freq2_val = midi_to_frequency(note2)
            duty_cycle2 = duty_percent_to_cycle(self.cfg.duty2)
        
        # PWM3: Aplicar harmònics o apagar si play=0
        if play == 0 or note == 0:
            freq3_val = 440  # Freqüència dummy
            duty_cycle3 = 0  # APAGAR PWM3
        else:
            note3 = apply_harmonic_interval(note, freq2)
            freq3_val = midi_to_frequency(note3)
            duty_cycle3 = duty_percent_to_cycle(self.cfg.duty3)
        
        # Aplicar a PWM
        self.hw.pwm1.frequency = base_freq
        self.hw.pwm2.frequency = freq2_val
        self.hw.pwm3.frequency = freq3_val
        self.hw.pwm1.duty_cycle = duty_cycle1
        self.hw.pwm2.duty_cycle = duty_cycle2
        self.hw.pwm3.duty_cycle = duty_cycle3

    def play_note_full_multi(self, nota_pwm1, nota_pwm2, nota_pwm3, play, octava, periode, duty=0, freq1=0, freq2=0):
        """Reprodueix 3 notes diferents simultàniament als 3 PWMs"""
        self.cfg.nota_actual = nota_pwm1
        current_time = time.monotonic()
        if play == 0 or (nota_pwm1 == 0 and nota_pwm2 == 0 and nota_pwm3 == 0):
            self._stop_note_immediate(nota_pwm1)
            return
        self.cfg.nota_tocada_ara = True
        gate_duration = get_gate_duration_for_mode(self.cfg.loop_mode, periode)
        if self.cfg.gate_active:
            self.hw.out_jack.value = False
            self.hw.led_2.value = False
            self.cfg.gate_active = False
        self.hw.out_jack.value = True
        self.hw.led_2.value = True
        self.cfg.gate_active = True
        self.cfg.gate_duration = gate_duration
        self.cfg.gate_off_time = current_time + gate_duration
        try:
            self.hw.midi.send(NoteOn(nota_pwm1 if nota_pwm1 > 0 else 60, 100))
        except Exception as exc:
            self._handle_midi_error(exc)
            self._stop_note_immediate(nota_pwm1 if nota_pwm1 > 0 else 60, suppress_midi=True)
            return
        self.cfg.playing_notes.add(nota_pwm1 if nota_pwm1 > 0 else 60)
        note_duration = gate_duration * NOTE_OFF_DEFAULT_RATIO
        note_duration = max(NOTE_OFF_MIN_DURATION, min(NOTE_OFF_MAX_DURATION, note_duration))
        self.cfg.note_off_schedule[nota_pwm1 if nota_pwm1 > 0 else 60] = current_time + note_duration
        
        # PWM1: Aplicar harmònics o apagar si nota=0
        if nota_pwm1 > 0:
            freq0 = getattr(self.cfg, "freqharm_base", 0)
            note1_final = apply_harmonic_interval(nota_pwm1, freq0)
            note1_final = max(0, min(127, note1_final))
            base_freq = midi_to_frequency(note1_final)
            duty_cycle1 = duty_percent_to_cycle(self.cfg.duty1)
        else:
            base_freq = 440  # Freqüència dummy (no s'escoltarà)
            duty_cycle1 = 0  # APAGAR PWM1
        
        # PWM2: Aplicar harmònics o apagar si nota=0
        if nota_pwm2 > 0:
            note2_temp = apply_harmonic_interval(nota_pwm2, freq1)
            note2_temp = max(0, min(127, note2_temp))
            note2_final = apply_harmonic_interval(note2_temp, self.cfg.freqharm1)
            note2_final = max(0, min(127, note2_final))
            freq2_val = midi_to_frequency(note2_final)
            duty_cycle2 = duty_percent_to_cycle(self.cfg.duty2)
        else:
            freq2_val = 440  # Freqüència dummy
            duty_cycle2 = 0  # APAGAR PWM2
        
        # PWM3: Aplicar harmònics o apagar si nota=0
        if nota_pwm3 > 0:
            note3_temp = apply_harmonic_interval(nota_pwm3, freq2)
            note3_temp = max(0, min(127, note3_temp))
            note3_final = apply_harmonic_interval(note3_temp, self.cfg.freqharm2)
            note3_final = max(0, min(127, note3_final))
            freq3_val = midi_to_frequency(note3_final)
            duty_cycle3 = duty_percent_to_cycle(self.cfg.duty3)
        else:
            freq3_val = 440  # Freqüència dummy
            duty_cycle3 = 0  # APAGAR PWM3
        
        # Aplicar freqüències i duty cycles
        self.hw.pwm1.frequency = base_freq
        self.hw.pwm2.frequency = freq2_val
        self.hw.pwm3.frequency = freq3_val
        self.hw.pwm1.duty_cycle = duty_cycle1
        self.hw.pwm2.duty_cycle = duty_cycle2
        self.hw.pwm3.duty_cycle = duty_cycle3

    def all_notes_off(self):
        """Envia All Notes Off i neteja estat intern."""
        for active_note in list(self.cfg.playing_notes):
            self._stop_note_immediate(active_note)

        try:
            self.hw.midi.send(ControlChange(ALL_NOTES_OFF_CC, 0))
        except Exception as exc:  # pragma: no cover - runtime safeguard
            self._handle_midi_error(exc)

    def _stop_note_immediate(self, note, suppress_midi=False):
        """Apaga immediatament una nota específica i neteja els registres."""
        if note in self.cfg.note_off_schedule:
            del self.cfg.note_off_schedule[note]
        if note in self.cfg.playing_notes:
            self.cfg.playing_notes.remove(note)

        if not suppress_midi and note not in (None, 0):
            try:
                self.hw.midi.send(NoteOff(note, 0))
            except Exception as exc:  # pragma: no cover - runtime safeguard
                self._handle_midi_error(exc)

        self.hw.out_jack.value = False
        self.hw.led_2.value = False
        self.cfg.gate_active = False
        self.cfg.nota_tocada_ara = False

    def _handle_midi_error(self, error):
        """Registra errors MIDI i estableix període de pausa."""
        self.cfg.last_midi_error = repr(error)
        self.cfg.midi_error_count += 1
        pause_until = time.monotonic() + 0.2
        if pause_until > self.cfg.error_pause_until:
            self.cfg.error_pause_until = pause_until
