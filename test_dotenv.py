"""Unit tests for envdot package"""

import unittest
import tempfile
import os
from pathlib import Path
from envdot import DotEnv, load_env, get_env, set_env
from envdot.core import TypeDetector
from envdot.exceptions import FileNotFoundError, ParseError, TypeConversionError


class TestTypeDetector(unittest.TestCase):
    """Test automatic type detection"""
    
    def test_boolean_detection(self):
        """Test boolean value detection"""
        self.assertTrue(TypeDetector.auto_detect('true'))
        self.assertTrue(TypeDetector.auto_detect('True'))
        self.assertTrue(TypeDetector.auto_detect('yes'))
        self.assertTrue(TypeDetector.auto_detect('on'))
        self.assertTrue(TypeDetector.auto_detect('1'))
        
        self.assertFalse(TypeDetector.auto_detect('false'))
        self.assertFalse(TypeDetector.auto_detect('False'))
        self.assertFalse(TypeDetector.auto_detect('no'))
        self.assertFalse(TypeDetector.auto_detect('off'))
        self.assertFalse(TypeDetector.auto_detect('0'))
    
    def test_none_detection(self):
        """Test None value detection"""
        self.assertIsNone(TypeDetector.auto_detect('none'))
        self.assertIsNone(TypeDetector.auto_detect('None'))
        self.assertIsNone(TypeDetector.auto_detect('null'))
        self.assertIsNone(TypeDetector.auto_detect(''))
    
    def test_integer_detection(self):
        """Test integer value detection"""
        self.assertEqual(TypeDetector.auto_detect('123'), 123)
        self.assertEqual(TypeDetector.auto_detect('0'), 0)
        self.assertEqual(TypeDetector.auto_detect('-456'), -456)
        self.assertIsInstance(TypeDetector.auto_detect('999'), int)
    
    def test_float_detection(self):
        """Test float value detection"""
        self.assertEqual(TypeDetector.auto_detect('123.45'), 123.45)
        self.assertEqual(TypeDetector.auto_detect('0.0'), 0.0)
        self.assertEqual(TypeDetector.auto_detect('-456.78'), -456.78)
        self.assertIsInstance(TypeDetector.auto_detect('3.14'), float)
    
    def test_string_detection(self):
        """Test string value detection"""
        self.assertEqual(TypeDetector.auto_detect('hello'), 'hello')
        self.assertEqual(TypeDetector.auto_detect('hello world'), 'hello world')
        self.assertEqual(TypeDetector.auto_detect('abc123'), 'abc123')
    
    def test_to_string_conversion(self):
        """Test conversion to string"""
        self.assertEqual(TypeDetector.to_string(True), 'true')
        self.assertEqual(TypeDetector.to_string(False), 'false')
        self.assertEqual(TypeDetector.to_string(None), '')
        self.assertEqual(TypeDetector.to_string(123), '123')
        self.assertEqual(TypeDetector.to_string(45.67), '45.67')


class TestDotEnvBasic(unittest.TestCase):
    """Test basic DotEnv functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = Path(self.temp_dir) / '.env'
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_instance(self):
        """Test creating DotEnv instance"""
        env = DotEnv(auto_load=False)
        self.assertIsInstance(env, DotEnv)
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        env = DotEnv(auto_load=False)
        env.set('TEST_KEY', 'test_value')
        
        self.assertEqual(env.get('TEST_KEY'), 'test_value')
    
    def test_get_with_default(self):
        """Test getting value with default"""
        env = DotEnv(auto_load=False)
        
        value = env.get('NONEXISTENT_KEY', default='default_value')
        self.assertEqual(value, 'default_value')
    
    def test_dictionary_access(self):
        """Test dictionary-style access"""
        env = DotEnv(auto_load=False)
        env['KEY'] = 'value'
        
        self.assertEqual(env['KEY'], 'value')
    
    def test_contains(self):
        """Test 'in' operator"""
        env = DotEnv(auto_load=False)
        env.set('EXISTING_KEY', 'value')
        
        self.assertTrue('EXISTING_KEY' in env)
        self.assertFalse('NONEXISTENT_KEY' in env)
    
    def test_delete(self):
        """Test deleting keys"""
        env = DotEnv(auto_load=False)
        env.set('KEY_TO_DELETE', 'value')
        
        self.assertTrue('KEY_TO_DELETE' in env)
        env.delete('KEY_TO_DELETE')
        self.assertFalse('KEY_TO_DELETE' in env)
    
    def test_clear(self):
        """Test clearing all keys"""
        env = DotEnv(auto_load=False)
        env.set('KEY1', 'value1')
        env.set('KEY2', 'value2')
        
        self.assertEqual(len(env.keys()), 2)
        env.clear()
        self.assertEqual(len(env.keys()), 0)


class TestDotEnvFiles(unittest.TestCase):
    """Test file loading and saving"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_env_file(self):
        """Test loading .env file"""
        env_file = Path(self.temp_dir) / '.env'
        env_file.write_text(
            'DEBUG=true\n'
            'PORT=8080\n'
            'APP_NAME=TestApp\n'
        )
        
        env = DotEnv(env_file, auto_load=False)
        env.load()
        
        self.assertEqual(env.get('DEBUG'), True)
        self.assertEqual(env.get('PORT'), 8080)
        self.assertEqual(env.get('APP_NAME'), 'TestApp')
    
    def test_load_json_file(self):
        """Test loading JSON file"""
        json_file = Path(self.temp_dir) / 'config.json'
        json_file.write_text('{"DEBUG": true, "PORT": 8080, "APP_NAME": "TestApp"}')
        
        env = DotEnv(json_file, auto_load=False)
        env.load()
        
        self.assertEqual(env.get('DEBUG'), True)
        self.assertEqual(env.get('PORT'), 8080)
        self.assertEqual(env.get('APP_NAME'), 'TestApp')
    
    def test_save_env_file(self):
        """Test saving to .env file"""
        env_file = Path(self.temp_dir) / '.env'
        
        env = DotEnv(auto_load=False)
        env.set('DEBUG', True)
        env.set('PORT', 8080)
        env.save(env_file)
        
        # Load and verify
        content = env_file.read_text()
        self.assertIn('DEBUG=true', content)
        self.assertIn('PORT=8080', content)
    
    def test_save_json_file(self):
        """Test saving to JSON file"""
        json_file = Path(self.temp_dir) / 'config.json'
        
        env = DotEnv(auto_load=False)
        env.set('DEBUG', True)
        env.set('PORT', 8080)
        env.save(json_file)
        
        # Load and verify
        import json
        with open(json_file) as f:
            data = json.load(f)
        
        self.assertEqual(data['DEBUG'], True)
        self.assertEqual(data['PORT'], 8080)
    
    def test_file_not_found(self):
        """Test file not found error"""
        env = DotEnv('nonexistent.env', auto_load=False)
        
        with self.assertRaises(FileNotFoundError):
            env.load()


