import unittest
from binascii import hexlify, unhexlify

import lifx.protocol

MAC_TEST_CASES = [
        (4930653221840,   'd073d5017c04'), # Actual Device
        (0,               '000000000000'), # Minimum
        (pow(2, 6*8) - 1, 'ffffffffffff'), # Maximum
]

VERSION_TEST_CASES = [
        (0x00020001, '2.1'),
]

BYTES_TO_LABEL_CASES = [
        (bytearray(b'Right \xe2\x86\x97\xef\xb8\x8f\x00'), u'Right \u2197\ufe0f'),
        (bytearray(b'\x00'), u''),
        (bytearray(b'Just Text\x00'), u'Just Text'),
        (bytearray(b'\x00AFTER_NULL'), u''),
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

EXAMPLE_PACKETS = [
        ({
            'source': 45,
            'target': 4930653221840,
            'ack_required': False,
            'res_required': True,
            'sequence': 97,
            'pkt_type': lifx.protocol.TYPE_GETPOWER,
        },
        (),
        '240000142d000000d073d5017c0400000000000000000161000000000000000014000000',
        {
            'tagged': False,
        },
        ),
]

class ProtocolTests(unittest.TestCase):
    def test_mac_string(self):
        for val, mac in MAC_TEST_CASES:
            self.assertEqual(lifx.protocol.mac_string(val), mac)

    def test_version_string(self):
        for vnum, vstr in VERSION_TEST_CASES:
            self.assertEqual(lifx.protocol.version_string(vnum), vstr)

    def test_bytes_to_label(self):
        for val, string in BYTES_TO_LABEL_CASES:
            self.assertEqual(lifx.protocol.bytes_to_label(val), string)

    def test_pack_section(self):
        for pack_type, args, packet in PACK_TEST_CASES:
            self.assertEqual(hexlify(lifx.protocol.pack_section(pack_type, *args)), packet)

    def test_unpack_section(self):
        for pack_type, args, packet in PACK_TEST_CASES:
            self.assertEqual(lifx.protocol.unpack_section(pack_type, unhexlify(packet)), args)

    def test_section_size(self):
        for section, size in SIZE_TEST_CASES:
            self.assertEqual(lifx.protocol.section_size(section), size)

    def test_make_packet(self):
        for kwargs, args, packet, vals in EXAMPLE_PACKETS:
            self.assertEqual(hexlify(lifx.protocol.make_packet(*args, **kwargs)), packet)

    def test_parse_packet(self):
        for kwargs, args, packet, vals in EXAMPLE_PACKETS:
            parsed = lifx.protocol.parse_packet(unhexlify(packet))

            size = len(unhexlify(packet))

            # Check data we sent
            self.assertEqual(parsed.frame_header.size, size)
            self.assertEqual(parsed.frame_header.protocol, 1024)
            self.assertEqual(parsed.frame_header.source, kwargs['source'])
            self.assertEqual(parsed.frame_address.target, kwargs['target'])
            self.assertEqual(parsed.frame_address.ack_required, kwargs['ack_required'])
            self.assertEqual(parsed.frame_address.res_required, kwargs['res_required'])
            self.assertEqual(parsed.frame_address.sequence, kwargs['sequence'])
            self.assertEqual(parsed.protocol_header.pkt_type, kwargs['pkt_type'])

            # Check other data
            self.assertEqual(parsed.frame_header.tagged, vals['tagged'])

    def test_parse_packet_with_incorrect_size(self):
        packet = '240000142d000000d073d5017c0400000000000000000161000000000000000014'
        self.assertIsNone(lifx.protocol.parse_packet(unhexlify(packet)))

    def test_parse_packet_with_unknown_type(self):
        packet = '2600005442524b52d073d501cf2c00004c49465856320000842e3128d92cf7136f000000890c'
        parsed = lifx.protocol.parse_packet(unhexlify(packet))
        self.assertEqual(parsed.protocol_header.pkt_type, 111)
        self.assertEqual(parsed.payload, '\x89\x0c')

    def test_discovery_packet(self):
        self.assertEqual(
                hexlify(lifx.protocol.discovery_packet(23, 5)),
                '240000341700000000000000000000000000000000000105000000000000000002000000',
        )

