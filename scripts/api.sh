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

function chrome_is_installed {
    #detects whether Google Chrome is installed
    TEST=$(mdfind kMDItemCFBundleIdentifier = 'com.google.Chrome')
    if [ -n "$TEST" ] ; then
        echo 1
    else
        echo 0
    fi
}

function java_is_installed {
    #detects whether JRE/JDK is installed or osx's placeholder is sitting there,
    #waiting to annoy us with pop-up windows if 'java' is invoked
    JAVA_WHICH=$(which java)
    LINK=$(readlink "$JAVA_WHICH")
    if [ "$LINK" = "/System/Library/Frameworks/JavaVM.framework/Versions/Current/Commands/java" ] ; then
        #fake java binary
        echo 0
    else
        IS_JAVA=$(java -version 2>&1 >/dev/null | grep -c 'java version')
        if [ "$IS_JAVA" = "1" ] ; then
            echo 1
        else
            echo 0
        fi
    fi
}

function little_snitch_is_installed {
    RUNNING=$(pgrep "Little Snitch Daemon")
    if [ -n "$RUNNING" ]; then
        echo 1
    else
        echo 0
    fi
}
