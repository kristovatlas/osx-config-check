"""Checks the configuration of various osx options."""

import time
import sys
import re
from subprocess import Popen, PIPE, STDOUT
from warnings import warn
from enum import Enum
import hjson
import const #const.py
import prompt #prompt.py

const.ENABLE_DEBUG_PRINT = False
const.DEFAULT_OUTPUT_LOCATION = "~/Documents/"
const.DEFAULT_CONFIG_FILE = "osx-config.hjson"
const.PROMPT_FOR_FIXES = True #TODO: allow user to pass command line arg
const.WARN_FOR_RECOMMENDED = True #TODO: command line flag
const.WARN_FOR_EXPERIMENTAL = True #TODO: command line flag
const.FIX_RECOMMENDED_BY_DEFAULT = True #TODO: command line flag
const.FIX_EXPERIMENTAL_BY_DEFAULT = False #TODO: command line flag

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
const.RECOMMENDED_STR = ("%s%s%s" % (const.COLORS['BOLD'],
                                     'RECOMMENDED',
                                     const.COLORS['ENDC']))
const.EXPERIMENTAL_STR = ("%s%s%s" % (const.COLORS['BOLD'],
                                      'EXPERIMENTAL',
                                      const.COLORS['ENDC']))

class Confidence(Enum):
    """Likelihood that a configuration will create negative side-effects.

    A lower integer value indicates less likelihood that a configuration will
    cause problems with applications.
    """
    required = 1
    recommended = 2
    experimental = 3

