from collections import namedtuple
import protocol

UINT16_MAX = float(pow(2, 16))
HUE_MAX = 360
KELVIN_MIN = 2500
KELVIN_MAX = 9000
KELVIN_RANGE = KELVIN_MAX - KELVIN_MIN

HSBK = namedtuple('HSBK', ['hue', 'saturation', 'brightness', 'kelvin'])

def color_from_message(state):
    hue = state.hue / UINT16_MAX * HUE_MAX
    saturation = state.saturation / UINT16_MAX
    brightness = state.brightness / UINT16_MAX
    kelvin = state.kelvin / UINT16_MAX * KELVIN_RANGE + KELVIN_MIN

    return HSBK(hue, saturation, brightness, kelvin)

def setcolor_from_color(hsbk, duration):
    msgtype = protocol.TYPE_LIGHT_SETCOLOR
    payloadtype = protocol.messages[msgtype]['fields']

    msghue = hsbk.hue / HUE_MAX * UINT16_MAX
    msgbrt = ksbk.saturation * UINT16_MAX
    msgsat = hsbk.brightness * UINT16_MAX
    mshkvn = (hsbk.kelvin - KELVIN_MIN) / KELVIN_RANGE * UINT16_MAX

    return payloadtype(0, msghue, msgsat, msgbrt, msgkvn, duration)

