#!/usr/bin/env python3

# File: envdot/core.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-12
# Description: Core functionality for dot-env package with full TOML support
# License: MIT

"""Core functionality for dot-env package with full TOML support"""

import os
import sys
import traceback
import re
import hashlib
from fnmatch import fnmatch
import json
import configparser
from pathlib3 import Path  # type: ignore
from typing import Any, Dict, Optional, Union, List
from .exceptions import FileNotFoundError, ParseError, TypeConversionError
import warnings

ENVDOT_CONFIGFILE = ""

try:
    import json5
    HAS_JSON5 = True
except ImportError:
    HAS_JSON5 = False

try:
    import tomli  # Python 3.11+ has tomllib built-in
    HAS_TOML = True
except ImportError:
    try:
        import tomllib as tomli  # Python 3.11+
        HAS_TOML = True
    except ImportError:
        HAS_TOML = False

LOG_LEVEL = os.getenv('LOG_LEVEL', 'CRITICAL')
tprint = None  # type: ignore
SHOW_LOGGING = False

if (len(sys.argv) > 1 and any('--debug' == arg for arg in sys.argv)) or str(os.getenv('DOTENV_DEBUG', os.getenv('DEBUG', False))).lower() in ('1', 'true', 'ok', 'yes', 'on'):
    print("🐞 Debug mode enabled")
    os.environ["DEBUG"] = "1"
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
    os.environ["LOGGING"] = "1"
    LOG_LEVEL = "DEBUG"
    SHOW_LOGGING = True
    try:
        from pydebugger import debug  # type: ignore
    except Exception as e:
        print("For better experience, please install 'pydebugger' [still in the development stage] (pip)")
        def debug(**kwargs):  # type: ignore
            if kwargs:
                for i in kwargs:
                    if not i == 'debug':
                        print(f"[DEBUG (envdot)] [1]: {i} = {kwargs.get(i)}")
else:
    os.environ['NO_LOGGING'] = "1"
    def debug(*args, **kwargs):  # type: ignore
        pass

try:
    from richcolorlog import setup_logging, print_exception as tprint  # type: ignore
    logger = setup_logging(
        name="envdot",
        level=LOG_LEVEL,
        show=SHOW_LOGGING
    )
    HAS_RICHCOLORLOG=True
except:
    HAS_RICHCOLORLOG=False
    import logging

    try:
        from .custom_logging import get_logger  # type: ignore
    except ImportError:
        from custom_logging import get_logger  # type: ignore
    
    logger = get_logger('envdot', level=getattr(logging, LOG_LEVEL.upper(), logging.CRITICAL))

if not tprint:
    def tprint(*args, **kwargs):
        traceback.print_exc(*args, **kwargs)

class TypeDetector:
    """Automatic type detection and conversion"""
    
    @staticmethod
    def auto_detect(value: str) -> Any:
        """
        Automatically detect and convert string to appropriate type
        Supports: bool, int, float, None, and string
        """
        if not isinstance(value, str):
            return value
        
        value = value.strip()
        
        if value.lower() in ('none', 'null', ''):
            return None
        
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0'):
            return False
        
        try:
            if '.' not in value and 'e' not in value.lower() and str(value).isdigit():
                return int(value)
        except (ValueError, AttributeError):
            pass
        
        try:
            return float(value)
        except (ValueError, AttributeError):
            pass
        
        return value
    
    @staticmethod
    def to_string(value: Any) -> str:
        """Convert any value to string for storage"""
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value)


