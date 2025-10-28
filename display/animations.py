# =============================================================================
# ANIMACIONS - TECLA  
# =============================================================================
# Animaciones para pantalla OLED en TECLA Professional.
# 
# Prevención de errores futuros:
# - Estas animaciones deben ser llamadas desde el bucle principal con buffering doble
#   para evitar bloqueos en el motor de timing (modo tracker).
# - Si una animación falla (e.g., por excepción en display), el sistema debe continuar
#   sin bloquearse: usar try-except en llamadas y fallback a pantalla básica.
# - Ejemplo de integración segura en main.py:
#   try:
#       anim.animacion_ojo()
#   except Exception as e:
#       hw.display.fill(0)
#       hw.display.text("Anim Error", 50, 30, 1)
#       hw.display.show()
# - Mantener animaciones desacopladas: No acceder directamente a variables de timing;
#   usar solo hw y cfg proporcionados.
# =============================================================================
import time
import random
import math
from music.converters import midi_to_note_name

class Animations:
    """Animacions per pantalla OLED"""
    
    def __init__(self, hardware, config):
        self.hw = hardware
        self.cfg = config
    
    def animacion_ojo(self):
        """Animación de ojo en modo inactivo - Muestra parámetros modificados (D1, D2, D3, H1, H2)"""
        self.hw.display.fill(0)  # Limpiar pantalla
        
        # Valores por defecto
        DUTY_DEFAULT = 50
        HARM_DEFAULT = 0
        CV_MAX = 3.3  # Valor máximo para CV (3.3V) - Mantenido para posibles usos futuros
        
        # Lista de parámetros modificados
        params = []
        
        # Verificar parámetros modificados (solo D1, D2, D3, H1, H2)
        if self.cfg.duty1 != DUTY_DEFAULT:
            params.append("D1")
        if self.cfg.duty2 != DUTY_DEFAULT:
            params.append("D2")
        if self.cfg.duty3 != DUTY_DEFAULT:
            params.append("D3")
        if self.cfg.freqharm1 != HARM_DEFAULT:
            params.append("H1")
        if self.cfg.freqharm2 != HARM_DEFAULT:
            params.append("H2")
        
        # Mostrar parámetros modificados en la parte superior (sin CV1 y CV2)
        if params:
            param_text = " ".join(params)
            # Asegurarse de que el texto no sea demasiado ancho
            if len(param_text) > 20:  # Aproximadamente el ancho máximo
                param_text = param_text[:17] + "..."
            self.hw.display.text(param_text, 2, 2, 1)
        
        # Animación del ojo
        cx, cy, r = 64, 40, 15  # Ojo más abajo para dejar espacio al texto
        t = time.monotonic()
        fase = int((t % 4.0) * 2)
        
        # Contorno del ojo
        self.hw.display.circle(cx, cy, r, 1)
        
        # Animación de la pupila
        if fase in [1, 4]:
            self.hw.display.hline(cx - r, cy, r * 2, 1)
        else:
            if fase in [0, 7]:
                pupila_x, pupila_y = cx, cy
            elif fase in [2, 3]:
                pupila_x, pupila_y = cx - 8, cy
            else:
                pupila_x, pupila_y = cx + 8, cy
            self.hw.display.circle(pupila_x, pupila_y, 5, 1)
        
        # Indicador del modo config activo (si es necesario)
        if hasattr(self.cfg, 'configout') and self.cfg.configout is not None:
            config_names = ["Mode", "Dty1", "Dty2", "Dty3", "H1", "H2", "CV1", "CV2"]
            if 0 <= self.cfg.configout < len(config_names):
                config_text = config_names[self.cfg.configout]
                text_width = len(config_text) * 6
                self.hw.display.text(config_text, (128 - text_width) // 2, 56, 1)
        
        self.hw.display.show()
        time.sleep(0.1)
    
    def dibujar_rayo_simple(self):
        """Raig espectacular a PANTALLA COMPLETA - només quan nota toca"""
        # Raig principal vertical amb desviacions horitzonals
        x = 64  # Començar al centre
        y = 0
        
        while y < 64:
            # Pre-calcular randoms per eficiència
            x_offset = random.randint(-8, 8)
            y_step = random.randint(3, 6)
            rand_val = random.randint(0, 100)
            
            x_new = max(10, min(118, x + x_offset))  # Mantenir dins límits
            y_next = y + y_step
            
            # Línia principal del raig
            self.hw.display.line(x, y, x_new, y_next, 1)
            
            # Branques laterals aleatòries (20% probabilitat)
            if rand_val < 20:
                branch_len = random.randint(8, 20)
                branch_angle = 1 if rand_val < 10 else -1  # Esquerra/dreta sense choice()
                self.hw.display.line(x_new, y, x_new + (branch_len * branch_angle), y + y_step + 2, 1)
            
            # Efecte de gruix (50% probabilitat)
            elif rand_val < 70:  # Reutilitzar rand_val
                self.hw.display.line(x + 1, y, x_new + 1, y_next, 1)
            
            # Branques secundàries més petites (10% probabilitat)
            elif rand_val < 80:
                mini_branch = random.randint(4, 10)
                mini_angle = 1 if rand_val < 75 else -1
                self.hw.display.line(x_new, y + 2, x_new + (mini_branch * mini_angle), y + 4, 1)
            
            # Actualitzar posició
            x = x_new
            y = y_next
        
        # Flash al final (impacte a la base)
        for i in range(3):
            flash_x = x + random.randint(-10, 10)
            flash_size = random.randint(3, 8)
            self.hw.display.hline(flash_x - flash_size, 63, flash_size * 2, 1)
            self.hw.display.vline(flash_x, 63 - flash_size, flash_size, 1)
    
    def mostrar_idle_con_simbolo(self, loop_mode):
        """Pantalla idle amb símbol del mode + barres CV"""
        from music.converters import get_voltage_calibrated, get_voltage_percentage
        
        self.hw.display.fill(0)
        
        # Llegir voltatges reals
        cv1_val_raw = self.hw.get_voltage(self.hw.pote_velocidad)
        cv2_val_raw = self.hw.get_voltage(self.hw.pote_analog_2)
        
        # Aplicar CV range (clamping)
        cv1_val = get_voltage_calibrated(cv1_val_raw, self.cfg.cv1_min, self.cfg.cv1_max)
        cv2_val = get_voltage_calibrated(cv2_val_raw, self.cfg.cv2_min, self.cfg.cv2_max)
        
        # Calcular percentatges dins el rang CV configurat
        cv1_pct = get_voltage_percentage(cv1_val_raw, self.cfg.cv1_min, self.cfg.cv1_max)
        cv2_pct = get_voltage_percentage(cv2_val_raw, self.cfg.cv2_min, self.cfg.cv2_max)
        
        # Barres laterals (fines 4px)
        bar_height = 60
        bar_y_start = 2
        
        # CV1 - Esquerra
        cv1_bar_h = int((cv1_pct / 100.0) * bar_height)
        self.hw.display.rect(2, bar_y_start, 4, bar_height, 1)  # Marco
        if cv1_bar_h > 0:
            self.hw.display.fill_rect(3, bar_y_start + bar_height - cv1_bar_h, 2, cv1_bar_h, 1)
        
        # CV2 - Dreta
        cv2_bar_h = int((cv2_pct / 100.0) * bar_height)
        self.hw.display.rect(122, bar_y_start, 4, bar_height, 1)  # Marco
        if cv2_bar_h > 0:
            self.hw.display.fill_rect(123, bar_y_start + bar_height - cv2_bar_h, 2, cv2_bar_h, 1)
        
        # Símbol central segons loop mode
        self._dibujar_simbolo_mode(loop_mode)
        
        # Nom mode i nota actual abaix
        mode_names = {
            1: "Fractal", 2: "Riu", 3: "Tempesta", 4: "Harmonia",
            5: "Bosc", 6: "Escala", 7: "Euclidia", 8: "Cosmos", 9: "Sequencer"
        }
        mode_name = mode_names.get(loop_mode, "---")
        note_name = midi_to_note_name(self.cfg.nota_actual)
        
        # Mode nom centrat
        text_w = len(mode_name) * 6
        self.hw.display.text(mode_name, (128 - text_w) // 2, 50, 1)
        
        # Nota actual centrada abaix
        note_w = len(note_name) * 6
        self.hw.display.text(note_name, (128 - note_w) // 2, 58, 1)
        
        self.hw.display.show()
    
    def _dibujar_simbolo_mode(self, mode):
        """Dibuixa símbol representatiu per cada mode"""
        cx, cy = 64, 28  # Centre pantalla
        
        if mode == 1:  # Fractal - Triangle fractal
            self.hw.display.line(cx, cy - 12, cx - 12, cy + 8, 1)
            self.hw.display.line(cx, cy - 12, cx + 12, cy + 8, 1)
            self.hw.display.line(cx - 12, cy + 8, cx + 12, cy + 8, 1)
            self.hw.display.line(cx - 6, cy - 2, cx + 6, cy - 2, 1)
            
        elif mode == 2:  # Rio - Ones fluides
            t_anim = time.monotonic() * 20  # Calcular una sola vegada
            for i in range(0, 40, 2):
                y_offset = int(5 * math.sin((i + t_anim) * 0.3))
                self.hw.display.pixel(cx - 20 + i, cy + y_offset, 1)
            
        elif mode == 3:  # Tormenta - Raig gran
            self.hw.display.line(cx, cy - 15, cx - 3, cy - 5, 1)
            self.hw.display.line(cx - 3, cy - 5, cx + 5, cy - 5, 1)
            self.hw.display.line(cx + 5, cy - 5, cx, cy + 5, 1)
            self.hw.display.line(cx, cy + 5, cx + 3, cy, 1)
            self.hw.display.line(cx + 3, cy, cx - 5, cy, 1)
            self.hw.display.line(cx - 5, cy, cx, cy + 15, 1)
            
        elif mode == 4:  # Harmonia - Notes musicals
            # Rodona nota
            self.hw.display.circle(cx - 8, cy, 4, 1)
            self.hw.display.vline(cx - 4, cy - 12, 12, 1)
            # Segona nota
            self.hw.display.circle(cx + 6, cy + 3, 3, 1)
            self.hw.display.vline(cx + 9, cy - 8, 11, 1)
            
        elif mode == 5:  # Bosque - Arbre
            self.hw.display.line(cx, cy + 10, cx, cy - 10, 1)  # Tronc
            # Branques
            self.hw.display.line(cx, cy - 5, cx - 8, cy - 12, 1)
            self.hw.display.line(cx, cy - 5, cx + 8, cy - 12, 1)
            self.hw.display.line(cx, cy, cx - 6, cy - 8, 1)
            self.hw.display.line(cx, cy, cx + 6, cy - 8, 1)
            
        elif mode == 6:  # Escala CV - Gràfic escalera
            for i in range(5):
                y = cy - 10 + i * 5
                x_offset = i * 4
                self.hw.display.hline(cx - 15 + x_offset, y, 8, 1)
                self.hw.display.vline(cx - 15 + x_offset + 8, y, 5, 1)
            
        elif mode == 7:  # Euclidià - Cercle amb punts
            self.hw.display.circle(cx, cy, 12, 1)
            angles = [0, 45, 90, 135, 180, 225, 270, 315]
            for angle in angles:
                rad = math.radians(angle)
                px = int(cx + 8 * math.cos(rad))
                py = int(cy + 8 * math.sin(rad))
                self.hw.display.fill_rect(px - 1, py - 1, 2, 2, 1)
            
        elif mode == 8:  # Cosmos - Espiral galàctica
            for i in range(0, 360, 15):
                rad = math.radians(i)
                r = 3 + i / 60
                px = int(cx + r * math.cos(rad))
                py = int(cy + r * math.sin(rad))
                self.hw.display.pixel(px, py, 1)
            
        elif mode == 9:  # Sequencer - Graella de steps
            # Dibuixar 8 quadrats (representant steps del sequencer)
            step_width = 4
            step_spacing = 6
            start_x = cx - 18
            
            for i in range(8):
                x = start_x + i * step_spacing
                # Marcar step actual amb quadrat ple
                if i == self.cfg.sequencer_edit_position % 8:
                    self.hw.display.fill_rect(x, cy - 2, step_width, 4, 1)
    def animacion_gameboy_tracker(self):
        """Animación de consola Game Boy fija con pupila del ojo en la pantalla (combinación creativa)"""
        self.hw.display.fill(0)
        
        # Posición fija centrada (sin oscilación)
        base_x = 40  # Centrado en 128 píxeles
        base_y = 10  # Posición vertical fija
        
        # Marco de la consola (contorno de GameBoy)
        self.hw.display.rect(base_x, base_y, 48, 64-10, 1)  # Cuerpo rectangular
        
        # Pantalla de la GameBoy
        screen_x = base_x + 6
        screen_y = base_y + 4
        screen_width = 36
        screen_height = 24
        self.hw.display.rect(screen_x, screen_y, screen_width, screen_height, 1)
        
        # Pupila del ojo integrada en la pantalla (combinada con GameBoy)
        t = time.monotonic()
        fase = int((t % 4.0) * 2)  # 8 fases de 0.5s
        
        # Centro de la pupila en la pantalla
        pupila_cx = screen_x + screen_width // 2
        pupila_cy = screen_y + screen_height // 2
        
        # Dibujar pupila según fase (adaptada del ojo)
        if fase == 0 or fase == 7:  # Mirando al frente
            pupila_x, pupila_y = pupila_cx, pupila_cy
        elif fase == 1 or fase == 4:  # Parpadeo (línea horizontal)
            self.hw.display.hline(pupila_cx - screen_width // 4, pupila_cy, screen_width // 2, 1)
            pupila_x, pupila_y = pupila_cx, pupila_cy
        elif fase == 2 or fase == 3:  # Mirando a la izquierda
            pupila_x, pupila_y = pupila_cx - 5, pupila_cy
        elif fase == 5 or fase == 6:  # Mirando a la derecha
            pupila_x, pupila_y = pupila_cx + 5, pupila_cy
        
        # Dibujar pupila (si no está parpadeando)
        if fase not in [1, 4]:
            self.hw.display.circle(pupila_x, pupila_y, 3, 1)
        
        # Cruceta (D-pad)
        cx, cy = base_x + 12, base_y + 36
        self.hw.display.vline(cx, cy - 3, 7, 1)
        self.hw.display.hline(cx - 3, cy, 7, 1)
        
        # Botones A y B
        self.hw.display.circle(base_x + 32, base_y + 36, 2, 1)  # Botón A
        self.hw.display.circle(base_x + 38, base_y + 30, 2, 1)  # Botón B
        
        # Start y Select (dos rayitas)
        self.hw.display.hline(base_x + 18, base_y + 46, 6, 1)
        self.hw.display.hline(base_x + 28, base_y + 46, 6, 1)
        
        self.hw.display.show()
