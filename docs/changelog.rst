=========
Changelog
=========

All notable changes to envdot are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

[1.0.44] - 2026
----------

**Added**

- Optional, opt-in persistent system-environment watching
  (``envdot.sysenv``): detects environment variables changed *outside*
  the running process via the Windows registry (``setx``, System
  Properties) or ``/etc/environment`` / ``~/.config/environment.d/`` on
  Linux, and applies them live. Enable with
  ``load_env(watch_system_env=True)`` or ``DotEnv.enable_system_watch()``.
  See :doc:`usage/system-env-watch`.

[1.0.37] - 2026
---------------

This release is a substantial correctness and reliability pass on type
casting and auto-reload, based on real user bug reports.

**Fixed**

- ``cast_type`` is now always applied to the **original raw string**
  value, never to a value auto-detection already converted. Previously,
  auto-detection ran first and unconditionally, so by the time
  ``cast_type`` ran, the original string could already be gone —
  making explicit casting unreliable.
- Removed an undocumented behavior where any value containing a space or
  comma was silently auto-split into a tuple (e.g.
  ``APP_NAME=My Application`` became ``('My', 'Application')``). List/
  tuple conversion now only ever happens via an explicit
  ``cast_type=list``/``tuple``, matching the documented behavior.
- ``1``/``0`` now auto-detect as ``int``, not ``bool`` (use
  ``cast_type=bool`` if you specifically want boolean semantics for
  ``1``/``0``).
- ``get()`` no longer force-reparses the entire config file on every
  single call. It now checks the file's content hash and reloads only
  when it actually changed — while still guaranteeing no stale reads.
- Every read path — not just ``get()`` — now performs this same
  auto-reload check: ``show()``, ``all()``, ``as_dict()``, ``data()``,
  ``keys()``, attribute access, ``in`` checks, ``find()``, ``filter()``,
  and ``search()``. Previously only ``get()`` did, so e.g. ``show()``
  could report stale data even right after the file changed on disk.
- Fixed a case where ``get()`` could return a **stale** value from a
  now-out-of-date ``os.environ`` mirror even after the config file was
  correctly reloaded — specifically when a key's freshly-reloaded value
  was legitimately ``None`` (e.g. an emptied-out entry). ``get()`` now
  correctly distinguishes "this key has no value of our own at all"
  from "this key's value happens to be ``None``".
- ``load()`` now refreshes ``os.environ`` for a key on reload when that
  key is one envdot itself previously wrote there — previously, once a
  value was mirrored into ``os.environ`` once, it was never updated on
  subsequent reloads, only ever on the very first load.
- ``DotEnv(filepath=...)`` with a filepath that doesn't exist no longer
  silently substitutes an unrelated auto-discovered config file; it's
  kept as given, so ``load()`` can correctly raise
  ``envdot.exceptions.FileNotFoundError`` for it.
- ``FileNotFoundError`` is now actually raised by ``load()`` when an
  explicit filepath is missing (previously it was defined but never
  raised).
- ``set()`` now auto-detects a string value the same way loading it from
  a file would — so ``set('EMPTY', '')`` now results in ``None``,
  matching what loading ``EMPTY=`` from a file produces. Previously
  ``set()`` stored raw values verbatim, inconsistently with ``load()``.
- Removed a hidden performance/reliability bug in ``patch_os_module()``
  where ``os.find``/``os.find_keys``/etc. each constructed a brand-new,
  independently auto-loading ``DotEnv()`` instance, which could race
  with and interfere with the shared global instance's own
  ``os.environ`` bookkeeping.

**Supported Python Versions**

- Python 3.7 – 3.12

[1.0.14] - 2025
---------------

**Features**

- Multiple file format support (``.env``, ``.json``, ``.yaml``, ``.yml``,
  ``.ini``, ``.toml``)
- Automatic type detection for boolean, integer, float, and string values
- Method chaining for a fluent API
- Dictionary-style and attribute-style access
- Seamless integration with ``os.environ``
- Type-specific helper functions (``getenv_int``, ``getenv_bool``, etc.)
- OS module patching capability
- File format conversion (e.g. ``.env`` to ``.json``)
- Comprehensive error handling with custom exceptions

**Supported Python Versions**

- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

[1.0.0] - Initial Release
--------------------------

**Added**

- Initial release of envdot
- ``DotEnv`` class for environment variable management
- Support for the ``.env`` file format
- Basic type detection (``bool``, ``int``, ``float``, ``str``)
- Convenience functions (``load_env``, ``get_env``, ``set_env``, ``save_env``)
- Integration with ``os.environ``

Roadmap
-------

Planned Features
~~~~~~~~~~~~~~~~~~~

- macOS support for persistent system-environment watching
  (``launchctl setenv``/``getenv``)
- Environment variable encryption
- Variable interpolation (e.g. ``${OTHER_VAR}``)
- Schema validation
- CLI tool for managing environment files
- Async file loading support

Contributing
~~~~~~~~~~~~~~

If you'd like to help implement any of these features, please see the
:doc:`contributing` guide.

Versioning
----------

envdot follows `Semantic Versioning <https://semver.org/>`_:

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Deprecation Policy
------------------

- Deprecated features are marked with warnings for at least one minor version
- Deprecated features are removed in the next major version
- Migration guides are provided for breaking changes
