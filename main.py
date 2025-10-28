# =============================================================================
# TECLA - SISTEMA MODULAR PROFESSIONAL
# Arquitectura optimitzada amb RTOS, CV calibrable i gate variable
# =============================================================================
print("🚀 TECLA Professional - Iniciant...")

import time
import random
from core.hardware import TeclaHardware
from core import config as cfg
from core.rtos import RTOSManager
from core.midi_handler import MidiHandler
from core import button_handler, calibration
from display.screens import ScreenManager
from display.animations import Animations
from music.converters import (
    voltage_to_bpm,
    bpm_to_sleep_time,
    map_value,
    midi_to_note_name,
    get_voltage_calibrated,
)
from modes.loader import ModeLoader

print("✅ Mòduls importats")

# =============================================================================
# INICIALITZACIÓ
# =============================================================================
try:
    hw = TeclaHardware()
    print("✅ Hardware inicialitzat")
    
    rtos = RTOSManager(hw, cfg)
    midi_handler = MidiHandler(hw, cfg)
    screen = ScreenManager(hw, cfg)
    anim = Animations(hw, cfg)
    mode_loader = ModeLoader(hw, cfg, midi_handler)
    print("✅ Gestors creats")
    
    # Temps inicials
    cfg.last_note_time = time.monotonic()
    cfg.next_note_time = cfg.last_note_time
    cfg.last_display_update = cfg.last_note_time
    cfg.last_button_check = cfg.last_note_time
    cfg.last_interaction_time = cfg.last_note_time
    cfg.last_input_sample = cfg.last_note_time
    
    # Animació inici - LEDs i missatge benvinguda
    hw.led_startup_animation()
    hw.display.fill(0)
    hw.display.text("Tecla x Kidmos", 15, 8, 1)
    hw.display.text("CHIPTUNE", 35, 20, 1)
    hw.display.text("Benvingut!", 28, 35, 1)
    hw.display.text("Sistema llest", 20, 50, 1)
    hw.display.show()
    time.sleep(1.5)
    
    print("✅ Sistema preparat - Arquitectura Modular Activa")
    print("")
    
except Exception as e:
    print(f"❌ Error inicialització: {e}")
    import traceback
    traceback.print_exception(e)
    while True:
        time.sleep(1)

# =============================================================================
# BUCLE PRINCIPAL - ARQUITECTURA RTOS AMB PRIORITATS
# =============================================================================
print("🔄 Bucle principal actiu")
iteration_count = 0

while True:
    try:
        current_time = time.monotonic()
        
        # ===== PRIORITAT MÀXIMA: RTOS (Gate temporal + NoteOff) =====
        rtos.update()
        
        # ===== PRIORITAT ALTA: Lectura inputs usuari =====
        x_raw = hw.get_voltage(hw.pote_analog_1)   # CV1 (GP28)
        y_raw = hw.get_voltage(hw.pote_analog_2)   # CV2 (GP27)
        z_raw = hw.get_voltage(hw.pote_velocidad)  # Slider (GP26)
        
        x = x_raw
        y = get_voltage_calibrated(y_raw, cfg.cv1_min, cfg.cv1_max)
        z = get_voltage_calibrated(z_raw, cfg.cv2_min, cfg.cv2_max)
        
        current_bpm = voltage_to_bpm(x)
        cfg.current_sleep_time = bpm_to_sleep_time(current_bpm)
        sleep_time = cfg.current_sleep_time
        cfg.bpm = current_bpm
        cfg.x, cfg.y, cfg.z = x, y, z
        
        cx = map_value(hw.potes[1].value, 0, 65535, -1.5, 1.5)
        cy = map_value(hw.potes[2].value, 0, 65535, -1.5, 1.5)
        cfg.cx, cfg.cy = cx, cy
        
        # Variables aleatòries per caos
        cfg.caos_note = random.randint(0, 1)
        
        # ===== PRIORITAT ALTA: Detecció botons (cada 5ms) =====
        if current_time - cfg.last_button_check > 0.005:
            cfg.last_button_check = current_time
            button_handler.process_buttons(hw, cfg, rtos, current_time)
        
        # ===== PRIORITAT ALTA: Execució modes musicals =====
        if cfg.loop_mode == 0:
            # Mode parada
            hw.pwm1.duty_cycle = 0
            hw.pwm2.duty_cycle = 0
            hw.pwm3.duty_cycle = 0
        elif current_time >= cfg.next_note_time and cfg.loop_mode > 0:
            # Actualitzar temps següent nota
            cfg.next_note_time = current_time + sleep_time
            
            # Executar mode actual amb valors calibrats
            mode_loader.execute_mode(cfg.loop_mode, x, y, z, sleep_time, cx, cy)
            
            # Incrementar iteration
            if cfg.loop_mode not in [6, 8]:  # Alguns modes gestionen la seva pròpia iteració
                cfg.iteration = (cfg.iteration + 1) % 60000
        
        # ===== PRIORITAT BAIXA: Actualització display =====
        if cfg.calibration_mode:
            screen.mostrar_calibracion_cv()
            calibration.procesar_calibracion(hw, cfg)
            time.sleep(0.05)  # 20 FPS en calibració
            
        elif current_time - cfg.last_display_update > 0.1:
            inactive_time = current_time - cfg.last_interaction_time
            
            if cfg.sequencer_mode_active:
                if inactive_time > 20.0:
                    try:
                        anim.animacion_gameboy_tracker()
                    except Exception:
                        anim.animacion_ojo()
                else:
                    screen.mostrar_sequencer_tracker()
            elif cfg.show_full_summary:
                screen._mostrar_resum_complet()
            elif cfg.caos == 1 and cfg.nota_tocada_ara:
                screen.mostrar_info_loop_mode()
                anim.dibujar_rayo_simple()
                hw.display.show()
                cfg.nota_tocada_ara = False
            elif cfg.loop_mode == 0:
                anim.animacion_ojo()
            elif cfg.loop_mode > 0 and inactive_time > 5.0:
                anim.mostrar_idle_con_simbolo(cfg.loop_mode)
            else:
                screen.mostrar_info_loop_mode()
            
            cfg.last_display_update = current_time
        
        # Sleep mínim CPU (0.5ms per màxima responsivitat)
        time.sleep(0.0005)
        
        # Debug cada 2000 iteracions (~4 segons)
        iteration_count += 1
        if iteration_count % 2000 == 0:
            try:
                note_name = midi_to_note_name(cfg.nota_actual)
            except Exception:
                note_name = "---"
            print(
                f"✅ {iteration_count} it | Mode:{cfg.loop_mode} Oct:{cfg.octava} "
                f"BPM:{int(current_bpm)} Gate:{cfg.gate_duration*1000:.1f}ms Nota:{note_name}"
            )
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupció manual - Netejant...")
        rtos.stop_all_notes()
        hw.all_leds_off()
        hw.display.fill(0)
        hw.display.text("STOPPED", 35, 28, 1)
        hw.display.show()
        break
        
    except Exception as e:
        print(f"❌ Error bucle: {e}")
        import traceback
        traceback.print_exception(e)
        
        # Mostrar error en pantalla
        hw.display.fill(0)
        hw.display.text("ERROR!", 40, 15, 1)
        error_str = str(e)[:20]
        hw.display.text(error_str, 0, 30, 1)
        hw.display.text("Check console", 10, 45, 1)
        hw.display.show()
        
        # Neteja i espera
        rtos.stop_all_notes()
        time.sleep(5)

print("🛑 TECLA Professional finalitzat")
