import signal
import sys
import time
import lifx.client

# Install a signal handler
def signal_handler(signal, frame):
    print 'CTRL-C received. Exiting.'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Start the client
lights = lifx.client.Client()

while True:
    # Give some time for discovery
    time.sleep(1)
    
    # Print what was discovered
    print lights.get_devices()

