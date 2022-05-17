"""
Example pyATS test using the AEtest automation harness and Easypy runtime
environment.

The job script (test_job.py) initializes the testbed, triggers this testscript,
and handles generation of HTML logs for task execution.

DEV NOTE: Observe this script imports the variable "command_list" from the
"commands.py" file, which is also used in the "configure_devices.py" script.
"""
# pylint: disable=no-self-use, too-few-public-methods, fixme
import logging
from pyats import aetest
from commands import command_list

logger = logging.getLogger(__name__)


# DEV NOTE: "CommonSetup" was chosen as the name of this class for clarity.
# The name can be any string, with a preferred naming scheme using CamelCase.
# As long as it inherits "aetest.CommonSetup", this class will be used as the
# one-time initialization for the following tests.
class CommonSetup(aetest.CommonSetup):
    """
    Common setup tasks - this class will only be instantiated one time per
    testscript.
    """

    # DEV NOTE: Class methods defined in this section will be executed in the
    # order defined, and only once per invocation of the script.  Each method
    # must be decorated with "@aetest.subsection" to be executed.
    @aetest.subsection
    def connect(self, testbed):
        """
        First setup task: connect to all devices in the testbed.  The "testbed"
        parameter is passed to the testscript when executed from the pyATS
        job file, and will be accessible to every test throughout.

        :param testbed: Testbed object passed as a parameter from the Easypy
        job file.
        :return: None (no return defined)
        """
        testbed.connect(log_stdout=False)

    @aetest.subsection
    def mark_tests_for_looping(self, testbed):
        """
        This testscript will be executed against every device in the testbed,
        so define a variable named "device_name" which stores the list of
        devices from the testbed.

        Each iteration of the marked Testcase will be passed the parameter
        "device_name" with the name of the device being tested.

        :param testbed: Testbed object passed as a parameter from the Easypy
        job file.
        :return: None (no return defined)
        """

        # Mark the "TestCommandsPresent" Testcase for looping
        aetest.loop.mark(TestCommandsPresent, device_name=testbed.devices)


# DEV NOTE: Like the CommonSetup class above, this class name can be anything
# that represents the purpose of the test - CamelCase preferred per Python
# class naming recommendations.  Note that the actual test class inherits
# the "aetest.Testcase" class (instead of aetest.CommonSetup) and can therefore
# be executed repeatedly, such as via a loop.  Also, note that the testcase
# name here matches the name of the testcase marked for looping in the
# "mark_tests_for_looping" method of CommonSetup.
class TestCommandsPresent(aetest.Testcase):
    """
    Test that each command defined in the imported list "command_list" is
    present in the running configuration of the device.
    """

    # DEV NOTE: Inside the Testcase, a single setup section and a single
    # cleanup section may be defined.  These are executed for each iteration
    # of the Testcase (compared to the CommonSetup, which is only executed
    # one time per execution of the entire script).
    # The setup section must be identified with the @aetest.setup decorator,
    # and the cleanup section must be identified with the @aetest.cleanup
    # decorator.
    @aetest.setup
    def setup(self, testbed, device_name):
        """
        Initial setup tasks for this Testcase.  Tasks performed:
            - Set the parameter 'device' accessible to each test which is a
              reference to the testbed device object for the current host to
              be tested

        :param testbed: Easypy-passed testbed object
        :param device_name: Current device name as loop-marked by CommonSetup

        :return: None (no return value)
        """
        # Set the 'device' parameter for all tests.  Once the parameter is set,
        # every test in this Testcase must have "device" as one of the
        # defined parameters.  Tests can then access any API, parser, or model
        # available to the device object without needing to repeat the
        # "device = testbed.devices[device_name]" definition.
        self.parameters["device"] = testbed.devices[device_name]

    @aetest.test
    def test_commands_in_configuration(self, device, steps):
        """
        Obtain the running configuration from the device into a dictionary
        using a Genie API.  Iterate over each command from the imported
        "command_list" variable and determine if the command is present
        in the keys of the running configuration dictionary.

        Each command being tested will appear in the final output as a
        separate step, so it will be obvious which command is present
        or missing instead of a single PASS/FAIL for the entire test.

        :param device: Current testbed device object reference
        :param steps: Reserved parameter argument representing the current
            step iteration.

        :return: None (no return)
        """
        device_config = device.api. # <TODO> - Use an API to get running-config dict

        # DEV NOTE: Each time this loop iterates over the command_list, the
        # "steps.start" creates a new instance of a "Steps" class and can be
        # accessed using the optional variable "step."  The parameter to
        # "steps.start" will be the output displayed at the completion of the
        # test script.
        #
        # The optional variable "step" can be named anything; it represents
        # each step (iteration), but "step" is short and meaningful.
        # Then, for each iteration, a state can be assigned to the individual
        # step such as "failed" or "passed" with a message to display during
        # execution of the test.
        #
        # Observe the reserved step parameter "continue_=True".  This
        # instructs pyATS to continue the steps even if the first step gets
        # marked as failed.  This is not always used, but in this test we want
        # to see if all commands are present or if some commands are missing,
        # so continue iterating through each command.  By default, if any step
        # is marked as failed, the test is marked as failed and processing
        # stops at that point.
        # Also note that the parameter has a trailing underscore (_) because
        # Python has a reserved statement "continue" for loop control.  The
        # underscore ensures there is no conflict with the Python statement.
        for command in command_list:
            with steps.start(command, continue_=True) as step:
                try:
                    # <TODO> - Create an assertion to check if command in device config

                except AssertionError:  # AssertionError means the test failed
                    # The current command was not found in the running config,
                    # so fail the step and print a message indicating the
                    # reason.
                    step.failed("Command not present in running-config")

                else:  # "else" will execute if no exceptions were raised.
                    # The current command is present in the running config,
                    # so set the step state to "passed" and display a
                    # message indicating the reason.
                    step.passed("Command present in running-config")


# DEV NOTE: "CommonCleanup" was chosen as the name of this class for clarity.
# The name can be any string, with a preferred naming scheme using CamelCase.
# As long as it inherits "aetest.CommonCleanup", this class will be used as the
# one-time cleanup after all testcases have been executed.
class CommonCleanup(aetest.CommonCleanup):
    """
    Common cleanup tasks - this class can only be instantiated one time per
    testscript.
    """

    # DEV NOTE: Class methods defined in this section will be executed in the
    # order defined, and only once per invocation of the script.  Each method
    # must be decorated with "@aetest.subsection" to be executed.
    @aetest.subsection
    def disconnect(self, testbed):
        """
        Disconnect from all testbed devices

        :param testbed: Easypy-passed testbed object
        :return: None (no return value)
        """
        testbed.disconnect()
