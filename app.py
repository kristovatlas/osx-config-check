"""Checks the configuration of various osx options."""

import time
import datetime
from os.path import expanduser
import sys
import re
from subprocess import Popen, PIPE, STDOUT
from warnings import warn
import json
from enum import Enum
import const #const.py
import prompt #prompt.py

const.ENABLE_DEBUG_PRINT = False
const.DEFAULT_OUTPUT_LOCATION = "~/Documents/"
const.WRITE_TO_LOG_FILE = True #TODO: Allow user to pass command line arg
const.DEFAULT_CONFIG_FILE = "osx-config.json"
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
    'RED': '\033[91m',
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

def get_timestamp():
    """Genereate a current timestamp that won't break a filename."""
    timestamp_format = '%Y-%m-%d_%H-%M-%S'
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime(timestamp_format)
    return timestamp

const.LOG_FILE_NAME = 'osx-config-check_%s.log' % get_timestamp()
const.LOG_FILE_LOC = const.DEFAULT_OUTPUT_LOCATION + const.LOG_FILE_NAME

glob_check_num = 1

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

    def __init__(self, command, comparison_type, expected, case_sensitive,
                 description, confidence, fix=None, sudo_fix=None,
                 manual_fix=None, sudo_command=None):
        """
        Args:

            command (str): The command to run to check OS configuration.
            comparison_type (str): "exact match" or "regex match"
            expected (str): The expected string to match or regex to match
                against the stdout of the specified `command`.
            case_senstive (bool): Specifies whether `expected` is a
                case-sensitive comparison.
            description (str): A human-readable description of the configuration
                being checked.
            confidence (str): "required", "recommended", or "experimental"
            fix (Optional[str]): The command to run if the configuration fails
                the check.
            sudo_fix (Optional[str]): A version of `fix` that requests
                administrative privileges from the operating system. This will
                only be executed if `fix` does not produce the desired config
                change.
            manual_fix (Optional[str]): Instructions to output to the user to
                manually remediate if a config cannot be fixed automatically.
            sudo_command (Optional[str]): A version of `command` that
                requests administrative privileges from the operating system.
                This will only be executed if `command` does not produce the
                desired results.
        """
        assert comparison_type in ('exact match', 'regex match')
        self.command = command
        self.comparison_type = comparison_type
        self.expected = expected
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

        #Optional args
        self.fix = fix #default: None
        self.sudo_fix = sudo_fix #default: None
        self.manual_fix = manual_fix #default: None
        self.sudo_command = sudo_command #default: None

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
        config = json.loads(config_file.read())

    config_checks = []

    for config_check in config:
        if '_comment' in config_check:
            continue

        #Config MUST specify a command to check the status of the system
        command = config_check['command']

        #Config MUST specify either expected STDOUT or regex pattern
        expected = None
        comparison_type = None
        if config_check['type'] == 'exact match':
            comparison_type = 'exact match'
            expected = config_check['expected_stdout']
        elif config_check['type'] == 'regex match':
            comparison_type = 'regex match'
            expected = config_check['expected_regex']
        else:
            sys.exit("Expected comparison string does not match 'type' field.")

        #Config MUST specify whether the commands checking the status are case
        #sensitive
        case_sensitive = False
        assert config_check['case_sensitive'] in ('true', True, 'false', False)
        if config_check['case_sensitive'] in ('true', True):
            case_sensitive = True

        #Config MUST specify a description of the check
        description = config_check['description']
        dprint("Description: %s" % description)

        #Config MUST indicate the confidence of the configuration check
        confidence = config_check['confidence']

        #Config MUST specify a fix object
        assert 'fix' in config_check
        assert isinstance(config_check['fix'], dict)

        #Fix object must specify at least one of these:
        #command, sudo_command, manual
        assert ('command' in config_check['fix'] or
                'sudo_command' in config_check['fix'] or
                'manual' in config_check['fix'])
        fix = None
        sudo_fix = None
        manual_fix = None
        if 'command' in config_check['fix']:
            fix = config_check['fix']['command']
        if 'sudo_command' in config_check['fix']:
            sudo_fix = config_check['fix']['sudo_command']
        if 'manual' in config_check['fix']:
            manual_fix = config_check['fix']['manual']

        #Config MAY specify a sudo_command, a sudo version of "command"
        sudo_command = None
        if 'sudo_command' in config_check:
            sudo_command = config_check['sudo_command']

        config_check_obj = ConfigCheck(
            command=command,
            comparison_type=comparison_type,
            expected=expected,
            case_sensitive=case_sensitive,
            description=description,
            confidence=confidence,
            fix=fix,
            sudo_fix=sudo_fix,
            manual_fix=manual_fix,
            sudo_command=sudo_command)
        config_checks.append(config_check_obj)

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
        fancy_sudo_command = re.sub("sudo",
                                    ("%s%ssudo%s" % (const.COLORS['BOLD'],
                                                     const.COLORS['RED'],
                                                     const.COLORS['ENDC'])),
                                    config_check.sudo_command)
        print(("The next configuration check requires elevated privileges; %s"
               "you may be prompted for your current OS X user's password "
               "below%s. The command to be executed is: '%s'") %
              (const.COLORS['BOLD'], const.COLORS['ENDC'],
               fancy_sudo_command))
        passed = _execute_check(config_check.sudo_command,
                                config_check.comparison_type,
                                config_check.expected,
                                config_check.case_sensitive)

    if passed or not quiet_fail:
        msg = ("\nCHECK #%d: %s... %s" % (glob_check_num,
                                        config_check.description,
                                        _get_result_str(passed)))
        print(msg)
        if const.WRITE_TO_LOG_FILE:
            log_to_file(msg)

    if not passed and last_attempt and do_warn(config_check):
        warn("Attempted fix %s" % const.FAILED_STR)

    return passed

