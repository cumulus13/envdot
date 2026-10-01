==============
Type Detection
==============

One of envdot's key features is automatic type detection. Instead of returning
everything as strings like ``os.getenv()``, envdot intelligently converts values
to their appropriate Python types.

How It Works
------------

When loading environment variables, envdot analyzes each value and converts it 
to the most appropriate Python type unless `cast_type` given:

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

Automatic detection (i.e. what you get from ``.get(key)`` with no
``cast_type``) only ever produces ``bool``, ``None``, ``int``, ``float``, or
``str``.

Boolean Values
~~~~~~~~~~~~~~

The following strings convert to ``True`` / ``False`` (case-insensitive):

* ``true`` / ``false``
* ``yes`` / ``no``
* ``on`` / ``off``

.. code-block:: python

   # All of these become True
   DEBUG=true
   DEBUG=True
   DEBUG=TRUE
   DEBUG=yes
   DEBUG=on

   # All of these become False
   DEBUG=false
   DEBUG=False
   DEBUG=no
   DEBUG=off

.. important::

   ``1`` and ``0`` are **not** in this list. They auto-detect as the
   integers ``1`` and ``0`` — not booleans — since a bare ``1``/``0`` is
   genuinely ambiguous (a count? a flag?) and treating every ``1``/``0``
   env var as boolean silently turns something like ``RETRY_COUNT=1``
   into ``True``, which is rarely what's wanted. If you specifically want
   a boolean from ``1``/``0``, use ``cast_type=bool`` explicitly — it
   accepts ``1``/``0`` in addition to the words above.

   .. code-block:: python

      env.get('RETRY_COUNT')                  # 1   (int)
      env.get('RETRY_COUNT', cast_type=bool)  # True (bool), forced

None Values
~~~~~~~~~~~

The following convert to ``None``:

* ``none`` (case-insensitive)
* ``null`` (case-insensitive)
* Empty string

.. code-block:: python

   EMPTY_VAR=
   NULL_VAR=null
   NONE_VAR=none

Integer Values
~~~~~~~~~~~~~~

A string that is only optional-sign + digits converts to ``int``:

.. code-block:: python

   PORT=8080        # 8080 (int)
   MAX_CONN=100     # 100 (int)
   OFFSET=-10       # -10 (int)
   ZERO=0           # 0 (int) - NOT False; see the Boolean note above, Note: "0" becomes False (bool), not 0 (int)

Float Values
~~~~~~~~~~~~

A string with digits and a decimal point (or exponent) converts to ``float``:

.. code-block:: python

   TIMEOUT=30.5     # 30.5 (float)
   RATE=0.15        # 0.15 (float)
   TEMP=-3.14       # -3.14 (float)
   SCI=1e10         # 10000000000.0 (float)

String Values
~~~~~~~~~~~~~

Everything else remains a string — **including** a value that contains a
space or a comma:

.. code-block:: python

   APP_NAME=MyApp                        # 'MyApp' (str)
   URL=https://example.com               # 'https://example.com' (str)
   VERSION=1.0.0                         # '1.0.0' (str) - not a valid float
   MIXED=abc123                          # 'abc123' (str)
   APP_NAME=My Application               # 'My Application' (str) - kept intact
   ALLOWED_HOSTS=localhost, 127.0.0.1    # 'localhost, 127.0.0.1' (str) - kept intact

.. warning::

   A value is **never** auto-split into a list/tuple just because it
   contains spaces or commas. Ask for ``cast_type=list``/``tuple``
   explicitly (see below) if that's what you want. Earlier envdot
   versions (before 1.0.37) did this automatically, which silently
   corrupted plain strings such as ``APP_NAME=My Application`` into
   ``('My', 'Application')`` — that behavior was removed as a bug fix.

Explicit Type Casting
----------------------

``cast_type`` always casts from the **original, untouched string** value —
never from a value auto-detection already converted. This keeps casting
predictable even in ambiguous cases:

