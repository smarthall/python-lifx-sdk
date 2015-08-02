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

    def __repr__(self):
        return repr(self.get_devices())

    @property
    def _seq(self):
        seq = self._sequence
        self._sequence = (self._sequence + 1) % pow(2, 8)
        return seq

    def _servicepacket(self, host, port, packet):
        service = packet.payload.service
        port = packet.payload.port
        deviceid = packet.frame_address.target

        if deviceid not in self._devices:
            # Create a new Device
            new_device = device.Device(deviceid, host, self)

            # Send its own packets to it
            pktfilter = lambda p:(
                    p.frame_address.target == deviceid
                    and (
                        p.protocol_header.pkt_type == protocol.TYPE_ACKNOWLEDGEMENT
                        or p.protocol_header.pkt_type in protocol.CLASS_TYPE_STATE
                    ))
            self._transport.register_packet_handler(new_device._packethandler, pktfilter)

            # Send the service packet directly to the device
            new_device._packethandler(host, port, packet)

            # Store it
            self._devices[deviceid] = new_device

    def send_packet(self, *args, **kwargs):
        # Add a sequence number if a higher layer didnt
        if 'sequence' not in kwargs.keys():
            kwargs['sequence'] = self._seq

        kwargs['source'] = self._source

        return self._transport.send_packet(
                *args,
                **kwargs
        )

    def discover(self):
        return self._transport.send_discovery(self._source, self._seq)

    def poll_devices(self):
        poll_delta = timedelta(seconds=self._devicepolltime - 1)

        for device in filter(lambda x:x.seen_ago > poll_delta,  self._devices.values()):
            device.send_poll_packet()

    def get_devices(self, max_seen=None):
        if max_seen is None:
            max_seen = self._devicepolltime * MISSED_POLLS

        seen_delta = timedelta(seconds=max_seen)

        devices = filter(lambda x:x.seen_ago < seen_delta, self._devices.values())

        # Sort by device id to ensure consistent ordering
        return sorted(devices, key=lambda k:k.device_id)

    def __getitem__(self, key):
        return self.get_devices()[key]

