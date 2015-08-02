from datetime import datetime
import protocol
from threading import Event
import color

DEFAULT_DURATION = 200
DEFAULT_TIMEOUT = 5

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

    @property
    def _seq(self):
        return self._client._seq

    def _packethandler(self, host, port, packet):
        self._seen()

        # If it was a service packet
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

        kwargs['address'] = self.host
        kwargs['port'] = self.get_port()
        kwargs['target'] = self._device_id

        return self._client.send_packet(
                *args,
                **kwargs
        )

    def _block_for_response(self, *args, **kwargs):
        """
        Send a packet and block waiting for the response, return the response payload.

        Only needs the type and an optional payload.
        """
        sequence = self._seq
        timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)

        e = Event()
        self._tracked[sequence] = e

        self._send_packet(
                ack_required=False,
                res_required=True,
                sequence=sequence,
                *args,
                **kwargs
        )

        e.wait(timeout)
        del self._tracked[sequence]

        # TODO: Check if it was the response we expected
        # TODO: Retransmissions

        return self._responses[sequence].payload

    def _block_for_ack(self, *args, **kwargs):
        """
        Send a packet and block waiting for the acknowledgement

        Only needs the type and an optional payload.
        """
        sequence = self._seq
        timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)

        e = Event()
        self._tracked[sequence] = e

        self._send_packet(
                ack_required=True,
                res_required=False,
                sequence=sequence,
                *args,
                **kwargs
        )

        res = e.wait(timeout)
        del self._tracked[sequence]

        # TODO: Check if the response was actually an ack
        # TODO: Retransmissions

        return True

    def send_poll_packet(self):
        return self._send_packet(
                ack_required=False,
                res_required=True,
                pkt_type=protocol.TYPE_GETSERVICE,
        )

    def _seen(self):
        self._lastseen = datetime.now()

    def __repr__(self):
        return 'Device(MAC:%s, Label:%s)' % (protocol.mac_string(self._device_id), self.label)

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
        response = self._block_for_response(pkt_type=protocol.TYPE_GETLABEL)
        return response.label.decode('UTF-8')

    @property
    def power(self):
        response = self._block_for_response(pkt_type=protocol.TYPE_GETPOWER)
        if response.level > 0:
            return True
        else:
            return False

    @power.setter
    def power(self, power):
        if power:
            msgpower = protocol.UINT16_MAX
        else:
            msgpower = 0

        return self._block_for_ack(msgpower, DEFAULT_DURATION, pkt_type=protocol.TYPE_LIGHT_SETPOWER)

    @property
    def color(self):
        response = self._block_for_response(pkt_type=protocol.TYPE_LIGHT_GET)
        return color.color_from_message(response)

    @color.setter
    def color(self, newcolor):
        colormsg = color.message_from_color(newcolor)
        return self._block_for_ack(
                0,
                colormsg.hue,
                colormsg.saturation,
                colormsg.brightness,
                colormsg.kelvin,
                DEFAULT_DURATION,
                pkt_type=protocol.TYPE_LIGHT_SETCOLOR
        )

    @property
    def colour(self):
        """
        For us aussies. :D
        """
        return self.color

    @colour.setter
    def colour(self, newcolour):
        """
        For us aussies. :D
        """
        self.color = newcolour

    def power_toggle(self):
        self.power = not self.power

