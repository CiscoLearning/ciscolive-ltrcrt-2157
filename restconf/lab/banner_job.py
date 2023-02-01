'''
Sample pyATS Easypy job file for banner testing.

Example:
    pyats run job banner_job.py --testbed-file <your tb file>

Arguments:
    --testbed-file: Path and filename of the pyATS testbed file
'''

import os
import logging
from pyats.easypy import run  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)

# Find the location of the script in relation to the job file
test_path = os.path.dirname(os.path.abspath(__file__))

# Define the testscript to execute
testscript = os.path.join(test_path, "banner_test.py")


def main(runtime):
    """
    Program entrypoint.

    main() is run automatically when pyATS Easypy starts the job.

    :param runtime: When defined, the Easypy engine automatically passes the
    current runtime object in as an argument.  Includes information about the
    current execution environment, job name, other useful information.

    :return: None (no return)
    """

    # Change the default job name to something useful
    runtime.job.name = "Test Login Banner configuration"

    # Execute the testscript
    run(testscript=testscript, runtime=runtime)
