#!/usr/bin/env python
import os
import code
import lifx

# Try to get readline if available
try:
    import readline
except ImportError:
    try:
        import pyreadline as readline
    except ImportError:
        pass

broadcast_addr = os.environ.get('LIFX_BROADCAST', '255.255.255.255')

# Start the client
lights = lifx.Client(broadcast=broadcast_addr)

# Start interactive console
shell = code.InteractiveConsole({'lights': lights})
shell.interact(banner='Use the "lights" variable to use the SDK')

