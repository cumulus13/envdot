#!/usr/bin/env python3

# File: envdot/helpers.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-12
# Description: Helper functions for enhanced environment variable access
# License: MIT

"""Helper functions for enhanced environment variable access"""

import os
import re
# import fnmatch
from typing import Any, Optional, TypeVar, Union, List, Dict
from .core import TypeDetector, get_logger
import ast
import json
# import traceback
# import sys

# LOG_LEVEL_ENVDOT = os.getenv('LOG_LEVEL_ENVDOT', 'CRITICAL')
# tprint = None  # type: ignore
# SHOW_LOGGING_ENVDOT = False

# # envdot/helpers.py
# import traceback

# # Fallback functions
# def _fallback_print_exception(e):
#     print(traceback.format_exc())

# def _fallback_logger():
#     import logging

#     try:
#         from .custom_logging import get_logger  # type: ignore
#     except ImportError:
#         from custom_logging import get_logger  # type: ignore
    
#     return get_logger('envdot', level=getattr(logging, LOG_LEVEL.upper(), logging.CRITICAL))

# def _fallback_pydebugger(**kwargs):
#     os.environ['NO_LOGGING'] = "1"
#     if kwargs:
#         for i in kwargs:
#             if not i == 'debug':
#                 print(f"[DEBUG (envdot)] [1]: {i} = {kwargs.get(i)}")

# # Lazy import dengan fallback
# _richcolorlog_available = None
# _richcolorlog__print_exception_available = None
# _richcolorlog__print_exception_available = None
# _pydebugger_available = None

# def get_richcolorlog():
#     global _richcolorlog_available
#     if _richcolorlog_available is None:
#         try:
#             from richcolorlog import setup_logging  # type: ignore
#             _richcolorlog_available = setup_logging
#         except ImportError:
#             _richcolorlog_available = False
#     return _richcolorlog_available

# def get_richcolorlog_print_exception():
#     global _richcolorlog__print_exception_available
#     if _richcolorlog__print_exception_available is None:
#         try:
#             from richcolorlog import print_exception  # type: ignore
#             _richcolorlog__print_exception_available = print_exception
#         except ImportError:
#             _richcolorlog__print_exception_available = False
#     return _richcolorlog__print_exception_available

# def get_pydebugger():
#     global _pydebugger_available
#     if _pydebugger_available is None:
#         try:
#             from pydebugger import debug  # type: ignore
#             _pydebugger_available = debug
#         except ImportError:
#             _pydebugger_available = False
#     return _pydebugger_available


# def tprint(e):
#     rcl = get_richcolorlog()
#     if rcl:
#         return rcl.print_exception(e)
#     else:
#         return _fallback_print_exception(e)

# def get_logger():
#     rcl = get_richcolorlog()
#     if rcl:
#         return rcl.setup_logging(
#         name="envdot",
#         level=LOG_LEVEL_ENVDOT,
#         show=SHOW_LOGGING_ENVDOT
#     )
#     else:
#         return _fallback_logger()

# def get_debug():
#     _debug = get_pydebugger()
#     if _debug:
#         return _debug
#     else:
#         return _fallback_pydebugger

# if (len(sys.argv) > 1 and any('--debug' == arg for arg in sys.argv)) or str(os.getenv('DOTENV_DEBUG', os.getenv('DEBUG', False))).lower() in ('1', 'true', 'ok', 'yes', 'on'):
#     print("🐞 Debug mode enabled")
#     os.environ["DEBUG"] = "1"
#     os.environ['LOGGING'] = "1"
#     os.environ.pop('NO_LOGGING', None)
#     os.environ['TRACEBACK'] = "1"
#     os.environ["LOGGING"] = "1"
#     LOG_LEVEL = "DEBUG"
#     SHOW_LOGGING = True
#     debug = get_debug()
# else:
#     debug = _fallback_pydebugger

logger = get_logger()

T = TypeVar('T')

# Save original os.getenv IMMEDIATELY when module loads
_original_getenv = os.getenv if not hasattr(os, '_env_dot_original_getenv') else os._env_dot_original_getenv

