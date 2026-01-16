#!/usr/bin/env python3

# File: envdot/helpers.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-12
# Description: Helper functions for enhanced environment variable access
# License: MIT

"""Helper functions for enhanced environment variable access"""

import os
import re
import fnmatch
from typing import Any, Optional, TypeVar, Union, List, Dict
from .core import TypeDetector

T = TypeVar('T')

# Save original os.getenv IMMEDIATELY when module loads
_original_getenv = os.getenv if not hasattr(os, '_env_dot_original_getenv') else os._env_dot_original_getenv
os._env_dot_original_getenv = _original_getenv


def getenv_typed(key: str, default: Any = None, cast_type: Optional[type] = None) -> Any:
    """
    Enhanced version of os.getenv() with automatic type detection
    
    This function wraps os.getenv() and automatically detects and converts
    types (bool, int, float, None) from string values.
    
    Args:
        key: Environment variable name
        default: Default value if key not found
        cast_type: Explicitly cast to this type
        
    Returns:
        Variable value with detected or specified type
        
    Examples:
        >>> os.environ['PORT'] = '8080'
        >>> getenv_typed('PORT')  # Returns: 8080 (int)
        
        >>> os.environ['DEBUG'] = 'true'
        >>> getenv_typed('DEBUG')  # Returns: True (bool)
        
        >>> getenv_typed('MISSING', default=100)  # Returns: 100
    """
    # ALWAYS use the saved original, never os.getenv

    value = os._env_dot_original_getenv(key)
    
    if value is None:
        return default
    
    # Auto-detect type
    typed_value = TypeDetector.auto_detect(value)
    
    # Apply explicit type casting if requested
    if cast_type:
        try:
            if cast_type == bool:
                if isinstance(typed_value, bool):
                    return typed_value
                if isinstance(typed_value, str):
                    return typed_value.lower() in ('true', 'yes', 'on', '1')

                return bool(typed_value)
            elif cast_type == list:
                value = [i.strip() for i in re.split(",| ", value, re.I) if i]
                return value
            elif cast_type == tuple:
                value = [i.strip() for i in re.split(",| ", value, re.I) if i]
                return tuple(typed_value)

            return cast_type(typed_value)
        except (ValueError, TypeError):
            # If casting fails, return default or original value
            return default if default is not None else typed_value
    
    return typed_value


def setenv_typed(key: str, value: Any) -> None:
    """
    Set environment variable with automatic type-to-string conversion
    
    Args:
        key: Environment variable name
        value: Value to set (will be converted to string)
        
    Examples:
        >>> setenv_typed('PORT', 8080)
        >>> os.getenv('PORT')  # Returns: '8080'
        
        >>> setenv_typed('DEBUG', True)
        >>> os.getenv('DEBUG')  # Returns: 'true'
    """
    os.environ[key] = TypeDetector.to_string(value)


def getenv_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer"""
    return getenv_typed(key, default=default, cast_type=int)


def getenv_float(key: str, default: float = 0.0) -> float:
    """Get environment variable as float"""
    return getenv_typed(key, default=default, cast_type=float)


def getenv_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean"""
    return getenv_typed(key, default=default, cast_type=bool)


def getenv_str(key: str, default: str = '') -> str:
    """Get environment variable as string"""
    return getenv_typed(key, default=default, cast_type=str)

# Monkey-patch os module for convenience (optional usage)
def patch_os_module():
    """
    Monkey-patch os module to add typed getenv functions and save_env
    
    After calling this, you can use:
        - os.getenv_typed()
        - os.getenv_int()
        - os.getenv_float()
        - os.getenv_bool()
        - os.setenv_typed()
        - os.save_env()
    
    Example:
        >>> from dotenv.helpers import patch_os_module
        >>> patch_os_module()
        >>> os.getenv_typed('PORT')  # Auto-typed
        >>> os.save_env()  # Save to file
    """
    # Import here to avoid circular import
    import envdot.core as core_module
    
    os.getenv_typed = getenv_typed  # type: ignore
    os.getenv_int = getenv_int  # type: ignore
    os.getenv_float = getenv_float  # type: ignore
    os.getenv_bool = getenv_bool  # type: ignore
    os.getenv_str = getenv_str  # type: ignore
    os.setenv_typed = setenv_typed  # type: ignore
    # def set_env(key: str, value: Any, **kwargs) -> DotEnv:
    os.setenv = lambda key, value, **kwargs: core_module.set_env(key, value, **kwargs)  # type: ignore
    os.save_env = lambda filepath=None, **kwargs: core_module.save_env(filepath, **kwargs)  # type: ignore
    os.find = lambda key, value, **kwargs: core_module.find(**args, **kwargs)  # type: ignore
    os.filter = lambda key, value, **kwargs: core_module.filter(**args, **kwargs)  # type: ignore
    os.search = lambda key, value, **kwargs: core_module.search(**args, **kwargs)  # type: ignore


def replace_os_getenv():
    """
    REPLACE os.getenv() to return auto-typed values!
    
    After calling this, os.getenv() will automatically detect and return
    proper types (int, float, bool, None) instead of always returning strings.
    
    WARNING: This modifies Python's built-in os.getenv behavior globally!
    
    Example:
        >>> from dotenv import replace_os_getenv, load_env
        >>> replace_os_getenv()  # Replace os.getenv with typed version
        >>> load_env()
        >>> 
        >>> port = os.getenv('DEBUG_PORT')  # Returns: 50001 (int) ✅
        >>> debug = os.getenv('DEBUG')      # Returns: True (bool) ✅
    """
    # Replace with typed version
    os.getenv = getenv_typed


def restore_os_getenv():
    """
    Restore original os.getenv() behavior
    """
    os.getenv = os._env_dot_original_getenv  # type: ignore