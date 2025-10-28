# =============================================================================
# SCREENS - TECLA Display Manager
# =============================================================================
import time
from music.converters import midi_to_note_name
from core.config import CV_RANGE_PRESETS

# Constants de timing per display - Adaptades a resposta humana
IDLE_SUMMARY_START = 6.0  # Iniciar resum complet després de 6s (més relaxat)
IDLE_SUMMARY_END = 9.0    # Finalitzar resum complet després de 9s

class ScreenManager:
    """Gestió de pantalles amb renderització diferencial"""
    
    # Noms dels modes musicals en català
    LOOP_NAMES = {
        0: "Pausa",        # Mode aturat
        1: "Fractal",      # Mode fractal Mandelbrot
        2: "Riu",          # Mode fluid i orgànic
        3: "Tempesta",     # Mode dinàmic amb llamps
        4: "Harmonia",     # Progressions harmòniques
        5: "Bosc",         # Mode orgànic impredictible
        6: "Escala CV",    # Quantitzador d'escales
        7: "Euclidia",     # Ritmes algorítmics
        8: "Cosmos",       # Síntesi híbrida complexa
        9: "Sequencer"     # Seqüenciador programable
    }
    
    # Noms dels intervals harmònics en català
    HARMONIC_NAMES = {
        0: "Uníson",       # Mateixa nota
        1: "Octava",       # 12 semitons
        2: "Quinta",       # 7 semitons
        3: "Quarta",       # 5 semitons
        4: "Tercera M",    # 4 semitons (major)
        5: "Tercera m",    # 3 semitons (menor)
        6: "Sexta M",      # 9 semitons (major)
        7: "Sèptima",      # 11 semitons
        8: "Trítono"       # 6 semitons (diabolus in musica)
    }
    
    # Noms dels paràmetres de configuració
    CONFIG_NAMES = ["Mode", "Cicle1", "Cicle2", "Cicle3", "H0", "H1", "H2", "CV1", "CV2"]
    
    def __init__(self, hardware, config):
        self.hw = hardware
        self.cfg = config
    
    def mostrar_info_loop_mode(self):
        """Pantalla principal - OPTIMITZAT amb menys informació"""
        current_time = time.monotonic()
        inactive_time = current_time - self.cfg.last_interaction_time
        
        # Després de 5s d'inactivitat: mostrar resum complet breument
        if IDLE_SUMMARY_START < inactive_time < IDLE_SUMMARY_END:
            self._mostrar_resum_complet()
        # Abans de 5s: mostrar només paràmetre configurat
        elif inactive_time <= IDLE_SUMMARY_START:
            self._mostrar_param_actual()
    
    def _mostrar_param_actual(self):
        """Mostra només el paràmetre que s'està configurant - MÍNIM"""
        note_name = midi_to_note_name(self.cfg.nota_actual)
        
        # Sistema sense cache per fluïdesa igual a pantalla idle
        # Actualitza cada 100ms com mostrar_idle_con_simbolo
        if True:  # Sempre actualitza (com pantalla idle)
            self.hw.display.fill(0)
            
            # LÍNIA 1: Mode actual (gran)
            if self.cfg.configout == 0:
                mode_name = self.LOOP_NAMES.get(self.cfg.loop_mode, 'Pausa')
                self.hw.display.text(mode_name, 10, 20, 2)  # Font gran
            
            # LÍNIA 2: Paràmetre configurat
            elif self.cfg.configout == 1:
                self.hw.display.text("CICLE 1", 25, 10, 1)
                self.hw.display.text(f"{self.cfg.duty1}%", 40, 30, 2)
            elif self.cfg.configout == 2:
                self.hw.display.text("CICLE 2", 25, 10, 1)
                self.hw.display.text(f"{self.cfg.duty2}%", 40, 30, 2)
            elif self.cfg.configout == 3:
                self.hw.display.text("CICLE 3", 25, 10, 1)
                self.hw.display.text(f"{self.cfg.duty3}%", 40, 30, 2)
            elif self.cfg.configout == 4:
                self.hw.display.text("HARMONIC 0", 10, 10, 1)
                harm_name = self.HARMONIC_NAMES.get(self.cfg.freqharm_base, '---')
                self.hw.display.text(harm_name, 10, 30, 1)
            elif self.cfg.configout == 5:
                self.hw.display.text("HARMONIC 1", 10, 10, 1)
                harm_name = self.HARMONIC_NAMES.get(self.cfg.freqharm1, '---')
                self.hw.display.text(harm_name, 10, 30, 1)
            elif self.cfg.configout == 6:
                self.hw.display.text("HARMONIC 2", 10, 10, 1)
                harm_name = self.HARMONIC_NAMES.get(self.cfg.freqharm2, '---')
                self.hw.display.text(harm_name, 10, 30, 1)
            elif self.cfg.configout == 7:
                _, _, range_name = CV_RANGE_PRESETS[self.cfg.cv1_range_config]
                self.hw.display.text("CV1 RANGE", 20, 10, 1)
                self.hw.display.text(range_name, 25, 30, 1)
            elif self.cfg.configout == 8:
                _, _, range_name = CV_RANGE_PRESETS[self.cfg.cv2_range_config]
                self.hw.display.text("CV2 RANGE", 20, 10, 1)
                self.hw.display.text(range_name, 25, 30, 1)
            
            # LÍNIA 3: Nota actual (petita, abaix)
            self.hw.display.text(f"Oct:{self.cfg.octava} {note_name}", 30, 54, 1)
            
            self.hw.display.show()
    
    def _mostrar_resum_complet(self):
        """Mostra resum complet durant 3s abans d'animació"""
        from music.converters import get_voltage_calibrated, get_voltage_percentage
        
        # Llegir voltatges reals
        cv1_val_raw = self.hw.get_voltage(self.hw.pote_velocidad)
        cv2_val_raw = self.hw.get_voltage(self.hw.pote_analog_2)
        
        # Aplicar CV range (clamping)
        cv1_val = get_voltage_calibrated(cv1_val_raw, self.cfg.cv1_min, self.cfg.cv1_max)
        cv2_val = get_voltage_calibrated(cv2_val_raw, self.cfg.cv2_min, self.cfg.cv2_max)
        
        # Calcular percentatges dins el rang CV configurat
        cv1_pct = get_voltage_percentage(cv1_val_raw, self.cfg.cv1_min, self.cfg.cv1_max)
        cv2_pct = get_voltage_percentage(cv2_val_raw, self.cfg.cv2_min, self.cfg.cv2_max)
        
        self.hw.display.fill(0)
        self.hw.display.text(f"Mod:{self.LOOP_NAMES.get(self.cfg.loop_mode, '?')}", 0, 0, 1)
        self.hw.display.text(f"D:{self.cfg.duty1}/{self.cfg.duty2}/{self.cfg.duty3}", 0, 10, 1)
        self.hw.display.text(f"H0:{self.cfg.freqharm_base} H1:{self.cfg.freqharm1} H2:{self.cfg.freqharm2}", 0, 20, 1)
        self.hw.display.text(f"CV1:{cv1_val:0.2f}V {cv1_pct}%", 0, 30, 1)
        self.hw.display.text(f"CV2:{cv2_val:0.2f}V {cv2_pct}%", 0, 40, 1)
        self.hw.display.text(f"Oct:{self.cfg.octava}", 0, 50, 1)
        self.hw.display.show()
    
    def mostrar_tracker_edit(self):
        """Pàgina 0: Edició notes i gates"""
        self.hw.display.fill(0)
        
        # Capçalera: TRK L:16 S:08/16
        length = min(self.cfg.sequencer_length, 32)
        play_pos = self.cfg.sequencer_play_position % length
        edit_pos = min(self.cfg.sequencer_edit_position, length - 1, 31)
        
        header = f"TRK L:{length:02d} S:{edit_pos:02d}/{length:02d}"
        self.hw.display.text(header, 0, 0, 1)
        self.hw.display.hline(0, 8, 128, 1)
        
        # Mostrar 6 steps visibles
        start_step = max(0, min(edit_pos - 2, length - 6))
        
        for i in range(6):
            step_num = start_step + i
            if step_num >= length or step_num >= 32:  # Protecció doble
                break
            
            y = 12 + (i * 8)
            
            # Número step
            self.hw.display.text(f"{step_num:02d}", 0, y, 1)
            
            # Play indicator
            if step_num == play_pos:
                self.hw.display.text(">", 14, y, 1)
            
            # Nota (amb protecció)
            note_midi = self.cfg.sequencer_pattern[step_num]
            note_name = midi_to_note_name(note_midi)
            self.hw.display.text(note_name, 20, y, 1)
            
            # Gate (texto personalizado: OFF/ON)
            gate = self.cfg.sequencer_gate[step_num]
            if gate == 0:
                gate_text = "OFF"
            elif gate == 50:
                gate_text = "ON"
            else:
                gate_text = "ERR"  # Error si no es 0 o 50
            self.hw.display.text(gate_text, 48, y, 1)
            
            # Cursor edició
            if step_num == edit_pos:
                self.hw.display.rect(18, y-1, 60, 9, 1)
        
        # Mostrar solo CV1 o CV2 en la esquina inferior derecha
        pot_text = f"CV{self.cfg.sequencer_note_pot}"
        self.hw.display.text(pot_text, 100, 58, 1)  # Esquina inferior derecha
        
        # Indicador de modo edición (si está activo)
        if self.cfg.sequencer_note_edit_mode:
            self.hw.display.text("EDIT", 0, 58, 1)  # Esquina inferior izquierda
            
        self.hw.display.show()
    
    def mostrar_tracker_length(self):
        """Pàgina 1: Ajustar longitud"""
        self.hw.display.fill(0)
        self.hw.display.text("LONGITUD PATRO", 10, 10, 1)
        
        # Barra visual
        length = self.cfg.sequencer_length
        bar_w = int((length - 8) * 3.84)  # 8-32 → 0-92px
        self.hw.display.rect(16, 30, 96, 10, 1)
        if bar_w > 0:
            self.hw.display.fill_rect(16, 30, bar_w, 10, 1)
        
        # Número gran
        length_text = f"{length}"
        text_w = len(length_text) * 12
        self.hw.display.text(length_text, (128 - text_w) // 2, 44, 2)
        
        self.hw.display.text("^v:Ajustar", 25, 58, 1)
        self.hw.display.show()
    
    def mostrar_tracker_info(self):
        """Pàgina 2: Info Duty/Harm/Oct"""
        from music.converters import get_voltage_percentage
        
        self.hw.display.fill(0)
        self.hw.display.text("CONFIG ACTUAL", 15, 0, 1)
        self.hw.display.hline(0, 8, 128, 1)
        
        self.hw.display.text(f"Dty:{self.cfg.duty1}/{self.cfg.duty2}/{self.cfg.duty3}", 0, 12, 1)
        self.hw.display.text(f"Hrm:{self.cfg.freqharm_base}/{self.cfg.freqharm1}/{self.cfg.freqharm2}", 0, 22, 1)
        self.hw.display.text(f"Oct: {self.cfg.octava}", 0, 32, 1)
        
        # CV percentatges
        try:
            cv1_raw = self.hw.get_voltage(self.hw.pote_analog_1)
            cv1_pct = get_voltage_percentage(cv1_raw, self.cfg.cv1_min, self.cfg.cv1_max)
            self.hw.display.text(f"VEL:{cv1_pct}%", 0, 42, 1)
        except:
            pass
        
        self.hw.display.text("E1:Tornar", 25, 58, 1)
        self.hw.display.show()
    
    def mostrar_sequencer_tracker(self):
        """Router segons pàgina activa"""
        if self.cfg.sequencer_page == 0:
            self.mostrar_tracker_edit()
        elif self.cfg.sequencer_page == 1:
            self.mostrar_tracker_length()
        elif self.cfg.sequencer_page == 2:
            self.mostrar_tracker_info()
    
    def _get_current_config_value(self):
        """Retorna valor actual del paràmetre configurat"""
        if self.cfg.configout == 0:
            return self.cfg.loop_mode
        elif self.cfg.configout == 1:
            return self.cfg.duty1
        elif self.cfg.configout == 2:
            return self.cfg.duty2
        elif self.cfg.configout == 3:
            return self.cfg.duty3
        elif self.cfg.configout == 4:
            return self.cfg.freqharm_base
        elif self.cfg.configout == 5:
            return self.cfg.freqharm1
        elif self.cfg.configout == 6:
            return self.cfg.freqharm2
        elif self.cfg.configout == 7:
            return self.cfg.cv1_range_config
        elif self.cfg.configout == 8:
            return self.cfg.cv2_range_config
        return 0
    
    def mostrar_loop_mode_animat(self):
        """Mostra animació ASCII per cada loop mode"""
        self.hw.display.fill(0)
        mode_name = self.LOOP_NAMES.get(self.cfg.loop_mode, '---')
        
        # ASCII art simple amb lletres per cada mode
        if self.cfg.loop_mode == 1:  # Fractal
            self.hw.display.text("/\\", 60, 15, 1)
            self.hw.display.text("/  \\", 56, 25, 1)
            self.hw.display.text("/__\\", 56, 35, 1)
        elif self.cfg.loop_mode == 2:  # Rio
            self.hw.display.text("~~~", 52, 25, 1)
            self.hw.display.text(" ~~~", 52, 35, 1)
        elif self.cfg.loop_mode == 3:  # Tormenta
            self.hw.display.text("||", 62, 15, 1)
            self.hw.display.text("\\/", 62, 25, 1)
        elif self.cfg.loop_mode >= 4:  # Altres
            self.hw.display.text("*", 60, 20, 2)
            self.hw.display.text("*", 56, 30, 1)
            self.hw.display.text("*", 68, 30, 1)
        
        self.hw.display.text(mode_name, 10, 50, 1)
        self.hw.display.show()
    
    def mostrar_calibracion_cv(self):
        """Pantalla calibració CV"""
        self.hw.display.fill(0)
        
        cv1_actual = self.hw.get_voltage(self.hw.pote_velocidad)
        cv2_actual = self.hw.get_voltage(self.hw.pote_analog_2)
        
        self.hw.display.text("CALIBRACIO CV", 10, 0, 1)
        self.hw.display.hline(0, 10, 128, 1)
        self.hw.display.text("CV1 (Slider):", 0, 15, 1)
        self.hw.display.text(f"{cv1_actual:.2f}V", 80, 15, 1)
        self.hw.display.text(f"Min:{self.cfg.cv1_min:.2f}", 0, 25, 1)
        self.hw.display.text(f"Max:{self.cfg.cv1_max:.2f}", 70, 25, 1)
        
        self.hw.display.text("CV2 (LDR):", 0, 38, 1)
        self.hw.display.text(f"{cv2_actual:.2f}V", 80, 38, 1)
        self.hw.display.text(f"Min:{self.cfg.cv2_min:.2f}", 0, 48, 1)
        self.hw.display.text(f"Max:{self.cfg.cv2_max:.2f}", 70, 48, 1)
        
        self.hw.display.text("BTN: 1/2=CV1 3/4=CV2", 0, 58, 1)
        self.hw.display.show()
