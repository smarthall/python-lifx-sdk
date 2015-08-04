import unittest
import time

from lifx.util import RepeatTimer

class UtilTests(unittest.TestCase):
    def test_timer(self):
        def trigger():
            trigger.counter += 1

        trigger.counter = 0

        timer = RepeatTimer(0.005, trigger)
        timer.start()

        time.sleep(0.04)
        timer.cancel()

        self.assertGreaterEqual(trigger.counter, 6)

