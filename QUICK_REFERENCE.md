# 🚀 Quick Reference: Auto-Detection

## TL;DR

```python
from envdot import load_env, get_env

# ✅ Just call load_env() - that's it!
load_env()  # Auto-searches and auto-detects format

# Access values
db_host = get_env('DATABASE_HOST')
```

---

## 📋 Two Auto-Detection Features

### 1️⃣ Auto-Search Files: `load_env()`

**Question:** *"What if I call `load_env()` without any arguments?"*

**Answer:** ✅ **YES! It auto-searches for config files in priority order**

```python
from envdot import load_env

# No arguments needed!
load_env()
```

**Search Priority (highest to lowest):**

| Priority | File | Format | Use Case |
|----------|------|--------|----------|
| 🥇 **1** | `.env` | env | **Secrets, environment vars** |
| 🥈 **2** | `.env.local` | env | Local overrides |
| 🥉 **3** | `config.toml` | toml | **Recommended for Python** |
| 4 | `pyproject.toml` | toml | Python project metadata |
| 5 | `config.yaml` | yaml | Human-readable config |
| 6 | `config.yml` | yaml | YAML alternative |
| 7 | `config.json` | json | Structured data |
| 8 | `config.ini` | ini | Legacy systems |
| 9 | `.toml` | toml | Dotfile TOML |
| 10 | `.yaml` | yaml | Dotfile YAML |
| 11 | `.yml` | yaml | Dotfile YAML alt |
| 12 | `.json` | json | Dotfile JSON |
| 13 | `.ini` | ini | Dotfile INI |

**Example:**

```python
# Your project directory:
# ├── config.toml       ← Has: VALUE = "toml"
# ├── config.json       ← Has: {"VALUE": "json"}
# └── .env              ← Has: VALUE=env

load_env()  # Loads .env (highest priority)
print(get_env('VALUE'))  # Output: "env"
```

---

### 2️⃣ Auto-Detect Format: `load_env('config.toml')`

**Question:** *"What if I call `load_env('config.toml')` without `format=` parameter?"*

**Answer:** ✅ **YES! It auto-detects format from file extension**

```python
# All of these auto-detect format - NO format= needed!
load_env('.env')           # → env format
load_env('config.toml')    # → toml format
load_env('config.json')    # → json format
load_env('config.yaml')    # → yaml format
load_env('config.ini')     # → ini format

# Even dotfiles work!
load_env('.toml')          # → toml format
load_env('.json')          # → json format
load_env('.yaml')          # → yaml format
```

**Format Detection Rules:**

| File Extension | Detected Format | Example |
|----------------|-----------------|---------|
| `.env` | env | `.env`, `.env.local` |
| `.toml`, `.tml` | toml | `config.toml`, `.toml` |
| `.json` | json | `config.json`, `.json` |
| `.yaml`, `.yml` | yaml | `config.yaml`, `.yaml` |
| `.ini` | ini | `config.ini`, `.ini` |
| *no extension* | env | `envfile` → defaults to env |

---

## 💡 Usage Patterns

### Pattern 1: Zero Configuration (Recommended!)

```python
from envdot import load_env, get_env

# Just load - auto-searches and auto-detects!
load_env()

# Use anywhere
db_host = get_env('DATABASE_HOST')
db_port = get_env('DATABASE_PORT')
debug = get_env('DEBUG')
```

**Works with any of these files:**
- `.env` ✅
- `config.toml` ✅
- `config.yaml` ✅
- `config.json` ✅
- `config.ini` ✅

---

### Pattern 2: Explicit File (Auto-Format)

```python
# Specify file, format auto-detected
load_env('custom.toml')     # Format: toml (auto)
load_env('settings.yaml')   # Format: yaml (auto)
load_env('app.json')        # Format: json (auto)

# NO need for:
# load_env('config.toml', format='toml')  ❌ Redundant!
```

---

### Pattern 3: Multiple Files (Priority Override)

```python
# Load base config
load_env('config.base.toml')

# Override with environment-specific
import os
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    load_env('config.prod.env', override=True)
elif env == 'staging':
    load_env('config.staging.env', override=True)
```

