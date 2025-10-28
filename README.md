# TECLA - Sintetitzador MIDI Modular

TECLA Chiptune és un sintetitzador MIDI i Eurorack modular desenvolupat per a plataformes embegudes amb CircuitPython. Aquest projecte permet crear sons i seqüències musicals mitjançant diferents modes d'operació, cadascun amb les seves pròpies característiques i comportaments.

## Característiques

- Múltiples modes d'operació (fractal, harmonic, bosc, etc.)
- Mode tracker per sequencies personalitzables
- Control analogic mitjançant potenciometre, ldr
- Control de navegació mitjançant botons
- Sortida MIDI per a controlar sintetitzadors externs
- 3 Sortides PWM modulables
- 1 Sortida gate
- 2 Entrades de CV amb rang configurable 
- Arquitectura modular per a fàcil expansió

## Requisits

- CircuitPython 7.0 o superior
- Mòduls necessaris:
  - adafruit_midi
  - Altres mòduls estàndard de CircuitPython

## Instal·lació

1. Copia el contingut d'aquest directori a la teva placa amb CircuitPython
2. Compila el fitxer .main.py amb el teu editor de codi i verifica que no hi ha errors
3. Desconecta el usb i connectau a la alimentació externa

## Ús

1. Connecta la placa al teu DAW, sintetitzador MIDI, sistema de pedals o sistema Eurorack
2. Selecciona el mode d'operació amb els botons
3. Ajusta els paràmetres amb els potenciòmetres
4. Disfruta!

## Llicència

Aquest projecte està sota la llicència MIT. Consulta (https://mit-license.org/) per a més informació.
