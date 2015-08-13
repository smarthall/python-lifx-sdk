from datetime import datetime
import protocol
from threading import Event
from lifx.color import modify_color
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
        """
        Send a poll packet to the device, without waiting for a response. The
        response will be received later and will update the time we last saw
        the bulb.
        """
        return self._send_packet(
                ack_required=False,
                res_required=True,
                pkt_type=protocol.TYPE_GETSERVICE,
        )

    def _seen(self):
        self._lastseen = datetime.now()

    def __repr__(self):
        return u'Device(MAC:%s, Label:%s)' % (protocol.mac_string(self._device_id), repr(self.label))

    def get_port(self, service_id=protocol.SERVICE_UDP):
        """
        Get the port for a service, by default the UDP service.

        :param service_id: The service whose port we are fetching.
        """
        return self._services[service_id]

    @property
    def udp_port(self):
        """
        The port of the UDP service. Read Only.
        """
        return self.get_port(protocol.SERVICE_UDP)

    @property
    def seen_ago(self):
        """
        The time in seconds since we last saw a packet from the device. Read Only.
        """
        return datetime.now() - self._lastseen

    @property
    def host(self):
        """
        The ip address of the device. Read Only.
        """
        return self._host

    @property
    def device_id(self):
        """
        The device id. Read Only.
        """
        return self._device_id

    @property
    def label(self):
        """
        The label for the device, setting this will change the label on the device.
        """
        response = self._block_for_response(pkt_type=protocol.TYPE_GETLABEL)
        return protocol.bytes_to_label(response.label)

    @label.setter
    def label(self, label):
        newlabel = bytearray(label.encode('utf-8')[0:protocol.LABEL_MAXLEN])

        return self._block_for_ack(newlabel, pkt_type=protocol.TYPE_SETLABEL)

    def fade_power(self, power, duration=DEFAULT_DURATION):
        """
        Transition to another power state slowly.

        :param power: The new power state
        :param duration: The number of milliseconds to perform the transition over.
        """
        if power:
            msgpower = protocol.UINT16_MAX
        else:
            msgpower = 0

        return self._block_for_ack(msgpower, duration, pkt_type=protocol.TYPE_LIGHT_SETPOWER)

    def power_toggle(self, duration=DEFAULT_DURATION):
        """
        Transition to the opposite power state slowly.

        :param duration: The number of milliseconds to perform the transition over.
        """
        self.fade_power(not self.power, duration)

    @property
    def power(self):
        """
        The power state of the device. Set to False to turn of and True to turn on.
        """
        response = self._block_for_response(pkt_type=protocol.TYPE_GETPOWER)
        if response.level > 0:
            return True
        else:
            return False

    @power.setter
    def power(self, power):
        self.fade_power(power)

    def fade_color(self, newcolor, duration=DEFAULT_DURATION):
        """
        Transition the light to a new color.

        :param newcolor: The HSBK tuple of the new color to transition to
        :param duration: The number of milliseconds to perform the transition over.
        """
        colormsg = color.message_from_color(newcolor)
        return self._block_for_ack(
                0,
                colormsg.hue,
                colormsg.saturation,
                colormsg.brightness,
                colormsg.kelvin,
                duration,
                pkt_type=protocol.TYPE_LIGHT_SETCOLOR
        )

    @property
    def color(self):
        """
        The color the device is currently set to. Set this value to change the
        color of the bulb all at once.
        """
        response = self._block_for_response(pkt_type=protocol.TYPE_LIGHT_GET)
        return color.color_from_message(response)

    @color.setter
    def color(self, newcolor):
        self.fade_color(newcolor)

    # Helpers to change the color on the bulb
    @property
    def hue(self):
        """
        The hue value of the color the bulb is set to. Set this to alter only
        the Hue.
        """
        return self.color.hue

    @hue.setter
    def hue(self, hue):
        self.color = modify_color(self.color, hue=hue)

    @property
    def saturation(self):
        """
        The saturation value the bulb is currently set to. Set this to alter
        only the saturation.
        """
        return self.color.saturation

    @saturation.setter
    def saturation(self, saturation):
        self.color = modify_color(self.color, saturation=saturation)

    @property
    def brightness(self):
        """
        The brightness value the bulb is currently set to. Set this to alter
        only the current brightness of the bulb.
        """
        return self.color.brightness

    @brightness.setter
    def brightness(self, brightness):
        self.color = modify_color(self.color, brightness=brightness)

    @property
    def kelvin(self):
        """
        The kelvin value the bulb is currently set to. Set this to alter
        only the current kelvin of the bulb.
        """
        return self.color.kelvin

    @kelvin.setter
    def kelvin(self, kelvin):
        self.color = modify_color(self.color, kelvin=kelvin)

