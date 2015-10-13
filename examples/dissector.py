#!/usr/bin/env python
import signal
import sys

from binascii import unhexlify
import lifx.protocol

# Install a signal handler
def signal_handler(signal, frame):
    print 'CTRL-C received. Exiting.'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print '\n'
print '---### LIFX Protocol Dissector ###---'
print 'Get packets from Wireshark and dissect them here.'
print 'Choose the "Data" section, right click it, then'
print 'choose Copy -> Bytes -> Hex Stream, then paste the'
print 'result here.\n'
print 'CTRL-C or CTRL-D to exit.'
print '\n'

while True:
    try:
        line = raw_input('Packet: ')
    except EOFError:
        print 'EOF received. Exiting.'
        break
    print repr(lifx.protocol.parse_packet(unhexlify(line))) + '\n'

