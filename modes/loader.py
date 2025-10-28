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
#   8. Cosmos     - Combinació de tots els algorismes
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
    
    def execute_mode(self, mode_num, x, y, z, sleep_time, cx, cy):
        """Executa el mode musical seleccionat
        
        Aquesta funció és com un "director d'orquestra" que decideix
        quin mode musical s'ha de tocar segons el número de mode actual.
        
        Arguments:
            mode_num: Número del mode (1-8)
            x: Voltatge del CV1 (sempre controla el BPM)
            y: Voltatge del CV2 (paràmetre secundari del mode)
            z: Voltatge del Slider (paràmetre terciari del mode)
            sleep_time: Temps entre notes (calculat des del BPM)
            cx, cy: Coordenades per al mode Fractal
        """
        
        if mode_num == 1:
            self._mode_mandelbrot(cx, cy, sleep_time)
        elif mode_num == 2:
            self._mode_rio(y, z, sleep_time)
        elif mode_num == 3:
            self._mode_tormenta(x, y, z, sleep_time)
        elif mode_num == 4:
            self._mode_armonia(y, z, sleep_time)
        elif mode_num == 5:
            self._mode_bosque(y, z, sleep_time)
        elif mode_num == 6:
            self._mode_escala(y, z, sleep_time)
        elif mode_num == 7:
            # Reset position si està fora de rang (canvi de mode anterior)
            steps_total = converters.steps(z) // 2 + 1
            if self.cfg.position >= steps_total:
                self.cfg.position = 0
            self._mode_euclidiano(y, z, sleep_time)
        elif mode_num == 8:
            self._mode_cosmos(y, z, sleep_time, cx, cy)
        elif mode_num == 9:
            self._mode_sequencer(x, z, sleep_time)
    
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
                self.midi.play_note_full(note, 1, octava_new, sleep_time * 20,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Toca la nota principal en l'octava configurada
        self.midi.play_note_full(note, 1, self.cfg.octava, sleep_time * 20,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 2: RIU
    # =========================================================================
    # Simula el flux d'un riu amb ones sinusoidals. El corrent determina
    # com de ràpid "flueixen" les notes, i la turbulència afegeix onades
    # i remolins aleatoris. És com escoltar música que fluïx com l'aigua.
    # 
    # Controls:
    #   CV1 (x): BPM - Velocitat del temps
    #   CV2 (y): Corrent - Velocitat del flux (0-12.7)
    #   Slider (z): Turbulència - Onades i remolins (0-127)
    # =========================================================================
    def _mode_rio(self, y, z, sleep_time):
        """Mode 2: Riu - Notes fluides com aigua"""
        
        # Converteix els voltatges en paràmetres musicals
        corriente = converters.steps(y) / 10  # Velocitat del flux: 0-12.7
        turbulencia = converters.steps(z)     # Força de les onades: 0-127
        rio_time = time.time()                # Temps actual (per les ones)
        
        # Calcular el rang de notes segons l'octava actual
        nota_min = 12 * self.cfg.octava  # Nota més baixa de l'octava
        nota_max = nota_min + 11          # Nota més alta de l'octava
        
        # El riu "avanc¸a" sempre endavant (augmenta la nota base)
        self.cfg.rio_base = (self.cfg.rio_base + corriente) % 12
        nota_base = nota_min + self.cfg.rio_base
        
        # Afegir moviment ondulatori (com ones a l'aigua)
        wave = math.sin(rio_time * 0.8) * (corriente * 0.5)      # Ona lenta
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
                self.midi.play_note_full(nota_rio, 1, octava_new, sleep_time * 20,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Toca la nota principal del riu
        self.midi.play_note_full(nota_rio, gate_on, self.cfg.octava, sleep_time * 20,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
    
    # =========================================================================
    # MODE 3: TEMPESTA
    # =========================================================================
    # Simula una tempesta amb pluja constant i llamps aleatoris. La pluja
    # crea notes suaus i constants, mentre que els llamps generen arpegis
    # ascendents o descendents sobtats. Com escoltar una tempesta real!
    # 
    # Controls:
    #   CV1 (x): BPM + Força del vent (intensitat general)
    #   CV2 (y): Intensitat de la pluja (densitat de notes)
    #   Slider (z): Freqüència dels llamps (probabilitat de relàmpecs)
    # =========================================================================
    def _mode_tormenta(self, x, y, z, sleep_time):
        """Mode 3: Tempesta - Pluja i llamps dinàmics"""
        
        # Escala musical pel arpegi dels llamps (intervals musicals)
        escala_tormenta = [0, 3, 5, 7, 10]  # Tercera, Quarta, Quinta, Sèptima
        
        # Convertir voltatges en paràmetres
        fuerza_viento = converters.steps(x)       # Força del vent: 0-127
        intensidad_lluvia = converters.steps(y)   # Intensitat pluja: 0-127
        frecuencia_rayos = converters.steps(z)    # Freqüència llamps: 0-127
        
        # Calcular nota base segons la intensitat de la pluja
        nota_base = 12 * min(self.cfg.octava, 9) + int(intensidad_lluvia * 0.09)
        nota_base = max(0, min(127, nota_base))  # Assegurar rang MIDI vàlid
        
        # Decidir si toca un llamp (aleatori segons freqüència)
        if random.randint(0, 1000) < (frecuencia_rayos * 8):  # Probabilitat 0-101.6%
            # LLAMP! Generar arpegi ascendent o descendent
            direccion = 1 if random.random() > 0.3 else -1  # 70% amunt, 30% avall
            
            # Tocar totes les notes de l'arpegi ràpidament
            for i, intervalo in enumerate(escala_tormenta[::direccion]):
                multiplicador = max(1, min(3, (i+1)))  # Intensificar el llamp
                nota_relampago = nota_base + (intervalo * direccion * multiplicador)
                nota_relampago = max(0, min(127, nota_relampago))  # Rang vàlid
                
                # Mode CAOS: llamps en octaves aleatòries
                if self.cfg.caos == 1:
                    octava_new = random.randint(0, 8)
                    if self.cfg.caos_note != 0:
                        self.midi.play_note_full(nota_relampago, 1, octava_new, sleep_time * 20,
                                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
                else:
                    # Toca nota del llamp
                    self.midi.play_note_full(nota_relampago, 1, self.cfg.octava, sleep_time * 20,
                                              0, self.cfg.freqharm1, self.cfg.freqharm2)
        else:
            # PLUJA: Notes constants amb petites variacions
            variacion_lluvia = random.randint(-3, 3)  # Variació aleatòria ±3 semitons
            nota_lluvia = max(0, min(127, nota_base + variacion_lluvia))
            
            # Mode CAOS: pluja en octaves aleatòries
            if self.cfg.caos == 1:
                octava_new = random.randint(0, 8)
                if self.cfg.caos_note != 0:
                    self.midi.play_note_full(nota_lluvia, 1, octava_new, sleep_time * 20,
                                              0, self.cfg.freqharm1, self.cfg.freqharm2)
            else:
                # Toca nota de la pluja
                self.midi.play_note_full(nota_lluvia, 1, self.cfg.octava, sleep_time * 20,
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
        
        # Inicialitzar estat la primera vegada
        if not self.cfg.state_harmony['initialized']:
            self.cfg.state_harmony.update({
                'previous_note': 60,      # Nota inicial (Do central)
                'last_profile': 0,        # Últim perfil usat
                'last_tension': 0,        # Última tensió usada
                'initialized': True       # Marcar com inicialitzat
            })
        
        # Convertir voltatges en paràmetres harmònics
        x_param = converters.steps(y) % 128  # Perfil harmònic: 0-127
        y_param = converters.steps(z) % 128  # Tensió harmònica: 0-127
        
        # Calcular la millor nota següent (algorisme harmònic)
        new_note = algorithms.harmonic_next_note(x_param, y_param, 
                                                  self.cfg.state_harmony['previous_note'])
        
        # Mantenir nota dins l'octava actual
        nota_min = 12 * self.cfg.octava
        nota_max = nota_min + 11
        new_note = max(nota_min, min(nota_max, new_note))
        
        # Mode CAOS: afegir notes en octaves aleatòries
        if self.cfg.caos == 1:
            octava_new = random.randint(0, 8)
            if self.cfg.caos_note != 0:
                self.midi.play_note_full(new_note, 1, octava_new, sleep_time * 20,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Guardar estat per la següent nota (memòria harmònica)
        self.cfg.state_harmony.update({
            'previous_note': new_note,                   # Recordar aquesta nota
            'last_profile': min(x_param // 21, 5),      # Recordar perfil
            'last_tension': min(y_param // 32, 3)       # Recordar tensió
        })
        
        # Tocar cada 2 iteracions per ritme harmònic
        play = 1 if self.cfg.iteration % 2 == 0 else 0
        self.midi.play_note_full(new_note, play, self.cfg.octava, sleep_time * 20,
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
    def _mode_bosque(self, y, z, sleep_time):
        """Mode 5: Bosc - Sons orgànics i imprevisibles"""
        
        # Convertir voltatges en paràmetres del bosc
        densidad = converters.steps(y) // 13 + 1  # Densitat: 1-10 notes/cicle
        profundidad_raw = converters.steps(z) // 16   # Profunditat: 0-7 octaves
        profundidad = min(profundidad_raw, 10 - self.cfg.octava)  # Limitar rang
        
        # Calcular rang de notes segons profunditat
        nota_min = 12 * (self.cfg.octava + profundidad)  # Nota més greu
        nota_max = nota_min + 11                          # Nota més aguda
        
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
                self.midi.play_note_full(nota_bosque, 1, octava_new, sleep_time * 20,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        elif gate_on:
            self.midi.play_note_full(nota_bosque, 1, self.cfg.octava, sleep_time * 20,
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
    def _mode_escala(self, y, z, sleep_time):
        """Mode 6: Escala CV - Quantitzador d'escales modals"""
        
        # Definir les 7 escales modals (intervals en semitons)
        escalas = {
            0: [0, 2, 4, 5, 7, 9, 11],  # Jònic (Major) - Alegre
            1: [2, 4, 6, 7, 9, 11, 1],  # Dòric - Jazz
            2: [4, 6, 8, 9, 11, 1, 3],  # Frigi - Espanyol
            3: [5, 7, 9, 10, 0, 2, 4],  # Lidi - Etèric
            4: [7, 9, 11, 0, 2, 4, 6],  # Mixolidi - Blues
            5: [9, 11, 1, 2, 4, 6, 8],  # Eòlic (Menor) - Trist
            6: [11, 1, 3, 4, 6, 8, 10], # Locri - Tensó
        }
        
        # Seleccionar l'escala segons el slider
        tonalidad = converters.steps(z) // 18  # Convertir 0-127 en 0-6
        tonalidad = min(tonalidad, 6)          # Assegurar rang vàlid
        escala = escalas[tonalidad]            # Obtenir l'escala seleccionada
        
        # Velocitat d'avançament per la seqüència
        salto = converters.steps(y) // 4 + 1  # Velocitat: 1-32
        
        # Calcular nota base de l'octava
        nota_base = 12 * self.cfg.octava
        
        # Calcular què nota de l'escala tocar (avança segons "salto")
        indice = (self.cfg.iteration * salto) % len(escala)
        nota = nota_base + escala[indice]  # Nota base + interval de l'escala
        nota = max(0, min(127, nota))      # Assegurar rang MIDI vàlid
        
        # Tocar la nota de l'escala
        self.midi.play_note_full(nota, 1, self.cfg.octava, sleep_time * 10,
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
    def _mode_euclidiano(self, y, z, sleep_time):
        """Mode 7: Euclidia - Ritmes algorítmics perfectes"""
        
        # Convertir voltatges en paràmetres rítmics
        pulsos = converters.steps(y) // 2 + 1        # Pulsos: 1-64
        steps_total = converters.steps(z) // 2 + 1   # Steps: 1-64
        
        # Reiniciar posició si arriba al final del patró
        if self.cfg.position >= steps_total:
            self.cfg.position = 0
        
        # Generar el patró rítmic euclidià (llista de 0s i 1s)
        ritmo = algorithms.generar_ritmo_euclideo(pulsos, steps_total)
        to_play = ritmo[self.cfg.position]  # Agafar el valor actual (0 o 1)
        
        # Nota base amb petita variació aleatòria
        nota_base = (self.cfg.octava * 12) + random.randint(-3, 3) if self.cfg.position > 0 else 0
        nota_base = max(0, min(127, nota_base))  # Assegurar rang MIDI
        
        # Mode CAOS: ritmes en octaves aleatòries
        if self.cfg.caos == 1:
            octava_new = random.randint(0, 8)
            if self.cfg.caos_note != 0:
                self.midi.play_note_full(nota_base, to_play, octava_new, sleep_time * 20,
                                          0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Tocar la nota segons el ritme euclidià (to_play = 0 o 1)
        self.midi.play_note_full(nota_base, to_play, self.cfg.octava, sleep_time * 20,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Avançar posició pel següent step
        self.cfg.position += 1
    
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
    def _mode_cosmos(self, y, z, sleep_time, cx, cy):
        """Mode 8: Cosmos - Síntesi híbrida de tots els algorismes"""
        # Component 1: Nota del fractal Mandelbrot
        fractal_note = algorithms.mandelbrot_to_midi(cx, cy)
        
        # Component 2: Nota sinusoidal (ones)
        sinusoidal_note = int(algorithms.sinusoidal_value_2(
            self.cfg.iteration,         # Posició temporal
            converters.steps(z),         # Freqüència de l'ona
            converters.steps(y) * 2 / 100  # Amplitud de l'ona
        ))
        
        # Component 3: Nota harmònica
        armonica = algorithms.harmonic_next_note(
            converters.steps_melo(y),  # Perfil harmònic
            converters.steps_melo(z),  # Tensió harmònica
            fractal_note               # Nota anterior
        )
        
        # Combinar les 3 components en una sola nota (mitjana)
        base_note = (fractal_note + sinusoidal_note + armonica) // 3
        base_note = max(0, min(127, base_note))  # Assegurar rang MIDI
        
        # Decidir octava (normal o caòtica)
        octava_to_use = self.cfg.octava
        if self.cfg.caos == 1:
            octava_to_use = random.randint(0, 8)  # Octava aleatòria
            if self.cfg.caos_note == 0:
                base_note = 0  # Silenci caòtic
        
        # Component 4: Ritme euclidià per al gate
        ritmo = algorithms.generar_ritmo_euclideo(
            converters.steps_ritme(y),      # Pulsos
            converters.steps_ritme(z) + 1   # Steps
        )
        to_play = ritmo[self.cfg.iteration % len(ritmo)]  # Ritme actual
        
        # Combinar ritme euclidià amb ritme de 2 steps
        play = 1 if self.cfg.iteration % 2 == 0 else 0
        final_play = play * to_play  # Ambdos han de ser 1 per tocar
        
        # Tocar la nota còsmica!
        self.midi.play_note_full(base_note, final_play, octava_to_use, sleep_time * 20,
                                  0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Incrementar iteració (amb reinici a 60000)
        self.cfg.iteration = (self.cfg.iteration + 1) % 60000
    
    # =========================================================================
    # MODE 9: TRACKER PROGRAMABLE
    # =========================================================================
    # Tracker de notes estil GameBoy amb 3 pàgines d'edició. Permet crear
    # patrons musicals en temps real amb control total de notes i gates.
    # Com LSDJ però per a synths modulars!
    # 
    # Controls:
    #   CV1: Nota del step actual (0-127 MIDI)
    #   CV2: Sense ús (reservat)
    #   Slider: BPM - Velocitat de reproducció
    #   Extra1: Canviar pàgina (0→1→2→0)
    #   
    # Pàgina 0 (Edició):
    #   ↑↓: Ajustar gate (0-100%, steps 5%)
    #   ←→: Navegar steps
    #   
    # Pàgina 1 (Longitud):
    #   ↑↓: Ajustar longitud (8-32 steps)
    #   
    # Pàgina 2 (Info):
    #   Mostra duty/harm/oct/CV (només lectura)
    # 
    # SORTIDA: Extra2 llarg (pausa total) - ÚNICA forma de sortir
    # =========================================================================
    def _mode_sequencer(self, x, z, sleep_time):
        """Mode 9: Tracker - Seqüenciador programable en temps real"""
        
        # Activar bloqueig de mode (no es pot canviar a altres modes)
        self.cfg.sequencer_mode_active = True
        
        # Calcular BPM i sleep time (amb CV1 calibrat)
        current_bpm = converters.voltage_to_bpm(x)
        
        # Aplicar factor de velocidad al Tracker (3x más rápido)
        # Usamos min() para no exceder el límite de 220 BPM
        tracker_bpm = min(current_bpm * 3, 220)
        
        # Usar el BPM ajustado para calcular el sleep_time
        sleep_time = converters.bpm_to_sleep_time(tracker_bpm)
        
        # Guardar el BPM real para mostrar en la interfaz
        self.cfg.current_sleep_time = sleep_time  # Guardar per sincronització de gate
        self.cfg.bpm = current_bpm  # Mantener el BPM original para la interfaz
        
        # Protecció: Assegurar que edit_position està dins de rang
        if self.cfg.sequencer_edit_position >= self.cfg.sequencer_length:
            self.cfg.sequencer_edit_position = self.cfg.sequencer_length - 1
        if self.cfg.sequencer_edit_position >= 32:  # Mida array
            self.cfg.sequencer_edit_position = 31
        
        # Control de nota con el potenciómetro seleccionado (CV1 o CV2)
        if self.cfg.sequencer_page == 0:  # Solo en la página de edición de notas
            # Usar el potenciómetro seleccionado según la configuración
            # potes[2] = GP26 = CV1
            # potes[1] = GP27 = CV2
            pot_index = 2 if self.cfg.sequencer_note_pot == 1 else 1  # 2=CV1, 1=CV2
            
            # Mapear el valor del potenciómetro a 0-127
            note_value = int(converters.map_value(
                self.hw.potes[pot_index].value,
                0, 65535,  # Rango del ADC
                0, 127     # Rango MIDI
            ))
            
            if self.cfg.sequencer_note_edit_mode:
                # Modo edición: actualizar la nota pendiente
                self.cfg.sequencer_pending_note = note_value
            else:
                # Actualizar la nota directamente si no estamos en modo edición
                self.cfg.sequencer_pattern[self.cfg.sequencer_edit_position] = note_value
        
        # Reproduir nota actual del patró (amb protecció)
        play_pos = self.cfg.sequencer_play_position % min(self.cfg.sequencer_length, 32)
        current_note = self.cfg.sequencer_pattern[play_pos]
        current_gate = self.cfg.sequencer_gate[play_pos]
        
        # Sincronización LED2 + salida MIDI según estado del gate
        if current_gate == self.cfg.SEQUENCER_GATE_OFF:
            self.hw.led_2.value = False
            # No tocar nota si gate es OFF
        else:
            self.hw.led_2.value = True
            # Calcular duración proporcional al gate %
            gate_duration = self.cfg.current_sleep_time * (current_gate / 100.0)
            # Tocar la nota amb l'octava configurada
            self.midi.play_note_full(current_note, 1, self.cfg.octava, gate_duration,
                                     0, self.cfg.freqharm1, self.cfg.freqharm2)
        
        # Avançar posició de reproducció (cíclic dins la longitud del patró)
        self.cfg.sequencer_play_position = (self.cfg.sequencer_play_position + 1) % self.cfg.sequencer_length
