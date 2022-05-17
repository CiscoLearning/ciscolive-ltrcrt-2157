"""
Example script to configure devices using CLI commands with pyATS

Reads the list of commands from the "command_list" variable inside the
"commands.py" file

Steps:
1. Loop over each device in the testbed
2. Connect to the device
3. For each command in the command list:
     - Print the command to be issued
     - Use the pyATS configure() method to issue the CLI command
4. Disconnect from the device
"""
from pyats.topology import loader

# pylint: disable-next=no-name-in-module
from unicon.core.errors import SubCommandFailure
from commands import command_list

# DEV NOTE: This script is treating the testbed filename as a constant.
# Best practice in Python is to use ALL_CAPS for constant names.
TESTBED = "~/abc-en/pyats-testbed/testbed.yml"

# DEV NOTE: The pyATS loader.load(testbed_filename) handles the import
# and parsing of the testbed YAML file.  No need to import yaml and
# handle the parsing yourself!
testbed = loader.load(TESTBED)

# DEV NOTE: Python supports operators such as this when printing strings.  In
# this example, print the dash (-) character 78 times to act as a separator.
print("-" * 78)

# DEV NOTE: testbed.devices returns a list of dictionaries where each dict
# key is the device name and the value is the pyATS device object.  The device
# object is used to perform operations such as APIs, parsers, configuration.
#
# The Python items() operator is used to create two variables from a dict:
# the first variable represents the key and the second variable represents
# the value associated with the key.  Here, you create two variables that
# are populated each iteration named "device_name" and "device"
for device_name, device in testbed.devices.items():

    # DEV NOTE: Python "f-strings" are very useful!  When using a print()
    # statement, you can prefix the string to print with the letter f
    # and then use variables or Python statement directly inside the string
    # without using concatenation.  Any variable or Python statement enclosed
    # inside single curly braces {} will be interpreted and the value printed!
    print(f"Configuring device '{device_name}'...")

    # DEV NOTE: By default, pyATS will display all CLI output generated during
    # the connection and setup process.  This can be a lot!  To suppress,
    # specify "log_stdout=False" as a parameter to device.connect()
    print("Connecting to device...")
    device.connect(log_stdout=False)

    # DEV NOTE: This is it!  For each command in the command list, use
    # device.configure() the command to the device in privileged exec/
    # configuration mode.  That's all there is to it.
    for command in command_list:

        # DEV NOTE: Adding "end=''" as a print parameter instructs Python to
        # replace the default trailing newline with an empty string, so an
        # "OK/FAIL" indicator can be printed on the same line after the
        # ellipses
        print(f"Sending command '{command}'... ", end="")
        try:
            device.configure(command)

        except SubCommandFailure:  # SubCommandFailure if invalid command sent
            # If the command is invalid and configure() fails, print FAIL for
            # the result
            print("FAIL")

        else:
            # The command was successfully sent, print OK as the result
            print("OK")

    # Disconnect from the device and print a separator string before the next
    # iteration
    print("Disconnecting from device...")
    device.disconnect()
    print("-" * 78)
