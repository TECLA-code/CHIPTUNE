# TECLA Professional – Guia completa del dispositiu

## 1. Visió general

TECLA Professional és un sintetitzador modular per Raspberry Pi Pico executat amb CircuitPython. El sistema combina generació de notes MIDI, síntesi PWM a tres canals i una interfície d’usuari basada en potenciòmetres, botons, OLED i LEDs. L’arquitectura es basa en un bucle principal cooperatiu amb un gestor RTOS lleuger que manté els temps crítics de gate i NoteOff.

### Objectius principals

- **Temps real estricte**: latència mínima en la gestió de notes, amb gates sincronitzats al BPM.  
- **Modes musicals múltiples**: rang d’algorismes generatius (Fractal, Riu, Tempesta, Harmonia, Bosc, Escala, Euclidia, Cosmos i Sequenciador).  
- **Personalització immediata**: configuració d’harmònics, duty cycles i rangs de CV sense reiniciar el dispositiu.  
- **Operació robusta**: gestió centralitzada de NoteOff, suport All Notes Off, i tractament dels errors MIDI.

## 2. Arquitectura del sistema

| Component | Funció | Fitxer principal |
|-----------|--------|------------------|
| `main.py` | Bucle principal, coordinació de RTOS, lectura d’inputs, execució de modes i display | `main.py` |
| `core/config.py` | Estat global, constants de timing, configuració de rangs i paràmetres persistents | `core/config.py` |
| `core/hardware.py` | Inicialització de pins, PWM, LEDs i display; animacions i lectura de CV | `core/hardware.py` |
| `core/midi_handler.py` | Enviament de NoteOn/Off, gestió d’harmònics i PWM, registre d’errors MIDI | `core/midi_handler.py` |
| `core/rtos.py` | Scheduler temps real per gates i NoteOff programats | `core/rtos.py` |
| `core/button_handler.py` | Debounce i gestió d’events dels botons | `core/button_handler.py` |
| `core/clock.py` | Filtres de BPM, generació de ticks i `idle_sleep` adaptatiu | `core/clock.py` |
| `modes/loader.py` | Implementació dels modes musicals i seqüenciador | `modes/loader.py` |
| `display/` | Animacions i pantalles OLED (informació, calibratge, tracker) | `display/` |
| `music/` | Conversions musicals (BPM, harmonics, mapping CV) | `music/` |

## 3. Flux d’arrencada

1. **Inicialització de hardware**: `TeclaHardware()` configura PWM, ADC, botons i display.  
2. **Creació de gestors**: RTOS, MIDI, clock, modes, display i animacions.  
3. **Registre de temps base**: `cfg.last_note_time` i derivats estableixen referència per al bucle.  
4. **Animació de benvinguda**: seqüència LED + pantalla estàtica.  
5. **Entrada al bucle principal**: `while True` manté la rutina amb prioritats (RTOS, inputs, modes, display, idle sleep).

## 4. Interfície física

### Controls

- **Potenciòmetres (CV1, CV2, Slider)**: control dinàmic de BPM i paràmetres segons mode. Rang calibrable per separat.  
- **Botons**: seleccionen modes, accedeixen a configuració, activen el tracker, etc. Debounce configurat a 11 ms.  
- **Display OLED 128x64**: mostra estat general, paràmetres del tracker i pantalles de calibratge.  
- **LEDs 1-7**: indicadors dinàmics per gates, harmonics, duty, mode loop i configuració.  
- **Sortida MIDI i jack de gate**: gate sincronitzat amb LED2 i PWM de sortida.

### Senyalització LED clau

- **LED2**: estat del gate (activat durant NoteOn).  
- **LED1 / LED4**: polsos quan hi ha canvis d’harmònics 1 i 2.  
- **LED5**: polsos quan es modifiquen duty cycles.  
- **LED3/6/7**: animació de loop actiu o patró d’indicació del menú de configuració (`configout`).

## 5. Modes musicals

| Mode | Descripció | Fonts principals |
|------|-------------|------------------|
| 1 – Fractal | Notes basades en coordenades Mandelbrot amb suport caos | `modes/loader.py` (`_mode_mandelbrot`)
| 2 – Riu | Flux sinusoidal amb corrent i turbulència | `_mode_rio`
| 3 – Tempesta | Llamps aleatoris + pluja, intensitat i freqüència via CV | `_mode_tormenta`
| 4 – Harmonia | Progressions harmòniques adaptatives | `_mode_armonia`
| 5 – Bosc | Textures orgàniques amb salts interval·lars | `_mode_bosque`
| 6 – Escala | Escales modals amb control de profunditat | `_mode_escala`
| 7 – Euclidia | Ritmes matemàtics distribuïts | `_mode_euclidiano`
| 8 – Cosmos | Fusió de Fractal + Sinusoidal + Harmonia + Euclidia | `_mode_cosmos`
| 9 – Sequencer | Tracker tipus GameBoy amb pàgines d’edició/gate/longitud | `_mode_sequencer`

> **Nota**: el Mode 9 bloqueja la resta de modes fins que es deixa el tracker via botó dedicat.

## 6. Configuració i ajustos en temps real

`cfg.configout` permet navegar per diferents paràmetres (duty1-3, harmonics base/1/2, rangs CV1/CV2). Els LEDs 6-3-7 mostren patrons únics segons el paràmetre actiu.  

Els duty cycles individuals (`cfg.duty1..3`) i harmonics (`cfg.freqharm_base/1/2`) s’apliquen immediatament a la sortida PWM i són persistits en estat global. Els valors per defecte són 50% i harmònics a 0.

## 7. Calibratge de CV

