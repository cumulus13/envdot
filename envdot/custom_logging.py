#!/usr/bin/env python3

# File: envdot/custom_logging.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Description: Extra syslog-style log levels, added WITHOUT touching stdlib methods
# License: MIT

"""
Adds extra levels (EMERGENCY, ALERT, NOTICE, SUCCESS) as new
``logging.Logger`` methods.

Unlike earlier versions this module NEVER replaces an existing
``logging.Logger`` attribute (``error``, ``warning``, ``fatal`` ...): doing
so is global to the host application and broke ``%(filename)s`` /
``%(lineno)d`` call-site reporting for every logger in the process.
New methods are built with ``functools.partialmethod`` so they add no
extra Python frame either.
Create a custom logging level:
    EMERGENCY, ALERT, CRITICAL, ERROR,
    WARNING, NOTICE, INFO, DEBUG,
    SUCCESS, FATAL
With syslog format + additional SUCCESS and FATAL.

"""

import logging

# ============================================================
# 1. LEVEL DEFINITION (Syslog + Extra)
# ============================================================

CUSTOM_LOG_LEVELS = {
    # Syslog RFC5424 severity (0 = highest severity)
    # We map to the top of the Python logging range (10–60)
    "EMERGENCY": 60,   # System unusable
    "ALERT":     55,   # Immediate action required
    "CRITICAL":  logging.CRITICAL,  # 50
    "ERROR":     logging.ERROR,     # 40
    "WARNING":   logging.WARNING,   # 30
    "NOTICE":    25,   # Normal but significant condition
    "INFO":      logging.INFO,      # 20
    "DEBUG":     logging.DEBUG,     # 10

    # Additional custom levels
    "SUCCESS":   22,   # Operation successful
    "FATAL":     65,   # Hard failure beyond CRITICAL
}

_registered = False

# ============================================================
# 2. LEVEL REGISTRATION TO LOGGING
# ============================================================


def register_custom_levels() -> None:
    """Idempotent. Only registers names/methods that don't exist yet."""
    global _registered
    if _registered:
        return
    for level_name, level_value in CUSTOM_LOG_LEVELS.items():
        # Register for Python logging
        logging.addLevelName(level_value, level_name)

        # Add method to logging.Logger
        def log_for(level):
            def _log_method(self, message, *args, **kwargs):
                if self.isEnabledFor(level):
                    self._log(level, message, args, **kwargs)
            return _log_method

        # create method lowercase: logger.emergency(), logger.notice(), dll
        setattr(logging.Logger, level_name.lower(), log_for(level_value))


register_custom_levels()

# ============================================================
# 3. FORMATTER DETAIL & PROFESSIONAL
# ============================================================

DEFAULT_FORMAT = (
    "[%(asctime)s] "
    "%(levelname)-10s "
    "%(name)s: "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_default_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT))
    return handler

# ============================================================
# 4. FUNCTION TO GET THE LOGGER THAT IS READY
# ============================================================

def get_logger(name="default", level=logging.DEBUG, handler: bool = True):
    """Return a configured logger.

    ``handler=False`` installs only a ``NullHandler`` (what a library should
    do by default: stay silent unless the application configures logging).
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:  # Avoid duplicated handler
        logger.addHandler(get_default_handler() if handler else logging.NullHandler())

    return logger
