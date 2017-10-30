#!/usr/bin/env python
"""Checks the configuration of various osx options."""

import sys
import time
import datetime
from os.path import expanduser
import re
from subprocess import Popen, PIPE, STDOUT
from warnings import warn
import json
import const #const.py
import prompt #prompt.py

const.DEFAULT_OUTPUT_LOCATION = "~/Documents/"
const.DEFAULT_CONFIG_FILE = "osx-config.json"
const.WARN_FOR_RECOMMENDED = True #TODO: command line flag
const.WARN_FOR_EXPERIMENTAL = True #TODO: command line flag
const.FIX_RECOMMENDED_BY_DEFAULT = True #TODO: command line flag
const.FIX_EXPERIMENTAL_BY_DEFAULT = False #TODO: command line flag
const.LOG_DEBUG_ALWAYS = True #TODO: command line flag

const.VERSION = "v1.1.0 (ivysaur)"

const.API_FILENAME = './scripts/api.sh'

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
const.SKIPPED_STR = const.COLORS['OKBLUE'] + "SKIPPED!" + const.COLORS['ENDC']
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

const.SUDO_STR = ("%s%ssudo%s" %
                  (const.COLORS['BOLD'], const.COLORS['RED'],
                   const.COLORS['ENDC']))

def get_timestamp():
    """Genereate a current timestamp that won't break a filename."""
    timestamp_format = '%Y-%m-%d_%H-%M-%S'
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime(timestamp_format)
    return timestamp

const.LOG_FILE_NAME = 'osx-config-check_%s.log' % get_timestamp()
const.LOG_FILE_LOC = const.DEFAULT_OUTPUT_LOCATION + const.LOG_FILE_NAME

glob_check_num = 1

#counters
glob_pass_no_fix = 0
glob_pass_after_fix = 0
glob_fail_fix_fail = 0
glob_fail_fix_skipped = 0
glob_fail_fix_declined = 0
glob_check_skipped = 0

class CheckResult(object):
    """Each test can have one of three results, informing the next step."""
    explicit_pass = 1
    explicit_fail = 2
    no_pass = 3
    all_skipped = 4

def check_result_to_str(val):
    """Convert enum to string representation"""
    if val == CheckResult.explicit_pass:
        return const.PASSED_STR
    elif val == CheckResult.explicit_fail:
        return const.FAILED_STR
    elif val == CheckResult.no_pass:
        return const.FAILED_STR
    elif val == CheckResult.all_skipped:
        return const.SKIPPED_STR
    else:
        raise ValueError

class Confidence(object):
    """Likelihood that a configuration will create negative side-effects.

    A lower integer value indicates less likelihood that a configuration will
    cause problems with applications.
    """
    required = 1
    recommended = 2
    experimental = 3

class ConfigCheck(object):
    """Encapsulates configuration to check in operating system."""
    def __init__(self, tests, description, confidence, fix=None, sudo_fix=None,
                 manual_fix=None):
        """
        Args:

            tests (List[dict]): The ordered list of tests to be performed, each
                a `dict` with these attributes including command_pass and/or
                command_fail:
                    * type (str): "exact match" or "regex match"
                    * command (str)
                    * command_pass (Optional[str])
                    * command_fail (Optional[str])
                    * case_sensitive (bool)
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
        """
        assert isinstance(tests, list)
        assert len(tests) > 0
        for test in tests:
            assert isinstance(test, dict), "%s" % str(test)
            assert test['type'] in ('exact match', 'regex match')
            assert 'command' in test
            assert 'command_pass' in test or 'command_fail' in test
            test['case_sensitive'] = bool(test['case_sensitive'])
        self.tests = tests

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

        #Config MUST specify a description of the check
        description = config_check['description']
        write_str("Description: %s" % description, debug=True)

        #Config MUST indicate the confidence of the configuration check
        confidence = config_check['confidence']

        #Config MUST include at least one test obj
        tests = config_check['tests']

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

        config_check_obj = ConfigCheck(
            tests=tests,
            description=description,
            confidence=confidence,
            fix=fix,
            sudo_fix=sudo_fix,
            manual_fix=manual_fix)
        config_checks.append(config_check_obj)

    return config_checks

