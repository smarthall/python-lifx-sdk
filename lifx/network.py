import protocol
import socket
import threading
from binascii import hexlify

class NetworkTransport(object):
    def __init__(self, address='0.0.0.0'):
        # Prepare a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((address, 0))

        self._socket = sock

        self._listener = ListenerThread(sock)
        self._listener.start()

    def sendto(self, packet, address):
        return self._socket.sendto(packet, address)

class ListenerThread(threading.Thread):
    """The Listener Thread grabs incoming packets, parses them and forwards them to the right listeners"""
    def __init__(self, socket):
        super(ListenerThread, self).__init__(
                name='ListenerThread'
        )

        # Exit on script exit
        self.daemon = True

        # Store the socket for later
        self._socket = socket

    def run(self):
        while True:
            data, addr = self._socket.recvfrom(1500)
            print '---'
            print 'Packet From:', addr
            print 'Raw Data:', hexlify(data)
            print 'Parsed:', protocol.parse_packet(data)

