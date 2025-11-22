===========
Basic Usage
===========

This guide covers the fundamental operations you'll use most often with envdot.

Loading Environment Variables
-----------------------------

Using Convenience Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest approach is using the ``load_env`` function:

.. code-block:: python

   from envdot import load_env, get_env, set_env, show

   # Load from default .env file
   load_env()

   # Load from a specific file
   load_env('config/production.env')

   # Display all loaded variables
   show()

Using the DotEnv Class
~~~~~~~~~~~~~~~~~~~~~~

For more control, use the ``DotEnv`` class:

.. code-block:: python

   from envdot import DotEnv

   # Auto-load from .env
   env = DotEnv()

   # Specify a file path
   env = DotEnv('.env')

   # Create without auto-loading
   env = DotEnv('.env', auto_load=False)
   env.load()  # Manual load

Getting Values
--------------

Using get() Method
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')

   # Basic get
   value = env.get('DATABASE_URL')

   # Get with default value
   port = env.get('PORT', default=8080)

   # Get with explicit type casting
   version = env.get('VERSION', cast_type=str)

Using Convenience Function
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import load_env, get_env

   load_env()

   # Get value
   debug = get_env('DEBUG')

   # With default
   timeout = get_env('TIMEOUT', default=30)

Dictionary-Style Access
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   env = DotEnv('.env')

   # Get using brackets
   value = env['DATABASE_URL']

   # Check if key exists
   if 'API_KEY' in env:
       print("API key is configured")

   # Get all keys
   all_keys = env.keys()

   # Get all variables as dict
   all_vars = env.all()

Attribute Access
~~~~~~~~~~~~~~~~

.. code-block:: python

   config = load_env()

   # Access as attributes
   debug = config.DEBUG
   port = config.PORT

   # Set as attributes
   config.NEW_KEY = 'value'

Setting Values
--------------

Using set() Method
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')

   # Set a string value
   env.set('API_URL', 'https://api.example.com')

   # Set an integer
   env.set('MAX_CONNECTIONS', 100)

   # Set a boolean
   env.set('DEBUG', True)

   # Set a float
   env.set('TIMEOUT', 30.5)

   # Set without applying to os.environ
   env.set('INTERNAL_KEY', 'value', apply_to_os=False)

Using Convenience Function
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import set_env

   set_env('NEW_FEATURE', True)
   set_env('VERSION', '2.0.0')

Dictionary-Style Assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   env = DotEnv('.env')

   env['NEW_KEY'] = 'new_value'
   env['FEATURE_FLAG'] = True

Saving Variables
----------------

Save to File
~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv, save_env

   env = DotEnv('.env')
   env.set('NEW_KEY', 'value')

   # Save to original file
   env.save()

   # Save to a different file
   env.save('backup.env')

   # Save to different format
   env.save('config.json')

   # Using convenience function
   save_env('config.env')

Deleting Variables
------------------

.. code-block:: python

   env = DotEnv('.env')

   # Delete from envdot only
   env.delete('OLD_KEY')

   # Delete from both envdot and os.environ
   env.delete('TEMP_KEY', remove_from_os=True)

Clearing Variables
------------------

.. code-block:: python

   env = DotEnv('.env')

   # Clear internal storage only
   env.clear()

   # Also clear from os.environ
   env.clear(clear_os=True)

Display Variables
-----------------

.. code-block:: python

   from envdot import load_env, show

   env = load_env()

   # Show all variables (module-level function)
   show()

   # Show via instance method
   env.show()

Method Chaining
---------------

envdot supports method chaining for a fluent API:

.. code-block:: python

   env = (DotEnv('.env')
          .load()
          .set('KEY1', 'value1')
          .set('KEY2', 123)
          .set('KEY3', True)
          .save())

OS Environment Integration
--------------------------

By default, envdot syncs with ``os.environ``:

.. code-block:: python

   import os
   from envdot import load_env

   # Load and sync to os.environ
   load_env()

   # Access via os.environ (properly typed)
   debug = os.getenv('DEBUG')  # True (bool)

   # Control sync behavior
   env = DotEnv('.env')
   env.load(apply_to_os=False)  # Don't sync to os.environ

Real-World Example
------------------

Here's a complete example for a web application:

.. code-block:: python

   from envdot import DotEnv

   # Load configuration
   env = DotEnv('.env')

   # Database configuration
   db_config = {
       'host': env.get('DB_HOST', default='localhost'),
       'port': env.get('DB_PORT', default=5432),
       'database': env.get('DB_NAME', default='myapp'),
       'username': env.get('DB_USER', default='postgres'),
       'password': env.get('DB_PASSWORD'),
   }

   # Application settings
   app_config = {
       'debug': env.get('DEBUG', default=False),
       'port': env.get('PORT', default=8000),
       'workers': env.get('WORKERS', default=4),
       'timeout': env.get('TIMEOUT', default=30.0),
   }

   # Feature flags
   features = {
       'enable_api': env.get('FEATURE_API', default=True),
       'enable_webhooks': env.get('FEATURE_WEBHOOKS', default=False),
       'enable_cache': env.get('FEATURE_CACHE', default=True),
   }

   print("Database Config:", db_config)
   print("Application Config:", app_config)
   print("Feature Flags:", features)