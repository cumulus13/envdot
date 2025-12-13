# 📘 Configuration File Formats Guide

Complete guide for reading different configuration formats in envdot.

## 🔧 Installation

```bash
# Basic installation
pip install envdot

# With all format support
pip install envdot pyyaml tomli tomli-w json5

# Python 3.11+ already has tomllib built-in (reading TOML)
# But still needs tomli-w for writing TOML
```

---

## 📝 1. .env File (Standard)

### Structure
```env
# Simple key=value format
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=admin
DATABASE_PASSWORD=secret123

# Boolean values
DEBUG=true
ENABLE_CACHE=false

# Numbers (auto-detected)
MAX_CONNECTIONS=100
TIMEOUT=30.5

# Values with spaces (use quotes)
APP_NAME="My Application"
DESCRIPTION="A production-ready app"
```

### Reading
```python
from envdot import load_env, get_env

# Load .env file
env = load_env('.env')

# Access values (auto-typed)
host = get_env('DATABASE_HOST')        # Returns: "localhost" (str)
port = get_env('DATABASE_PORT')        # Returns: 5432 (int)
debug = get_env('DEBUG')               # Returns: True (bool)
timeout = get_env('TIMEOUT')           # Returns: 30.5 (float)

# With default values
redis_host = get_env('REDIS_HOST', default='127.0.0.1')

# Force type casting
max_conn = get_env('MAX_CONNECTIONS', cast_type=int)
```

### Key Features
- ✅ Simple key=value format
- ✅ Comments with `#`
- ✅ Automatic type detection
- ✅ Quote handling for spaces
- ✅ Most portable format

---

## 🗂️ 2. JSON File

### Structure
```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "credentials": {
      "username": "admin",
      "password": "secret123"
    }
  },
  "app": {
    "name": "My Application",
    "debug": true,
    "max_connections": 100
  },
  "features": ["auth", "cache", "logging"]
}
```

### Flattened Keys
envdot automatically flattens nested JSON:
```
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_CREDENTIALS_USERNAME = "admin"
DATABASE_CREDENTIALS_PASSWORD = "secret123"
APP_NAME = "My Application"
APP_DEBUG = true
APP_MAX_CONNECTIONS = 100
FEATURES_0 = "auth"
FEATURES_1 = "cache"
FEATURES_2 = "logging"
```

### Reading
```python
from envdot import load_env, get_env

# Load JSON file
env = load_env('config.json')

# Access flattened keys
db_host = get_env('DATABASE_HOST')
db_port = get_env('DATABASE_PORT')
username = get_env('DATABASE_CREDENTIALS_USERNAME')
app_debug = get_env('APP_DEBUG')

# Array access
feature_0 = get_env('FEATURES_0')  # "auth"
feature_1 = get_env('FEATURES_1')  # "cache"
```

### JSON5 Support (Flexible JSON)
```json5
{
  // Comments allowed!
  database: {
    host: 'localhost',  // Single quotes OK
    port: 5432,
  },  // Trailing comma OK
}
```

### Key Features
- ✅ Nested structure support
- ✅ Arrays and objects
- ✅ JSON5 support (comments, single quotes)
- ✅ Automatic flattening with `_` separator
- ⚠️ Array indices become keys (FEATURES_0, FEATURES_1)

---

## 📋 3. YAML File

### Structure
```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret123

app:
  name: My Application
  debug: true
  max_connections: 100

features:
  - auth
  - cache
  - logging

# Complex nested structure
server:
  primary:
    host: server1.example.com
    port: 8080
  secondary:
    host: server2.example.com
    port: 8081
```

### Flattened Keys
```
DATABASE_HOST = localhost
DATABASE_PORT = 5432
DATABASE_CREDENTIALS_USERNAME = admin
DATABASE_CREDENTIALS_PASSWORD = secret123
APP_NAME = My Application
APP_DEBUG = true
APP_MAX_CONNECTIONS = 100
FEATURES_0 = auth
FEATURES_1 = cache
FEATURES_2 = logging
SERVER_PRIMARY_HOST = server1.example.com
SERVER_PRIMARY_PORT = 8080
SERVER_SECONDARY_HOST = server2.example.com
SERVER_SECONDARY_PORT = 8081
```

### Reading
```python
from envdot import load_env, get_env

# Load YAML file
env = load_env('config.yaml')

# Access nested values
db_host = get_env('DATABASE_HOST')
primary_host = get_env('SERVER_PRIMARY_HOST')
secondary_port = get_env('SERVER_SECONDARY_PORT')

# Boolean and numeric types preserved
debug = get_env('APP_DEBUG')  # Returns: True (bool)
port = get_env('DATABASE_PORT')  # Returns: 5432 (int)
```

### Key Features
- ✅ Human-readable format
- ✅ Deep nesting support
- ✅ Comments with `#`
- ✅ Lists and complex structures
- ✅ Type preservation
- ⚠️ Requires PyYAML: `pip install pyyaml`

