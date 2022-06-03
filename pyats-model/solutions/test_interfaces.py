"""
Example pyATS test using the AEtest automation harness and Easypy
runtime environment for interface state testing.

The job script (interface_job.py) initializes the testbed, triggers
this testscript, and handles generation of HTML logs for task
execution.
"""
# pylint: disable=no-self-use, too-few-public-methods, too-many-branches, line-too-long
import logging
from pyats import aetest

# Initialize logging
logger = logging.getLogger(__name__)

# If no shutdown state defined for an interface, set a default
# False = "no shutdown"
# True = "shutdown"
UNSPECIFIED_SHUTDOWN_STATE = False

# If no IPv4 address or unnumbered reference defined for an interface, should
# it be assumed to be unnumbered?
ASSUME_DEFAULT_UNNUMBERED = True

# If assuming unnumbered, what should the assumed source interface be?
DEFAULT_UNNUMBERED_SOURCE = "Loopback0"


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
        :return: None (no return defined)
        """
        testbed.connect(log_stdout=False)

    @aetest.subsection
    def mark_tests_for_looping(self, testbed):
        """
        The test will be executed against every device in the testbed, so
        define a variable named "device_name" which stores the list of
        devices from the testbed.

        Each iteration of the marked Testcase will be passed the parameter
        "device_name" with the current device's testbed object.

        :param testbed: Testbed object passed as a parameter from the Easypy
        job file.
        :return: None (no return defined)
        """
        aetest.loop.mark(TestInterfaces, device_name=testbed.devices)


class TestInterfaces(aetest.Testcase):
    """
    Main Testcase.  Perform checks against desired vs configured interface
    state on the IOSXE platform.
    """

    # Create 'device' attribute which will be initialized with the pyATS
    # device object during setup.  Any future reference to the device will
    # be made using "self.device" instead of passing the device parameter
    # or repeating "device = testbed.devices[device_name]" in each test.
    device = None

    @aetest.setup
    def setup(self, testbed, device_name):
        """
        Initial setup tasks for this Testcase.  Tasks performed:
            - Initialize the object attribute "device" as a reference to the
              testbed device object for the current host.
            - Mark the "test_interface" method for looping where method
              parameter "interface_name" will represent the currently
              iterated interface's name.

        :param testbed: Easypy-passed testbed object
        :param device_name: Current device as loop-marked by CommonSetup

        :return: None (no return)
        """
        self.device = testbed.devices[device_name]

        # Mark test_interface_state test to loop device interface names
        aetest.loop.mark(
            self.test_interface_state, interface_name=self.device.interfaces.keys()
        )

    @aetest.test
    def test_interface_state(self, interface_name, steps):
        """
        Perform tests against the current interface.  The following test logic
        is implemented:
          - Validate interface admin state (shutdown?)
          - Validate the interface description if defined in the testbed
          - Check configured interface IPv4 address/prefix matches the desired
          - Check unnumbered interface settings if no IPv4 and the interface
            has a testbed unnumbered source reference OR use the default
            unnumbered source if unspecified interfaces are assumed to be
            unnumbered (check constants at the top of this file)

        :param interface_name: pyATS testbed interface name as marked for
            looping in the setup method.
        :param steps: Reserved parameter argument representing the current
            step iteration.

        :return: None (no return)
        """
        # pylint: disable=too-many-statements

        # Set the current interface object for easy access in the test
        current_interface = self.device.interfaces[interface_name]

        # Grab the running config dict for this interface then remove the key
        # so only the interface config lines exist.  Useful for tests where no
        # API currently exists.
        current_interface_config = self.device.api.get_interface_running_config(
            interface=current_interface.name
        )
        current_interface_config = current_interface_config[
            f"interface {current_interface.name}"
        ]

        # Test 1: Check the admin state.
        with steps.start("Admin state (shutdown)", continue_=True) as step:
            # If the shutdown attribute is not set, UNSPECIFIED_SHUTDOWN_STATE
            # will be the default (True = shutdown, False = no shutdown)
            desired_state = current_interface.shutdown or UNSPECIFIED_SHUTDOWN_STATE

            # Use "verify_interface_state_admin_down" as it reflects the same
            # boolean state as interface.shutdown
            configured_state = self.device.api.verify_interface_state_admin_down(
                interface=interface_name, max_time=1
            )

            try:
                assert desired_state == configured_state, "Check interface shutdown state"
            except AssertionError:
                step.failed(
                    f"Desired shutdown state: {desired_state}, "
                    f"configured is {configured_state}"
                )
            else:
                step.passed("Interface admin state matches desired.")

        # Verify the interface description.  If not defined in the testbed,
        # skip this test
        with steps.start("Interface description", continue_=True) as step:
            if desired_state := current_interface.description:
                try:
                    assert self.device.api.verify_interface_description_in_running_config(
                            interface=current_interface.name, description=desired_state
                    ), "Test interface description"
                except AssertionError:
                    step.failed(f"Desired description '{desired_state}' not configured")
                else:
                    step.passed("Configured interface description matches desired.")
            else:
                step.skipped("No desired state defined for description.")

        # Check the IPv4 address and prefix for the interface.  If no IPv4
        # defined in the testbed, skip this test.
        with steps.start("Interface IPv4 address", continue_=True) as step:
            if not current_interface.ipv4:
                step.skipped("No desired IPv4 address defined in testbed")

            try:
                configured_state = self.device.api.get_interface_ip_and_mask(
                    interface=current_interface.name, prefix=True
                )[0]
                assert str(current_interface.ipv4) == str(configured_state), "Test IPv4 address"
            except AssertionError:
                step.failed(
                    f"Expecting {current_interface.ipv4}, configured is {configured_state}"
                )
            else:
                step.passed("Desired IP address matches configured")

        # If the interface should be unnumbered OR if there is no definition
        # for the interface in the testbed, see if the ASSUME constant is set.
        # If both false, skip this test.
        # If an IPv4 address is defined for this interface, skip the test.
        with steps.start("Unnumbered interface", continue_=True) as step:
            if ASSUME_DEFAULT_UNNUMBERED:
                logger.info(
                    "NOTICE: Assuming unnumbered interface for unspecified state"
                )

            if (
                not current_interface.unnumbered_intf_ref
                and not ASSUME_DEFAULT_UNNUMBERED
            ):
                step.skipped("No desired unnumbered configuration")
            elif current_interface.ipv4:
                step.skipped("IPv4 defined for interface, skipping unnumbered check")

            # Set the unnumbered source to the testbed OR the default constant
            # if not defined.  Then obtain the desired IP for the source
            desired_unnumbered_source = (
                current_interface.unnumbered_intf_ref or DEFAULT_UNNUMBERED_SOURCE
            )

            # Initialize the configured source in case no matching config
            for config_line in current_interface_config:
                if config_line.startswith("ip unnumbered"):

                    # Found the config, reduce to the target interface
                    configured_unnumbered_source = config_line.replace(
                        "ip unnumbered ", ""
                    )
                    break

            # Does the configured unnumbered source match desired?
            with step.start("Unnumbered source interface") as substep:
                try:
                    assert desired_unnumbered_source == configured_unnumbered_source, "Test unnumbered source interface"
                except AssertionError:
                    substep.failed(
                        f"Desired unnumbered source: {desired_unnumbered_source}, "
                        f"Configured unnumbered source {configured_unnumbered_source}"
                    )
                except UnboundLocalError:
                    substep.failed(
                        "No ip unnumbered configuration present on interface."
                    )
                else:
                    substep.passed("Interface configured for IP unnumbered")

            # Determine the IP and prefix of the desired/configured sources
            desired_ip_address = self.device.interfaces[desired_unnumbered_source].ipv4
            configured_ip_address = self.device.api.get_interface_ip_and_mask(
                interface=configured_unnumbered_source, prefix=True
            )[0]

            # ... and test that the addresses match:
            with step.start("Unnumbered IP address") as substep:
                try:
                    assert str(desired_ip_address) == str(configured_ip_address), "Test unnumbered source IP"
                except AssertionError:
                    substep.failed(
                        f"Desired source IP: {desired_ip_address}, "
                        f"Configured source IP: {configured_ip_address}"
                    )
                else:
                    substep.passed("Unnumbered source IP matches desired")


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
        :return: None (no return value)
        """
        testbed.disconnect()
