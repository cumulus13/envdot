============
File Formats
============

envdot supports multiple configuration file formats, making it easy to work with 
different project setups and migrate between formats.

Supported Formats
-----------------

* ``.env`` - Traditional environment file format
* ``.json`` - JSON configuration files
* ``.yaml`` / ``.yml`` - YAML configuration files (requires PyYAML)
* ``.ini`` - INI configuration files

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

   Nested JSON structures are automatically flattened:

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

   YAML support requires PyYAML. Install with:

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

   INI sections are prefixed to key names:

   * ``[database]`` section with ``host`` key becomes ``DATABASE_HOST``

Auto-Detection
--------------

envdot automatically detects the file format based on the extension:

.. code-block:: python

   # These are automatically handled based on extension
   env1 = DotEnv('.env')           # .env format
   env2 = DotEnv('config.json')    # JSON format
   env3 = DotEnv('config.yaml')    # YAML format
   env4 = DotEnv('settings.ini')   # INI format

Converting Between Formats
--------------------------

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

Format Comparison
-----------------

.. list-table:: Format Feature Comparison
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Feature
     - .env
     - JSON
     - YAML
     - INI
   * - Native types
     - ✗
     - ✓
     - ✓
     - ✗
   * - Comments
     - ✓
     - ✗
     - ✓
     - ✓
   * - Nested structures
     - ✗
     - ✓
     - ✓
     - ✓ (sections)
   * - Dependencies
     - None
     - None
     - PyYAML
     - None
   * - Human readable
     - ✓✓
     - ✓
     - ✓✓
     - ✓

Nested Structure Handling
-------------------------

When loading nested structures from JSON, YAML, or INI, envdot flattens them:

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

1. **For simplicity**: Use ``.env`` files for straightforward key-value pairs
2. **For complex configuration**: Use JSON or YAML for nested structures
3. **For compatibility**: Use INI for legacy system integration
4. **For documentation**: Use YAML with comments for self-documenting configs
5. **Keep sensitive data out of version control**: Add your config files to ``.gitignore``