======================
Convenience Functions
======================

Module-level convenience functions that operate on a shared global
``DotEnv`` instance, so you don't have to instantiate ``DotEnv`` yourself
for simple scripts.

.. module:: envdot
   :no-index:
   :synopsis: Convenience functions for environment variable management

load_env()
----------

.. function:: load_env(filepath=None, auto_replace_getenv=True, apply_to_os=True, patch_os=True, debugging=False, watch_system_env=False, **kwargs)

   Load environment variables from a file into the shared global instance.

   :param filepath: Path to configuration file (auto-discovered, ``.env``
      by default, if omitted).
   :type filepath: str or Path or None
   :param auto_replace_getenv: Replace ``os.getenv`` with a typed version
      (default: ``True``). See :func:`replace_os_getenv`.
   :type auto_replace_getenv: bool
   :param patch_os: Also patch the ``os`` module with extra helpers like
      ``os.setenv``, ``os.find``, ``os.save_env`` (default: ``True``).
      See :func:`envdot.patch_os_module`.
   :type patch_os: bool
   :param watch_system_env: Also start :doc:`../usage/system-env-watch`
      (default: ``False``).
   :type watch_system_env: bool
   :param kwargs: Passed through to :meth:`DotEnv.load`.
   :returns: The shared global ``DotEnv`` instance, for attribute access
      or chaining.
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      from envdot import load_env

      # Load from default .env
      config = load_env()

      # Load from specific file
      config = load_env('config/production.env')
      config = load_env(watch_system_env=True)

      # Access values via attributes
      print(config.DEBUG)
      print(config.PORT)

get_env()
---------

.. function:: get_env(key, default=None, cast_type=None, **kwargs)

   Get a variable from the shared global instance. ``kwargs`` are passed
   through to :meth:`DotEnv.get` (e.g. ``reload=False``, ``with_os=False``).

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist
   :type default: Any
   :param cast_type: Force conversion to specific type
   :type cast_type: type or None
   :returns: The value with detected or cast type
   :rtype: Any

   **Example:**

   .. code-block:: python

      from envdot import load_env, get_env

      load_env()

      # Get with auto type detection
      debug = get_env('DEBUG')
      port = get_env('PORT')

      # Get with default value
      timeout = get_env('TIMEOUT', default=30)

      # Get with explicit type
      version = get_env('VERSION', cast_type=str)

set_env()
---------

.. function:: set_env(key, value=None, option=None, **kwargs)

   Set a variable on the shared global instance.

   :param key: The variable name
   :type key: str
   :param value: The value to set
   :type value: Any
   :param kwargs: Additional arguments passed to DotEnv.set()
   :returns: None

   **Example:**

   .. code-block:: python

      from envdot import set_env

      set_env('NEW_FEATURE', True)
      set_env('MAX_WORKERS', 8)
      set_env('API_URL', 'https://api.example.com')

save_env()
----------

.. function:: save_env(filepath=None, **kwargs)

   Save the shared global instance's variables to a file.

   :param filepath: Path to save file
   :type filepath: str or Path or None
   :param kwargs: Additional arguments passed to DotEnv.save()
   :returns: None

   **Example:**

   .. code-block:: python

      from envdot import load_env, set_env, save_env

      load_env()
      set_env('NEW_KEY', 'value')

      # Save to original file
      save_env()

      # Save to different file
      save_env('backup.env')

      # Save as different format
      save_env('config.json')

show()
------

.. function:: show()

   Display all loaded variables from the shared global instance (same as
   ``DotEnv.show()``).

   :returns: Dictionary of all variables
   :rtype: dict

   **Example:**

   .. code-block:: python

      from envdot import load_env, show

      load_env()
      show()

find_env() / filter_env() / search_env()
--------------------------------------------

.. function:: find_env(pattern, mode='wildcard', **kwargs)
.. function:: filter_env(predicate)
.. function:: search_env(pattern, value=None, mode='wildcard', **kwargs)

   Module-level equivalents of :meth:`DotEnv.find`, :meth:`DotEnv.filter`,
   and :meth:`DotEnv.search` on the shared global instance. Import these
   from :mod:`envdot.core` (they aren't re-exported from the top-level
   ``envdot`` package):

   .. code-block:: python

      from envdot.core import find_env, filter_env, search_env

      find_env('DB_*')

sync_system_env()
-------------------

.. function:: sync_system_env()

   Apply any pending persistent environment changes on the shared global
   instance immediately, if :doc:`../usage/system-env-watch` is enabled.
   Import from :mod:`envdot.core`.

Combined Example
------------------

.. code-block:: python

   from envdot import load_env, get_env, set_env, save_env, show

   # Load environment
   config = load_env('.env')

   # Display all variables
   print("Current configuration:")
   show()

   # Get specific values
   debug = get_env('DEBUG', default=False)
   port = get_env('PORT', default=8000)
   db_url = get_env('DATABASE_URL')

   print(f"\nApplication settings:")
   print(f"  Debug mode: {debug}")
   print(f"  Port: {port}")
   print(f"  Database: {db_url}")

   # Modify configuration
   set_env('DEBUG', False)
   set_env('PORT', 9000)
   set_env('NEW_FEATURE', True)

   # Save changes
   save_env()

   print("\nConfiguration updated and saved!")

Functions vs the DotEnv Class
----------------------------------

**Using convenience functions** (share one global instance — ideal for
simple scripts):

.. code-block:: python

   from envdot import load_env, get_env, set_env, save_env

   load_env('.env')
   debug = get_env('DEBUG')
   set_env('PORT', 9000)
   save_env()

**Using the DotEnv class** (own instance — better for multiple
configuration files or more complex applications):

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')
   debug = env.get('DEBUG')
   env.set('PORT', 9000)
   env.save()

The convenience functions use a shared global instance internally, making them 
ideal for simple applications. For more complex scenarios with multiple 
configuration files, use the ``DotEnv`` class directly.
