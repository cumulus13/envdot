.. envdot documentation master file

===============================================
envdot - Enhanced Environment Variable Manager
===============================================

.. image:: https://img.shields.io/pypi/v/envdot.svg
   :target: https://pypi.org/project/envdot/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/envdot.svg
   :target: https://pypi.org/project/envdot/
   :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

**envdot** is an enhanced environment variable management library for Python with 
multi-format support and automatic type detection.

Features
--------

🔧 **Multiple Format Support**
   Load configuration from ``.env``, ``.json``, ``.yaml``, ``.yml``, and ``.ini`` files.

🎯 **Automatic Type Detection**
   Automatically converts strings to ``bool``, ``int``, ``float``, or keeps as ``string``. and Support converts strings to ``list``, ``tuple`` by using ``cast_type``.

💾 **Read and Write**
   Load from and save to configuration files seamlessly.

🔄 **Method Chaining**
   Fluent API for cleaner, more readable code.

🌍 **OS Environment Integration**
   Works seamlessly with ``os.environ``.

📦 **Zero Dependencies**
   Core functionality works without external packages (YAML support requires PyYAML).

🌿 **Auto re-load**
   Automatically reload the config file if the hash changes or use `reload=True`

Quick Example
-------------

.. code-block:: python

   from envdot import load_env, get_env, set_env

   # Load environment variables from .env file
   load_env()

   # or load_env('.env')
   # or load_env('.json')
   # or load_env('.yaml')
   # or load_env('.ini')
   # or load_env('config.env')
   # or load_env('/etc/config.env')
   # or load_env(r'c:\.env')
   # or load_env(r'c:\traceback.ini')

   # Get values with automatic type detection
   debug = get_env('DEBUG')       # Returns: True (bool)
   port = get_env('PORT')         # Returns: 8080 (int)
   timeout = get_env('TIMEOUT')   # Returns: 30.5 (float)
   allowed_hosts = os.getenv("*,127.0.0.1 192.168.10.2,example.com", cast_type=list) # Return: [*,127.0.0.1,192.168.10.2,example.com]  # (list)
   allowed_hosts = os.getenv("*,127.0.0.1 192.168.10.2,example.com", cast_type=tuple) # Return: (*,127.0.0.1,192.168.10.2,example.com)  # (tuple)

   # Set new values
   set_env('NEW_FEATURE', True) or os.setenv('NEW_FEATURE', True)

   # Find by keys
   os.find("DB_*") # return dict

Installation
------------

.. code-block:: bash

   # Basic installation
   pip install envdot

   # With YAML support
   pip install envdot[yaml]

   # With all extras
   pip install envdot[all]

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   usage/basic
   usage/file-formats
   usage/type-detection
   usage/advanced

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/dotenv
   api/functions
   api/helpers
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   changelog

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Links
-----

* **PyPI**: https://pypi.org/project/envdot/
* **GitHub**: https://github.com/cumulus13/envdot
* **Issues**: https://github.com/cumulus13/envdot/issues

License
-------

envdot is released under the MIT License. See the `LICENSE <https://github.com/cumulus13/envdot/blob/main/LICENSE>`_ file for details.

Author
------

Created by `Hadi Cahyadi <mailto:cumulus13@gmail.com>`_

Support the Project
-------------------

* `Buy Me a Coffee <https://www.buymeacoffee.com/cumulus13>`_
* `Ko-fi <https://ko-fi.com/cumulus13>`_
* `Patreon <https://www.patreon.com/cumulus13>`_