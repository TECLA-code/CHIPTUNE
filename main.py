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
from core.clock import MasterClock
from display.screens import ScreenManager
from display.animations import Animations
from music.converters import (
    voltage_to_bpm,
    map_value,
    midi_to_note_name,
    get_voltage_calibrated,
    smooth_value,
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
    clock = MasterClock(cfg)
    print("✅ Gestors creats")
    
    # Temps inicials
    cfg.last_note_time = time.monotonic()
    cfg.next_note_time = cfg.last_note_time
    cfg.last_display_update = cfg.last_note_time
    cfg.last_button_check = cfg.last_note_time
    cfg.last_interaction_time = cfg.last_note_time
    cfg.last_input_sample = cfg.last_note_time
    cfg.next_calibration_frame = cfg.last_note_time
    
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
        
        x = get_voltage_calibrated(x_raw, cfg.cv1_min, cfg.cv1_max)
        y = get_voltage_calibrated(y_raw, cfg.cv2_min, cfg.cv2_max)
        z = get_voltage_calibrated(z_raw, cfg.cv2_min, cfg.cv2_max)
        
        cfg.bpm_voltage_raw = x
        thr_filter = smooth_value(cfg.bpm_voltage_filtered, x, cfg.bpm_voltage_smoothing)
        cfg.bpm_voltage_filtered = thr_filter
        raw_bpm = voltage_to_bpm(
            thr_filter,
            pot_min=cfg.cv1_min,
            pot_max=cfg.cv1_max,
            bpm_min=cfg.bpm_min,
            bpm_max=cfg.bpm_max,
            curve=cfg.bpm_curve,
        )
        sleep_time = clock.update(raw_bpm, current_time)
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
        
        error_block_active = current_time < cfg.error_pause_until

        # ===== PRIORITAT ALTA: Execució modes musicals =====
        if cfg.loop_mode == 0 or error_block_active:
            # Mode parada o pausa per error
            if cfg.playing_notes:
                midi_handler.all_notes_off()
            hw.pwm1.duty_cycle = 0
            hw.pwm2.duty_cycle = 0
            hw.pwm3.duty_cycle = 0
        elif cfg.loop_mode > 0:
            ticks = clock.consume_ticks(current_time)
            for tick_time in ticks:
                cfg.next_note_time = tick_time + sleep_time
                mode_loader.execute_mode(cfg.loop_mode, x, y, z, sleep_time, cx, cy)
                if cfg.loop_mode not in [6, 8]:
                    cfg.iteration = (cfg.iteration + 1) % 60000
        
        # Feedback LED dinàmic per harmonies i duty sense enlluernar
        hw.update_dynamic_leds(cfg, current_time)
        
        # ===== PRIORITAT BAIXA: Actualització display =====
        if cfg.calibration_mode:
            calibration.procesar_calibracion(hw, cfg)
            if current_time >= cfg.next_calibration_frame:
                cfg.next_calibration_frame = current_time + cfg.calibration_frame_interval
                screen.mostrar_calibracion_cv()
            
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
        clock.idle_sleep(current_time)
        
        # Debug cada 2000 iteracions (~4 segons)
        iteration_count += 1
        if iteration_count % 2000 == 0:
            try:
                note_name = midi_to_note_name(cfg.nota_actual)
            except Exception:
                note_name = "---"
            print(
                f"✅ {iteration_count} it | Mode:{cfg.loop_mode} Oct:{cfg.octava} "
                f"BPM:{cfg.bpm} Gate:{cfg.gate_duration*1000:.1f}ms Nota:{note_name}"
            )
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupció manual - Netejant...")
        rtos.stop_all_notes()
        midi_handler.all_notes_off()
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
        midi_handler.all_notes_off()
        cfg.error_pause_until = max(cfg.error_pause_until, time.monotonic() + 5.0)

print("🛑 TECLA Professional finalitzat")
