#!/usr/bin/env python3
# file: envdot/setup.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-10 23:58:33.095178
# Description: Setup configuration for envdot package
# License: MIT

from setuptools import setup, find_packages
import traceback
from pathlib import Path

NAME = 'envdot'

def generate_toml(version="0.1.0"):
    with open(str(Path(__file__).parent / 'pyproject.toml'), 'w') as f_toml:
        f_toml.write("""[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "envdot"
version = "%s"
description = "Enhanced environment variable management with multi-format support"
readme = "README.md"
requires-python = ">=3.7"
license = {text = "MIT"}
authors = [
    {name = "Hadi Cahyadi", email = "cumulus13@gmail.com"}
]
keywords = ["environment", "variables", "config", "envdot", "configuration"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.optional-dependencies]
yaml = ["PyYAML>=5.1"]
all = ["PyYAML>=5.1"]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.950",
]

[project.urls]
Homepage = "https://github.com/cumulus13/envdot"
Documentation = "https://github.com/cumulus13/envdot#readme"
Repository = "https://github.com/cumulus13/envdot"
"Bug Tracker" = "https://github.com/cumulus13/envdot/issues"

[tool.black]
line-length = 100
target-version = ['py37', 'py38', 'py39', 'py310', 'py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.7"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true"""%(version))

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
    description="Enhanced environment variable management with multi-format support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cumulus13/envdot",
    packages=[NAME],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "yaml": ["PyYAML>=5.1"],
        "all": ["PyYAML>=5.1"],
    },
)