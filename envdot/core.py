#!/usr/bin/env python3
# file: envdot/core.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:58:18.904513
# Description: Core functionality for envdot package 
# License: MIT

import os
import json
import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Union
from .exceptions import FileNotFoundError, ParseError, TypeConversionError


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
            if '.' not in value and 'e' not in value.lower():
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
        ext = filepath.suffix.lower()
        if ext in ('.yaml', '.yml'):
            return 'yaml'
        elif ext == '.json':
            return 'json'
        elif ext == '.ini':
            return 'ini'
        elif ext == '.env':
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
        """Load .json file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Flatten nested structures if needed
            flattened = {}
            FileHandler._flatten_dict(data, flattened)
            return flattened
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON format: {e}")
    
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


class DotEnv:
    """Main class for managing environment variables from multiple file formats"""
    
    def __init__(self, filepath: Optional[Union[str, Path]] = None, auto_load: bool = True):
        """
        Initialize DotEnv instance
        
        Args:
            filepath: Path to configuration file. If None, searches for common files
            auto_load: Automatically load the file on initialization
        """
        self._data: Dict[str, Any] = {}
        self._filepath: Optional[Path] = None
        self._format: Optional[str] = None
        
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
    
    def load(self, filepath: Optional[Union[str, Path]] = None, 
             override: bool = True, apply_to_os: bool = True) -> 'DotEnv':
        """
        Load environment variables from file
        
        Args:
            filepath: Path to configuration file (uses initialized path if None)
            override: Override existing values in internal storage
            apply_to_os: Apply loaded variables to os.environ
            
        Returns:
            self for method chaining
        """
        if filepath:
            self._filepath = Path(filepath)
        
        if not self._filepath:
            raise FileNotFoundError("No configuration file specified")
        
        if not self._filepath.exists():
            raise FileNotFoundError(f"File not found: {self._filepath}")
        
        # Detect format
        self._format = FileHandler.detect_format(self._filepath)
        
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
            raise ValueError("No filepath specified for saving")
        
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


# Global instance for convenience functions
_global_env = DotEnv(auto_load=False)


def load_env(filepath: Optional[Union[str, Path]] = None, **kwargs) -> DotEnv:
    """
    Convenience function to load environment variables
    
    Args:
        filepath: Path to configuration file
        **kwargs: Additional arguments passed to DotEnv.load()
    
    Returns:
        DotEnv instance
    """
    global _global_env
    _global_env = DotEnv(filepath=filepath, auto_load=False)
    _global_env.load(**kwargs)
    return _global_env


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