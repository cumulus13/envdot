#!/usr/bin/env python3
# file: envdot/exceptions.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:59:13.218740
# Description: Custom exceptions for envdot package 
# License: MIT


class DotEnvError(Exception):
    """Base exception for envdot errors"""
    pass


class FileNotFoundError(DotEnvError):
    """Raised when the configuration file is not found"""
    pass


class ParseError(DotEnvError):
    """Raised when there's an error parsing the configuration file"""
    pass


class TypeConversionError(DotEnvError):
    """Raised when type conversion fails"""
    pass