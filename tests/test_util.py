import unittest
import time

from lifx.util import RepeatTimer

class UtilTests(unittest.TestCase):
    def test_timer(self):
        def trigger():
            trigger.counter += 1

        trigger.counter = 0

        timer = RepeatTimer(1, trigger)
        timer.start()

        time.sleep(4)
        timer.cancel()

        self.assertGreaterEqual(trigger.counter, 3)

