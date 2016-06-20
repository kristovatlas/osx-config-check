"""Reads and writes Google Chome preferences in OS X.

Based on the `defaults` utility for reading/writing PList files in OS X.

TODO: unit test me
"""

import sys
import json
from datetime import datetime
import shutil

def _main():
    (action, preferences_filename, chrome_property) = get_args()
    preferences_json = _get_json(preferences_filename)
    if action == 'read':
        if chrome_property is None:
            print "%s\n" % json.dumps(preferences_json, indent=4)
            sys.exit()
        else:
            value = get_json_field(
                preferences_json, chrome_property, preferences_filename)
            print "%s\n" % _normalize(value)
    else: #'write'
        #TODO
        _make_backup(preferences_filename)

def _normalize(obj):
    #http://stackoverflow.com/questions/18272066/easy-way-to-convert-a-unicode-list-to-a-list-containing-python-strings
    if isinstance(obj, unicode):
        return obj.encode('utf-8')
    elif isinstance(obj, dict):
        return dict((_normalize(k), _normalize(obj[k])) for k in obj)
    elif isinstance(obj, list):
        return list(_normalize(i) for i in obj)
    else:
        return obj

def get_json_field(json_obj, attribute_name, json_filename=None):
    """Retrieves a value from a JSON object (dict).
    Args:
        json_obj (dict): The JSON file to retrieve a value from.
        attribute_name (str): The attribute to look up. If there are nested
            structures expressed within the attribute_name, they should be
            separated by periods. Consequently, attribute names and nested
            names cannot contain periods.
        json_filename (Optional[str]): The name of the JSON file the attribute
            is read from. This will be included in error messages.
    """
    while '.' in attribute_name:
        attrib_as_list = attribute_name.split('.')
        attrib_name_single = attrib_as_list.pop(0)
        try:
            json_obj = json_obj[attrib_name_single]
        except KeyError:
            error_suffix = '.'
            if json_filename is not None:
                error_suffix = " '%s'." % json_filename
            print("Attribute '%s' not found in preferences file%s" %
                  (attrib_name_single, error_suffix))
        attribute_name = '.'.join(attrib_as_list) #no period included for len 1
    return json_obj[attribute_name]

def _get_json(filename):
    try:
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    except TypeError:
        sys.exit("No Google Chrome preferences file found at '%s'\n" % filename)

def get_args():
    """Reads command line arguments.
    Returns:
        tuple: action, preferences, chrome_property. If no chrome_property is
        specified by the user, this value is set to None.
    """
    if len(sys.argv) in (3, 4):
        action = sys.argv[1]
        if action in ('read', 'write'):
            preferences_filename = sys.argv[2]
            chrome_property = None
            if len(sys.argv) == 4:
                chrome_property = sys.argv[3]
            return (action, preferences_filename, chrome_property)

    print_usage()

def print_usage():
    """Prints syntax for usage and exits the program."""
    print("usage:\tpython chrome_defaults.py [read|write] "
          "google-chrome-preferences-file TODO]\n")
    sys.exit()

def _make_backup(filename):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    dest = "%s%s" % (filename, timestamp)
    shutil.copymode(filename, dest)

if __name__ == "__main__":
    _main()
