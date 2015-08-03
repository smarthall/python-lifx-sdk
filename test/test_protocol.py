import unittest
from binascii import hexlify, unhexlify

import lifx.protocol

MAC_TEST_CASES = [
        (4930653221840,   'd073d5017c04'), # Actual Device
        (0,               '000000000000'), # Minimum
        (pow(2, 6*8) - 1, 'ffffffffffff'), # Maximum
]

PACK_TEST_CASES = [
        (lifx.protocol.frame_header,     (0, 0, 0, 0, 0, 0,),          '0000000000000000'),
        (lifx.protocol.frame_header,     (49, 0, 1, 1, 1024, 4752,),   '3100003490120000'),
        (lifx.protocol.protocol_header,  (0, 0, 0),                    '000000000000000000000000'),
        (lifx.protocol.protocol_header,  (0, 117, 0),                  '000000000000000075000000'),
]

SIZE_TEST_CASES = [
        (lifx.protocol.frame_header, 64),
        (lifx.protocol.frame_address, 128),
        (lifx.protocol.protocol_header, 96),
        (lifx.protocol.messages[lifx.protocol.TYPE_GETSERVICE], 0),
        (lifx.protocol.messages[lifx.protocol.TYPE_STATESERVICE], 40),
]

class ProtocolTests(unittest.TestCase):
    def test_mac_string(self):
        for val, mac in MAC_TEST_CASES:
            self.assertEqual(lifx.protocol.mac_string(val), mac)

    def test_pack_section(self):
        for pack_type, args, packet in PACK_TEST_CASES:
            self.assertEqual(hexlify(lifx.protocol.pack_section(pack_type, *args)), packet)

    def test_unpack_section(self):
        for pack_type, args, packet in PACK_TEST_CASES:
            self.assertEqual(lifx.protocol.unpack_section(pack_type, unhexlify(packet)), args)

    def test_section_size(self):
        for section, size in SIZE_TEST_CASES:
            self.assertEqual(lifx.protocol.section_size(section), size)

    def test_discovery_packet(self):
        self.assertEqual(
                hexlify(lifx.protocol.discovery_packet(23, 5)),
                '240000341700000000000000000000000000000000000105000000000000000002000000',
        )

