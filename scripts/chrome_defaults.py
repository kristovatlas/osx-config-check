# -*- coding: utf-8 -*-
"""Reads and writes Google Chome preferences in OS X.

Based on the `defaults` utility for reading/writing PList files in OS X.

The two sub-commands currently supported are "read" and "write".

Nested attribute names of JSON objects are referred to using dot-notation, e.g.
"my.object.property"

If the user attempts to "write" to a property that does not currently exist, it
will be created. If the property is nested, a series of required JSON objects
will be created containing only the nested attribute names. For example, if the
user writes to "my.nonexistent.property" with the value 42, and the "my"
attribute does not exist at the top level, the following structure will be
created in the JSON:
{
    ...other attributes in the JSON
    "my": {
        "nonexistent": {
            "property": 42
        }
    }
}

Examples:

    $ python chrome_defaults.py read "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences"

    $ python chrome_defaults.py read "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" download.directory_upgrade

    $ python chrome_defaults.py write "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" download.directory_upgrade -bool true

Todo:
    * Unit tests
    * Add support for writing list values
    * Add support for writing null value
"""

import sys
import json
from datetime import datetime
import shutil
from copy import deepcopy
import re

UNDERLINE = '\033[4m'
ENDC = '\033[0m'

def _main():
    (action, preferences_filename, chrome_property, value) = get_args()
    preferences_json = _get_json(preferences_filename)
    if action == 'read':
        if chrome_property is None:
            print "%s" % json.dumps(preferences_json, indent=4)
            sys.exit()
        else:
            try:
                value = get_json_field(
                    preferences_json, chrome_property, preferences_filename)
                print "%s" % normalize(value)
            except KeyError:
                print("The attribute '%s' does not exist in '%s'." %
                      (chrome_property, preferences_filename))
    else: #'write'
        _make_backup(preferences_filename)
        new_json = write_json_field(preferences_json, chrome_property, value)

        with open(preferences_filename, 'w') as preferences_file:
            preferences_file.write(json.dumps(new_json))

def normalize(obj):
    """Recursively normalizes `unicode` data into utf-8 encoded `str`.
    http://stackoverflow.com/questions/18272066/easy-way-to-convert-a-unicode-list-to-a-list-containing-python-strings
    """
    if isinstance(obj, unicode):
        return obj.encode('utf-8')
    elif isinstance(obj, dict):
        return dict((normalize(key), normalize(obj[key])) for key in obj)
    elif isinstance(obj, list):
        return list(normalize(item) for item in obj)
    else:
        return obj

def write_json_field(json_obj, attribute_name, value):
    """Writes a string value to a JSON object (dict).

    Args:
        json_obj (dict): The JSON file to retrieve a value from.
        attribute_name (str): The attribute name to write to. If there are
            nested structures expressed within the attribute_name, they should
            be separated by periods. Consequently, attribute names and nested
            names cannot contain periods.
        value: The value to write to the attribute. The `value` should be
            an instance of one of the following Python data types: int, float,
            str, bool, list, dict, None. The "None" value is used to represent
            a "null" value in JSON.

    Returns:
        dict: The new JSON object with the modified or added attribute.

    Raises:
        ValueError: If the `value` parameter is not of one of the accepted
            types.
    """
    if (type(value) not in (int, float, str, bool, list, dict) and
            value is not None):
        raise ValueError("Type '%s' of value '%s' is not valid." %
                         (type(value), value))

    try:
        new_json = _recursive_write(deepcopy(json_obj), attribute_name, value)
        return new_json
    except KeyError as err:
        sys.exit("Error: " + re.sub('"', '', str(err)))

def _recursive_write(json_obj, attribute_name, value):
    """
    Raises:
        KeyError: When a sub-attribute is specified for a non-object.
    """
    #print("DEBUG: json_obj = %s attribute_name = %s value = %s" %
    #      (json_obj, attribute_name, value))
    attrib_as_list = attribute_name.split('.')
    current_attrib = attrib_as_list.pop(0)

    if len(attrib_as_list) == 0:
        json_obj[attribute_name] = value
        return json_obj
    else:
        if not isinstance(json_obj, dict):
            raise KeyError(("The specified parent of the supposed sub-"
                            "attribute '%s' is not an object, and therefore "
                            "cannot have a sub-attribute.") % current_attrib)
        if current_attrib not in json_obj:
            json_obj[current_attrib] = dict()
        attribute_name = '.'.join(attrib_as_list) #no period included for len 1
        json_obj[current_attrib] = _recursive_write(json_obj[current_attrib],
                                                    attribute_name, value)
        return json_obj


def get_json_field(json_obj, attribute_name, json_filename=None,
                   suppress_err_msg=False):
    """Retrieves a value from a JSON object (dict).
    Args:
        json_obj (dict): The JSON file to retrieve a value from.
        attribute_name (str): The attribute to look up. If there are nested
            structures expressed within the attribute_name, they should be
            separated by periods. Consequently, attribute names and nested
            names cannot contain periods.
        json_filename (Optional[str]): The name of the JSON file the attribute
            is read from. This will be included in error messages. Default is
            `None`.
        suppress_err_msg (Optional[bool]): Specifies whether an error message
            will be printed to stdout if an error condition is met. By default,
            error messages will be printed.
    Raises:
        KeyError: If the specified `attribute_name` does not exist in the JSON.
    """
    while '.' in attribute_name:
        attrib_as_list = attribute_name.split('.')
        attrib_name_single = attrib_as_list.pop(0)
        try:
            json_obj = json_obj[attrib_name_single]
        except KeyError:
            if not suppress_err_msg:
                error_suffix = '.'
                if json_filename is not None:
                    error_suffix = " '%s'." % json_filename
                print("Attribute '%s' not found in preferences file%s" %
                      (attrib_name_single, error_suffix))
            raise
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
    if len(sys.argv) in (3, 4, 6):
        action = sys.argv[1]
        if action in ('read', 'write'):
            preferences_filename = sys.argv[2]
            chrome_property = None
            if len(sys.argv) in (4, 6):
                chrome_property = sys.argv[3]
            value = None
            if len(sys.argv) == 6:
                write_type = sys.argv[4]
                write_value = sys.argv[5]
                if write_type == '-bool':
                    if write_value.lower() == 'true':
                        value = True
                    elif write_value.lower() == 'false':
                        value = False
                    else:
                        print "'%s' is not a valid boolean." % str(write_value)
                        print_usage()
                elif write_type == '-int':
                    try:
                        value = int(write_value)
                    except ValueError:
                        print "'%s' is not a valid integer." % str(write_value)
                        print_usage()
                elif write_type == '-string':
                    try:
                        value = str(write_value)
                    except ValueError:
                        print "Provided value is not a valid string."
                        print_usage()
                else:
                    print_usage()
            return (action, preferences_filename, chrome_property, value)

    print_usage()

def print_usage():
    """Prints syntax for usage and exits the program."""
    print(("Usage:\n"
           "\tpython chrome_defaults.py read %sfile%s "
           "[%sattribute-name%s]\n"
           "\tOR\n"
           "\tpython chrome_defaults.py write %sfile%s %sattribute-name%s "
           "-bool|-string|-int %svalue%s") %
          (UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC,
           UNDERLINE, ENDC))
    sys.exit()

def _make_backup(filename):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    dest = "%s%s.bak" % (filename, timestamp)
    shutil.copyfile(filename, dest)

if __name__ == "__main__":
    _main()
