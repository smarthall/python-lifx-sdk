from datetime import datetime
import protocol
from threading import Event
from colors import HSBK

class Device(object):
    def __init__(self, device_id, host, client):
        # Our Device
        self._device_id = device_id
        self._host = host

        # Services
        self._services = {}

        # Last seen time
        self._lastseen = datetime.now()

        # For sending packets
        self._client = client

        # Tools for tracking responses
        self._tracked = {}
        self._responses = {}

    def _packethandler(self, host, port, packet):
        self._seen()

        if packet.protocol_header.pkt_type == protocol.TYPE_STATESERVICE:
            self._services[packet.payload.service] = packet.payload.port

        # Store packet and fire events
        self._responses[packet.frame_address.sequence] = packet
        event = self._tracked.get(packet.frame_address.sequence, None)
        if event is not None:
            event.set()

    def _send_packet(self, *args, **kwargs):
        """
        At this point we have most of the required arguments for the packet. The
        only arguments left that we need are:

        * ack_required
        * res_required
        * pkt_type
        * Arguments for the payload
        """
        return self._client.send_packet(
                address=self.host,
                port=self.get_port(),
                target=self._device_id,
                *args,
                **kwargs
        )

    def _block_for_response(self, timeout=5, *args, **kwargs):
        """
        Send a packet and block waiting for the response, return the response payload.

        Only needs the type and an optional payload.
        """
        self._send_packet(
                ack_required=False,
                res_required=True,
                *args,
                **kwargs
        )

        sequence = kwargs['sequence']

        e = Event()
        self._tracked[sequence] = e
        e.wait(timeout)
        del self._tracked[sequence]
        return self._responses[sequence].payload

    def send_poll_packet(self):
        return self._send_packet(
                ack_required=False,
                res_required=True,
                pkt_type=protocol.TYPE_GETSERVICE,
        )

    def _seen(self):
        self._lastseen = datetime.now()

    def __repr__(self):
        return 'Device(MAC:%s, Seen:%s)' % (protocol.mac_string(self._device_id), self.seen_ago)

    def get_port(self, service_id=protocol.SERVICE_UDP):
        return self._services[service_id]

    @property
    def udp_port(self):
        return self.get_port(protocol.SERVICE_UDP)

    @property
    def seen_ago(self):
        return datetime.now() - self._lastseen

    @property
    def host(self):
        return self._host

    @property
    def device_id(self):
        return self._device_id

    @property
    def label(self):
        return self._block_for_response(pkt_type=protocol.TYPE_GETLABEL)

