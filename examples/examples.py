"""Example usage of dot-env package"""

from envdot import DotEnv, load_env, get_env, set_env
from envdot import getenv_typed, getenv_int, getenv_bool, getenv_float, getenv_str, patch_os_module
import os


def example_helpers_basic():
    """Using helper functions for typed os.getenv()"""
    print("=== Helper Functions - Basic Usage ===")
    
    # Load environment
    load_env('.env')
    
    # Problem: os.getenv() returns strings
    port_str = os.getenv('PORT')
    print(f"os.getenv('PORT'): {port_str} ({type(port_str).__name__})")
    
    # Solution 1: Use getenv_typed() - auto-detects type
    port = getenv_typed('PORT')
    print(f"getenv_typed('PORT'): {port} ({type(port).__name__})")
    
    # Solution 2: Use specific type helpers
    port_int = getenv_int('PORT', default=8000)
    debug = getenv_bool('DEBUG', default=False)
    timeout = getenv_float('TIMEOUT', default=30.0)
    app_name = getenv_str('APP_NAME', default='MyApp')
    
    print(f"getenv_int('PORT'): {port_int} ({type(port_int).__name__})")
    print(f"getenv_bool('DEBUG'): {debug} ({type(debug).__name__})")
    print(f"getenv_float('TIMEOUT'): {timeout} ({type(timeout).__name__})")
    print(f"getenv_str('APP_NAME'): {app_name} ({type(app_name).__name__})")
    print()


def example_helpers_comparison():
    """Comparison: os.getenv() vs helper functions"""
    print("=== Comparison: Standard vs Typed ===")
    
    # Set some test values
    os.environ['DEBUGGER_SERVER'] = '50002'
    os.environ['ENABLE_FEATURE'] = 'true'
    os.environ['API_TIMEOUT'] = '30.5'
    
    print("--- Using os.getenv() (returns strings) ---")
    server = os.getenv('DEBUGGER_SERVER')
    feature = os.getenv('ENABLE_FEATURE')
    timeout = os.getenv('API_TIMEOUT')
    print(f"DEBUGGER_SERVER: {server!r} ({type(server).__name__})")
    print(f"ENABLE_FEATURE: {feature!r} ({type(feature).__name__})")
    print(f"API_TIMEOUT: {timeout!r} ({type(timeout).__name__})")
    
    print("\n--- Using getenv_typed() (auto-detects types) ---")
    server = getenv_typed('DEBUGGER_SERVER')
    feature = getenv_typed('ENABLE_FEATURE')
    timeout = getenv_typed('API_TIMEOUT')
    print(f"DEBUGGER_SERVER: {server!r} ({type(server).__name__})")
    print(f"ENABLE_FEATURE: {feature!r} ({type(feature).__name__})")
    print(f"API_TIMEOUT: {timeout!r} ({type(timeout).__name__})")
    print()


def example_helpers_with_defaults():
    """Using helpers with default values"""
    print("=== Helpers with Default Values ===")
    
    # Get with defaults for missing keys
    max_workers = getenv_int('MAX_WORKERS', default=4)
    cache_enabled = getenv_bool('CACHE_ENABLED', default=True)
    retry_delay = getenv_float('RETRY_DELAY', default=1.5)
    api_key = getenv_str('API_KEY', default='default-key')
    
    print(f"MAX_WORKERS: {max_workers} (default: 4)")
    print(f"CACHE_ENABLED: {cache_enabled} (default: True)")
    print(f"RETRY_DELAY: {retry_delay} (default: 1.5)")
    print(f"API_KEY: {api_key} (default: 'default-key')")
    print()


