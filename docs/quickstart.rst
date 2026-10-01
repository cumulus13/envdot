==========
Quickstart
==========

This guide will help you get started with envdot in just a few minutes.

Creating Your First .env File
------------------------------

Create a ``.env`` file in your project root:

.. code-block:: bash

   # .env
   DEBUG=true
   PORT=8080
   DATABASE_URL=postgresql://localhost/mydb
   API_TIMEOUT=30.5
   APP_NAME=MyApplication

Loading Environment Variables
------------------------------

The simplest way to load your environment variables:

.. code-block:: python

   from envdot import load_env

   # Load from .env in the current directory (searched automatically)
   load_env()

   # or load_env('.env')
   # or load_env('config.json')
   # or load_env('config.yaml')
   # or load_env('config.ini')
   # or load_env('config.toml')
   # or load_env('config.env')
   # or load_env('/etc/config.env')
   # or load_env(r'c:\.env')
   # or load_env(r'c:\traceback.ini')

Using the DotEnv Class
------------------------

For more control, use the ``DotEnv`` class directly:

.. code-block:: python

   from envdot import DotEnv

   # Create instance and auto-load
   env = DotEnv('.env')

   # Access values with automatic type detection
   debug = env.get('DEBUG')          # Returns: True (bool)
   port = env.get('PORT')            # Returns: 8080 (int)
   timeout = env.get('API_TIMEOUT')  # Returns: 30.5 (float)

Automatic Type Detection
--------------------------

envdot automatically converts values to appropriate Python types:

.. code-block:: python

   from envdot import load_env, get_env

   load_env()

   # Boolean values
   debug = get_env('DEBUG')  # "true" -> True

   # Integer values
   port = get_env('PORT')    # "8080" -> 8080

   # Float values
   timeout = get_env('API_TIMEOUT')  # "30.5" -> 30.5

   # String values remain as strings - a space or comma in the value
   # does NOT turn it into a list/tuple automatically
   name = get_env('APP_NAME')  # "MyApplication" -> "MyApplication"

See :doc:`usage/type-detection` for the complete rules, and how to force a
type with ``cast_type``.

Setting Values
--------------

You can set new environment variables:

.. code-block:: python

   from envdot import set_env

   set_env('NEW_FEATURE', True)
   set_env('MAX_WORKERS', 4)

Or using the DotEnv class:

.. code-block:: python

   env = DotEnv('.env')
   env.set('NEW_KEY', 'value')
   env.set('FEATURE_ENABLED', True)

Attribute Access
------------------

envdot supports attribute-style access for convenience:

.. code-block:: python

   config = load_env()

   # Read values as attributes
   debug = config.DEBUG       # True
   port = config.PORT         # 8080

   # Set values as attributes
   config.DEBUG_SERVER = True

   # Changes sync with os.environ
   import os
   print(os.getenv('DEBUG_SERVER'))  # True

Saving Changes
--------------

Save your changes back to a file:

.. code-block:: python

   from envdot import save_env

   # Save to original file
   save_env()

   # Or save to a new file (format is inferred from the extension)
   save_env('config.json')

Method Chaining
----------------

Use method chaining for cleaner code:

.. code-block:: python

   from envdot import DotEnv

   env = (DotEnv('.env')
          .set('KEY1', 'value1')
          .set('KEY2', 123)
          .save())

Default Values
--------------

Provide default values for missing keys:

.. code-block:: python

   from envdot import get_env

   # Returns 3000 if PORT is not set
   port = get_env('PORT', default=3000)

   # Returns 'localhost' if DB_HOST is not set
   host = get_env('DB_HOST', default='localhost')

Auto-Reload — Just Read Again
--------------------------------

Every read reflects the current file content — no manual reload step, no
process restart:

.. code-block:: python

   from envdot import load_env, get_env

   conf = load_env('config.ini')
   print(conf.show())          # {'TAG_NAME': None, ...}

   # ...edit config.ini on disk, e.g. name = TEST under [tag]...

   print(conf.show())          # picks up the change automatically
   print(conf.TAG_NAME)        # 'TEST'
   print(get_env('TAG_NAME'))  # 'TEST'

See :doc:`usage/auto-reload` for exactly what triggers a reload and how to
control it.

Using with os.getenv
----------------------

After ``replace_os_getenv()`` (called automatically by ``load_env()``),
values are available via ``os.getenv`` with proper types:

.. code-block:: python

   import os
   from envdot import load_env

   load_env()

   # Values are properly typed even through os.getenv
   debug = os.getenv('DEBUG')  # True (bool), not "true" (str)
   port = os.getenv('PORT')    # 8080 (int), not "8080" (str)

Next Steps
----------

* Learn about :doc:`usage/file-formats` for JSON, YAML, INI, and TOML support
* Explore :doc:`usage/type-detection` for type conversion rules
* Understand :doc:`usage/auto-reload` for exactly when a reload happens
* Check out :doc:`usage/system-env-watch` for cross-process (registry) env changes
* See :doc:`usage/advanced` for advanced features
* See the :doc:`api/dotenv` for the complete API reference