class FileHandler:
    """Handle different file format operations"""
    
    @staticmethod
    def detect_format(filepath: Path) -> str:
        """Detect file format from extension"""
        name = filepath.name
        
        # Handle dotfiles properly
        if name.startswith('.') and len(name.split('.')) == 2:
            ext = name
        else:
            ext = filepath.suffix.lower()
        
        # Detect format
        if ext in ('.yaml', '.yml') or name in ('.yaml', '.yml'):
            return 'yaml'
        elif ext == '.json' or name == '.json':
            return 'json'
        elif ext == '.ini' or name == '.ini':
            return 'ini'
        elif ext in ('.toml', '.tml') or name in ('.toml', '.tml'):
            return 'toml'
        elif ext == '.env' or name == '.env':
            return 'env'
        else:
            return 'env'
    
    @staticmethod
    def load_env_file(filepath: Path) -> Dict[str, str]:
        """Load .env file"""
        env_vars = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                else:
                    raise ParseError(f"Invalid format at line {line_num}: {line}")
        
        return env_vars
    
    @staticmethod
    def load_json_file(filepath: Path) -> Dict[str, str]:
        """Load .json file with fallback to JSON5"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                if HAS_JSON5:
                    data = json5.loads(content)
                else:
                    processed_content = FileHandler._fix_invalid_json(content)
                    data = json.loads(processed_content)
            
            flattened = {}
            FileHandler._flatten_dict(data, flattened)
            return flattened
        except Exception as e:
            raise ParseError(f"Invalid JSON format: {e}")

    @staticmethod
    def _fix_invalid_json(content: str) -> str:
        """Fix common JSON issues"""
        content = content.replace('\\"', '___ESCAPED_DOUBLE___')
        content = content.replace("\\'", '___ESCAPED_SINGLE___')
        content = content.replace("'", '"')
        content = content.replace('___ESCAPED_DOUBLE___', '\\"')
        content = content.replace('___ESCAPED_SINGLE___', "'")
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        return content

    @staticmethod
    def load_yaml_file(filepath: Path) -> Dict[str, str]:
        """Load .yaml/.yml file"""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML support. "
                "Install it with: pip install pyyaml"
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            flattened = {}
            FileHandler._flatten_dict(data, flattened)
            return flattened
        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML format: {e}")
    
    @staticmethod
    def load_ini_file(filepath: Path) -> Dict[str, str]:
        """
        Load .ini file with proper handling of sections and nested structure
        
        INI Structure:
        [section]
        key = value
        
        Will be flattened to: SECTION_KEY = value
        """
        config = configparser.ConfigParser()
        try:
            config.read(filepath, encoding='utf-8')
        except configparser.Error as e:
            raise ParseError(f"Invalid INI format: {e}")
        
        env_vars = {}
        
        # Process each section
        for section in config.sections():
            for key, value in config.items(section):
                # Create hierarchical key: SECTION_KEY
                full_key = f"{section.upper()}_{key.upper()}"
                env_vars[full_key] = value
        
        # Add DEFAULT section items without prefix (standard INI behavior)
        if config.defaults():
            for key, value in config.defaults().items():
                env_vars[key.upper()] = value
        
        return env_vars
    
    @staticmethod
    def load_toml_file(filepath: Path) -> Dict[str, str]:
        """
        Load .toml file with proper nested structure handling
        
        TOML Structure Example:
        [database]
        host = "localhost"
        port = 5432
        
        [database.credentials]
        username = "admin"
        password = "secret"
        
        Will be flattened to:
        DATABASE_HOST = localhost
        DATABASE_PORT = 5432
        DATABASE_CREDENTIALS_USERNAME = admin
        DATABASE_CREDENTIALS_PASSWORD = secret
        """
        if not HAS_TOML:
            raise ImportError(
                "tomli/tomllib is required for TOML support. "
                "Install it with: pip install tomli (Python < 3.11)"
            )
        
        try:
            with open(filepath, 'rb') as f:
                data = tomli.load(f)
            
            flattened = {}
            FileHandler._flatten_dict(data, flattened)
            return flattened
        except Exception as e:
            raise ParseError(f"Invalid TOML format: {e}")
    
    @staticmethod
    def _flatten_dict(d: Any, result: Dict[str, str], prefix: str = '') -> None:
        """
        Recursively flatten nested dictionaries and lists
        
        Examples:
        {"db": {"host": "localhost"}} -> DB_HOST = localhost
        {"items": [1, 2, 3]} -> ITEMS_0 = 1, ITEMS_1 = 2, ITEMS_2 = 3
        """
        if isinstance(d, dict):
            for key, value in d.items():
                new_key = f"{prefix}_{key}".upper() if prefix else key.upper()
                if isinstance(value, (dict, list)):
                    FileHandler._flatten_dict(value, result, new_key)
                else:
                    result[new_key] = str(value) if value is not None else ''
        elif isinstance(d, list):
            for i, item in enumerate(d):
                new_key = f"{prefix}_{i}"
                if isinstance(item, (dict, list)):
                    FileHandler._flatten_dict(item, result, new_key)
                else:
                    result[new_key] = str(item) if item is not None else ''
        else:
            result[prefix] = str(d) if d is not None else ''
    
    @staticmethod
    def save_env_file(filepath: Path, data: Dict[str, Any]) -> None:
        """Save to .env file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for key, value in sorted(data.items()):
                value_str = TypeDetector.to_string(value)
                if ' ' in value_str or '#' in value_str:
                    value_str = f'"{value_str}"'
                f.write(f"{key}={value_str}\n")
    
    @staticmethod
    def save_json_file(filepath: Path, data: Dict[str, Any]) -> None:
        """Save to .json file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def save_yaml_file(filepath: Path, data: Dict[str, Any]) -> None:
        """Save to .yaml file"""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML support. "
                "Install it with: pip install pyyaml"
            )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
    
    @staticmethod
    def save_ini_file(filepath: Path, data: Dict[str, Any]) -> None:
        """Save to .ini file"""
        config = configparser.ConfigParser()
        config['DEFAULT'] = {k: TypeDetector.to_string(v) for k, v in data.items()}
        
        with open(filepath, 'w', encoding='utf-8') as f:
            config.write(f)
    
    @staticmethod
    def save_toml_file(filepath: Path, data: Dict[str, Any]) -> None:
        """Save to .toml file"""
        try:
            import tomli_w  # pip install tomli-w
        except ImportError:
            raise ImportError(
                "tomli-w is required for TOML writing support. "
                "Install it with: pip install tomli-w"
            )
        
        with open(filepath, 'wb') as f:
            tomli_w.dump(data, f)


# class DotEnvMeta(type):
#     """Metaclass to enable attribute-style access and automatic saving"""
    
#     def __call__(cls, *args, **kwargs):
#         instance = super().__call__(*args, **kwargs)
#         return instance
    
#     def __getattribute__(cls, name):
#         try:
#             return super().__getattribute__(name)
#         except AttributeError:
#             global _global_env
#             if hasattr(_global_env, name):
#                 return getattr(_global_env, name)
#             raise
    
#     def __setattr__(cls, name, value):
#         if name.startswith('_') or name in cls.__dict__:
#             super().__setattr__(name, value)
#         else:
#             global _global_env
#             if hasattr(_global_env, name):
#                 setattr(_global_env, name, value)
#             else:
#                 _global_env.__set__(name, value)
    
#     def __getattr__(cls, name):
#         global _global_env
#         if hasattr(_global_env, name):
#             return getattr(_global_env, name)
#         raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

class DotEnvMeta(type):
    """Metaclass to enable attribute-style access and automatic saving"""
    
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        return instance
    
    def __getattribute__(cls, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            global _global_env
            if hasattr(_global_env, name):
                return getattr(_global_env, name)
            raise
    
    def __setattr__(cls, name, value):
        # Internal attributes that should NOT trigger save
        INTERNAL_ATTRS = {'newone', 'hash', 'stat'}
        
        if name.startswith('_') or name in cls.__dict__ or name in INTERNAL_ATTRS:
            super().__setattr__(name, value)
        else:
            global _global_env
            if hasattr(_global_env, name):
                # IMPORTANT: Use object.__setattr__ to bypass __setattr__ instances
                object.__setattr__(_global_env, name, value)
            else:
                _global_env.__set__(name, value)
    
    def __getattr__(cls, name):
        global _global_env
        if hasattr(_global_env, name):
            return getattr(_global_env, name)
        raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

class DotEnv(metaclass=DotEnvMeta):
    """Main class for managing environment variables from multiple file formats"""
    
    def __init__(self, filepath: Optional[Union[str, Path]] = None, auto_load: bool = True, newone: bool = False):
        global ENVDOT_CONFIGFILE
        self._data: Dict[str, Any] = {}
        self._filepath: Optional[Path] = None
        self._format: Optional[str] = None
        # self.newone = newone

        object.__setattr__(self, 'newone', newone)
        object.__setattr__(self, 'hash', '')
        
        if filepath and Path(filepath).is_file():
            self._filepath = Path(filepath)
            ENVDOT_CONFIGFILE = filepath
        else:
            self._filepath = self._find_config_file()
        
        if auto_load and self._filepath and self._filepath.exists():
            self.load()
    
    # @staticmethod
    def _find_config_file(self) -> Optional[Path]:
        """
        Find common configuration files in current directory
        
        Search order (by priority):
        1. .env (most common, highest priority)
        2. .env.local (local overrides)
        3. config.toml (recommended for Python projects)
        4. pyproject.toml (Python project config)
        5. config.yaml / config.yml (human-readable)
        6. config.json (structured data)
        7. config.ini (legacy support)
        8. Other dotfiles: .toml, .yaml, .yml, .json, .ini
        
        Returns:
            Path to first found config file, or None if not found
        """

        global ENVDOT_CONFIGFILE

        # Priority order: .env first, then recommended formats, then legacy
        common_files = [
            '.env',              # Standard environment file (highest priority)
            '.env.local',        # Local environment overrides
            'config.toml',       # Modern Python config (recommended)
            'pyproject.toml',    # Python project metadata with config
            'config.yaml',       # Human-readable config
            'config.yml',        # Alternative YAML extension
            'config.json',       # Structured data config
            'config.ini',        # Legacy config format
            '.toml',             # Dotfile TOML
            '.yaml',             # Dotfile YAML
            '.yml',              # Dotfile YAML alt
            '.json',             # Dotfile JSON
            '.ini',              # Dotfile INI
        ]
        
        for filename in common_files:
            filepath = Path(filename)
            if filepath.exists():
                logger.debug(f"Auto-detected config file: {filepath}")
                debug(filepath = filepath)
                object.__setattr__(self, 'hash', Path(filepath).hash())
                ENVDOT_CONFIGFILE = filepath
                return filepath
        
        logger.debug("No config file found in current directory")
        return None

    def find_settings_recursive(self, start_path=None, max_depth=0, filename='.env', exceptions=['node_modules', 'venv', '__pycache__']):
        """
        Recursively search for configuration file downwards from start_path
        
        Args:
            start_path: Starting directory (default: current directory)
            max_depth: Maximum depth to search (default: 5)
            filename: Filename(s) to search for (default: '.env')
            exceptions: Directories to skip (default: ['node_modules', 'venv', '__pycache__'])
        
        Returns:
            Path to found config file, or None
        
        Search Priority:
            If filename is '.env' (default), searches in order:
            1. .env, .env.local
            2. config.toml, pyproject.toml
            3. config.yaml, config.yml
            4. config.json
            5. config.ini
            6. Dotfiles: .toml, .yaml, .yml, .json, .ini
        """
        filenames = [filename] if not isinstance(filename, list) else filename
        
        # Add default config files with priority order if not already specified
        default_files = [
            '.env',           # Highest priority
            '.env.local',     # Local overrides
            'config.toml',    # Recommended for Python
            'pyproject.toml', # Python project config
            '.toml',          # Dotfile TOML
            'config.yaml',    # Human-readable
            'config.yml',     # YAML alternative
            '.yaml',          # Dotfile YAML
            '.yml',           # Dotfile YAML alt
            'config.json',    # Structured data
            '.json',          # Dotfile JSON
            'config.ini',     # Legacy
            '.ini',           # Dotfile INI
        ]
        
        for default_file in default_files:
            if not any(f == default_file for f in filenames):
                filenames.append(default_file)

        if start_path is None:
            start_path = os.getcwd()

        start_path = str(start_path)
        
        def search_directory(path, current_depth=0):
            if current_depth > max_depth:
                return None
            
            # Check each filename in priority order
            for f in filenames:
                settings_path = os.path.join(path, f)
                if os.path.isfile(settings_path):
                    logger.debug(f"Found config file recursively: {settings_path}")
                    self.hash = Path(settings_path).hash()
                    return Path(settings_path)
            
            # Search in subdirectories
            if current_depth < max_depth:
                try:
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if (os.path.isdir(item_path) and 
                            item not in exceptions and 
                            '-env' not in item):
                            result = search_directory(item_path, current_depth + 1)
                            if result:
                                return result
                except (PermissionError, OSError):
                    pass
            
            return None
        
        return search_directory(start_path)
    
    def load(self, filepath: Optional[Union[str, Path]] = None, 
         override: bool = True, apply_to_os: bool = True,
         store_typed: bool = True, recursive: bool = True, newone: bool = False, os_overwrite: bool = False, **kwargs) -> 'DotEnv':
        """Load environment variables from file"""
        debug(filepath = filepath)
        if filepath:
            self._filepath = Path(filepath)
        
        if not self._filepath:
            self._filepath = self.find_settings_recursive(
                kwargs.get('start_path', None),
                kwargs.get('max_depth', 0),
                kwargs.get('filename', ".env"),
                kwargs.get('exceptions', ['node_modules', 'venv', '__pycache__']),
            )

        debug(self__filepath = self._filepath)
        debug(newone = newone)
        debug(self_newone = self.newone)

        if not self._filepath and (newone or self.newone):
            debug("No configuration file specified, creating new .env")
            warnings.warn("No configuration file specified, creating new .env")
            self._filepath = Path.cwd() / '.env'
            with open(self._filepath, 'w') as f:  # type: ignore
                f.write('')
        
        if self._filepath and not self._filepath.exists():
            return self
        elif not self._filepath:
            return self
        
        self._format = FileHandler.detect_format(self._filepath)
        
        loaders = {
            'env': FileHandler.load_env_file,
            'json': FileHandler.load_json_file,
            'yaml': FileHandler.load_yaml_file,
            'ini': FileHandler.load_ini_file,
            'toml': FileHandler.load_toml_file,
        }
        
        loader = loaders.get(self._format)
        if not loader:
            raise ParseError(f"Unsupported file format: {self._format}")
        
        raw_data = loader(self._filepath)
        debug(raw_data = raw_data)
        
        debug(apply_to_os = apply_to_os)
        debug(os_overwrite = os_overwrite)

        # Filter internal attributes
        INTERNAL_ATTRS = {'hash', 'newone', 'stat'}
        
        # If override=True, delete keys that do not exist in the file
        if override:
            keys_to_remove = []
            for key in list(self._data.keys()):
                if key.lower() not in INTERNAL_ATTRS and key not in raw_data:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._data[key]
                if apply_to_os and key in os.environ:
                    del os.environ[key]
        
        # Load/update data from file
        for key, value in raw_data.items():
            # SKIP internal attributes
            if key.lower() in INTERNAL_ATTRS:
                continue
            
            typed_value = TypeDetector.auto_detect(value)
            
            if override or key not in self._data:
                self._data[key] = typed_value

            if apply_to_os:
                if not os.getenv(key, False) or os_overwrite:
                    os.environ[key] = TypeDetector.to_string(typed_value)

        return self

    def check_file(self, configfile):
        """Check if config file has changed using hash comparison"""
        if not configfile:
            return True
        
        # Initialize hash if it doesn't exist yet (BYPASS __setattr__)
        if not hasattr(self, 'hash') or not self.hash:
            new_hash = Path(configfile).hash()
            object.__setattr__(self, 'hash', new_hash)
            return True
        
        # Calculate the hash of the current file
        current_hash = Path(configfile).hash()
        
        # Compare
        if self.hash == current_hash:
            return True  # Files are NOT changed
        else:
            # Update hash BYPASS __setattr__
            object.__setattr__(self, 'hash', current_hash)
            return False  # File CHANGED
    
    def get(self, key: str, default: Any = None, cast_type: Optional[type] = None, reload: Optional[bool] = False) -> Any:
        """Get environment variable with automatic type detection"""

        debug(self__filepath = self._filepath)
        if getattr(self, 'hash'):
            debug(self_hash = self.hash)
            
        debug(reload = reload)

        if reload or not self.check_file(self._filepath):
            self.load(self._filepath, apply_to_os=True)
            new_hash = Path(self._filepath).hash()
            debug(new_hash = new_hash)
            object.__setattr__(self, 'hash', new_hash)
            object.__setattr__(self, 'hash', new_hash)

        value = self._data.get(key)
        debug(value = value)

        if value is None:
            value = os.environ.get(key)
            if value is not None:
                value = TypeDetector.auto_detect(value)
        
        debug(default = default)
        if value is None:
            return default
        
        debug(cast_type = cast_type)
        if cast_type:
            try:
                if cast_type == bool:
                    if isinstance(value, bool):
                        return value
                    if isinstance(value, str):
                        return value.lower() in ('true', 'yes', 'on', '1')
                    return bool(value)
                elif cast_type == list:
                    value = [i.strip() for i in re.split(r"[, ]+", value) if i]
                    return value
                elif cast_type == tuple:
                    value = [i.strip() for i in re.split(r"[, ]+", value) if i]
                    return tuple(value)
                return cast_type(value)
            except (ValueError, TypeError) as e:
                raise TypeConversionError(f"Cannot convert '{value}' to {cast_type.__name__}: {e}")
        debug(value = value)
        return value
    
    def get_config(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def set(self, key: str, value: Any, apply_to_os: bool = True) -> 'DotEnv':
        """Set environment variable"""
        self._data[key] = value
        
        if apply_to_os:
            os.environ[key] = TypeDetector.to_string(value)
        
        return self

    def set_config(self, *args, **kwargs):
        return self.set(*args, **kwargs)

    def setenv(self, *args, **kwargs):
        return self.set(*args, **kwargs)

    def getenv(self, *args, **kwargs):
        return self.get(*args, **kwargs)
    
    def save(self, filepath: Optional[Union[str, Path]] = None, 
             format: Optional[str] = None) -> 'DotEnv':
        """Save current environment variables to file"""
        save_path = Path(filepath) if filepath else self._filepath
        
        if not save_path:
            return self
        
        save_format = format or FileHandler.detect_format(save_path)
        
        savers = {
            'env': FileHandler.save_env_file,
            'json': FileHandler.save_json_file,
            'yaml': FileHandler.save_yaml_file,
            'ini': FileHandler.save_ini_file,
            'toml': FileHandler.save_toml_file,
        }
        
        saver = savers.get(save_format)
        if not saver:
            raise ParseError(f"Unsupported file format for saving: {save_format}")
        
        saver(save_path, self._data)
        return self

    def save_env(self, *args, **kwargs):
        return self.save(*args, **kwargs)
    
    def delete(self, key: str, remove_from_os: bool = True) -> 'DotEnv':
        """Delete environment variable"""
        if key in self._data:
            del self._data[key]
        
        if remove_from_os and key in os.environ:
            del os.environ[key]
        
        return self
    
    def all(self) -> Dict[str, Any]:
        """Get all environment variables as dictionary"""
        data = os.environ.copy()
        data.update(self._data)
        return data

    def show(self, all = False):
        if all:
            return self.all()
        return self._data.copy()

    def as_dict(self, all = False):
        if all:
            return self.all()
        return self._data
    
    def data(self, all = False):
        if all:
            return self.all()
        return self._data
    
    def keys(self, all = False) -> list:
        """Get all variable names"""
        if all:
            data = self.all()
            return list(data.keys())
        return list(self._data.keys())
    
    def clear(self, clear_os: bool = False) -> 'DotEnv':
        """Clear all stored variables"""
        if clear_os:
            for key in self._data.keys():
                if key in os.environ:
                    del os.environ[key]
        
        self._data.clear()
        return self
    
    def find(self, 
             pattern: str, 
             mode: str = 'wildcard',
             case_sensitive: bool = True,
             return_dict: bool = True, reload: bool = False) -> Union[Dict[str, Any], List[tuple]]:
        """
        Find configuration keys matching a pattern
        
        Args:
            pattern: Search pattern (wildcard, regex, or substring)
            mode: Search mode - 'wildcard', 'regex', 'contains', or 'startswith', 'endswith'
            case_sensitive: Whether search is case-sensitive (default: True)
            return_dict: Return as dict if True, list of tuples if False
            
        Returns:
            Dictionary or list of (key, value) tuples matching the pattern
            
        Examples:
            >>> env = DotEnv('.env')
            >>> env.load()
            
            # Wildcard search (Unix shell-style)
            >>> env.find('DB_*')
            {'DB_HOST': 'localhost', 'DB_PORT': 5432, 'DB_NAME': 'mydb'}
            
            >>> env.find('*_PORT')
            {'DB_PORT': 5432, 'REDIS_PORT': 6379}
            
            # Regex search
            >>> env.find(r'^API_\w+_KEY$', mode='regex')
            {'API_PUBLIC_KEY': 'xxx', 'API_SECRET_KEY': 'yyy'}
            
            # Contains search
            >>> env.find('password', mode='contains', case_sensitive=False)
            {'DB_PASSWORD': 'secret', 'ADMIN_PASSWORD': 'admin123'}
            
            # Starts with
            >>> env.find('REDIS', mode='startswith')
            {'REDIS_HOST': 'localhost', 'REDIS_PORT': 6379}
            
            # Ends with
            >>> env.find('_URL', mode='endswith')
            {'API_URL': 'https://api.example.com', 'DATABASE_URL': 'postgres://...'}
        """

        pattern_lower = ""  # type: ignore

        debug(self__filepath = self._filepath)
        if getattr(self, 'hash'):
            debug(self_hash = self.hash)
            
        debug(reload = reload)

        if reload or not self.check_file(self._filepath):
            self.load(self._filepath, apply_to_os=True)
            new_hash = Path(self._filepath).hash()
            debug(new_hash = new_hash)
            object.__setattr__(self, 'hash', new_hash)
            object.__setattr__(self, 'hash', new_hash)

        results = {}
        
        # Prepare pattern based on case sensitivity
        if not case_sensitive:
            pattern_lower = pattern.lower()
        
        data = os.environ.copy()
        data.update(self._data)

        # for key, value in self._data.items():
        for key, value in data.items():  # type: ignore
            match = False
            search_key = key if case_sensitive else key.lower()
            search_pattern = pattern if case_sensitive else pattern_lower

            if not search_pattern:
                return {}
            
            if mode == 'wildcard':
                # Unix shell-style wildcards: *, ?, [seq], [!seq]
                match = fnmatch(search_key, search_pattern)
                
            elif mode == 'regex':
                # Regular expression matching
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    match = bool(re.search(search_pattern, key, flags=flags))
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {e}")
                    
            elif mode == 'contains':
                # Substring matching
                match = search_pattern in search_key
                
            elif mode == 'startswith':
                # Prefix matching
                match = search_key.startswith(search_pattern)
                
            elif mode == 'endswith':
                # Suffix matching
                match = search_key.endswith(search_pattern)
                
            else:
                raise ValueError(f"Invalid mode: {mode}. Use 'wildcard', 'regex', 'contains', 'startswith', or 'endswith'")
            
            if match:
                results[key] = value
        
        return results if return_dict else list(results.items())
    
    def find_wildcard(self, pattern: str, **kwargs) -> Dict[str, Any]:
        """Shortcut for wildcard search"""
        return self.find(pattern, mode='wildcard', **kwargs)
    
    def find_regex(self, pattern: str, **kwargs) -> Dict[str, Any]:
        """Shortcut for regex search"""
        return self.find(pattern, mode='regex', **kwargs)
    
    def find_contains(self, pattern: str, **kwargs) -> Dict[str, Any]:
        """Shortcut for contains search"""
        return self.find(pattern, mode='contains', **kwargs)
    
    def find_keys(self, pattern: str, mode: str = 'wildcard', **kwargs) -> List[str]:
        """
        Find keys matching pattern, return only keys
        
        Returns:
            List of matching keys
        """
        results = self.find(pattern, mode=mode, return_dict=True, **kwargs)
        return list(results.keys())
    
    def find_values(self, pattern: str, mode: str = 'wildcard', **kwargs) -> List[Any]:
        """
        Find keys matching pattern, return only values
        
        Returns:
            List of matching values
        """
        results = self.find(pattern, mode=mode, return_dict=True, **kwargs)
        return list(results.values())
    
    def filter(self, predicate) -> Dict[str, Any]:
        """
        Filter config using a custom predicate function
        
        Args:
            predicate: Function that takes (key, value) and returns bool
            
        Returns:
            Dictionary of items where predicate returns True
            
        Examples:
            >>> # Find all integer ports
            >>> env.filter(lambda k, v: k.endswith('_PORT') and isinstance(v, int))
            
            >>> # Find all boolean debug flags
            >>> env.filter(lambda k, v: 'DEBUG' in k and isinstance(v, bool))
            
            >>> # Find all non-empty strings
            >>> env.filter(lambda k, v: isinstance(v, str) and v.strip())
        """
        return {k: v for k, v in self._data.items() if predicate(k, v)}
    
    def search(self, 
               key_pattern: Optional[str] = None,
               value_pattern: Optional[str] = None,
               mode: str = 'wildcard',
               **kwargs) -> Dict[str, Any]:
        """
        Advanced search by both key and value patterns
        
        Args:
            key_pattern: Pattern to match keys
            value_pattern: Pattern to match values (as strings)
            mode: Search mode
            **kwargs: Additional arguments for find()
            
        Returns:
            Dictionary matching both patterns (AND logic)
            
        Examples:
            >>> # Find database configs with 'localhost'
            >>> env.search(key_pattern='DB_*', value_pattern='*localhost*')
            
            >>> # Find all API keys containing 'prod'
            >>> env.search(key_pattern='*_KEY', value_pattern='*prod*')
        """

        results = os.environ.copy()
        results.update(self._data)

        # results = self._data.copy()
        
        # Filter by key pattern
        if key_pattern:
            results = {k: v for k, v in results.items() 
                      if k in self.find(key_pattern, mode=mode, **kwargs)}
        
        # Filter by value pattern
        if value_pattern:
            filtered = {}
            for key, value in results.items():
                value_str = str(value) if value is not None else ''
                
                if mode == 'wildcard':
                    if fnmatch(value_str, value_pattern):
                        filtered[key] = value
                elif mode == 'regex':
                    if re.search(value_pattern, value_str):
                        filtered[key] = value
                elif mode == 'contains':
                    if value_pattern in value_str:
                        filtered[key] = value
                        
            results = filtered
        
        return results

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        elif name in os.environ:
            return TypeDetector.auto_detect(os.environ[name])
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    # def __setattr__(self, name: str, value: Any) -> None:
    #     if name.startswith('_'):
    #         super().__setattr__(name, value)
    #     else:
    #         self.set(name, value, apply_to_os=True)
    #         self.save()

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attributes with protection for internal attributes"""
        # Internal attributes that should NOT be included in _data and auto-save
        INTERNAL_ATTRS = {'newone', 'hash', 'stat'}
        
        if name.startswith('_') or name in INTERNAL_ATTRS:
            # Bypass custom logic, set it directly to the object
            object.__setattr__(self, name, value)
        else:
            # User attribute, save to _data and file
            if hasattr(self, '_data'):
                self.set(name, value, apply_to_os=True)
                if hasattr(self, '_filepath') and self._filepath:
                    self.save()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        return key in self._data or key in os.environ
    
    def __repr__(self) -> str:
        return f"DotEnv(filepath={self._filepath}, vars={len(self._data)})"

    def __call__(self, key: str, value: Any = None, default: Any = None) -> Any:
        if value is not None:
            self.set(key, value)
            self.save()
            return self
        else:
            return self.get(key, default)