def example_patch_os_module():
    """Using monkey-patch for os module"""
    print("=== Monkey-Patching os Module ===")
    
    # Patch os module to add typed methods
    patch_os_module()
    
    # Set some test values
    os.environ['PORT'] = '8080'
    os.environ['DEBUG'] = 'true'
    
    # Now os module has typed methods
    print("After patching, os module has new methods:")
    print(f"  - os.getenv_typed()")
    print(f"  - os.getenv_int()")
    print(f"  - os.getenv_bool()")
    print(f"  - os.getenv_float()")
    print(f"  - os.getenv_str()")
    print(f"  - os.setenv_typed()")
    
    # Use the new methods
    port = os.getenv_typed('PORT')
    debug = os.getenv_bool('DEBUG')
    
    print(f"\nos.getenv_typed('PORT'): {port} ({type(port).__name__})")
    print(f"os.getenv_bool('DEBUG'): {debug} ({type(debug).__name__})")
    
    # Set typed values
    os.setenv_typed('NEW_PORT', 9000)
    os.setenv_typed('NEW_DEBUG', False)
    
    print(f"\nAfter os.setenv_typed('NEW_PORT', 9000):")
    print(f"  os.getenv('NEW_PORT'): {os.getenv('NEW_PORT')!r}")
    print(f"  os.getenv_int('NEW_PORT'): {os.getenv_int('NEW_PORT')}")
    print()


def example_real_world_with_helpers():
    """Real-world example using helpers"""
    print("=== Real-World Application with Helpers ===")
    
    from dotenv import setenv_typed
    
    # Set configuration using typed values
    setenv_typed('DB_PORT', 5432)
    setenv_typed('DB_POOL_SIZE', 10)
    setenv_typed('DB_TIMEOUT', 30.0)
    setenv_typed('DB_SSL_ENABLED', True)
    
    # Load configuration with proper types
    config = {
        'host': getenv_str('DB_HOST', default='localhost'),
        'port': getenv_int('DB_PORT', default=5432),
        'pool_size': getenv_int('DB_POOL_SIZE', default=5),
        'timeout': getenv_float('DB_TIMEOUT', default=10.0),
        'ssl_enabled': getenv_bool('DB_SSL_ENABLED', default=False),
    }
    
    print("Database Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value} ({type(value).__name__})")
    print()


def example_all_import_methods():
    """Show all ways to import and use helpers"""
    print("=== All Import Methods ===")
    
    print("Method 1 - Import specific functions:")
    print("  from dotenv import getenv_typed, getenv_int")
    print("  port = getenv_int('PORT')")
    print()
    
    print("Method 2 - Import all from helpers:")
    print("  from dotenv.helpers import *")
    print("  port = getenv_int('PORT')")
    print()
    
    print("Method 3 - Import helpers module:")
    print("  from dotenv import helpers")
    print("  port = helpers.getenv_int('PORT')")
    print()
    
    print("Method 4 - Patch os module:")
    print("  from dotenv import patch_os_module")
    print("  patch_os_module()")
    print("  port = os.getenv_int('PORT')")
    print()
    """Basic usage example"""
    print("=== Basic Usage ===")
    
    # Create and load from .env file
    env = DotEnv('.env')
    
    # Get values with automatic type detection
    debug = env.get('DEBUG')
    port = env.get('PORT')
    timeout = env.get('TIMEOUT')
    
    print(f"DEBUG: {debug} (type: {type(debug).__name__})")
    print(f"PORT: {port} (type: {type(port).__name__})")
    print(f"TIMEOUT: {timeout} (type: {type(timeout).__name__})")
    print()


def example_convenience_functions():
    """Using convenience functions"""
    print("=== Convenience Functions ===")
    
    # Load environment
    load_env('.env.example')
    
    # Get values
    app_name = get_env('APP_NAME', default='MyApp')
    max_conn = get_env('MAX_CONNECTIONS', default=10)
    
    print(f"App Name: {app_name}")
    print(f"Max Connections: {max_conn}")
    
    # Set new values
    set_env('NEW_FEATURE', True)
    set_env('VERSION', '1.0.0')
    
    print()


