import random
import threading
from datetime import datetime, timedelta

import network
import protocol
import device
import util

MISSED_POLLS = 3

class Client(object):
    def __init__(self, address='0.0.0.0', discoverpoll=60, devicepoll=5):
        # Get Transport
        self._transport = network.NetworkTransport(address)

        # Arguments
        self._discoverpolltime = discoverpoll
        self._devicepolltime = devicepoll

        # Generate Random Client ID
        self._source = random.randrange(1, pow(2, 32) - 1)

        # Start packet sequence at zero
        self._sequence = 0

        # Storage for devices
        self._devices = {}

        # Install our packet handler
        pktfilter = lambda p:p.protocol_header.pkt_type == protocol.TYPE_STATESERVICE
        self._transport.register_packet_handler(self._servicepacket, pktfilter)

        # Send initial discovery packet
        self.discover()

        # Start polling threads
        self._discoverpoll = util.RepeatTimer(discoverpoll, self.discover)
        self._discoverpoll.daemon = True
        self._discoverpoll.start()
        self._devicepoll = util.RepeatTimer(devicepoll, self.poll_devices)
        self._devicepoll.daemon = True
        self._devicepoll.start()

    def __del__():
        self._discoverpoll.cancel()

    @property
    def _seq(self):
        seq = self._sequence
        self._sequence += 1
        return seq

    def _servicepacket(self, host, port, packet):
        self._foundservice(host, packet.payload.service, packet.payload.port, packet.frame_address.target)

    def _foundservice(self, host, service, port, deviceid):
        if deviceid not in self._devices:
            new_device = device.Device(deviceid, host, self)
            pktfilter = lambda p:p.frame_address.target == deviceid
            self._devices[deviceid] = new_device

        self._devices[deviceid].found_service(service, port)

    def _poll_device(self, device):
        return self._transport.send_packet(
                device.host,
                device.get_port(protocol.SERVICE_UDP),
                self._source,
                device.device_id,
                False, # No Ack Required
                True, # Response Required
                self._seq,
                protocol.TYPE_GETSERVICE,
        )

    def discover(self):
        return self._transport.send_discovery(self._source, self._seq)

    def poll_devices(self):
        poll_delta = timedelta(seconds=self._devicepolltime - 1)

        for device in filter(lambda x:x.seen_ago > poll_delta,  self._devices.values()):
            self._poll_device(device)

    def get_devices(self, max_seen=None):
        if max_seen is None:
            max_seen = self._devicepolltime * MISSED_POLLS

        seen_delta = timedelta(seconds=max_seen)

        return filter(lambda x:x.seen_ago < seen_delta, self._devices.values())