---

## ⚙️ 4. INI File

### Structure
```ini
# config.ini
[DEFAULT]
app_name = My Application
version = 1.0.0

[database]
host = localhost
port = 5432
username = admin
password = secret123

[server]
host = 0.0.0.0
port = 8080
workers = 4

[cache]
enabled = true
ttl = 3600
```

### Flattened Keys
INI sections become prefixes:
```
APP_NAME = My Application          # From [DEFAULT]
VERSION = 1.0.0                    # From [DEFAULT]
DATABASE_HOST = localhost          # From [database]
DATABASE_PORT = 5432
DATABASE_USERNAME = admin
DATABASE_PASSWORD = secret123
SERVER_HOST = 0.0.0.0             # From [server]
SERVER_PORT = 8080
SERVER_WORKERS = 4
CACHE_ENABLED = true              # From [cache]
CACHE_TTL = 3600
```

### Reading
```python
from envdot import load_env, get_env

# Load INI file
env = load_env('config.ini')

# Access with section prefixes
app_name = get_env('APP_NAME')              # From DEFAULT
db_host = get_env('DATABASE_HOST')          # From database section
server_port = get_env('SERVER_PORT')        # From server section
cache_enabled = get_env('CACHE_ENABLED')    # From cache section

# Types auto-detected
port = get_env('DATABASE_PORT')      # Returns: 5432 (int)
workers = get_env('SERVER_WORKERS')  # Returns: 4 (int)
enabled = get_env('CACHE_ENABLED')   # Returns: True (bool)
```

### Key Features
- ✅ Section-based organization
- ✅ DEFAULT section for globals
- ✅ Simple key=value format
- ✅ Section names become key prefixes
- ⚠️ No deep nesting (only 1 level: section.key)

---

## 🎯 5. TOML File (Recommended for Python Projects)

### Structure
```toml
# config.toml
title = "My Application"
version = "1.0.0"

[database]
host = "localhost"
port = 5432
max_connections = 100

[database.credentials]
username = "admin"
password = "secret123"

[server]
host = "0.0.0.0"
port = 8080
workers = 4
debug = true

[cache]
enabled = true
ttl = 3600
type = "redis"

[[features]]
name = "authentication"
enabled = true

[[features]]
name = "caching"
enabled = false

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[logging.handlers]
console = true
file = "app.log"
```

### Flattened Keys
TOML sections and nested tables:
```
TITLE = My Application
VERSION = 1.0.0
DATABASE_HOST = localhost
DATABASE_PORT = 5432
DATABASE_MAX_CONNECTIONS = 100
DATABASE_CREDENTIALS_USERNAME = admin
DATABASE_CREDENTIALS_PASSWORD = secret123
SERVER_HOST = 0.0.0.0
SERVER_PORT = 8080
SERVER_WORKERS = 4
SERVER_DEBUG = true
CACHE_ENABLED = true
CACHE_TTL = 3600
CACHE_TYPE = redis
FEATURES_0_NAME = authentication
FEATURES_0_ENABLED = true
FEATURES_1_NAME = caching
FEATURES_1_ENABLED = false
LOGGING_LEVEL = INFO
LOGGING_FORMAT = %(asctime)s - %(name)s - %(levelname)s - %(message)s
LOGGING_HANDLERS_CONSOLE = true
LOGGING_HANDLERS_FILE = app.log
```

### Reading
```python
from envdot import load_env, get_env

# Load TOML file
env = load_env('config.toml')

# Access root level
title = get_env('TITLE')
version = get_env('VERSION')

# Access nested sections
db_host = get_env('DATABASE_HOST')
db_user = get_env('DATABASE_CREDENTIALS_USERNAME')

# Server config
server_host = get_env('SERVER_HOST')
server_port = get_env('SERVER_PORT')
debug = get_env('SERVER_DEBUG')

# Arrays of tables
feature_0_name = get_env('FEATURES_0_NAME')      # "authentication"
feature_0_enabled = get_env('FEATURES_0_ENABLED')  # True
feature_1_name = get_env('FEATURES_1_NAME')      # "caching"

# Deep nesting
log_level = get_env('LOGGING_LEVEL')
log_file = get_env('LOGGING_HANDLERS_FILE')

# Type preservation
port = get_env('DATABASE_PORT')  # Returns: 5432 (int)
debug = get_env('SERVER_DEBUG')  # Returns: True (bool)
```

### Key Features
- ✅ **Best for Python projects** (pyproject.toml)
- ✅ Strong typing (dates, times, arrays)
- ✅ Deep nested structure
- ✅ Array of tables support
- ✅ Comments with `#`
- ✅ Multi-line strings
- ⚠️ Requires tomli (Python < 3.11) or built-in tomllib (3.11+)
- ⚠️ Requires tomli-w for writing: `pip install tomli-w`

---

## 🔄 Format Comparison