- **Activació**: botó dedicat obre el mode calibratge.  
- **Procés**: `calibration.procesar_calibracion()` llegeix els valors min/max mentre l’usuari mou els potenciòmetres.  
- **Refresc pantalla**: la pantalla de calibratge es redibuixa cada `cfg.calibration_frame_interval` (50 ms) sense bloquejar el bucle principal.  
- **Persistència**: `cfg.cv1_min/max` i `cfg.cv2_min/max` actualitzats serveixen per clamp i percentatges.

## 8. Gestió de temps i gates

- `MasterClock` filtra BPM i genera `sleep_time`.  
- `RTOSManager.update()` és cridat a cada iteració per comprovar:  
  - **Prioritat 1**: tancament del gate quan s’arriba a `cfg.gate_off_time`.  
  - **Prioritat 2**: NoteOff programats (`cfg.note_off_schedule`).  
- `MidiHandler.play_note_full()` calcula `gate_duration` amb `get_gate_duration_for_mode()` (percentatge del període segons mode) i programa un NoteOff segur entre `NOTE_OFF_MIN_DURATION` i `NOTE_OFF_MAX_DURATION`.

## 9. MIDI i PWM

- Enviament de **NoteOn** amb velocitat 100.  
- Tres canals PWM configuren portadora i dos harmònics (`apply_harmonic_interval`).  
- **All Notes Off**: accessible via `midi_handler.all_notes_off()` i automàticament en parades, errors o bloqueig per error.  
- Gestió d’errors MIDI: `_handle_midi_error()` incrementa `cfg.midi_error_count`, registra l’excepció i estableix una pausa (`cfg.error_pause_until`) per evitar saturacions.

## 10. Gestió d’errors i recuperació

- **Bucle principal**: qualsevol excepció mostra l’error a pantalla, emet logs, envia All Notes Off i estableix una pausa de 5 segons abans de reprendre la lectura.  
- **KeyboardInterrupt**: atura RTOS, envia All Notes Off, neteja LEDs i mostra “STOPPED”.  
- **Error MIDI**: pausa de 0,2 s per donar temps a estabilitzar la línia MIDI.

## 11. Display i modes visuals

- **Pantalla principal**: mostra mode actiu, paràmetres, nota actual i BPM.  
- **Tracker**: pàgines per editar notes/gate, canviar longitud i veure informació resumida.  
- **Animacions idle**: ull dinàmic, GameBoy tracker i animacions d’icones segons mode.  
- **Mode calibratge**: barres de percentatge de CV i valors calibrats.

## 12. Proves i validació

### Bateria recomanada

1. **Test de tempos extrems**: operar a 20 BPM i 220 BPM durant com a mínim 10 minuts per cada mode.  
2. **Stress tracker**: reproduir patrons de 32 steps amb canvis de gate ràpids i editar notes durant la reproducció.  
3. **Simulació d’errors MIDI**: desconnectar/reconnectar el bus per validar la pausa d’errors i All Notes Off.  
4. **Long run**: sessió de 30 minuts amb canvis de mode continus per garantir estabilitat del RTOS i timings.  
5. **Calibratge repetit**: entrar/sortir de calibratge durant 5 minuts comprovant que la pantalla no flashein ni bloqueja.

## 13. Còpies de seguretat i desplegament

- Recomanat copiar periòdicament el directori del projecte a un directori `CHECKPOINT/` amb data (`BACKUP_YYYYMMDD`).  
- Verificar que `code.py` o `main.py` es troba a l’arrel del dispositiu CircuitPython juntament amb tots els mòduls requerits.  
- Ajustar la configuració a `core/config.py` abans de desplegar (octava inicial, configuració de rangs, etc.).

## 14. Manteniment i bones pràctiques

- **No interrompre** la tensió del dispositiu mentre `cfg.playing_notes` sigui no-buit; utilitzar el botó de parada o el mode 0.  
- **Registrar canvis** significatius en un changelog (e.g. TECLA_GUIDE) i actualitzar `README.md` si es modifica l’estructura.  
- **Monitoritzar** `cfg.midi_error_count` i `cfg.last_midi_error` per detectar cables defectuosos o perifèrics problemàtics.  
- **Respirar intervals**: `MasterClock.idle_sleep()` garanteix un descans mínim de CPU; no afegir `time.sleep()` directament al bucle principal.  
- **Seguiment de configuració**: fer servir els LEDs per identificar ràpidament el paràmetre de configuració actiu.

## 15. Taula ràpida de paràmetres clau

| Paràmetre | Valor per defecte | Notes |
|-----------|-------------------|-------|
| `cfg.octava` | 5 | Octava global de reproducció |
| `cfg.current_sleep_time` | 0.3 s | Actualitzat pel rellotge mestre |
| `GATE_PERCENTAGES` | 5% – 20% | Percentatge del període segons mode |
| `NOTE_OFF_MIN_DURATION` | 20 ms | Límit inferior per NoteOff |
| `NOTE_OFF_MAX_DURATION` | 1 s | Límit superior per NoteOff |
| `loop_sleep_min` | 0.5 ms | Descans mínim per iteració |
| `loop_sleep_max` | 5 ms | Descans màxim |
| `loop_sleep_factor` | 0.05 | Relació del temps restant |

## 16. Glossari

- **Gate**: senyal digital que indica quan la nota està activa; sincronitzat amb LED2 i sortida jack.  
- **Harmònic**: desplaçament en semitons que controla els canals PWM addicionals per enriquir el timbre.  
- **Loop Mode**: mode musical automàtic (1-8) o tracker (9).  
- **RTOS**: gestor de tasques de temps real que evita latència en gates i NoteOff.  
- **Tracker**: seqüenciador pas a pas integrat amb 32 steps màxims.

## 17. Historial de revisió

- **2025-12-06**: Actualització major amb gestió millorada de NoteOff, pausa per errors MIDI, i guia completa del dispositiu.
