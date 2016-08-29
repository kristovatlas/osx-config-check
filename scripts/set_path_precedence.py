"""Enforces a specific order for two directories in the PATH environment var.

This is enforced by modifying the bash profile file stored at ~/.profile
"""

import sys
import re
import os

ENABLE_DEBUG_PRINT = False
PROFILE_FILENAME =  os.path.expanduser('~/.profile')

class BrokenOrderError(Exception):
    """There's something wrong with the order of commands in .profile """
    pass

def _main():
    assert len(sys.argv) == 3
    dir_1 = str(sys.argv[1])
    dir_2 = str(sys.argv[2])

    dprint("%s %s" % (dir_1, dir_2))

    if _is_path_good(dir_1, dir_2):
        dprint("Path was good")
        return

    #scan profile to ensure PATH is not already set to desired value
    profile = []
    with open(PROFILE_FILENAME, 'r') as profile_read:
        profile = profile_read.readlines()

    found_intended_path = False

    for line in profile:
        #ignore commented out lines
        if re.search(line, r'^\s*#.*$') is not None:
            continue

        if _is_path_set_in_line(line, dir_1):
            dprint("Found line that sets intended path: %s" % line)
            found_intended_path = True

        if found_intended_path and _is_path_set_in_line(line, dir_2):
            #a later export declaration has overriden what we wanted, panic D-:
            raise BrokenOrderError

    if not found_intended_path:
        new_path_entry = "\nexport PATH=%s:$PATH\n" % dir_1
        with open(PROFILE_FILENAME, 'a') as profile_append:
            profile_append.write(new_path_entry)

def _is_path_good(dir_1, dir_2):
    return _is_match(os.environ['PATH'], r'.*%s.*%s.*' % (dir_1, dir_2))

def _is_match(string, pattern):
    return re.compile(pattern).search(string) is not None

def _is_path_set_in_line(line, dir_1):
    passing_path_entry = r'^.*PATH=%s.*$' % dir_1
    return _is_match(line, passing_path_entry)

def dprint(data):
    """Print debug data, if enabled."""
    if ENABLE_DEBUG_PRINT:
        print "DEBUG: %s" % data

if __name__ == '__main__':
    _main()