def run_check(config_check, last_attempt=False, quiet_fail=False):
    """Perform the specified configuration check against the OS.

    Each config check may specify multiple test cases with early-succeed and/or
    early-fail parameters.

    These are the possible conditions resulting from run_check:
    1. One of the tests explicitly passed.
    2. One of the tests explicitly failed.
    3. All of the tests were run and none of them passed or failed. (This
        should be considered a fail.)
    4. All of the tests were skipped because we're skipping sudo checks and
        the only tests available require sudo privs.

    Args:
        config_check (`ConfigCheck`): The check to perform. May contain multiple
            commands to test.
        last_attempt (bool): Is this the last time the script checks this
            configuration, or will we check again during this run?
        quiet_fail (bool): Suppress print failed results to stdout?
            Default: False.

    Returns: `CheckResult`: The check explicitly passed, explicitly
        failed, never passed, or all checks were skipped.

    Raises: ValueError if result of _execute_check is not valid.
    """
    assert isinstance(config_check, ConfigCheck)

    #Assume all tests have been skipped until demonstrated otherwise.
    result = CheckResult.all_skipped
    for test in config_check.tests:
        #alert user if he might get prompted for admin privs due to sudo use
        if 'sudo ' in test['command']:
            if const.SKIP_SUDO_TESTS:
                write_str("Skipping test because app skipping sudo tests.",
                          debug=True)
            else:
                fancy_sudo_command = re.sub(
                    "sudo", const.SUDO_STR, test['command'])
                write_str(("The next configuration check requires elevated "
                           "privileges; %syou may be prompted for your current "
                           "OS X user's password  below%s. The command to be "
                           "executed is: '%s'") %
                          (const.COLORS['BOLD'], const.COLORS['ENDC'],
                           fancy_sudo_command))

        if 'sudo ' not in test['command'] or not const.SKIP_SUDO_TESTS:
            command_pass = None
            if 'command_pass' in test:
                command_pass = str(test['command_pass'])
            command_fail = None
            if 'command_fail' in test:
                command_fail = str(test['command_fail'])
            result = _execute_check(command=test['command'],
                                    comparison_type=test['type'],
                                    case_sensitive=test['case_sensitive'],
                                    command_pass=command_pass,
                                    command_fail=command_fail)
            if result == CheckResult.explicit_pass:
                write_str("Test passed exlicitly for '%s'" % test['command'],
                          debug=True)
                break
            elif result == CheckResult.explicit_fail:
                write_str("Test failed exlicitly for '%s'" % test['command'],
                          debug=True)
                break
            elif result == CheckResult.no_pass:
                write_str("Test did not pass for '%s'" % test['command'],
                          debug=True)
                continue
            else:
                raise ValueError("Invalid return value from _execute_check.")

    if result == CheckResult.explicit_pass or not quiet_fail:
        write_str("\nCHECK #%d: %s... %s" % (glob_check_num,
                                             config_check.description,
                                             check_result_to_str(result)))

    if (result not in (CheckResult.explicit_pass, CheckResult.all_skipped) and
            last_attempt and do_warn(config_check)):
        warn("Attempted fix %s" % const.FAILED_STR)

    return result

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

