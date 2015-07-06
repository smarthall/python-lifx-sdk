from bitstruct import unpack, pack, byteswap, calcsize

# Header Descriptions
frame_header_format = 'u16u2u1u1u12u32'
frame_header_byteswap = '224'

frame_address_format = 'u64u48u6u1u1u8'
frame_address_byteswap = '8611'

protocol_header_format = 'u64u16u16'
protocol_header_byteswap = '822'

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

messages = {
    TYPE_GETSERVICE: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATESERVICE: {
        'format': 'u8u32',
        'byteswap': '14',
    },
    TYPE_GETHOSTINFO: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATEHOSTINFO: {
        'format': 'u32u32u32u16',
        'byteswap': '4442',
    },
    TYPE_GETHOSTFIRMWARE: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATEHOSTFIRMWARE: {
        'format': 'u64u64u32',
        'byteswap': '844',
    },
    TYPE_GETWIFIINFO: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATEWIFIINFO: {
        'format': 'u32u32u32u16',
        'byteswap': '4442',
    },
    TYPE_GETWIFIFIRMWARE: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATEWIFIFIRMWARE: {
        'format': 'u64u64u32',
        'byteswap': '884',
    },
    TYPE_GETPOWER: {
        'format': '',
        'byteswap': '',
    },
    TYPE_SETPOWER: {
        'format': 'u16',
        'byteswap': '2',
    },
    TYPE_STATEPOWER: {
        'format': 'u16',
        'byteswap': '2',
    },
    TYPE_GETLABEL: {
        'format': '',
        'byteswap': '',
    },
    TYPE_SETLABEL: {
        'format': 'b256',
        'byteswap': '1' * 32,
    },
    TYPE_STATELABEL: {
        'format': 'b256',
        'byteswap': '1' * 32,
    },
    TYPE_GETVERSION: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATEVERSION: {
        'format': 'u32u32u32',
        'byteswap': '444',
    },
    TYPE_GETINFO: {
        'format': '',
        'byteswap': '',
    },
    TYPE_STATEINFO: {
        'format': 'u64u64u64',
        'byteswap': '888',
    },
    TYPE_ACKNOWLEGEMENT: {
        'format': '',
        'byteswap': '',
    },
    TYPE_ECHOREQUEST: {
        'format': 'b64',
        'byteswap': '1' * 64,
    },
    TYPE_ECHORESPONSE: {
        'format': 'b64',
        'byteswap': '1' * 64,
    },
    TYPE_LIGHT_GET: {
        'format': '',
        'byteswap': '',
    },
    TYPE_LIGHT_SETCOLOR: {
        'format': 'u8u16u16u16u16u32',
        'byteswap': '122224',
    },
    TYPE_LIGHT_STATE: {
        'format': 'u16u16u16u16s16u16b256u64',
        'byteswap': '222222' + '1' * 32 + '8',
    },
    TYPE_LIGHT_GETPOWER: {
        'format': '',
        'byteswap': '',
    },
    TYPE_LIGHT_SETPOWER: {
        'format': 'u16u32',
        'byteswap': '24',
    },
    TYPE_LIGHT_STATEPOWER: {
        'format': 'u16',
        'byteswap': '2',
    },
}

def pack_section(fmt, bs, *args):
    """Packs bytes into a header including the swap to little-endian"""
    return byteswap(bs, pack(fmt, *args))

def unpack_section(fmt, bs, data):
    """Unpacks bytes into data, including the endian swap"""
    return unpack(fmt, byteswap(bs, data))

