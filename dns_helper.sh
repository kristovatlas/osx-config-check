#!/bin/bash
#Author: Kristov Atlas https://github.com/kristovatlas/osx-config-check
#Description: Helps user temporarily return to automatic DNS configuration in
#order to resolve problems connecting to wi-fi active portals that use their own
#DNS servers.

#This uses the networksetup tool and requires sudo privs

STORED_DNS=''

function store_dns {
    #echo "DEBUG: entered store_dns"
    STORED_DNS=$(networksetup -getdnsservers Wi-Fi | tr -s "\n" " ")
    if [ "$STORED_DNS" = "There aren't any DNS Servers set on Wi-Fi. " ]; then
        echo "Oops! You already had DNS settings set to automatic. You're having some other kind of problem connecting to wi-fi. Try opening your browser and surfing to 'http://example' to bring up an active-portal login page."
        exit
    fi
    echo "(Your current DNS servers are '$STORED_DNS')"
}

function set_automatic_dns {
    #echo "DEBUG: entered set_automatic_dns."
    store_dns
    echo "Enter your OSX login password if prompted: "
    sudo networksetup -setdnsservers Wi-Fi "empty"
    
    NEW_VAL=$(networksetup -getdnsservers Wi-Fi)
    if [ "$NEW_VAL" = "There aren't any DNS Servers set on Wi-Fi." ]; then
        echo "Successfully changed DNS settings to automatic."
    else
        echo "Oops! There may have been a problem setting DNS settings to automatic :("
    fi
    #echo "DEBUG: new DNS settings: '$NEW_VAL'"
}

function restore_dns {
    #echo "DEBUG: Entered restore_dns"
    echo "Enter your OSX login password if prompted: "
    sudo networksetup -setdnsservers Wi-Fi $STORED_DNS
    echo "DNS settings restored."
}

echo This program will help you temporarily restore automatic DNS settings when you\'re having trouble connecting to Wi-Fi networks.

valid_response=0
while [ $valid_response -eq 0 ] ; do
    read -r -p "Temporarily set DNS to automatic settings? [Y/n] " response
    response=$(perl -e "print lc('$response')")

    if [[ $response =~ ^(yes|y| ) ]]; then
        valid_response=1
        set_automatic_dns
    else
        if [[ $response =~ ^(no|n) ]]; then
            exit
        fi
    fi
done

read -r -p "You're now ready to connect to a Wi-Fi active portal. You may need to open a web browser and surf to 'http://example.com' to interact with the active portal. When you're done connecting, PRESS ENTER here to restore your original DNS settings."
restore_dns
