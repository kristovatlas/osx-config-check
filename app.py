"""Checks the configuration of various osx options."""

import time
import sys
import re
from subprocess import Popen, PIPE, STDOUT
import hjson
from warnings import warn
import const #const.py
import prompt #prompt.py

const.ENABLE_DEBUG_PRINT = False
const.DEFAULT_OUTPUT_LOCATION = "~/Documents/"
const.DEFAULT_CONFIG_FILE = "osx-config.hjson"
const.PROMPT_FOR_FIXES = True #TODO: allow user to pass command line arg

const.COLORS = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

const.PASSED_STR = const.COLORS['OKGREEN'] + "PASSED!" + const.COLORS['ENDC']
const.FAILED_STR = const.COLORS['FAIL'] + "FAILED!" + const.COLORS['ENDC']
const.NO_SUDO_STR = ("%s%s%s" %
                     (const.COLORS['WARNING'],
                      ("Insufficient privileges to perform this check. "
                       "Skipping."),
                      const.COLORS['ENDC']))

class ConfigCheck(object):
    """Encapsulates configuration to check in operating system."""
    check_type = ''
    expected_stdout = ''

    def __init__(self, command, comparison_type, expected, fix, case_sensitive,
                 description):
        """
        Args:

            command (str): The command to run to check OS configuration.
            comparison_type (str): "exact match" or "regex match"
            expected (str): The expected string to match or regex to match
                against the stdout of the specified `command`.
            fix (str): The command to run if the configuration fails the check.
            case_senstive (bool): Specifies whether `expected` is a
                case-sensitive comparison.
            description (str): A human-readable description of the configuration
                being checked.
        """
        assert comparison_type in ('exact match', 'regex match')
        self.command = command
        self.comparison_type = comparison_type
        self.expected = expected
        self.fix = fix
        self.case_sensitive = case_sensitive
        self.description = description

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

def get_output_filename():
    """Get the filename of the file to write results to."""
    return (const.DEFAULT_OUTPUT_LOCATION + "config-check_" +
            time.strftime("%Y%m%d%H%M%S") + ".txt")

def read_config(config_filename):
    """Read the expected system configuration from the config file."""

    config = None
    with open(config_filename, 'r') as config_file:
        config = hjson.loads(config_file.read())

    config_checks = []

    for config_check_hjson in config:
        expected = None
        if config_check_hjson['type'] == 'exact match':
            expected = config_check_hjson['expected_stdout']
        elif config_check_hjson['type'] == 'regex match':
            expected = config_check_hjson['expected_regex']
        else:
            sys.exit("Expected comparison string does not match 'type' field.")

        config_check = ConfigCheck(
            command=config_check_hjson['command'],
            comparison_type=config_check_hjson['type'],
            expected=expected,
            fix=config_check_hjson['fix'],
            case_sensitive=(True if config_check_hjson['case_sensitive'] == \
                            'true' else False),
            description=config_check_hjson['description'])
        config_checks.append(config_check)

    return config_checks

def run_check(config_check, last_attempt=False):
    """Perform the specified configuration check against the OS.

    Args:
        config_check (`ConfigCheck`): The check to perform.
        last_attempt (bool): Is this the last time the script checks this
            configuration, or will we check again during this run?
    """
    assert isinstance(config_check, ConfigCheck)

    if 'sudo' in config_check.command:
        print(("About to execute this command to check configuration -- %smay "
               "require administrator privileges%s: '%s'") %
              (const.COLORS['BOLD'], const.COLORS['ENDC'],
               config_check.command))

    #http://stackoverflow.com/questions/7129107/python-how-to-suppress-the-output-of-os-system
    process = Popen(config_check.command, stdout=PIPE, stderr=STDOUT,
                    shell=True)
    stdout, _ = process.communicate()

    stdout = stdout.strip()

    dprint(stdout)
    dprint(config_check.expected)

    result = ""
    if "is not in the sudoers file" in stdout:
        #command required sudo permissions, but user isn't in sudoers list.
        result = const.NO_SUDO_STR
    else:
        if config_check.comparison_type == 'exact match':
            if config_check.case_sensitive:
                if stdout == config_check.expected:
                    result = const.PASSED_STR
                else:
                    result = const.FAILED_STR
            else:
                if stdout.lower() == str(config_check.expected).lower():
                    result = const.PASSED_STR
                else:
                    result = const.FAILED_STR

        elif config_check.comparison_type == 'regex match':
            if is_match(config_check.expected, stdout,
                        ignore_case=(not config_check.case_sensitive)):
                result = const.PASSED_STR
            else:
                result = const.FAILED_STR

    print "%s... %s" % (config_check.description, result)

    if result == const.FAILED_STR and last_attempt:
        warn("Attempted fix %s" % const.FAILED_STR)

    #TODO: write result of check to file
    if result == const.PASSED_STR or result == const.NO_SUDO_STR:
        return True
    elif result == const.FAILED_STR:
        return False
    else:
        raise ValueError

def try_fix(config_check):
    """Attempt to fix a misconfiguration.

    Args:
        config_check (`ConfigCheck`): The check to perform.
    """
    process = Popen(config_check.fix, stdout=PIPE, stderr=STDOUT,
                    shell=True)
    stdout, _ = process.communicate()

def main():
    """Main function."""
    config_checks = read_config(const.DEFAULT_CONFIG_FILE)
    for config_check in config_checks:
        if not run_check(config_check):
            if const.PROMPT_FOR_FIXES:
                question = (("Apply the following fix? This will execute this "
                             "command: '%s'") % config_check.fix)
                if prompt.query_yes_no(question=question, default="yes"):
                    try_fix(config_check)
                    run_check(config_check, last_attempt=True)
            else:
                try_fix(config_check)
                run_check(config_check, last_attempt=True)

def dprint(msg):
    """Debug print statements."""
    if const.ENABLE_DEBUG_PRINT:
        print "DEBUG: %s" % msg

def is_match(regex, string, ignore_case=False):
    """Check if regex matches string."""
    regex_flags = re.DOTALL
    if ignore_case:
        regex_flags = re.DOTALL | re.IGNORECASE

    return re.match(regex, string, regex_flags) is not None

if __name__ == "__main__":
    main()
