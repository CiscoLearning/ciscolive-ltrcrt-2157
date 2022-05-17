# DEV NOTE: In this example, a "try...except...else" statement is used to
# "catch" the AssertionError exception generated by the failed first test,
# and continue to the second.
#
# This demonstrates the Python concept of "EAFP," or "Easier to Ask for
# Forgiveness than Permission" - in other words, design the script so that
# any expected errors are caught when generated and handled gracefully instead
# of letting the program terminate unexpectedly.
#
# "try" means to begin a block of commands that we are interested in catching
# exceptions.
#
# "except" means to catch a specific exception such as AssertionError and do
# some task instead of failing
#
# "else" instructs Python to perform tasks inside that block if no exception
# is generated.
#
# In this script, the second assert will be executed because the AssertionError
# created by the first assert will be handled in the try...except...else block.
#
try:
    # This will result in a value of False.
    assert 2 == 1
except AssertionError:
    print("2 doesn't equal 1!  This failed, but we'll continue")
else:
    print("This will never be printed because 2 will never equal 1.")

try:
    # This will result in a value of True.
    assert 1 == 1
except AssertionError:
    print("This should never be printed, because 1 equals 1.")
else:
    print("This will always be printed because no exception was raised!")
