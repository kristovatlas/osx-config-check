"""Prompt user for yes/no answer to question.
From:
http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
"""

import sys

try:
    input = raw_input
except NameError:
    # In Python 2 there is raw_input() that takes a string from stdin and
    # input() that takes a string from stdin and evaluates it. That last
    # function is not very useful and has been removed in Python 3, while
    # raw_input() has been renamed to input()
    pass

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    Args:
        question (str): A string that is presented to the user.
        default (str): The presumed answer if the user just hits <Enter>. It
            must be "yes" (the default), "no" or None (meaning an answer is
            required of the user).

    Returns:
        (bool) True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
