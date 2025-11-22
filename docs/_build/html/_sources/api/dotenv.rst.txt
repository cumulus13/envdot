=============
DotEnv Class
=============

The ``DotEnv`` class is the main interface for managing environment variables.

.. module:: envdot
   :synopsis: Enhanced environment variable management

Class Reference
---------------

.. class:: DotEnv(filepath=None, auto_load=True)

   Main class for environment variable management.

   :param filepath: Path to configuration file (optional)
   :type filepath: str or Path or None
   :param auto_load: Automatically load file on initialization (default: True)
   :type auto_load: bool

   **Example:**

   .. code-block:: python

      from envdot import DotEnv

      # Auto-load from .env
      env = DotEnv('.env')

      # Create without loading
      env = DotEnv('.env', auto_load=False)

Methods
-------

load()
~~~~~~

.. method:: DotEnv.load(filepath=None, override=True, apply_to_os=True)

   Load environment variables from a file.

   :param filepath: Path to file (uses instance filepath if not specified)
   :type filepath: str or Path or None
   :param override: Whether to override existing values (default: True)
   :type override: bool
   :param apply_to_os: Whether to apply values to os.environ (default: True)
   :type apply_to_os: bool
   :returns: Self for method chaining
   :rtype: DotEnv
   :raises FileNotFoundError: If the specified file doesn't exist
   :raises ParseError: If the file cannot be parsed

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

get()
~~~~~

.. method:: DotEnv.get(key, default=None, cast_type=None)

   Get an environment variable with automatic type detection.

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist
   :type default: Any
   :param cast_type: Force conversion to specific type (int, float, bool, str)
   :type cast_type: type or None
   :returns: The value with detected or cast type
   :rtype: Any
   :raises TypeConversionError: If cast_type is specified and conversion fails

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

set()
~~~~~

.. method:: DotEnv.set(key, value, apply_to_os=True)

   Set an environment variable.

   :param key: The variable name
   :type key: str
   :param value: The value to set
   :type value: Any
   :param apply_to_os: Whether to also set in os.environ (default: True)
   :type apply_to_os: bool
   :returns: Self for method chaining
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

save()
~~~~~~

.. method:: DotEnv.save(filepath=None, format=None)

   Save environment variables to a file.

   :param filepath: Path to save file (uses instance filepath if not specified)
   :type filepath: str or Path or None
   :param format: File format ('env', 'json', 'yaml', 'ini') - auto-detected from extension if not specified
   :type format: str or None
   :returns: Self for method chaining
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      env.set('NEW_KEY', 'value')

      # Save to original file
      env.save()

      # Save to new file
      env.save('backup.env')

      # Convert to different format
      env.save('config.json')

delete()
~~~~~~~~

.. method:: DotEnv.delete(key, remove_from_os=True)

   Delete an environment variable.

   :param key: The variable name to delete
   :type key: str
   :param remove_from_os: Whether to also remove from os.environ (default: True)
   :type remove_from_os: bool
   :returns: Self for method chaining
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')

      # Delete from envdot and os.environ
      env.delete('OLD_KEY')

      # Delete from envdot only
      env.delete('TEMP_KEY', remove_from_os=False)

all()
~~~~~

.. method:: DotEnv.all()

   Get all environment variables as a dictionary.

   :returns: Dictionary of all variables
   :rtype: dict

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      all_vars = env.all()

      for key, value in all_vars.items():
          print(f"{key} = {value} ({type(value).__name__})")

keys()
~~~~~~

.. method:: DotEnv.keys()

   Get all variable names.

   :returns: List of variable names
   :rtype: list

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      for key in env.keys():
          print(key)

clear()
~~~~~~~

.. method:: DotEnv.clear(clear_os=False)

   Clear all stored variables.

   :param clear_os: Whether to also clear from os.environ (default: False)
   :type clear_os: bool
   :returns: Self for method chaining
   :rtype: DotEnv

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')

      # Clear internal storage only
      env.clear()

      # Clear both internal storage and os.environ
      env.clear(clear_os=True)

show()
~~~~~~

.. method:: DotEnv.show()

   Display all environment variables.

   :returns: Dictionary of all variables (also prints to console)
   :rtype: dict

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      env.show()

Magic Methods
-------------

__getitem__
~~~~~~~~~~~

.. method:: DotEnv.__getitem__(key)

   Dictionary-style access for getting values.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      value = env['DATABASE_URL']

__setitem__
~~~~~~~~~~~

.. method:: DotEnv.__setitem__(key, value)

   Dictionary-style access for setting values.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      env['NEW_KEY'] = 'value'

__contains__
~~~~~~~~~~~~

.. method:: DotEnv.__contains__(key)

   Check if a key exists using ``in`` operator.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      if 'API_KEY' in env:
          print("API key is configured")

__getattr__
~~~~~~~~~~~

.. method:: DotEnv.__getattr__(key)

   Attribute-style access for getting values.

   **Example:**

   .. code-block:: python

      config = DotEnv('.env')
      debug = config.DEBUG
      port = config.PORT

__setattr__
~~~~~~~~~~~

.. method:: DotEnv.__setattr__(key, value)

   Attribute-style access for setting values.

   **Example:**

   .. code-block:: python

      config = DotEnv('.env')
      config.DEBUG = True
      config.PORT = 9000

__repr__
~~~~~~~~

.. method:: DotEnv.__repr__()

   String representation of the DotEnv instance.

   **Example:**

   .. code-block:: python

      env = DotEnv('.env')
      print(env)  # DotEnv(filepath=.env, vars=18)