| Feature | .env | JSON | YAML | INI | TOML |
|---------|------|------|------|-----|------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Nesting** | ❌ | ✅ Deep | ✅ Deep | ⚠️ 1 level | ✅ Deep |
| **Comments** | ✅ | ❌* | ✅ | ✅ | ✅ |
| **Type Safety** | ⚠️ Auto | ✅ Native | ✅ Native | ⚠️ Auto | ✅ Strong |
| **Arrays** | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Portability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Python Std** | ❌ | ✅ | ❌ | ✅ | ✅ (3.11+) |

\* JSON5 supports comments

---

## 🚀 Usage Examples

### 1. Auto-detect Format
```python
from envdot import load_env, get_env

# Automatically finds .env, config.json, config.yaml, or config.toml
env = load_env()

# Access any key
api_key = get_env('API_KEY')
```

### 2. Explicit File Selection
```python
# Load specific file
env = load_env('production.toml')
env = load_env('development.yaml')
env = load_env('staging.json')
```

### 3. Override and Save
```python
from envdot import load_env, set_env, save_env

# Load config
env = load_env('config.toml')

# Modify values
set_env('DATABASE_PORT', 5433)
set_env('DEBUG', False)

# Save back to file
save_env('config.toml')
```

### 4. Multiple Formats
```python
# Load from TOML, save to .env
env = load_env('config.toml')
save_env('.env', format='env')

# Load from JSON, save to YAML
env = load_env('config.json')
save_env('config.yaml', format='yaml')
```

---

## ⚠️ Important Notes

### Flattening Rules
1. **Nested objects**: Use `_` separator
   - `database.host` → `DATABASE_HOST`
   - `server.ssl.enabled` → `SERVER_SSL_ENABLED`

2. **Arrays**: Use numeric indices
   - `features[0]` → `FEATURES_0`
   - `servers[1].host` → `SERVERS_1_HOST`

3. **Key normalization**: All keys converted to UPPERCASE

### Type Detection
```python
# Automatic type detection
'true' → True (bool)
'false' → False (bool)
'123' → 123 (int)
'45.67' → 45.67 (float)
'none' → None
'hello' → 'hello' (str)
```

### Best Practices

1. **Use .env for**:
   - Simple configuration
   - Environment-specific secrets
   - CI/CD pipelines
   - Maximum portability

2. **Use JSON for**:
   - API configuration
   - Web applications
   - When nested structure needed
   - Cross-language projects

3. **Use YAML for**:
   - Complex configurations
   - Kubernetes/Docker configs
   - Human-readable configs
   - Deep nested structures

4. **Use INI for**:
   - Legacy systems
   - Section-based configs
   - Simple hierarchies
   - When compatibility needed

5. **Use TOML for**:
   - **Python projects** (pyproject.toml)
   - Strong typing requirements
   - Modern applications
   - Configuration with metadata

---

## 📦 Dependencies

```bash
# Minimal (only .env and JSON)
pip install envdot

# Full support
pip install envdot pyyaml tomli tomli-w json5
```

### Required packages per format:
- **.env**: No dependencies ✅
- **JSON**: No dependencies ✅
- **JSON5**: `pip install json5` (optional)
- **YAML**: `pip install pyyaml`
- **INI**: No dependencies ✅
- **TOML**: 
  - Read: `pip install tomli` (Python < 3.11) or built-in (3.11+)
  - Write: `pip install tomli-w`

---

## 🎓 Advanced Usage

### Recursive File Search
```python
from envdot import DotEnv

env = DotEnv()
# Automatically searches current dir and subdirectories
env.load(recursive=True)
```

### Type Casting
```python
from envdot import get_env

# Explicit type casting
port = get_env('PORT', cast_type=int)
hosts = get_env('ALLOWED_HOSTS', cast_type=list)
ratio = get_env('RATIO', cast_type=float)
```

### Environment Priority
```python
# Load base config
env = load_env('config.toml')

# Override with environment-specific
if os.getenv('ENV') == 'production':
    env.load('production.env', override=True)
```

---

## 🔒 Production Ready Checklist

✅ **All formats supported**: .env, JSON, YAML, INI, TOML  
✅ **Type safety**: Automatic type detection  
✅ **Error handling**: Proper exceptions for parse errors  
✅ **Nested structure**: Deep flattening with consistent naming  
✅ **Comments support**: Where format allows  
✅ **Backward compatible**: Works with existing configs  
✅ **No data loss**: Preserves all values during conversion  
✅ **Thread safe**: Can be used in multi-threaded apps  
✅ **Well tested**: Comprehensive test coverage  

---

## 📞 Support

For issues, feature requests, or questions:
- GitHub: [envdot repository]
- Documentation: Full API docs available
- Examples: See `examples/` directory

---

**Recommendation**: For new Python projects, use **TOML** (config.toml) as it's now the standard for Python configuration and will be natively supported in all Python 3.11+ installations.