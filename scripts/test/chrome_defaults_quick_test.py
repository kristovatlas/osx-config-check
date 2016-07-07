"""Unit tests for chrome_defaults.py.

Todos:
    * Add unit tests to WriteArrayComandTest to check for what happens when user
        incorrectly uses this sub-command.
    * More top-level unit tests of the wrapper functions to make sure that
        `sys`.`exit` is called when appropriate, rather than permitting uncaught
        exceptions.
"""

# pylint: disable=invalid-name, protected-access

import unittest
import json
from .. import chrome_defaults #chrome_defaults.py

class SupportFunctionTest(unittest.TestCase):
    """Tests for various support functions."""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_normalize_no_clobber(self):
        """The `normalize` function should not break strings already utf-8."""
        sample_json = {
            'dict': {
                'list': [1, 2, '3'],
                'int': 1,
                'str': 'bar',
            },
            'list': [1, 2, '3'],
            'int': 1,
            'str': 'foo'
        }
        self.assertEqual(sample_json, chrome_defaults.normalize(sample_json))

    def test_normalize_cope_with_unicode(self):
        """The `normalize` function should not raise errors."""
        sample_json = {'str1': u"\u0394", 'str2': u"\U00000394"}
        chrome_defaults.normalize(sample_json)

#   TODO: I need to study more how unicode works here.
#   def test_normalize_replace_non_utf8(self):
#       """The `normalize` function should replace non-UTF-8 characters.
#
#       See: https://docs.python.org/2/howto/unicode.html
#       """
#       sample_json = {'str': u'\x80abc'}
#       result = chrome_defaults.normalize(sample_json)
#       self.assertEqual(result['str'], u'\ufffdabc')

