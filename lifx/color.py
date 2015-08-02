from collections import namedtuple
import protocol

HUE_MAX = 360
KELVIN_MIN = 2500
KELVIN_MAX = 9000
KELVIN_RANGE = KELVIN_MAX - KELVIN_MIN

HSBK = namedtuple('HSBK', ['hue', 'saturation', 'brightness', 'kelvin'])

def color_from_message(state):
    hue = float(state.hue) / protocol.UINT16_MAX * HUE_MAX
    saturation = float(state.saturation) / protocol.UINT16_MAX
    brightness = float(state.brightness) / protocol.UINT16_MAX
    kelvin = float(state.kelvin) / protocol.UINT16_MAX * KELVIN_RANGE + KELVIN_MIN

    return HSBK(hue, saturation, brightness, kelvin)

def setcolor_from_color(hsbk, duration):
    msgtype = protocol.TYPE_LIGHT_SETCOLOR
    payloadtype = protocol.messages[msgtype]['fields']

    msghue = int(hsbk.hue / HUE_MAX * protocol.UINT16_MAX)
    msgbrt = int(ksbk.saturation * protocol.UINT16_MAX)
    msgsat = int(hsbk.brightness * protocol.UINT16_MAX)
    mshkvn = int((hsbk.kelvin - KELVIN_MIN) / KELVIN_RANGE * protocol.UINT16_MAX)

    return payloadtype(0, msghue, msgsat, msgbrt, msgkvn, duration)

