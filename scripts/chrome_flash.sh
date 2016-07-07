#!/bin/bash
# Description: Patches Chrome "Preferences" file if needed. The setting for
# plugins.plugins_list appears to be set to "False" or "[]" sometimes rather
# than an arrray of objects, but we always want the latter. Once standardized,
# Shockwave Flash will be disabled.
#
# Usage: chrome_flash.sh location-of-preferences-file

# set working directory to the one containing this script so it can find other
# scripts.
cd "$(dirname "$0")"

FILE=$1

echo "DEBUG: FILE = $FILE"

if [ $# -ne 1 ] ; then
    echo "Usage: chrome_flash.sh location-of-preferences-file"
    exit
fi

#http://www.linuxjournal.com/content/return-values-bash-functions
function plugins_list_value {
    echo DEBUG: python chrome_defaults.py read "$FILE" plugins.plugins_list
    VALUE=$(python chrome_defaults.py read "$FILE" plugins.plugins_list)
    echo "$VALUE"
}

function is_list_missing {
    echo DEBUG: python chrome_defaults.py read "$FILE" plugins.plugins_list
    MISSING=$(python chrome_defaults.py read "$FILE" plugins.plugins_list | grep -c "The attribute 'plugins\.plugins_list' does not exist")
    echo "$MISSING"
}

#initialize
plugins_list_value
is_list_missing
if [ "$VALUE" = "False" ] || [ "$VALUE" = "[]" ] || [[ $MISSING = "1" ]] ; then
    python chrome_defaults.py delete "$FILE" plugins.plugins_list
    python chrome_defaults.py write "$FILE" plugins.plugins_list -json '[{"enabled": false, "version": "", "name": "Shockwave Flash"},{"enabled": false, "version": "", "name": "Adobe Flash Player"},{"enabled": false, "version": "", "name": "Native Client"},{"enabled": false, "version": "", "name": "Widevine Content Decryption Module"}]'
fi

#write correct value
echo DEBUG: python chrome_defaults.py write-array "$FILE" plugins.plugins_list enabled -bool false where name -string "Shockwave Flash"
python chrome_defaults.py write-array "$FILE" plugins.plugins_list enabled -bool false where name -string "Shockwave Flash"
python chrome_defaults.py write-array "$FILE" plugins.plugins_list enabled -bool false where name -string "Adobe Flash Player"
