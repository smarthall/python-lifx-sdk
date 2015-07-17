import socket
import signal
import sys
import code
import lifx.protocol
import lifx.network

# Start listening for packets
net = lifx.network.NetworkTransport()

# Install a packet handler
def packet_handler(host, port, packet):
    print '---'
    print 'Packet from: %s:%s' % (host, port)
    print 'Parsed: ' + str(packet)

net.register_packet_handler(packet_handler)

# Install a signal handler
def signal_handler(signal, frame):
    print 'CTRL-C received. Exiting.'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Send a discovery packet (expecting replies)
net.send_discovery(1, 0)

# Wait for CTRL-C
signal.pause()

