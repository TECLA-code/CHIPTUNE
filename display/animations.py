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
from music.converters import midi_to_note_name  # Note: No longer used in idle animation

class Animations:
    """Animacions per pantalla OLED"""
    
    def __init__(self, hardware, config):
        self.hw = hardware
        self.cfg = config
    
    def animacion_ojo(self):
        """Animación de ojo en modo inactivo con 24 frames - Muestra parámetros modificados"""
        self.hw.display.fill(0)  # Limpiar pantalla
        
        # Valores por defecto
        DUTY_DEFAULT = 50
        HARM_DEFAULT = 0
        
        # Lista de parámetros modificados
        params = []
        
        # Verificar parámetros modificados
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
        
        # Mostrar parámetros modificados en la parte superior
        if params:
            param_text = " ".join(params)
            if len(param_text) > 20:
                param_text = param_text[:17] + "..."
            self.hw.display.text(param_text, 2, 2, 1)
        
        # ANIMACIÓ ÈPICA: 30 segons en 3 parts
        # Part 1 (2s): Despertar | Part 2 (25s): Mirar suau | Part 3 (3s): Megaglitch
        cx, cy, r = 64, 32, 26  # ULL GEGANT
        t = time.monotonic()
        fase = int((t * 10) % 300)  # 300 frames, cicle de 30 segons
        
        # Contorno del ojo GEGANT
        self.hw.display.circle(cx, cy, r, 1)
        
        # Funció helper per omplir cercle manualment
        def dibuixar_pupila(px, py, radi):
            for dy in range(-radi, radi + 1):
                for dx in range(-radi, radi + 1):
                    if dx*dx + dy*dy <= radi*radi:
                        if 0 <= px + dx < 128 and 0 <= py + dy < 64:
                            self.hw.display.pixel(px + dx, py + dy, 1)
        
        # Funció helper per afegir iris (anells al voltant de la pupil·la)
        def dibuixar_iris(px, py):
            # Anells de l'iris
            for radius in [8, 12, 16, 20]:  # Iris més gran (abans 10,14,18)
                for angle in range(0, 360, 12):
                    import math
                    rad = math.radians(angle)
                    ix = int(px + radius * math.cos(rad))
                    iy = int(py + radius * math.sin(rad))
                    if 0 <= ix < 128 and 0 <= iy < 64:
                        self.hw.display.pixel(ix, iy, 1)
        
        # Funció helper per afegir reflex (punt blanc)
        def dibuixar_reflex(px, py):
            for dx in [-2, -1, 0]:
                for dy in [-2, -1]:
                    if 0 <= px + dx < 128 and 0 <= py + dy < 64:
                        self.hw.display.pixel(px + dx, py + dy, 0)
        
        # === PART 1: DESPERTAR (0-19) - 2 segons ===
        if fase >= 0 and fase < 20:
            # Creixement gradual de la pupil·la
            pupila_size = min(5, fase // 3)  # Creix fins a 5
            dibuixar_pupila(cx, cy, pupila_size)
            if fase > 10:
                dibuixar_reflex(cx - 1, cy - 1)
        
        # === PART 2: MIRAR AL VOLTANT (20-269) - 25 segons SUAU ===
        elif fase >= 20 and fase < 270:
            import math
            # Moviment suau amb funcions sin/cos
            frame_rel = fase - 20  # 0-249
            
            # Patró de moviment suau amb diverses fases
            angle_slow = (frame_rel / 250.0) * 360 * 3  # 3 voltes completes en 25s
            angle_fast = (frame_rel / 250.0) * 360 * 8  # 8 voltes ràpides
            
            # Combinar moviments per varietat
            offset_x = int(10 * math.sin(math.radians(angle_slow)) + 
                          3 * math.cos(math.radians(angle_fast)))
            offset_y = int(8 * math.cos(math.radians(angle_slow * 0.7)) + 
                          2 * math.sin(math.radians(angle_fast * 1.3)))
            
            # Parpelles ocasionals (cada ~4 segons)
            if frame_rel % 40 == 38 or frame_rel % 40 == 39:
                # Parpella
                self.hw.display.hline(cx - r, cy, r * 2, 1)
                if frame_rel % 40 == 39:
                    self.hw.display.hline(cx - r, cy - 1, r * 2, 1)
                    self.hw.display.hline(cx - r, cy + 1, r * 2, 1)
            else:
                # Dibuixar ull normal amb moviment suau (sense iris)
                dibuixar_pupila(cx + offset_x, cy + offset_y, 5)  # Pupil·la més gran (abans 3)
                dibuixar_reflex(cx + offset_x - 2, cy + offset_y - 2)
        
        # === PART 3: MEGAGLITCH (270-299) - 3 segons ===
        elif fase >= 270:
            frame_glitch = fase - 270  # 0-29
            
            if frame_glitch == 0:
                # Pupil·la normal abans del caos
                dibuixar_pupila(cx, cy, 5)
                dibuixar_reflex(cx - 2, cy - 2)
            
            elif frame_glitch == 1:
                # Comença distorsió
                dibuixar_pupila(cx - 2, cy, 5)
                dibuixar_pupila(cx + 2, cy, 5)
            
            elif frame_glitch == 2:
                # DUES PUPIL·LES
                dibuixar_pupila(cx - 8, cy, 6)
                dibuixar_pupila(cx + 8, cy, 6)
            
            elif frame_glitch == 3:
                # TRES PUPIL·LES
                dibuixar_pupila(cx, cy - 12, 4)
                dibuixar_pupila(cx, cy, 6)
                dibuixar_pupila(cx, cy + 12, 4)
            
            elif frame_glitch == 4:
                # QUATRE PUPIL·LES
                dibuixar_pupila(cx - 10, cy - 10, 5)
                dibuixar_pupila(cx + 10, cy - 10, 5)
                dibuixar_pupila(cx - 10, cy + 10, 5)
                dibuixar_pupila(cx + 10, cy + 10, 5)
            
            elif frame_glitch == 5:
                # SIS PUPIL·LES (cercle)
                import math
                for i in range(6):
                    angle = i * 60
                    rad = math.radians(angle)
                    px = int(cx + 12 * math.cos(rad))
                    py = int(cy + 12 * math.sin(rad))
                    dibuixar_pupila(px, py, 4)
            
            elif frame_glitch == 6:
                # Cercles caòtics
                dibuixar_pupila(cx, cy, 10)
                self.hw.display.circle(cx, cy, 6, 1)
                self.hw.display.circle(cx, cy, 14, 1)
                self.hw.display.circle(cx, cy, 18, 1)
                self.hw.display.circle(cx, cy, 22, 1)
            
            elif frame_glitch == 7:
                # Espiral
                import math
                for i in range(0, 360, 20):
                    rad = math.radians(i)
                    r_spiral = 3 + i / 30.0
                    px = int(cx + r_spiral * math.cos(rad))
                    py = int(cy + r_spiral * math.sin(rad))
                    if 0 <= px < 128 and 0 <= py < 64:
                        dibuixar_pupila(px, py, 2)
            
            elif frame_glitch == 8:
                # Inversió 25%
                dibuixar_pupila(cx, cy, 9)
                for x in range(0, 128, 4):
                    for y in range(0, 64, 4):
                        self.hw.display.pixel(x, y, 0)
            
            elif frame_glitch == 9:
                # Inversió 50%
                dibuixar_pupila(cx, cy, 10)
                for x in range(0, 128, 2):
                    for y in range(0, 64, 2):
                        if (x + y) % 4 == 0:
                            self.hw.display.pixel(x, y, 0)
            
            elif frame_glitch == 10:
                # Inversió 75%
                for x in range(0, 128, 2):
                    for y in range(0, 64, 2):
                        self.hw.display.pixel(x, y, 0)
                dibuixar_pupila(cx - 12, cy, 5)
                dibuixar_pupila(cx + 12, cy, 5)
            
            elif frame_glitch >= 11 and frame_glitch <= 15:
                # INVERSIÓ COMPLETA (5 frames)
                self.hw.display.fill(1)  # Tot blanc
                self.hw.display.circle(cx, cy, r, 0)  # Ull negre
                # Pupil·la blanca (píxels negres = 0)
                for dy in range(-6, 7):
                    for dx in range(-6, 7):
                        if dx*dx + dy*dy <= 36:
                            if 0 <= cx + dx < 128 and 0 <= cy + dy < 64:
                                self.hw.display.pixel(cx + dx, cy + dy, 0)
            
            elif frame_glitch == 16:
                # Tornada amb glitch
                dibuixar_pupila(cx, cy, 8)
                # Línies verticals glitch
                for i in range(0, 128, 6):
                    self.hw.display.vline(i, 0, 64, 1)
            
            elif frame_glitch == 17:
                # Glitch horitzontal
                dibuixar_pupila(cx, cy, 7)
                for i in range(0, 64, 4):
                    self.hw.display.hline(0, i, 128, 1)
            
            elif frame_glitch == 18:
                # Pupil·les tremoloses
                dibuixar_pupila(cx - 3, cy - 2, 5)
                dibuixar_pupila(cx + 1, cy + 1, 6)
            
            elif frame_glitch == 19:
                # Més pupil·les caòtiques
                for i in range(8):
                    import math
                    angle = i * 45 + (frame_glitch * 10)
                    rad = math.radians(angle)
                    px = int(cx + 10 * math.cos(rad))
                    py = int(cy + 10 * math.sin(rad))
                    dibuixar_pupila(px, py, 3)
            
            elif frame_glitch >= 20 and frame_glitch <= 24:
                # Reset gradual (5 frames)
                size = 9 - (frame_glitch - 20)
                dibuixar_pupila(cx, cy, size)
                if frame_glitch > 22:
                    dibuixar_reflex(cx - 2, cy - 2)
            
            else:
                # Final suau (25-29)
                dibuixar_pupila(cx, cy, 5)
                dibuixar_reflex(cx - 2, cy - 2)
        
        # Indicador del modo config activo
        if hasattr(self.cfg, 'configout') and self.cfg.configout is not None:
            config_names = ["Mode", "Dty1", "Dty2", "Dty3", "H1", "H2", "H3"]
            if 0 < self.cfg.configout < len(config_names):
                config_text = config_names[self.cfg.configout]
                text_width = len(config_text) * 6
                self.hw.display.text(config_text, (128 - text_width) // 2, 56, 1)
        
        self.hw.display.show()
        time.sleep(0.1)  # Manté 100ms per frame (sortida ràpida possible)
    
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
        """Pantalla idle amb símbol del mode + barres CV (ultra-optimitzat)"""
        from music.converters import get_voltage_calibrated, get_voltage_percentage
        
        # SEMPRE redraw complet per fluides (sense cache que complica)
        self.hw.display.fill(0)
        
        # Usar valors BUFFERED de cfg (NO llegir ADCs!)
        cv1_val_raw = self.cfg.x  # Valor clamped de CV1
        cv2_val_raw = self.cfg.y  # Valor clamped de CV2
        
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
            
        elif mode == 4:  # Harmonia - Notes musicals
            # Rodona nota
            self.hw.display.circle(cx - 8, cy, 4, 1)
            self.hw.display.vline(cx - 4, cy - 12, 12, 1)
            # Segona nota
            self.hw.display.circle(cx + 6, cy + 3, 3, 1)
            self.hw.display.vline(cx + 9, cy - 8, 11, 1)
            
        elif mode == 8:  # Cosmos
            # Estrella cosmic (8 puntes)
            self.hw.display.text("  *  ", 52, 22, 1)
            self.hw.display.text(" *** ", 52, 28, 1)
            self.hw.display.text("*****", 51, 34, 1)
            self.hw.display.text(" *** ", 52, 40, 1)
            self.hw.display.text("  *  ", 52, 46, 1)
            
        elif mode == 9:  # Campanetes
            # Campana amb badall que oscil·la
            fase = (self.cfg.iteration % 6) // 2  # 0, 1, 2
            # Campana superior
            self.hw.display.text("  ^  ", 52, 18, 1)
            self.hw.display.text(" / \\ ", 51, 24, 1)
            self.hw.display.text("/   \\", 50, 30, 1)
            self.hw.display.text("|   |", 51, 36, 1)
            # Badall (oscil·la)
            if fase == 0:
                self.hw.display.text(" o  ", 54, 42, 1)  # Esquerra
            elif fase == 1:
                self.hw.display.text("  o ", 55, 42, 1)  # Centre
            else:
                self.hw.display.text("   o", 56, 42, 1)  # Dreta
            
        elif mode == 10:  # Segones
            # Dues notes amb fletxa (moviment per tons)
            # Primera nota
            self.hw.display.circle(cx - 12, cy, 4, 1)
            self.hw.display.vline(cx - 8, cy - 12, 12, 1)
            # Fletxa horitzontal
            self.hw.display.hline(cx - 6, cy, 12, 1)
            self.hw.display.pixel(cx + 6, cy - 1, 1)  # Punta esquerra
            self.hw.display.pixel(cx + 6, cy + 1, 1)  # Punta dreta
            # Segona nota
            self.hw.display.circle(cx + 12, cy, 4, 1)
            self.hw.display.vline(cx + 16, cy - 12, 12, 1)
            
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
        
        elif mode == 11:  # Espiral - Espiral ascendent amb transposició
            # Espiral que va pujant (representa transposició gradual)
            t = time.monotonic() * 2  # Animació lenta
            num_loops = 3  # Tres voltes de l'espiral
            for i in range(0, 360 * num_loops, 12):
                # Radi que creix amb cada volta (espiral)
                rad_angle = math.radians(i + t * 30)
                radius = 3 + (i / 100.0)  # Espiral cap enfora
                # Y que puja gradualment (transposició)
                y_offset = -(i / 80.0)  # Puja cap amunt
                
                px = int(cx + radius * math.cos(rad_angle))
                py = int(cy + y_offset + radius * math.sin(rad_angle))
                
                # Només dibuixar si està dins la pantalla
                if 0 <= px < 128 and 0 <= py < 64:
                    self.hw.display.pixel(px, py, 1)
            
            # Fletxa cap amunt (indica transposició ascendent)
            self.hw.display.vline(cx, cy - 16, 8, 1)
            self.hw.display.pixel(cx - 1, cy - 15, 1)  # Punta esquerra
            self.hw.display.pixel(cx + 1, cy - 15, 1)  # Punta dreta
            self.hw.display.pixel(cx - 2, cy - 14, 1)
            self.hw.display.pixel(cx + 2, cy - 14, 1)
        
        elif mode == 12:  # Contrapunt - Dues veus independents
            # Veu principal (línia contínua ondulada)
            for x in range(-20, 21, 3):
                y1 = int(3 * math.sin(x * 0.3))
                y2 = int(3 * math.sin((x + 3) * 0.3))
                self.hw.display.line(cx + x, cy - 8 + y1, cx + x + 3, cy - 8 + y2, 1)
            
            # Veu secundària (punts espaiats - representa densitat variable)
            fase = (self.cfg.iteration % 8) // 2  # 0, 1, 2, 3
            spacing = [0, 10, 20, 30]  # Posicions de les notes del contrapunt
            for i, pos in enumerate(spacing):
                # Només dibuixar alguns punts segons fase (representa timing independent)
                if i <= fase or (self.cfg.iteration % 4 == 0):
                    x_pos = cx - 18 + pos
                    y_offset = int(4 * math.cos((pos * 0.2) + time.monotonic()))
                    # Nota del contrapunt (cercle petit)
                    self.hw.display.circle(x_pos, cy + 8 + y_offset, 2, 1)
            
            # Línia separadora (mostra independència de les veus)
            self.hw.display.hline(cx - 20, cy, 40, 1)
        
        elif mode == 13:  # Narval - 3 narvals nadant en formació
            # Tres narvals (triangles) que es persegueixen
            # Animació de moviment
            t = time.monotonic() * 3
            offset = int(3 * math.sin(t))
            
            # Narval 1 (PWM1) - Dalt esquerra
            x1, y1 = cx - 15, cy - 8 + offset
            self.hw.display.line(x1, y1, x1 + 6, y1 + 4, 1)  # Cos
            self.hw.display.line(x1 + 6, y1 + 4, x1, y1 + 8, 1)
            self.hw.display.line(x1, y1, x1, y1 + 8, 1)
            self.hw.display.pixel(x1 - 2, y1 + 2, 1)  # Dent (narval característica)
            
            # Narval 2 (PWM2) - Centre dreta
            x2, y2 = cx + 10, cy - offset
            self.hw.display.line(x2, y2, x2 + 6, y2 + 4, 1)
            self.hw.display.line(x2 + 6, y2 + 4, x2, y2 + 8, 1)
            self.hw.display.line(x2, y2, x2, y2 + 8, 1)
            self.hw.display.pixel(x2 - 2, y2 + 2, 1)
            
            # Narval 3 (PWM3) - Part baixa
            x3, y3 = cx - 5, cy + 10 + offset // 2
            self.hw.display.line(x3, y3, x3 + 6, y3 + 4, 1)
            self.hw.display.line(x3 + 6, y3 + 4, x3, y3 + 8, 1)
            self.hw.display.line(x3, y3, x3, y3 + 8, 1)
            self.hw.display.pixel(x3 - 2, y3 + 2, 1)
        
        elif mode == 14:  # Ciclador - Tres ones PWM amb diferents duty cycles
            # Animació que mostra 3 ones quadrades amb amplades diferents
            # representant els 3 duty cycles independents
            anim_offset = int((time.monotonic() * 8) % 32)
            
            # PWM1 (superior) - Controlat per CV1
            for i in range(32):
                x = (i - anim_offset) % 32
                # Ona quadrada amb duty variable
                y_high = cy - 16 if (x % 8) < 4 else cy - 12
                self.hw.display.pixel(cx - 16 + x, y_high, 1)
            
            # PWM2 (central) - Controlat per CV2
            for i in range(32):
                x = (i - anim_offset) % 32
                y_high = cy - 4 if (x % 8) < 5 else cy
                self.hw.display.pixel(cx - 16 + x, y_high, 1)
            
            # PWM3 (inferior) - Controlat per Slider
            for i in range(32):
                x = (i - anim_offset) % 32
                y_high = cy + 8 if (x % 8) < 3 else cy + 12
                self.hw.display.pixel(cx - 16 + x, y_high, 1)
        
        self.hw.display.show()

