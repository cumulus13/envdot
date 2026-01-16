#!/usr/bin/env python3
# file: envdot/setup.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:58:33.095178
# Description: Setup configuration for envdot package
# License: MIT

from setuptools import setup, find_packages
import traceback
from pathlib import Path
import os

NAME = 'envdot'

def generate_toml(version="0.1.0"):
    with open(str(Path(__file__).parent / 'pyproject.toml'), 'w') as f_toml:
        f_toml.write("""[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "envdot"
version = "%s"
description = "Enhanced environment variable management with multi-format support (.env, JSON, YAML, INI, TOML)"
readme = "README.md"
requires-python = ">=3.8"
license = "MIT"
authors = [
    {name = "Hadi Cahyadi", email = "cumulus13@gmail.com"}
]
maintainers = [
    {name = "Hadi Cahyadi", email = "cumulus13@gmail.com"}
]
keywords = [
    "environment",
    "config",
    "configuration",
    "env",
    "dotenv",
    "yaml",
    "json",
    "toml",
    "ini",
    "settings"
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration",
    "Topic :: Utilities"
]
dependencies = ["version_get"]

[project.optional-dependencies]
full = [
    "pyyaml>=6.0.1",
    "tomli>=2.0.1;python_version<'3.11'",
    "tomli-w>=1.0.0",
    "json5>=0.9.14",
    "richcolorlog>=0.1.0"
]
yaml = ["pyyaml>=6.0.1"]
toml = [
    "tomli>=2.0.1;python_version<'3.11'",
    "tomli-w>=1.0.0"
]
json5 = ["json5>=0.9.14"]
rich = ["richcolorlog>=0.1.0"]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pre-commit>=3.3.0"
]

[project.urls]
Homepage = "https://github.com/cumulus13/envdot"
Documentation = "https://envdot.readthedocs.io"
Repository = "https://github.com/cumulus13/envdot"
"Bug Tracker" = "https://github.com/cumulus13/envdot/issues"

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | \.eggs
  | build
  | dist
)/
'''

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = [
    "--verbose",
    "--cov=envdot",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-branch"
]

[tool.setuptools.packages.find]
where = ["."]
include = ["envdot*"]
exclude = ["tests*", "docs*", "examples*"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_calls = false
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_optional = true

[[tool.mypy.overrides]]
module = [
    "yaml.*",
    "tomli.*",
    "tomllib.*",
    "tomli_w.*",
    "json5.*",
    "richcolorlog.*",
    "version_get.*"
]
ignore_missing_imports = true

[tool.coverage.run]
source = ["envdot"]
omit = [
    "tests/*",
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod"
]"""%(version))


def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "0.1.0"

generate_toml(get_version())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


__version__ = get_version()
print(f"NAME   : {NAME}")
print(f"VERSION: {__version__}")

setup(
    name="envdot",
    version=__version__,
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    description="Enhanced environment variable management with multi-format support (.env, JSON, YAML, INI, TOML)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cumulus13/envdot",
    packages=find_packages(),
    license="MIT",
    license_files=["LICENSE"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "version-get>=0.1.0",
        "pathlib3"
    ],
    extras_require={
        "full": [
            "pyyaml>=6.0.1",
            "tomli>=2.0.1;python_version<'3.11'",
            "tomli-w>=1.0.0",
            "json5>=0.9.14",
            "richcolorlog>=0.1.0",
        ],
        "yaml": ["pyyaml>=6.0.1"],
        "toml": [
            "tomli>=2.0.1;python_version<'3.11'",
            "tomli-w>=1.0.0",
        ],
        "json5": ["json5>=0.9.14"],
        "rich": ["richcolorlog>=0.1.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
    },
    # entry_points={
    #     "console_scripts": [
    #         "envdot=envdot.cli:main",  # If you add CLI later
    #     ],
    # },
    keywords=[
        "environment",
        "config",
        "configuration",
        "env",
        "dotenv",
        "yaml",
        "json",
        "toml",
        "ini",
        "settings",
    ],
    project_urls={
        "Documentation": "https://envdot.readthedocs.io",
        "Source": "https://github.com/cumulus13/envdot",
        "Bug Tracker": "https://github.com/cumulur13/envdot/issues",
    },
)