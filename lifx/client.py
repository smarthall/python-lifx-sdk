import network
import protocol
import random

class Client(object):
    def __init__(self, address):
        self._transport = network.NetworkTransport(address)

        # Generate Random Client ID
        self._source = random.randrange(1, pow(2, 32) - 1)

        # Start packet sequence at zero
        self._sequence = 0

        # Install our packet handler
        self._transport.register_packet_handler(self._packethandler)

        # Storage for devices
        self._devices = {}

    def _nseq(self):
        seq = self._sequence
        self.sequence += 1
        return seq

    def _packethandler(self, host, port, packet):
        if packet.protocol_header.pkt_type == protocol.TYPE_STATESERVICE:
            self._foundservice(host, packet.payload.service, packet.payload.port, packet.frame_header.source)

    def _foundservice(self, host, service, port, deviceid):
        if deviceid not in self._devices:
            self._devices[deviceid] = Device(deviceid, host)

        self._devices[deviceid].found_service(service, port)

    def discover(self):
        return self._transport.send_discovery(self._source, self._nseq())


class Device(object):
    def __init__(self, device_id, host):
        # Our Device
        self._device_id = device_id
        self._host = host

        # Services
        self._services = {}

    def found_service(service, port):
        self._services[service] = port

