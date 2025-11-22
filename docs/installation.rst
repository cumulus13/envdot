============
Installation
============

Requirements
------------

envdot requires Python 3.7 or later. It has no required dependencies for core 
functionality, making it lightweight and easy to install.

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

* **PyYAML** (>=5.1): Required for YAML file support

Installing from PyPI
--------------------

The recommended way to install envdot is via pip:

.. code-block:: bash

   pip install envdot

Installing with Extras
----------------------

YAML Support
~~~~~~~~~~~~

To include YAML file support, install with the ``yaml`` extra:

.. code-block:: bash

   pip install envdot[yaml]

All Extras
~~~~~~~~~~

To install all optional dependencies:

.. code-block:: bash

   pip install envdot[all]

Installing from Source
----------------------

You can also install envdot directly from the GitHub repository:

.. code-block:: bash

   pip install git+https://github.com/cumulus13/envdot.git

Or clone the repository and install locally:

.. code-block:: bash

   git clone https://github.com/cumulus13/envdot.git
   cd envdot
   pip install -e .

Development Installation
------------------------

For development purposes, you can install with additional development dependencies:

.. code-block:: bash

   git clone https://github.com/cumulus13/envdot.git
   cd envdot
   pip install -e ".[dev]"

This installs:

* pytest for testing
* pytest-cov for coverage reporting
* black for code formatting
* flake8 for linting
* mypy for type checking

Verifying Installation
----------------------

After installation, verify that envdot is installed correctly:

.. code-block:: python

   >>> import envdot
   >>> print(envdot.__version__)
   1.0.14

Or from the command line:

.. code-block:: bash

   python -c "import envdot; print(envdot.__version__)"

Upgrading
---------

To upgrade envdot to the latest version:

.. code-block:: bash

   pip install --upgrade envdot

Uninstalling
------------

To remove envdot from your system:

.. code-block:: bash

   pip uninstall envdot

Compatibility
-------------

envdot is tested and compatible with:

* Python 3.7
* Python 3.8
* Python 3.9
* Python 3.10
* Python 3.11
* Python 3.12

It works on all major operating systems:

* Linux
* macOS
* Windows