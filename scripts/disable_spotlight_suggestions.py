#!/usr/bin/python
"""Disable information leaks to Apple in Safari and Spotlight.

Adapted from:
https://fix-macosx.com/fix-macosx.py
"""

import os
import sys
#pylint: disable=no-name-in-module
from Foundation import (NSMutableArray, NSMutableDictionary,
                        CFPreferencesSynchronize, CFPreferencesCopyValue,
                        CFPreferencesSetValue, kCFPreferencesCurrentUser,
                        kCFPreferencesAnyHost)

def is_spotlight_fixed():
    raise NotImplementedError #TODO

def is_safari_spotlight_fixed():
    raise NotImplementedError #TODO

def fix_spotlight():
    """Fix OSX Spotlight information leak."""
    disabled_items = set(["MENU_WEBSEARCH", "MENU_SPOTLIGHT_SUGGESTIONS"])
    required_item_keys = set(["enabled", "name"])
    bundle_id = "com.apple.Spotlight"
    pref_name = "orderedItems"
    default_value = [
        {'enabled' : True, 'name' : 'APPLICATIONS'},
        {'enabled' : False, 'name' : 'MENU_SPOTLIGHT_SUGGESTIONS'},
        {'enabled' : True, 'name' : 'MENU_CONVERSION'},
        {'enabled' : True, 'name' : 'MENU_EXPRESSION'},
        {'enabled' : True, 'name' : 'MENU_DEFINITION'},
        {'enabled' : True, 'name' : 'SYSTEM_PREFS'},
        {'enabled' : True, 'name' : 'DOCUMENTS'},
        {'enabled' : True, 'name' : 'DIRECTORIES'},
        {'enabled' : True, 'name' : 'PRESENTATIONS'},
        {'enabled' : True, 'name' : 'SPREADSHEETS'},
        {'enabled' : True, 'name' : 'PDF'},
        {'enabled' : True, 'name' : 'MESSAGES'},
        {'enabled' : True, 'name' : 'CONTACT'},
        {'enabled' : True, 'name' : 'EVENT_TODO'},
        {'enabled' : True, 'name' : 'IMAGES'},
        {'enabled' : True, 'name' : 'BOOKMARKS'},
        {'enabled' : True, 'name' : 'MUSIC'},
        {'enabled' : True, 'name' : 'MOVIES'},
        {'enabled' : True, 'name' : 'FONTS'},
        {'enabled' : True, 'name' : 'MENU_OTHER'},
        {'enabled' : False, 'name' : 'MENU_WEBSEARCH'}
    ]

    items = CFPreferencesCopyValue(
        pref_name, bundle_id, kCFPreferencesCurrentUser, kCFPreferencesAnyHost)
    new_items = None
    if items is None or len(items) is 0:
        # Actual preference values are populated on demand; if the user
        # hasn't previously configured Spotlight, the preference value
        # will be unavailable
        new_items = default_value
    else:
        new_items = NSMutableArray.new()
        for item in items:
            missing_keys = []
            for key in required_item_keys:
                if not item.has_key(key):
                    missing_keys.append(key)

            if len(missing_keys) != 0:
                print(("Preference item %s is missing expected keys (%s), "
                       "skipping") % (item, missing_keys))
                new_items.append(item)
                continue

            if item["name"] not in disabled_items:
                new_items.append(item)
                continue

            new_item = NSMutableDictionary.dictionaryWithDictionary_(item)
            new_item.setObject_forKey_(0, "enabled")
            new_items.append(new_item)

    CFPreferencesSetValue(pref_name, new_items, bundle_id,
                          kCFPreferencesCurrentUser, kCFPreferencesAnyHost)
    CFPreferencesSynchronize(bundle_id, kCFPreferencesCurrentUser,
                             kCFPreferencesAnyHost)

def fix_safari_spotlight():
    """Fix Safari information leak.

    Safari "Spotlight" respects the system-wide Spotlight privacy settings
    EXCEPT when it comes to submitting search metrics to Apple.

    To disable these metrics, we have to disable Safari's *seperate*
    "Spotlight Suggestions" setting, in addition to Spotlight's
    "Spotlight Suggestions".

    You'll be forgiven if you find this confusing.
    """
    bundle_id = "com.apple.Safari"
    pref_name = "UniversalSearchEnabled"
    CFPreferencesSetValue(pref_name, False, bundle_id,
                          kCFPreferencesCurrentUser, kCFPreferencesAnyHost)
    CFPreferencesSynchronize(bundle_id, kCFPreferencesCurrentUser,
                             kCFPreferencesAnyHost)

def main():
    """Main function."""
    # We only handle Yosemite's spotlight for now
    major_release = int(os.uname()[2].split(".")[0])
    if major_release < 14:
        print("Good news! This version of Mac OS X's Spotlight and Safari are not "
              "known to invade your privacy.")
        sys.exit(0)

    fix_spotlight()
    fix_safari_spotlight()
    print("All done. Make sure to log out (and back in) for the changes to "
          "take effect.")

if __name__ == "__main__":
    main()
