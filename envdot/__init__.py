#!/usr/bin/env python3
# file: envdot/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:59:34.906959
# License: MIT

"""
envdot: Enhanced environment variable management with multi-format support
Supports .env, .json, .yaml, .yml, and .ini files with automatic type detection
"""

from .core import DotEnv, load_env, get_env, set_env, save_env, show
from .exceptions import DotEnvError, FileNotFoundError, ParseError, TypeConversionError
from .helpers import getenv_typed, getenv_int, getenv_float, getenv_bool, getenv_str, setenv_typed, patch_os_module

__version__ = "1.0.0"
__all__ = [
    "DotEnv",
    "load_env",
    "get_env",
    "set_env",
    "save_env",
    "DotEnvError",
    "FileNotFoundError",
    "ParseError",
    "TypeConversionError",
    "show"
]