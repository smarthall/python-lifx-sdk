from collections import namedtuple
import protocol

HUE_MAX = 360
KELVIN_MIN = 2500
KELVIN_MAX = 9000
KELVIN_RANGE = KELVIN_MAX - KELVIN_MIN

MID_KELVIN = 5750

HSBK = namedtuple('HSBK', ['hue', 'saturation', 'brightness', 'kelvin'])

# Bright Colors
RED = HSBK(0, 1, 1, MID_KELVIN)
YELLOW = HSBK(60, 1, 1, MID_KELVIN)
GREEN = HSBK(120, 1, 1, MID_KELVIN)
AQUA = HSBK(180, 1, 1, MID_KELVIN)
BLUE = HSBK(240, 1, 1, MID_KELVIN)
PURPLE = HSBK(300, 1, 1, MID_KELVIN)
WHITE = HSBK(0, 0, 1, MID_KELVIN)


def color_from_message(state):
    hue = float(state.hue) / protocol.UINT16_MAX * HUE_MAX
    saturation = float(state.saturation) / protocol.UINT16_MAX
    brightness = float(state.brightness) / protocol.UINT16_MAX
    kelvin = float(state.kelvin) / protocol.UINT16_MAX * KELVIN_RANGE + KELVIN_MIN

    return HSBK(hue, saturation, brightness, kelvin)

def message_from_color(hsbk):
    msghue = int(float(hsbk.hue) / HUE_MAX * protocol.UINT16_MAX)
    msgsat = int(float(hsbk.saturation) * protocol.UINT16_MAX)
    msgbrt = int(float(hsbk.brightness) * protocol.UINT16_MAX)
    msgkvn = int((float(hsbk.kelvin) - KELVIN_MIN) / KELVIN_RANGE * protocol.UINT16_MAX)

    return HSBK(msghue, msgsat, msgbrt, msgkvn)

