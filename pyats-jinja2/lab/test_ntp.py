"""
Example pyATS test using the AEtest automation harness and Easypy
runtime environment.

The job script (ntp_job.py) initializes the testbed, triggers
this testscript, and handles generation of HTML logs for task
execution.
"""
# pylint: disable=no-self-use, too-few-public-methods, fixme
import logging
from pyats import aetest

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    """
    Common setup tasks - this class can only be instantiated one time per
    testscript.
    """

    @aetest.subsection
    def connect(self, testbed):
        """
        First setup task: connect to all devices in the testbed

        :param testbed: Testbed object passed as a parameter from the Easypy
            job file.

        :return: None (no return)
        """
        testbed. # <TODO_1> - Connect to each device without showing CLI output

    @aetest.subsection
    def mark_tests_for_looping(self, testbed):  # , perform_configuration):
        """
        The test will be executed against every device in the testbed, so
        define a variable named "device_name" which stores the list of
        devices from the testbed.

        Each iteration of the marked Testcase will be passed the parameter
        "device_name" with the current device's testbed object name.

        :param testbed: Testbed object passed as a parameter from the Easypy
            job file.

        :return: None (no return)
        """

        aetest.loop.mark(TestNTP, device_name=testbed.devices)


class TestNTP(aetest.Testcase):
    """
    NTP Testcase.  Perform checks related to NTP configuration and operations
    on the IOS-XE platform.
    """

    device = None

    @aetest.setup
    def setup(self, testbed, device_name):
        """
        Initial setup tasks for this Testcase.  Tasks performed:
            - Set the object attribute 'device' which is accessible throughout
              this test as "self.device" and is a reference to the pyATS
              testbed device object.

        :param testbed: Easypy-passed testbed object
        :param device_name: Current device as loop-marked by CommonSetup

        :return: None (no return)
        """
        # Set the 'device' parameter for all tests
        self.device = testbed.devices[device_name]

        aetest.loop.mark(self.test_ntp_servers,
                         ntp_server=self.device.custom.ntp_servers)

    @aetest.test
    def test_ntp_source_interface(self):
        """
        Verify the desired NTP source interface matches the configured source
        interface

        :return: None (no return)
        """

        desired_source_interface = self.device.custom.ntp_source
        configured_source_interface = self.device. # <TODO_2> - Use a Genie API to get the NTP source interface

        # Observe that a simple pass/fail result will be generated based on
        # the test of the desired state (from the testbed) to the configured
        # state based on the output of the device get_ntp_source_interface_ip()
        # API. In this scenario, the self.failed or self.passed state is set
        # to indicate pass/fail status of this test.
        try:
            assert # <TODO_3> - Assert that the desired source interface exists in the configuration

        except TypeError:  # Raised if the configured interface is "None"
            self.failed("No source interface configured on device")

        except AssertionError:  # Raised if the test fails
            self.failed("Desired source interface does not match configured")

        else:  # Test success - pass!
            self.passed("Desired source interface matches configured source")

    @aetest.test
    def test_ntp_servers(self, ntp_server):
        """
        Verify that desired NTP servers configured on the device match the
        desired state

        :param ntp_server: Current NTP server iteration as marked by the
            test setup method.

        :return: None (no return)
        """

        try:
            assert  # <TODO_4> - Verify the ntp server exists in the configured server list
        # <TODO_5> - Catch the TypeError exception if no NTP servers are configured
        except AssertionError:
            self.failed(f"Server {ntp_server} not present in running config")
        else:
            self.passed("Desired server present in running config")


class CommonCleanup(aetest.CommonCleanup):
    """
    Common cleanup tasks - this class can only be instantiated one time per
    testscript.
    """

    @aetest.subsection
    def disconnect(self, testbed):
        """
        Disconnect from all testbed devices

        :param testbed: Easypy-passed testbed object

        :return: None (no return)
        """
        testbed.disconnect()
