"""Core functionality for dot-env package with full TOML support"""

import os
import sys
import traceback
import re
import json
import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Union
from .exceptions import FileNotFoundError, ParseError, TypeConversionError

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

if (len(sys.argv) > 1 and any('--debug' == arg or '-d' == arg for arg in sys.argv)) or (os.getenv('DEBUG') and str(os.getenv('DEBUG', '0')).lower() in ['1', 'true', 'yes', 'ok']):
    print("🐞 Debug mode enabled")
    os.environ["DEBUG"] = "1"
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
else:
    os.environ['NO_LOGGING'] = "1"

tprint: Optional[traceback.print_exc] = None

def get_logger(name: str = 'envdot', level: Optional[int] = None, prefer_rich: bool = True, force_plain: bool = False):
    """Return a configured logger instance."""
    import logging
    global tprint

    if level is None:
        level = logging.DEBUG if str(os.getenv("DEBUG", "")).lower() in ("1", "true", "yes") else logging.INFO

    if force_plain or str(os.getenv("FORCE_PLAIN_LOG", "")).lower() in ("1", "true", "yes"):
        logging.basicConfig(level=level)
        return logging.getLogger(name)

    if prefer_rich:
        try:
            from richcolorlog import setup_logging as _setup, print_exception as tprint
            if name and name == '__main__': name = 'envdot'
            try:
                logger_obj = _setup(name=name, level=level)
            except TypeError:
                try:
                    logger_obj = _setup()
                except Exception:
                    import logging as _logging
                    _logging.basicConfig(level=level)
                    logger_obj = _logging.getLogger(name)
            return logger_obj
        except Exception:
            import logging as _logging
            _logging.basicConfig(level=level)
            return _logging.getLogger(name)

    import logging as _logging
    _logging.basicConfig(level=level)
    return _logging.getLogger(name)

if not tprint:
    def tprint(*args, **kwargs):
        traceback.print_exc(*args, **kwargs)

logger = get_logger()

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
        if name.startswith('_') or name in cls.__dict__:
            super().__setattr__(name, value)
        else:
            global _global_env
            if hasattr(_global_env, name):
                setattr(_global_env, name, value)
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
        self._data: Dict[str, Any] = {}
        self._filepath: Optional[Path] = None
        self._format: Optional[str] = None
        self.newone = newone
        
        if filepath:
            self._filepath = Path(filepath)
        else:
            self._filepath = self._find_config_file()
        
        if auto_load and self._filepath and self._filepath.exists():
            self.load()
    
    @staticmethod
    def _find_config_file() -> Optional[Path]:
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
                return filepath
        
        logger.debug("No config file found in current directory")
        return None

    def find_settings_recursive(self, start_path=None, max_depth=5, filename='.env', exceptions=['node_modules', 'venv', '__pycache__']):
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
             store_typed: bool = True, recursive: bool = True, newone: bool = False) -> 'DotEnv':
        """Load environment variables from file"""
        if filepath:
            self._filepath = Path(filepath)
        
        if not self._filepath:
            self._filepath = self.find_settings_recursive()
        
        if not self._filepath and (newone or self.newone):
            print("No configuration file specified, creating new .env")
            self._filepath = Path.cwd() / '.env'
            with open(self._filepath, 'w') as f:
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
        
        for key, value in raw_data.items():
            typed_value = TypeDetector.auto_detect(value)
            
            if override or key not in self._data:
                self._data[key] = typed_value
            
            if apply_to_os:
                os.environ[key] = TypeDetector.to_string(typed_value)
        
        return self
    
    def get(self, key: str, default: Any = None, cast_type: Optional[type] = None) -> Any:
        """Get environment variable with automatic type detection"""
        value = self._data.get(key)
        
        if value is None:
            value = os.environ.get(key)
            if value is not None:
                value = TypeDetector.auto_detect(value)
        
        if value is None:
            return default
        
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
        
        return value
    
    def set(self, key: str, value: Any, apply_to_os: bool = True) -> 'DotEnv':
        """Set environment variable"""
        self._data[key] = value
        
        if apply_to_os:
            os.environ[key] = TypeDetector.to_string(value)
        
        return self

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
        return self._data.copy()

    def show(self):
        return self._data.copy()

    def as_dict(self):
        return self._data
    
    def data(self):
        return self._data
    
    def keys(self) -> list:
        """Get all variable names"""
        return list(self._data.keys())
    
    def clear(self, clear_os: bool = False) -> 'DotEnv':
        """Clear all stored variables"""
        if clear_os:
            for key in self._data.keys():
                if key in os.environ:
                    del os.environ[key]
        
        self._data.clear()
        return self
    
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        elif name in os.environ:
            return TypeDetector.auto_detect(os.environ[name])
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self.set(name, value, apply_to_os=True)
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
             auto_replace_getenv: bool = True,
             patch_os: bool = True,
             **kwargs) -> DotEnv:
    """Convenience function to load environment variables"""
    global _global_env
    
    if auto_replace_getenv:
        from .helpers import replace_os_getenv
        replace_os_getenv()
    
    if patch_os:
        from .helpers import patch_os_module
        patch_os_module()
    
    _global_env = DotEnv(filepath=filepath, auto_load=False)
    logger.debug(f"kwargs: {kwargs}")
    _global_env.load(**kwargs)
    return _global_env


def show():
    global _global_env
    return _global_env.show()


def data():
    global _global_env
    return _global_env.show()


def get_env(key: str, default: Any = None, cast_type: Optional[type] = None) -> Any:
    """Convenience function to get environment variable"""
    return _global_env.get(key, default, cast_type)


def set_env(key: str, value: Any, **kwargs) -> DotEnv:
    """Convenience function to set environment variable"""
    return _global_env.set(key, value, **kwargs)


def save_env(filepath: Optional[Union[str, Path]] = None, **kwargs) -> DotEnv:
    """Convenience function to save environment variables"""
    return _global_env.save(filepath, **kwargs)