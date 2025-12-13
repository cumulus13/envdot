#!/usr/bin/env python3
"""
Complete examples for using envdot with all supported formats
.env, JSON, YAML, INI, and TOML
"""

import os
from pathlib import Path
from envdot import load_env, get_env, set_env, save_env, DotEnv

# ============================================================================
# EXAMPLE 1: Using .env file (Most Common)
# ============================================================================

def example_dotenv():
    """Example using .env file"""
    print("\n" + "="*70)
    print("EXAMPLE 1: .env File")
    print("="*70)
    
    # Create sample .env file
    env_content = """
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=admin
DATABASE_PASSWORD=secret123

# Application Settings
APP_NAME="My Application"
DEBUG=true
MAX_CONNECTIONS=100
TIMEOUT=30.5

# Feature Flags
ENABLE_CACHE=true
ENABLE_AUTH=false
"""
    
    Path('.env.example').write_text(env_content)
    
    # Load .env file
    env = load_env('.env.example')
    
    # Access values (auto-typed!)
    print(f"Database Host: {get_env('DATABASE_HOST')}")  # str
    print(f"Database Port: {get_env('DATABASE_PORT')} (type: {type(get_env('DATABASE_PORT')).__name__})")  # int
    print(f"Debug Mode: {get_env('DEBUG')} (type: {type(get_env('DEBUG')).__name__})")  # bool
    print(f"Timeout: {get_env('TIMEOUT')} (type: {type(get_env('TIMEOUT')).__name__})")  # float
    
    # Modify and save
    set_env('DATABASE_PORT', 5433)
    set_env('NEW_FEATURE', 'enabled')
    save_env('.env.example')
    
    print("\n✅ .env file loaded and modified successfully!")


# ============================================================================
# EXAMPLE 2: Using JSON file
# ============================================================================

def example_json():
    """Example using JSON file"""
    print("\n" + "="*70)
    print("EXAMPLE 2: JSON File")
    print("="*70)
    
    # Create sample JSON file
    json_content = """{
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
}"""
    
    Path('config.json').write_text(json_content)
    
    # Load JSON file
    env = load_env('config.json')
    
    # Access flattened nested keys
    print(f"Database Host: {get_env('DATABASE_HOST')}")
    print(f"Database Port: {get_env('DATABASE_PORT')}")
    print(f"Username: {get_env('DATABASE_CREDENTIALS_USERNAME')}")
    print(f"App Name: {get_env('APP_NAME')}")
    print(f"Debug: {get_env('APP_DEBUG')}")
    
    # Array access
    print(f"Feature 0: {get_env('FEATURES_0')}")
    print(f"Feature 1: {get_env('FEATURES_1')}")
    print(f"Feature 2: {get_env('FEATURES_2')}")
    
    # Show all loaded keys
    print("\nAll loaded keys:")
    for key in env.keys():
        print(f"  {key} = {get_env(key)}")
    
    print("\n✅ JSON file loaded successfully!")


# ============================================================================
# EXAMPLE 3: Using YAML file
# ============================================================================

def example_yaml():
    """Example using YAML file"""
    print("\n" + "="*70)
    print("EXAMPLE 3: YAML File")
    print("="*70)
    
    # Create sample YAML file
    yaml_content = """
# Application Configuration
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

server:
  primary:
    host: server1.example.com
    port: 8080
  secondary:
    host: server2.example.com
    port: 8081

features:
  - auth
  - cache
  - logging
"""
    
    Path('config.yaml').write_text(yaml_content)
    
    try:
        # Load YAML file
        env = load_env('config.yaml')
        
        # Access nested values
        print(f"Database Host: {get_env('DATABASE_HOST')}")
        print(f"Username: {get_env('DATABASE_CREDENTIALS_USERNAME')}")
        print(f"Primary Server: {get_env('SERVER_PRIMARY_HOST')}:{get_env('SERVER_PRIMARY_PORT')}")
        print(f"Secondary Server: {get_env('SERVER_SECONDARY_HOST')}:{get_env('SERVER_SECONDARY_PORT')}")
        
        # Array access
        print(f"Features: {get_env('FEATURES_0')}, {get_env('FEATURES_1')}, {get_env('FEATURES_2')}")
        
        print("\n✅ YAML file loaded successfully!")
    except ImportError:
        print("\n⚠️  PyYAML not installed. Install with: pip install pyyaml")


# ============================================================================
# EXAMPLE 4: Using INI file
# ============================================================================

def example_ini():
    """Example using INI file"""
    print("\n" + "="*70)
    print("EXAMPLE 4: INI File")
    print("="*70)
    
    # Create sample INI file
    ini_content = """[DEFAULT]
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
type = redis
"""
    
    Path('config.ini').write_text(ini_content)
    
    # Load INI file
    env = load_env('config.ini')
    
    # Access with section prefixes
    print(f"App Name: {get_env('APP_NAME')}")  # From DEFAULT
    print(f"Version: {get_env('VERSION')}")    # From DEFAULT
    print(f"Database Host: {get_env('DATABASE_HOST')}")     # From [database]
    print(f"Database Port: {get_env('DATABASE_PORT')}")     # From [database]
    print(f"Server Host: {get_env('SERVER_HOST')}")         # From [server]
    print(f"Server Port: {get_env('SERVER_PORT')}")         # From [server]
    print(f"Cache Enabled: {get_env('CACHE_ENABLED')}")     # From [cache]
    print(f"Cache TTL: {get_env('CACHE_TTL')}")             # From [cache]
    
    print("\n✅ INI file loaded successfully!")