def _execute_check(command, comparison_type, case_sensitive, command_pass=None,
                   command_fail=None):
    """Helper function for `run_check` -- executes command and checks result.

    This check can result in three conditions:
    1. The check explicitly passed, and no subsequent tests need to be performed
        for this check. Returns True.
    2. The check explicitly failed, and no subsequent tests need to be performed
        for this check. Raises ConfigCheckFailedExplicitly.
    3. The check produced another result, and if there is another test
        available, it

    Args:
        command (str): The command to execute to perform the check.
        comparison_type (str): 'exact match' or 'regex match'
        case_sensitive (bool): Whether the comparison to output is case
            sensitive.
        command_pass (str or None): The output of the command which constitutes
            an explicit pass for the test, either as an exact string or regex
            depending on `comparison_type`.
        command_fail (str or None): The output of the command which constitutes
            an explicit fail for the test, either as an exact string or regex
            depending on `comparison_type`.

    Returns:
       `CheckResult`: explicit pass, explicit failure, or lacking of passing for
            this test only.

    Raises:
        ValueError if `comparison_type` is not an expected value
    """
    #http://stackoverflow.com/questions/7129107/python-how-to-suppress-the-output-of-os-system
    command = "source %s ; %s" % (const.API_FILENAME, command)
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    stdout, _ = process.communicate()

    stdout = stdout.strip().decode(encoding='UTF-8')

    write_str("Command executed to check config: '%s'" % str(command),
              debug=True)
    write_str("Result of command: '%s'" % str(stdout), debug=True)
    write_str("Explicit pass condition for command: '%s'" % str(command_pass),
              debug=True)
    write_str("Explicit fail condition for command: '%s'" % str(command_fail),
              debug=True)

    if comparison_type == 'exact match':
        if case_sensitive:
            if command_fail is not None and stdout == command_fail:
                return CheckResult.explicit_fail
            if command_pass is not None and stdout == command_pass:
                return CheckResult.explicit_pass
            else:
                return CheckResult.no_pass
        else:
            if (command_fail is not None and
                    stdout.lower() == str(command_fail.lower())):
                return CheckResult.explicit_fail
            if (command_pass is not None and
                    stdout.lower() == str(command_pass).lower()):
                return CheckResult.explicit_pass
            else:
                return CheckResult.no_pass
    elif comparison_type == 'regex match':
        ignore_case = not case_sensitive
        if (command_fail is not None and
                is_match(command_fail, stdout, ignore_case=ignore_case)):
            return CheckResult.explicit_fail
        if (command_pass is not None and
                is_match(command_pass, stdout, ignore_case=ignore_case)):
            return CheckResult.explicit_pass
        else:
            return CheckResult.no_pass
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
        write_str(("\tAttempting configuration fix with elevated privileges; %s"
                   "you may be prompted for your OS X login password%s...") %
                  (const.COLORS['BOLD'], const.COLORS['ENDC']))
    stdoutdata = ""
    stderrdata = ""
    if command is not None:
        command = "source %s ; %s" % (const.API_FILENAME, command)
        process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        stdoutdata, stderrdata = process.communicate()

    write_str("Command executed: '%s'" % str(command), debug=True)
    write_str("Command STDOUT: '%s'" % str(stdoutdata), debug=True)
    write_str("Command STDERR: '%s'" % str(stderrdata), debug=True)

def do_fix_and_test(config_check):
    """Attempt to fix misconfiguration, returning the result.

    If a non-sudo fix is specified, this will be attempted first.
    If a non-sudo fix fails or there is none specified and a sudo fix is
    specified, this will be attempted next.
    If all previous attempts have failed or none have been specified and
    instructions for manually fixing the configuration have been specified,
    these will be printed out at the end of execution by another function.

    Args:
        config_check (`ConfigCheck`): The check to perform.

    Returns:
        bool: Whether an attempted fix was successful.
    """
    write_str("Entered do_fix_and_test()", debug=True)

    if config_check.fix is not None:
        _try_fix(config_check, use_sudo=False)
        check_result = run_check(
            config_check, last_attempt=False, quiet_fail=True)
        if check_result == CheckResult.explicit_pass:
            return True

    if config_check.sudo_fix is not None:
        _try_fix(config_check, use_sudo=True)
        check_result = run_check(
            config_check, last_attempt=True, quiet_fail=False)
        return bool(check_result == CheckResult.explicit_pass)
    else:
        return False

def dprint_settings():
    """Prints current global flags when debug printing is enabled."""
    write_str("ENABLE_DEBUG_PRINT: %s" % str(const.ENABLE_DEBUG_PRINT),
              debug=True)
    write_str("WRITE_TO_LOG_FILE: %s" % str(const.WRITE_TO_LOG_FILE),
              debug=True)
    write_str("PROMPT_FOR_FIXES: %s" % str(const.PROMPT_FOR_FIXES), debug=True)
    write_str("ATTEMPT_FIXES: %s" % str(const.ATTEMPT_FIXES), debug=True)
    write_str("SKIP_SUDO_TESTS: %s" % str(const.SKIP_SUDO_TESTS), debug=True)

