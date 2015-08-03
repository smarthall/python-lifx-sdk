import unittest

import lifx.protocol

MAC_TEST_CASES = [
        (4930653221840,   'd073d5017c04'), # Actual Device
        (0,               '000000000000'), # Minimum
        (pow(2, 6*8) - 1, 'ffffffffffff'), # Maximum
]

class ProtocolTests(unittest.TestCase):
    def test_mac_string(self):
        for val, mac in MAC_TEST_CASES:
            self.assertEqual(lifx.protocol.mac_string(val), mac)

