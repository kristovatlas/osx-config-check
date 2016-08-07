#!/bin/bash
# Description: Checks various configuration settings related to the
#   "DestroyFVKeyOnStandby" setting.
# See: https://github.com/drduh/OS-X-Security-and-Privacy-Guide/issues/124
#
# Usage: DestroyFVKeyOnStandby_check.sh


VALUE1=$(pmset -g | grep -i "DestroyFVKeyOnStandby" | cut -f 3)
VALUE2=$(pmset -g | grep "hibernatemode" | cut -d " " -f 10)
VALUE3=$(pmset -g | grep "powernap" | cut -d " " -f 15)
VALUE4=$(pmset -g | grep "standby " | cut -d " " -f 16)
VALUE5=$(pmset -g | grep "standbydelay" | cut -d " " -f 11)
VALUE6=$(pmset -g | grep "autopoweroff " | cut -d " " -f 11)

if [ "$VALUE1" = "1" ] && [ "$VALUE2" = "25" ] && [ "$VALUE3" = "0" ] && [ "$VALUE4" = "0" ] && [ "$VALUE5" = "0" ] && [ "$VALUE6" = "0" ] ; then
    echo "1"
else
    echo "0"
fi