def example_multiple_formats():
    """Working with different file formats"""
    print("=== Multiple Format Support ===")
    
    # Load from JSON
    env_json = DotEnv('config.json')
    print(f"Loaded from JSON: {len(env_json.all())} variables")
    
    # Load from YAML
    env_yaml = DotEnv('config.yaml')
    print(f"Loaded from YAML: {len(env_yaml.all())} variables")
    
    # Load from INI
    env_ini = DotEnv('config.ini')
    print(f"Loaded from INI: {len(env_ini.all())} variables")
    
    # Convert between formats
    env = DotEnv('.env')
    env.save('config.json')  # Save as JSON
    env.save('config.yaml')  # Save as YAML
    print("Converted .env to JSON and YAML formats")
    print()


def example_type_casting():
    """Explicit type casting examples"""
    print("=== Type Casting ===")
    
    env = DotEnv('.env')
    
    # Auto-detected types
    port = env.get('PORT')
    print(f"Auto: PORT = {port} ({type(port).__name__})")
    
    # Force string type
    port_str = env.get('PORT', cast_type=str)
    print(f"Forced string: PORT = {port_str} ({type(port_str).__name__})")
    
    # Force integer type
    timeout = env.get('TIMEOUT', cast_type=int)
    print(f"Forced int: TIMEOUT = {timeout} ({type(timeout).__name__})")
    
    # Boolean casting
    debug = env.get('DEBUG', cast_type=bool)
    print(f"Boolean: DEBUG = {debug} ({type(debug).__name__})")
    print()


def example_method_chaining():
    """Method chaining for fluent API"""
    print("=== Method Chaining ===")
    
    env = (DotEnv('.env')
           .load()
           .set('CHAIN_KEY_1', 'value1')
           .set('CHAIN_KEY_2', 123)
           .set('CHAIN_KEY_3', True))
    
    print("Set 3 keys using method chaining")
    print(f"CHAIN_KEY_1: {env.get('CHAIN_KEY_1')}")
    print(f"CHAIN_KEY_2: {env.get('CHAIN_KEY_2')}")
    print(f"CHAIN_KEY_3: {env.get('CHAIN_KEY_3')}")
    print()


def example_dictionary_access():
    """Dictionary-style access"""
    print("=== Dictionary-Style Access ===")
    
    env = DotEnv('.env')
    
    # Get using []
    app_name = env['APP_NAME']
    print(f"Get: APP_NAME = {app_name}")
    
    # Set using []
    env['NEW_KEY'] = 'new_value'
    env['ANOTHER_KEY'] = 999
    print("Set: NEW_KEY and ANOTHER_KEY")
    
    # Check existence
    if 'APP_NAME' in env:
        print("APP_NAME exists")
    
    # Get all keys
    print(f"Total keys: {len(env.keys())}")
    print()


def example_nested_json_yaml():
    """Handling nested structures in JSON/YAML"""
    print("=== Nested Structures ===")
    
    # Example JSON with nested structure
    json_content = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret"
            }
        },
        "features": ["auth", "api", "webhooks"]
    }
    
    # This would be flattened to:
    # DATABASE_HOST = localhost
    # DATABASE_PORT = 5432
    # DATABASE_CREDENTIALS_USERNAME = admin
    # DATABASE_CREDENTIALS_PASSWORD = secret
    # FEATURES_0 = auth
    # FEATURES_1 = api
    # FEATURES_2 = webhooks
    
    print("Nested JSON/YAML structures are automatically flattened")
    print("Example flattened keys:")
    print("  DATABASE_HOST")
    print("  DATABASE_PORT")
    print("  DATABASE_CREDENTIALS_USERNAME")
    print("  FEATURES_0")
    print()


def example_default_values():
    """Using default values"""
    print("=== Default Values ===")
    
    env = DotEnv('.env')
    
    # Existing key
    port = env.get('PORT', default=3000)
    print(f"PORT (exists): {port}")
    
    # Non-existing key with default
    timeout = env.get('TIMEOUT', default=30)
    print(f"TIMEOUT (with default): {timeout}")
    
    # Non-existing key without default
    missing = env.get('MISSING_KEY')
    print(f"MISSING_KEY (no default): {missing}")
    print()


