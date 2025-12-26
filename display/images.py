# =============================================================================
# IMAGES - Imatges estàtiques de pantalla completa per modes TECLA
# =============================================================================
# Imatges 128×64 píxels generades amb GurgleApps image-to-code
# Format: Base64 string convertit a bytearray

import binascii

# Mode 1: Fractal (exemple)
IMAGE_FRACTAL_B64 = "Lv////////////////+/////////////////v////////////////7////////////////+/////////////////v////////////////7////////////////+/////////////////v////////////////7////////////////+///8Af///////////v/+AAAB//////////7/8AAAAB/////////+/4AD8AAD/////////v8AP//+AH////////7/8Af///AP///////+//8A///+Af///////v//4D///8B///////7///gf///wH//////+///+AU///A///////v///4Hj//8D//////7////g+f/fwf/////+////8H5/h/B//////v////gff7H4P/////7////8D/+8/g/////+/////wPv3v8H/////v////+B5+Z/w/////7/////4Pfw/+H////+//////Bz///w/////v/////4O///+D////7//////B3///wf///+//////4d///8D////v//////DP///Af///7//////4b///yD///+///////Cf//8wf///v//////4H///OD///7///////B///zwf//+///////4f//8/D///v///////H///nw///7///////4///5+H//+///////+P///fw///v///////x///z+H//7///////+P//+fw//+////////z///z8P//v///////8f//8/h//7////////j///n8P/+f///////4///8/D//n////////H//9n4f/4////////5///s/D/+H///////+P//9nw//h////////j///McH/4P///////8////gB/+B////////H///+MP/gf///////w/////j/4D///////+P////4f+A////////j///87H/gH///////8f///xw/6A////////H////+P+YH///////x/////j/hwf//////+f////8f4OD///////n/////H+A4///////5/////w/gGP//////+f/g//+P4Aj///////H/h///h+AI///////x/x///8fkCP//////4/4////D5gD//////+P8f///w+QB///////j+P///8PkA///////w/n////h4A///////8Pz////4eg////////D8/////Hof///////w+P////x6P///////+PnwB//8eD////////h5wIH//Dg////////8fQGA//44f////////D4DgH/+OH////////4+A8Af/jh////////+PAfAD/44f////////jwHwAf4OH////////48A4AP9xj////////+PAOAH+cY/////////D4BAD/vGP////////x/gAD/7xj////////4f+AH/+8J////////8P5////vCf////////H+P///7xn////////h/h///+8J////////w/4P///vC////////8f/I///7wv///////+P/zB//+8L////////H/+eH//vC////////x//z///5xv///////4//8f///cb///////8f//j///zG////////H//+P//+Rv///////j///4f//8b///////4/+P/////G///////+f/A/////xv///////H/yP////4b///////x//x//g/+G///////8f/+f/gH/jv///////H//n//4/47///////j+Bz///P+O///////4/AM///5/jv//////+PgAf//+f47///////gAef///n+e///////8AD//+P5/nv///////h4///A+fx7////////+P//+Hn8e/////////j///55/Pv////////x////efz7////////8f//5zn4+////////+H//+c7+Pv////////D///Hf/j7////////h///Dn/4+////////4///B5/8fv///////+P//A+f/H7////////x/+Afv/x+////////8AAAP7/4fv////////wAAH//+P7/////////ACB///j+/////////j7B///x/v////////wAA///8f7////////8AAf//+P+/////////gAf///j/v///////4AAf///w/7///////4AAf///8f+///////8Ph////+H/v///////H//////j/7///////j//////w/+///////4//////8f/v///////P/////+H/7///////x//////D/+///////8f/////w//v///////H/////4f/7///////x/////+P/+///////4f/////D//v//////8P/////h//7///////H/////4//+///////h/////8f//v//////w/////+H//7//////4f///8fj//+//////8P///8/x///v/////+H+P/8+A///7//////D+T/88cP//+//////h/N/+8eH///v/////w/0//MfD///7/////4f/f/sfh///+/////8P///2Pw////v////8H///5P4f///4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

def get_image_data(b64_string):
    """Converteix Base64 a bytearray per framebuffer"""
    # Afegir padding si cal (Base64 necessita múltiple de 4)
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += '=' * (4 - missing_padding)
    
    return bytearray(binascii.a2b_base64(b64_string))

# Diccionari d'imatges disponibles
IMAGES = {
    1: get_image_data(IMAGE_FRACTAL_B64),  # Fractal
    # Afegeix més modes aquí quan tinguis les imatges
}
