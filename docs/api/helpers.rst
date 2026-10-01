================
Helper Functions
================

envdot provides type-specific helper functions that serve as enhanced
replacements for ``os.getenv()``, plus utilities for patching the ``os``
module itself.

.. module:: envdot
   :no-index:
   :synopsis: Type-specific helper functions

Typed Getters
-------------

getenv_typed()
~~~~~~~~~~~~~~~

.. function:: getenv_typed(key, default=None, cast_type=None)

   Enhanced replacement for ``os.getenv()`` with automatic type detection
   (and, unlike ``os.getenv()``, it re-checks the config file's content
   hash first — see :doc:`../usage/auto-reload` — so it stays live).

   :param key: The variable name.
   :type key: str
   :param default: Default value if the key doesn't exist.
   :type default: Any
   :param cast_type: Force conversion to a specific type, cast from the
      original raw string (see :doc:`../usage/type-detection`).
   :type cast_type: type or None
   :returns: Value with detected or cast type.
   :rtype: bool, int, float, str, list, tuple, dict, or None

   **Example:**

   .. code-block:: python

      from envdot import getenv_typed

      # Auto-detects types unless with 'cast_type'
      debug = getenv_typed('DEBUG')      # True (bool)
      port = getenv_typed('PORT')        # 8080 (int)
      timeout = getenv_typed('TIMEOUT')  # 30.5 (float)
      name = getenv_typed('APP_NAME')    # 'MyApp' (str)

getenv_int() / getenv_float() / getenv_bool() / getenv_str()
------------------------------------------------------------------

.. function:: getenv_int(key, default=0)
.. function:: getenv_float(key, default=0.0)
.. function:: getenv_bool(key, default=False)
.. function:: getenv_str(key, default='')

   Thin wrappers around :func:`getenv_typed` that fix ``cast_type`` to
   ``int``/``float``/``bool``/``str`` respectively.

   For ``getenv_bool``, both the usual words (``true``/``yes``/``on`` and
   ``false``/``no``/``off``) **and** ``1``/``0`` are recognized as
   booleans — this is different from *automatic* detection elsewhere in
   envdot, where a bare ``1``/``0`` normally detects as ``int`` (see
   :doc:`../usage/type-detection`). Because you're explicitly asking for
   a bool here, the ambiguity is resolved in favor of boolean.

   **Example:**

   .. code-block:: python

      from envdot import getenv_int, getenv_bool, getenv_float, getenv_str

      port = getenv_int('PORT', default=8000)
      debug = getenv_bool('DEBUG', default=False)
      timeout = getenv_float('TIMEOUT', default=30.0)
      name = getenv_str('APP_NAME', default='MyApp')

Typed Setter
------------

setenv_typed()
~~~~~~~~~~~~~~~

.. function:: setenv_typed(key, value)

   Set ``os.environ[key]`` from any Python value, converting it to its
   string representation the same way envdot would write it to a file.

   **Example:**

   .. code-block:: python

      from envdot import setenv_typed

      setenv_typed('DEBUG', True)      # os.environ['DEBUG'] = 'true'
      setenv_typed('PORT', 8080)       # os.environ['PORT'] = '8080'
      setenv_typed('TIMEOUT', 30.5)    # os.environ['TIMEOUT'] = '30.5'

Replacing / Restoring ``os.getenv``
----------------------------------------

replace_os_getenv()
~~~~~~~~~~~~~~~~~~~~~~

.. function:: replace_os_getenv()

   Replace the built-in ``os.getenv`` with :func:`getenv_typed`, so every
   call to ``os.getenv()`` anywhere in your codebase — including in
   third-party libraries — returns typed, auto-reloading values instead
   of plain strings. Called automatically by :func:`load_env` unless you
   pass ``auto_replace_getenv=False``.

   .. warning::

      This modifies ``os.getenv`` **globally** for the whole process.

   **Example:**

   .. code-block:: python

      import os
      from envdot import replace_os_getenv, load_env

      replace_os_getenv()
      load_env()

      port = os.getenv('PORT')     # 8080 (int), not '8080' (str)
      debug = os.getenv('DEBUG')   # True (bool)

restore_os_getenv()
~~~~~~~~~~~~~~~~~~~~~~

