from pyats.topology import loader

TEMPLATE_PATH = "./templates"
TESTBED = "testbed.yml"

def read_banner_text(banner_file):
    with open(banner_file, "r", encoding="utf-8") as file:
        banner = file.read()
    return banner

def create_payload(template, value):
    payload = ""
    return payload

def configure_banner_with_restconf(device, payload):
    device.connect(via="rest")
    url = "/restconf/data/Cisco-IOS-XE-native:native/banner/login/banner"
    device.rest.patch(
            api_url = url,
            payload = payload,
            content_type = "application/yang-data+json"
            )


banner_text = read_banner_text()
banner_payload = create_payload()

testbed = loader.load(TESTBED)
for device in testbed.devices:
    configure_banner_with_restconf(device)