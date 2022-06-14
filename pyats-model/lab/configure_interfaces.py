"""
Script demonstrating the use of a pyATS method to configure
interfaces based on definitions in the testbed file.

Attributes of interfaces which may be configured are accessible inside the
interface "for" loop using dir(interface).  Any attribute listed that is
specified in the testbed and assigned a value will be applied to the device,
assuming "apply=True" is passed to the method responsible for building
the configuration.
"""
from pyats.topology import loader

TESTBED = "testbed.yml"

# Should the running-config be saved after configuration?
SAVE_CONFIG = True
testbed = loader.load(TESTBED)

print("*" * 78)
for device_name, device in testbed.devices.items():
    print(f"Connecting to device '{device_name}'")
    device.connect(log_stdout=False)

    for interface_name, interface in device.interfaces.items():
        print(f"\tConfiguring interface {interface_name}")

        # How easy is this?
        interface. # <TODO> - Use a method to build and apply interface config

    # Save the running config
    if SAVE_CONFIG:
        device.api. # <TODO> - Use an API to apply and save the configuration

    print(f"Disconnecting from '{device_name}'")
    device.disconnect()
    print("*" * 78)