class ConfigCheck(object):
    """Encapsulates configuration to check in operating system."""
    check_type = ''
    expected_stdout = ''

    def __init__(self, command, comparison_type, expected, fix, case_sensitive,
                 description, confidence, sudo_command=None, sudo_fix=None):
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
            confidence (str): "required", "recommended", or "experimental"
            sudo_command (Optional[str]): A version of `command` that
                requests administrative privileges from the operating system.
                This will only be executed if `command` does not produce the
                desired results.
            sudo_fix (Optional[str]): A version of `fix` that requests
                administrative privileges from the operating system. This will
                only be executed if `fix` does not produce the desired config
                change.
        """
        assert comparison_type in ('exact match', 'regex match')
        self.command = command
        self.sudo_command = sudo_command #default: None
        self.comparison_type = comparison_type
        self.expected = expected
        self.fix = fix
        self.sudo_fix = sudo_fix #default: None
        self.case_sensitive = case_sensitive
        self.description = description

        if confidence == 'required':
            self.confidence = Confidence.required
        elif confidence == 'recommended':
            self.confidence = Confidence.recommended
        elif confidence == 'experimental':
            self.confidence = Confidence.experimental
        else:
            raise ValueError

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

        sudo_command = None
        if 'sudo_command' in config_check_hjson:
            sudo_command = config_check_hjson['sudo_command']

        sudo_fix = None
        if 'sudo_fix' in config_check_hjson:
            sudo_fix = config_check_hjson['sudo_fix']

        config_check = ConfigCheck(
            command=config_check_hjson['command'],
            comparison_type=config_check_hjson['type'],
            expected=expected,
            fix=config_check_hjson['fix'],
            case_sensitive=(True if config_check_hjson['case_sensitive'] == \
                            'true' else False),
            description=config_check_hjson['description'],
            confidence=config_check_hjson['confidence'],
            sudo_command=sudo_command,
            sudo_fix=sudo_fix)
        config_checks.append(config_check)

    return config_checks

def run_check(config_check, last_attempt=False, quiet_fail=False):
    """Perform the specified configuration check against the OS.

    This will perform the check once without sudo privileges; if that fails and
    a sudo version of this check has been specified, that will be performed,
    with the final result value being a logical-or of the outcomes.

    Args:
        config_check (`ConfigCheck`): The check to perform.
        last_attempt (bool): Is this the last time the script checks this
            configuration, or will we check again during this run?
        quiet_fail (bool): Suppress print failed results to stdout?
            Default: False.

    Returns:
        bool: Whether check passed.
    """
    assert isinstance(config_check, ConfigCheck)

    passed = _execute_check(config_check.command, config_check.comparison_type,
                            config_check.expected, config_check.case_sensitive)

    if not passed and config_check.sudo_command is not None:
        passed = _execute_check(config_check.sudo_command,
                                config_check.comparison_type,
                                config_check.expected,
                                config_check.case_sensitive)

    if passed or not quiet_fail:
        print "%s... %s" % (config_check.description, _get_result_str(passed))
        #TODO: write result of check to file

    if not passed and last_attempt and do_warn(config_check):
        warn("Attempted fix %s" % const.FAILED_STR)

    return passed

def _get_result_str(result_bool):
    return const.PASSED_STR if result_bool else const.FAILED_STR

def _execute_check(command, comparison_type, expected, case_sensitive):
    """Helper function for `run_check` -- executes command and checks result.

    Args:
        command (str): The command to execute to perform the check.
        comparison_type (str): 'exact match' or 'regex match'
        expected (str): Result expected in output, either exact match or regex.
        case_sensitive (bool): Whether the comparison to output is case
            senstive.

    Returns:
       bool: Whether the output matched the expected output of the command.
    """
    #http://stackoverflow.com/questions/7129107/python-how-to-suppress-the-output-of-os-system
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    stdout, _ = process.communicate()

    stdout = stdout.strip()

    dprint("Command executed to check config: '%s'" % str(command))
    dprint("Result of command: '%s'" % str(stdout))
    dprint("Expected this result: '%s'" % str(expected))

    if comparison_type == 'exact match':
        if case_sensitive:
            return stdout == expected
        else:
            return stdout.lower() == str(expected).lower()
    elif comparison_type == 'regex match':
        return is_match(expected, stdout, ignore_case=(not case_sensitive))
    else:
        raise ValueError

def do_warn(config_check):
    """Determines whether the config failure merits warning."""
    if config_check.confidence == Confidence.required:
        return True
    if (config_check.confidence == Confidence.recommended and
            const.WARN_FOR_RECOMMENDED):
        return True
    if (config_check.confidence == Confidence.experimental and
            const.WARN_FOR_EXPERIMENTAL):
        return True
    return False

def _try_fix(config_check, use_sudo=False):
    """Attempt to fix a misconfiguration.

    Args:
        config_check (`ConfigCheck`): The check to perform.
        use_sudo (bool): Whether to use the sudo version of this command. If
            no sudo version of this command has been specified in the config
            file, this will simply return without executing anything.
    """
    command = config_check.sudo_fix if use_sudo else config_check.fix
    if use_sudo:
        print(("Attempting configuration fix with elevated privileges; %syou "
              "may be prompted for your OS X login password%s...") %
              (const.COLORS['BOLD'], const.COLORS['ENDC']))
    if command is not None:
        process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        process.communicate()

    dprint("Command executed: '%s'" % str(command))

def do_fix_and_test(config_check):
    """Attempt to fix misconfiguration w/ and w/o sudo privs, returning result.

    Args:
        config_check (`ConfigCheck`): The check to perform.

    Returns:
        bool: Whether an attempted fix was successful.
    """
    _try_fix(config_check, use_sudo=False)
    if run_check(config_check, last_attempt=False, quiet_fail=True):
        return True
    else:
        _try_fix(config_check, use_sudo=True)
        return run_check(config_check, last_attempt=True, quiet_fail=False)

def main():
    """Main function."""
    config_checks = read_config(const.DEFAULT_CONFIG_FILE)
    for config_check in config_checks:
        if not run_check(config_check):
            #config failed check
            if const.PROMPT_FOR_FIXES:
                prompt_default = True
                descriptor = ''
                if config_check.confidence == Confidence.recommended:
                    prompt_default = const.FIX_RECOMMENDED_BY_DEFAULT
                    descriptor = const.RECOMMENDED_STR + ' '
                elif config_check.confidence == Confidence.experimental:
                    prompt_default = const.FIX_EXPERIMENTAL_BY_DEFAULT
                    descriptor = const.EXPERIMENTAL_STR + ' '
                question = (("Apply the following %s fix? This will execute "
                             "this command: '%s'") %
                            (descriptor, config_check.fix))
                if prompt.query_yes_no(question=question,
                                       default=_bool_to_yes_no(prompt_default)):
                    do_fix_and_test(config_check)
            else:
                do_fix_and_test(config_check)

def _bool_to_yes_no(boolean):
    return 'yes' if boolean else 'no'

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