def log_to_file(string):
    """Append string, followed by newline character, to log file.

    Color codes will be stripped out of the string non-destructively before
    writing.
    """
    string = re.sub(r"\033\[\d{1,2}m", "", string)
    log_file_loc = const.LOG_FILE_LOC
    if log_file_loc.startswith('~'):
        log_file_loc = expanduser(log_file_loc)
    with open(log_file_loc, 'a+') as log_file:
        log_file.write("%s\n" % string)

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
        print(("\tAttempting configuration fix with elevated privileges; %syou "
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
    global glob_check_num

    _print_banner()

    config_checks = read_config(const.DEFAULT_CONFIG_FILE)
    completely_failed_tests = []
    for config_check in config_checks:
        if not run_check(config_check):
            #config failed check
            if config_check.fix is None and config_check.sudo_fix is None:
                #no automatic fix available
                if config_check.manual_fix is not None:
                    completely_failed_tests.append(glob_check_num)
                else:
                    dprint(("Could not satisfy test #%d but no manual fix "
                            "specified.") % glob_check_num)
            else:
                #attempt fix, but prompt user first if appropriate
                if const.PROMPT_FOR_FIXES:
                    prompt_default = True
                    descriptor = ''
                    if config_check.confidence == Confidence.recommended:
                        prompt_default = const.FIX_RECOMMENDED_BY_DEFAULT
                        descriptor = const.RECOMMENDED_STR + ' '
                    elif config_check.confidence == Confidence.experimental:
                        prompt_default = const.FIX_EXPERIMENTAL_BY_DEFAULT
                        descriptor = const.EXPERIMENTAL_STR + ' '
                    question = (("\tApply the following %s fix? This will "
                                 "execute  this command:\n\t\t'%s'") %
                                (descriptor, config_check.fix))
                    if prompt.query_yes_no(question=question,
                                           default=_bool_to_yes_no(prompt_default)):
                        fixed = do_fix_and_test(config_check)
                        dprint("Value of fixed is: %s" % str(fixed))
                        if not fixed:
                            if config_check.manual_fix is not None:
                                completely_failed_tests.append(glob_check_num)
                            else:
                                dprint(("Could not satisfy test #%d but no "
                                        "manual fix specified.") %
                                       glob_check_num)
                else:
                    fixed = do_fix_and_test(config_check)
                    dprint("Value of fixed is: %s" % str(fixed))
                    if not fixed:
                        if config_check.manual_fix is not None:
                            completely_failed_tests.append(glob_check_num)
                        else:
                            dprint(("Could not satisfy test #%d but no manual "
                                    "fix specified.") % glob_check_num)

        glob_check_num += 1

    if const.WRITE_TO_LOG_FILE:
        print("Wrote results to %s'%s'%s." %
              (const.COLORS['BOLD'], const.LOG_FILE_LOC, const.COLORS['ENDC']))

    if len(completely_failed_tests) > 0:
        print("==========================")
        print(("%s%d tests could not be automatically fixed, but manual "
               "instructions are available. Please manually remediate these "
               "problems and re-run the tool:%s") %
              (const.COLORS['BOLD'], len(completely_failed_tests),
               const.COLORS['ENDC']))
        for test_num in completely_failed_tests:
            description = config_checks[test_num - 1].description
            instructions = config_checks[test_num - 1].manual_fix
            print("TEST #%d: %s" % (test_num, description))
            print("%s" % _underline_hyperlink(instructions))
            print("==========================")
    else:
        dprint("List of completely failed tests is empty.")

def _underline_hyperlink(string):
    """Insert underlines into hyperlinks"""
    return re.sub(
        r"(https?://[^ ]+)",
        (r"%s\1%s" % (const.COLORS['UNDERLINE'], const.COLORS['ENDC'])),
        string,
        flags=re.IGNORECASE)

def _bool_to_yes_no(boolean):
    return 'yes' if boolean else 'no'

def dprint(msg):
    """Debug print statements."""
    if const.ENABLE_DEBUG_PRINT:
        print("DEBUG: %s" % msg)


def is_match(regex, string, ignore_case=False):
    """Check if regex matches string."""
    regex_flags = re.DOTALL
    if ignore_case:
        regex_flags = re.DOTALL | re.IGNORECASE

    return re.match(regex, string, regex_flags) is not None

def _print_banner():
    banner = (("---------------------------------------------------------------"
               "---------------------------\n"
               "%s%sosx-config-check%s\n"
               "Download the latest copy of this tool at: "
               "https://github.com/kristovatlas/osx-config-check \n"
               "Report bugs/issues:\n"
               "\t* GitHub: "
               "https://github.com/kristovatlas/osx-config-check/issues \n"
               "\t* Twitter: https://twitter.com/kristovatlas \n"
               "---------------------------------------------------------------"
               "---------------------------\n") %
              (const.COLORS['BOLD'], const.COLORS['OKBLUE'],
               const.COLORS['ENDC']))
    print(_underline_hyperlink(banner))


if __name__ == "__main__":
    main()