class ReadCommandTest(unittest.TestCase):
    """Tests for the 'read' sub-command.

    Relevant functions in chrome_defaults:
        * get_json_field(json_obj, attribute_name, json_filename=None,
                         suppress_err_msg=False)
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_simple_string_val(self):
        """Read a simple string value"""
        sample_json = {'str': 'val'}
        self.assertEqual(chrome_defaults.get_json_field(sample_json, 'str'),
                         'val')

    def test_read_simple_int_val(self):
        """Read a simple int value"""
        sample_json = {'int': 42}
        self.assertEqual(chrome_defaults.get_json_field(sample_json, 'int'), 42)

    def test_read_simple_bool_val(self):
        """Read a simple bool value"""
        sample_json = {'bool': False}
        self.assertEqual(chrome_defaults.get_json_field(sample_json, 'bool'),
                         False)

    def test_read_nested_val(self):
        """Read a nested value using dot notation."""
        sample_json = {'level1': {'level2': {'level3': {'int': 42}}}}
        self.assertEqual(
            chrome_defaults.get_json_field(
                sample_json, 'level1.level2.level3.int'),
            42)

    def test_missing_attribute(self):
        """Test error handling when requested attribute is missing."""
        sample_json = dict()
        with self.assertRaises(KeyError):
            chrome_defaults.get_json_field(sample_json, "missing_attrib")

class WriteCommandTest(unittest.TestCase):
    """Tests for the 'write' sub-command.

    Relevant functions in chrome_defaults:
        * write_json_field(json_obj, attribute_name, value): this is mostly a
            wrapper function
        * _recursive_write(json_obj, attribute_name, value=None,
                           delete_attrib=False, child_name=None,
                           where_clause=None)
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_overwrite_simple_int(self):
        """Overwite an integer with another value."""
        sample_json = {'int': 42}
        result = chrome_defaults._recursive_write(sample_json, 'int', 11)
        self.assertEqual(result['int'], 11)

    def test_overwrite_nested_int(self):
        """Overwrite an integer nested within objects with another value."""
        sample_json = {'level1': {'level2': {'level3': {'int': 42}}}}
        result = chrome_defaults._recursive_write(sample_json,
                                                  'level1.level2.level3.int',
                                                  11)
        self.assertEqual(result['level1']['level2']['level3']['int'], 11)

    def test_write_to_sub_attrib_of_non_obj(self):
        """`_recursive_write` should raise an exception in this situation."""
        sample_json = {'int': 42}
        with self.assertRaises(KeyError):
            chrome_defaults._recursive_write(sample_json, 'int.str', 'val')

    def test_write_to_sub_attrib_of_non_obj_exit(self):
        """`write_json_field` should terminate in this situation."""
        sample_json = {'int': 42}
        with self.assertRaises(SystemExit):
            chrome_defaults.write_json_field(sample_json, 'int.str', 'val')

    def test_write_to_sub_attrib_of_missing_obj(self):
        """This hould create nested `dicts` to fill missing attribs."""
        sample_json = {'level1': {'level2': {'level3': {'str': 'foo'}}}}
        result = chrome_defaults.write_json_field(
            sample_json, 'level1.level2.level3.level4.str', 'val')
        self.assertEqual(result['level1']['level2']['level3']['str'], 'foo')
        self.assertEqual(result['level1']['level2']['level3']['level4']['str'],
                         'val')

    def test_overwrite_attrib_with_json(self):
        """This should support writing an arbitrarily complex JSON object."""
        original_json = {'level1': 'asdf'}
        new_json_val = ('{"level2": [{"name": "arr-obj1", "val": 1},'
                        '{"name": "arr-obj2", "val": 2}]}')
        result = chrome_defaults.write_json_field(
            original_json, 'level1', json.loads(new_json_val))
        self.assertIsInstance(result['level1'], dict)
        self.assertEqual(result['level1']['level2'][0]['name'], 'arr-obj1')
        self.assertEqual(result['level1']['level2'][0]['val'], 1)
        self.assertEqual(result['level1']['level2'][1]['name'], 'arr-obj2')
        self.assertEqual(result['level1']['level2'][1]['val'], 2)
        self.assertEqual(len(result['level1']['level2']), 2)

    def test_write_nested_attrib_with_json(self):
        """This should write a JSON object to a nested attrib."""
        original_json = {'level1': {'level2': {}}}
        new_json_val = ('{"level4": [{"name": "arr-obj1", "val": 1},'
                        '{"name": "arr-obj2", "val": 2}]}')
        result = chrome_defaults.write_json_field(
            original_json, 'level1.level2.level3', json.loads(new_json_val))
        self.assertIsInstance(result['level1']['level2']['level3'], dict)
        self.assertEqual(
            result['level1']['level2']['level3']['level4'][0]['name'],
            'arr-obj1')
        self.assertEqual(
            result['level1']['level2']['level3']['level4'][0]['val'],
            1)
        self.assertEqual(
            result['level1']['level2']['level3']['level4'][1]['name'],
            'arr-obj2')
        self.assertEqual(
            result['level1']['level2']['level3']['level4'][1]['val'],
            2)
        self.assertEqual(len(result['level1']['level2']['level3']['level4']), 2)

    def test_write_nested_attrib_with_json_parent_not_obj_exit(self):
        """This should terminate because a parent attrib is a non-obj.

        Note that if you want to overwrite a non-obj and replace it with an
        object-based structure, you can first use the 'delete' sub-command on
        it, and then write to it.
        """
        original_json = {'level1': {'level2': False}}
        new_json_val = ('{"level4": [{"name": "arr-obj1", "val": 1},'
                        '{"name": "arr-obj2", "val": 2}]}')
        with self.assertRaises(SystemExit):
            result = chrome_defaults.write_json_field(
                original_json, 'level1.level2.level3', json.loads(new_json_val))

