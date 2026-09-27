# 🌟 envdot

Enhanced environment variable management for Python with multi-format support and automatic type detection.

[![PyPI version](https://badge.fury.io/py/envdot.svg)](https://badge.fury.io/py/envdot)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://envdot.readthedocs.io/)

## 📋 Features

- 🔧 **Multiple Format Support**: `.env`, `.json`, `.yaml`, `.yml`, and `.ini` files
- 🎯 **Automatic Type Detection**: Automatically converts strings to `bool`, `int`, `float`, or keeps as `string`
- 💾 **Read and Write**: Load from and save to configuration files
- 🔄 **Method Chaining**: Fluent API for cleaner code
- 🌍 **OS Environment Integration**: Seamlessly works with `os.environ` (os.getenv, os.setenv)
- 📦 **Zero Dependencies**: Core functionality works without external packages (YAML support requires PyYAML)
- ✅ **Nested structure flattening**: Deep hierarchies → flat env vars  
- ✅ **Format conversion**: Convert between any supported formats  
- ✅ **Auto-typed `os.getenv()`**: Get typed values instead of strings  
- ✅ **Attribute-style access**: `config.DATABASE_HOST`  
- ✅ **Dictionary-style access**: `config['DATABASE_HOST']`  

---

## 🩹 1.0.37 bug fixes

Several users reported `cast_type` not working reliably and stale values
after config changes. Both are fixed as of **1.0.37**:

- Auto-detection no longer silently splits any string containing a space
  or comma into a tuple. A value like `APP_NAME=My Application` now stays
  the plain string `'My Application'` instead of becoming
  `('My', 'Application')` — this was the main reason `cast_type` seemed
  "useless": the original string was already gone by the time the cast
  ran. Lists/tuples/dicts are now only ever produced via an explicit
  `cast_type=list` / `tuple` / `dict`.
- `cast_type` now always casts from the original raw string rather than
  from a value auto-detection already converted, so it behaves
  predictably even in ambiguous cases (e.g. `RETRY_COUNT=1`).
- `get()` no longer force-reparses the whole config file on every single
  call — it now reloads automatically only when the file actually
  changed (or a file that didn't exist yet has appeared), and separately
  picks up direct `os.environ[key] = ...` changes. See
  [Auto-Reload](#8-auto-reload-config-file--os-env-changes).

See the [Type Detection Rules](#type-detection-rules) and
[Explicit Type Casting](#explicit-type-casting) sections below for the
current behavior.

---

## Installation

```bash
pip install envdot

# Full installation (all formats)
pip install envdot[full]

# Specific format support
pip install envdot[yaml]    # YAML support
pip install envdot[toml]    # TOML support
pip install envdot[json5]   # JSON5 support
```

## Documentation
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://envdot.readthedocs.io/)

## 🚀 Quick Start

### Basic Usage

```python
from envdot import load_env, get_env

# Load configuration (auto-detects format)
load_env()  # Searches for .env, config.json, config.yaml, etc.

# Or load specific file
load_env('config.toml')

# Get values (automatically typed!)
db_host = get_env('DATABASE_HOST')      # Returns: "localhost" (str)
db_port = get_env('DATABASE_PORT')      # Returns: 5432 (int)
debug = get_env('DEBUG')                # Returns: True (bool)
timeout = get_env('TIMEOUT')            # Returns: 30.5 (float)

# With defaults
redis_host = get_env('REDIS_HOST', default='127.0.0.1')

# Explicit type casting
max_connections = get_env('MAX_CONNECTIONS', cast_type=int)
allowed_hosts = get_env('ALLOWED_HOSTS', cast_type=list)
```

```bash
$ cat .env
CELERY_BACKEND=redis://redis:6379/0
CELERY_BROKER=redis://redis:6379/0
DEBUG=true
DEBUGGER_SERVER=5.5
DEBUG_SERVER=false
DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1 [::1] 192.168.100.2 192.168.100.2"
POSTGRES_DB=django_celery
POSTGRES_PASSWORD=password1234-8
POSTGRES_USER=celery_admin
PYTHONDONTWRITEBYTECODE=true
PYTHONUNBUFFERED=true
RABBITMQ_DEFAULT_PASS=hackmeplease
RABBITMQ_DEFAULT_USER=syslog
RABBITMQ_HOST_DJANGO=rabbitmq
RABBITMQ_MANAGEMENT=true
RABBITMQ_PASSWORD_DJANGO=123-8
RABBITMQ_USERNAME_DJANGO=syslog
SECRET_KEY=dbaa1_i7%*3r9-=z-+_mz4r-!qeed@(-a_r(g@k8jo8y3r27%m
```

```python
In [1]: from envdot import load_env, show

In [2]: load_env()
Out[2]: DotEnv(filepath=.env, vars=18)

In [3]: show()
Out[3]:
{'CELERY_BACKEND': 'redis://redis:6379/0',
 'CELERY_BROKER': 'redis://redis:6379/0',
 'DEBUG': True,
 'DEBUGGER_SERVER': 5.5,
 'DEBUG_SERVER': False,
 'DJANGO_ALLOWED_HOSTS': 'localhost 127.0.0.1 [::1] 192.168.100.2 192.168.100.2',
 'POSTGRES_DB': 'django_celery',
 'POSTGRES_PASSWORD': 'password1234-8',
 'POSTGRES_USER': 'celery_admin',
 'PYTHONDONTWRITEBYTECODE': True,
 'PYTHONUNBUFFERED': True,
 'RABBITMQ_DEFAULT_PASS': 'hackmeplease',
 'RABBITMQ_DEFAULT_USER': 'syslog',
 'RABBITMQ_HOST_DJANGO': 'rabbitmq',
 'RABBITMQ_MANAGEMENT': True,
 'RABBITMQ_PASSWORD_DJANGO': '123-8',
 'RABBITMQ_USERNAME_DJANGO': 'syslog',
 'SECRET_KEY': 'dbaa1_i7%*3r9-=z-+_mz4r-!qeed@(-a_r(g@k8jo8y3r27%m'}

In [4]: config = load_env()

In [5]: config.show()
Out[5]:
{'CELERY_BACKEND': 'redis://redis:6379/0',
 'CELERY_BROKER': 'redis://redis:6379/0',
 'DEBUG': True,
 'DEBUGGER_SERVER': 5.5,
 'DEBUG_SERVER': False,
 'DJANGO_ALLOWED_HOSTS': 'localhost 127.0.0.1 [::1] 192.168.100.2 192.168.100.2',
 'POSTGRES_DB': 'django_celery',
 'POSTGRES_PASSWORD': 'password1234-8',
 'POSTGRES_USER': 'celery_admin',
 'PYTHONDONTWRITEBYTECODE': True,
 'PYTHONUNBUFFERED': True,
 'RABBITMQ_DEFAULT_PASS': 'hackmeplease',
 'RABBITMQ_DEFAULT_USER': 'syslog',
 'RABBITMQ_HOST_DJANGO': 'rabbitmq',
 'RABBITMQ_MANAGEMENT': True,
 'RABBITMQ_PASSWORD_DJANGO': '123-8',
 'RABBITMQ_USERNAME_DJANGO': 'syslog',
 'SECRET_KEY': 'dbaa1_i7%*3r9-=z-+_mz4r-!qeed@(-a_r(g@k8jo8y3r27%m'}

In [6]: config.DEBUG_SERVER
Out[6]: False

In [7]: config.DEBUG_SERVER = True

In [8]: show()
Out[8]:
{'CELERY_BACKEND': 'redis://redis:6379/0',
 'CELERY_BROKER': 'redis://redis:6379/0',
 'DEBUG': True,
 'DEBUGGER_SERVER': 5.5,
 'DEBUG_SERVER': True,
 'DJANGO_ALLOWED_HOSTS': 'localhost 127.0.0.1 [::1] 192.168.100.2 192.168.100.2',
 'POSTGRES_DB': 'django_celery',
 'POSTGRES_PASSWORD': 'password1234-8',
 'POSTGRES_USER': 'celery_admin',
 'PYTHONDONTWRITEBYTECODE': True,
 'PYTHONUNBUFFERED': True,
 'RABBITMQ_DEFAULT_PASS': 'hackmeplease',
 'RABBITMQ_DEFAULT_USER': 'syslog',
 'RABBITMQ_HOST_DJANGO': 'rabbitmq',
 'RABBITMQ_MANAGEMENT': True,
 'RABBITMQ_PASSWORD_DJANGO': '123-8',
 'RABBITMQ_USERNAME_DJANGO': 'syslog',
 'SECRET_KEY': 'dbaa1_i7%*3r9-=z-+_mz4r-!qeed@(-a_r(g@k8jo8y3r27%m'}

In [9]: config.show()
Out[9]:
{'CELERY_BACKEND': 'redis://redis:6379/0',
 'CELERY_BROKER': 'redis://redis:6379/0',
 'DEBUG': True,
 'DEBUGGER_SERVER': 5.5,
 'DEBUG_SERVER': True,
 'DJANGO_ALLOWED_HOSTS': 'localhost 127.0.0.1 [::1] 192.168.100.2 192.168.100.2',
 'POSTGRES_DB': 'django_celery',
 'POSTGRES_PASSWORD': 'password1234-8',
 'POSTGRES_USER': 'celery_admin',
 'PYTHONDONTWRITEBYTECODE': True,
 'PYTHONUNBUFFERED': True,
 'RABBITMQ_DEFAULT_PASS': 'hackmeplease',
 'RABBITMQ_DEFAULT_USER': 'syslog',
 'RABBITMQ_HOST_DJANGO': 'rabbitmq',
 'RABBITMQ_MANAGEMENT': True,
 'RABBITMQ_PASSWORD_DJANGO': '123-8',
 'RABBITMQ_USERNAME_DJANGO': 'syslog',
 'SECRET_KEY': 'dbaa1_i7%*3r9-=z-+_mz4r-!qeed@(-a_r(g@k8jo8y3r27%m'}

In [10]: os.getenv('DEBUG_SERVER')
Out[10]: True

In [11]: config.DEBUG_SERVER = False

In [12]: os.getenv('DEBUG_SERVER')
Out[12]: False

```

```python
from envdot import DotEnv

# Auto-detect and load from common config files (.env, config.json, etc.)
env = DotEnv()

# Or specify a file
env = DotEnv('.env')

# Get values with automatic type detection
db_host = env.get('DB_HOST')            # Returns string
# or
db_host = os.getenv('DB_HOST')          # Returns string

db_port = env.get('DB_PORT')            # Returns int (auto-detected)
# or
db_port = os.getenv('DB_PORT')         # Returns int (auto-detected)

debug_mode = env.get('DEBUG')           # Returns bool (auto-detected)
# or
debug_mode = os.getenv('DEBUG')        # Returns bool (auto-detected)

api_timeout = env.get('API_TIMEOUT')    # Returns float (auto-detected)
# or
api_timeout = os.getenv('API_TIMEOUT') # Returns float (auto-detected)

# Set values
env.set('NEW_KEY', 'value')
# or
env.setenv('NEW_KEY', 'value')

env.set('FEATURE_ENABLED', True)
# or
env.setenv('FEATURE_ENABLED', True)

# Save to file
env.save('.env')
# or
env.save()
# or
os.save_env()
```

### Convenience Functions

```python
from envdot import load_env, get_env, set_env, save_env

# Load configuration
load_env('.env')

# or just
load_env()

# Get values
database_url = get_env('DATABASE_URL')
max_connections = get_env('MAX_CONNECTIONS', default=100)

# Set values
set_env('NEW_FEATURE', True)

# Save changes
save_env('.env') # or just save_env()
```

### Working with Different File Formats

#### .env File
```python
env = DotEnv('.env')
env.load()
```

#### JSON File
```python
env = DotEnv('config.json')
env.load()
```

#### YAML File
```python
env = DotEnv('config.yaml')
env.load()  # Requires PyYAML
```

#### INI File
```python
env = DotEnv('config.ini')
env.load()
```

### Type Detection Examples

The package automatically detects and converts types:

```python
# Given this .env file:
# DEBUG=true
# PORT=8080
# TIMEOUT=30.5
# APP_NAME=MyApp
# EMPTY_VALUE=

env = DotEnv('.env') # or load_env() or load_env('.env')

env.get('DEBUG')      # Returns: True (bool)
env.get('PORT')       # Returns: 8080 (int)
env.get('TIMEOUT')    # Returns: 30.5 (float)
env.get('APP_NAME')   # Returns: 'MyApp' (str)
env.get('EMPTY_VALUE') # Returns: None

# env.get same as os.getenv
```

> ⚠️ Auto-detection only ever produces `bool`, `None`, `int`, `float`, or
> `str`. A value like `ALLOWED_HOSTS=localhost, 127.0.0.1` is **kept as
> the plain string** `'localhost, 127.0.0.1'` — it is never silently
> split into a list/tuple just because it contains spaces or commas.
> Ask for `cast_type=list` (or `tuple`) explicitly if that's what you want
> (see below). This used to not be the case in versions before 1.0.37,
> where any value containing a space or comma was auto-split into a
> tuple — this broke plain strings such as `APP_NAME=My Application`
> and made `cast_type` ineffective, since the original string was
> already gone by the time the cast ran. That bug is fixed as of 1.0.37.

### Explicit Type Casting

`cast_type` always casts from the **original, untouched string** value in
the config file / `os.environ` — never from a value that auto-detection
already converted. This keeps casting predictable even in ambiguous cases,
e.g. `RETRY_COUNT=1` auto-detects as `int` `1` (not `bool`), but you can
still force it either way explicitly:

```python
# Force a specific type
version = env.get('VERSION', cast_type=str)
port = env.get('PORT', cast_type=int)
enabled = env.get('RETRY_COUNT', cast_type=bool)   # '1'/'yes'/'on'/'true' -> True

# Cast to list / tuple - splits on commas/whitespace, or parses a
# "[...]" / "(...)" literal
hosts = env.get('ALLOWED_HOSTS', cast_type=list)
# "localhost, 127.0.0.1, example.com" -> ['localhost', '127.0.0.1', 'example.com']

# Cast to dict - parses a "{...}" JSON/JSON5-ish literal, or
# whitespace-separated "key:value" pairs
opts = env.get('SETTINGS_MAP', cast_type=dict)
# "a:1 b:2 c:3" -> {'a': '1', 'b': '2', 'c': '3'}
```

### Method Chaining

```python
env = DotEnv('.env') \
    .load() \
    .set('NEW_KEY', 'value') \
    .set('ANOTHER_KEY', 123) \
    .save()
```

### Dictionary-Style Access

```python
env = DotEnv('.env')

# Get values
value = env['KEY_NAME']

# Set values
env['NEW_KEY'] = 'new value'

# Check existence
if 'API_KEY' in env:
    print("API key is configured")

# Get all variables
all_vars = env.all()
```

### Advanced Features

#### Load Without Overriding

```python
env.load(override=False)  # Keep existing values
```

#### Load Without Applying to OS Environment

```python
env.load(apply_to_os=False)  # Don't set in os.environ
```

#### Save to Different Format

```python
env = DotEnv('.env')
env.load()
env.save('config.json')  # Convert .env to JSON
```

#### Clear Variables

```python
env.clear()  # Clear internal storage only
env.clear(clear_os=True)  # Also clear from os.environ
```

#### Delete Specific Keys

```python
env.delete('OLD_KEY')
env.delete('TEMP_KEY', remove_from_os=True)
```

## Type Detection Rules

The package uses the following rules for **automatic** type detection
(i.e. what you get back from `.get(key)` with no `cast_type`):

- **Boolean**: `true`, `yes`, `on` → `True` | `false`, `no`, `off` → `False`
- **None**: `none`, `null`, empty string → `None`
- **Integer**: `1`, `0`, `42`, `-7`, ... → `int`
- **Float**: `30.5`, `1e10`, ... → `float`
- **String**: Everything else → `str` (including things like
  `"localhost, 127.0.0.1"` or `"My Application"` - a space or comma in
  the value does **not** turn it into a list/tuple automatically)

> Note: `1`/`0` are always auto-detected as `int`, not `bool` - they're
> genuinely ambiguous (is `RETRY=1` a count or a flag?), so envdot
> resolves that ambiguity toward the more common case (a number) and
> lets you opt into a boolean explicitly with `cast_type=bool`, which
> treats `1`/`0`/`true`/`false`/`yes`/`no`/`on`/`off` all as booleans.

List, tuple, and dict values are **never** produced automatically - only
via an explicit `cast_type=list` / `cast_type=tuple` / `cast_type=dict`
(see [Explicit Type Casting](#explicit-type-casting)).

## 📝 Supported Formats

### 1. .env File (Most Common)

```env
DEBUG=true
PORT=8080
DATABASE_URL=postgresql://localhost/mydb
```

```env
# .env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DEBUG=true
TIMEOUT=30.5
APP_NAME="My Application"
```

```python
from envdot import load_env, get_env

load_env('.env')
print(get_env('DATABASE_PORT'))  # 5432 (int, not string!)
print(get_env('DEBUG'))           # True (bool, not string!)
```

### 2. JSON File

```json
{
  "DEBUG": true,
  "PORT": 8080,
  "DATABASE_URL": "postgresql://localhost/mydb"
}
```

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "credentials": {
      "username": "admin",
      "password": "secret"
    }
  },
  "features": ["auth", "cache"]
}
```

```python
load_env('config.json')

# Nested keys are flattened with underscores
print(get_env('DATABASE_HOST'))                    # localhost
print(get_env('DATABASE_CREDENTIALS_USERNAME'))    # admin
print(get_env('FEATURES_0'))                       # auth
```

**Flattening Rules:**
- `database.host` → `DATABASE_HOST`
- `database.credentials.username` → `DATABASE_CREDENTIALS_USERNAME`
- `features[0]` → `FEATURES_0`


### 3. YAML File

```yaml
DEBUG: true
PORT: 8080
DATABASE_URL: postgresql://localhost/mydb
```

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret

server:
  primary:
    host: server1.example.com
    port: 8080
  secondary:
    host: server2.example.com
    port: 8081
```

```python
load_env('config.yaml')

print(get_env('DATABASE_HOST'))              # localhost
print(get_env('DATABASE_CREDENTIALS_USERNAME'))  # admin
print(get_env('SERVER_PRIMARY_HOST'))        # server1.example.com
```

**Installation:** `pip install pyyaml`

### 4. INI File

```ini
[DEFAULT]
DEBUG = true
PORT = 8080
DATABASE_URL = postgresql://localhost/mydb
```

```ini
# config.ini
[DEFAULT]
app_name = My Application
version = 1.0.0

[database]
host = localhost
port = 5432
username = admin

[server]
host = 0.0.0.0
port = 8080
```

```python
load_env('config.ini')

# DEFAULT section items have no prefix
print(get_env('APP_NAME'))          # My Application

# Other sections use section name as prefix
print(get_env('DATABASE_HOST'))     # localhost
print(get_env('SERVER_PORT'))       # 8080
```

### 5. TOML File (⭐ Recommended for Python Projects)

```toml
# config.toml
title = "My Application"
version = "1.0.0"

[database]
host = "localhost"
port = 5432

[database.credentials]
username = "admin"
password = "secret"

[[features]]
name = "authentication"
enabled = true

[[features]]
name = "caching"
enabled = false
```

```python
load_env('config.toml')

print(get_env('TITLE'))                         # My Application
print(get_env('DATABASE_HOST'))                 # localhost
print(get_env('DATABASE_CREDENTIALS_USERNAME')) # admin
print(get_env('FEATURES_0_NAME'))              # authentication
print(get_env('FEATURES_0_ENABLED'))           # True
```

**Installation:**
- Python 3.11+: Built-in support for reading
- Python < 3.11: `pip install tomli`
- Writing TOML: `pip install tomli-w` (all Python versions)

---

## 🔄 Format Conversion

Convert between any supported formats:

```python
from envdot import load_env, save_env

# Load from JSON
load_env('config.json')

# Save as different formats
save_env('config.env', format='env')      # Convert to .env
save_env('config.yaml', format='yaml')    # Convert to YAML
save_env('config.toml', format='toml')    # Convert to TOML
save_env('config.ini', format='ini')      # Convert to INI
```

---

## 🎯 Advanced Usage

### 1. Auto-typed `os.getenv()`

Make `os.getenv()` return typed values automatically:

```python
from envdot import load_env
import os

# Enable auto-typed os.getenv()
load_env(auto_replace_getenv=True)  # Default is True

# Now os.getenv() returns typed values!
port = os.getenv('DATABASE_PORT')  # Returns: 5432 (int), not "5432" (str)
debug = os.getenv('DEBUG')          # Returns: True (bool), not "true" (str)
timeout = os.getenv('TIMEOUT')      # Returns: 30.5 (float), not "30.5" (str)
```

### 2. OS Module Patching

Add helpful methods to `os` module:

```python
from envdot import load_env
import os

# Enable os module patching
load_env(patch_os=True)  # Default is True

# Now you can use:
os.getenv_typed('PORT')           # Auto-typed getenv
os.getenv_int('PORT', default=8080)
os.getenv_bool('DEBUG', default=False)
os.getenv_float('RATIO', default=1.0)
os.setenv('KEY', 'value')         # Set and save
os.save_env()                      # Save to file
```

### 3. Attribute-Style Access

```python
from envdot import DotEnv

env = DotEnv('config.toml')

# Access like attributes
print(env.DATABASE_HOST)
print(env.DATABASE_PORT)

# Set like attributes (auto-saves!)
env.NEW_KEY = 'new_value'
env.MAX_WORKERS = 10
```

### 4. Dictionary-Style Access

```python
from envdot import DotEnv

env = DotEnv('config.json')

# Dictionary-like access
print(env['DATABASE_HOST'])
env['NEW_KEY'] = 'value'

# Check existence
if 'DEBUG' in env:
    print("Debug mode is set")
```

### 5. Explicit Type Casting

```python
from envdot import get_env

# Force specific types
port = get_env('PORT', cast_type=int)
enabled = get_env('ENABLED', cast_type=bool)
ratio = get_env('RATIO', cast_type=float)

# Cast to list
hosts = get_env('ALLOWED_HOSTS', cast_type=list)
# "localhost, 127.0.0.1, example.com" → ['localhost', '127.0.0.1', 'example.com']

# Cast to tuple
coords = get_env('COORDINATES', cast_type=tuple)
```

### 6. Production Environment Setup

```python
from envdot import load_env, get_env
import os

# Load base configuration
load_env('config.base.toml')

# Override with environment-specific settings
environment = os.getenv('ENVIRONMENT', 'development')

if environment == 'production':
    load_env('config.prod.env', override=True)
elif environment == 'staging':
    load_env('config.staging.env', override=True)

# Now get_env() returns environment-specific values
db_host = get_env('DATABASE_HOST')
```

### 7. Recursive File Search

```python
from envdot import DotEnv

# Automatically search current directory and subdirectories
env = DotEnv()
env.load(recursive=True)

# Or specify search parameters
env.find_settings_recursive(
    start_path='/path/to/project',
    max_depth=5,
    filename=['.env', 'config.toml'],
    exceptions=['node_modules', 'venv']
)
```

### 8. Auto-Reload (config file & OS env changes)

`get()` (and `get_env()`) accept a `reload` argument that controls whether
the backing config file gets re-checked:

```python
from envdot import get_env

get_env('PORT')                 # reload=None (default): "smart" - only
                                 # re-reads the file if its content
                                 # actually changed since the last read
                                 # (or a config file that didn't exist
                                 # yet has now appeared)
get_env('PORT', reload=True)    # always force a full re-read of the file
get_env('PORT', reload=False)   # never check/re-read the file this call
```

This replaces the old behavior of unconditionally re-parsing the entire
config file on every single `get()` call, while still guaranteeing you
never get a stale value after the file changes on disk.

Independently of `reload`, if something sets `os.environ[key]` directly
(bypassing envdot) *after* envdot itself wrote that key to `os.environ`,
`get()` picks up the new value:

```python
import os
from envdot import load_env, get_env

load_env()                      # PORT=8080 from .env
os.environ['PORT'] = '9999'     # changed directly, outside envdot
get_env('PORT')                 # -> 9999
```

A pre-existing `os.environ` value that envdot never wrote itself (e.g.
left over from another `DotEnv` instance, or set before `load_env()` ran)
is *not* treated this way - it won't silently override a value envdot
just loaded from its own config file. Pass `with_os=False` to disable
this OS-environment sync entirely for a call.

---


## 🔧 API Reference

### DotEnv Class

#### `__init__(filepath=None, auto_load=True)`
Initialize DotEnv instance.

#### `load(filepath=None, override=True, apply_to_os=True)`
Load environment variables from file.

#### `get(key, default=None, cast_type=None, reload=None, with_os=True)`
Get environment variable with automatic type detection. `reload=None`
(default) re-reads the config file only if it changed; `True`/`False`
force or skip the check. `with_os=True` picks up `os.environ[key]`
changes made outside envdot (see [Auto-Reload](#8-auto-reload-config-file--os-env-changes)).

#### `set(key, value, apply_to_os=True)`
Set environment variable.

#### `os.getenv(key, default=None, cast_type=None)`
Get environment variable with automatic type detection.

#### `os.setenv(key, value, apply_to_os=True)`
Set environment variable.

#### `save(filepath=None, format=None)`
Save environment variables to file.

#### `delete(key, remove_from_os=True)`
Delete environment variable.

#### `all()`
Get all environment variables as dictionary.

#### `keys()`
Get all variable names.

#### `clear(clear_os=False)`
Clear all stored variables.

#### Main Functions

```python
# Load configuration
load_env(
    filepath=None,              # Path to config file (auto-detects if None)
    auto_replace_getenv=True,   # Replace os.getenv() with typed version
    patch_os=True,              # Add helpers to os module
    override=True,              # Override existing values
    apply_to_os=True,           # Set values in os.environ
    store_typed=True,           # Store typed values internally
    recursive=True,             # Search recursively for config files
    newone=False               # Create new file if not found
)

# Get environment variable
get_env(
    key,                       # Variable name
    default=None,             # Default value if not found
    cast_type=None            # Force type conversion
)

# Set environment variable
set_env(
    key,                      # Variable name
    value,                    # Variable value
    apply_to_os=True         # Also set in os.environ
)

# Save configuration
save_env(
    filepath=None,            # Path to save (uses loaded path if None)
    format=None              # Format: 'env', 'json', 'yaml', 'ini', 'toml'
)
```

#### DotEnv Class

```python
from envdot import DotEnv

env = DotEnv(
    filepath='config.toml',   # Config file path
    auto_load=True,           # Auto-load on init
    newone=False             # Create new if not exists
)

# Methods
env.load(filepath=None, **kwargs)
env.get(key, default=None, cast_type=None)
env.set(key, value, apply_to_os=True)
env.save(filepath=None, format=None)
env.delete(key, remove_from_os=True)
env.all()                    # Get all as dict
env.keys()                   # Get all keys
env.clear(clear_os=False)   # Clear all variables

# Access styles
value = env.KEY              # Attribute
value = env['KEY']           # Dictionary
value = env.get('KEY')       # Method
value = env('KEY')           # Callable
```

#### Convenience Functions

- `load_env(filepath=None, **kwargs)` - Load environment variables
- `get_env(key, default=None, cast_type=None)` - Get environment variable same as os.getenv
- `set_env(key, value, **kwargs)` - Set environment variable same as os.setenv
- `save_env(filepath=None, **kwargs)` - Save environment variables

## 📊 Format Comparison

| Feature | .env | JSON | YAML | INI | TOML |
|---------|:----:|:----:|:----:|:---:|:----:|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Nesting** | ❌ | ✅ Deep | ✅ Deep | ⚠️ 1 level | ✅ Deep |
| **Comments** | ✅ | ❌* | ✅ | ✅ | ✅ |
| **Type Safety** | ⚠️ Auto | ✅ Native | ✅ Native | ⚠️ Auto | ✅ Strong |
| **Arrays** | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Portability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Python Std** | ❌ | ✅ | ❌ | ✅ | ✅ (3.11+) |
| **Best For** | Secrets | Web apps | Complex config | Legacy | Python projects |

\* JSON5 supports comments

---

## 🎓 Best Practices

### 1. Choose the Right Format

- **Use .env for**: Secrets, simple configs, CI/CD, maximum portability
- **Use JSON for**: API configs, web apps, cross-language projects
- **Use YAML for**: Complex configs, Kubernetes/Docker, human-readable
- **Use INI for**: Legacy systems, section-based configs
- **Use TOML for**: Python projects (recommended), strong typing needs

### 2. Type Safety

```python
# ✅ Good: Use explicit types for critical values
db_port = get_env('DATABASE_PORT', cast_type=int)
max_retries = get_env('MAX_RETRIES', cast_type=int)

# ✅ Good: Use defaults
timeout = get_env('TIMEOUT', default=30, cast_type=int)

# ⚠️ Careful: Auto-detection might surprise you
value = get_env('SOME_VALUE')  # Could be str, int, float, bool, or None
```

### 3. Environment-Specific Configs

```python
# config.base.toml - shared settings
# config.dev.env - development overrides
# config.prod.env - production overrides

load_env('config.base.toml')

import os
env = os.getenv('ENVIRONMENT', 'development')
if env == 'production':
    load_env('config.prod.env', override=True)
```

### 4. Secure Secrets

```python
# ✅ Good: Keep secrets in .env, never in version control
# .env (in .gitignore)
DATABASE_PASSWORD=secret123
API_KEY=xyz789

# config.toml (in git)
[database]
host = "localhost"
port = 5432
# password loaded from .env

# Load both
load_env('config.toml')
load_env('.env', override=True)  # Secrets override config
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=envdot --cov-report=html

# Specific test file
pytest tests/test_all_formats.py -v
```

---

## 📦 Dependencies

### Core (always installed)
- `version-get` - Version management

### Optional
- `pyyaml>=6.0.1` - YAML support
- `tomli>=2.0.1` - TOML reading (Python < 3.11)
- `tomli-w>=1.0.0` - TOML writing
- `json5>=0.9.14` - JSON5 support
- `richcolorlog>=0.1.0` - Rich logging

---

## 🔒 Security

- **Never commit** `.env` files to version control
- Use environment variables for **secrets**
- Use config files for **non-sensitive settings**
- Consider using **secret management services** for production

### Example `.gitignore`

```gitignore
# Environment files
.env
.env.local
.env.*.local
config.local.*
*.env.local

# But keep examples
!.env.example
!config.example.*
```

---

## 📖 Examples

See the `examples/` directory for complete examples:
- `example_basic.py` - Basic usage
- `example_all_formats.py` - All format examples
- `example_production.py` - Production setup
- `example_conversion.py` - Format conversion

---

## 📄 Debug envs

- `DOTENV_DEBUG` 
- `LOG_LEVEL_ENVDOT` | `ENVDOT_LOG_LEVEL` - default: `CRITICAL`
- `NO_LOGGING` - use by richcolorlog
- `PYDEBUGGER` - use by pydebugger
- `DEBUG` - global debug env for any modules 

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by `python-dotenv`
- TOML support via `tomli`/`tomllib`
- YAML support via `PyYAML`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/cumulus13/envdot/issues)
- **Email**: cumulus13@gmail.com
- **Documentation**: See this README and inline documentation

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)

**Made with ❤️ by Hadi Cahyadi**

⭐ **Star this repo** if you find it helpful!