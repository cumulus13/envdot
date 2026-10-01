============
File Formats
============

envdot supports multiple configuration file formats, making it easy to work with
different project setups and migrate between formats.

Supported Formats
------------------

* ``.env`` - Traditional environment file format
* ``.json`` - JSON configuration files
* ``.yaml`` / ``.yml`` - YAML configuration files (requires ``PyYAML``)
* ``.ini`` - INI configuration files
* ``.toml`` - TOML configuration files (requires ``tomli``/``tomllib`` to read,
  ``tomli-w`` to write)

.env Format
-----------

The standard format for environment variables:

.. code-block:: bash

   # .env file
   DEBUG=true
   PORT=8080
   DATABASE_URL=postgresql://localhost/mydb
   SECRET_KEY=my-secret-key-here

   # Comments are supported
   APP_NAME=MyApplication

   # Quoted values
   MESSAGE="Hello, World!"

Loading .env files:

.. code-block:: python

   from envdot import DotEnv

   env = DotEnv('.env')
   env.load()

JSON Format
-----------

JSON configuration with native type support:

.. code-block:: json

   {
     "DEBUG": true,
     "PORT": 8080,
     "DATABASE_URL": "postgresql://localhost/mydb",
     "FEATURES": {
       "API": true,
       "WEBHOOKS": false
     }
   }

Loading JSON files:

.. code-block:: python

   env = DotEnv('config.json')
   env.load()

.. note::

   Nested structures are automatically flattened:

   * ``FEATURES.API`` becomes ``FEATURES_API``
   * ``DATABASE.HOST`` becomes ``DATABASE_HOST``

YAML Format
-----------

YAML configuration with clean syntax:

.. code-block:: yaml

   # config.yaml
   DEBUG: true
   PORT: 8080
   DATABASE_URL: postgresql://localhost/mydb

   # Nested configuration
   database:
     host: localhost
     port: 5432
     name: myapp

   # Lists
   allowed_hosts:
     - localhost
     - 127.0.0.1

.. warning::

   YAML support requires PyYAML:

   .. code-block:: bash

      pip install envdot[yaml]

Loading YAML files:

.. code-block:: python

   env = DotEnv('config.yaml')
   env.load()

INI Format
----------

Traditional INI configuration:

.. code-block:: ini

   [DEFAULT]
   DEBUG = true
   PORT = 8080
   DATABASE_URL = postgresql://localhost/mydb

   [database]
   host = localhost
   port = 5432
   name = myapp

   [features]
   api = true
   webhooks = false

Loading INI files:

.. code-block:: python

   env = DotEnv('config.ini')
   env.load()

.. note::

   INI sections are prefixed onto key names:

   * ``[database]`` section with ``host`` key becomes ``DATABASE_HOST``

   An empty value (``name =``) parses as an empty string, which
   auto-detects to ``None`` — this is expected and matches how an empty
   ``.env`` assignment (``NAME=``) behaves.

TOML Format
-----------

.. code-block:: toml

   # config.toml
   DEBUG = true
   PORT = 8080
   DATABASE_URL = "postgresql://localhost/mydb"

   [database]
   host = "localhost"
   port = 5432

   [[servers]]
   name = "alpha"
   ip = "10.0.0.1"

.. warning::

   Reading ``.toml`` uses the standard-library ``tomllib`` on Python 3.11+,
   or the ``tomli`` package on older versions. Writing/saving ``.toml``
   (via ``env.save('config.toml')``) requires ``tomli-w``:

   .. code-block:: bash

      pip install envdot[toml]

.. code-block:: python

   env = DotEnv('config.toml')
   env.load()

.. note::

   Nested tables flatten the same way JSON/YAML do
   (``[database]`` + ``host`` -> ``DATABASE_HOST``), and arrays of tables
   (``[[servers]]``) flatten with an index, e.g. ``SERVERS_0_NAME``.

Auto-Detection
--------------

envdot automatically detects the file format from the extension:

.. code-block:: python

   # These are automatically handled based on extension
   env1 = DotEnv('.env')           # .env format
   env2 = DotEnv('config.json')    # JSON format
   env3 = DotEnv('config.yaml')    # YAML format
   env4 = DotEnv('settings.ini')   # INI format
   env5 = DotEnv('settings.toml')  # TOML format

Converting Between Formats
------------------------------

Easily convert from one format to another:

.. code-block:: python

   from envdot import DotEnv

   # Load from .env
   env = DotEnv('.env')
   env.load()

   # Save to different formats
   env.save('config.json')    # Export to JSON
   env.save('config.yaml')    # Export to YAML
   env.save('config.ini')     # Export to INI
   env.save('config.toml')    # Export to TOML

Format Comparison
------------------

.. list-table:: Format Feature Comparison
   :header-rows: 1
   :widths: 20 16 16 16 16 16

   * - Feature
     - .env
     - JSON
     - YAML
     - INI
     - TOML
   * - Native types
     - ✗
     - ✓
     - ✓
     - ✗
     - ✓
   * - Comments
     - ✓
     - ✗
     - ✓
     - ✓
     - ✓
   * - Nested structures
     - ✗
     - ✓
     - ✓
     - ✓ (sections)
     - ✓ (tables)
   * - Dependencies
     - None
     - None
     - PyYAML
     - None
     - tomli / tomli-w
   * - Human readable
     - ✓✓
     - ✓
     - ✓✓
     - ✓
     - ✓✓

Nested Structure Handling
------------------------------

**Original JSON:**

.. code-block:: json

   {
     "database": {
       "host": "localhost",
       "port": 5432,
       "credentials": {
         "username": "admin",
         "password": "secret"
       }
     }
   }

**Flattened result:**

.. code-block:: python

   {
       'DATABASE_HOST': 'localhost',
       'DATABASE_PORT': 5432,
       'DATABASE_CREDENTIALS_USERNAME': 'admin',
       'DATABASE_CREDENTIALS_PASSWORD': 'secret'
   }

List Handling
-------------

Lists are converted to indexed keys:

**Original:**

.. code-block:: yaml

   allowed_hosts:
     - localhost
     - 127.0.0.1
     - example.com

**Flattened result:**

.. code-block:: python

   {
       'ALLOWED_HOSTS_0': 'localhost',
       'ALLOWED_HOSTS_1': '127.0.0.1',
       'ALLOWED_HOSTS_2': 'example.com'
   }

Best Practices
--------------

1. **For simplicity**: use ``.env`` files for straightforward key-value pairs
2. **For complex configuration**: use JSON, YAML, or TOML for nested structures
3. **For legacy integration**: use INI
4. **For self-documenting configs**: use YAML or TOML with comments
5. **Keep sensitive data out of version control**: add your config files to ``.gitignore``
