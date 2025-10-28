# =============================================================================
# SISTEMA RTOS - Real-Time Operating System per TECLA
# =============================================================================
import time
from adafruit_midi.note_off import NoteOff

class RTOSManager:
    """Gestió temporal en temps real amb prioritats"""
    
    def __init__(self, hardware, config):
        self.hw = hardware
        self.cfg = config
    
    def update(self):
        """
        Sistema RTOS amb PRIORIDADES - Gestiona timings crítics en temps real
        
        PRIORIDAD 1 (CRÍTICA): Gate/Trigger temporal
        PRIORIDAD 2 (ALTA): NoteOff programats
        """
        current_time = time.monotonic()
        
        # ===== PRIORIDAD 1: Gestió del Gate temporal (CRÍTICO) =====
        if self.cfg.gate_active and current_time >= self.cfg.gate_off_time:
            self.hw.out_jack.value = False
            self.hw.led_2.value = False
            self.cfg.gate_active = False
        
        # ===== PRIORIDAD 2: Gestió de NoteOff programats (ALTA) =====
        if self.cfg.note_off_schedule:
            notes_to_remove = []
            for note, off_time in self.cfg.note_off_schedule.items():
                if current_time >= off_time:
                    self.hw.midi.send(NoteOff(note, 0))
                    if note in self.cfg.playing_notes:
                        self.cfg.playing_notes.remove(note)
                    notes_to_remove.append(note)
            
            for note in notes_to_remove:
                del self.cfg.note_off_schedule[note]
    
    def stop_all_notes(self):
        """Detiene todas las notas activas"""
        for note in self.cfg.playing_notes:
            self.hw.midi.send(NoteOff(note, 0))
        self.cfg.playing_notes.clear()
        self.cfg.note_off_schedule.clear()
        self.cfg.gate_active = False
        self.hw.out_jack.value = False
        self.hw.led_2.value = False
