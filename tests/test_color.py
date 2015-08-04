import unittest

from lifx.color import HSBK, color_from_message, message_from_color, modify_color

COLOR_MESSAGE_TEST = [
        (HSBK(0, 0, 0, 0), HSBK(0, 0, 0, 0)),
        (HSBK(360, 1, 1, 9000), HSBK(pow(2, 16), pow(2, 16), pow(2, 16), 9000)),
        (HSBK(0, 0, 0.5, 3000), HSBK(0, 0, 32767, 3000)),
]

class ColorTests(unittest.TestCase):
    def test_color_from_message(self):
        for color, message in COLOR_MESSAGE_TEST:
            newcolor = color_from_message(message)
            for i in range(0, len(HSBK._fields)):
                self.assertAlmostEqual(color[i], newcolor[i], places=1)

    def test_message_from_color(self):
        for color, message in COLOR_MESSAGE_TEST:
            newmessage = message_from_color(color)
            for i in range(0, len(HSBK._fields)):
                self.assertAlmostEqual(message[i], newmessage[i], delta=1)

    def test_modify_color(self):
        beforecolor = HSBK(0, 0, 0, 0)
        aftercolor = HSBK(120, 0, 0, 0)
        changedcolor = modify_color(beforecolor, hue=120)
        self.assertEqual(changedcolor, aftercolor)

