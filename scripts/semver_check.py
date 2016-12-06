"""Verifies that the output of a command contains a compatible semver string.

Currently this can only support a limited subset of semantic version strings,
e.g.:
 * "git version 2.10.2"
 * "curl 7.50.1 (x86_64-apple-darwin15.6.0) libcurl/7.50.1 SecureTransport zlib/1.2.5"
 * "java version "1.8.0_102""
 * "OpenSSL 1.0.2h  3 May 2016"

The script aspires to be fully semver 2.0.0 compliant in the future. See:
http://semver.org/

The command that is piped to this script via stdin must only return a matching
string once; otherwise, the first string that looks like a semver string using
the optional prefix string will be compared and subsequent ones will be ignored.

Usage:

    $ some command | python semver_check.py [--prefix "prefix string"] "semver pattern"

Examples:

    $ git --version | python semver_check.py --prefix "git version " ">=2.10.1"
    1

    $ git --version | python semver_check.py ">=2.10.3"
    0
"""
import sys
import os
import re

ENABLE_DEBUG_PRINT = False
SEMVER_PERMITTED_REGEX = r'(\>\=)?(\d+\w*\.\d+\w*\.\d+\w*)'
SEMVER_SEARCH_REGEX = r"(\d+\w*\.\d+\w*\.\d+\w*)"

def print_usage(err_msg=None):
    """Print usage string and exit"""
    if err_msg is not None:
        print "Error: %s" % err_msg
    print("Usage: $ some command | python semver_check.py [--prefix "
          "\"prefix string\"] \"semver pattern\"")
    sys.exit()


def _get_number_part(version_piece):
    matches = re.search(r'(\d+)', version_piece)
    if matches is None:
        raise ValueError
    else:
        return int(matches.groups(1)[0])


def _get_alpha_part(version_piece):
    """Returns the alphabetical portion of version piece with exception*.

    Exception*: If the alphabetical portion matches an underscore followed by
    digits, then this will instead be cast to int and returned to ensure proper
    comparison by the caller. This accounts for version strings such as those
    used by Java, e.g. version "1.0.0_1" is less than "1.0.0_10"

    Returns: str or int
    """
    matches = re.search(r'\d+(\w+)', version_piece)
    if matches is None:
        return ''
    else:
        alpha = matches.groups(1)[0]
        matches2 = re.search(r'_(\d+)', alpha)
        if matches2 is not None:
            return int(matches2.groups(1)[0])
        else:
            return alpha

def does_str_match_semver(subject_str, semver_str, gr_or_eq=False):
    """Returns True if subject matches semver.
    Args:
        subject_str (str): The subject we're scrutinizing.
        semver_str (str): The semver we're testing against the subject.
        gr_pr_eq (bool): If set, the subject can be equal to or greater than
            the specified semver.
    """
    dprint("Comparing subject '%s' with semver '%s'" % (subject_str, semver_str))
    subject_pieces = subject_str.split('.')
    semver_pieces = semver_str.split('.')

    for cur_index, subject_piece in enumerate(subject_pieces):
        semver_piece = semver_pieces[cur_index]

        subject_numbers = _get_number_part(subject_piece)
        semver_numbers = _get_number_part(semver_piece)

        subject_alpha = _get_alpha_part(subject_piece)
        semver_alpha = _get_alpha_part(semver_piece)

        if gr_or_eq:
            if (subject_numbers > semver_numbers and
                    subject_alpha >= semver_alpha):
                #Strictly greater version, no need to check subsequent pieces
                return True

            elif (subject_numbers == semver_numbers and
                  subject_alpha > semver_alpha):
                #Strictly greater version, no need to check subsequent pieces
                return True

            elif subject_numbers < semver_numbers:
                return False

            elif (subject_numbers == semver_numbers and
                  subject_alpha < semver_alpha):
                return False

        else:
            if (subject_numbers != semver_numbers or
                    subject_alpha != semver_alpha):
                return False

    return True


def get_stdin():
    """Returns stdin or exits if not available.

    See:
    http://stackoverflow.com/questions/13143218/how-do-i-avoid-processing-an-empty-stdin-with-python
    """
    if os.fstat(sys.stdin.fileno()).st_size > 0:
        return sys.stdin.readlines()
    else:
        print_usage("No command output provided via stdin.")


def get_args():
    """Get command-line arguments or exit with usage string."""
    args = {}
    if len(sys.argv) == 2:
        args['semver'] = sys.argv[1]
    elif len(sys.argv) == 4:
        args['prefix'] = sys.argv[2]
        args['semver'] = sys.argv[3]
    else:
        print_usage("Wrong number of command-line arguments.")

    dprint(args)

    return args


def is_match(stdin=None, args=None):
    """Returns as bool whether stdin is a match for specified semver."""
    if stdin is None:
        stdin = get_stdin()
    if args is None:
        args = get_args()

    dprint("stdin='%s' type='%s'" % (str(stdin), str(type(stdin))))

    semver_matches = re.match(SEMVER_PERMITTED_REGEX, args['semver'])
    gr_or_eq = False
    if semver_matches is None:
        dprint("Semver: '%s'" % args['semver'])
        print_usage("Invalid semver pattern.")
    else:
        gr_or_eq = (semver_matches.group(1) != None)

    #find a semver-looking string in stdin
    search_regex = SEMVER_SEARCH_REGEX
    if 'prefix' in args:
        search_regex = r'%s%s' % (re.escape(args['prefix']), search_regex)
    dprint("search_regex = '%s'" % search_regex)

    for index, line in enumerate(stdin):
        matches = re.search(search_regex, line)
        if matches is not None:
            dprint("Line #%d matches the search_regex: '%s'" % (index + 1, line))
            subject_str = matches.group(1)
            return does_str_match_semver(subject_str, args['semver'], gr_or_eq)

    #Never found the string we were looking for
    return False

def dprint(data):
    """Print debug information."""
    if ENABLE_DEBUG_PRINT:
        print "DEBUG: %s" % str(data)

if __name__ == '__main__':
    print "1" if is_match() else "0"