class TestTypeCasting(unittest.TestCase):
    """Test explicit type casting"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.env = DotEnv(auto_load=False)
        self.env.set('STRING_VALUE', 'hello')
        self.env.set('INT_VALUE', '123')
        self.env.set('BOOL_VALUE', 'true')
    
    def test_cast_to_string(self):
        """Test casting to string"""
        value = self.env.get('INT_VALUE', cast_type=str)
        self.assertEqual(value, '123')
        self.assertIsInstance(value, str)
    
    def test_cast_to_int(self):
        """Test casting to int"""
        value = self.env.get('INT_VALUE', cast_type=int)
        self.assertEqual(value, 123)
        self.assertIsInstance(value, int)
    
    def test_cast_to_bool(self):
        """Test casting to bool"""
        value = self.env.get('BOOL_VALUE', cast_type=bool)
        self.assertEqual(value, True)
        self.assertIsInstance(value, bool)
    
    def test_invalid_cast(self):
        """Test invalid type casting"""
        with self.assertRaises(TypeConversionError):
            self.env.get('STRING_VALUE', cast_type=int)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = Path(self.temp_dir) / '.env'
        self.env_file.write_text('TEST_VAR=test_value\n')
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_env_function(self):
        """Test load_env convenience function"""
        load_env(self.env_file)
        value = get_env('TEST_VAR')
        self.assertEqual(value, 'test_value')
    
    def test_set_env_function(self):
        """Test set_env convenience function"""
        set_env('NEW_VAR', 'new_value')
        value = get_env('NEW_VAR')
        self.assertEqual(value, 'new_value')


class TestMethodChaining(unittest.TestCase):
    """Test method chaining"""
    
    def test_chaining(self):
        """Test fluent API with method chaining"""
        env = (DotEnv(auto_load=False)
               .set('KEY1', 'value1')
               .set('KEY2', 'value2')
               .set('KEY3', 'value3'))
        
        self.assertEqual(env.get('KEY1'), 'value1')
        self.assertEqual(env.get('KEY2'), 'value2')
        self.assertEqual(env.get('KEY3'), 'value3')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios"""
    
    def test_empty_value(self):
        """Test empty string values"""
        env = DotEnv(auto_load=False)
        env.set('EMPTY', '')
        
        value = env.get('EMPTY')
        self.assertIsNone(value)
    
    def test_whitespace_handling(self):
        """Test whitespace in values"""
        env = DotEnv(auto_load=False)
        env.set('SPACES', '  value with spaces  ')
        
        # Type detector strips whitespace
        value = TypeDetector.auto_detect('  value with spaces  ')
        self.assertEqual(value, 'value with spaces')
    
    def test_special_characters(self):
        """Test special characters in values"""
        env = DotEnv(auto_load=False)
        env.set('SPECIAL', 'value@with#special$chars')
        
        value = env.get('SPECIAL')
        self.assertEqual(value, 'value@with#special$chars')


if __name__ == '__main__':
    unittest.main()