=============
DotEnv Class
=============

The ``DotEnv`` class is the main interface for managing environment variables.

.. module:: envdot
   :synopsis: Enhanced environment variable management

Class Reference
----------------

.. class:: DotEnv(filepath=None, auto_load=True, newone=False)

   Main class for environment variable management.

   :param filepath: Path to a configuration file. If given but the file
      does not exist, it is kept as-is (not silently swapped for an
      auto-discovered file) so ``load()`` can correctly report it's
      missing. If omitted, envdot searches for a supported config file
      (``.env`` by default).
   :type filepath: str or Path or None
   :param auto_load: Automatically call :meth:`load` on construction
      (default: ``True``).
   :type auto_load: bool
   :param newone: If no config file can be found/given, create a new
      empty ``.env`` instead of staying unconfigured.
   :type newone: bool

   **Example:**

   .. code-block:: python

      from envdot import DotEnv

      env = DotEnv('.env')                      # auto-load from .env
      env = DotEnv('.env', auto_load=False)      # create without loading
      env = DotEnv()                             # auto-discover a config file

Loading
-------

load()
~~~~~~

.. method:: DotEnv.load(filepath=None, override=True, apply_to_os=True, store_typed=True, recursive=True, newone=False, os_overwrite=False, **kwargs)

   Load environment variables from a file.

   :param filepath: Path to file (uses the instance's tracked filepath if
      not specified).
   :type filepath: str or Path or None
   :param override: Whether to override already-loaded values for keys
      also present in the file (default: ``True``).
   :type override: bool
   :param apply_to_os: Whether to mirror loaded values into ``os.environ``
      (default: ``True``). See :doc:`../usage/auto-reload` for exactly
      when an already-set ``os.environ`` entry is or isn't overwritten.
   :type apply_to_os: bool
   :param os_overwrite: Force-overwrite ``os.environ`` even for a value
      envdot doesn't recognize as its own (default: ``False``).
   :type os_overwrite: bool
   :param recursive: Search subdirectories when no filepath is known and
      one must be auto-discovered (default: ``True``).
   :type recursive: bool
   :returns: ``self``, for method chaining.
   :rtype: DotEnv
   :raises envdot.exceptions.FileNotFoundError: If an *explicit* filepath
      (given here or at construction) doesn't exist. A filepath that was
      never given at all (auto-discovery finding nothing) does not raise.
   :raises envdot.exceptions.ParseError: If the file can't be parsed.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env', auto_load=False)

      # Basic load
      env.load()

      # Load from different file
      env.load('config.json')

      # Load without overriding existing values
      env.load(override=False)

      # Load without affecting os.environ
      env.load(apply_to_os=False)

check_file()
~~~~~~~~~~~~~

.. method:: DotEnv.check_file()

   Check whether the tracked config file's content has changed since the
   last load, using a content hash comparison.

   :returns: ``True`` if nothing changed (safe to skip a reload), ``False``
      if a reload is needed. Calling this does **not** itself reload the
      file — see :meth:`get` and the other read methods, which call this
      internally and reload automatically when it returns ``False``.
   :rtype: bool

Getting Values
--------------

get()
~~~~~

.. method:: DotEnv.get(key, default=None, cast_type=None, reload=True, with_os=True)

   Get an environment variable with automatic type detection.

   :param key: The variable name.
   :type key: str
   :param default: Value to return if the key doesn't exist.
   :type default: Any
   :param cast_type: Force conversion to a specific type
      (``int``, ``float``, ``bool``, ``str``, ``list``, ``tuple``, ``dict``).
      Always casts from the original raw string, not from an
      already-auto-detected value.
   :type cast_type: type or None
   :param reload: If ``True`` (default), checks the config file's content
      hash and reloads if it changed. Pass ``False`` to skip that check
      for this call.
   :type reload: bool
   :param with_os: If ``True`` (default), falls back to ``os.environ`` for
      a key envdot has no value of its own for, and picks up a direct
      ``os.environ[key] = ...`` change made after envdot last wrote that
      key. See :doc:`../usage/auto-reload`.
   :type with_os: bool
   :returns: The value with detected or cast type.
   :rtype: Any
   :raises envdot.exceptions.TypeConversionError: If ``cast_type`` is
      given and conversion fails.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')

      # Get with auto type detection
      debug = env.get('DEBUG')  # Returns bool
      port = env.get('PORT')    # Returns int

      # Get with default
      timeout = env.get('TIMEOUT', default=30)

      # Get with explicit type casting
      version = env.get('PORT', cast_type=str)
      hosts = env.get('ALLOWED_HOSTS', cast_type=list)

Setting Values
--------------

set()
~~~~~

.. method:: DotEnv.set(key, value, apply_to_os=True)

   Set an environment variable. A **string** value is auto-detected the
   same way a value loaded from a file would be (so ``set('EMPTY', '')``
   -> ``None``, ``set('COUNT', '5')`` -> ``int`` ``5``); a non-string
   value you pass directly is stored exactly as given.

   :param key: The variable name.
   :type key: str
   :param value: The value to set.
   :type value: Any
   :param apply_to_os: Whether to also set it in ``os.environ``
      (default: ``True``).
   :type apply_to_os: bool
   :returns: ``self``, for method chaining.
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')

      # Set various types
      env.set('DEBUG', True)
      env.set('PORT', 8080)
      env.set('TIMEOUT', 30.5)
      env.set('APP_NAME', 'MyApp')

      # Set without affecting os.environ
      env.set('INTERNAL', 'value', apply_to_os=False)

