#!/bin/bash
# Description: Contains functions that serve as an API for osx-config-check and
# which maximize code reuse of bash script.
# All functions added to this file should be simple and easy to review for
# security.

# Other bash scripts can use these functions by sourcing this file and invoking
# the functions as if they were commands. Example:
# source ./scripts/api.sh ; if [ $(homebrew_is_installed) = "1" ] ; then echo "pass" ; else echo "fail" ; fi
# OR
# source ./scripts/api.sh ; echo $(homebrew_is_installed)

function homebrew_is_installed {
    TEST=$(which brew)
    if [ -n "$TEST" ] ; then
        TEST=$(brew --version | grep Homebrew)
        if [ -n "$TEST" ] ;  then
            echo 1
        else
            echo 0
        fi
    else
        echo 0
    fi
}
