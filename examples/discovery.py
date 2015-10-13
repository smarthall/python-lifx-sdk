#!/usr/bin/env python
import signal
import sys
import time
import lifx

# Install a signal handler
def signal_handler(signal, frame):
    print 'CTRL-C received. Exiting.'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Start the client
lights = lifx.Client()

while True:
    # Give some time for discovery
    time.sleep(1)
    
    # Print results
    print '---- DEVICES ----'
    for i in lights.get_devices():
        print i.label

