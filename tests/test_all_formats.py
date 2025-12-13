#!/usr/bin/env python3
"""
Complete test suite for envdot - all formats
Tests .env, JSON, YAML, INI, and TOML support
"""

import os
import pytest
from pathlib import Path
import tempfile
import shutil

# Import envdot
from envdot import (
    DotEnv, load_env, get_env, set_env, save_env,
    DotEnvError, FileNotFoundError, ParseError
)


class TestDotEnvFormat:
    """Test .env file format"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.env_file = Path(self.test_dir) / '.env'
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_env_file(self):
        """Test loading .env file"""
        content = """
DATABASE_HOST=localhost
DATABASE_PORT=5432
DEBUG=true
TIMEOUT=30.5
APP_NAME="My Application"
"""
        self.env_file.write_text(content)
        
        env = load_env(self.env_file)
        
        assert get_env('DATABASE_HOST') == 'localhost'
        assert get_env('DATABASE_PORT') == 5432
        assert get_env('DEBUG') is True
        assert get_env('TIMEOUT') == 30.5
        assert get_env('APP_NAME') == 'My Application'
    
    def test_save_env_file(self):
        """Test saving .env file"""
        env = DotEnv(self.env_file, auto_load=False, newone=True)
        env.set('TEST_KEY', 'test_value')
        env.set('TEST_INT', 42)
        env.set('TEST_BOOL', True)
        env.save()
        
        # Reload and verify
        env2 = load_env(self.env_file)
        assert get_env('TEST_KEY') == 'test_value'
        assert get_env('TEST_INT') == 42
        assert get_env('TEST_BOOL') is True
    
    def test_type_detection(self):
        """Test automatic type detection"""
        content = """
STR_VALUE=hello
INT_VALUE=42
FLOAT_VALUE=3.14
BOOL_TRUE=true
BOOL_FALSE=false
NULL_VALUE=none
"""
        self.env_file.write_text(content)
        env = load_env(self.env_file)
        
        assert isinstance(get_env('STR_VALUE'), str)
        assert isinstance(get_env('INT_VALUE'), int)
        assert isinstance(get_env('FLOAT_VALUE'), float)
        assert isinstance(get_env('BOOL_TRUE'), bool)
        assert isinstance(get_env('BOOL_FALSE'), bool)
        assert get_env('NULL_VALUE') is None


class TestJSONFormat:
    """Test JSON file format"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.json_file = Path(self.test_dir) / 'config.json'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_json_file(self):
        """Test loading JSON file"""
        content = """{
  "database": {
    "host": "localhost",
    "port": 5432,
    "credentials": {
      "username": "admin",
      "password": "secret"
    }
  },
  "app": {
    "name": "Test App",
    "debug": true
  },
  "features": ["auth", "cache"]
}"""
        self.json_file.write_text(content)
        
        env = load_env(self.json_file)
        
        # Test flattened keys
        assert get_env('DATABASE_HOST') == 'localhost'
        assert get_env('DATABASE_PORT') == 5432
        assert get_env('DATABASE_CREDENTIALS_USERNAME') == 'admin'
        assert get_env('APP_NAME') == 'Test App'
        assert get_env('APP_DEBUG') is True
        assert get_env('FEATURES_0') == 'auth'
        assert get_env('FEATURES_1') == 'cache'
    
    def test_json5_support(self):
        """Test JSON5 format (single quotes, trailing commas)"""
        content = """{
  // Comment here
  'database': {
    'host': 'localhost',
    'port': 5432,
  },
}"""
        self.json_file.write_text(content)
        
        try:
            env = load_env(self.json_file)
            assert get_env('DATABASE_HOST') == 'localhost'
            assert get_env('DATABASE_PORT') == 5432
        except (ImportError, ParseError):
            # JSON5 not available or fallback parser used
            pytest.skip("JSON5 parsing not available")
    
    def test_nested_arrays(self):
        """Test nested arrays flattening"""
        content = """{
  "servers": [
    {"host": "server1", "port": 8080},
    {"host": "server2", "port": 8081}
  ]
}"""
        self.json_file.write_text(content)
        env = load_env(self.json_file)
        
        assert get_env('SERVERS_0_HOST') == 'server1'
        assert get_env('SERVERS_0_PORT') == 8080
        assert get_env('SERVERS_1_HOST') == 'server2'
        assert get_env('SERVERS_1_PORT') == 8081


