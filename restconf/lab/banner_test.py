'''
Example pyATS test using the AEtest automation harness and Easypy
runtime environment.

The job script (banner_job.py) initializes the testbed, triggers
this testscript, and handles generation of HTML logs for task
execution.
'''

# pylint: disable=no-self-use, too-few-public-methods, fixme
import logging
from requests.exceptions import RequestException
from pyats import aetest

logger = logging.getLogger(__name__)

# Define here where the desired banner text is defined
BANNER_TEXT_FILE = "banner.txt"

class CommonSetup(aetest.CommonSetup):
    """
    Common setup tasks - this class can only be instantiated one time per
    testscript.
    """

    @aetest.subsection
    def mark_tests_for_looping(self, testbed):
        """
        The test will be executed against every device in the testbed, so
        define a variable named "device_name" which stores the list of
        devices from the testbed.
        """
        aetest.loop.mark(TestBanner, device_name=testbed.devices)


class TestBanner(aetest.Testcase):
    """
    Banner Testcase.  Checks whether the Banner text on the device matches
    the desired state.
    """

    device = None
    current_banner = None
    desired_banner = None

    @aetest.setup
    def setup(self, testbed, device_name):
        """
        Initial setup tasks for this Testcase.  Tasks performed:
        1. Connects to the device under test using RESCONF
        2. Reads the desired banner text from BANNER_TEXT_FILE and
           saves the message into self.desired_banner
        """
        self.device = testbed.devices[device_name]
        self.device.connect(via="rest")

        with open(BANNER_TEXT_FILE, "r", encoding="utf-8") as file:
            self.desired_banner = file.read()

    @aetest.test
    def test_banner(self, steps):
        """
        Verify the desired banner message matches the configured banner message
        """

        # First test that you can retrieve the current banner.
        # If there is no banner defined on the router, this leaf does not exist and the
        # step will fail.
        with steps.start(f"Retrieving current banner from {self.device.name}") as step:
            try:
                api_url = "/restconf/data/Cisco-IOS-XE-native:native/banner/login/banner"
                response = self.device.rest.get(
                    api_url =  api_url,
                    content_type = "application/yang-data+json")
            except RequestException:  # Raised if the test fails
                step.failed("No banner message defined for this device.")
            else:  # Test success - pass!
                self.current_banner = response.json()["Cisco-IOS-XE-native:banner"]
                step.passed("Banner message found and retrieved.")

        # After retrieving the current banner message, compare it to the desired banner message.
        with steps.start(
            f"Check whether desired banner matches the configured on {self.device.name}"
                ) as step:
            try:
                assert self.desired_banner == self.current_banner, \
                    "Check whether desired banner matches the configured"
            except AssertionError:  # Raised if the test fails
                step.failed("Desired banner does not match configured banner")
            else:  # Test success - pass!
                step.passed("Desired banner matches configured banner")

    @aetest.cleanup
    def disconnect(self):
        """
        Disconnect from the current device
        """
        self.device.disconnect()
