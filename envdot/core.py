"""Core functionality for dot-env package"""

import os
import re
import json
import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Union
from .exceptions import FileNotFoundError, ParseError, TypeConversionError
try:
    import json5  # pip install json5
    HAS_JSON5 = True
except ImportError:
    HAS_JSON5 = False

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
        
        # Strip whitespace
        value = value.strip()
        
        # Check for None/null
        if value.lower() in ('none', 'null', ''):
            return None
        
        # Check for boolean
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0'):
            return False
        
        # Check for integer
        try:
            if '.' not in value and 'e' not in value.lower() and str(value).isdigit():
                return int(value)
        except (ValueError, AttributeError):
            pass
        
        # Check for float
        try:
            return float(value)
        except (ValueError, AttributeError):
            pass
        
        # Return as string
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
        # print(f"filepath: {filepath}, name: '{filepath.name}'")
        
        # Method 1: Handle dotfiles properly
        name = filepath.name
        
        # Untuk file seperti '.json', '.env' - ini adalah dotfiles, bukan file dengan ekstensi
        if name.startswith('.') and len(name.split('.')) == 2:
            # Ini adalah dotfile seperti '.json', '.env'
            ext = name  # seluruh nama file adalah 'ekstensi'
            # print(f"Dotfile detected: {ext}")
        else:
            # File normal dengan ekstensi
            ext = filepath.suffix.lower()
            # print(f"Normal file extension: {ext}")
        
        # Deteksi format
        if ext in ('.yaml', '.yml') or name in ('.yaml', '.yml'):
            return 'yaml'
        elif ext == '.json' or name == '.json':
            return 'json'
        elif ext == '.ini' or name == '.ini':
            return 'ini'
        elif ext == '.env' or name == '.env':
            return 'env'
        else:
            return 'env'  # Default to .env format
    
    @staticmethod
    def load_env_file(filepath: Path) -> Dict[str, str]:
        """Load .env file"""
        env_vars = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                else:
                    raise ParseError(f"Invalid format at line {line_num}: {line}")
        
        return env_vars
    
    @staticmethod
    def load_json_file(filepath: Path) -> Dict[str, str]:
        """Load .json file with fallback to JSON5 for invalid JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try standard JSON first
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                if HAS_JSON5:
                    # Use JSON5 which supports single quotes and trailing commas
                    data = json5.loads(content)
                else:
                    # Fallback to our preprocessor
                    processed_content = FileHandler._fix_invalid_json(content)
                    data = json.loads(processed_content)
            
            # Flatten nested structures
            flattened = {}
            FileHandler._flatten_dict(data, flattened)
            return flattened
        except Exception as e:
            raise ParseError(f"Invalid JSON format: {e}")

    @staticmethod
    def _fix_invalid_json(content: str) -> str:
        """
        Fix common JSON issues:
        1. Single quotes to double quotes
        2. Trailing commas
        3. Escaped characters handling
        """
        # Step 1: Protect escaped sequences
        content = content.replace('\\"', '___ESCAPED_DOUBLE___')
        content = content.replace("\\'", '___ESCAPED_SINGLE___')
        
        # Step 2: Replace single quotes with double quotes
        content = content.replace("'", '"')
        
        # Step 3: Restore protected sequences
        content = content.replace('___ESCAPED_DOUBLE___', '\\"')
        content = content.replace('___ESCAPED_SINGLE___', "'")
        
        # Step 4: Remove trailing commas before closing braces/brackets
        # Remove trailing comma before }
        content = re.sub(r',\s*}', '}', content)
        # Remove trailing comma before ]
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
        """Load .ini file"""
        config = configparser.ConfigParser()
        try:
            config.read(filepath, encoding='utf-8')
        except configparser.Error as e:
            raise ParseError(f"Invalid INI format: {e}")
        
        env_vars = {}
        for section in config.sections():
            for key, value in config.items(section):
                # Prefix keys with section name
                full_key = f"{section.upper()}_{key.upper()}"
                env_vars[full_key] = value
        
        # Also add items from DEFAULT section without prefix
        if config.defaults():
            for key, value in config.defaults().items():
                env_vars[key.upper()] = value
        
        return env_vars
    
    @staticmethod
    def _flatten_dict(d: Any, result: Dict[str, str], prefix: str = '') -> None:
        """Recursively flatten nested dictionaries"""
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
                # Quote values with spaces
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

class DotEnvMeta(type):
    """
    Metaclass to enable attribute-style access and automatic saving on assignment
    """
    
    def __call__(cls, *args, **kwargs):
        """Called when class is instantiated: config = DotEnv()"""
        instance = super().__call__(*args, **kwargs)
        return instance
    
    def __getattribute__(cls, name):
        """Handle attribute access on class level: DotEnv.DEBUG_SERVER"""
        # First check if it's a regular class attribute
        try:
            return super().__getattribute__(name)
        except AttributeError:
            # If not found, try to get from global instance
            global _global_env
            if hasattr(_global_env, name):
                return getattr(_global_env, name)
            raise
    
    def __setattr__(cls, name, value):
        """Handle attribute assignment on class level: DotEnv.DEBUG_SERVER = True"""
        # Allow setting regular class attributes
        if name.startswith('_') or name in cls.__dict__:
            super().__setattr__(name, value)
        else:
            # Set on global instance and save
            global _global_env
            if hasattr(_global_env, name):
                setattr(_global_env, name, value)
            else:
                # For new attributes, use __set__ method
                _global_env.__set__(name, value)
    
    def __getattr__(cls, name):
        """Fallback for attribute access"""
        global _global_env
        if hasattr(_global_env, name):
            return getattr(_global_env, name)
        raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

class DotEnv(metaclass=DotEnvMeta):
    """Main class for managing environment variables from multiple file formats"""
    
    def __init__(self, filepath: Optional[Union[str, Path]] = None, auto_load: bool = True, newone: bool = False):
        """
        Initialize DotEnv instance
        
        Args:
            filepath: Path to configuration file. If None, searches for common files
            auto_load: Automatically load the file on initialization
        """
        self._data: Dict[str, Any] = {}
        self._filepath: Optional[Path] = None
        self._format: Optional[str] = None
        self.newone = newone
        
        if filepath:
            self._filepath = Path(filepath)
        else:
            # Auto-detect common config files
            self._filepath = self._find_config_file()
        
        if auto_load and self._filepath and self._filepath.exists():
            self.load()
    
    @staticmethod
    def _find_config_file() -> Optional[Path]:
        """Find common configuration files in current directory"""
        common_files = ['.env', 'config.json', 'config.yaml', 'config.yml', 'config.ini']
        for filename in common_files:
            filepath = Path(filename)
            if filepath.exists():
                return filepath
        return None

    def find_settings_recursive(self, start_path=None, max_depth=5, filename='.env', exceptions=['node_modules', 'venv', '__pycache__']):
        """
        Recursively search for configuration (.env/.json/.yml) file downwards from start_path
        Returns the full path of configuration file if found, None otherwise
        """

        filenames = [filename] if not isinstance(filename, list) else filename
        
        # Add default config files if not already specified
        default_files = ['.json', '.yaml', '.yml']
        for default_file in default_files:
            if not any(f.endswith(default_file) for f in filenames):
                filenames.append(default_file)

        if start_path is None:
            start_path = os.getcwd()

        # print(f"filenames: {filenames}")

        # Ensure start_path is string
        start_path = str(start_path)
        
        def search_directory(path, current_depth=0):
            if current_depth > max_depth:
                return None
            
            # Check each filename in current directory
            for f in filenames:
                settings_path = os.path.join(path, f)
                # print(f"checking: {settings_path}")
                if os.path.isfile(settings_path):
                    # print(f"FOUND FILE CONFIG: {settings_path}")
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
        """
        Load environment variables from file
        
        Args:
            filepath: Path to configuration file (uses initialized path if None)
            override: Override existing values in internal storage
            apply_to_os: Apply loaded variables to os.environ
            store_typed: Store typed values internally (recommended: True)
            
        Returns:
            self for method chaining
            
        Note:
            os.environ only stores strings. Use env.get() or get_env() 
            to retrieve typed values, not os.getenv()
        """

        # print(f"filepath: {filepath}")

        if filepath:
            self._filepath = Path(filepath)
        
        # print(f"self._filepath [1]: {self._filepath}")

        if not self._filepath:
            self._filepath = self.find_settings_recursive()

        # print(f"self._filepath [2]: {self._filepath}")
        
        if not self._filepath and (newone or self.newone):
            # raise FileNotFoundError("No configuration (.env/.json/.yml) file specified")
            print("No configuration (.env/.json/.yml) file specified, create new one")
            self._filepath = Path.cwd() / '.env'
            with open(self._filepath, 'w') as f:
                f.write('')
        
        if self._filepath and not self._filepath.exists():
            # raise FileNotFoundError(f"File not found: {self._filepath}")
            # print(f"File not found: {self._filepath}")
            return self
        elif not self._filepath:
            return self
        
        # Detect format
        self._format = FileHandler.detect_format(self._filepath)
        # print(f"self._format: {self._format}")
        
        # Load based on format
        loaders = {
            'env': FileHandler.load_env_file,
            'json': FileHandler.load_json_file,
            'yaml': FileHandler.load_yaml_file,
            'ini': FileHandler.load_ini_file,
        }
        
        loader = loaders.get(self._format)
        if not loader:
            raise ParseError(f"Unsupported file format: {self._format}")
        
        raw_data = loader(self._filepath)
        
        # Convert types automatically
        for key, value in raw_data.items():
            typed_value = TypeDetector.auto_detect(value)
            
            if override or key not in self._data:
                self._data[key] = typed_value
            
            if apply_to_os:
                os.environ[key] = TypeDetector.to_string(typed_value)
        
        return self
    
    def get(self, key: str, default: Any = None, cast_type: Optional[type] = None) -> Any:
        """
        Get environment variable with automatic type detection
        
        Args:
            key: Variable name
            default: Default value if key not found
            cast_type: Explicitly cast to this type
            
        Returns:
            Variable value with detected or specified type
        """
        # Check internal storage first
        value = self._data.get(key)
        
        # Fall back to os.environ
        if value is None:
            value = os.environ.get(key)
            if value is not None:
                value = TypeDetector.auto_detect(value)
        
        if value is None:
            return default
        
        # Apply explicit type casting if requested
        if cast_type:
            try:
                if cast_type == bool:
                    if isinstance(value, bool):
                        return value
                    if isinstance(value, str):
                        return value.lower() in ('true', 'yes', 'on', '1')
                    return bool(value)
                elif cast_type == list:
                    value = [i.strip() for i in re.split(",| ", value, re.I) if i]
                    return value
                elif cast_type == tuple:
                    value = [i.strip() for i in re.split(",| ", value, re.I) if i]
                    
                return cast_type(value)

            except (ValueError, TypeError) as e:
                raise TypeConversionError(f"Cannot convert '{value}' to {cast_type.__name__}: {e}")
        
        return value
    
    def set(self, key: str, value: Any, apply_to_os: bool = True) -> 'DotEnv':
        """
        Set environment variable
        
        Args:
            key: Variable name
            value: Variable value (will be auto-typed)
            apply_to_os: Also set in os.environ
            
        Returns:
            self for method chaining
        """
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
        """
        Save current environment variables to file
        
        Args:
            filepath: Path to save to (uses initialized path if None)
            format: File format (auto-detected from extension if None)
            
        Returns:
            self for method chaining
        """
        save_path = Path(filepath) if filepath else self._filepath
        
        if not save_path:
            #raise ValueError("No filepath specified for saving")
            # print("[envdot] warning: No file config found !")
            return self
        
        save_format = format or FileHandler.detect_format(save_path)
        
        savers = {
            'env': FileHandler.save_env_file,
            'json': FileHandler.save_json_file,
            'yaml': FileHandler.save_yaml_file,
            'ini': FileHandler.save_ini_file,
        }
        
        saver = savers.get(save_format)
        if not saver:
            raise ParseError(f"Unsupported file format for saving: {save_format}")
        
        saver(save_path, self._data)
        return self

    def save_env(self, *args, **kwargs):
        return self.save(*args, **kwargs)
    
    def delete(self, key: str, remove_from_os: bool = True) -> 'DotEnv':
        """
        Delete environment variable
        
        Args:
            key: Variable name to delete
            remove_from_os: Also remove from os.environ
            
        Returns:
            self for method chaining
        """
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
    
    def keys(self) -> list:
        """Get all variable names"""
        return list(self._data.keys())
    
    def clear(self, clear_os: bool = False) -> 'DotEnv':
        """
        Clear all stored variables
        
        Args:
            clear_os: Also clear variables from os.environ
            
        Returns:
            self for method chaining
        """
        if clear_os:
            for key in self._data.keys():
                if key in os.environ:
                    del os.environ[key]
        
        self._data.clear()
        return self
    
    def __getattr__(self, name: str) -> Any:
        """Handle attribute-style access: config.DEBUG_SERVER"""
        if name in self._data:
            return self._data[name]
        elif name in os.environ:
            return TypeDetector.auto_detect(os.environ[name])
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Handle attribute assignment: config.DEBUG_SERVER = True"""
        # Handle private attributes normally
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            # Set the value and auto-save
            self.set(name, value, apply_to_os=True)
            self.save()

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access: env['KEY']"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting: env['KEY'] = value"""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists: 'KEY' in env"""
        return key in self._data or key in os.environ
    
    def __repr__(self) -> str:
        return f"DotEnv(filepath={self._filepath}, vars={len(self._data)})"

    def __call__(self, key: str, value: Any = None, default: Any = None) -> Any:
        """Callable interface: config('DEBUG_SERVER') or config('DEBUG_SERVER', True)"""
        if value is not None:
            self.set(key, value)
            self.save()  # Auto-save when setting via call
            return self
        else:
            return self.get(key, default)

# Global instance for convenience functions
_global_env = DotEnv(auto_load=False)


def load_env(filepath: Optional[Union[str, Path]] = None, 
             auto_replace_getenv: bool = True,
             patch_os: bool = True,
             **kwargs) -> DotEnv:
    """
    Convenience function to load environment variables
    
    Args:
        filepath: Path to configuration file
        auto_replace_getenv: Automatically replace os.getenv() with typed version (default: True)
        patch_os: Also patch os module with helper functions like os.save_env() (default: True)
        **kwargs: Additional arguments passed to DotEnv.load()
    
    Returns:
        DotEnv instance
    """
    global _global_env
    
    # Auto-replace os.getenv with typed version
    if auto_replace_getenv:
        from .helpers import replace_os_getenv
        replace_os_getenv()
    
    # Patch os module with additional helpers (NOW DEFAULT!)
    if patch_os:
        from .helpers import patch_os_module
        patch_os_module()
        # print("[DEBUG] os module patched - os.save_env() should be available")
    
    _global_env = DotEnv(filepath=filepath, auto_load=False)
    _global_env.load(**kwargs)
    return _global_env

def show():
    global _global_env
    return _global_env.show()

def get_env(key: str, default: Any = None, cast_type: Optional[type] = None) -> Any:
    """
    Convenience function to get environment variable
    
    Args:
        key: Variable name
        default: Default value if not found
        cast_type: Explicitly cast to this type
    
    Returns:
        Variable value
    """
    return _global_env.get(key, default, cast_type)


def set_env(key: str, value: Any, **kwargs) -> DotEnv:
    """
    Convenience function to set environment variable
    
    Args:
        key: Variable name
        value: Variable value
        **kwargs: Additional arguments passed to DotEnv.set()
    
    Returns:
        DotEnv instance
    """
    return _global_env.set(key, value, **kwargs)


def save_env(filepath: Optional[Union[str, Path]] = None, **kwargs) -> DotEnv:
    """
    Convenience function to save environment variables
    
    Args:
        filepath: Path to save to
        **kwargs: Additional arguments passed to DotEnv.save()
    
    Returns:
        DotEnv instance
    """
    return _global_env.save(filepath, **kwargs)