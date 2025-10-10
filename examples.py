"""Example usage of dot-env package"""

from dotenv import DotEnv, load_env, get_env, set_env

def example_basic_usage():
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
    load_env('.env')
    
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
    
    from dotenv import FileNotFoundError, ParseError, TypeConversionError
    
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