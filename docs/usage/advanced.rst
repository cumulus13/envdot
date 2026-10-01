=================
Advanced Features
=================

This guide covers advanced envdot features for power users and complex use cases.

Load Options
------------

Override Behavior
~~~~~~~~~~~~~~~~~~~

Control whether existing values are overwritten:

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')

   env.load(override=True)   # default: override existing values
   env.load(override=False)  # keep existing values, only add new ones

OS Environment Sync
~~~~~~~~~~~~~~~~~~~~~

Control synchronization with ``os.environ``:

.. code-block:: python

   # Apply to os.environ (default)
   env.load(apply_to_os=True)

   # Don't modify os.environ
   env.load(apply_to_os=False)

   # Set individual values without os.environ sync
   env.set('INTERNAL_KEY', 'value', apply_to_os=False)

Multiple Configuration Files
--------------------------------

Load from multiple sources:

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv(auto_load=False)

   # Load base configuration
   env.load('.env')

   # Overlay environment-specific settings
   env.load('.env.production', override=True)

   # Add local overrides
   env.load('.env.local', override=True)

Priority order (last wins): ``.env`` -> ``.env.production`` -> ``.env.local``.

1. ``.env`` - Base configuration
2. ``.env.production`` - Environment-specific
3. ``.env.local`` - Local developer overrides

Environment-Based Loading
-----------------------------

Load different configurations based on environment:

.. code-block:: python

   import os
   from envdot import DotEnv
   from envdot.exceptions import FileNotFoundError as EnvdotFileNotFoundError

   def load_config():
       env = DotEnv(auto_load=False)

       # Always load base config
       env.load('.env')

       # Load environment-specific config
       environment = os.getenv('ENVIRONMENT', 'development')
       env_file = f'.env.{environment}'

       try:
           env.load(env_file, override=True)
       except EnvdotFileNotFoundError:
           pass  # environment-specific file is optional
       except FileNotFoundError:
           pass  # Environment-specific file is optional

       return env

   config = load_config()

.. note::

   Catch ``envdot.exceptions.FileNotFoundError``, not the builtin
   ``FileNotFoundError`` — envdot defines its own exception of that name
   (see :doc:`../api/exceptions`). If you ``import envdot`` and then
   ``from envdot.exceptions import FileNotFoundError``, that import shadows
   the builtin in your module's namespace, which is convenient here but
   worth being deliberate about elsewhere in the same file.

Searching, Filtering, and Finding Keys
-------------------------------------------

Beyond simple ``get()``, envdot can search across all loaded variables:

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')

   # Wildcard, regex, or "contains" key matching
   env.find('DB_*')                            # wildcard (default mode)
   env.find(r'^API_\w+_KEY$', mode='regex')
   env.find('DB', mode='contains')

   env.find_wildcard('DB_*')                   # shortcuts for each mode
   env.find_regex(r'^API_\w+_KEY$')
   env.find_contains('DB')

   env.find_keys('DB_*')                       # just the matching key names

   # Search by VALUE pattern instead of key
   env.find_values('postgres*')

   # Arbitrary predicate over (key, value) pairs
   env.filter(lambda k, v: isinstance(v, str) and v.strip())

   # Search key AND/OR value together
   env.search('DB_*', value='postgres*')

The module-level equivalents (``find_env``, ``filter_env``, ``search_env``)
operate on the shared global instance the same way ``get_env``/``set_env`` do:

.. code-block:: python

   from envdot.core import find_env, filter_env, search_env

   find_env('DB_*')

After ``patch_os_module()``, these are also available as ``os.find()``,
``os.filter()``, and ``os.search()``.

All of these go through the same auto-reload check as ``get()`` — see
:doc:`auto-reload`.

Custom Type Handlers
-----------------------

For types envdot doesn't cast to directly, post-process after loading:

.. code-block:: python

   from envdot import DotEnv
   import json

   env = DotEnv('.env')

   # Parse a JSON array value manually if you need something cast_type
   # doesn't cover directly
   # ALLOWED_HOSTS=["localhost", "127.0.0.1"]
   hosts_str = env.get('ALLOWED_HOSTS', cast_type=str)
   allowed_hosts = json.loads(hosts_str) if hosts_str else []

   # cast_type=list/tuple already handles simple comma/whitespace-separated
   # values and bracketed literals directly - see usage/type-detection
   cors_origins = env.get('CORS_ORIGINS', cast_type=list, default=[])

Configuration Classes
------------------------

Create structured configuration classes:

.. code-block:: python

   from dataclasses import dataclass
   from envdot import DotEnv

   @dataclass
   class DatabaseConfig:
       host: str
       port: int
       name: str
       user: str
       password: str

   @dataclass
   class AppConfig:
       debug: bool
       port: int
       workers: int
       database: DatabaseConfig

   def load_config() -> AppConfig:
       env = DotEnv('.env')

       db_config = DatabaseConfig(
           host=env.get('DB_HOST', default='localhost'),
           port=env.get('DB_PORT', default=5432),
           name=env.get('DB_NAME', default='app'),
           user=env.get('DB_USER', default='postgres'),
           password=env.get('DB_PASSWORD', default=''),
       )

       return AppConfig(
           debug=env.get('DEBUG', default=False),
           port=env.get('PORT', default=8000),
           workers=env.get('WORKERS', default=4),
           database=db_config,
       )

   config = load_config()
   print(f"Connecting to {config.database.host}:{config.database.port}")

