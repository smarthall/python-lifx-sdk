from bitstruct import unpack, pack, byteswap, calcsize
from binascii import hexlify
from collections import namedtuple

UINT16_MAX = pow(2, 16) - 1

# Packet tuple
lifx_packet = namedtuple('lifx_packet', ['frame_header', 'frame_address', 'protocol_header', 'payload'])

# Header Descriptions
frame_header = {
        'format': 'u16u2u1u1u12u32',
        'byteswap': '224',
        'fields': namedtuple('frame_header', [
            'size',
            'origin',
            'tagged',
            'addressable',
            'protocol',
            'source'
        ]),
}

frame_address = {
        'format': 'u64u48u6u1u1u8',
        'byteswap': '8611',
        'fields': namedtuple('frame_address', [
            'target',
            'reserved1',
            'reserved2',
            'ack_required',
            'res_required',
            'sequence'
        ]),
}

protocol_header = {
        'format': 'u64u16u16',
        'byteswap': '822',
        'fields': namedtuple('protocol_header', [
            'reserved1',
            'pkt_type',
            'reserved2'
        ]),
}

# Device Messages
TYPE_GETSERVICE = 2
TYPE_STATESERVICE = 3
TYPE_GETHOSTINFO = 12
TYPE_STATEHOSTINFO = 13
TYPE_GETHOSTFIRMWARE = 14
TYPE_STATEHOSTFIRMWARE = 15
TYPE_GETWIFIINFO = 16
TYPE_STATEWIFIINFO = 17
TYPE_GETWIFIFIRMWARE = 18
TYPE_STATEWIFIFIRMWARE = 19
TYPE_GETPOWER = 20
TYPE_SETPOWER = 21
TYPE_STATEPOWER = 22
TYPE_GETLABEL = 23
TYPE_SETLABEL = 24
TYPE_STATELABEL = 25
TYPE_GETVERSION = 32
TYPE_STATEVERSION = 33
TYPE_GETINFO = 34
TYPE_STATEINFO = 35
TYPE_ACKNOWLEDGEMENT = 45
TYPE_ECHOREQUEST = 58
TYPE_ECHORESPONSE = 59

# Light Messages
TYPE_LIGHT_GET = 101
TYPE_LIGHT_SETCOLOR = 102
TYPE_LIGHT_STATE = 107
TYPE_LIGHT_GETPOWER = 116
TYPE_LIGHT_SETPOWER = 117
TYPE_LIGHT_STATEPOWER = 118

# Message Classes
CLASS_TYPE_GET = (
    TYPE_GETSERVICE,
    TYPE_GETHOSTINFO,
    TYPE_GETHOSTFIRMWARE,
    TYPE_GETWIFIINFO,
    TYPE_GETWIFIFIRMWARE,
    TYPE_GETPOWER,
    TYPE_GETLABEL,
    TYPE_GETVERSION,
    TYPE_GETINFO,
    TYPE_LIGHT_GET,
    TYPE_LIGHT_GETPOWER,
)

CLASS_TYPE_SET = (
    TYPE_SETPOWER,
    TYPE_SETLABEL,
    TYPE_LIGHT_SETCOLOR,
    TYPE_LIGHT_SETPOWER,
)

CLASS_TYPE_STATE = (
    TYPE_STATESERVICE,
    TYPE_STATEHOSTINFO,
    TYPE_STATEHOSTFIRMWARE,
    TYPE_STATEWIFIINFO,
    TYPE_STATEWIFIFIRMWARE,
    TYPE_STATEPOWER,
    TYPE_STATELABEL,
    TYPE_STATEVERSION,
    TYPE_STATEINFO,
    TYPE_LIGHT_STATE,
    TYPE_LIGHT_STATEPOWER,
)

CLASS_TYPE_OTHER = (
    TYPE_ACKNOWLEDGEMENT,
    TYPE_ECHOREQUEST,
    TYPE_ECHORESPONSE,
)

# Service Types
SERVICE_UDP = 1
SERVICE_RESERVED1 = 2
SERVICE_RESERVED2 = 3
SERVICE_RESERVED3 = 4
SERVICE_RESERVED4 = 5

