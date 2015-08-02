import readline
import code
import time
import lifx.client

# Start the client
lights = lifx.client.Client()

# Start interactive console
print 'Use the "lights" variable to use the SDK'
shell = code.InteractiveConsole({'lights': lights})
shell.interact()
