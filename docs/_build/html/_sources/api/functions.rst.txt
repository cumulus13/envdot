======================
Convenience Functions
======================

envdot provides module-level convenience functions for quick and easy access 
to environment variables without needing to instantiate the ``DotEnv`` class.

.. module:: envdot
   :synopsis: Convenience functions for environment variable management

load_env()
----------

.. function:: load_env(filepath=None, **kwargs)

   Load environment variables from a file.

   :param filepath: Path to configuration file (default: '.env')
   :type filepath: str or Path or None
   :param kwargs: Additional arguments passed to DotEnv.load()
   :returns: DotEnv instance for method chaining or attribute access
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      from envdot import load_env

      # Load from default .env
      config = load_env()

      # Load from specific file
      config = load_env('config/production.env')

      # Access values via attributes
      print(config.DEBUG)
      print(config.PORT)

get_env()
---------

.. function:: get_env(key, default=None, cast_type=None)

   Get an environment variable with automatic type detection.

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

.. function:: set_env(key, value, **kwargs)

   Set an environment variable.

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

   Save environment variables to a file.

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

   Display all loaded environment variables.

   :returns: Dictionary of all variables
   :rtype: dict

   **Example:**

   .. code-block:: python

      from envdot import load_env, show

      load_env()
      show()

      # Output:
      # {'DEBUG': True,
      #  'PORT': 8080,
      #  'DATABASE_URL': 'postgresql://localhost/mydb',
      #  ...}

Combined Example
----------------

Here's a complete example using all convenience functions:

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

Comparison: Functions vs Class
------------------------------

Both approaches are equivalent. Choose based on your preference:

**Using convenience functions:**

.. code-block:: python

   from envdot import load_env, get_env, set_env, save_env

   load_env('.env')
   debug = get_env('DEBUG')
   set_env('PORT', 9000)
   save_env()

**Using DotEnv class:**

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')
   debug = env.get('DEBUG')
   env.set('PORT', 9000)
   env.save()

The convenience functions use a shared global instance internally, making them 
ideal for simple applications. For more complex scenarios with multiple 
configuration files, use the ``DotEnv`` class directly.