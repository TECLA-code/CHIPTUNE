# =============================================================================
# SCREENS - TECLA Display Manager
# =============================================================================
import time
from music.converters import midi_to_note_name

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
        9: "Campanetes",   # Campanes musicals
        10: "Segones",     # Melodies per tons
        11: "Espiral",     # Recorregut circular amb transposició
        12: "Contrapunt",  # Dues veus independents
        13: "Narval",      # Tres narvals que es comuniquen
        14: "Ciclador"     # Control directe duty cycles
    }
    
    # Noms dels intervals harmònics en català
    HARMONIC_NAMES = {
        0: "Uníson",       # 0 semitons
        1: "2a menor",     # 1 semitó
        2: "2a major",     # 2 semitons
        3: "3a menor",     # 3 semitons
        4: "3a major",     # 4 semitons
        5: "4a justa",     # 5 semitons
        6: "Trítono",      # 6 semitons
        7: "5a justa",     # 7 semitons
        8: "6a menor",     # 8 semitons
        9: "6a major",     # 9 semitons
        10: "7a menor",    # 10 semitons
        11: "7a major",    # 11 semitons
        12: "Octava"       # 12 semitons
    }
    
    # Noms dels paràmetres de configuració
    CONFIG_NAMES = ["Mode", "Cicle1", "Cicle2", "Cicle3", "H0", "H1", "H2"]
    
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
                self.hw.display.text("DUTY 1", 30, 10, 1)
                self.hw.display.text(f"{self.cfg.duty1}%", 40, 30, 2)
            elif self.cfg.configout == 2:
                self.hw.display.text("DUTY 2", 30, 10, 1)
                self.hw.display.text(f"{self.cfg.duty2}%", 40, 30, 2)
            elif self.cfg.configout == 3:
                self.hw.display.text("DUTY 3", 30, 10, 1)
                self.hw.display.text(f"{self.cfg.duty3}%", 40, 30, 2)
            elif self.cfg.configout == 4:
                self.hw.display.text("HARMONIC 1", 10, 10, 1)  # GP22 (pwm1)
                harm_name = self.HARMONIC_NAMES.get(self.cfg.freqharm_base, '---')
                self.hw.display.text(harm_name, 10, 30, 1)
            elif self.cfg.configout == 5:
                self.hw.display.text("HARMONIC 2", 10, 10, 1)  # GP2 (pwm2)
                harm_name = self.HARMONIC_NAMES.get(self.cfg.freqharm1, '---')
                self.hw.display.text(harm_name, 10, 30, 1)
            elif self.cfg.configout == 6:
                self.hw.display.text("HARMONIC 3", 10, 10, 1)  # GP0 (pwm3)
                harm_name = self.HARMONIC_NAMES.get(self.cfg.freqharm2, '---')
                self.hw.display.text(harm_name, 10, 30, 1)
            
            # LÍNIA 3: Nota actual (petita, abaix)
            self.hw.display.text(f"Oct:{self.cfg.octava} {note_name}", 30, 54, 1)
            
            self.hw.display.show()
    
    def _mostrar_resum_complet(self):
        """Mostra imatge gran dibuixada + nom mode"""
        self.hw.display.fill(0)
        
        # Dibuixar imatge gran per al mode
        self._dibuixar_imatge_gran(self.cfg.loop_mode)
    
        
        self.hw.display.show()
    
    def _dibuixar_imatge_gran(self, mode):
        """Dibuixa imatge gran procedural per cada mode"""
        
        if mode == 0:  # Pausa - Píxels aleatoris (dau)
            # Cada 0.5s tira una dau per cada LED
            import random
            import time
            # Usar temps truncat a 0.5s com a seed per canviar cada mig segon
            seed = int(time.monotonic() / 0.5)
            random.seed(seed)
            
            # Omplir pantalla amb píxels aleatoris (50% probabilitat)
            for x in range(0, 128, 2):
                for y in range(0, 64, 2):
                    if random.random() < 0.5:  # 50% probabilitat (dau amb 2 cares)
                        self.hw.display.pixel(x, y, 1)
        
        elif mode == 1:  # Fractal - Conjunt de Mandelbrot
            # Distribució de píxels del conjunt de Mandelbrot
            for px in range(0, 128, 2):
                for py in range(0, 64, 2):
                    # Convertir píxel a coordenades complexes
                    # Zoom al centre del conjunt
                    x0 = (px - 64) / 30.0 - 0.5
                    y0 = (py - 32) / 30.0
                    
                    # Iteració de Mandelbrot simplificada
                    x, y = 0.0, 0.0
                    iteracio = 0
                    max_iter = 12
                    
                    while x*x + y*y <= 4 and iteracio < max_iter:
                        xtemp = x*x - y*y + x0
                        y = 2*x*y + y0
                        x = xtemp
                        iteracio += 1
                    
                    # Dibuixar píxel si està dins del conjunt o frontissa
                    if iteracio >= max_iter or (iteracio > 6 and iteracio % 2 == 0):
                        if 0 <= px < 128 and 0 <= py < 64:
                            self.hw.display.pixel(px, py, 1)
                            # Afegir densitat
                            if px + 1 < 128 and iteracio >= max_iter:
                                self.hw.display.pixel(px + 1, py, 1)
        
        elif mode == 2:  # Riu - Ones fluides grans
            # Múltiples ones verticals simulant aigua
            for x in range(0, 128, 4):
                import math
                for y in range(8, 56, 3):
                    offset = int(8 * math.sin((x + y) * 0.15))
                    self.hw.display.pixel(x + offset, y, 1)
                    self.hw.display.pixel(x + offset + 1, y, 1)
        
        elif mode == 3:  # Tempesta - Núvols variats i pluja dispersa
            # Núvol 1: Esquerra-dalt (petit i alt)
            for x in range(5, 35, 2):
                for y in range(3, 12):
                    # Forma arrodonida
                    if (x - 20)**2 / 225 + (y - 7)**2 / 16 <= 1:
                        if 0 <= x < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x, y, 1)
            
            # Núvol 2: Centre (gran i irregular)
            for x in range(35, 95, 2):
                for y in range(8, 22):
                    # Forma irregular amb dues bombolles
                    if ((x - 55)**2 / 400 + (y - 15)**2 / 25 <= 1) or \
                       ((x - 75)**2 / 300 + (y - 12)**2 / 36 <= 1):
                        if 0 <= x < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x, y, 1)
            
            # Núvol 3: Dreta (ample i pla, més amunt)
            for x in range(75, 125, 2):
                for y in range(8, 19):
                    # Més pla i allargat
                    if (x - 100)**2 / 625 + (y - 13)**2 / 25 <= 1:
                        if 0 <= x < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x, y, 1)
            
            # Núvol 4: Esquerra-mig (petit complement)
            for x in range(8, 28, 2):
                for y in range(18, 28):
                    if (x - 18)**2 / 100 + (y - 23)**2 / 25 <= 1:
                        if 0 <= x < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x, y, 1)
            
            # Pluja: gotes curtes (1-2 píxels) molt disperses per tota la pantalla
            import random
            random.seed(42)  # Seed fix per consistència
            
            for i in range(100):  # 100 gotes
                x = random.randint(0, 127)
                y_start = random.randint(12, 50)
                gota_len = random.choice([1, 1, 1, 2])  # Majoria 1 píxel, algunes 2
                
                for dy in range(gota_len):
                    y = y_start + dy
                    if 0 <= x < 128 and 0 <= y < 64:
                        self.hw.display.pixel(x, y, 1)
            
            # Rajos (3 rajos en zigzag amb línies)
            # Raig 1: Del núvol esquerra
            raig1_punts = [(15, 12), (18, 20), (14, 28), (16, 36), (12, 44)]
            for i in range(len(raig1_punts) - 1):
                x1, y1 = raig1_punts[i]
                x2, y2 = raig1_punts[i + 1]
                self.hw.display.line(x1, y1, x2, y2, 1)
            
            # Raig 2: Del núvol centre (més llarg)
            raig2_punts = [(60, 16), (65, 25), (58, 34), (62, 43), (56, 52), (58, 60)]
            for i in range(len(raig2_punts) - 1):
                x1, y1 = raig2_punts[i]
                x2, y2 = raig2_punts[i + 1]
                self.hw.display.line(x1, y1, x2, y2, 1)
            
            # Raig 3: Del núvol dreta
            raig3_punts = [(105, 13), (102, 22), (108, 30), (104, 38), (106, 46)]
            for i in range(len(raig3_punts) - 1):
                x1, y1 = raig3_punts[i]
                x2, y2 = raig3_punts[i + 1]
                self.hw.display.line(x1, y1, x2, y2, 1)
        
        elif mode == 4:  # Harmonia - Ones harmòniques superposades
            # Múltiples ones amb diferents freqüències harmòniques
            import math
            
            # Ona 1: Fonamental (amplitud màxima - omple pantalla)
            for x in range(0, 128, 2):
                y = int(32 + 24 * math.sin(x * 0.1))
                if 0 <= y < 64:
                    self.hw.display.pixel(x, y, 1)
                    if x + 1 < 128:
                        self.hw.display.pixel(x + 1, y, 1)
            
            # Ona 2: Tercera harmònica
            for x in range(0, 128, 2):
                y = int(32 + 18 * math.sin(x * 0.3))
                if 0 <= y < 64:
                    self.hw.display.pixel(x, y, 1)
            
            # Ona 3: Quinta harmònica
            for x in range(0, 128, 2):
                y = int(32 + 12 * math.sin(x * 0.5))
                if 0 <= y < 64:
                    self.hw.display.pixel(x, y, 1)
            
            # Afegir píxels de densitat per omplir més verticalment
            for x in range(0, 128, 3):
                for offset in [-20, -10, 0, 10, 20]:
                    y = 32 + offset
                    if 0 <= y < 64 and x % 6 < 3:
                        self.hw.display.pixel(x, y, 1)
        
        elif mode == 5:  # Bosc - Múltiples arbres densos
            # Patró orgànic de bosc amb múltiples arbrets
            
            # Posicions dels arbres (x, alçada)
            arbres = [
                (15, 12), (28, 10), (42, 14), (56, 11), (70, 13), 
                (84, 12), (98, 10), (112, 14), (22, 8), (50, 9), 
                (78, 8), (106, 9), (35, 7), (63, 7), (91, 7)
            ]
            
            for x, h in arbres:
                # Tronc (2 píxels d'ample)
                base_y = 55
                self.hw.display.vline(x, base_y - h, h, 1)
                self.hw.display.vline(x + 1, base_y - h + 1, h - 1, 1)
                
                # Copa triangular amb píxels densos
                copa_h = h // 2 + 3
                for i in range(copa_h):
                    y = base_y - h - i
                    w = (copa_h - i) // 2 + 1
                    # Brilla més l'interior (omplir)
                    for dx in range(-w, w + 1):
                        if 0 <= x + dx < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x + dx, y, 1)
            
            # Afegir "fullaraca" - píxels esparsos al terra
            for x in range(0, 128, 3):
                if x % 7 < 3:
                    y = 56 + (x % 3)
                    if 0 <= y < 64:
                        self.hw.display.pixel(x, y, 1)
            
            # Ocells petits volant (forma de V)
            ocells = [(45, 12), (75, 8), (105, 15), (20, 18)]
            for ox, oy in ocells:
                # Ocell en forma de V (3 píxels)
                self.hw.display.pixel(ox - 1, oy, 1)
                self.hw.display.pixel(ox, oy - 1, 1)
                self.hw.display.pixel(ox + 1, oy, 1)
            
            # Lluna menguant (mitja lluna al centre-dalt)
            import math
            lx, ly = 64, 20  # Posició de la lluna
            
            # Dibuixar mitja lluna menguant (forma de C)
            # 1. Omplir semicercle exterior dret
            for y in range(ly - 8, ly + 9):
                for x in range(lx, lx + 9):
                    dx = x - lx
                    dy = y - ly
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist <= 8:
                        if 0 <= x < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x, y, 1)
            
            # 2. Buidar semicercle interior (crear la forma de C)
            for y in range(ly - 6, ly + 7):
                for x in range(lx + 1, lx + 8):
                    dx = x - (lx + 1)  # Cercle desplaçat cap a dins
                    dy = y - ly
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist <= 5:
                        if 0 <= x < 128 and 0 <= y < 64:
                            self.hw.display.pixel(x, y, 0)  # Buidar (píxel negre)
        
        elif mode == 6:  # Escala CV - Il·lusió òptica d'escala
            # Efecte òptic d'escala amb graons diagonals
            
            # Crear 6 graons amb il·lusió de profunditat
            for step in range(6):
                x_start = step * 20
                y_start = 10 + step * 7
                
                # Graó horitzontal
                for x in range(x_start, x_start + 22):
                    if 0 <= x < 128 and 0 <= y_start < 64:
                        self.hw.display.pixel(x, y_start, 1)
                        self.hw.display.pixel(x, y_start + 1, 1)
                
                # Vertical (paret)
                for y in range(y_start, min(y_start + 8, 64)):
                    if 0 <= x_start + 21 < 128:
                        self.hw.display.pixel(x_start + 21, y, 1)
                        self.hw.display.pixel(x_start + 20, y, 1)
                
                # Afegir densitat de píxels (ombra)
                for dx in range(0, 18, 3):
                    for dy in range(2, 6):
                        px = x_start + dx
                        py = y_start + dy
                        if 0 <= px < 128 and 0 <= py < 64 and dx % 6 < 2:
                            self.hw.display.pixel(px, py, 1)
        
        elif mode == 7:  # Euclidia - Drum and Bass visual
            # Patró de píxels inspirat en ritme Drum and Bass
            
            # Kick drums (píxels densos a baix - baixos)
            kick_pattern = [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0]
            for i, hit in enumerate(kick_pattern):
                if hit:
                    x_pos = i * 8
                    # Píxels densos verticals (kick)
                    for y in range(45, 60):
                        if 0 <= x_pos < 128 and (y - 45) % 2 == 0:
                            self.hw.display.pixel(x_pos, y, 1)
                            if x_pos + 1 < 128:
                                self.hw.display.pixel(x_pos + 1, y, 1)
            
            # Snare (píxels al mig - mitjos)
            snare_pattern = [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0]
            for i, hit in enumerate(snare_pattern):
                if hit:
                    x_pos = i * 8
                    for y in range(28, 38):
                        if 0 <= x_pos < 128 and (y - 28) % 3 == 0:
                            self.hw.display.pixel(x_pos, y, 1)
            
            # Hi-hats densos (píxels a dalt - aguts)
            for x in range(0, 128, 4):
                if x % 8 < 3:
                    for y in range(8, 22, 2):
                        if (x + y) % 5 < 2:
                            self.hw.display.pixel(x, y, 1)
            
            # Afegir "breaks" - píxels de transició
            for x in range(0, 128, 16):
                for dy in range(0, 55, 8):
                    if x % 32 < 8:
                        self.hw.display.pixel(x, 10 + dy, 1)
        
        elif mode == 8:  # Cosmos - Nebulosa
            import math
            import random
            # Espiral galàctica amb estrelles
            for i in range(0, 360, 8):
                rad = math.radians(i)
                r = 3 + i / 20.0
                px = int(64 + r * math.cos(rad))
                py = int(32 + r * math.sin(rad))
                self.hw.display.pixel(px, py, 1)
                self.hw.display.pixel(px + 1, py, 1)
            
            # Estrelles aleatòries
            for _ in range(30):
                sx = random.randint(10, 118)
                sy = random.randint(5, 59)
                self.hw.display.pixel(sx, sy, 1)
        
        elif mode == 9:  # Campanetes - Campana VERTICAL
            cx, cy = 64, 20
            
            # Campana amb forma vertical correcta
            # Part superior arrodonida
            for x in range(cx - 12, cx + 13):
                dx = abs(x - cx)
                # Arc superior (semicercle)
                if dx <= 12:
                    import math
                    y_top = int(cy + 5 - math.sqrt(144 - dx**2))
                    if y_top >= cy - 7:
                        self.hw.display.pixel(x, y_top, 1)
            
            # Costats de la campana (s'obre cap avall)
            for y in range(cy + 5, cy + 20):
                dy = y - (cy + 5)
                w = 12 + int(dy * 0.3)  # S'obre gradualment
                self.hw.display.pixel(cx - w, y, 1)
                self.hw.display.pixel(cx + w, y, 1)
            
            # Base de la campana (línia)
            self.hw.display.hline(cx - 15, cy + 20, 30, 1)
            self.hw.display.hline(cx - 14, cy + 21, 28, 1)
            
            # Badall penjant
            self.hw.display.vline(cx, cy + 22, 4, 1)
            self.hw.display.circle(cx, cy + 26, 2, 1)
            self.hw.display.fill_rect(cx - 1, cy + 26, 2, 2, 1)
        
        elif mode == 10:  # Segones - Dues ones paral·leles denses
            # Dues ones amb interval de segona (desplaçament vertical)
            import math
            
            # Ona superior (més densa)
            for x in range(0, 128, 2):
                y1 = int(22 + 8 * math.sin(x * 0.12))
                if 0 <= y1 < 64:
                    self.hw.display.pixel(x, y1, 1)
                    if x + 1 < 128:
                        self.hw.display.pixel(x + 1, y1, 1)
            
            # Ona inferior (desplaçada - interval de segona)
            for x in range(0, 128, 2):
                y2 = int(42 + 8 * math.sin(x * 0.12))
                if 0 <= y2 < 64:
                    self.hw.display.pixel(x, y2, 1)
                    if x + 1 < 128:
                        self.hw.display.pixel(x + 1, y2, 1)
        
        elif mode == 11:  # Espiral - Espiral MEGA DENSA
            import math
            cx, cy = 64, 32
            # 5 voltes amb més punts per omplir més
            for i in range(0, 1800, 2):  # 5 voltes (1800°) amb pas de 2°
                rad = math.radians(i)
                r = i / 50.0  # Creixement del radi
                px = int(cx + r * math.cos(rad))
                py = int(cy + r * math.sin(rad))
                if 0 <= px < 128 and 0 <= py < 64:
                    self.hw.display.pixel(px, py, 1)
                    # Doble gruix per fer-la més visible
                    if px + 1 < 128:
                        self.hw.display.pixel(px + 1, py, 1)
        
        elif mode == 12:  # Contrapunt - Espirals contrarotants hipnòtiques
            # Patró hipnòtic amb dues espirals que giren en sentits oposats
            import math
            cx, cy = 64, 32
            
            # Espiral 1: Sentit horari (densa)
            for i in range(0, 900, 3):  # 2.5 voltes
                rad = math.radians(i)
                r = i / 30.0
                px = int(cx + r * math.cos(rad))
                py = int(cy + r * math.sin(rad))
                if 0 <= px < 128 and 0 <= py < 64:
                    self.hw.display.pixel(px, py, 1)
                    # Afegir densitat
                    if i % 6 < 3:
                        if px + 1 < 128:
                            self.hw.display.pixel(px + 1, py, 1)
            
            # Espiral 2: Sentit antihorari (contrarotant)
            for i in range(0, 900, 3):
                rad = -math.radians(i)  # Negatiu = antihorari
                r = i / 30.0
                px = int(cx + r * math.cos(rad))
                py = int(cy + r * math.sin(rad))
                if 0 <= px < 128 and 0 <= py < 64:
                    self.hw.display.pixel(px, py, 1)
            
            # Afegir punts de focus al centre (hipnòtic)
            for ring in range(1, 4):
                radius = ring * 3
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    px = int(cx + radius * math.cos(rad))
                    py = int(cy + radius * math.sin(rad))
                    if 0 <= px < 128 and 0 <= py < 64:
                        self.hw.display.pixel(px, py, 1)
                        if px + 1 < 128:
                            self.hw.display.pixel(px + 1, py, 1)
        
        elif mode == 13:  # Narval - Bombolletes de comunicació
            # Bombolletes esparses pujant (comunicació dels narvals)
            import math
            
            # Posicions de les bombolletes (x, y, mida) - distribució DENSA
            bombolletes = [
                # Zona esquerra - molt dens
                (10, 58, 2), (18, 56, 2), (14, 52, 2), (22, 50, 2), (28, 54, 2),
                (25, 48, 3), (32, 50, 2), (36, 46, 2), (20, 44, 2), (28, 42, 2),
                (16, 40, 2), (24, 38, 3), (30, 36, 2), (18, 34, 2), (26, 32, 2),
                (22, 28, 2), (30, 26, 3), (16, 24, 2), (28, 20, 2), (20, 18, 2),
                (32, 16, 2), (24, 14, 3), (12, 12, 2), (18, 8, 2),
                # Zona centre - dens
                (45, 58, 2), (48, 56, 2), (52, 58, 2), (56, 54, 2), (50, 52, 2),
                (58, 50, 3), (54, 48, 2), (48, 46, 2), (62, 46, 2), (56, 44, 2),
                (50, 42, 2), (44, 40, 3), (58, 38, 2), (52, 36, 2), (48, 34, 2),
                (62, 34, 2), (56, 30, 3), (50, 28, 2), (44, 26, 2), (58, 24, 2),
                (52, 20, 2), (48, 16, 3), (54, 12, 2), (46, 10, 2), (52, 6, 2),
                # Zona dreta - molt dens
                (70, 58, 2), (76, 56, 2), (82, 58, 2), (78, 54, 3), (85, 52, 2),
                (90, 54, 2), (94, 50, 2), (88, 48, 2), (82, 46, 2), (76, 44, 2),
                (92, 44, 3), (86, 40, 2), (80, 38, 2), (94, 38, 2), (88, 34, 2),
                (82, 32, 2), (76, 30, 3), (92, 30, 2), (86, 26, 2), (80, 24, 2),
                (94, 24, 2), (88, 20, 3), (82, 18, 2), (96, 16, 2), (90, 14, 2),
                (84, 10, 2), (100, 12, 3), (106, 18, 2), (110, 22, 2), (114, 26, 2),
                (108, 30, 2), (116, 32, 3), (112, 36, 2), (118, 40, 2), (110, 44, 2),
                (116, 48, 2), (106, 50, 2), (112, 54, 2),
                # Bombolles grans (més)
                (36, 60, 5), (68, 60, 5), (100, 58, 5), (18, 48, 4), (54, 44, 4), (88, 42, 4)
            ]
            
            for bx, by, size in bombolletes:
                # Dibuixar bombolleta com a cercle de píxels
                if size == 2:
                    # Bombolleta petita (4 píxels)
                    self.hw.display.pixel(bx, by, 1)
                    self.hw.display.pixel(bx + 1, by, 1)
                    self.hw.display.pixel(bx, by + 1, 1)
                    self.hw.display.pixel(bx + 1, by + 1, 1)
                elif size == 3:
                    # Bombolleta mitjana (8 píxels)
                    for dx, dy in [(-1,0), (0,-1), (1,0), (0,1), (-1,-1), (1,-1), (-1,1), (1,1)]:
                        px, py = bx + dx, by + dy
                        if 0 <= px < 128 and 0 <= py < 64:
                            self.hw.display.pixel(px, py, 1)
                elif size == 4:
                    # Bombolleta mitjana-gran (cercle radi 2)
                    import math
                    for angle in range(0, 360, 40):
                        rad = math.radians(angle)
                        for r in [1, 2]:
                            px = int(bx + r * math.cos(rad))
                            py = int(by + r * math.sin(rad))
                            if 0 <= px < 128 and 0 <= py < 64:
                                self.hw.display.pixel(px, py, 1)
                else:
                    # Bombolleta gran (cercle de radi 2-3)
                    import math
                    for angle in range(0, 360, 30):
                        rad = math.radians(angle)
                        for r in [2, 3]:
                            px = int(bx + r * math.cos(rad))
                            py = int(by + r * math.sin(rad))
                            if 0 <= px < 128 and 0 <= py < 64:
                                self.hw.display.pixel(px, py, 1)
        
        elif mode == 14:  # Ciclador - Tres senyals quadrades grans
            # Senyal 1 (superior)
            for i in range(0, 120, 20):
                high = 1 if (i // 20) % 2 == 0 else 0
                y = 12 if high else 18
                self.hw.display.hline(4 + i, y, 20, 1)
                if i > 0:
                    self.hw.display.vline(4 + i, 12, 7, 1)
            
            # Senyal 2 (central)
            for i in range(0, 120, 15):
                high = 1 if (i // 15) % 2 == 0 else 0
                y = 28 if high else 35
                self.hw.display.hline(4 + i, y, 15, 1)
                if i > 0:
                    self.hw.display.vline(4 + i, 28, 8, 1)
            
            # Senyal 3 (inferior)
            for i in range(0, 120, 25):
                high = 1 if (i // 25) % 2 == 0 else 0
                y = 45 if high else 52
                self.hw.display.hline(4 + i, y, 25, 1)
                if i > 0:
                    self.hw.display.vline(4 + i, 45, 8, 1)
    
    def _dibuixar_icona_mode(self, mode):
        """Dibuixa icona petita i estàtica per cada mode (dalt esquerra)"""
        # Posició icona: cantonada superior esquerra
        ix, iy = 8, 8
        
        if mode == 0:  # Pausa - Quadrat buit
            self.hw.display.rect(ix, iy, 8, 8, 1)
        
        elif mode == 1:  # Fractal - Triangle
            self.hw.display.line(ix + 4, iy, ix, iy + 8, 1)
            self.hw.display.line(ix + 4, iy, ix + 8, iy + 8, 1)
            self.hw.display.line(ix, iy + 8, ix + 8, iy + 8, 1)
        
        elif mode == 2:  # Riu - Ones
            for i in range(0, 9, 2):
                y_offset = 2 if i % 4 == 0 else -2
                self.hw.display.pixel(ix + i, iy + 4 + y_offset, 1)
        
        elif mode == 3:  # Tempesta - Raig
            self.hw.display.line(ix + 4, iy, ix + 2, iy + 3, 1)
            self.hw.display.line(ix + 2, iy + 3, ix + 6, iy + 3, 1)
            self.hw.display.line(ix + 6, iy + 3, ix + 4, iy + 8, 1)
        
        elif mode == 4:  # Harmonia - Nota musical
            self.hw.display.circle(ix + 2, iy + 6, 2, 1)
            self.hw.display.vline(ix + 4, iy + 2, 4, 1)
        
        elif mode == 5:  # Bosc - Arbre
            self.hw.display.vline(ix + 4, iy + 2, 6, 1)  # Tronc
            self.hw.display.line(ix + 4, iy + 3, ix + 1, iy, 1)  # Branques
            self.hw.display.line(ix + 4, iy + 3, ix + 7, iy, 1)
        
        elif mode == 6:  # Escala CV - Escalera
            for i in range(3):
                self.hw.display.hline(ix + i * 2, iy + 6 - i * 2, 3, 1)
                self.hw.display.vline(ix + i * 2 + 3, iy + 6 - i * 2, 2, 1)
        
        elif mode == 7:  # Euclidia - Cercle amb punts
            self.hw.display.circle(ix + 4, iy + 4, 4, 1)
            for angle in [0, 90, 180, 270]:
                import math
                rad = math.radians(angle)
                px = int(ix + 4 + 2 * math.cos(rad))
                py = int(iy + 4 + 2 * math.sin(rad))
                self.hw.display.pixel(px, py, 1)
        
        elif mode == 8:  # Cosmos - Estrella
            self.hw.display.text("*", ix + 2, iy, 1)
        
        elif mode == 9:  # Campanetes - Campana
            self.hw.display.text("^", ix + 2, iy, 1)
            self.hw.display.line(ix + 1, iy + 6, ix + 1, iy + 8, 1)
            self.hw.display.line(ix + 1, iy + 8, ix + 6, iy + 8, 1)
            self.hw.display.line(ix + 6, iy + 8, ix + 6, iy + 6, 1)
        
        elif mode == 10:  # Segones - Dues notes
            self.hw.display.circle(ix + 1, iy + 6, 1, 1)
            self.hw.display.circle(ix + 6, iy + 6, 1, 1)
            self.hw.display.hline(ix + 2, iy + 6, 3, 1)
        
        elif mode == 11:  # Espiral - Espiral simple
            import math
            for i in range(0, 180, 20):
                rad = math.radians(i)
                r = i / 60.0
                px = int(ix + 4 + r * math.cos(rad))
                py = int(iy + 4 + r * math.sin(rad))
                self.hw.display.pixel(px, py, 1)
        
        elif mode == 12:  # Contrapunt - Tres línies
            self.hw.display.hline(ix, iy + 2, 8, 1)
            self.hw.display.hline(ix, iy + 4, 8, 1)
            self.hw.display.hline(ix, iy + 6, 8, 1)
        
        elif mode == 13:  # Narval - Triangle (narval)
            self.hw.display.line(ix, iy + 8, ix + 4, iy, 1)
            self.hw.display.line(ix + 4, iy, ix + 8, iy + 8, 1)
            self.hw.display.line(ix, iy + 8, ix + 8, iy + 8, 1)
        
        elif mode == 14:  # Ciclador - Ona quadrada
            for i in range(0, 9, 2):
                y_val = iy if i % 4 == 0 else iy + 6
                self.hw.display.vline(ix + i, y_val, 2, 1)
    

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
        
        cv1_actual = self.hw.get_voltage(self.hw.cv1_pote)  # GP26
        cv2_actual = self.hw.get_voltage(self.hw.cv2_ldr)   # GP27
        
        self.hw.display.text("CALIBRACIO CV", 10, 0, 1)
        self.hw.display.hline(0, 10, 128, 1)
        self.hw.display.text("CV1 (Pote):", 0, 15, 1)
        self.hw.display.text(f"{cv1_actual:.2f}V", 80, 15, 1)
        self.hw.display.text(f"Min:{self.cfg.cv1_min:.2f}", 0, 25, 1)
        self.hw.display.text(f"Max:{self.cfg.cv1_max:.2f}", 70, 25, 1)
        
        self.hw.display.text("CV2 (LDR):", 0, 38, 1)
        self.hw.display.text(f"{cv2_actual:.2f}V", 80, 38, 1)
        self.hw.display.text(f"Min:{self.cfg.cv2_min:.2f}", 0, 48, 1)
        self.hw.display.text(f"Max:{self.cfg.cv2_max:.2f}", 70, 48, 1)
        
        self.hw.display.text("BTN: 1/2=CV1 3/4=CV2", 0, 58, 1)
        self.hw.display.show()
