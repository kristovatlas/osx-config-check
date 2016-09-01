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

function apple_mail_in_use {
    #I use "ls" here to resolve the "~" symbol to the fully qualified file path
    #that "test" requires.
    IN_USE=$(ls ~/Library/Preferences/com.apple.mail-shared.plist)
    if [ -e $IN_USE ]; then
        echo 1
    else
        echo 0
    fi
}

function gpg_mail_in_use {
    #I use "ls" here to resolve the "~" symbol to the fully qualified file path
    #that "test" requires.
    IN_USE=$(ls ~/Library/Preferences/org.gpgtools.gpgmail.plist)
    if [ -e $IN_USE ]; then
        echo 1
    else
        echo 0
    fi
}

function is_el_capitan {
    #Detects whether this system is El Capitan
    SW_VERSION=$(sw_vers -productVersion)
    if [[ $SW_VERSION =~ 10.11.[0-9]+ ]] ; then
        echo 1
    else
        echo 0
    fi
}

function does_defaults_domain_exist {
    DOMAIN=$1
    READ_VAL=$(defaults read $DOMAIN 2>&1 | tail -n 1 )
    if [[ $READ_VAL =~ "Domain $DOMAIN does not exist" ]]; then
        echo 0
    else
        echo 1
    fi
}
export -f does_defaults_domain_exist

function defaults_write_ignore_missing {
    #Usage: defaults_write_ignore_missing mydomain key -type value
    #e.g.: defaults_write_ignore_missing com.apple.NetworkBrowser DisableAirDrop -bool true
    #Writes to the specified domain using the 'defaults' utility, but will
    #initialize the domain with a blank plist value if the domain does not
    #already exist.
    DOMAIN=$1
    KEY=$2
    DATA_TYPE=$3
    VAL=$4

    DOMAIN_EXISTS=$(does_defaults_domain_exist $DOMAIN)
    if [ "$DOMAIN_EXISTS" = "0" ]; then
        defaults write $DOMAIN '{"osxconfig-reserved" = 1;}'
        DOMAIN_EXISTS=$(does_defaults_domain_exist $DOMAIN)
        if [ "$DOMAIN_EXISTS" = "0" ]; then
            echo "Could not successfully create the specified domain."
            exit
        fi
    fi
    defaults write $DOMAIN $KEY $DATA_TYPE $VAL
}