def example_os_environ_integration():
    """Integration with os.environ"""
    print("=== OS Environment Integration ===")
    
    import os
    
    env = DotEnv('.env')
    
    # Load applies to os.environ by default
    env.load(apply_to_os=True)
    print("Loaded to os.environ")
    
    # Access via os.environ
    if 'PORT' in os.environ:
        print(f"PORT in os.environ: {os.environ['PORT']}")
    
    # Set without applying to os.environ
    env.set('INTERNAL_KEY', 'value', apply_to_os=False)
    print("Set INTERNAL_KEY (not in os.environ)")
    
    # Verify it's not in os.environ
    print(f"INTERNAL_KEY in os.environ: {'INTERNAL_KEY' in os.environ}")
    print()


def example_save_and_load():
    """Save and load operations"""
    print("=== Save and Load ===")
    
    # Create new environment
    env = DotEnv(auto_load=False)
    
    # Set some values
    env.set('APP_NAME', 'MyApplication')
    env.set('VERSION', '2.0.0')
    env.set('DEBUG', False)
    env.set('MAX_WORKERS', 4)
    env.set('TIMEOUT', 60.5)
    
    # Save to different formats
    env.save('output.env')
    env.save('output.json')
    print("Saved to output.env and output.json")
    
    # Load from saved file
    env2 = DotEnv('output.json')
    print(f"Loaded {len(env2.all())} variables from output.json")
    
    # Display loaded values
    for key, value in env2.all().items():
        print(f"  {key} = {value} ({type(value).__name__})")
    print()


def example_clear_and_delete():
    """Clear and delete operations"""
    print("=== Clear and Delete ===")
    
    env = DotEnv('.env')
    print(f"Initial keys: {len(env.keys())}")
    
    # Delete specific key
    env.delete('TEMP_KEY')
    print("Deleted TEMP_KEY")
    
    # Clear all (keeping os.environ)
    env.clear(clear_os=False)
    print(f"After clear: {len(env.keys())} keys")
    print()


def example_error_handling():
    """Error handling examples"""
    print("=== Error Handling ===")
    
    from envdot import FileNotFoundError, ParseError, TypeConversionError
    
    try:
        env = DotEnv('nonexistent.env')
        env.load()
    except FileNotFoundError as e:
        print(f"Caught FileNotFoundError: {e}")
    
    try:
        env = DotEnv('.env')
        # Try to cast incompatible type
        value = env.get('APP_NAME', cast_type=int)
    except TypeConversionError as e:
        print(f"Caught TypeConversionError: {e}")
    
    print()


def example_real_world_app():
    """Real-world application example"""
    print("=== Real-World Application Example ===")
    
    # Load configuration
    env = DotEnv('.env')
    
    # Database configuration
    db_config = {
        'host': env.get('DB_HOST', default='localhost'),
        'port': env.get('DB_PORT', default=5432),
        'database': env.get('DB_NAME', default='myapp'),
        'username': env.get('DB_USER', default='postgres'),
        'password': env.get('DB_PASSWORD'),
    }
    
    # Application settings
    app_config = {
        'debug': env.get('DEBUG', default=False),
        'port': env.get('PORT', default=8000),
        'workers': env.get('WORKERS', default=4),
        'timeout': env.get('TIMEOUT', default=30.0),
    }
    
    # Feature flags
    features = {
        'enable_api': env.get('FEATURE_API', default=True),
        'enable_webhooks': env.get('FEATURE_WEBHOOKS', default=False),
        'enable_cache': env.get('FEATURE_CACHE', default=True),
    }
    
    print("Database Config:", db_config)
    print("Application Config:", app_config)
    print("Feature Flags:", features)
    print()


if __name__ == '__main__':
    print("DOT-ENV Package Examples\n")
    
    # Run all examples
    examples = [
        example_basic_usage,
        example_convenience_functions,
        example_multiple_formats,
        example_type_casting,
        example_method_chaining,
        example_dictionary_access,
        example_nested_json_yaml,
        example_default_values,
        example_os_environ_integration,
        example_save_and_load,
        example_clear_and_delete,
        example_error_handling,
        example_real_world_app,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}\n")