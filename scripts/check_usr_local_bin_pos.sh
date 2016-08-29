#!/bin/bash
# Description: Checks the position of /usr/local/bin relative to /usr/bin/ in
# the $PATH environment variable. If /usr/bin/local is first, this will echo
# the value "1", otherwise it will echo "0"

UB_POS=$(echo $PATH | awk '{print index($1, "/usr/bin")}')
ULB_POS=$(echo $PATH | awk '{print index($1, "/usr/local/bin")}')

if [ "$ULB_POS" -eq "0" ] || [ "$ULB_POS" -gt "$UB_POS" ] ; then
    echo 0
else
    echo 1
fi
