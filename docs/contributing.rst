============
Contributing
============

Thank you for your interest in contributing to envdot! This guide will help
you get started.

Getting Started
----------------

Fork and Clone
~~~~~~~~~~~~~~~~

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/envdot.git
      cd envdot

3. Add the upstream remote:

   .. code-block:: bash

      git remote add upstream https://github.com/cumulus13/envdot.git

Development Setup
~~~~~~~~~~~~~~~~~~~~

1. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      venv\Scripts\activate     # Windows

2. Install in editable mode with every optional extra, plus dev tools:

   .. code-block:: bash

      pip install -e ".[full]"
      pip install pytest pytest-cov coverage black flake8 mypy

3. Verify the setup by running the test suite:

   .. code-block:: bash

      pytest

      # or, without pytest:
      python test_dotenv.py

Development Workflow
------------------------

Creating a Branch
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name

Making Changes
~~~~~~~~~~~~~~~~

1. Write your code following the coding standards below
2. Add tests for new functionality — prefer real execution over
   theoretical/mocked-out assertions where practical, and add a fixture
   under ``tests/`` for anything format-specific
3. Update documentation as needed (this ``docs/`` tree)
4. Run tests and linting:

   .. code-block:: bash

      # Run tests
      pytest

      # Run tests with coverage
      pytest --cov=envdot

      # Run linting
      flake8 envdot tests

      # Run type checking
      mypy envdot

      # Format code
      black envdot tests

Commit messages
~~~~~~~~~~~~~~~~~~

Write clear commit messages:

.. code-block:: text

   feat: Add support for TOML configuration files

   - Add TOMLParser class for parsing .toml files
   - Update DotEnv to detect and handle .toml extension
   - Add tests for TOML parsing
   - Update documentation

Commit message prefixes:

- ``feat:`` - New feature
- ``fix:`` - Bug fix
- ``docs:`` - Documentation changes
- ``test:`` - Test additions or changes
- ``refactor:`` - Code refactoring
- ``style:`` - Code style changes (formatting, etc.)
- ``chore:`` - Maintenance tasks

Submitting a Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Push your branch to your fork:

   .. code-block:: bash

      git push origin feature/your-feature-name

2. Open a Pull Request on GitHub
3. Fill in the PR template with:

   - Description of changes
   - Related issue (if applicable)
   - Screenshots (if applicable)
   - Checklist of completed items

4. Wait for code review and address feedback

Coding Standards
--------------------

Code Style
~~~~~~~~~~~~

envdot follows PEP 8 with some modifications:

- Line length: 100 characters
- Use type hints where appropriate
- Use docstrings for all public functions and classes

Use black for formatting:

.. code-block:: bash

   black envdot tests --line-length 100

Documentation
~~~~~~~~~~~~~~~

- Use Google-style docstrings (Napoleon-compatible)
- Include type information in docstrings
- Provide examples for non-trivial functions

Example docstring:

.. code-block:: python

   def get(self, key: str, default: Any = None, cast_type: type = None) -> Any:
       """Get an environment variable with automatic type detection.

       Args:
           key: The variable name to retrieve.
           default: Default value if key doesn't exist.
           cast_type: Force conversion to a specific type, always from the
               original raw string rather than an already-detected value.

       Returns:
           The value with detected or cast type.

       Raises:
           envdot.exceptions.TypeConversionError: If cast_type is given and
               conversion fails.

       Example:
           >>> env = DotEnv('.env')
           >>> debug = env.get('DEBUG')  # Returns bool
           >>> port = env.get('PORT', default=8000)  # Returns int
       """

Testing
-------

Writing Tests
~~~~~~~~~~~~~~~~

- Place tests in ``tests/`` (or alongside ``test_dotenv.py`` at the repo root)
- Name test files ``test_*.py``
- Name test functions ``test_*``
- Use pytest fixtures for common setup, and ``tmp_path`` for anything
  touching the filesystem so tests don't pollute the real working directory

Example test:

.. code-block:: python

   import pytest
   from envdot import DotEnv

   @pytest.fixture
   def env_file(tmp_path):
       """Create a temporary .env file."""
       env_file = tmp_path / '.env'
       env_file.write_text('DEBUG=true\nPORT=8080')
       return env_file

   def test_load_env_file(env_file):
       """Test loading .env file."""
       env = DotEnv(env_file)

       assert env.get('DEBUG') is True
       assert env.get('PORT') == 8080

   def test_type_detection():
       """Test automatic type detection."""
       env = DotEnv(auto_load=False)
       env.set('BOOL_VAL', 'true')
       env.set('INT_VAL', '123')

       assert isinstance(env.get('BOOL_VAL'), bool)
       assert isinstance(env.get('INT_VAL'), int)

.. tip::

   A stray config file left over in the current working directory from an
   earlier test can affect auto-discovery in a later one. If your test
   doesn't pass an explicit ``filepath``, run it from (or ``chdir`` into)
   an isolated ``tmp_path``, or pass an explicit nonexistent-by-design
   path with ``auto_load=False``.

Running Tests
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run with verbose output
   pytest -v
   pytest tests/test_all_formats.py
   pytest tests/test_all_formats.py::TestDotEnvFormat::test_load_env_file
   pytest --cov=envdot --cov-report=html

   # or, without pytest:
   python test_dotenv.py

Reporting Issues
--------------------

Bug Reports
~~~~~~~~~~~~~~

Include:

- Python version, envdot version, operating system
- Steps to reproduce, ideally a minimal ``.env``/config file plus the code
- Expected vs actual behavior
- Whether the config file changed on disk during the session, and any
  relevant environment variables that were also set (sanitized)

Feature Requests
~~~~~~~~~~~~~~~~~~~

Include:

- Use case description
- Proposed solution
- Alternative solutions considered
- Any relevant examples

Code of Conduct
--------------------

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Maintain a positive environment

Getting Help
------------

- Open an issue on GitHub
- Check existing issues and this documentation
- Contact the maintainer: cumulus13@gmail.com

Thank you for contributing to envdot!
