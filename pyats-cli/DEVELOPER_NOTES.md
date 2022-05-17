# DEV NOTES: pyats-cli
Notes contained in this file are referenced by files inside the ```pyats-cli``` lab activity.  
## test_job.py
1. Any command starting with ```# pylint``` is used to control the
behavior of pylint and disable/enable specific checks which may fail
but are not "true" failures.  Used sparingly, these controls can improve
the quality of your code linting tasks!


2. Best practice when using the ```logging``` package is to instantiate
a logger for the special variable ```__name__```.  This enables scripts in a
Python package/module to inherit the same logging object and output the
name of the current script when writing output to the logging target.
In this script, the ```logger``` object is not used but is instantiated
as a best practice :)

## test_devices.py
3. ```CommonSetup``` was chosen as the name of this class for clarity.
The name can be any string, with a preferred naming scheme using CamelCase.
As long as it inherits ```aetest.CommonSetup```, this class will be used as the
one-time initialization for the following tests.


4. Class methods defined in this section will be executed in the
order defined, and only once per invocation of the script.  Each method
must be decorated with ```@aetest.subsection``` to be executed.


5. Like the CommonSetup class above, this class name can be anything
that represents the purpose of the test - CamelCase preferred per Python
class naming recommendations.  Note that the actual test class inherits
the ```aetest.Testcase``` class (instead of ```aetest.CommonSetup```) and can therefore
be executed repeatedly, such as via a loop.  Also, note that the testcase
name here matches the name of the testcase marked for looping in the
```mark_tests_for_looping``` method of CommonSetup. 


6. Inside the Testcase, a single setup section and a single
cleanup section may be defined.  These are executed for each iteration
of the Testcase (compared to the ```CommonSetup```, which is only executed
one time per execution of the entire script).
The setup section must be identified with the ```@aetest.setup``` decorator,
and the cleanup section must be identified with the ```@aetest.cleanup```
decorator.


7. Each time this loop iterates over the command_list, the
```steps.start``` creates a new instance of a ```steps``` class and can be
accessed using the optional variable ```step```.  The parameter to
```steps.start``` will be the output displayed at the completion of the
test script.

   - The optional variable ```step``` can be named anything; it represents
   each step (iteration), but "step" is short and meaningful.
   Then, for each iteration, a state can be assigned to the individual
   step such as ```failed``` or ```passed``` with a message to display during
   execution of the test.

   - Observe the reserved step parameter ```continue_=True```.  This
instructs pyATS to continue the steps even if the first step gets
marked as **failed**.  This is not always used, but in this test we want
to see if all commands are present or if some commands are missing,
so continue iterating through each command.  By default, if any step
is marked as **failed**, the test is marked as **failed** and processing
stops at that point.

   - Also note that the parameter has a trailing underscore (```_```) because
Python has a reserved statement ```continue``` for loop control.  The
underscore ensures there is no conflict with the Python statement.


8. ```CommonCleanup``` was chosen as the name of this class for clarity.
The name can be any string, with a preferred naming scheme using CamelCase.
As long as it inherits ```aetest.CommonCleanup```, this class will be used as the
one-time cleanup after all testcases have been executed.

## configure_devices.py
9. This script is treating the testbed filename as a constant.
Best practice in Python is to use ALL_CAPS for constant names.


10. The pyATS ```loader.load(testbed_filename)``` handles the import
and parsing of the testbed YAML file.  No need to import yaml and
handle the parsing yourself!


11. Python supports operators such as this when printing strings.  In
this example, print the dash (```-```) character 78 times to act as a separator.


12. testbed.devices returns a list of dictionaries where each dict
key is the device name and the value is the pyATS device object.  The device
object is used to perform operations such as APIs, parsers, configuration.

    - The Python items() operator is used to create two variables from a dict:
    the first variable represents the key and the second variable represents
    the value associated with the key.  Here, you create two variables that
    are populated each iteration named "device_name" and "device"


13. Python "f-strings" are very useful!  When using a print()
statement, you can prefix the string to print with the letter ```f```
and then use variables or Python statement directly inside the string
without using concatenation.  Any variable or Python statement enclosed
inside single curly braces ```{}``` will be interpreted and the value printed!


14. By default, pyATS will display all CLI output generated during
the connection and setup process.  This can be a lot!  To suppress,
specify ```log_stdout=False``` as a parameter to device.connect()


15. For each command in the command list, issue
```device.configure()``` as command to the device in privileged exec/
configuration mode.  That's all there is to it!


16. Adding ```end=''``` as a print parameter instructs Python to
replace the default trailing newline with an empty string, so an
"OK/FAIL" indicator can be printed on the same line after the
ellipses
