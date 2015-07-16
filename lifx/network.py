import protocol
import socket
import threading
from binascii import hexlify

class LIFXListener(threading.Thread):
    def __init__(self, address='0.0.0.0', port=56700):
        super(LIFXListener, self).__init__(
                name='LIFXListener'
        )

        self.daemon = True

        self._address = address
        self._port = port

    def run(self):
        # Start Listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self._address, self._port))

        while True:
            data, addr = sock.recvfrom(1500)
            print '---'
            print 'Packet From:', addr
            print 'Raw Data:', hexlify(data)
            print 'Parsed:', protocol.parse_packet(data)