.. code-block:: python

   env = DotEnv('.env')

   version = env.get('PORT', cast_type=str)     # '8080' (str)
   count = env.get('COUNT', cast_type=int)       # int
   enabled = env.get('RETRY_COUNT', cast_type=bool)  # True, forced from '1'
   rate = env.get('RATE', cast_type=float)       # float

List and Tuple Values
~~~~~~~~~~~~~~~~~~~~~~~

Cast a string to ``list`` or ``tuple`` explicitly:

* If the raw value looks like a Python literal (``[...]`` or ``(...)``),
  it's parsed as one.
* Otherwise, it's split on commas and/or whitespace.

.. code-block:: python

   # ALLOWED_HOSTS=localhost, 127.0.0.1, example.com
   env.get('ALLOWED_HOSTS', cast_type=list)
   # -> ['localhost', '127.0.0.1', 'example.com']

   env.get('ALLOWED_HOSTS', cast_type=tuple)
   # -> ('localhost', '127.0.0.1', 'example.com')

   # NUMBERS=[1, 2, 3]
   env.get('NUMBERS', cast_type=list)
   # -> [1, 2, 3]   (parsed as a literal, not split character-by-character)

Dict Values
~~~~~~~~~~~~

Cast a string to ``dict``:

* A ``{...}``-shaped value is parsed as JSON (falling back to
  ``ast.literal_eval``, and then ``json5`` if installed, for lenient
  JSON-like input).
* Otherwise, whitespace/comma-separated ``key:value`` pairs are parsed.

.. code-block:: python

   # SETTINGS_MAP=a:1 b:2 c:3
   env.get('SETTINGS_MAP', cast_type=dict)
   # -> {'a': '1', 'b': '2', 'c': '3'}

   # JSON_LIKE={"x": 1, "y": 2}
   env.get('JSON_LIKE', cast_type=dict)
   # -> {'x': 1, 'y': 2}

Type Conversion Errors
~~~~~~~~~~~~~~~~~~~~~~~~

If explicit casting fails, ``TypeConversionError`` is raised:

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
------------------------

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
----------------------------

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

Patching the os Module
------------------------

For seamless integration, you can patch the ``os`` module:

.. code-block:: python

   from envdot import patch_os_module

   patch_os_module()

   import os

   port = os.getenv_typed('PORT')
   debug = os.getenv_bool('DEBUG')
   timeout = os.getenv_float('TIMEOUT')

   # Set with type preservation
   os.setenv_typed('NEW_PORT', 9000)

TypeDetector Class
--------------------

For advanced use cases, use ``TypeDetector`` directly:

.. code-block:: python

   from envdot.core import TypeDetector

   # Automatic detection (bool/None/int/float/str only)
   value = TypeDetector.auto_detect('true')    # True (bool)
   value = TypeDetector.auto_detect('8080')    # 8080 (int)
   value = TypeDetector.auto_detect('30.5')    # 30.5 (float)
   value = TypeDetector.auto_detect('My App')  # 'My App' (str, unchanged)

   # Convert back to string, for writing to a file / os.environ
   string = TypeDetector.to_string(True)       # 'true'
   string = TypeDetector.to_string(8080)       # '8080'
   string = TypeDetector.to_string(30.5)       # '30.5'
   string = TypeDetector.to_string(None)       # ''

   # Explicit cast from a raw string - what cast_type uses internally
   TypeDetector.cast('localhost, 127.0.0.1', list)
   # -> ['localhost', '127.0.0.1']
   TypeDetector.cast('a:1 b:2', dict)
   # -> {'a': '1', 'b': '2'}

Best Practices
---------------

1. **Use meaningful boolean values**: prefer ``true``/``false`` over ``1``/``0``,
   since ``1``/``0`` auto-detect as ``int``, not ``bool``
2. **Be explicit when needed**: use ``cast_type`` for ambiguous values
3. **Handle None carefully**: empty values become ``None``, not empty strings
4. **Version numbers**: keep as strings (``VERSION=1.0.0``) to avoid float issues
5. **Test type detection**: verify your values are detected as expected
