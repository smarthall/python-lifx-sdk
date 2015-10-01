.. lifx-sdk documentation master file, created by
   sphinx-quickstart on Tue Aug  4 22:06:59 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to lifx-sdk's documentation!
====================================

Contents
--------

.. toctree::
   :maxdepth: 1

   SDK Documentation <modules>

Getting Started
---------------

Controlling the lights with this SDK has been designed to be as easy as
possible. The SDK handles discovering bulbs and assessing their reachability.

The main entrypoint to the SDK is the :class:`lifx.client.Client` class. It is
responsible for the discovery, reachability and querying the light bulbs. It
returns :class:`lifx.device.Device` objects which represent individual lights.
These two classes will make up the bulk of interactions with the SDK.

A simple workflow for accessing a light is as follows:

#. Create a :class:`lifx.client.Client` class.
#. Wait for discovery to complete
#. Select relevent bulbs.
#. Perform an action on the bulbs.

This is demonstrated in the following code:

.. code-block:: python

    import lifx
    import time

    # Create the client and start discovery
    lights = lifx.Client()

    # Wait for discovery to complete
    time.sleep(1)

    # Turn all bulbs off
    for l in lights.get_devices():
        print 'Turning off %s' % l.label
        l.power = False

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

