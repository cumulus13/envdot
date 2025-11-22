================
Helper Functions
================

envdot provides type-specific helper functions that serve as enhanced 
replacements for ``os.getenv()``. These functions ensure you get properly 
typed values from environment variables.

.. module:: envdot
   :synopsis: Type-specific helper functions

Typed Getters
-------------

getenv_typed()
~~~~~~~~~~~~~~

.. function:: getenv_typed(key, default=None)

   Get an environment variable with automatic type detection.

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist
   :type default: Any
   :returns: Value with automatically detected type
   :rtype: bool, int, float, str, or None

   **Example:**

   .. code-block:: python

      from envdot import getenv_typed

      # Auto-detects types
      debug = getenv_typed('DEBUG')      # True (bool)
      port = getenv_typed('PORT')        # 8080 (int)
      timeout = getenv_typed('TIMEOUT')  # 30.5 (float)
      name = getenv_typed('APP_NAME')    # 'MyApp' (str)

getenv_int()
~~~~~~~~~~~~

.. function:: getenv_int(key, default=None)

   Get an environment variable as an integer.

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist (default: None)
   :type default: int or None
   :returns: Integer value
   :rtype: int or None
   :raises ValueError: If value cannot be converted to int

   **Example:**

   .. code-block:: python

      from envdot import getenv_int

      port = getenv_int('PORT', default=8000)
      workers = getenv_int('MAX_WORKERS', default=4)
      retries = getenv_int('MAX_RETRIES', default=3)

getenv_bool()
~~~~~~~~~~~~~

.. function:: getenv_bool(key, default=None)

   Get an environment variable as a boolean.

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist (default: None)
   :type default: bool or None
   :returns: Boolean value
   :rtype: bool or None

   Recognized true values: ``true``, ``yes``, ``on``, ``1``
   Recognized false values: ``false``, ``no``, ``off``, ``0``

   **Example:**

   .. code-block:: python

      from envdot import getenv_bool

      debug = getenv_bool('DEBUG', default=False)
      ssl_enabled = getenv_bool('SSL_ENABLED', default=True)
      verbose = getenv_bool('VERBOSE', default=False)

getenv_float()
~~~~~~~~~~~~~~

.. function:: getenv_float(key, default=None)

   Get an environment variable as a float.

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist (default: None)
   :type default: float or None
   :returns: Float value
   :rtype: float or None
   :raises ValueError: If value cannot be converted to float

   **Example:**

   .. code-block:: python

      from envdot import getenv_float

      timeout = getenv_float('TIMEOUT', default=30.0)
      rate_limit = getenv_float('RATE_LIMIT', default=1.5)
      threshold = getenv_float('THRESHOLD', default=0.75)

getenv_str()
~~~~~~~~~~~~

.. function:: getenv_str(key, default=None)

   Get an environment variable as a string (no type conversion).

   :param key: The variable name
   :type key: str
   :param default: Default value if key doesn't exist (default: None)
   :type default: str or None
   :returns: String value
   :rtype: str or None

   **Example:**

   .. code-block:: python

      from envdot import getenv_str

      app_name = getenv_str('APP_NAME', default='MyApp')
      api_key = getenv_str('API_KEY', default='')
      version = getenv_str('VERSION', default='1.0.0')

Typed Setter
------------

setenv_typed()
~~~~~~~~~~~~~~

.. function:: setenv_typed(key, value)

   Set an environment variable with proper type handling.

   :param key: The variable name
   :type key: str
   :param value: The value to set (any type)
   :type value: Any
   :returns: None

   **Example:**

   .. code-block:: python

      from envdot import setenv_typed

      setenv_typed('DEBUG', True)
      setenv_typed('PORT', 8080)
      setenv_typed('TIMEOUT', 30.5)
      setenv_typed('APP_NAME', 'MyApp')

OS Module Patching
------------------

patch_os_module()
~~~~~~~~~~~~~~~~~

.. function:: patch_os_module()

   Patch the ``os`` module to add typed environment variable methods.

   After calling this function, the ``os`` module will have the following 
   additional methods:

   - ``os.getenv_typed()``
   - ``os.getenv_int()``
   - ``os.getenv_bool()``
   - ``os.getenv_float()``
   - ``os.getenv_str()``
   - ``os.setenv_typed()``

   **Example:**

   .. code-block:: python

      from envdot import patch_os_module
      import os

      # Patch the os module
      patch_os_module()

      # Now os has typed methods
      debug = os.getenv_bool('DEBUG', default=False)
      port = os.getenv_int('PORT', default=8000)
      timeout = os.getenv_float('TIMEOUT', default=30.0)

      # Set typed values
      os.setenv_typed('NEW_PORT', 9000)
      os.setenv_typed('FEATURE_ENABLED', True)

Comparison: Standard vs Typed
-----------------------------

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

   port = getenv_int('PORT', default=8000)   # 8080 (int)
   debug = getenv_bool('DEBUG', default=False) # True (bool)

   # No manual conversion needed!

Complete Example
----------------

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