# ============================================================================
# EXAMPLE 5: Using TOML file (Recommended for Python projects)
# ============================================================================

def example_toml():
    """Example using TOML file"""
    print("\n" + "="*70)
    print("EXAMPLE 5: TOML File (Recommended!)")
    print("="*70)
    
    # Create sample TOML file
    toml_content = """# Application Configuration
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
"""
    
    Path('config.toml').write_text(toml_content)
    
    try:
        # Load TOML file
        env = load_env('config.toml')
        
        # Access root level
        print(f"Title: {get_env('TITLE')}")
        print(f"Version: {get_env('VERSION')}")
        
        # Access nested sections
        print(f"Database: {get_env('DATABASE_HOST')}:{get_env('DATABASE_PORT')}")
        print(f"Credentials: {get_env('DATABASE_CREDENTIALS_USERNAME')}")
        
        # Server config
        print(f"Server: {get_env('SERVER_HOST')}:{get_env('SERVER_PORT')}")
        print(f"Workers: {get_env('SERVER_WORKERS')}")
        print(f"Debug: {get_env('SERVER_DEBUG')}")
        
        # Cache config
        print(f"Cache: {get_env('CACHE_TYPE')} (TTL: {get_env('CACHE_TTL')}s)")
        
        # Array of tables
        print(f"Feature 0: {get_env('FEATURES_0_NAME')} - Enabled: {get_env('FEATURES_0_ENABLED')}")
        print(f"Feature 1: {get_env('FEATURES_1_NAME')} - Enabled: {get_env('FEATURES_1_ENABLED')}")
        
        # Deep nesting
        print(f"Logging: {get_env('LOGGING_LEVEL')} -> {get_env('LOGGING_HANDLERS_FILE')}")
        
        print("\n✅ TOML file loaded successfully!")
    except ImportError as e:
        print(f"\n⚠️  TOML support not available: {e}")
        print("Install with: pip install tomli tomli-w (Python < 3.11)")


# ============================================================================
# EXAMPLE 6: Format Conversion
# ============================================================================

def example_format_conversion():
    """Example of converting between formats"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Format Conversion")
    print("="*70)
    
    # Load from JSON
    json_content = """{
  "database": {
    "host": "localhost",
    "port": 5432
  },
  "app": {
    "name": "My App",
    "debug": true
  }
}"""
    Path('source.json').write_text(json_content)
    
    # Load JSON and save as different formats
    env = load_env('source.json')
    
    # Save as .env
    save_env('converted.env', format='env')
    print("✅ Converted JSON → .env")
    
    # Save as YAML (if available)
    try:
        save_env('converted.yaml', format='yaml')
        print("✅ Converted JSON → YAML")
    except ImportError:
        print("⚠️  YAML conversion skipped (PyYAML not installed)")
    
    # Save as INI
    save_env('converted.ini', format='ini')
    print("✅ Converted JSON → INI")
    
    # Save as TOML (if available)
    try:
        save_env('converted.toml', format='toml')
        print("✅ Converted JSON → TOML")
    except ImportError:
        print("⚠️  TOML conversion skipped (tomli-w not installed)")
    
    print("\n✅ Format conversion completed!")


# ============================================================================
# EXAMPLE 7: Advanced Usage - Type Casting
# ============================================================================

def example_type_casting():
    """Example of explicit type casting"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Type Casting")
    print("="*70)
    
    # Create .env with various types
    env_content = """
PORT=8080
DEBUG=true
RATIO=0.75
ALLOWED_HOSTS=localhost, 127.0.0.1, example.com
MAX_RETRIES=5
"""
    Path('.env.types').write_text(env_content)
    env = load_env('.env.types')
    
    # Auto-detected types
    print("Auto-detected types:")
    print(f"  PORT: {get_env('PORT')} (type: {type(get_env('PORT')).__name__})")
    print(f"  DEBUG: {get_env('DEBUG')} (type: {type(get_env('DEBUG')).__name__})")
    print(f"  RATIO: {get_env('RATIO')} (type: {type(get_env('RATIO')).__name__})")
    
    # Explicit type casting
    print("\nExplicit type casting:")
    port = get_env('PORT', cast_type=int)
    print(f"  PORT as int: {port} (type: {type(port).__name__})")
    
    hosts = get_env('ALLOWED_HOSTS', cast_type=list)
    print(f"  ALLOWED_HOSTS as list: {hosts} (type: {type(hosts).__name__})")
    
    retries = get_env('MAX_RETRIES', cast_type=int)
    print(f"  MAX_RETRIES as int: {retries} (type: {type(retries).__name__})")
    
    print("\n✅ Type casting examples completed!")


# ============================================================================
# EXAMPLE 8: Using os.getenv() with Auto-typing
# ============================================================================

