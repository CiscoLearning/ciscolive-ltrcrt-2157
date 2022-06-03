"""
Docstring
"""
import re
from requests.exceptions import RequestException
from pyats.topology import loader

TEMPLATE_PATH = "./templates"
TESTBED = "testbed.yml"

NATIVE_MODEL = "Cisco-IOS-XE-native:native"
OSPF_MODEL = "Cisco-IOS-XE-ospf:router-ospf"

testbed = loader.load(TESTBED)

interface_regex = re.compile(r"^(\D+)(.*)$")

print("*" * 78)
for device_name, device in testbed.devices.items():
    print(f"Connecting to device '{device_name}'")
    device.connect(via="rest")

    for interface_name, interface in device.interfaces.items():
        print(f"\tConfiguring OSPF on interface {interface_name}")

        parsed_interface_name = interface_regex.match(interface_name)
        interface_type, interface_index = parsed_interface_name.groups()

        url = f"/restconf/data/{NATIVE_MODEL}/interface/" \
              f"{interface_type}={interface_index}/ip/{OSPF_MODEL}/ospf"

        try:
            rest_payload = device.api. # <TODO> - Locate correct template API
                path=TEMPLATE_PATH,
                # <TODO> - Complete parameters for this API call
            )

            print("\t\tConfiguring OSPF process and area...", end="")
            config_result = device.rest.put(
                api_url=url,
                payload=rest_payload,
                content_type="application/yang-data+json",
            )

        except AttributeError as err:
            print("\t\tSKIPPED: No OSPF area defined for interface.")
        except RequestException as err:
            print(
                print(f"FAILED: Error details:\n\t\t\t{err}")
            )
        else:
            print(f"SUCCESS: {config_result.status_code} ({config_result.reason})")

        try:
            url = f"{url}/network"

            rest_payload = device.api. # <TODO> - Load the template via API
                # <TODO> - Supply necessary parameters to this API
            )

            print("\t\tConfiguring OSPF network type...", end="")
            config_result = device.rest.put(
                api_url=url,
                payload=rest_payload,
                content_type="application/yang-data+json",
            )
        except AttributeError as err:
            print("\t\tSKIPPED: No OSPF network type defined for interface.")
        except RequestException as err:
            print(f"FAILED: Error details:\n\t\t\t{err}")
        else:
            print(f"SUCCESS: {config_result.status_code} ({config_result.reason})")

    device.disconnect()
    print("*" * 78)