def main():
    """Main function."""
    global glob_check_num, glob_fail_fix_declined, glob_pass_after_fix, \
           glob_fail_fix_fail, glob_fail_fix_skipped, glob_pass_no_fix, \
           glob_check_skipped

    args = get_sys_args()
    const.ENABLE_DEBUG_PRINT = args['debug-print']
    const.WRITE_TO_LOG_FILE = args['write-to-log-file']
    const.PROMPT_FOR_FIXES = not args['no-prompt']
    const.ATTEMPT_FIXES = not args['report-only']
    const.SKIP_SUDO_TESTS = args['skip-sudo-checks']

    dprint_settings()

    _print_banner()

    config_checks = read_config(const.DEFAULT_CONFIG_FILE)
    completely_failed_tests = []
    for config_check in config_checks:
        check_result = run_check(config_check)
        if check_result in (CheckResult.explicit_fail, CheckResult.no_pass):
            if not const.ATTEMPT_FIXES:
                #report-only mode
                glob_fail_fix_skipped += 1
                glob_check_num += 1
                continue

            if config_check.fix is None and config_check.sudo_fix is None:
                #no automatic fix available
                if config_check.manual_fix is not None:
                    completely_failed_tests.append(glob_check_num)
                else:
                    write_str(("Could not satisfy test #%d but no manual fix "
                               "specified.") % glob_check_num, debug=True)
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

                    next_fix_command = config_check.fix
                    if next_fix_command is None:
                        next_fix_command = config_check.sudo_fix

                    question = (("\tApply the following %s fix? This will "
                                 "execute  this command:\n\t\t'%s'") %
                                (descriptor, next_fix_command))
                    if prompt.query_yes_no(question=question,
                                           default=_bool_to_yes_no(prompt_default)):
                        fixed = do_fix_and_test(config_check)
                        write_str("Value of fixed is: %s" % str(fixed),
                                  debug=True)
                        if fixed:
                            glob_pass_after_fix += 1
                        else:
                            glob_fail_fix_fail += 1
                            if config_check.manual_fix is not None:
                                completely_failed_tests.append(glob_check_num)
                            else:
                                write_str(("Could not satisfy test #%d but no "
                                           "manual fix specified.") %
                                          glob_check_num, debug=True)
                    else:
                        #user declined fix
                        glob_fail_fix_declined += 1
                else:
                    fixed = do_fix_and_test(config_check)
                    write_str("Value of fixed is: %s" % str(fixed), debug=True)
                    if fixed:
                        glob_pass_after_fix += 1
                    else:
                        glob_fail_fix_fail += 1
                        if config_check.manual_fix is not None:
                            completely_failed_tests.append(glob_check_num)
                        else:
                            write_str(("Could not satisfy test #%d but no "
                                       "manual fix specified.") %
                                      glob_check_num, debug=True)

        elif check_result == CheckResult.explicit_pass:
            glob_pass_no_fix += 1
        elif check_result == CheckResult.all_skipped:
            glob_check_skipped += 1

        glob_check_num += 1

    print_tallies()

    if len(completely_failed_tests) > 0:
        write_str("==========================")
        write_str(("%s%d tests could not be automatically fixed, but manual "
                   "instructions are available. Please manually remediate these"
                   " problems and re-run the tool:%s") %
                  (const.COLORS['BOLD'], len(completely_failed_tests),
                   const.COLORS['ENDC']))
        for test_num in completely_failed_tests:
            description = config_checks[test_num - 1].description
            instructions = config_checks[test_num - 1].manual_fix
            write_str("TEST #%d: %s" % (test_num, description))
            write_str("%s" % _underline_hyperlink(instructions))
            write_str("==========================")
    else:
        write_str("List of completely failed tests is empty.", debug=True)

    if const.WRITE_TO_LOG_FILE:
        print("Wrote results to %s'%s'%s. Please review the contents before "
              "submitting them to third parties, as they may contain sensitive "
              "information about your system." %
              (const.COLORS['BOLD'], const.LOG_FILE_LOC, const.COLORS['ENDC']))

def _underline_hyperlink(string):
    """Insert underlines into hyperlinks"""
    return re.sub(
        r"(https?://[^ ]+)",
        (r"%s\1%s" % (const.COLORS['UNDERLINE'], const.COLORS['ENDC'])),
        string,
        flags=re.IGNORECASE)

def _bool_to_yes_no(boolean):
    return 'yes' if boolean else 'no'


def write_str(msg, debug=False):
    """Print and logs the specified message unless prohibited by settings.

    Args:
        msg (str): The message to be written.
        debug (bool): Whether the message is normal or debug-only info.
            Default: False
    """
    if debug:
        dprint(msg)
        if ((const.ENABLE_DEBUG_PRINT or const.LOG_DEBUG_ALWAYS) and
                const.WRITE_TO_LOG_FILE):
            log_to_file("DEBUG: %s" % msg)
    else:
        print("%s" % msg)
        if const.WRITE_TO_LOG_FILE:
            log_to_file(msg)