def example_os_getenv_typed():
    """Example of automatic os.getenv() replacement"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Auto-typed os.getenv()")
    print("="*70)
    
    # Load with auto_replace_getenv=True (default)
    env_content = """
API_PORT=9000
API_DEBUG=true
API_TIMEOUT=5.5
"""
    Path('.env.api').write_text(env_content)
    env = load_env('.env.api', auto_replace_getenv=True)
    
    # Now os.getenv() returns typed values!
    import os
    
    port = os.getenv('API_PORT')
    debug = os.getenv('API_DEBUG')
    timeout = os.getenv('API_TIMEOUT')
    
    print(f"API Port: {port} (type: {type(port).__name__})")      # int, not str!
    print(f"API Debug: {debug} (type: {type(debug).__name__})")   # bool, not str!
    print(f"API Timeout: {timeout} (type: {type(timeout).__name__})")  # float, not str!
    
    # Also available: os.save_env()
    os.setenv('NEW_KEY', 'new_value')
    os.save_env('.env.api')
    
    print("\n✅ Auto-typed os.getenv() working!")


# ============================================================================
# EXAMPLE 9: Attribute-style Access
# ============================================================================

def example_attribute_access():
    """Example of using attribute-style access"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Attribute-style Access")
    print("="*70)
    
    # Create config
    env_content = """
SERVER_HOST=localhost
SERVER_PORT=8080
SERVER_DEBUG=true
"""
    Path('.env.server').write_text(env_content)
    
    # Load and use attribute access
    env = DotEnv('.env.server')
    
    # Access like attributes
    print(f"Server: {env.SERVER_HOST}:{env.SERVER_PORT}")
    print(f"Debug: {env.SERVER_DEBUG}")
    
    # Set like attributes (auto-saves!)
    env.SERVER_WORKERS = 4
    env.SERVER_TIMEOUT = 30
    
    print(f"Workers: {env.SERVER_WORKERS}")
    print(f"Timeout: {env.SERVER_TIMEOUT}")
    
    print("\n✅ Attribute-style access working!")


# ============================================================================
# EXAMPLE 10: Production Environment Setup
# ============================================================================

def example_production_setup():
    """Example of production environment setup"""
    print("\n" + "="*70)
    print("EXAMPLE 10: Production Environment Setup")
    print("="*70)
    
    # Base configuration (development)
    base_config = """
[app]
name = My Application
version = 1.0.0

[database]
host = localhost
port = 5432
pool_size = 10

[logging]
level = DEBUG
"""
    Path('config.base.ini').write_text(base_config)
    
    # Production overrides
    prod_config = """
DATABASE_HOST=prod-db.example.com
DATABASE_POOL_SIZE=50
LOGGING_LEVEL=INFO
ENABLE_MONITORING=true
"""
    Path('config.prod.env').write_text(prod_config)
    
    # Load base config
    env = load_env('config.base.ini')
    print("Loaded base configuration:")
    print(f"  Database: {get_env('DATABASE_HOST')}:{get_env('DATABASE_PORT')}")
    print(f"  Pool Size: {get_env('DATABASE_POOL_SIZE')}")
    print(f"  Log Level: {get_env('LOGGING_LEVEL')}")
    
    # Override with production settings
    env.load('config.prod.env', override=True)
    print("\nAfter production overrides:")
    print(f"  Database: {get_env('DATABASE_HOST')}:{get_env('DATABASE_PORT')}")
    print(f"  Pool Size: {get_env('DATABASE_POOL_SIZE')}")
    print(f"  Log Level: {get_env('LOGGING_LEVEL')}")
    print(f"  Monitoring: {get_env('ENABLE_MONITORING')}")
    
    print("\n✅ Production setup completed!")


# ============================================================================
# Main Function - Run All Examples
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("ENVDOT - Complete Usage Examples")
    print("Multi-format Configuration Management (.env, JSON, YAML, INI, TOML)")
    print("="*70)
    
    examples = [
        ("Basic .env File", example_dotenv),
        ("JSON File with Nesting", example_json),
        ("YAML File", example_yaml),
        ("INI File with Sections", example_ini),
        ("TOML File (Recommended)", example_toml),
        ("Format Conversion", example_format_conversion),
        ("Type Casting", example_type_casting),
        ("Auto-typed os.getenv()", example_os_getenv_typed),
        ("Attribute-style Access", example_attribute_access),
        ("Production Setup", example_production_setup),
    ]
    
    for title, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {title}: {e}")
            import traceback
            traceback.print_exc()
    
    # Cleanup
    print("\n" + "="*70)
    print("Cleaning up example files...")
    cleanup_files = [
        '.env.example', 'config.json', 'config.yaml', 'config.ini', 'config.toml',
        'source.json', 'converted.env', 'converted.yaml', 'converted.ini', 'converted.toml',
        '.env.types', '.env.api', '.env.server', 'config.base.ini', 'config.prod.env'
    ]
    
    for file in cleanup_files:
        try:
            Path(file).unlink(missing_ok=True)
        except:
            pass
    
    print("✅ Cleanup completed!")
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()