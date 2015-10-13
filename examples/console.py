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


# Start the client
lights = lifx.Client()

# Start interactive console
shell = code.InteractiveConsole({'lights': lights})
shell.interact(banner='Use the "lights" variable to use the SDK')

