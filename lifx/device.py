from datetime import datetime
import protocol
from threading import Event
from collections import namedtuple
from lifx.color import modify_color
import color
import time

DEFAULT_DURATION = 200
DEFAULT_TIMEOUT = 2.0
DEFAULT_RETRANSMITS = 10

StatsTuple = namedtuple('StatsTuple', ['dropped_packets', 'sent_packets'])

class DeviceTimeoutError(Exception):
    '''Raise when we time out waiting for a response'''
    def __init__(self, device, timeout, retransmits):
        message = "Device with id:'%s' timed out after %s seconds and %s retransmissions." % (protocol.mac_string(device.id), timeout, retransmits)

        super(DeviceTimeoutError, self).__init__(message)
        self.device = device
        self.timeout = timeout
        self.retransmits = retransmits

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

        # Stats tracking
        self._dropped_packets = 0
        self._sent_packets = 0

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

        self._sent_packets += 1

        return self._client.send_packet(
                *args,
                **kwargs
        )

    def _block_for_response(self, *args, **kwargs):
        return self._block_for(False, True, *args, **kwargs)

    def _block_for_ack(self, *args, **kwargs):
        return self._block_for(True, False, *args, **kwargs)

    def _block_for(self, need_ack, need_res, *args, **kwargs):
        """
        Send a packet and block waiting for the replies.

        Only needs the type and an optional payload.
        """
        if need_ack and need_res:
            raise NotImplemented('Waiting for both acknowledgement and response not yet supported.')

        sequence = self._seq
        timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
        sub_timeout = timeout / DEFAULT_RETRANSMITS

        for i in range(1, DEFAULT_RETRANSMITS):
            if i != 1:
                self._dropped_packets += 1

            e = Event()
            self._tracked[sequence] = e

            self._send_packet(
                    ack_required=need_ack,
                    res_required=need_res,
                    sequence=sequence,
                    *args,
                    **kwargs
            )

            # If we don't care about a response, don't block at all
            if not (need_ack or need_res):
                return None

            if e.wait(sub_timeout):
                response = self._responses[sequence]

                # TODO: Check if the response was actually what we expected

                if need_res:
                    return response.payload
                else:
                    return True

        # We did get a response
        raise DeviceTimeoutError(self, timeout, DEFAULT_RETRANSMITS)


    def _get_group_data(self):
        """
        Called by the group object so it can see the updated_at from the group
        """
        return self._block_for_response(pkt_type=protocol.TYPE_GETGROUP)

    def _get_location_data(self):
        """
        Called by the group object so it can see the updated_at from the location
        """
        return self._block_for_response(pkt_type=protocol.TYPE_GETLOCATION)

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
        return u'<Device MAC:%s, Label:%s>' % (protocol.mac_string(self._device_id), repr(self.label))

    def get_port(self, service_id=protocol.SERVICE_UDP):
        """
        Get the port for a service, by default the UDP service.

        :param service_id: The service whose port we are fetching.
        """
        return self._services[service_id]

    @property
    def stats(self):
        return StatsTuple(
                dropped_packets=self._dropped_packets,
                sent_packets=self._sent_packets,
        )

    @property
    def group_id(self):
        """
        The id of the group that the Device is in. Read Only.
        """
        response = self._get_group_data()
        return response.group

    @property
    def location_id(self):
        """
        The id of the group that the Device is in. Read Only.
        """
        response = self._get_location_data()
        return response.location

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
    def host_firmware(self):
        """
        The version string representing the firmware version.
        """
        response = self._block_for_response(pkt_type=protocol.TYPE_GETHOSTFIRMWARE)
        return protocol.version_string(response.version)

    @property
    def wifi_firmware(self):
        """
        The version string representing the firmware version.
        """
        response = self._block_for_response(pkt_type=protocol.TYPE_GETWIFIFIRMWARE)
        return protocol.version_string(response.version)

    @property
    def id(self):
        """
        The device id. Read Only.
        """
        return self._device_id

    @property
    def latency(self):
        """
        The latency to the device. Read Only.
        """
        ping_payload = bytearray('\x00' * 64)
        start = time.time()
        response = self._block_for_response(ping_payload, pkt_type=protocol.TYPE_ECHOREQUEST)
        end = time.time()
        return end - start

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

