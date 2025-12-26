# 🎮 TECLA - GUIA RÀPIDA

> **Manual d'instruccions condensat per començar a fer música IMMEDIATAMENT**

---

## ⚡ START RÀPID (30 SEGONS)

1. **Encén** el TECLA → Veuràs animació d'inici
2. **Prem Botó 2 (►)** → Passa a MODE 1: FRACTAL
3. **Mou SLIDER** → Controla velocitat (BPM)
4. **Gira CV1 i CV2** → Explora sons
5. **Prem Botó 4 (▲)** → Puja octava (més agut)

**Ja estàs fent música!** 🎵

---

## 🕹️ CONTROLS BÀSICS

```
              [▲] Octava+
               │
          [◄]─[●]─[►]
 Mode ANTERIOR │  Mode SEGÜENT
              [▼] Octava-
```

**SLIDER:** Velocitat (20-220 BPM)  
**CV1/CV2:** Paràmetres del mode (canvien segons mode)

---

## 💡 LEDS

- **LED 2 (central):** S'encén quan sona o canvia una nota 🔴
- **Altres LEDs:** Config activa (Duty, Harmònics)

---

## 🎵 ELS 14 MODES (RESUM)

| Mode | Nom | Què Fa? |
|------|-----|---------|
| 0 | **PAUSA**         | Silenci + efectes visuals |
| 1 | **FRACTAL**       | Mandelbrot → Melodies matemàtiques |
| 2 | **RIU**           | Notes fluides com aigua |
| 3 | **TEMPESTA**      | Pluja + llamps aleatoris |
| 4 | **HARMONIA**      | Progressions d'acords |
| 5 | **BOSC**          | Sons orgànics i aleat​oris |
| 6 | **ESCALA CV**     | 7 escales modals (sempre sona bé!) |
| 7 | **EUCLIDIA**      | Ritmes matemàtics perfectes |
| 8 | **COSMOS**        | Combinació complexa de tot |
| 9 | **CAMPANETES**    | Campanes musicals Do-Mi-Sol |
| 10 | **SEGONES**      | Dues notes amb interval variable |
| 11 | **ESPIRAL**      | Escala que puja gradualment |
| 12 | **CONTRAPUNT**   | 3 veus independents |
| 13 | **NARVAL**       | 3 narvals que es comuniquen |
| 14 | **CICLADOR**     | Nota fixa per explorar valors de duty diferents |

---

## 🎛️ FUNCIONS AVANÇADES

### 🔥 MODE CAOS

Activa improvisació salvatge:

3. Les notes es tornen aleatòries i impredictibles
4. **Repeteix per desactivar**

### ⚙️ CONFIGURAR PARÀMETRES

1. **Prem EXTRA 1** → Cicla paràmetres
   - Mode → Duty1 → Duty2 → Duty3 → Harmònic 1 → Harmònic 2 → Harmònic 3
2. **Prem EXTRA 2** → inverteix 
3. Els LEDs indiquen què estàs editant

### 🎚️ HARMÒNICS (So Multi-Canal)

Configura intervals musicals per als 3 canals PWM:

**Recomanacions:**

- **Power Chord:** H1=0, H2=7
- **Acord Major:** H1=4, H2=7
- **Acord Menor:** H1=3, H2=7
- **Octaves:** H1=12, H2=12

### 🎯 CALIBRACIÓ CV

Si CV1/CV2 no responen bé:

1. **Mantén EXTRA 1 + EXTRA2**  → Mode Calibració
2. **CVC mínim** → Prem Botó 1 (◄)
3. **CV2 màxim** → Prem Botó 4 (►)
4. **CV1 mínim** → Prem Botó 3 (▼)
5. **CV1 màxim** → Prem Botó 2 (▲)
6. **Prem EXTRA 1 + EXTRA2** per sortir

---

## 🔊 SORTIDES

- **PWM1 (GP22):** Canal principal
- **PWM2 (GP2):** Canal harmònic 1
- **PWM3 (GP0):** Canal harmònic 2
- **GATE (GP1):** Senyal de gate 3V3

**💡 TIP:** Connecta PWM1+PWM2+PWM3 a un mixer per so complet!

---

## 📊 VALORS PER DEFECTE

- **Mode:** 0 (Pausa)
- **Octava:** 5 (central)
- **Duty:** 50% (ona quadrada perfecta)
- **Harmònics:** 0 (unísono)

---

**🎵 Gaudeix creant música amb TECLA! ✨**
