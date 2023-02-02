"""
Simple script to locate CML topology with title including "clus" and call the
lab start API.

Error checking is minimal - rapid prototype for lab use
"""
from sys import exit as sysexit
from time import sleep
import requests
from urllib3 import disable_warnings
from cml_creds import CML_HOST, auth_payload
from apihelper import http_exceptions, init_http_session, BearerAuth, close_http_session
from argparse import (ArgumentParser)


# Global TLS verification - False if using self-signed certificates
TLS_VERIFY = False

# If self-signed, disable the urllib3 security warnings
if not TLS_VERIFY:
    disable_warnings()

# Base URL for the HTTP session
BASE_URL = f"https://{CML_HOST}"

# Generic application/json headers
HTTP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Authenticate, get a token, and create an HTTP session.  Retry until
# MAX_RETRIES is hit, otherwise exit the script
CML_TOKEN = None
MAX_RETRIES = 5
RETRY = 1

while not CML_TOKEN:
    if RETRY == MAX_RETRIES:
        sysexit("Maximum retry limit reached, unable to connect to CML. "
                "Check settings and CML host reachability.")
    else:
        try:
            print(f"Attempting to authenticate to CML at {BASE_URL} (attempt #{RETRY})...")
            cml_auth_url = f"{BASE_URL}/api/v0/authenticate"
            auth_response = requests.post(url=cml_auth_url,
                                          json=auth_payload,
                                          headers=HTTP_HEADERS,
                                          verify=TLS_VERIFY,
                                          timeout=5)
            CML_TOKEN = auth_response.json()
        # pylint: disable-next=broad-except
        except Exception as err:  # Catch any exception, not worried about specifics
            print(f"Exception encountered during authentication.  Details:\n{err}")
            RETRY += 1
        else:
            # Use init_http_session from apihelper to start a BaseUrlSession
            # with bearer token auth, TLS validation disabled, and generic
            # application/json headers
            print("Authentication success!  Initializing the HTTP session...")
            http_session = init_http_session(baseurl=BASE_URL, auth=BearerAuth(token=CML_TOKEN))
            http_session.verify = TLS_VERIFY
            http_session.headers.update(
                {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )


@http_exceptions
def get_cml_labs():
    """
    Get all labs from the CML instance.

    :return: JSON response containing a list of lab IDs
    """
    url = "/api/v0/labs"
    print("Retrieving available labs from CML...")
    lab_response = http_session.get(url=url)
    return lab_response.json()


@http_exceptions
def get_cml_lab_details(lab_id):
    """
    Get the details of a specific lab

    :param lab_id: ID of the lab to retrieve
    :return: JSON response containing the lab details
    """
    url = f"/api/v0/labs/{lab_id}"
    print(f"Retrieving details for lab with ID '{lab_id}' from CML...")
    lab_response = http_session.get(url=url)
    return lab_response.json()


@http_exceptions
def get_cml_lab_nodes(lab_id):
    """
    Get all nodes from a CML lab.

    :return: JSON response containing a list of node IDs
    """
    url = f"/api/v0/labs/{lab_id}/nodes"
    print(f"Retrieving all nodes from from with ID '{lab_id}'...")
    lab_response = http_session.get(url=url)
    return lab_response.json()


@http_exceptions
def get_cml_node_details(lab_id, node_id):
    """
    Get details for a specific CML node.

    :return: JSON response containing node details
    """
    url = f"/api/v0/labs/{lab_id}/nodes/{node_id}"
    # print(f"Retrieving node details for device...")
    lab_response = http_session.get(url=url)
    return lab_response.json()


@http_exceptions
def restart_cml_node(lab_id, node_id):
    """
    Restart a CML node.

    :return: Boolean indicating success (True) or failure (False)
    """
    restart_result = False

    state_url = f"/api/v0/labs/{lab_id}/nodes/{node_id}/state"
    stop_url = f"{state_url}/stop"
    start_url = f"{state_url}/start"
    print(f"Stopping node...")
    lab_response = http_session.put(url=stop_url)
    if lab_response.ok:
        while stop_result := http_session.get(url=state_url):
            if stop_result.json()["state"] == "STOPPED":
                break
            else:
                sleep(5)

        print(f"Starting node...")
        start_response = http_session.put(url=start_url)
        if start_response.ok:
            while stop_result := http_session.get(url=state_url):
                if stop_result.json()["state"] == "STARTED":
                    restart_result = True
                    break
                else:
                    sleep(5)

    return restart_result


@http_exceptions
def start_cml_lab(lab_id):
    """
    Send a start request for the specified lab

    :param lab_id: ID of the lab to start
    :return: HTTP response of the start request
    """
    url = f"/api/v0/labs/{lab_id}/start"
    print(f"Starting CML topology with ID '{lab_id}'...")
    lab_response = http_session.put(url=url)
    return lab_response


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-n",
                        dest="node_name",
                        action="store",
                        help="Name of node to restart",
                        required=True)
    args = parser.parse_known_args()[0]

    cml_labs = get_cml_labs()
    print(f"Got labs: {cml_labs}")

    try:
        for lab in cml_labs:
            lab_details = get_cml_lab_details(lab)
            if "ltrcrt-2157" in lab_details.get("lab_title").lower():
                lab_nodes = get_cml_lab_nodes(lab)
                for node in lab_nodes:
                    node_details = get_cml_node_details(lab, node)
                    if args.node_name.lower() == node_details["data"]["label"].lower():
                        print("Node ID located, restarting device...")
                        restart_response = restart_cml_node(lab, node)
                        if restart_response:
                            print("\n*** Node restarted. Please wait 3-5 minutes for bootup ***\n")
                        else:
                            print("\n***Problem restarting the node. Please ask your proctor for assistance! ***\n")

                break
    except TypeError:
        print("No labs retrieved from CML, check settings and re-try.")

    close_http_session(http_session)