messages = {
    TYPE_GETSERVICE: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_getservice', [
        ]),
    },
    TYPE_STATESERVICE: {
        'format': 'u8u32',
        'byteswap': '14',
        'fields': namedtuple('payload_stateservice', [
            'service',
            'port',
        ]),
    },
    TYPE_GETHOSTINFO: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_gethostinfo', [
        ]),
    },
    TYPE_STATEHOSTINFO: {
        'format': 'u32u32u32u16',
        'byteswap': '4442',
        'fields': namedtuple('payload_statehostinfo', [
            'signal',
            'tx',
            'rx',
            'reserved',
        ]),
    },
    TYPE_GETHOSTFIRMWARE: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_gethostfirmware', [
        ]),
    },
    TYPE_STATEHOSTFIRMWARE: {
        'format': 'u64u64u32',
        'byteswap': '844',
        'fields': namedtuple('payload_statehostfirmware', [
            'build',
            'reserved',
            'version',
        ]),
    },
    TYPE_GETWIFIINFO: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_getwifiinfo', [
        ]),
    },
    TYPE_STATEWIFIINFO: {
        'format': 'u32u32u32u16',
        'byteswap': '4442',
        'fields': namedtuple('payload_statewifiinfo', [
            'signal',
            'tx',
            'rx',
            'reserved',
        ]),
    },
    TYPE_GETWIFIFIRMWARE: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_wififirmware', [
        ]),
    },
    TYPE_STATEWIFIFIRMWARE: {
        'format': 'u64u64u32',
        'byteswap': '884',
        'fields': namedtuple('payload_statewififirmware', [
            'build',
            'reserved',
            'version',
        ]),
    },
    TYPE_GETPOWER: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_getpower', [
        ]),
    },
    TYPE_SETPOWER: {
        'format': 'u16',
        'byteswap': '2',
        'fields': namedtuple('payload_setpower', [
            'level',
        ]),
    },
    TYPE_STATEPOWER: {
        'format': 'u16',
        'byteswap': '2',
        'fields': namedtuple('payload_statepower', [
            'level',
        ]),
    },
    TYPE_GETLABEL: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_getlabel', [
        ]),
    },
    TYPE_SETLABEL: {
        'format': 'b256',
        'byteswap': '1' * 32,
        'fields': namedtuple('payload_setlabel', [
            'label',
        ]),
    },
    TYPE_STATELABEL: {
        'format': 'b256',
        'byteswap': '1' * 32,
        'fields': namedtuple('payload_statelabel', [
            'label',
        ]),
    },
    TYPE_GETVERSION: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_getversion', [
        ]),
    },
    TYPE_STATEVERSION: {
        'format': 'u32u32u32',
        'byteswap': '444',
        'fields': namedtuple('payload_stateversion', [
            'vendor',
            'product',
            'version',
        ]),
    },
    TYPE_GETINFO: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_getinfo', [
        ]),
    },
    TYPE_STATEINFO: {
        'format': 'u64u64u64',
        'byteswap': '888',
        'fields': namedtuple('payload_stateinfo', [
            'time',
            'uptime',
            'downtime',
        ]),
    },
    TYPE_ACKNOWLEDGEMENT: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_acknowledgement', [
        ]),
    },
    TYPE_ECHOREQUEST: {
        'format': 'b64',
        'byteswap': '1' * 64,
        'fields': namedtuple('payload_echorequest', [
            'payload',
        ]),
    },
    TYPE_ECHORESPONSE: {
        'format': 'b64',
        'byteswap': '1' * 64,
        'fields': namedtuple('payload_echoresponse', [
            'payload',
        ]),
    },
    TYPE_LIGHT_GET: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_light_get', [
        ]),
    },
    TYPE_LIGHT_SETCOLOR: {
        'format': 'u8u16u16u16u16u32',
        'byteswap': '122224',
        'fields': namedtuple('payload_light_setcolor', [
            'reserved',
            'hue',
            'saturation',
            'brightness',
            'kelvin',
            'duration',
        ]),
    },
    TYPE_LIGHT_STATE: {
        'format': 'u16u16u16u16s16u16b256u64',
        'byteswap': '222222' + '1' * 32 + '8',
        'fields': namedtuple('payload_light_state', [
            'hue',
            'saturation',
            'brightness',
            'kelvin',
            'reserved1',
            'power',
            'label',
            'reserved2',
        ]),
    },
    TYPE_LIGHT_GETPOWER: {
        'format': '',
        'byteswap': '',
        'fields': namedtuple('payload_light_getpower', [
        ]),
    },
    TYPE_LIGHT_SETPOWER: {
        'format': 'u16u32',
        'byteswap': '24',
        'fields': namedtuple('payload_light_setpower', [
            'level',
            'duration',
        ]),
    },
    TYPE_LIGHT_STATEPOWER: {
        'format': 'u16',
        'byteswap': '2',
        'fields': namedtuple('payload_light_statepower', [
            'level',
        ]),
    },
}

