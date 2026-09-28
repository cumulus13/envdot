#!/usr/bin/env python3

# File: envdot/sysenv.py
# Description: Detect persistent (system / user level) environment variable
#              changes made OUTSIDE this process, so envdot can apply them.
# License: MIT

"""
Why this exists
---------------
A process receives a *snapshot* of the environment when it starts. If you
later change a variable persistently (Windows "Edit environment variables"
dialog, `setx`, `[Environment]::SetEnvironmentVariable(...)`, editing
/etc/environment, ...) the running process never sees it - only newly
started processes do.

This module watches the *persistent store* and reports what changed:

* Windows : HKCU\\Environment and
            HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment
            (change detection = registry key last-write time, so a poll is
            two cheap registry calls; contents are only re-read when the
            timestamp moved)
* Linux   : /etc/environment and ~/.config/environment.d/*.conf
            (change detection = mtime + size). Shell rc files such as
            ~/.bashrc / ~/.profile are deliberately NOT parsed - they are
            scripts, and executing/interpreting them is unsafe.
* macOS / other: not supported (``supported`` is False, ``poll()`` is a no-op).

Only the DIFFERENCE between two snapshots is reported, so a variable you
overrode inside the process is never clobbered unless that variable itself
changed in the persistent store.
"""

import glob
import os
import re
import sys
import time
from typing import Dict, Iterable, List, Optional, Set, Tuple

IS_WINDOWS = sys.platform.startswith('win')
IS_LINUX = sys.platform.startswith('linux')

_WIN_KEYS = (
    # (root attribute on winreg, subkey). System first, user second:
    # Windows applies user values over system values for the same name.
    ('HKEY_LOCAL_MACHINE', r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),
    ('HKEY_CURRENT_USER', r'Environment'),
)


class _WindowsRegistryBackend:
    """Reads persistent env vars from the Windows registry."""

    def __init__(self, winreg_module=None):
        if winreg_module is None:
            import winreg as winreg_module  # type: ignore  # Windows only
        self._winreg = winreg_module

    def token(self) -> Tuple:
        w = self._winreg
        parts = []
        for root_name, sub in _WIN_KEYS:
            try:
                with w.OpenKey(getattr(w, root_name), sub, 0, w.KEY_READ) as key:
                    parts.append(w.QueryInfoKey(key)[2])  # last write time
            except OSError:
                parts.append(None)
        return tuple(parts)

    _PCT = re.compile(r'%([^%]+)%')

    def read(self) -> Dict[str, str]:
        w = self._winreg
        raw: Dict[str, Tuple[str, bool]] = {}
        for root_name, sub in _WIN_KEYS:
            try:
                key = w.OpenKey(getattr(w, root_name), sub, 0, w.KEY_READ)
            except OSError:
                continue
            with key:
                i = 0
                while True:
                    try:
                        name, value, vtype = w.EnumValue(key, i)
                    except OSError:
                        break
                    i += 1
                    if vtype not in (w.REG_SZ, w.REG_EXPAND_SZ) or not isinstance(value, str):
                        continue
                    # Windows names are case-insensitive; later hive (user) wins
                    raw[name.upper()] = (value, vtype == w.REG_EXPAND_SZ)

        # Expand %VAR% in REG_EXPAND_SZ values against the registry values
        # FIRST (so "%JAVA_HOME%\\bin" uses the JAVA_HOME that was just
        # changed), then the current process environment.
        lookup = {k.upper(): v for k, v in os.environ.items()}
        lookup.update({k: v for k, (v, _) in raw.items()})
        sub_fn = lambda m: lookup.get(m.group(1).upper(), m.group(0))
        return {k: (self._PCT.sub(sub_fn, v) if expand else v)
                for k, (v, expand) in raw.items()}


class _PosixFileBackend:
    """Reads persistent env vars from simple KEY=VALUE files."""

    def __init__(self, paths: Optional[Iterable[str]] = None):
        if paths is None:
            paths = ['/etc/environment',
                     os.path.expanduser('~/.config/environment.d/*.conf')]
        self._patterns = list(paths)

    def _files(self) -> List[str]:
        files: List[str] = []
        for p in self._patterns:
            files.extend(sorted(glob.glob(p)))
        return files

    def token(self) -> Tuple:
        parts = []
        for f in self._files():
            try:
                st = os.stat(f)
                parts.append((f, st.st_mtime_ns, st.st_size))
            except OSError:
                continue
        return tuple(parts)

    @staticmethod
    def parse(text: str) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:].lstrip()
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k, v = k.strip(), v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
                v = v[1:-1]
            if k.isidentifier():
                out[k] = v
        return out

    def read(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for f in self._files():
            try:
                with open(f, 'r', encoding='utf-8', errors='replace') as fh:
                    out.update(self.parse(fh.read()))
            except OSError:
                continue
        return out


class SystemEnvWatcher:
    """
    Poll the persistent environment store and report changes.

    ``poll()`` returns ``(changed, removed)``:
      * changed - {NAME: new_value} for variables added or modified
      * removed - {NAME: last_known_value} for variables that disappeared

    The first successful poll only records a baseline and reports nothing
    (the running process already has the environment it started with).

    ``ignore`` - names never reported. Defaults to ``PATH``, because the
    process PATH is a merge of system+user PATH (plus whatever the parent
    injected); blindly replacing it with one registry value would break it.

    ``min_interval`` - minimum seconds between actual store checks, so
    calling ``get()`` in a hot loop doesn't hammer the registry/filesystem.
    """

    def __init__(self, ignore: Iterable[str] = ('PATH',), min_interval: float = 0.25,
                 backend=None):
        norm = (lambda s: s.upper()) if IS_WINDOWS else (lambda s: s)
        self.ignore: Set[str] = {norm(k) for k in ignore}
        self.min_interval = float(min_interval)
        self._backend = backend if backend is not None else self._default_backend()
        self._token = None
        self._snapshot: Optional[Dict[str, str]] = None
        self._last_check = 0.0

    @staticmethod
    def _default_backend():
        if IS_WINDOWS:
            try:
                return _WindowsRegistryBackend()
            except ImportError:
                return None
        if IS_LINUX:
            return _PosixFileBackend()
        return None

    @property
    def supported(self) -> bool:
        return self._backend is not None

    def poll(self, force: bool = False) -> Tuple[Dict[str, str], Dict[str, str]]:
        if self._backend is None:
            return {}, {}
        now = time.monotonic()
        if not force and self._snapshot is not None and (now - self._last_check) < self.min_interval:
            return {}, {}
        self._last_check = now
        try:
            token = self._backend.token()
            if self._snapshot is not None and token == self._token:
                return {}, {}
            snap = {k: v for k, v in self._backend.read().items() if k not in self.ignore}
        except Exception:
            # An unreadable registry/file must never break normal reads.
            return {}, {}
        old, self._token, self._snapshot = self._snapshot, token, snap
        if old is None:
            return {}, {}
        changed = {k: v for k, v in snap.items() if old.get(k) != v}
        removed = {k: v for k, v in old.items() if k not in snap}
        return changed, removed
