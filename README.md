# envdot

Enhanced environment variable management for Python with multi-format support and automatic type detection.

## Features

- 🔧 **Multiple Format Support**: `.env`, `.json`, `.yaml`, `.yml`, and `.ini` files
- 🎯 **Automatic Type Detection**: Automatically converts strings to `bool`, `int`, `float`, or keeps as `string`
- 💾 **Read and Write**: Load from and save to configuration files
- 🔄 **Method Chaining**: Fluent API for cleaner code
- 🌍 **OS Environment Integration**: Seamlessly works with `os.environ`
- 📦 **Zero Dependencies**: Core functionality works without external packages (YAML support requires PyYAML)

## Installation

```bash
pip install envdot

# With YAML support
pip install envdot[yaml]

# With all extras
pip install envdot[all]
```

## Quick Start

### Basic Usage

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

### Explicit Type Casting

```python
# Force a specific type
version = env.get('VERSION', cast_type=str)
port = env.get('PORT', cast_type=int)
enabled = env.get('ENABLED', cast_type=bool)
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

The package uses the following rules for automatic type detection:

- **Boolean**: `true`, `yes`, `on`, `1` → `True` | `false`, `no`, `off`, `0` → `False`
- **None**: `none`, `null`, empty string → `None`
- **Integer**: Numbers without decimal point → `int`
- **Float**: Numbers with decimal point → `float`
- **String**: Everything else → `str`

## File Format Examples

### .env
```env
DEBUG=true
PORT=8080
DATABASE_URL=postgresql://localhost/mydb
```

### .json
```json
{
  "DEBUG": true,
  "PORT": 8080,
  "DATABASE_URL": "postgresql://localhost/mydb"
}
```

### .yaml
```yaml
DEBUG: true
PORT: 8080
DATABASE_URL: postgresql://localhost/mydb
```

### .ini
```ini
[DEFAULT]
DEBUG = true
PORT = 8080
DATABASE_URL = postgresql://localhost/mydb
```

## API Reference

### DotEnv Class

#### `__init__(filepath=None, auto_load=True)`
Initialize DotEnv instance.

#### `load(filepath=None, override=True, apply_to_os=True)`
Load environment variables from file.

#### `get(key, default=None, cast_type=None)`
Get environment variable with automatic type detection.

#### `set(key, value, apply_to_os=True)`
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

### Convenience Functions

- `load_env(filepath=None, **kwargs)` - Load environment variables
- `get_env(key, default=None, cast_type=None)` - Get environment variable
- `set_env(key, value, **kwargs)` - Set environment variable
- `save_env(filepath=None, **kwargs)` - Save environment variables

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)