os._env_dot_original_getenv = _original_getenv  # type: ignore


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

    value = os._env_dot_original_getenv(key)  # type: ignore
    # logger.debug(f"key   [x]: {key}")  
    # logger.debug(f"value [x]: {value}")  
    # debug(key = key)
    # debug(value = value)
    
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
            elif cast_type == dict and isinstance(value, dict):
                return value
            elif cast_type == dict and isinstance(value, str) and value.strip().startswith("{") and value.strip().endswith("}"):
                try:
                    return json.loads(value)
                except:
                    try:
                        return ast.literal_eval(value)
                    except:
                        import json5
                        return json5.loads(value)
            elif cast_type == dict and isinstance(value, str) and ":" in value.strip():
                value = {
                    a: b
                    for part in re.split(r"\s+", value)
                    if ":" in part
                    for a, b in [part.split(":", 1)]
                }
            elif cast_type in (list, tuple) and isinstance(value, (list, tuple)) and len(value) > 0 and ":" in value[0]:
                return {
                    a: b
                    for item in value
                    if ":" in item
                    for a, b in [item.split(":", 1)]
                }
            elif cast_type in (list, tuple) and isinstance(value, str) and value.strip().startswith(("[", "(")) and value.strip().endswith(("]", ")")):
                try:
                    return ast.literal_eval(value)
                except Exception as e:
                    print("cast_type in (list, tuple), ERROR: {e]}")
            elif cast_type in (list, tuple) and isinstance(value, str):
                # print("5"*100)
                return value
            elif cast_type in (list, tuple) and isinstance(value, (list, tuple)):
                return tuple(value)
            return cast_type(value)
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

class DynamicConfigPathProxy:
    """A proxy object that always returns the current global config file path."""
    def __repr__(self):
        import envdot.core as core_module
        return repr(core_module._global_env._filepath)

    def __str__(self):
        import envdot.core as core_module
        return str(core_module._global_env._filepath)

    def __fspath__(self):
        import envdot.core as core_module
        return os.fspath(core_module._global_env._filepath)

    # Forward attribute access to the underlying Path object if needed
    def __getattr__(self, name):
        import envdot.core as core_module
        path_obj = core_module._global_env._filepath
        if path_obj is None:
            raise AttributeError(f"No configuration file loaded.")
        return getattr(path_obj, name)

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
        - os.setenv()
    
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
    os.writeenv = lambda key, value, **kwargs: core_module.set_env(key, value, **kwargs)  # type: ignore
    os.write_env = lambda key, value, **kwargs: core_module.set_env(key, value, **kwargs)  # type: ignore
    os.write_config = lambda key, value, **kwargs: core_module.set_env(key, value, **kwargs)  # type: ignore
    os._write = lambda key, value, **kwargs: core_module.set_env(key, value, **kwargs)  # type: ignore
    os.find = core_module.DotEnv().find  # type: ignore
    os.find_keys = core_module.DotEnv().find_keys  # type: ignore
    os.find_values = core_module.DotEnv().find_values  # type: ignore
    os.find_wildcard = core_module.DotEnv().find_wildcard  # type: ignore
    os.find_regex = core_module.DotEnv().find_regex  # type: ignore
    os.find_contains = core_module.DotEnv().find_contains  # type: ignore
    os.show = core_module.show  # type: ignore
    os._show = core_module.show  # type: ignore
    os.show_config = core_module.show  # type: ignore
    
    # os.configfile = core_module._global_env._filepath  # type: ignore
    # os.config_file = core_module._global_env._filepath  # type: ignore
    # os.configpath = core_module._global_env._filepath  # type: ignore
    # os.config_path = core_module._global_env._filepath  # type: ignore
    # os.fileconfig = core_module._global_env._filepath  # type: ignore
    # os.file_config = core_module._global_env._filepath  # type: ignore

    # Use the dynamic proxy here instead of static assignment
    proxy = DynamicConfigPathProxy()
    os.configfile = proxy  # type: ignore  
    os.config_file = proxy  # type: ignore  
    os.configpath = proxy  # type: ignore  
    os.config_path = proxy  # type: ignore  
    os.fileconfig = proxy  # type: ignore  
    os.file_config = proxy  # type: ignore

    os.save_env = lambda filepath=None, **kwargs: core_module.save_env(filepath, **kwargs)  # type: ignore
    os.find = lambda *args, **kwargs: core_module.find_env(*args, **kwargs)  # type: ignore
    os.filter = lambda *args, **kwargs: core_module.filter_env(*args, **kwargs)  # type: ignore
    os.search = lambda *args, **kwargs: core_module.search_env(*args, **kwargs)  # type: ignore


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
    # print("Replace with typed version >>>>>>>>>>>>>>>>>>>>")
    os.getenv = getenv_typed

# def replace_os_getenv():
#     """
#     REPLACE os.getenv() to return auto-typed AND hot-reloaded values!
#     """
#     import envdot.core as core_module
#     # Point directly to core's get_env, which routes through DotEnv.get()
#     # and safely triggers the check_file() auto-reload logic!
#     os.getenv = core_module.get_env


def restore_os_getenv():
    """
    Restore original os.getenv() behavior
    """
    os.getenv = os._env_dot_original_getenv  # type: ignore