Validation
----------

Validate required variables:

.. code-block:: python

   from envdot import DotEnv

   def validate_config(env: DotEnv):
       required_keys = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
       missing = [key for key in required_keys if key not in env]

       if missing:
           raise ValueError(f"Missing required environment variables: {missing}")

   env = DotEnv('.env')
   validate_config(env)

Value Validation
~~~~~~~~~~~~~~~~~~

Validate value ranges and formats:

.. code-block:: python

   from envdot import DotEnv
   import re

   def validate_values(env: DotEnv):
       # Validate port range
       port = env.get('PORT', default=8000)
       if not (1 <= port <= 65535):
           raise ValueError(f"PORT must be between 1 and 65535, got {port}")

       # Validate URL format
       db_url = env.get('DATABASE_URL')
       if db_url and not db_url.startswith(('postgresql://', 'mysql://')):
           raise ValueError("DATABASE_URL must be a valid database URL")

       # Validate secret key length
       secret = env.get('SECRET_KEY', default='')
       if len(secret) < 32:
           raise ValueError("SECRET_KEY should be at least 32 characters")

   env = DotEnv('.env')
   validate_values(env)

Context Managers
-----------------

Use envdot in temporary contexts:

.. code-block:: python

   import os
   from contextlib import contextmanager
   from envdot import DotEnv

   @contextmanager
   def temp_env(**kwargs):
       """Temporarily set environment variables."""
       env = DotEnv(auto_load=False)
       original = {}

       # Save original values and set new ones
       for key, value in kwargs.items():
           original[key] = os.environ.get(key)
           env.set(key, value)

       try:
           yield env
       finally:
           # Restore original values
           for key, value in original.items():
               if value is None:
                   os.environ.pop(key, None)
               else:
                   os.environ[key] = value

   # Usage
   with temp_env(DEBUG=True, PORT=9000):
       # These values are only set within this block
       print(os.getenv('DEBUG'))  # True
       print(os.getenv('PORT'))   # 9000

   # Original values restored here

Lazy Loading
------------

Defer loading until first access:

.. code-block:: python

   from envdot import DotEnv

   class LazyConfig:
       _instance = None
       _loaded = False

       @classmethod
       def get_instance(cls) -> DotEnv:
           if cls._instance is None:
               cls._instance = DotEnv('.env', auto_load=False)

           if not cls._loaded:
               cls._instance.load()
               cls._loaded = True

           return cls._instance

   # First access triggers loading
   config = LazyConfig.get_instance()

Watching for File Changes
-----------------------------

You generally don't need a file watcher — every ``get()``/``show()``/etc.
call already checks the file's content hash and reloads automatically if
it changed (see :doc:`auto-reload`). If you specifically want to run code
*at the moment* a change is detected (e.g. logging "reloaded config"),
poll ``check_file()`` yourself:

.. code-block:: python

   from envdot import DotEnv
   import time

   env = DotEnv('.env')

   while True:
       if not env.check_file():          # False means "changed, was reloaded"
           print("Configuration changed and was reloaded")
       time.sleep(1)

For environment variables changed **outside the process** (registry /
``/etc/environment``), see :doc:`system-env-watch` instead — that's a
different mechanism from file-content watching.

.. code-block:: python

   from envdot import DotEnv
   from watchdog.observers import Observer
   from watchdog.events import FileSystemEventHandler

   class ConfigReloader(FileSystemEventHandler):
       def __init__(self, env: DotEnv, filepath: str):
           self.env = env
           self.filepath = filepath

       def on_modified(self, event):
           if event.src_path.endswith(self.filepath):
               print(f"Reloading configuration from {self.filepath}")
               self.env.load(override=True)

   # Setup
   env = DotEnv('.env')
   handler = ConfigReloader(env, '.env')
   observer = Observer()
   observer.schedule(handler, '.', recursive=False)
   observer.start()

Thread Safety
-------------

For multi-threaded applications:

.. code-block:: python

   import threading
   from envdot import DotEnv

   class ThreadSafeConfig:
       _lock = threading.Lock()
       _instance = None

       @classmethod
       def get_instance(cls) -> DotEnv:
           if cls._instance is None:
               with cls._lock:
                   if cls._instance is None:
                       cls._instance = DotEnv('.env')
           return cls._instance

   # Thread-safe singleton access
   config = ThreadSafeConfig.get_instance()

Testing with envdot
--------------------

Mock configuration in tests:

.. code-block:: python

   import pytest
   from envdot import DotEnv

   @pytest.fixture
   def mock_env(tmp_path):
       """Create a temporary .env file for testing."""
       env_file = tmp_path / '.env'
       env_file.write_text('''
           DEBUG=true
           PORT=8080
           DATABASE_URL=sqlite:///test.db
       ''')

       env = DotEnv(str(env_file))
       yield env

       # Cleanup
       env.clear(clear_os=True)

   def test_config_loading(mock_env):
       assert mock_env.get('DEBUG') is True
       assert mock_env.get('PORT') == 8080

Isolation between tests:

.. code-block:: python

   @pytest.fixture(autouse=True)
   def isolate_env():
       """Isolate environment between tests."""
       import os
       original_env = os.environ.copy()

       yield

       # Restore original environment
       os.environ.clear()
       os.environ.update(original_env)
