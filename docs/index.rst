.. envdot documentation master file

===============================================
envdot - Enhanced Environment Variable Manager
===============================================

.. image:: https://img.shields.io/pypi/v/envdot.svg
   :target: https://pypi.org/project/envdot/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/envdot.svg
   :target: https://pypi.org/project/envdot/
   :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

**envdot** is an enhanced environment variable management library for Python with
multi-format support, automatic type detection, and hot auto-reload.

Features
--------

🔧 **Multiple Format Support**
   Load configuration from ``.env``, ``.json``, ``.yaml``, ``.yml``, ``.ini``, and ``.toml`` files.

🎯 **Automatic Type Detection**
   Automatically converts strings to ``bool``, ``int``, ``float``, ``None``, or keeps as ``str``.
   Explicitly cast to ``list``, ``tuple``, or ``dict`` with ``cast_type`` — always from the
   original raw string, never from an already-detected value, so casting stays predictable.

💾 **Read and Write**
   Load from and save to configuration files seamlessly, across formats.

🔄 **Method Chaining**
   Fluent API for cleaner, more readable code.

🌍 **OS Environment Integration**
   Works seamlessly with ``os.environ`` — including an optional typed ``os.getenv()``
   replacement.

📦 **Minimal Core Dependencies**
   Core ``.env``/``.json``/``.ini`` support works out of the box; YAML/TOML support needs
   their respective optional packages.

🌿 **Smart Auto-Reload**
   Every read — ``get()``, ``show()``, ``all()``, attribute access, ``in`` checks,
   ``find()``/``filter()``/``search()`` — automatically re-reads the config file when its
   content actually changed, using a cheap hash check, not a full reparse on every call.

🪟 **Persistent System Environment Watching** *(optional, opt-in)*
   On Windows and Linux, envdot can additionally detect environment variables changed
   *outside* the running process — via the Windows registry (``setx``, System Properties)
   or ``/etc/environment`` / ``~/.config/environment.d/`` on Linux — and apply them live.
   See :doc:`usage/system-env-watch`.

Quick Example
-------------

.. code-block:: python

   import os
   from envdot import load_env, get_env, set_env

   # Load environment variables from .env (or any supported format)
   load_env()

   # or load_env('.env')
   # or load_env('config.json')
   # or load_env('config.yaml')
   # or load_env('config.ini')
   # or load_env('config.toml')
   # or load_env('/etc/config.env')
   # or load_env(r'c:\.env')
   # or load_env(r'c:\traceback.ini')

   # Get values with automatic type detection
   debug = get_env('DEBUG')       # Returns: True (bool)
   port = get_env('PORT')         # Returns: 8080 (int)
   timeout = get_env('TIMEOUT')   # Returns: 30.5 (float)

   # Explicit casting - always works from the ORIGINAL string, so it's
   # reliable even for values auto-detection would otherwise mangle
   # ALLOWED_HOSTS=localhost, 127.0.0.1, example.com
   hosts = get_env('ALLOWED_HOSTS', cast_type=list)
   # -> ['localhost', '127.0.0.1', 'example.com']
   allowed_hosts = os.getenv("*,127.0.0.1 192.168.10.2,example.com", cast_type=tuple) # Return: (*,127.0.0.1,192.168.10.2,example.com)  # (tuple)

   # Set new values
   set_env('NEW_FEATURE', True)
   os.setenv('NEW_FEATURE', True)   # equivalent, after patch_os_module()

   # Find by key pattern
   os.find("DB_*")  # -> dict of matching DB_* variables

   # Edit the config file on disk, then just read again - no restart needed
   print(get_env('DEBUG'))   # reflects the file's current content

Installation
------------

.. code-block:: bash

   # Basic installation
   pip install envdot

   # With YAML support
   pip install envdot[yaml]

   # With TOML support (Python < 3.11 also needs tomli)
   pip install envdot[toml]

   # With every optional extra
   pip install envdot[full]

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   usage/basic
   usage/file-formats
   usage/type-detection
   usage/auto-reload
   usage/system-env-watch
   usage/advanced

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/dotenv
   api/functions
   api/helpers
   api/sysenv
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   changelog

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Links
-----

* **PyPI**: https://pypi.org/project/envdot/
* **GitHub**: https://github.com/cumulus13/envdot
* **Issues**: https://github.com/cumulus13/envdot/issues

License
-------

envdot is released under the MIT License. See the `LICENSE <https://github.com/cumulus13/envdot/blob/main/LICENSE>`_ file for details.

Author
------

Created by `Hadi Cahyadi <mailto:cumulus13@gmail.com>`_

Support the Project
--------------------

* `Buy Me a Coffee <https://www.buymeacoffee.com/cumulus13>`_
* `Ko-fi <https://ko-fi.com/cumulus13>`_
* `Patreon <https://www.patreon.com/cumulus13>`_
