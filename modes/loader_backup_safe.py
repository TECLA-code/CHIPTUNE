# =============================================================================
# CARREGADOR DE MODES MUSICALS - TECLA Professional
# =============================================================================
# Aquest fitxer conté tots els modes musicals que pot tocar el TECLA.
# Cada mode és una "personalitat" musical diferent que genera notes
# de forma automàtica segons els valors dels potenciòmetres (CVs).
#
# Modes disponibles:
#   1. Fractal    - Explora el conjunt de Mandelbrot (matemàtica visual)
#   2. Riu        - Notes fluides com aigua d'un riu
#   3. Tempesta   - Pluja constant amb llamps aleatoris
#   4. Harmonia   - Progressions harmòniques intel·ligents
#   5. Bosc       - Notes orgàniques i impredictibles
#   6. Escala CV  - Seqüències d'escales modals
#   7. Euclidia   - Ritmes matemàtics perfectament distribuïts
#   8. Cosmos     - Combinació de tots els algorismes (MODE FINAL)
# =============================================================================

import random  # Per generar números aleatoris
import time    # Per mesurar el temps
import math    # Per funcions matemàtiques (sin, cos)
from music import algorithms, converters  # Eines musicals personalitzades

class ModeLoader:
    """Carrega i executa modes musicals amb qualitat professional"""
    
    def __init__(self, hardware, config, midi_handler):
        """Inicialitza el carregador de modes
        
        Arguments:
            hardware: Accés als components físics (PWM, display, etc.)
            config: Configuració actual (octava, modo, etc.)
            midi_handler: Gestor de notes MIDI
        """
        self.hw = hardware      # Hardware del TECLA
        self.cfg = config       # Configuració actual
        self.midi = midi_handler  # Per tocar notes
    
    def execute_mode(self, mode_num, x, y, sleep_time, cx, cy):
        """Executa el mode musical seleccionat
        
        Arguments:
            mode_num: Mode 1-10
            x: CV1 (GP26) calibrat
            y: CV2 (GP27) calibrat
            sleep_time: Temps entre notes
            cx, cy: Coordenades Fractal
        """
        
        if mode_num == 1:
            self._mode_mandelbrot(cx, cy, sleep_time)
        elif mode_num == 2:
            self._mode_rio(x, y, sleep_time)
        elif mode_num == 3:
            self._mode_tormenta(x, y, sleep_time)
        elif mode_num == 4:
            self._mode_armonia(x, y, sleep_time)
        elif mode_num == 5:
            self._mode_bosque(x, y, sleep_time)
        elif mode_num == 6:
            self._mode_escala(x, y, sleep_time)
        elif mode_num == 7:
            self._mode_euclidiano(x, y, sleep_time)
        elif mode_num == 8:
            self._mode_cosmos(x, y, sleep_time, cx, cy)
        elif mode_num == 9:
            self._mode_campanetes(x, y, sleep_time)
        elif mode_num == 10:
            self._mode_segones(x, y, sleep_time)
    
    # =========================================================================
    # MODE 1: FRACTAL MANDELBROT
    # =========================================================================
    # Explora el famós fractal de Mandelbrot, convertint coordenades
    # matemàtiques en notes musicals. És com "navegar" per un paisatge
    # infinit de matemàtiques i escoltar el que "sonen" els diferents punts.
    # 
    # Controls:
    #   CV1 (x): BPM - Velocitat de navegació
    #   CV2 (y): Coordenada X del fractal (-1.5 a 1.5)
    #   Slider (z): Coordenada Y del fractal (-1.5 a 1.5)
    # =========================================================================
    def _mode_mandelbrot(self, cx, cy, sleep_time):
        """Mode 1: Fractal - Matemàtica visual convertida a música"""
        
        # Converteix les coordenades del fractal en una nota MIDI (0-127)
        note = algorithms.mandelbrot_to_midi(cx, cy)
        
        # Si el mode CAOS està activat, afegeix imprevisibilitat
        if self.cfg.caos == 1:
            octava_new = random.randint(0, 8)  # Octava aleatòria
            
            if self.cfg.caos_note == 0:
                note = 0  # Silenci aleatori
            else:
                # Toca una nota extra en una octava aleatòria (eco caòtic)
                self.midi.play_note_full(note, 1, octava_new, sleep_time * 500,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Toca la nota principal en l'octava configurada
        self.midi.play_note_full(note, 1, self.cfg.octava, sleep_time * 500,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 2: RIU
    # =========================================================================
    # Notes fluides com aigua que corre per un riu. L'algorisme simula ones
    # sinusoïdals que creen melodies orgàniques i fluides.
    # 
    # Controls:
    #   CV1 (GP26): Densitat - Nombre de notes per cicle (1-10)
    #   CV2 (GP27): Turbulència - Força de les onades (0-127)
    #   Slider (GP28): BPM - Velocitat del riu (automàtic)
    # =========================================================================
    def _mode_rio(self, x, y, sleep_time):
        """Mode 2: Riu
        
        Controls:
            x (CV1/GP26): Densitat (1-10)
            y (CV2/GP27): Turbulència (0-127)
        """
        
        # Convertir voltatges (distribució uniforme)
        densitat = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 9.999) + 1
        turbulencia = converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 127
        rio_time = time.time()                # Temps actual (per les ones)
        
        # Calcular el rang de notes segons l'octava actual
        nota_min = 12 * self.cfg.octava  # Nota més baixa de l'octava
        nota_max = nota_min + 11          # Nota més alta de l'octava
        
        # El riu "avança" sempre endavant (augmenta la nota base)
        self.cfg.rio_base = (self.cfg.rio_base + densitat) % 12
        nota_base = nota_min + self.cfg.rio_base
        
        # Afegir moviment ondulatori (com ones a l'aigua)
        wave = math.sin(rio_time * 0.8) * (densitat * 0.5)      # Ona lenta
        ripple = math.cos(rio_time * 2.2) * (turbulencia * 0.05) # Ona ràpida
        random_offset = random.uniform(-2, 2)                     # Variació aleatòria
        
        # Combinar tots els elements per obtenir la nota final
        nota_rio = nota_base + wave + ripple + random_offset
        nota_rio = int(max(0, min(127, nota_rio)))  # Assegurar rang MIDI vàlid
        
        # Patró de gate (quan sona / quan no sona)
        patron_gate = [1, 1, 1, 0, 0, 1, 1, 1, 1, 0]  # 1=toca, 0=silenci
        gate_on = patron_gate[self.cfg.iteration % len(patron_gate)]
        
        # Mode CAOS: afegeix notes aleatòries en octaves diferents
        if self.cfg.caos == 1:
            octava_new = random.randint(0, 8)  # Octava aleatòria
            
            if self.cfg.caos_note == 0:
                nota_rio = 0  # Silenci caòtic
            elif gate_on:
                # Toca eco caòtic en octava aleatòria
                self.midi.play_note_full(nota_rio, 1, octava_new, sleep_time * 500,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Toca la nota principal del riu
        self.midi.play_note_full(nota_rio, gate_on, self.cfg.octava, sleep_time * 500,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 3: TEMPESTA
    # =========================================================================
    # Controls:
    #   CV1 (GP26): Intensitat lluvia (0-127)
    #   CV2 (GP27): Freqüència llamps (0-127)
    #   Slider (GP28): BPM
    # =========================================================================
    def _mode_tormenta(self, x, y, sleep_time):
        """Mode 3: Tempesta
        
        Controls:
            x (CV1/GP26): Intensitat pluja
            y (CV2/GP27): Freqüència llamps
        """
        
        escala_tormenta = [0, 3, 5, 7, 10]
        
        # Convertir voltatges (distribució uniforme)
        intensidad_lluvia = converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 127
        frecuencia_rayos = converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 127
        
        # Calcular nota base dins de l'octava actual
        nota_min = 12 * self.cfg.octava
        nota_max = min(nota_min + 11, 127)
        nota_base = nota_min + int(intensidad_lluvia * 0.09)
        nota_base = max(nota_min, min(nota_max, nota_base))
        
        # Decidir si toca un llamp (aleatori segons freqüència)
        if random.randint(0, 1000) < (frecuencia_rayos * 8):  # Probabilitat 0-101.6%
            # LLAMP! Generar arpegi ascendent o descendent
            direccion = 1 if random.random() > 0.3 else -1  # 70% amunt, 30% avall
            
            # Tocar totes les notes de l'arpegi ràpidament
            for i, intervalo in enumerate(escala_tormenta[::direccion]):
                multiplicador = max(1, min(3, (i+1)))  # Intensificar el llamp
                nota_relampago = nota_base + (intervalo * direccion * multiplicador)
                nota_relampago = max(nota_min, min(nota_max, nota_relampago))
                
                # Mode CAOS: llamps en octaves aleatòries
                if self.cfg.caos == 1:
                    octava_new = random.randint(0, 8)
                    if self.cfg.caos_note != 0:
                        self.midi.play_note_full(nota_relampago, 1, octava_new, sleep_time * 500,
                                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
                else:
                    # Toca nota del llamp
                    self.midi.play_note_full(nota_relampago, 1, self.cfg.octava, sleep_time * 500,
                                              0, self.cfg.freqharm1, self.cfg.freqharm2)
        else:
            # PLUJA: Notes constants amb petites variacions
            variacion_lluvia = random.randint(-3, 3)  # Variació aleatòria ±3 semitons
            nota_lluvia = max(nota_min, min(nota_max, nota_base + variacion_lluvia))
            
            # Mode CAOS: pluja en octaves aleatòries
            if self.cfg.caos == 1:
                octava_new = random.randint(0, 8)
                if self.cfg.caos_note != 0:
                    self.midi.play_note_full(nota_lluvia, 1, octava_new, sleep_time * 500,
                                              0, self.cfg.freqharm1, self.cfg.freqharm2)
            else:
                # Toca nota de la pluja
                self.midi.play_note_full(nota_lluvia, 1, self.cfg.octava, sleep_time * 500,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 4: HARMONIA
    # =========================================================================
    # Genera progressions harmòniques intel·ligents. La nota següent depèn
    # de la nota anterior, creant seqüències musicals coherents i agradables.
    # Com un pianista que escull la millor nota següent en una improvisació.
    # 
    # Controls:
    #   CV1 (x): BPM - Velocitat de la progressió
    #   CV2 (y): Perfil harmònic - Tipus de progressió (0-127)
    #   Slider (z): Tensió harmònica - Dissonancia/Resolució (0-127)
    # =========================================================================
    def _mode_armonia(self, y, z, sleep_time):
        """Mode 4: Harmonia - Progressions harmòniques intel·ligents"""
    def _mode_armonia(self, x, y, sleep_time):
        """Mode 4: Harmonia - Progressions d'acords
        
        Controls:
            x (CV1/GP26): Arrel (0-6)
            y (CV2/GP27): Tensió (0-3)
        """
        
        # Inicialitzar estat la primera vegada
        if not self.cfg.state_harmony['initialized']:
            self.cfg.state_harmony.update({
                'previous_note': 12 * self.cfg.octava,
                'chord_step': 0,
                'initialized': True
            })

        # Escala base (major) i selecció d'arrel/tensió
        major_scale = [0, 2, 4, 5, 7, 9, 11]
        # Utilitzar normalize per distribució uniforme amb qualsevol rang CV
        root_index = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 6.999)
        tension_level = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 3.999)

        chord_shapes = [
            [0, 4, 7],      # Triada major
            [0, 3, 7],      # Triada menor
            [0, 4, 7, 11],  # Major 7
            [0, 3, 7, 10],  # Menor 7
        ]

        chord = chord_shapes[tension_level]
        base_note = self.cfg.octava * 12
        root_interval = major_scale[root_index]

        step_index = self.cfg.state_harmony.get('chord_step', 0) % len(chord)
        interval = chord[step_index]
        new_note = base_note + root_interval + interval

        # Mantenir la nota dins l'octava base
        while new_note > base_note + 11:
            new_note -= 12
        while new_note < base_note:
            new_note += 12

        # Mode CAOS: afegir notes en octaves aleatòries
        if self.cfg.caos == 1 and self.cfg.caos_note != 0:
            octava_new = random.randint(0, 8)
            self.midi.play_note_full(new_note, 1, octava_new, sleep_time * 500,
                                      0, self.cfg.freqharm1, self.cfg.freqharm2)

        # Guardar estat per la següent iteració
        self.cfg.state_harmony.update({
            'previous_note': new_note,
            'chord_step': (step_index + 1) % len(chord),
            'initialized': True,
            'last_root': root_index,
            'last_tension': tension_level,
        })

        # Tocar la nota actual
        self.midi.play_note_full(new_note, 1, self.cfg.octava, sleep_time * 500,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 5: BOSC
    # =========================================================================
    # Simula els sons orgànics d'un bosc: notes aleatòries que apareixen
    # a diferents profunditats (octaves). La densitat controla quantes notes
    # "canten els ocells", i la profunditat determina si són greus o aguts.
    # 
    # Controls:
    #   CV1 (x): BPM - Velocitat del temps al bosc
    #   CV2 (y): Densitat - Nombre de notes per cicle (1-10)
    #   Slider (z): Profunditat - Octaves de rang (0-7)
    # =========================================================================
    def _mode_bosque(self, x, y, sleep_time):
        """Mode 5: Bosc - Sons orgànics
        
        Controls:
            x (CV1/GP26): Densitat (1-10)
            y (CV2/GP27): Profunditat (0-7)
        """
        
        # Distribució uniforme
        densidad = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 9.999) + 1  # 1-10
        profundidad = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 7.999)   # 0-7
        
        # Distribuir profunditat al voltant de l'octava base (tant avall com es pugui)
        octaves_down = min(profundidad, self.cfg.octava)
        octaves_up = min(profundidad, 10 - self.cfg.octava)
        base_octave = max(self.cfg.octava - octaves_down, 0)
        top_octave = min(self.cfg.octava + octaves_up, 10)
        
        nota_min = 12 * base_octave
        nota_max = 12 * top_octave + 11
        
        # Cada X iteracions, fer un "salt" (com un ocell que canvia de branca)
        if self.cfg.iteration % densidad == 0:
            salto = random.choice([-2, -1, 0, 1, 2, 4, 7])  # Interval musical
            nota_bosque = random.randint(nota_min, nota_max) + salto
        else:
            # Notes normals: aleatòries dins l'octava
            nota_bosque = random.randint(nota_min, nota_max)
        
        nota_bosque = max(0, min(127, nota_bosque))  # Assegurar rang MIDI
        gate_on = random.choice([0, 1, 1])  # 66% probabilitat de sonar
        
        if self.cfg.caos == 1:
            octava_new = random.randint(0, 8)
            if self.cfg.caos_note != 0 and gate_on:
                self.midi.play_note_full(nota_bosque, 1, octava_new, sleep_time * 500,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        elif gate_on:
            self.midi.play_note_full(nota_bosque, 1, self.cfg.octava, sleep_time * 500,
                                      0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 6: ESCALA CV
    # =========================================================================
    # Quantitzador d'escales modals. Toca seqüències seguint les 7 escales
    # gregorianes (modes musicals antics). Perfecte per crear melodies que
    # sempre "sonen bé" dins d'una tonalitat específica.
    # 
    # Controls:
    #   CV1 (x): BPM - Velocitat de la seqüència
    #   CV2 (y): Salt melòdic - Velocitat d'avançament (1-32)
    #   Slider (z): Tonalitat - Escala modal (0-6)
    # 
    # Escales:
    #   0=Jònic (Major), 1=Dòric, 2=Frigi, 3=Lidi, 4=Mixolidi, 5=Eòlic (Menor), 6=Locri
    # =========================================================================
    def _mode_escala(self, x, y, sleep_time):
        """Mode 6: Escala CV - Quantitzador d'escales
        
        Controls:
            x (CV1/GP26): Tonalitat/escala (0-6)
            y (CV2/GP27): Velocitat (1-32)
        """
        
        escalas = {
            0: [0, 2, 4, 5, 7, 9, 11],  # Jònic (Major)
            1: [2, 4, 6, 7, 9, 11, 1],  # Dòric
            2: [4, 6, 8, 9, 11, 1, 3],  # Frigi
            3: [5, 7, 9, 10, 0, 2, 4],  # Lidi
            4: [7, 9, 11, 0, 2, 4, 6],  # Mixolidi
            5: [9, 11, 1, 2, 4, 6, 8],  # Eòlic (Menor)
            6: [11, 1, 3, 4, 6, 8, 10], # Locri
        }
        
        # Distribució uniforme
        tonalidad = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 6.999)  # 0-6
        escala = escalas[tonalidad]
        salto = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 31.999) + 1  # 1-32
        
        # Calcular nota base de l'octava
        nota_base = 12 * self.cfg.octava
        
        # Calcular què nota de l'escala tocar (avança segons "salto")
        indice = (self.cfg.iteration * salto) % len(escala)
        nota = nota_base + escala[indice]  # Nota base + interval de l'escala
        nota = max(0, min(127, nota))      # Assegurar rang MIDI vàlid
        
        # Tocar la nota de l'escala
        self.midi.play_note_full(nota, 1, self.cfg.octava, sleep_time * 500,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 7: EUCLIDIA
    # =========================================================================
    # Genera ritmes matemàticament perfectes. L'algorisme euclidià distribueix
    # X pulsos en Y steps de la manera més uniforme possible. Es fa servir
    # en música tradicional de tot el món (rumba, bossa nova, etc.).
    # 
    # Controls:
    #   CV1 (x): BPM - Velocitat del ritme
    #   CV2 (y): Pulsos - Notes actives (1-64)
    #   Slider (z): Steps - Llargada del patró (1-64)
    # 
    # Exemple: 3 pulsos en 8 steps = [X..X..X.] (tresillo afro-cubano)
    # =========================================================================
    def _mode_euclidiano(self, x, y, sleep_time):
        """Mode 7: Euclidia - Ritmes euclidians
        
        Controls:
            x (CV1/GP26): Pulsos (1-32)
            y (CV2/GP27): Accents (1-32)
        """
        
        # Estat persistent
        state = self.cfg.state_euclid
        if not state['initialized']:
            state.update({
                'initialized': True,
                'pattern': [0] * 32,
                'accent_map': [0] * 32,
                'pulses': -1,
                'accent_level': -1,
                'position': 0,
                'degree': 0,
                'direction': 1,
                'previous_note': None,
            })

        # Distribució uniforme
        pulses = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 31.999) + 1  # 1-32
        accent_level = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 31.999) + 1  # 1-32

        major_scale = [0, 2, 4, 5, 7, 9, 11]
        base_note = max(0, min(12 * self.cfg.octava, 120))

        if state['previous_note'] is None:
            state['previous_note'] = base_note + major_scale[0]

        # Recalcular patró o accents si ha canviat algun paràmetre
        if pulses != state['pulses'] or accent_level != state['accent_level']:
            if pulses > 0:
                pattern = algorithms.generar_ritmo_euclideo(pulses, 32)
            else:
                pattern = [0] * 32

            accent_map = [0] * 32
            if pulses > 0 and accent_level > 0:
                ones_idx = [idx for idx, value in enumerate(pattern) if value == 1]
                accent_count = min(len(ones_idx), accent_level)
                if accent_count > 0:
                    spacing = len(ones_idx) / accent_count
                    for i in range(accent_count):
                        target = ones_idx[min(len(ones_idx) - 1, int(i * spacing))]
                        accent_map[target] = 1

            state.update({
                'pattern': pattern,
                'accent_map': accent_map,
                'pulses': pulses,
                'accent_level': accent_level,
                'position': 0,
                'degree': 0,
                'direction': 1,
                'previous_note': base_note + major_scale[0],
            })

        step_index = state['position'] % 32
        gate = state['pattern'][step_index] if state['pattern'] else 0
        accent = state['accent_map'][step_index] if state['accent_map'] else 0

        current_note = state['previous_note'] or (base_note + major_scale[0])
        play = 0

        if gate == 1:
            step_size = 2 if accent else 1
            degree = state['degree']
            direction = state['direction']
            new_degree = degree + (direction * step_size)

            if new_degree >= len(major_scale):
                new_degree = len(major_scale) - 1
                direction = -1
            elif new_degree < 0:
                new_degree = 0
                direction = 1

            current_note = base_note + major_scale[new_degree]

            # Aplicar una desviació mínima segons el slider (±1 semitò)
            # slider_offset = int(round(((slider_steps / 127.0) - 0.5) * 2)) # No hi ha slider en aquesta signatura
            # current_note += slider_offset

            state['degree'] = new_degree
            state['direction'] = direction
            state['previous_note'] = current_note
            play = 1

        current_note = max(0, min(127, current_note))

        # Mode CAOS: mantenim compatibilitat amb octaves aleatòries
        if self.cfg.caos == 1 and play == 1 and self.cfg.caos_note != 0:
            octava_new = random.randint(0, 8)
            self.midi.play_note_full(current_note, 1, octava_new, sleep_time * 500,
                                      0, self.cfg.freqharm1, self.cfg.freqharm2)

        self.midi.play_note_full(current_note, play, self.cfg.octava, sleep_time * 500,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)

        state['position'] = (step_index + 1) % 32
        self.cfg.position = state['position']
    
    # =========================================================================
    # MODE 8: COSMOS
    # =========================================================================
    # El mode més complex: combina TOTS els algorismes anteriors en una
    # síntesi híbrida. Barreja Fractal + Sinusoidal + Harmonia + Euclidia
    # per crear textures musicals úniques i impossibles d'aconseguir d'altra manera.
    # 
    # Controls:
    #   CV1 (x): BPM + Coordenada X Fractal
    #   CV2 (y): Harmonia + Sinusoidal
    #   Slider (z): Harmonia + Sinusoidal + Ritme
    # =========================================================================
    def _mode_cosmos(self, x, y, sleep_time, cx, cy):
        """Mode 8: Cosmos - Síntesi fractal
        
        Controls:
            x (CV1/GP26): Freq/Perfil
            y (CV2/GP27): Amplitude/Tensió
        """
        # Component 1: Nota del fractal Mandelbrot
        fractal_note = algorithms.mandelbrot_to_midi(cx, cy)
        
        # Component 2: Sinusoidal (distribució uniforme)
        freq_ona = converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 127
        amplitude_ona = converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 2
        
        sinusoidal_note = int(algorithms.sinusoidal_value_2(
            self.cfg.iteration,
            freq_ona,
            amplitude_ona / 100
        ))
        
        # Component 3: Harmònica (distribució uniforme)
        perfil = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 10.999)
        tensio = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 10.999)
        
        armonica = algorithms.harmonic_next_note(perfil, tensio, fractal_note)
        
        # Combinar
        base_note = (fractal_note + sinusoidal_note + armonica) // 3
        base_note = max(0, min(127, base_note))
        
        if self.cfg.caos > 0:
            caos_offset = random.randint(-self.cfg.caos, self.cfg.caos)
            base_note = max(0, min(127, base_note + caos_offset))
            if self.cfg.caos_note == 0:
                base_note = 0
        
        # Component 4: Ritme euclidià (distribució uniforme)
        pulsos = int(converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 35.999) + 1
        steps_ritme = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 35.999) + 2
        
        ritmo = algorithms.generar_ritmo_euclideo(pulsos, steps_ritme)
        pattern_value = ritmo[self.cfg.iteration % len(ritmo)]  # Ritme actual

        # Invertir el gate: per defecte encès, s'apaga quan el patró és 0
        play = 1
        if pattern_value == 0:
            play = 0 if (self.cfg.iteration % 2 == 0) else 1

        # Tocar la nota còsmica!
        self.midi.play_note_full(base_note, play, self.cfg.octava, sleep_time * 500,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Incrementar iteració (amb reinici a 60000)
        self.cfg.iteration = (self.cfg.iteration + 1) % 60000
    
    # =========================================================================
    # MODE 9: CAMPANETES
    # =========================================================================
    def _mode_campanetes(self, x, y, sleep_time):
        """Mode 9: Campanetes - Campanes musicals amb progressió harmònica
        
        Controls:
            x (CV1/GP26): Densitat (% de notes que sonen vs silencis)
            y (CV2/GP27): Brillantor (durada del gate, més llarg = més brillant)
        """
        
        # CV1: Densitat (probabilitat de tocar)
        densitat = converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max) * 100  # 0-100%
        
        # CV2: Brillantor via durada del gate (10% a 100% del beat)
        brillantor_pct = converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max)
        gate_ms = sleep_time * 1000 * (0.1 + brillantor_pct * 0.9)
        
        # Intervals de campana (acord major: Do-Mi-Sol)
        intervals_campana = [0, 4, 7]
        
        # Progressió harmònica: cada 3 notes, pujar una tercera menor (3 semitons)
        cicle_complet = self.cfg.iteration // len(intervals_campana)  # Cada 3 notes
        nota_base_offset = (cicle_complet * 3) % 12  # Pujar per terceres dins l'octava
        
        # Nota base amb progressió
        nota_base = 12 * self.cfg.octava + nota_base_offset
        indice = self.cfg.iteration % len(intervals_campana)
        nota = max(0, min(127, nota_base + intervals_campana[indice]))
        
        # Decidir si toca o silenci segons densitat
        probabilitat = random.randint(0, 100)
        gate_on = 1 if probabilitat < densitat else 0
        
        # Mode CAOS: campanes en octaves aleatòries
        if self.cfg.caos == 1 and self.cfg.caos_note != 0 and gate_on:
            octava_new = random.randint(0, 8)
            self.midi.play_note_full(nota, 1, octava_new, gate_ms,
                                      0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Campana principal (usa harmònics globals com tots els altres modes)
        self.midi.play_note_full(nota, gate_on, self.cfg.octava, gate_ms,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 10: SEGONES
    # =========================================================================
    def _mode_segones(self, x, y, sleep_time):
        """Mode 10: Segones - Dues notes simultànies amb interval
        
        Controls:
            x (CV1/GP26): Direcció (0-50% avall, 50-100% amunt)
            y (CV2/GP27): Separació entre notes (1-12 semitons)
        
        Notes:
            - PWM1 toca la nota base
            - PWM2 toca la nota base + separació
        """
        
        # Inicialitzar estat si no existeix
        if not hasattr(self.cfg, 'segones_nota_anterior'):
            self.cfg.segones_nota_anterior = 12 * self.cfg.octava
        
        # CV1: Direcció (0-0.5 = avall, 0.5-1 = amunt)
        direccio_pct = converters.normalize(x, self.cfg.cv1_min, self.cfg.cv1_max)
        
        # CV2: Separació entre notes (1-12 semitons, default 2 = segona)
        separacio = int(converters.normalize(y, self.cfg.cv2_min, self.cfg.cv2_max) * 11.999) + 1
        
        # Calcular nova nota: moviment de 1 to (2 semitons)
        if direccio_pct < 0.5:
            nova_nota = self.cfg.segones_nota_anterior - 2  # Avall
        else:
            nova_nota = self.cfg.segones_nota_anterior + 2  # Amunt
        
        # Mantenir dins del rang MIDI
        nova_nota = max(0, min(127, nova_nota))
        if nova_nota <= 0:
            nova_nota = 2
        elif nova_nota >= 127:
            nova_nota = 125
        
        self.cfg.segones_nota_anterior = nova_nota
        
        # Tocar nota amb dues freqüències simultànies:
        # PWM1 = nota base (via freqharm_base global)
        # PWM2 = nota base + separacio (via freq1 paràmetre)
        # PWM3 = nota base (via freq2=0)
        
        # Caos
        if self.cfg.caos == 1 and self.cfg.caos_note != 0:
            octava_new = random.randint(0, 8)
            self.midi.play_note_full(nova_nota, 1, octava_new, sleep_time * 500,
                                      0, separacio, 0)  # freq1=separacio
        
        # Nota principal amb dues freqüències
        self.midi.play_note_full(nova_nota, 1, self.cfg.octava, sleep_time * 500,
                                  0, separacio, 0)  # freq1=separacio per PWM2