_global_env = DotEnv(auto_load=False)


def load_env(filepath: Optional[Union[str, Path]] = None, 
             apply_to_os=True,
             auto_replace_getenv: bool = True,
             patch_os: bool = True,
             debugging: bool = False,
             **kwargs) -> DotEnv:

    """Convenience function to load environment variables"""
    if debugging:
        os.environ['DEBUG'] = '1'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['LOGGING'] = '1'
        os.environ.pop('NO_LOGGING', None)

    global _global_env

    debug(_global_env = _global_env)
    
    debug(auto_replace_getenv = auto_replace_getenv)
    debug(patch_os = patch_os)

    if auto_replace_getenv:
        from .helpers import replace_os_getenv
        replace_os_getenv()
    
    if patch_os:
        from .helpers import patch_os_module
        patch_os_module()
    
    debug(filepath = filepath)
    debug(_global_env = _global_env)
    _global_env = DotEnv(filepath=filepath, auto_load=kwargs.get('auto_load', kwargs.get('reload', False)))
    logger.debug(f"kwargs: {kwargs}")
    kwargs.pop('reload', None)
    _global_env.load(apply_to_os=apply_to_os, **kwargs)
    # _global_env.load(**kwargs)
    return _global_env

def Env(*args, **kwargs):
    return load_env(*args, **kwargs)

