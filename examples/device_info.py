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

# Give some time for discovery
time.sleep(1)

# Print results
for i in lights.get_devices():
    print '--- Device: "%s" ---' % i.label
    print 'Power: %r' % i.power
    color = i.color
    print 'Color:'
    print '  Hue: %d' % color.hue
    print '  Saturation: %d' % color.saturation
    print '  Brightness: %d' % color.brightness
    print '  Kelvin: %d' % color.kelvin

