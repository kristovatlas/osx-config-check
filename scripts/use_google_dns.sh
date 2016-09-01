#!/bin/bash
# Description: Sets all network interfaces to use Google DNS servers, but only
# for the network interfaces that are not compliant.

function non_google_dns {
    INTERFACE=$1
    if [ "$INTERFACE" = "An asterisk (*) denotes that a network service is disabled." ]; then
        echo 0
    else
        DNS=$(networksetup -getdnsservers "$INTERFACE" | tr -d "\n")
        if [ "$DNS" != "8.8.8.88.8.4.4" ]; then
            echo 1
        else
            echo 0
        fi
    fi
}
export -f non_google_dns

function set_google_dns {
    INTERFACE=$1
    sudo networksetup -setdnsservers "$INTERFACE" 8.8.8.8 8.8.4.4
}
export -f set_google_dns


function process {
    INTERFACE=$1
    IS_NON_GOOGLE_DNS=$(non_google_dns "$INTERFACE")
    if [ "$IS_NON_GOOGLE_DNS" = "1" ]; then
        set_google_dns "$INTERFACE"
    fi
}
export -f process

networksetup listallnetworkservices | xargs -I{} bash -c 'process "{}"'
