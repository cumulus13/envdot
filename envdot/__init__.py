#!/usr/bin/env python3

# file: envdot/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:59:34.906959
# License: MIT

"""
envdot: Enhanced environment variable management with multi-format support
Supports .env, .json, .yaml, .yml, and .ini files with automatic type detection
"""

from .core import DotEnv, load_env, get_env, set_env, save_env, show, data, Env
from .exceptions import DotEnvError, FileNotFoundError, ParseError, TypeConversionError
from .helpers import getenv_typed, getenv_int, getenv_float, getenv_bool, getenv_str, setenv_typed, patch_os_module


def get_version():
    import traceback
    from pathlib import Path
    import os
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "1.0.0"


# __version__ = vget().get(True)
__version__ = get_version()
__all__ = [
    "DotEnv",
    "load_env",
    "Env",
    "get_env",
    "set_env",
    "save_env",
    "DotEnvError",
    "FileNotFoundError",
    "ParseError",
    "TypeConversionError",
    "show",
    "data"
]