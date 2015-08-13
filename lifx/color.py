from collections import namedtuple
import protocol

HUE_MAX = 360
KELVIN_MIN = 2500
KELVIN_MAX = 9000
KELVIN_RANGE = KELVIN_MAX - KELVIN_MIN

MID_KELVIN = KELVIN_MIN + (KELVIN_RANGE/2)

HSBK = namedtuple('HSBK', ['hue', 'saturation', 'brightness', 'kelvin'])

# Bright Colors
RED = HSBK(0, 1, 1, MID_KELVIN)
YELLOW = HSBK(60, 1, 1, MID_KELVIN)
GREEN = HSBK(120, 1, 1, MID_KELVIN)
AQUA = HSBK(180, 1, 1, MID_KELVIN)
BLUE = HSBK(240, 1, 1, MID_KELVIN)
PURPLE = HSBK(300, 1, 1, MID_KELVIN)
WHITE = HSBK(0, 0, 1, MID_KELVIN)

# Whites
COOL_WHITE = HSBK(0, 0, 1, KELVIN_MAX)
WARM_WHITE = HSBK(0, 0, 1, KELVIN_MIN)


def color_from_message(state):
    """
    Translates values from a packet into actual color values

    :param state: The state data from the light state message
    :returns: HSBK -- The actual color values
    """
    hue = float(state.hue) / protocol.UINT16_MAX * HUE_MAX
    saturation = float(state.saturation) / protocol.UINT16_MAX
    brightness = float(state.brightness) / protocol.UINT16_MAX
    kelvin = int(state.kelvin)

    return HSBK(hue, saturation, brightness, kelvin)

def message_from_color(hsbk):
    """
    Translates values from a color to values suitable for the packet.

    :param hsbk: The data from the actual color
    :returns: HSBK -- Color values for a light state message
    """
    msghue = int(float(hsbk.hue) / HUE_MAX * protocol.UINT16_MAX)
    msgsat = int(float(hsbk.saturation) * protocol.UINT16_MAX)
    msgbrt = int(float(hsbk.brightness) * protocol.UINT16_MAX)
    msgkvn = int(hsbk.kelvin) % (protocol.UINT16_MAX + 1)

    return HSBK(msghue, msgsat, msgbrt, msgkvn)

def modify_color(hsbk, **kwargs):
    """
    Helper function to make new colors from an existing color by modifying it.

    :param hsbk: The base color
    :param hue: The new Hue value (optional)
    :param saturation: The new Saturation value (optional)
    :param brightness: The new Brightness value (optional)
    :param kelvin: The new Kelvin value (optional)
    """
    return hsbk._replace(**kwargs)

