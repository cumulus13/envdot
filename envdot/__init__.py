#!/usr/bin/env python3

# file: envdot/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:59:34.906959
# License: MIT

"""
envdot: Enhanced environment variable management with multi-format support
Supports .env, .json, .yaml, .yml, and .ini files with automatic type detection
"""

from .core import DotEnv, load_env, get_env, set_env, save_env, show, data, Env, TypeDetector, get_logger, set_or_dict, check_file
from .exceptions import EnvDotError, FileNotFoundError, ParseError, TypeConversionError
from .helpers import getenv_typed, getenv_int, getenv_float, getenv_bool, getenv_str, setenv_typed, patch_os_module



def get_version():
    import os
    try:
        from importlib.metadata import version, PackageNotFoundError  # py3.8+
        try:
            return version("envdot")
        except PackageNotFoundError:
            pass
    except Exception:
        pass

    try:
        from pathlib import Path
        for candidate in (Path(__file__).parent / "__version__.py",
                          Path(__file__).parent.parent / "__version__.py"):
            if candidate.is_file():
                with open(candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("version"):
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            import traceback
            print(traceback.format_exc())
        else:
            print(f"WARNING: No __version__ file found: {e}")

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
    "EnvDotError",
    "FileNotFoundError",
    "ParseError",
    "TypeConversionError",
    "show",
    "data",
    "TypeDetector", 
    "get_logger", 
    "set_or_dict", 
    "check_file",
    "getenv_typed",
    "getenv_int",
    "getenv_float",
    "getenv_bool",
    "getenv_str",
    "setenv_typed",
    "patch_os_module",
]
