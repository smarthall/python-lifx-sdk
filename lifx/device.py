from datetime import datetime
import protocol

class Device(object):
    def __init__(self, device_id, host, client):
        # Our Device
        self._device_id = device_id
        self._host = host

        # Services
        self._services = {}

        # Last seen time
        self._lastseen = datetime.now()

        # Handle packets from the client
        self._client = client

    def _packethandler(self, host, port, packet):
        pass

    def _seen(self):
        self._lastseen = datetime.now()

    @property
    def seen_ago(self):
        return datetime.now() - self._lastseen

    def found_service(self, service, port):
        self._seen()
        self._services[service] = port

    def __repr__(self):
        return 'Device(MAC:%012x, Seen:%s)' % (self._device_id, self.seen_ago)

    @property
    def host(self):
        return self._host

    @property
    def device_id(self):
        return self._device_id

    def get_port(self, service_id=protocol.SERVICE_UDP):
        return self._services[service_id]

