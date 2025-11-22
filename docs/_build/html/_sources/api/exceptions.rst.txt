==========
Exceptions
==========

envdot defines custom exceptions for clear error handling.

.. module:: envdot.exceptions
   :synopsis: Custom exceptions for envdot

Exception Hierarchy
-------------------

.. code-block:: text

   Exception
   └── EnvDotError (base class)
       ├── FileNotFoundError
       ├── ParseError
       └── TypeConversionError

Base Exception
--------------

EnvDotError
~~~~~~~~~~~

.. class:: EnvDotError

   Base exception class for all envdot errors.

   All envdot exceptions inherit from this class, making it easy to catch 
   any envdot-related error:

   .. code-block:: python

      from envdot import DotEnv
      from envdot.exceptions import EnvDotError

      try:
          env = DotEnv('config.env')
          value = env.get('KEY', cast_type=int)
      except EnvDotError as e:
          print(f"envdot error: {e}")

File Exceptions
---------------

FileNotFoundError
~~~~~~~~~~~~~~~~~

.. class:: FileNotFoundError

   Raised when a specified configuration file does not exist.

   :param filepath: Path to the file that was not found
   :type filepath: str or Path

   **Example:**

   .. code-block:: python

      from envdot import DotEnv
      from envdot.exceptions import FileNotFoundError

      try:
          env = DotEnv('nonexistent.env', auto_load=False)
          env.load()
      except FileNotFoundError as e:
          print(f"Configuration file not found: {e}")
          # Use defaults or create file

   **Attributes:**

   - ``filepath``: The path that was not found

Parsing Exceptions
------------------

ParseError
~~~~~~~~~~

.. class:: ParseError

   Raised when a configuration file cannot be parsed.

   This can occur when:

   - The file format doesn't match the extension
   - The file contains invalid syntax
   - Required dependencies are missing (e.g., PyYAML for .yaml files)

   **Example:**

   .. code-block:: python

      from envdot import DotEnv
      from envdot.exceptions import ParseError

      try:
          env = DotEnv('config.json')
          env.load()
      except ParseError as e:
          print(f"Failed to parse configuration: {e}")

   **Common causes:**

   .. code-block:: python

      # Invalid JSON
      # config.json contains: { invalid json }

      # Invalid YAML syntax
      # config.yaml contains improper indentation

      # Missing YAML dependency
      # Trying to load .yaml without PyYAML installed

Type Exceptions
---------------

TypeConversionError
~~~~~~~~~~~~~~~~~~~

.. class:: TypeConversionError

   Raised when a value cannot be converted to the requested type.

   This occurs when using ``cast_type`` parameter and the conversion fails.

   **Example:**

   .. code-block:: python

      from envdot import DotEnv
      from envdot.exceptions import TypeConversionError

      env = DotEnv('.env')
      # Assuming APP_NAME=MyApplication (a string)

      try:
          value = env.get('APP_NAME', cast_type=int)
      except TypeConversionError as e:
          print(f"Type conversion failed: {e}")
          # Handle the error - maybe use default value

   **Attributes:**

   - ``key``: The variable name
   - ``value``: The original value
   - ``target_type``: The type conversion was attempted to

Error Handling Patterns
-----------------------

Catching Specific Errors
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv
   from envdot.exceptions import (
       FileNotFoundError,
       ParseError,
       TypeConversionError
   )

   def load_config(filepath: str):
       try:
           env = DotEnv(filepath, auto_load=False)
           env.load()
           return env
       except FileNotFoundError:
           print(f"Warning: {filepath} not found, using defaults")
           return DotEnv(auto_load=False)
       except ParseError as e:
           print(f"Error parsing {filepath}: {e}")
           raise

Catching All envdot Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv
   from envdot.exceptions import EnvDotError

   def safe_load_config():
       try:
           env = DotEnv('.env')
           return env
       except EnvDotError as e:
           print(f"Configuration error: {e}")
           # Return empty config or defaults
           return DotEnv(auto_load=False)

Safe Value Retrieval
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv
   from envdot.exceptions import TypeConversionError

   def get_port(env: DotEnv) -> int:
       try:
           return env.get('PORT', cast_type=int)
       except TypeConversionError:
           print("Warning: Invalid PORT value, using default 8000")
           return 8000

   def get_config(env: DotEnv) -> dict:
       return {
           'port': get_port(env),
           'debug': env.get('DEBUG', default=False),
           'name': env.get('APP_NAME', default='App'),
       }

Validation with Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from envdot import DotEnv
   from envdot.exceptions import EnvDotError

   class ConfigurationError(Exception):
       """Application-specific configuration error."""
       pass

   def validate_config(env: DotEnv):
       """Validate required configuration."""
       required = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
       missing = [key for key in required if key not in env]

       if missing:
           raise ConfigurationError(
               f"Missing required configuration: {', '.join(missing)}"
           )

       # Validate value constraints
       port = env.get('PORT', default=8000)
       if not (1 <= port <= 65535):
           raise ConfigurationError(
               f"PORT must be between 1 and 65535, got {port}"
           )

   # Usage
   try:
       env = DotEnv('.env')
       validate_config(env)
   except (EnvDotError, ConfigurationError) as e:
       print(f"Configuration error: {e}")
       exit(1)