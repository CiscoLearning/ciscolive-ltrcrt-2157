'''
Script to automate changing the banner message of IOS XE device.

Reads file "banner.txt" into variable "banner", which is then
updated on the device using RESTCONF patch method.
'''

from pyats.topology import loader
from requests.exceptions import RequestException

TEMPLATE_PATH = "./templates"
TESTBED = "testbed.yml"
BANNER_TEXT_FILE = "banner.txt"

# Open the banner text file and save the text into banner
with open(BANNER_TEXT_FILE, "r", encoding="utf-8") as file:
    banner = file.#<TODO> add a method that reads the content of the file

print(f"Banner to be configured:\n{banner}")

testbed = loader.load(TESTBED)

print("*" * 78)
# Loop through each of the device in the testbed
for device_name, device in testbed.devices.items():
    print(f"Connecting to device '{device_name}'")
    device.connect(via="<TODO>") # add the rest connection method

    # Load the Jinja2 template and replace the variable
    # banner message with the text saved from the text
    # file.
    rest_payload = device.api.load_jinja_template(
            path=TEMPLATE_PATH,
            file="<TODO>", # add the name of the jinja2 file
            <TODO>=banner, # add the variable you used in the template
            )
    try:
        print("Configuring banner...", end=" ")
        API_URL = "/restconf/<TODO>" # Add the correct RESTCONF URL
        config_result = device.rest.<TODO>( # Add the correct method
                    api_url = API_URL,
                    payload = <TODO>, # Add the correct payload
                    content_type = "application/yang-data+json"
                    )
    # If the previous results in an error, print the error message
    except RequestException as err:
        print(f"FAILED: Error details:\n\t\t\t{err}")
    else:
        print(f"SUCCESS: {config_result.status_code} ({config_result.reason})")
    device.disconnect()
    print("*" * 78)