.. function:: restore_os_getenv()

   Restore the original, unpatched ``os.getenv``.

Patching the ``os`` Module
------------------------------

patch_os_module()
~~~~~~~~~~~~~~~~~~~~

.. function:: patch_os_module()

   Attach a set of envdot-powered helpers directly onto the ``os`` module.
   Called automatically by :func:`load_env` unless you pass
   ``patch_os=False``.

   After calling this, ``os`` additionally has:

   .. list-table::
      :header-rows: 1
      :widths: 35 65

      * - Attribute
        - Equivalent to
      * - ``os.getenv_typed`` / ``os.getenv_int`` / ``os.getenv_float`` / ``os.getenv_bool`` / ``os.getenv_str``
        - the matching function above
      * - ``os.setenv_typed``
        - :func:`setenv_typed`
      * - ``os.setenv`` / ``os.writeenv`` / ``os.write_env`` / ``os.write_config`` / ``os._write``
        - ``envdot.set_env``
      * - ``os.find`` / ``os.filter`` / ``os.search``
        - ``find_env`` / ``filter_env`` / ``search_env`` on the shared global instance
      * - ``os.save_env``
        - :func:`envdot.core.save_env`
      * - ``os.show`` / ``os._show`` / ``os.show_config``
        - :func:`show`
      * - ``os.configfile`` / ``os.config_file`` / ``os.configpath`` / ``os.config_path`` / ``os.fileconfig`` / ``os.file_config``
        - a live proxy for the shared global instance's current config
          file path (always reflects the *current* path, even after a
          later ``load_env()`` call changes it)

   **Example:**

   .. code-block:: python

      from envdot import patch_os_module, load_env
      import os

      load_env()          # calls patch_os_module() for you by default
      # or call it yourself:
      patch_os_module()

      debug = os.getenv_bool('DEBUG', default=False)
      port = os.getenv_int('PORT', default=8000)
      timeout = os.getenv_float('TIMEOUT', default=30.0)

      # Set typed values
      os.setenv_typed('NEW_PORT', 9000)
      os.setenv_typed('FEATURE_ENABLED', True)
      os.find('DB_*')
      print(os.configfile)   # e.g. PosixPath('.env')

Comparison: Standard vs Typed
----------------------------------

Here's why typed helpers are useful:

**Standard os.getenv() - always returns strings:**

.. code-block:: python

   import os

   os.environ['PORT'] = '8080'
   os.environ['DEBUG'] = 'true'

   port = os.getenv('PORT')   # '8080' (str)
   debug = os.getenv('DEBUG') # 'true' (str)

   # Manual conversion required
   port = int(os.getenv('PORT', '8000'))
   debug = os.getenv('DEBUG', 'false').lower() in ('true', 'yes', '1', 'on')

**envdot helpers - properly typed:**

.. code-block:: python

   from envdot import getenv_int, getenv_bool

   port = getenv_int('PORT', default=8000)     # 8080 (int)
   debug = getenv_bool('DEBUG', default=False) # True (bool)

   # No manual conversion needed!

Complete Example
------------------

.. code-block:: python

   from envdot import (
       load_env,
       getenv_typed,
       getenv_int,
       getenv_bool,
       getenv_float,
       getenv_str,
       setenv_typed
   )

   # Load environment
   load_env('.env')

   # Database configuration
   db_config = {
       'host': getenv_str('DB_HOST', default='localhost'),
       'port': getenv_int('DB_PORT', default=5432),
       'pool_size': getenv_int('DB_POOL_SIZE', default=5),
       'timeout': getenv_float('DB_TIMEOUT', default=30.0),
       'ssl_enabled': getenv_bool('DB_SSL', default=False),
   }

   # Application settings
   app_config = {
       'debug': getenv_bool('DEBUG', default=False),
       'port': getenv_int('PORT', default=8000),
       'workers': getenv_int('WORKERS', default=4),
       'name': getenv_str('APP_NAME', default='MyApp'),
   }

   # Set new configuration
   setenv_typed('NEW_FEATURE', True)
   setenv_typed('MAX_CONNECTIONS', 100)

   print("Database Config:", db_config)
   print("Application Config:", app_config)