def mac_string(device_id):
    return hexlify(byteswap('6', pack('u48', device_id)))

def pack_section(section, *args):
    """Packs bytes into a header including the swap to little-endian"""
    return byteswap(section['byteswap'], pack(section['format'], *args))

def unpack_section(section, data):
    """Unpacks bytes into data, including the endian swap"""

    # Bitstruct only takes byte arrays, some things give us strings
    if type(data) != bytearray:
        data = bytearray(data)

    unpacked = unpack(section['format'], byteswap(section['byteswap'], data))
    return section['fields'](*unpacked)

def section_size(section):
    """Returns the size of a section"""
    return calcsize(section['format'])

def make_packet(*args, **kwargs):
    """Builds a packet from data supplied, required arguments depends on the packet type"""

    source = kwargs['source']
    target = kwargs['target']
    ack_required = kwargs['ack_required']
    res_required = kwargs['res_required']
    sequence = kwargs['sequence']
    pkt_type = kwargs['pkt_type']

    # Frame header
    packet_size = ( section_size(frame_header)
           + section_size(frame_address)
           + section_size(protocol_header)
           + section_size(messages[pkt_type]) ) / 8

    origin = 0 # Origin is always zero
    tagged = 1 if target is not None else 0
    addressable = 1 # Addressable is always one
    protocol = 1024 # Only protocol 1024 so far

    frame_header_data = pack_section(
            frame_header,
            packet_size,
            origin,
            tagged,
            addressable,
            protocol,
            source,
    )

    # Frame Address
    target = 0 if target is not None else target
    res_required = 1 if res_required else 0
    ack_required = 1 if ack_required else 0

    frame_address_data = pack_section(
            frame_address,
            target,
            0, # Reserved
            0, # Reserved
            ack_required,
            res_required,
            sequence,
    )

    # Protocol Header
    protocol_header_data = pack_section(
            protocol_header,
            0, # Reserved
            pkt_type,
            0, # Reserved
    )

    # Payload
    payload_data = pack_section(
            messages[pkt_type],
            *args
    )

    packet = frame_header_data + frame_address_data + protocol_header_data + payload_data

    return packet


def parse_packet(data):
    """Takes packet data as composes it into several namedtuple objects"""
    # Frame Header
    frame_header_size = section_size(frame_header) / 8
    frame_header_data = data[0:frame_header_size]

    frame_header_struct = unpack_section(
            frame_header,
            frame_header_data
    )

    if frame_header_struct.size != len(data):
        return None

    # Frame Address
    frame_address_size = section_size(frame_address) / 8
    frame_address_start = frame_header_size
    frame_address_end = frame_header_size + frame_address_size
    frame_address_data = data[frame_address_start:frame_address_end]
    frame_address_struct = unpack_section(
            frame_address,
            frame_address_data
    )

    # Protocol Header
    protocol_header_size = section_size(protocol_header) / 8
    protocol_header_start = frame_address_end
    protocol_header_end = protocol_header_start + protocol_header_size
    protocol_header_data = data[protocol_header_start:protocol_header_end]
    protocol_header_struct = unpack_section(
            protocol_header,
            protocol_header_data
    )

    # Payload
    payload_start = protocol_header_end
    if protocol_header_struct.pkt_type in messages.keys():
        payload = messages[protocol_header_struct.pkt_type]
        payload_size = section_size(payload) / 8
        payload_end = payload_start + payload_size
        payload_data = data[payload_start:payload_end]
        payload_struct = unpack_section(
                payload,
                payload_data
        )
    else:
        payload_size = frame_header_struct.size - payload_start
        payload_end = payload_start + payload_size
        payload_struct = data[payload_start:payload_end]


    return lifx_packet(
            frame_header_struct,
            frame_address_struct,
            protocol_header_struct,
            payload_struct
    )

def discovery_packet(source, sequence):
    return make_packet(
            source=source,
            target=0,
            ack_required=False,
            res_required=True,
            sequence=sequence,
            pkt_type=TYPE_GETSERVICE,
    )