class TestYAMLFormat:
    """Test YAML file format"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.yaml_file = Path(self.test_dir) / 'config.yaml'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_yaml_file(self):
        """Test loading YAML file"""
        content = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret

app:
  name: Test App
  debug: true
  
features:
  - auth
  - cache
"""
        self.yaml_file.write_text(content)
        
        try:
            env = load_env(self.yaml_file)
            
            assert get_env('DATABASE_HOST') == 'localhost'
            assert get_env('DATABASE_PORT') == 5432
            assert get_env('DATABASE_CREDENTIALS_USERNAME') == 'admin'
            assert get_env('APP_NAME') == 'Test App'
            assert get_env('APP_DEBUG') is True
            assert get_env('FEATURES_0') == 'auth'
        except ImportError:
            pytest.skip("PyYAML not installed")
    
    def test_yaml_types(self):
        """Test YAML native types"""
        content = """
string: hello
integer: 42
float: 3.14
boolean: true
null_value: null
list:
  - item1
  - item2
"""
        self.yaml_file.write_text(content)
        
        try:
            env = load_env(self.yaml_file)
            
            assert get_env('STRING') == 'hello'
            assert get_env('INTEGER') == 42
            assert get_env('FLOAT') == 3.14
            assert get_env('BOOLEAN') is True
            assert get_env('NULL_VALUE') is None
            assert get_env('LIST_0') == 'item1'
        except ImportError:
            pytest.skip("PyYAML not installed")


class TestINIFormat:
    """Test INI file format"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.ini_file = Path(self.test_dir) / 'config.ini'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_ini_file(self):
        """Test loading INI file"""
        content = """[DEFAULT]
app_name = Test App
version = 1.0.0

[database]
host = localhost
port = 5432
username = admin

[server]
host = 0.0.0.0
port = 8080
"""
        self.ini_file.write_text(content)
        
        env = load_env(self.ini_file)
        
        # DEFAULT section without prefix
        assert get_env('APP_NAME') == 'Test App'
        assert get_env('VERSION') == '1.0.0'
        
        # Other sections with prefix
        assert get_env('DATABASE_HOST') == 'localhost'
        assert get_env('DATABASE_PORT') == 5432
        assert get_env('SERVER_HOST') == '0.0.0.0'
        assert get_env('SERVER_PORT') == 8080
    
    def test_ini_sections(self):
        """Test INI section handling"""
        content = """[section1]
key1 = value1

[section2]
key2 = value2
"""
        self.ini_file.write_text(content)
        env = load_env(self.ini_file)
        
        assert get_env('SECTION1_KEY1') == 'value1'
        assert get_env('SECTION2_KEY2') == 'value2'


class TestTOMLFormat:
    """Test TOML file format"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.toml_file = Path(self.test_dir) / 'config.toml'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_toml_file(self):
        """Test loading TOML file"""
        content = """title = "Test App"
version = "1.0.0"

[database]
host = "localhost"
port = 5432

[database.credentials]
username = "admin"
password = "secret"

[server]
host = "0.0.0.0"
port = 8080
debug = true
"""
        self.toml_file.write_text(content)
        
        try:
            env = load_env(self.toml_file)
            
            assert get_env('TITLE') == 'Test App'
            assert get_env('VERSION') == '1.0.0'
            assert get_env('DATABASE_HOST') == 'localhost'
            assert get_env('DATABASE_PORT') == 5432
            assert get_env('DATABASE_CREDENTIALS_USERNAME') == 'admin'
            assert get_env('SERVER_HOST') == '0.0.0.0'
            assert get_env('SERVER_PORT') == 8080
            assert get_env('SERVER_DEBUG') is True
        except ImportError:
            pytest.skip("tomli/tomllib not installed")
    
    def test_toml_array_of_tables(self):
        """Test TOML array of tables"""
        content = """[[features]]
name = "auth"
enabled = true

[[features]]
name = "cache"
enabled = false
"""
        self.toml_file.write_text(content)
        
        try:
            env = load_env(self.toml_file)
            
            assert get_env('FEATURES_0_NAME') == 'auth'
            assert get_env('FEATURES_0_ENABLED') is True
            assert get_env('FEATURES_1_NAME') == 'cache'
            assert get_env('FEATURES_1_ENABLED') is False
        except ImportError:
            pytest.skip("tomli/tomllib not installed")
    
    def test_toml_nested_tables(self):
        """Test deep nested TOML tables"""
        content = """[a.b.c.d]
value = "deep"

[x]
[x.y]
[x.y.z]
nested = "value"
"""
        self.toml_file.write_text(content)
        
        try:
            env = load_env(self.toml_file)
            
            assert get_env('A_B_C_D_VALUE') == 'deep'
            assert get_env('X_Y_Z_NESTED') == 'value'
        except ImportError:
            pytest.skip("tomli/tomllib not installed")


