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

# NOTE: the commented "pylint" lines in scripts are used to control behavior
# of pylint when errors will be displayed but no reasonable workaround is
# possible.
#
# pylint: disable-next=no-name-in-module
from unicon.core.errors import SubCommandFailure
from commands import command_list

TESTBED = "~/abc-en/pyats-testbed/testbed.yml"

testbed = loader.load(TESTBED)

print("-" * 78)

for device_name, device in testbed.devices.items():
    print(f"Configuring device '{device_name}'...")

    print("Connecting to device...")
    device.connect(log_stdout=False)

    # Send each command from the command_list to the device.
    # For each command in the command list, issue
    # device.configure() to send the command to the device in privileged exec
    # configuration mode.  That's all there is to it!
    for command in command_list:

        # Print that the command is being executed without a trailing newline.
        # By default, Python adds a newline to each print() statement.
        # Adding end="" as a print parameter instructs Python to
        # replace the default trailing newline with an empty string, so an
        # "OK/FAIL" indicator can be printed on the same line after the
        # ellipses
        print(f"Sending command '{command}'... ", end="")
        try:
            device. # <TODO> - Use a device method to send each CLI command

        except SubCommandFailure:  # SubCommandFailure if invalid command sent
            # If the command is invalid and configure() fails, print FAIL for
            # the result
            print("FAIL")

        else:
            # The command was successfully sent, print OK as the result
            print("OK")

    print("Disconnecting from device...")
    device.disconnect()
    print("-" * 78)
