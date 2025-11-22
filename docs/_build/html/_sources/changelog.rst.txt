=========
Changelog
=========

All notable changes to envdot are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_, 
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

[1.0.14] - 2025
---------------

Current Release
~~~~~~~~~~~~~~~

**Features**

- Multiple file format support (.env, .json, .yaml, .yml, .ini)
- Automatic type detection for boolean, integer, float, and string values
- Method chaining for fluent API
- Dictionary-style and attribute-style access
- Seamless integration with ``os.environ``
- Type-specific helper functions (``getenv_int``, ``getenv_bool``, etc.)
- OS module patching capability
- File format conversion (e.g., .env to .json)
- Comprehensive error handling with custom exceptions

**Supported Python Versions**

- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

[1.0.0] - Initial Release
-------------------------

**Added**

- Initial release of envdot
- ``DotEnv`` class for environment variable management
- Support for ``.env`` file format
- Basic type detection (bool, int, float, str)
- Convenience functions (``load_env``, ``get_env``, ``set_env``, ``save_env``)
- Integration with ``os.environ``

Roadmap
-------

Planned Features
~~~~~~~~~~~~~~~~

- TOML file support
- Environment variable encryption
- Variable interpolation (e.g., ``${OTHER_VAR}``)
- Schema validation
- CLI tool for managing environment files
- Async file loading support

Contributing
~~~~~~~~~~~~

If you'd like to help implement any of these features, please see the 
:doc:`contributing` guide.

Versioning
----------

envdot follows `Semantic Versioning <https://semver.org/>`_:

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Deprecation Policy
------------------

- Deprecated features are marked with warnings for at least one minor version
- Deprecated features are removed in the next major version
- Migration guides are provided for breaking changes