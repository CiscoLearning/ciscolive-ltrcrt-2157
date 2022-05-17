"""
Sample pyATS Easypy job file.  The benefits of using a job file:
  - Parameters passed to the job, such as --testbed-file, will be parsed
    and passed as necessary to the test script, reducing the need to use
    argparse or similar to handle argument testing
  - The testbed object will be loaded during job setup, so there is no need
    to import the pyats.topology.loader and use loader.load() to import
    the testbed
  - The job handles execution of the test script and stores execution results,
    enabling the "pyats logs view" command to start the log web server and
    display results in HTML.

Example:
    pyats run job test_job.py --testbed-file <your_testbed_file>

Arguments:
    --testbed-file: Path and filename of the pyATS testbed file
"""
# DEV NOTE: Any command starting with "# pylint" is used to control the
# behavior of pylint and disable/enable specific checks which may fail
# but are not "true" failures.  Used sparingly, these controls can improve
# the quality of your code linting tasks!
import os
import logging
from pyats.easypy import run  # pylint: disable=no-name-in-module


# DEV NOTE: Best practice when using the "logging" package is to instantiate
# a logger for the special variable "__name__".  This enables scripts in a
# Python package/module to inherit the same logging object and output the
# name of the current script when writing output to the logging target.
# In this script, the "logger" object is not used but is instantiated anyway
# as a best practice :)
logger = logging.getLogger(__name__)

# Find the filesystem location of this file.  This will be used to specify
# a full path and filename to the testscript to execute
test_path = os.path.dirname(os.path.abspath(__file__))

# Define the testscript to execute.  "os.path.join" will create a full
# filesystem path by joining the first path to the name of the file specified.
testscript = os.path.join(test_path, "")  # <TODO> - specify the test file


def main(runtime):
    """
    Program entrypoint.

    main() is run automatically when pyATS Easypy starts the job.

    :param runtime: When defined, the Easypy engine automatically passes the
    current runtime object in as an argument.  Includes information about the
    current execution environment, job name, other useful information.

    :return: None (no return)
    """

    # Change the default job name to something useful.  Default is the name of
    # the job file.  This will be displayed in the output and log file.
    runtime.job.name = "Test commands present in device running configuration"

    # Execute the testscript
    run(testscript=testscript, runtime=runtime)