---

### Pattern 4: Recursive Search

```python
from envdot import DotEnv

env = DotEnv()

# Search current dir and subdirectories
config_path = env.find_settings_recursive(
    start_path='.',
    max_depth=5
)

if config_path:
    env.load(config_path)
```

---

## 🎯 Common Scenarios

### Scenario 1: Simple Project

```python
# Your project:
# └── .env

from envdot import load_env, get_env

load_env()  # Finds .env automatically
db_url = get_env('DATABASE_URL')
```

---

### Scenario 2: Python Project with pyproject.toml

```python
# Your project:
# ├── pyproject.toml
# └── src/

from envdot import load_env, get_env

load_env()  # Finds pyproject.toml automatically
app_name = get_env('PROJECT_NAME')
```

---

### Scenario 3: Multiple Config Files

```python
# Your project:
# ├── .env              ← Secrets (highest priority)
# ├── config.toml       ← Base config
# └── config.local.toml ← Local overrides

from envdot import load_env

# Loads .env (highest priority)
load_env()

# Or load specific file
load_env('config.toml')
```

---

### Scenario 4: Different Formats in Different Environments

```python
# Development: .env
# Staging: config.staging.yaml
# Production: config.prod.toml

import os
from envdot import load_env

env = os.getenv('ENV', 'development')

if env == 'production':
    load_env('config.prod.toml')    # Auto-detects TOML
elif env == 'staging':
    load_env('config.staging.yaml')  # Auto-detects YAML
else:
    load_env()  # Auto-searches, finds .env
```

---

## ✅ Best Practices

### 1. Use Auto-Search for Development

```python
# ✅ Good: Let envdot find the config
load_env()
```

```python
# ❌ Avoid: Hard-coding paths
load_env('/absolute/path/to/.env')
```

---

### 2. Use Explicit Paths for Production

```python
# ✅ Good: Explicit config for production
import os

if os.getenv('ENV') == 'production':
    load_env('/etc/myapp/config.toml')
else:
    load_env()  # Auto-search for development
```

---

### 3. No Need to Specify Format

```python
# ✅ Good: Format auto-detected
load_env('config.toml')
```

```python
# ❌ Redundant: Format parameter not needed
load_env('config.toml', format='toml')
```

---

### 4. Priority Awareness

```python
# If you have multiple config files:
# ├── .env              ← Priority 1
# ├── config.toml       ← Priority 3
# └── config.json       ← Priority 7

load_env()  # Always loads .env first

# To load config.toml instead:
load_env('config.toml')  # Explicit path
```

---

## 🔍 Debug Auto-Detection

Enable debug mode to see which file is loaded:

```python
import os
os.environ['DEBUG'] = '1'

from envdot import load_env

load_env()
# Output: "Auto-detected config file: .env"
```

---

## 📦 Summary

| Feature | Description | Example |
|---------|-------------|---------|
| **Auto-Search** | Finds config files automatically | `load_env()` |
| **Auto-Detect** | Detects format from extension | `load_env('config.toml')` |
| **Priority Order** | `.env` → `.toml` → `.yaml` → `.json` → `.ini` | Sequential search |
| **No format= needed** | Extension determines format | All formats auto-detected |
| **Recursive Search** | Search subdirectories | `find_settings_recursive()` |

---

## 🎓 Key Takeaways

1. ✅ **`load_env()` auto-searches** for config files in priority order
2. ✅ **`load_env('file.ext')` auto-detects** format from extension
3. ✅ **NO `format=` parameter needed** - it's automatic!
4. ✅ **`.env` has highest priority** when auto-searching
5. ✅ **All standard formats supported** - .env, TOML, YAML, JSON, INI

---

## 🚀 Get Started

```bash
pip install envdot[full]
```

```python
from envdot import load_env, get_env

# That's literally all you need!
load_env()

# Now use your config
print(get_env('DATABASE_HOST'))
print(get_env('API_KEY'))
```

**Zero configuration. Zero hassle. Just works.** ✨