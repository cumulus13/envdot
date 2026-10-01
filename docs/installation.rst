============
Installation
============

Requirements
------------

envdot requires Python 3.7 or later. Core functionality (``.env``, ``.json``, ``.ini``)
works with no required third-party dependencies.

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Package
     - Needed for
     - Notes
   * - ``PyYAML`` (>=6.0.1)
     - ``.yaml`` / ``.yml`` files
     - Install with ``envdot[yaml]``
   * - ``tomli`` (>=2.0.1)
     - Reading ``.toml`` files
     - Only needed on Python < 3.11 (3.11+ has ``tomllib`` built in)
   * - ``tomli-w`` (>=1.0.0)
     - Writing/saving ``.toml`` files
     - Install with ``envdot[toml]``
   * - ``json5`` (>=0.9.14)
     - Lenient parsing of ``cast_type=dict`` JSON-like values
     - Falls back gracefully if not installed
   * - ``richcolorlog``
     - Rich, colorized internal debug logging
     - Falls back to a plain logger if not installed
   * - ``pathlib3``
     - File content hashing used by auto-reload
     - Required — provides ``Path.hash()``

Installing from PyPI
---------------------

The recommended way to install envdot is via pip:

.. code-block:: bash

   pip install envdot

Installing with Extras
------------------------

YAML Support
~~~~~~~~~~~~

To include YAML file support, install with the ``yaml`` extra:

.. code-block:: bash

   pip install envdot[yaml]

TOML Support
~~~~~~~~~~~~

.. code-block:: bash

   pip install envdot[toml]

All Extras
~~~~~~~~~~

To install every optional dependency at once:

.. code-block:: bash

   pip install envdot[full]

Installing from Source
------------------------

You can also install envdot directly from the GitHub repository:

.. code-block:: bash

   pip install git+https://github.com/cumulus13/envdot.git

Or clone the repository and install locally:

.. code-block:: bash

   git clone https://github.com/cumulus13/envdot.git
   cd envdot
   pip install -e .

Development Installation
--------------------------

For development purposes, you can install with additional development dependencies:

.. code-block:: bash

   git clone https://github.com/cumulus13/envdot.git
   cd envdot
   pip install -e ".[full]"
   pip install pytest pytest-cov black flake8 mypy

This installs every optional format dependency plus:

* ``pytest`` / ``pytest-cov`` for testing
* ``black`` for code formatting
* ``flake8`` for linting
* ``mypy`` for type checking

Verifying Installation
------------------------

After installation, verify that envdot is installed correctly:

.. code-block:: python

   >>> import envdot
   >>> print(envdot.__version__)
   1.0.44

Or from the command line:

.. code-block:: bash

   python -c "import envdot; print(envdot.__version__)"

Upgrading
---------

.. code-block:: bash

   pip install --upgrade envdot

Uninstalling
------------

.. code-block:: bash

   pip uninstall envdot

Compatibility
-------------

envdot is tested and compatible with:

* Python 3.7 – 3.12

It works on Linux, macOS, and Windows. Persistent, cross-process environment
watching (:doc:`usage/system-env-watch`) currently supports Windows (registry)
and Linux (``/etc/environment`` and ``~/.config/environment.d/``); it is a
safe no-op on macOS and any other unsupported platform.
