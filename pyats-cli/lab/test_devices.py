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

# Path and name of the pyATS testbed file to load.  Python does not support
# true constants, but variables that should be used as a constant should use
# UPPERCASE names.
TESTBED = "~/abc-en/pyats-testbed/testbed.yml"

# Load the testbed.  The pyATS "loader.load()" handles the import and parsing
# of the YAML testbed file, without requiring additional Python packages
# such as "yaml"
testbed = loader.load(TESTBED)

# Python supports operators such as this when printing strings.  In
# this example, print the dash (-) character 78 times to act as a
# separator.
print("-" * 78)

# Iterate over each device defined in the testbed.
# testbed.devices returns a list of dictionaries where each dict
# key is the device name and the value is the pyATS device object.  The device
# object is used to perform operations such as APIs, parsers, configuration.
#
# The Python items() operator is used to create two variables from a
# dict: the first variable represents the key and the second variable
# represents the value associated with the key.  Here, you create two
# variables that are populated each iteration named "device_name" and
# "device"
for device_name, device in testbed.devices.items():

    # Show the name of the device being tested.
    # Python "f-strings" are very useful!  When using a print()
    # statement, you can prefix the string to print with the letter f
    # and then use variables or Python statement directly inside the string
    # without using concatenation.  Any variable or Python statement enclosed
    # inside single curly braces {} will be interpreted and the value printed!
    print(f"Testing running config for '{device_name}'")

    # Connect to the device and suppress STDOUT
    # By default, pyATS will display all CLI output generated during
    # the connection and setup process, which can be a lot.  To suppress,
    # specify log_stdout=False as a parameter to device.connect()
    print("Connecting to device...")
    device.connect(log_stdout=False)

    print("Getting running configuration")
    device_config = device.  # <TODO_1> - Add a parser to obtain the running configuration

    # For each command in the command_list, assert that the command is present
    # in the running configuration. Catch any AssertionError and print a
    # meaningful message indicating that the command is missing.
    # If no exception is caught, print a message that the command IS in the
    # running-config.
    for command in command_list:
        try:
            assert # <TODO_2> - Build an assertion to test that the command exists in the running-config
        except AssertionError:
            print(f"FAIL: '{command}' not found in configuration.")
        else:
            print(f"PASS: '{command}' is in the configuration.")

    # Disconnect from the device and print a separator string before the next
    # iteration
    print("Disconnecting from device...")
    device.disconnect()
    print("-" * 78)
