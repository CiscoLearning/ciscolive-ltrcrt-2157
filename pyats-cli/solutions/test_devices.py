"""
Example script to test that commands are present in the running configuration
of each device.

Reads the list of commands from the "command_list" variable inside "commands.py"

Steps:
1. Loop over each device in the testbed
2. Connect to the device
3. Use a pyATS parser to get the running configuration
4. For each command in the command list, test that the command is
   present in the running configuration
     - If present, print a PASS statement
     - If absent, print a FAIL statement
5. Disconnect from the device
"""
from pyats.topology import loader
from commands import command_list

TESTBED = "~/abc-en/testbed/testbed.yml"

testbed = loader.load(TESTBED)

print("-" * 78)
for device_name, device in testbed.devices.items():
    print(f"Testing running config for '{device_name}'")

    print("Connecting to device...")
    device.connect(log_stdout=False)

    print("Getting running configuration")
    device_config = device.parse("show running-config")

    for command in command_list:
        try:
            assert command in device_config.keys(), "Test that the command exists in running-config"
        except AssertionError:
            print(f"FAIL: '{command}' not found in configuration.")
        else:
            print(f"PASS: '{command}' is in the configuration.")

    print("Disconnecting from device...")
    device.disconnect()
    print("-" * 78)
