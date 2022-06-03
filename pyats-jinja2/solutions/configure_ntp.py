"""
Example script to configure devices using Jinja2 templates with pyATS

Steps:
1. Loop over each device in the testbed
2. Connect to the device
3. Load a Jinja2 template as an object using a Genie API
4. Configure the device using the template object, passing custom testbed
   parameters to the Jinja2 template for rendering
"""
from pyats.topology import loader

# pylint: disable-next=no-name-in-module
from unicon.core.errors import SubCommandFailure

TESTBED = "testbed.yml"

# TEMPLATE_DIR will be used as the path to locate Jinja2 templates
# and TEMPLATE_FILE will be used to specify the template file to be read.
TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "ntp_template.j2"

testbed = loader.load(TESTBED)

print("*" * 78)
for device_name, device in testbed.devices.items():
    print(f"Connecting to device '{device_name}'")
    device.connect(log_stdout=False)

    device_template = device.api.get_jinja_template(
        templates_dir=TEMPLATE_DIR, template_name=TEMPLATE_FILE
    )

    try:
        # Other than the template parameter which specifies the
        # template object to load, any other key/value pair will be passed
        # to Jinja2 and accessible inside the template for rendering.
        device.api.change_configuration_using_jinja_templates(
            template=device_template,
            ntp_source=device.custom.ntp_source,
            ntp_servers=device.custom.ntp_servers,
        )
    except SubCommandFailure as err:
        print(f"Failed to configure device:\n{err}")

    print(f"Disconnecting from '{device_name}'")
    device.disconnect()
    print("*" * 78)
