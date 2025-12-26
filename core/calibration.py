# =============================================================================
# CALIBRACIÓ CV - TECLA
# =============================================================================
import time

# Debounce per botons de calibració - Temps humà natural
_calibration_debounce = [0.0, 0.0, 0.0, 0.0]
CALIBRATION_DEBOUNCE_TIME = 0.4  # 400ms entre pulsacions (temps per ajustar potenciòmetre)

def procesar_calibracion(hw, cfg):
    """Processa calibració dels rangs CV"""
    current_time = time.monotonic()
    
    # Botó 1: Establir CV1 mínim
    if hw.boton_crueta_1.value and current_time - _calibration_debounce[0] > CALIBRATION_DEBOUNCE_TIME:
        cfg.cv1_min = hw.get_voltage(hw.cv1_pote)  # GP26
        _calibration_debounce[0] = current_time
    
    # Botó 2: Establir CV1 màxim
    if hw.boton_crueta_2.value and current_time - _calibration_debounce[1] > CALIBRATION_DEBOUNCE_TIME:
        cfg.cv1_max = hw.get_voltage(hw.cv1_pote)  # GP26
        _calibration_debounce[1] = current_time
    
    # Botó 3: Establir CV2 mínim
    if hw.boton_crueta_3.value and current_time - _calibration_debounce[2] > CALIBRATION_DEBOUNCE_TIME:
        cfg.cv2_min = hw.get_voltage(hw.cv2_ldr)  # GP27
        _calibration_debounce[2] = current_time
    
    # Botó 4: Establir CV2 màxim
    if hw.boton_crueta_4.value and current_time - _calibration_debounce[3] > CALIBRATION_DEBOUNCE_TIME:
        cfg.cv2_max = hw.get_voltage(hw.cv2_ldr)  # GP27
        _calibration_debounce[3] = current_time