def dprint(msg):
    """Print debug statements."""
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
               "%s%sosx-config-check%s %s\n"
               "Download the latest copy of this tool at: "
               "https://github.com/kristovatlas/osx-config-check \n"
               "Report bugs/issues:\n"
               "\t* GitHub: "
               "https://github.com/kristovatlas/osx-config-check/issues \n"
               "\t* Twitter: https://twitter.com/kristovatlas \n"
               "---------------------------------------------------------------"
               "---------------------------\n") %
              (const.COLORS['BOLD'], const.COLORS['OKBLUE'],
               const.COLORS['ENDC'], const.VERSION))
    write_str(_underline_hyperlink(banner))

def print_usage():
    """Prints usage for this command-line tool and exits."""
    print("Usage: python app.py [OPTIONS]\n"
          "OPTIONS:\n"
          "\t--debug-print        Enables verbose output for debugging the "
          "tool.\n"
          "\t--report-only        Only reports on compliance and does not "
          "offer to fix broken configurations.\n"
          "\t--disable-logs       Refrain from creating a log file with the "
          "results.\n"
          "\t--disable-prompt     Refrain from prompting user before applying "
          "fixes.\n"
          "\t--skip-sudo-checks   Do not perform checks that require sudo "
          "privileges.\n"
          "\t--help -h            Print this usage information.\n")
    sys.exit()

def print_tallies():
    """Prints totals of the various possible outcomes of config checks."""
    total_checks = glob_check_num - 1
    total_passed = glob_pass_no_fix + glob_pass_after_fix
    total_failed = (glob_fail_fix_fail + glob_fail_fix_skipped +
                    glob_fail_fix_declined + glob_check_skipped)

    out = trim_block('''
    Configurations passed total:                 %s
    Configurations failed or skipped total:      %s
    Configurations passed without applying fix:  %s
    Configurations passed after applying fix:    %s
    Configurations failed and fix failed:        %s
    Configurations failed and fix skipped:       %s
    Configurations failed and fix declined:      %s
    Configuration checks skipped:                %s
    ''' % (_number_and_pct(total_passed, total_checks, 'pass'),
           _number_and_pct(total_failed, total_checks, 'fail'),
           _number_and_pct(glob_pass_no_fix, total_checks, 'pass'),
           _number_and_pct(glob_pass_after_fix, total_checks, 'pass'),
           _number_and_pct(glob_fail_fix_fail, total_checks, 'fail'),
           _number_and_pct(glob_fail_fix_skipped, total_checks, 'fail'),
           _number_and_pct(glob_fail_fix_declined, total_checks, 'fail'),
           _number_and_pct(glob_check_skipped, total_checks, 'skip')))

    write_str(out)

def _number_and_pct(num, total, result):
    assert result in ('pass', 'fail', 'skip')
    if result == 'pass':
        color = const.COLORS['OKGREEN']
    elif result == 'fail':
        color = const.COLORS['FAIL']
    elif result == 'skip':
        color = const.COLORS['OKBLUE']
    end_color = '' if color == '' else const.COLORS['ENDC']
    return "%s%d (%s)%s" % (color, num, _pct(num, total), end_color)

def _pct(num, total):
    return "{0:.2f}".format(100.0 * num / total) + '%'

def trim_block(multiline_str):
    """Remove empty lines and leading whitespace"""
    result = ""
    for line in multiline_str.split("\n"):
        line = line.lstrip()
        if line != '':
            result += "%s\n" % line
    return result.rstrip() #remove trailing newline

def get_sys_args():
    """Parses command line args, setting defaults where not specified.

    Returns: dict:
        * debug-print (bool)
        * report-only (bool)
        * write-to-log-file (bool)
        * no-prompt (bool)
        * skip-sudo-checks (bool)
    """
    args = {'debug-print': False,
            'report-only': False,
            'write-to-log-file': True,
            'no-prompt': False,
            'skip-sudo-checks': False}
    unprocessed_args = sys.argv[1:]
    while len(unprocessed_args) > 0:
        flag = unprocessed_args.pop(0)
        if flag == '--debug-print':
            args['debug-print'] = True
        elif flag == '--report-only':
            args['report-only'] = True
        elif flag == '--disable-logs':
            args['write-to-log-file'] = False
        elif flag == '--disable-prompt':
            args['no-prompt'] = True
        elif flag == '--skip-sudo-checks':
            args['skip-sudo-checks'] = True
        elif flag == '-h' or flag == '--help':
            print_usage()
        else:
            print("ERROR: Unrecognized option '%s'" % flag)
            print_usage()

    return args

if __name__ == "__main__":
    main()
