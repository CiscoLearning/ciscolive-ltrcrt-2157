"""
Simple module to store a list of commands readable by configuration
and test scripts.

Each CLI command should be entered as a separate list element, enclosed
in quotation marks and comma-separated except the last element in the list
"""
command_list = [
    "ip httr secure-server",
    "ip http authentication local",
    # <TODO> - Add any other commands to be applied to the running-config
]