Persisting Changes
---------------------

save()
~~~~~~

.. method:: DotEnv.save(filepath=None, format=None)

   Save the current variables to a file.

   :param filepath: Path to save to (uses the instance's tracked filepath
      if not specified).
   :type filepath: str or Path or None
   :param format: File format (``env``, ``json``, ``yaml``, ``ini``,
      ``toml``) — auto-detected from the extension if not given.
   :type format: str or None
   :returns: ``self``, for method chaining.
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      env.set('NEW_KEY', 'value')

      env.save()                # to the original file
      env.save('backup.env')    # to a new file
      env.save('config.json')   # convert to a different format

delete()
~~~~~~~~~

.. method:: DotEnv.delete(key, remove_from_os=True)

   Delete a variable.

   :param key: The variable name to delete.
   :type key: str
   :param remove_from_os: Whether to also remove it from ``os.environ``
      (default: ``True``).
   :type remove_from_os: bool
   :returns: ``self``, for method chaining.
   :rtype: DotEnv

clear()
~~~~~~~~

.. method:: DotEnv.clear(clear_os=False)

   Clear all stored variables.

   :param clear_os: Whether to also remove them from ``os.environ``
      (default: ``False``).
   :type clear_os: bool
   :returns: ``self``, for method chaining.
   :rtype: DotEnv

Reading Everything
--------------------

Every method in this section re-checks the config file's content hash
first, the same way :meth:`get` does — see :doc:`../usage/auto-reload`.

all()
~~~~~~

.. method:: DotEnv.all()

   :returns: ``os.environ`` merged with envdot's own loaded data (its own
      data wins on overlap).
   :rtype: dict

show()
~~~~~~~

.. method:: DotEnv.show(all=False)

   :param all: If ``True``, equivalent to :meth:`all`; if ``False``
      (default), returns just envdot's own loaded data.
   :type all: bool
   :returns: Dictionary of variables.
   :rtype: dict

keys()
~~~~~~~

.. method:: DotEnv.keys(all=False)

   :param all: Same meaning as in :meth:`show`.
   :type all: bool
   :returns: List of variable names.
   :rtype: list

Searching and Filtering
----------------------------

See :doc:`../usage/advanced` for full usage examples of this group.

find()
~~~~~~~

.. method:: DotEnv.find(pattern, mode='wildcard', case_sensitive=True, return_dict=True, reload=False)

   Find keys matching a pattern.

   :param pattern: A wildcard (``DB_*``), regex, or plain substring
      pattern, depending on ``mode``.
   :type pattern: str
   :param mode: ``'wildcard'`` (default), ``'regex'``, or ``'contains'``.
   :type mode: str
   :returns: Matching ``{key: value}`` pairs (or a list of ``(key, value)``
      tuples if ``return_dict=False``).
   :rtype: dict or list

find_wildcard() / find_regex() / find_contains()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: DotEnv.find_wildcard(pattern, **kwargs)
.. method:: DotEnv.find_regex(pattern, **kwargs)
.. method:: DotEnv.find_contains(pattern, **kwargs)

   Shortcuts for :meth:`find` with a fixed ``mode``.

find_keys()
~~~~~~~~~~~~

.. method:: DotEnv.find_keys(pattern, mode='wildcard', **kwargs)

   :returns: Just the matching key names.
   :rtype: list[str]

find_values()
~~~~~~~~~~~~~~

.. method:: DotEnv.find_values(value_pattern, case_sensitive=False, **kwargs)

   Find entries whose **value** matches ``value_pattern``.

   :returns: Matching ``{key: value}`` pairs.
   :rtype: dict

filter()
~~~~~~~~~

.. method:: DotEnv.filter(predicate)

   :param predicate: A ``callable(key, value) -> bool``.
   :returns: Entries for which ``predicate`` returned true-y.
   :rtype: dict

   **Example:**

   .. code-block:: python

      env.filter(lambda k, v: isinstance(v, str) and v.strip())

search()
~~~~~~~~~

.. method:: DotEnv.search(pattern, value=None, mode='wildcard', **kwargs)

   Search by key pattern and, optionally, an additional value pattern.

System Environment Watching
--------------------------------

See :doc:`../usage/system-env-watch` for full details.

enable_system_watch()
~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: DotEnv.enable_system_watch(ignore=('PATH',), min_interval=0.25, backend=None)

   Start applying persistent (Windows registry / Linux env-file)
   environment changes made outside this process.

   :returns: ``True`` if the current platform is supported, ``False``
      otherwise (always safe to call either way).
   :rtype: bool

disable_system_watch()
~~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: DotEnv.disable_system_watch()

   Stop applying persistent environment changes.

Magic Methods
-------------

__getitem__ / __setitem__ / __contains__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   env = DotEnv('.env')

   value = env['DATABASE_URL']
   env['NEW_KEY'] = 'value'
   if 'API_KEY' in env:
       ...

__getattr__ / __setattr__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   config = DotEnv('.env')

   debug = config.DEBUG
   config.PORT = 9000

__call__
~~~~~~~~~

.. method:: DotEnv.__call__(key, value=None, default=None)

   Calling an instance is a shortcut: with just a ``key`` it behaves like
   :meth:`get`; passing ``value`` behaves like :meth:`set`.

   .. code-block:: python

      env = DotEnv('.env')
      env('DEBUG')            # get
      env('DEBUG', True)      # set

__repr__
~~~~~~~~~

.. method:: DotEnv.__repr__()

   String representation of the DotEnv instance.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      print(env)  # DotEnv(filepath=.env, vars=18)
