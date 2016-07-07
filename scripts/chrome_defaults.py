# -*- coding: utf-8 -*-
"""Reads and writes Google Chome preferences in OS X.

Based on the `defaults` utility for reading/writing PList files in OS X.

The sub-commands currently supported are
* read
* write
* delete
* write-array

###########################
# write-array Sub-Command #
###########################

The "write-array" sub-command is a `defaults`-unlike command that allows one to
write a value to objects contained in array, optionally specifying a condition
to match only some of the array objects. For example:
{
    ...other attributes in the JSON
    "plugins_list": [
        {
            "enabled": true,
            "name": "Widevine Content Decryption Module"
        },
        {
            "enabled": true,
            "name": "Shockwave Flash"
        }
    ]
}

In order to set the "Shockwave Flash" element of the "plugins_list" array to
enabled = false, we can use this write-array sub-command:
write-array plugins_list enabled -bool false where name -string "Shockwave Flash"

################
# Dot Notation #
################

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

#######################
# Writing JSON values #
#######################

The 'write' command now accepts '-json' as type argument. The argument that
follows this will be decoded as a string representation of a JSON object. This
facilitates setting arbitrarily complex values, including arrays and objects
(dictionaries in Python).

Examples:

    $ python chrome_defaults.py read "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences"

    $ python chrome_defaults.py read "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" download.directory_upgrade

    $ python chrome_defaults.py write "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" download.directory_upgrade -bool true

    $ python chrome_defaults.py write "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" plugins.plugins_list -json '[{"enabled": false, "name": "Shockwave Flash"}]'

    $ python chrome_defaults.py delete "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" dns_prefetching

    $ python chrome_defaults.py write-array "/Users/myusername/Library/Application Support/Google/Chrome/Default/Preferences" plugins.plugins_list enabled -bool false where name -string "Shockwave Flash"

Todos:
    * Unit tests
    * Add support for writing list values e.g. write [1, 2, 3]
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

DEBUG_PRINT = False

def _main():
    args = get_args()
    dprint(args)
    preferences_json = _get_json(args['preferences_filename'])
    if args['action'] == 'read':
        if args['chrome_property'] is None:
            print "%s" % json.dumps(preferences_json, indent=4)
            sys.exit()
        else:
            try:
                args['value'] = get_json_field(
                    preferences_json, args['chrome_property'],
                    args['preferences_filename'])
                print "%s" % normalize(args['value'])
            except KeyError:
                print("The attribute '%s' does not exist in '%s'." %
                      (args['chrome_property'], args['preferences_filename']))
    elif args['action'] == 'write':
        _make_backup(args['preferences_filename'])
        new_json = write_json_field(
            preferences_json, args['chrome_property'], args['value'])

        with open(args['preferences_filename'], 'w') as preferences_file:
            preferences_file.write(json.dumps(new_json))
    elif args['action'] == 'delete':
        _make_backup(args['preferences_filename'])
        new_json = delete_json_field(preferences_json, args['chrome_property'])

        with open(args['preferences_filename'], 'w') as preferences_file:
            preferences_file.write(json.dumps(new_json))
    elif args['action'] == 'write-array':
        _make_backup(args['preferences_filename'])

        where_clause = None
        if 'where_property' in args and 'where_value' in args:
            where_clause = (args['where_property'], args['where_value'])

        new_json = write_json_array(preferences_json, args['chrome_property'],
                                    args['value'], args['child_attrib'],
                                    where_clause=where_clause)
        with open(args['preferences_filename'], 'w') as preferences_file:
            preferences_file.write(json.dumps(new_json))
    else:
        raise ValueError("Invalid sub-command.")

def normalize(obj):
    """Recursively normalizes `unicode` data into utf-8 encoded `str`.

    This will have the effect of converting a Chrome preferences JSON file into
    UTF-8 encoding, which may break some non-English or otherwise funky files.

    http://stackoverflow.com/questions/18272066/easy-way-to-convert-a-unicode-list-to-a-list-containing-python-strings
    """
    dprint("normalize: object is of type %s" % str(type(obj)))
    if isinstance(obj, unicode):
        encoded = obj.encode('utf-8', errors='replace')
        dprint('Encoded %s' % encoded)
        return encoded
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

def write_json_array(json_obj, attribute_name, value, child_name,
                     where_clause=None):
    """
    Args:
        json_obj (dict): The JSON data being modified.
        attribute_name (str): The location of the parent array that contains
        the objects being written to.
        value (Optional): The value to write to the attribute. The `value`
            should be an instance of one of the following Python data types:
            int, float, str, bool, list, dict, None. The "None" value is used to
            represent a "null" value in JSON. The default value is None.
        child_name (str): The name of the attribute that will be modified within
            the members of the object array. If there are nested structures
            expressed within child_name, they should be separated by periods.
        where_clause (Optional[(str, value)]: If writing to multiple objects
            using the "write-array" sub-command, this argument can indicate
            criteria by which to choose specific members of the object array
            to write to. This argument consists of a 2-tuple: The name of the
            attribute to match, and the value it must equal in order to meet
            the criteria. This is akin to a "WHERE {atrib} = {value}" clause
            in SQL.
    """
    if (type(value) not in (int, float, str, bool, list, dict) and
            value is not None):
        raise ValueError("Type '%s' of value '%s' is not valid." %
                         (type(value), value))

    try:
        new_json = _recursive_write(json_obj=deepcopy(json_obj),
                                    attribute_name=attribute_name,
                                    value=value,
                                    delete_attrib=False,
                                    child_name=child_name,
                                    where_clause=where_clause)
        return new_json
    except KeyError as err:
        sys.exit("Error: " + re.sub('"', '', str(err)))


def _recursive_write(json_obj, attribute_name, value=None, delete_attrib=False,
                     child_name=None, where_clause=None):
    """
    Args:
        json_obj (dict): The JSON data being modified.
        attribute_name (str): The attribute to modify. If there are nested
            structures expressed within the attribute_name, they should be
            separated by periods. Consequently, attribute names and nested
            names cannot contain periods. If writing to multiple objects using
            the "write-array" sub-command, this argument should instead be the
            location of the parent array that contains the objects being written
            to.
        value (Optional): The value to write to the attribute. The `value`
            should be an instance of one of the following Python data types:
            int, float, str, bool, list, dict, None. The "None" value is used to
            represent a "null" value in JSON. The default value is None.
        delete_attrib (Optional[bool]): If set to True, the attribute will be
            deleted instead of set to a specific value. When this is set to
            True, the `value` parameter should be set to `None`.
        child_name (Optional[str]): If writing to multiple objects using the
            "write-array" sub-command, this argument should be the name of the
            attribute that will be modified within the members of the object
            array. If there are nested structures expressed within child_name,
            they should be separated by periods.
        where_clause (Optional[(str, value)]: If writing to multiple objects
            using the "write-array" sub-command, this argument can indicate
            criteria by which to choose specific members of the object array
            to write to. This argument consists of a 2-tuple: The name of the
            attribute to match, and the value it must equal in order to meet
            the criteria. This is akin to a "WHERE {atrib} = {value}" clause
            in SQL.
    Raises:
        KeyError: When a sub-attribute is specified for a non-object.
    """
    if delete_attrib:
        assert value is None

    if child_name is None:
        assert where_clause is None

    attrib_as_list = attribute_name.split('.')
    current_attrib = attrib_as_list.pop(0)

    dprint(("_recursive_write: attribute_name='%s' current_attrib='%s' "
            "value='%s' type(value)='%s' delete_attrib='%s' child_name='%s' "
            "where_clause='%s'") %
           (attribute_name, current_attrib, str(value), str(type(value)),
            str(delete_attrib), str(child_name), str(where_clause)))

    if len(attrib_as_list) == 0:
        #Recursed down to target attribute
        if delete_attrib:
            try:
                del json_obj[current_attrib]
            except TypeError:
                raise KeyError(("Error: Attribute '%s' cannot be deleted "
                                "because the presumed parent attribute is not "
                                "an object.") % current_attrib)
        elif child_name is None:
            #normal write operation
            try:
                json_obj[current_attrib] = value
            except TypeError:
                raise KeyError(("Error: Attribute '%s' cannot be set because "
                                "the parent attribute is already set to a "
                                "non-object value.") % current_attrib)
        else:
            #write-array operation
            try:
                iter(json_obj[current_attrib])
            except TypeError:
                sys.exit(("Error: Cannot write to array because '%s' is not an "
                          "array.") % current_attrib)

            for array_item in json_obj[current_attrib]:
                if where_clause is None:
                    try:
                        array_item[child_name] = value
                    except TypeError:
                        sys.exit(("Error: Attribute '%s' cannot be set because "
                                  "one of the elements of the target array is "
                                  "already set to a non-object value.") %
                                 current_attrib)
                else:
                    where_attrib = str(where_clause[0])
                    where_val = where_clause[1]
                    if array_item[where_attrib] == where_val:
                        try:
                            array_item[child_name] = value
                        except TypeError:
                            sys.exit(("Error: Attribute '%s' cannot be set "
                                      "because one of the elements of the "
                                      "target array is already set to a "
                                      "non-object value.") % current_attrib)
        dprint("_recursive_write: base case: returning '%s'" % str(json_obj))
        return json_obj
    else:
        if not isinstance(json_obj, dict):
            raise KeyError(("The specified parent of the supposed sub-"
                            "attribute '%s' is not an object, and therefore "
                            "cannot have a sub-attribute.") % current_attrib)
        if current_attrib not in json_obj:
            json_obj[current_attrib] = dict()
        attribute_name = '.'.join(attrib_as_list) #no period included for len 1

        json_obj[current_attrib] = _recursive_write(
            json_obj=json_obj[current_attrib], attribute_name=attribute_name,
            value=value, delete_attrib=delete_attrib, child_name=child_name,
            where_clause=where_clause)

        dprint("_recursive_write: returning '%s'" % str(json_obj))
        return json_obj

def delete_json_field(json_obj, attribute_name):
    """Deletes a value from a JSON object (dict).
    Args:
        json_obj (dict): The JSON file that contains the attribute to delete.
        attribute_name (str): The attribute to delete. If there are nested
            structures expressed within the attribute_name, they should be
            separated by periods. Consequently, attribute names and nested
            names cannot contain periods.
    """
    try:
        new_json = _recursive_write(deepcopy(json_obj), attribute_name,
                                    value=None, delete_attrib=True)
        return new_json
    except KeyError:
        sys.exit("Error: '%s' attribute not found." % attribute_name)

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
        sys.exit("No Google Chrome preferences file found at '%s'" % filename)
    except ValueError:
        sys.exit(("File '%s' does not appear to be a valid JSON file. Check "
                  "this directory for backup copies to restore to, in case "
                  "this file has become corrupted.") % filename)

def get_args():
    """Reads command line arguments.
    Returns:
        dict: Contains the following keys set to values:
            * 'action'
            * 'preferences_filename'
            * 'chrome_property': If no chrome_property is specified by the user,
                this value is set to None.
            * 'value' (optional)
            * 'where_property' (optional): Condition to write 'value' to array
                of objects
            * 'where_value' (optional)
    """
    args = dict()
    args['action'] = None
    args['preferences_filename'] = None
    args['chrome_property'] = None

    if len(sys.argv) > 2:
        args['action'] = sys.argv[1]
    else:
        print_usage()

    if args['action'] == 'read':
        if len(sys.argv) == 3:
            args['preferences_filename'] = sys.argv[2]
        elif len(sys.argv) == 4:
            args['preferences_filename'] = sys.argv[2]
            args['chrome_property'] = sys.argv[3]
        else:
            print_usage()
    elif args['action'] == 'delete':
        if len(sys.argv) == 4:
            args['preferences_filename'] = sys.argv[2]
            args['chrome_property'] = sys.argv[3]
        else:
            print_usage()
    elif args['action'] == 'write':
        if len(sys.argv) == 6:
            args['preferences_filename'] = sys.argv[2]
            args['chrome_property'] = sys.argv[3]
            write_type = sys.argv[4]
            write_value = sys.argv[5]

            args['value'] = _get_value_and_handle_errors(value=write_value,
                                                         type_arg=write_type)
        else:
            print_usage()
    elif args['action'] == 'write-array':
        if len(sys.argv) in (7, 11):
            args['preferences_filename'] = sys.argv[2]
            args['chrome_property'] = sys.argv[3]
            args['child_attrib'] = sys.argv[4]
            write_type = sys.argv[5]
            write_value = sys.argv[6]

            args['value'] = _get_value_and_handle_errors(value=write_value,
                                                         type_arg=write_type)
            if len(sys.argv) == 11:
                if sys.argv[7] == 'where':
                    args['where_property'] = sys.argv[8]
                    where_type = sys.argv[9]
                    where_val = sys.argv[10]
                    args['where_value'] = _get_value_and_handle_errors(
                        value=where_val, type_arg=where_type)
                else:
                    print_usage()
        else:
            print_usage()

    return args

def _get_value_and_handle_errors(value, type_arg):
    """See: `_get_value`"""
    try:
        return _get_value(value, type_arg)
    except ValueError as err:
        print re.sub('"', '', str(err))
        print_usage()
    except TypeError as err:
        print re.sub('"', '', str(err))
        print_usage()

def _get_value(value, type_arg):
    """Returns the value cast into the appropriate Python data type.
    Arguments:
        value: The value to return, in some castable form.
        type_arg (str): One of the following strings: '-bool', '-int', 'string'

    Raises:
        ValueError: If the value is not castable into the specified data type.
        TypeError: If the `type_arg` is not a valid type
    """

    if type_arg == '-bool':
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ValueError("'%s' is not a valid boolean." % str(value))
    elif type_arg == '-int':
        try:
            return int(value)
        except ValueError:
            raise ValueError("'%s' is not a valid integer." % str(value))
    elif type_arg == '-string':
        try:
            return str(value)
        except ValueError:
            raise ValueError("Provided value is not a valid string.")
    elif type_arg == '-json':
        try:
            return json.loads(value)
        except ValueError:
            raise ValueError("'%s' is not a valid JSON string representation." %
                             str(value))
    else:
        raise TypeError("The type '%s' is not a supported data type." %
                        re.sub('-', '', str(type_arg)))


def print_usage():
    """Prints syntax for usage and exits the program."""
    print(("Usage:\n"
           "\tpython chrome_defaults.py read %sfile%s "
           "[%sattribute-name%s]\n"
           "\tOR\n"
           "\tpython chrome_defaults.py write %sfile%s %sattribute-name%s "
           "-bool|-string|-int|-json %svalue%s\n"
           "\tOR\n"
           "\tpython chrome_defaults.py delete %sfile%s %sattribute-name%s\n"
           "\tOR\n"
           "\tpython chrome_defaults.py write-array %sfile%s "
           "%sarray-name%s %sattribute-name%s -bool|-string|-int %svalue%s "
           "[where %sattribute-name%s -bool|-string|-int %svalue%s]") %
          (UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC,
           UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC,
           UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC, UNDERLINE, ENDC,
           UNDERLINE, ENDC))
    sys.exit()

def _make_backup(filename):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    dest = "%s%s.bak" % (filename, timestamp)
    shutil.copyfile(filename, dest)

def dprint(data):
    """Print debug information."""
    if DEBUG_PRINT:
        print "DEBUG: %s" % str(data)

if __name__ == "__main__":
    _main()
