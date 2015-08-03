import readline
import code
import lifx

# Start the client
lights = lifx.Client()

# Start interactive console
shell = code.InteractiveConsole({'lights': lights})
shell.interact(banner='Use the "lights" variable to use the SDK')

