==============
Type Detection
==============

One of envdot's key features is automatic type detection. Instead of returning 
everything as strings like ``os.getenv()``, envdot intelligently converts values 
to their appropriate Python types.

How It Works
------------

When loading environment variables, envdot analyzes each value and converts it 
to the most appropriate Python type:

.. code-block:: python

   from envdot import DotEnv

   # Given this .env file:
   # DEBUG=true
   # PORT=8080
   # TIMEOUT=30.5
   # APP_NAME=MyApp
   # EMPTY_VALUE=

   env = DotEnv('.env')

   env.get('DEBUG')       # Returns: True (bool)
   env.get('PORT')        # Returns: 8080 (int)
   env.get('TIMEOUT')     # Returns: 30.5 (float)
   env.get('APP_NAME')    # Returns: 'MyApp' (str)
   env.get('EMPTY_VALUE') # Returns: None

Type Detection Rules
--------------------

envdot uses the following rules for automatic type detection:

Boolean Values
~~~~~~~~~~~~~~

The following strings are converted to ``True``:

* ``true`` (case-insensitive)
* ``yes`` (case-insensitive)
* ``on`` (case-insensitive)
* ``1``

The following strings are converted to ``False``:

* ``false`` (case-insensitive)
* ``no`` (case-insensitive)
* ``off`` (case-insensitive)
* ``0``

.. code-block:: python

   # All of these become True
   DEBUG=true
   DEBUG=True
   DEBUG=TRUE
   DEBUG=yes
   DEBUG=on
   DEBUG=1

   # All of these become False
   DEBUG=false
   DEBUG=False
   DEBUG=no
   DEBUG=off
   DEBUG=0

None Values
~~~~~~~~~~~

The following are converted to ``None``:

* ``none`` (case-insensitive)
* ``null`` (case-insensitive)
* Empty string

.. code-block:: python

   EMPTY_VAR=
   NULL_VAR=null
   NONE_VAR=none

Integer Values
~~~~~~~~~~~~~~

Strings containing only digits (with optional leading minus sign) are converted 
to integers:

.. code-block:: python

   PORT=8080        # 8080 (int)
   MAX_CONN=100     # 100 (int)
   OFFSET=-10       # -10 (int)
   ZERO=0           # Note: "0" becomes False (bool), not 0 (int)

Float Values
~~~~~~~~~~~~

Strings containing digits with a decimal point are converted to floats:

.. code-block:: python

   TIMEOUT=30.5     # 30.5 (float)
   RATE=0.15        # 0.15 (float)
   TEMP=-3.14       # -3.14 (float)

String Values
~~~~~~~~~~~~~

Everything that doesn't match the above patterns remains as a string:

.. code-block:: python

   APP_NAME=MyApp              # 'MyApp' (str)
   URL=https://example.com     # 'https://example.com' (str)
   VERSION=1.0.0               # '1.0.0' (str) - not a valid float
   MIXED=abc123                # 'abc123' (str)

Explicit Type Casting
---------------------

You can override automatic detection with explicit type casting:

.. code-block:: python

   env = DotEnv('.env')

   # Force string type (even for numbers)
   version = env.get('PORT', cast_type=str)  # '8080' (str)

   # Force integer type
   count = env.get('COUNT', cast_type=int)

   # Force boolean type
   enabled = env.get('ENABLED', cast_type=bool)

   # Force float type
   rate = env.get('RATE', cast_type=float)


List Values
~~~~~~~~~~~~~

Anything that matches the above pattern will remain a string unless a specific `cast_type` is specified:

.. code-block:: python

   ALLOWED_HOST=*,127.0.0.1 192.168.10.2,example.com  # (str)
   # example:
   os.getenv('ALLOWED_HOST', cast_type=list)
   # [*,127.0.0.1,192.168.10.2,example.com]  # (list)

Tuple Values
~~~~~~~~~~~~~

Anything that matches the above pattern will remain a string unless a specific `cast_type` is specified:

.. code-block:: python

   ALLOWED_HOST=*,127.0.0.1 192.168.10.2,example.com  # (str)
   # example:
   os.getenv('ALLOWED_HOST', cast_type=tuple)
   # (*,127.0.0.1,192.168.10.2,example.com)  # (tuple)
   
Type Conversion Errors
~~~~~~~~~~~~~~~~~~~~~~

If explicit casting fails, a ``TypeConversionError`` is raised:

.. code-block:: python

   from envdot import DotEnv
   from envdot.exceptions import TypeConversionError

   env = DotEnv('.env')
   # APP_NAME=MyApplication

   try:
       value = env.get('APP_NAME', cast_type=int)
   except TypeConversionError as e:
       print(f"Cannot convert: {e}")

Using Helper Functions
----------------------

envdot provides type-specific helper functions:

.. code-block:: python

   from envdot import (
       getenv_typed,
       getenv_int,
       getenv_bool,
       getenv_float,
       getenv_str
   )

   # Auto-detect type
   port = getenv_typed('PORT')  # Returns appropriate type

   # Specific type getters
   port = getenv_int('PORT', default=8000)
   debug = getenv_bool('DEBUG', default=False)
   timeout = getenv_float('TIMEOUT', default=30.0)
   name = getenv_str('APP_NAME', default='MyApp')

Comparison with os.getenv
-------------------------

Standard ``os.getenv()`` always returns strings:

.. code-block:: python

   import os

   os.environ['PORT'] = '8080'
   os.environ['DEBUG'] = 'true'

   # Standard behavior - always strings
   port = os.getenv('PORT')     # '8080' (str)
   debug = os.getenv('DEBUG')   # 'true' (str)

   # Manual conversion needed
   port = int(os.getenv('PORT'))
   debug = os.getenv('DEBUG').lower() == 'true'

With envdot, this becomes much cleaner:

.. code-block:: python

   from envdot import load_env, get_env

   load_env()

   # Automatic type detection
   port = get_env('PORT')   # 8080 (int)
   debug = get_env('DEBUG') # True (bool)

Patching os Module
------------------

For seamless integration, you can patch the ``os`` module:

.. code-block:: python

   from envdot import patch_os_module

   patch_os_module()

   import os

   # Now os has typed getters
   port = os.getenv_typed('PORT')
   debug = os.getenv_bool('DEBUG')
   timeout = os.getenv_float('TIMEOUT')

   # Set with type preservation
   os.setenv_typed('NEW_PORT', 9000)

TypeDetector Class
------------------

For advanced use cases, you can use the ``TypeDetector`` class directly:

.. code-block:: python

   from envdot.core import TypeDetector

   # Detect and convert value
   value = TypeDetector.auto_detect('true')    # True (bool)
   value = TypeDetector.auto_detect('8080')    # 8080 (int)
   value = TypeDetector.auto_detect('30.5')    # 30.5 (float)

   # Convert back to string
   string = TypeDetector.to_string(True)       # 'true'
   string = TypeDetector.to_string(8080)       # '8080'
   string = TypeDetector.to_string(30.5)       # '30.5'
   string = TypeDetector.to_string(None)       # ''

Best Practices
--------------

1. **Use meaningful boolean values**: Prefer ``true``/``false`` over ``1``/``0``
2. **Be explicit when needed**: Use ``cast_type`` for ambiguous values
3. **Handle None carefully**: Empty values become ``None``, not empty strings
4. **Version numbers**: Keep as strings (``VERSION=1.0.0``) to avoid float issues
5. **Test type detection**: Verify your values are detected as expected