class DeleteCommandTest(unittest.TestCase):
    """Tests for the 'delete' sub-command.

    Relevant functions in chrome_defaults:
        * def delete_json_field(json_obj, attribute_name): this is mostly a
            wrapper function
        * _recursive_write(json_obj, attribute_name, value=None,
                           delete_attrib=False, child_name=None,
                           where_clause=None)

    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_int_delete(self):
        """Delete a simple int field."""
        sample_json = {'int': 42}
        result = chrome_defaults._recursive_write(json_obj=sample_json,
                                                  attribute_name='int',
                                                  value=None,
                                                  delete_attrib=True)
        self.assertNotIn('int', result)

    def test_delete_key_not_present(self):
        """Deleting a field not present in the JSON should raise error."""
        with self.assertRaises(KeyError):
            chrome_defaults._recursive_write(
                {}, 'int', value=None, delete_attrib=True)

    def test_delete_key_referencing_sub_attrib_of_non_object(self):
        """Referencing a sub-attribute of a non-obj should raise error."""
        sample_json = {'int': 42}
        with self.assertRaises(KeyError):
            chrome_defaults._recursive_write(
                sample_json, 'int.str', value=None, delete_attrib=True)

    def test_delete_key_not_present_exit(self):
        """`delete_json_field` should terminate in this condition"""
        with self.assertRaises(SystemExit):
            chrome_defaults.delete_json_field({}, 'int')

    def test_delete_key_referencing_sub_attrib_of_non_object_exit(self):
        """`delete_json_field` should terminate in this condition"""
        sample_json = {'int': 42}
        with self.assertRaises(SystemExit):
            chrome_defaults.delete_json_field(sample_json, 'int.str')

class WriteArrayComandTest(unittest.TestCase):
    """Tests for the 'write-array' sub-command.

    Relevant functions in chrome_defaults:
        * write_json_array(json_obj, attribute_name, value, child_name,
                           where_clause=None)
        * _recursive_write(json_obj, attribute_name, value=None,
                           delete_attrib=False, child_name=None,
                           where_clause=None)

    """

    def test_write_simple_int_to_array(self):
        """Write a simple int value to an array of objects."""
        sample_json = {'arr': [{'key': 'val1'}, {'key':'val2'}]}
        result = chrome_defaults._recursive_write(
            sample_json, 'arr', value='val3', delete_attrib=False,
            child_name='key', where_clause=None)
        self.assertEqual(result['arr'][0]['key'], 'val3')
        self.assertEqual(result['arr'][1]['key'], 'val3')
        self.assertEqual(len(result['arr']), 2)

    def test_write_simple_int_to_array_with_where_clause(self):
        """Write a simple int value to some objects in an array."""
        sample_json = {
            'arr': [
                {'name': 'obj1', 'key': 'val1'},
                {'name': 'obj2', 'key': 'val2'}
            ]
        }
        result = chrome_defaults._recursive_write(
            sample_json, 'arr', value='val3', delete_attrib=False,
            child_name='key', where_clause=('name', 'obj2'))
        self.assertEqual(result['arr'][0]['key'], 'val1')
        self.assertEqual(result['arr'][1]['key'], 'val3')
        self.assertEqual(len(result['arr']), 2)

    def test_write_simple_str_to_nested_array(self):
        """Write a simple int value to a nested array of objects."""
        sample_json = {
            'plugins': {
                'plugin_list': [
                    {
                        "enabled": True,
                        "name": "Widevine Content Decryption Module",
                    },
                    {
                        "enabled": True,
                        "name": "Shockwave Flash"
                    }
                ]
            }
        }

        result = chrome_defaults._recursive_write(
            sample_json, 'plugins.plugin_list', value=False,
            delete_attrib=False, child_name='enabled', where_clause=None)
        self.assertEqual(result['plugins']['plugin_list'][0]['enabled'], False)
        self.assertEqual(result['plugins']['plugin_list'][1]['enabled'], False)
        self.assertEqual(len(result['plugins']['plugin_list']), 2)

    def test_write_simple_str_to_nested_array_with_where_clause(self):
        """Write a simple int value to some objects in a nested array."""
        sample_json = {
            'plugins': {
                'plugin_list': [
                    {
                        "enabled": True,
                        "name": "Widevine Content Decryption Module",
                    },
                    {
                        "enabled": True,
                        "name": "Shockwave Flash"
                    }
                ]
            }
        }

        result = chrome_defaults._recursive_write(
            sample_json, 'plugins.plugin_list', value=False,
            delete_attrib=False, child_name='enabled',
            where_clause=('name', 'Shockwave Flash'))
        self.assertEqual(result['plugins']['plugin_list'][0]['enabled'], True)
        self.assertEqual(result['plugins']['plugin_list'][1]['enabled'], False)
        self.assertEqual(len(result['plugins']['plugin_list']), 2)

suite1 = unittest.TestLoader().loadTestsFromTestCase(SupportFunctionTest)
suite2 = unittest.TestLoader().loadTestsFromTestCase(ReadCommandTest)
suite3 = unittest.TestLoader().loadTestsFromTestCase(WriteCommandTest)
suite4 = unittest.TestLoader().loadTestsFromTestCase(DeleteCommandTest)
suite5 = unittest.TestLoader().loadTestsFromTestCase(WriteArrayComandTest)
