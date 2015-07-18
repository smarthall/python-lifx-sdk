import protocol
import socket
import threading
from binascii import hexlify
from collections import namedtuple

DEFAULT_LIFX_PORT = 56700

PacketHandler = namedtuple('PacketHandler', ['handler', 'pktfilter'])

class NetworkTransport(object):
    """The network transport manages the network sockets and the networking threads"""
    def __init__(self, address='0.0.0.0'):
        # Prepare a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((address, 0))

        self._socket = sock

        self._listener = ListenerThread(sock, self._handle_packet)
        self._listener.start()

        self._packet_handlers = []

    def _sendto(self, packet, address, port):
        return self._socket.sendto(packet, (address, port))

    def send_packet(self, address, port, *args, **kwargs):
        packet = protocol.make_packet(*args, **kwargs)
        return self._sendto(packet, address, port)

    def send_discovery(self, source, sequence, address='255.255.255.255'):
        return self._sendto(protocol.discovery_packet(source, sequence), address, DEFAULT_LIFX_PORT)

    def register_packet_handler(self, handler, pktfilter=None):
        # If None install all packet handler
        if pktfilter is None:
            pktfilter = lambda x:True

        h = PacketHandler(handler, pktfilter)
        self._packet_handlers.append(h)

    def _handle_packet(self, address, packet):
        for handler, pktfilter in self._packet_handlers:
            if pktfilter(packet):
                host, port = address
                handler(host, port, packet)

class ListenerThread(threading.Thread):
    """The Listener Thread grabs incoming packets, parses them and forwards them to the right listeners"""
    def __init__(self, socket, handler):
        super(ListenerThread, self).__init__(
                name='ListenerThread'
        )

        # Exit on script exit
        self.daemon = True

        # Store instance data
        self._socket = socket
        self._handler = handler

    def run(self):
        while True:
            data, addr = self._socket.recvfrom(1500)
            self._handler(addr, protocol.parse_packet(data))