class TestFormatConversion:
    """Test format conversion between different types"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_json_to_env(self):
        """Test converting JSON to .env"""
        json_file = Path(self.test_dir) / 'source.json'
        env_file = Path(self.test_dir) / 'target.env'
        
        json_file.write_text('{"key": "value", "number": 42}')
        
        env = load_env(json_file)
        save_env(env_file, format='env')
        
        assert env_file.exists()
        content = env_file.read_text()
        assert 'KEY=value' in content
        assert 'NUMBER=42' in content
    
    def test_env_to_json(self):
        """Test converting .env to JSON"""
        env_file = Path(self.test_dir) / 'source.env'
        json_file = Path(self.test_dir) / 'target.json'
        
        env_file.write_text('KEY=value\nNUMBER=42')
        
        env = load_env(env_file)
        save_env(json_file, format='json')
        
        assert json_file.exists()


class TestTypeCasting:
    """Test explicit type casting"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.env_file = Path(self.test_dir) / '.env'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_cast_to_int(self):
        """Test casting to int"""
        self.env_file.write_text('PORT=8080')
        load_env(self.env_file)
        
        port = get_env('PORT', cast_type=int)
        assert isinstance(port, int)
        assert port == 8080
    
    def test_cast_to_bool(self):
        """Test casting to bool"""
        self.env_file.write_text('DEBUG=true\nDISABLED=false')
        load_env(self.env_file)
        
        debug = get_env('DEBUG', cast_type=bool)
        disabled = get_env('DISABLED', cast_type=bool)
        
        assert isinstance(debug, bool)
        assert debug is True
        assert disabled is False
    
    def test_cast_to_list(self):
        """Test casting to list"""
        self.env_file.write_text('HOSTS=localhost, 127.0.0.1, example.com')
        load_env(self.env_file)
        
        hosts = get_env('HOSTS', cast_type=list)
        assert isinstance(hosts, list)
        assert len(hosts) == 3
        assert 'localhost' in hosts
    
    def test_default_value(self):
        """Test default values"""
        self.env_file.write_text('KEY1=value1')
        load_env(self.env_file)
        
        val1 = get_env('KEY1', default='default')
        val2 = get_env('MISSING_KEY', default='default')
        
        assert val1 == 'value1'
        assert val2 == 'default'


class TestErrorHandling:
    """Test error handling"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        json_file = Path(self.test_dir) / 'invalid.json'
        json_file.write_text('{ invalid json }')
        
        with pytest.raises(ParseError):
            load_env(json_file)
    
    def test_invalid_yaml(self):
        """Test invalid YAML handling"""
        yaml_file = Path(self.test_dir) / 'invalid.yaml'
        yaml_file.write_text('invalid: yaml: content:')
        
        try:
            with pytest.raises(ParseError):
                load_env(yaml_file)
        except ImportError:
            pytest.skip("PyYAML not installed")
    
    def test_invalid_toml(self):
        """Test invalid TOML handling"""
        toml_file = Path(self.test_dir) / 'invalid.toml'
        toml_file.write_text('[invalid toml content')
        
        try:
            with pytest.raises(ParseError):
                load_env(toml_file)
        except ImportError:
            pytest.skip("tomli not installed")


class TestAttributeAccess:
    """Test attribute-style access"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.env_file = Path(self.test_dir) / '.env'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_attribute_get(self):
        """Test getting values via attributes"""
        self.env_file.write_text('TEST_KEY=test_value')
        env = DotEnv(self.env_file)
        
        assert env.TEST_KEY == 'test_value'
    
    def test_attribute_set(self):
        """Test setting values via attributes"""
        env = DotEnv(self.env_file, auto_load=False, newone=True)
        env.TEST_KEY = 'test_value'
        
        assert env.TEST_KEY == 'test_value'
        assert get_env('TEST_KEY') == 'test_value'


class TestDictionaryAccess:
    """Test dictionary-style access"""
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.env_file = Path(self.test_dir) / '.env'
    
    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_getitem(self):
        """Test __getitem__ access"""
        self.env_file.write_text('KEY=value')
        env = DotEnv(self.env_file)
        
        assert env['KEY'] == 'value'
    
    def test_setitem(self):
        """Test __setitem__ access"""
        env = DotEnv(self.env_file, auto_load=False, newone=True)
        env['KEY'] = 'value'
        
        assert env['KEY'] == 'value'
    
    def test_contains(self):
        """Test __contains__ (in operator)"""
        self.env_file.write_text('KEY=value')
        env = DotEnv(self.env_file)
        
        assert 'KEY' in env
        assert 'MISSING' not in env


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])