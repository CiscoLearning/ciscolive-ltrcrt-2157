"""
Example pyATS test using the AEtest automation harness and Easypy
runtime environment for interface state testing.

The job script (interface_job.py) initializes the testbed, triggers
this testscript, and handles generation of HTML logs for task
execution.
"""
# pylint: disable=no-self-use, too-few-public-methods, too-many-branches, line-too-long
import logging
import re
from pyats import aetest

# Initialize logging
logger = logging.getLogger(__name__)

ALL_LOOPBACKS = [
    "172.20.100.10",
    "172.20.100.11",
    "172.20.100.12",
    "172.20.100.13",
    "172.20.100.14",
    "192.168.100.1"
]


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

        Each iteration of the marked Testcase will be passed the parameter
        "device_name" with the current device's testbed object.

        :param testbed: Testbed object passed as a parameter from the Easypy
        job file.
        :return: None (no return defined)
        """
        aetest.loop.mark(TestOspf, device_name=testbed.devices)


class TestOspf(aetest.Testcase):
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
        self.device.connect(log_stdout=False, via="cli")

        aetest.loop.mark(
            self.test_interface_ospf, interface_name=self.device.interfaces.keys()
        )

    @aetest.test
    def test_ospf_process(self, steps):
        """
        docstring

        :param steps:

        :return: None (no return)
        """
        ospf_config = self.device.api.get_router_ospf_section_running_config(
            ospf_process_id=self.device.custom.ospf["process_id"])
        ospf_config = ospf_config[f"router ospf {self.device.custom.ospf['process_id']}"]
        logger.info("OSPF config: %s", ospf_config)
        with steps.start("Router-ID matches Loopback0 IP"):
            assert f"router-id {self.device.interfaces['Loopback0'].ipv4.ip}" in ospf_config

        with steps.start("Default route origination") as step:
            if "default_originate_always" in self.device.custom.ospf and self.device.custom.ospf["default_originate_always"]:
                ospf_cli = "default-information originate always"
            elif "default_originate" in self.device.custom.ospf and self.device.custom.ospf["default_originate"]:
                ospf_cli = "default-information originate"
            else:
                step.skipped("No default origination desired.")

            assert ospf_cli in ospf_config

        with steps.start("OSPF Area configuration") as step:
            try:
                for ospf_area in self.device.custom.ospf["ospf_area"]:
                    with step.start(f"Area {ospf_area['area_id']}") as substep:
                        ospf_cli = f"area {ospf_area['area_id']} {ospf_area['area_type']}"
                        if not ospf_area.get("summary", True):
                            ospf_cli = f"{ospf_cli} no-summary"

                        assert ospf_cli in ospf_config
            except KeyError:
                step.skipped("No areas defined")

    @aetest.test
    def test_interface_ospf(self, interface_name, steps):
        """
        Docstring

        :param interface_name:
        :param steps:

        :return: None (no return)
        """
        # pylint: disable=too-many-statements, too-many-locals

        current_interface = self.device.interfaces[interface_name]

        current_interface_config = self.device.api.get_interface_running_config(
            interface=current_interface.name
        )
        current_interface_config = current_interface_config[
            f"interface {current_interface.name}"
        ]

        logger.info("Interface config: %s", current_interface_config)

        with steps.start("OSPF Process and Area") as step:
            try:
                desired_process = current_interface.ospf_process
                desired_area = current_interface.ospf_area

                configured_process = None
                configured_area = None
                configured_network_type = "broadcast"
                # pylint: disable-next=unused-variable
                configured_network_option = ""

                ospf_process_area_regex = re.compile(r"^ip ospf (\d+) area (\d+)")
                ospf_network_type_regex = re.compile(r"^ip ospf network (\S+)\s?(non-broadcast)?$")
                for config_line in current_interface_config:
                    if parsed_line := ospf_process_area_regex.match(config_line):
                        configured_process, configured_area = parsed_line.groups()
                    elif parsed_line := ospf_network_type_regex.match(config_line):
                        configured_network_type, configured_network_option = parsed_line.groups()

                with step.start("OSPF Process") as substep:
                    try:
                        assert int(desired_process) == int(configured_process)
                    except AssertionError:
                        substep.failed(f"Expecting process {desired_process}, configured is {configured_process}")
                    except TypeError:
                        substep.failed(f"Expecting process {desired_process}, configured is {configured_process}")
                    else:
                        substep.passed(f"Interface configured for desired process {desired_process}")

                with step.start("OSPF Area") as substep:
                    try:
                        assert int(desired_area) == int(configured_area)
                    except AssertionError:
                        substep.failed(f"Expecting area {desired_area}, configured is {configured_area}")
                    except TypeError:
                        substep.failed(f"Expecting area {desired_area}, configured is {configured_area}")
                    else:
                        substep.passed(f"Interface configured for desired area {desired_area}")

                with step.start("OSPF Network Type") as substep:
                    try:
                        desired_network_type = current_interface.ospf_network_type
                        assert desired_network_type == configured_network_type
                    except AttributeError:
                        substep.skipped("No network type defined for interface")
                    except AssertionError:
                        substep.failed(f"Expecting network type '{desired_network_type}', configured is '{configured_network_type}'")
                    else:
                        substep.passed(f"Expected network type '{desired_network_type}' configured for interface")


                # This section not used in this lab; leaving source as an example
                # with step.start("OSPF multipoint non-broadcast option") as substep:
                #     try:
                #         desired_network_option = current_interface.ospf_non_broadcast
                #         if desired_network_option:
                #             assert configured_network_option == "non-broadcast"
                #     except AttributeError:
                #         substep.skipped("Non-broadcast option not set for multipoint interface")
                #     except AssertionError:
                #         substep.failed("Multipoint non-broadcast expected but not configured!")
                #     else:
                #         substep.passed("Desired multipoint non-broadcast option is configured")

            except AttributeError:
                self.skipped("No desired OSPF configuration for interface")

    @aetest.test
    def test_ping_from_loopback(self, steps):

        with steps.start("Ping from Loopback0") as step:
            for remote_ip in ALL_LOOPBACKS:
                with step.start(remote_ip, continue_=True) as substep:
                    if str(remote_ip) != str(self.device.interfaces["Loopback0"].ipv4.ip):
                        try:
                            assert self.device.api.verify_ping(address=remote_ip, source="Loopback0", count=3, max_time=1, check_interval=1)
                        except AssertionError:
                            substep.failed("Ping failed - remote loopback unreachable")
                        else:
                            substep.passed("Ping success - device reachable from Loopback0")
                    else:
                        substep.skipped("Destination IP is local Loopback0 - skipping")

    @aetest.cleanup
    def cleanup(self):
        """
        Some docstring

        :return: None (no return)
        """
        self.device.disconnect()