def show():
    global _global_env
    return _global_env.show()

def data():
    global _global_env
    return _global_env.show()

def get_env(key: str, default: Any = None, cast_type: Optional[type] = None) -> Any:
    """Convenience function to get environment variable"""
    return _global_env.get(key, default, cast_type)

def set_env(key: str, value: Optional[Any] = None, **kwargs) -> DotEnv:
    """Convenience function to set environment variable"""
    if isinstance(key, dict) and not value:
        _key = list(key.keys())[0]
        _value = key.get(_key)
        return _global_env.set(_key, _value, **kwargs)    
    return _global_env.set(key, value, **kwargs)


def save_env(filepath: Optional[Union[str, Path]] = None, **kwargs) -> DotEnv:
    """Convenience function to save environment variables"""
    return _global_env.save(filepath, **kwargs)

# ============================================================================
# Global convenience functions
# ============================================================================

def find_env(pattern: str, mode: str = 'wildcard', **kwargs) -> Dict[str, Any]:
    """
    Global function to find environment variables
    
    Examples:
        >>> from envdot import load_env, find_env
        >>> load_env()
        >>> find_env('DB_*')
        >>> find_env(r'^\w+_PORT$', mode='regex')
    """
    global _global_env
    return _global_env.find(pattern, mode=mode, **kwargs)  # type: ignore


def filter_env(predicate) -> Dict[str, Any]:
    """
    Global function to filter environment variables
    
    Examples:
        >>> from envdot import load_env, filter_env
        >>> load_env()
        >>> filter_env(lambda k, v: isinstance(v, int) and v > 1000)
    """
    global _global_env
    return _global_env.filter(predicate)

def search_env(pattern: str, value: Optional[str] = None, mode: str = 'wildcard', **kwargs) -> Dict[str, Any]:
    global _global_env
    return _global_env.search(pattern, value, mode, **kwargs)
