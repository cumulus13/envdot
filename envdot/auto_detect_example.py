#!/usr/bin/env python3

# File: envdot/auto_detect_example.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-12
# Description: Complete examples for auto-detection in envdot
# License: MIT

"""
Complete examples for auto-detection in envdot

Demonstrates:
1. load_env() without any arguments - auto-searches for config files
2. load_env('config.toml') - auto-detects format from extension
3. Priority order of auto-detection
4. Recursive search capabilities
"""

import os
from pathlib import Path
from envdot import load_env, get_env, DotEnv

# ============================================================================
# EXAMPLE 1: load_env() - Auto-Search Config Files
# ============================================================================

def example_auto_search():
    """
    Example: load_env() without arguments
    
    Auto-searches in priority order:
    1. .env (highest priority)
    2. .env.local
    3. config.toml (recommended)
    4. pyproject.toml
    5. config.yaml / config.yml
    6. config.json
    7. config.ini
    8. Dotfiles: .toml, .yaml, .yml, .json, .ini
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Auto-Search Config Files")
    print("="*70)
    
    # Scenario 1: Only .env exists
    print("\n--- Scenario 1: Only .env exists ---")
    Path('.env').write_text('TEST_VALUE=from_env')
    
    env = load_env()  # No arguments!
    print(f"✅ Auto-detected: .env")
    print(f"   TEST_VALUE = {get_env('TEST_VALUE')}")
    
    Path('.env').unlink()
    
    # Scenario 2: Only config.toml exists
    print("\n--- Scenario 2: Only config.toml exists ---")
    Path('config.toml').write_text('TEST_VALUE = "from_toml"')
    
    env = load_env()  # No arguments!
    print(f"✅ Auto-detected: config.toml")
    print(f"   TEST_VALUE = {get_env('TEST_VALUE')}")
    
    Path('config.toml').unlink()
    
    # Scenario 3: Multiple files - priority test
    print("\n--- Scenario 3: Multiple files exist (priority test) ---")
    Path('.env').write_text('TEST_VALUE=from_env')
    Path('config.toml').write_text('TEST_VALUE = "from_toml"')
    Path('config.json').write_text('{"TEST_VALUE": "from_json"}')
    
    env = load_env()  # No arguments!
    print(f"✅ Auto-detected: .env (highest priority)")
    print(f"   TEST_VALUE = {get_env('TEST_VALUE')}")
    print(f"   NOTE: .env has highest priority, so config.toml and config.json are ignored")
    
    # Cleanup
    Path('.env').unlink()
    Path('config.toml').unlink()
    Path('config.json').unlink()
    
    # Scenario 4: .env.local overrides .env
    print("\n--- Scenario 4: .env.local takes priority over .env ---")
    Path('.env').write_text('TEST_VALUE=from_env\nOTHER=value')
    Path('.env.local').write_text('TEST_VALUE=from_local')
    
    env = load_env()  # Loads .env first (highest priority)
    print(f"✅ Auto-detected: .env (loaded first)")
    print(f"   TEST_VALUE = {get_env('TEST_VALUE')}")
    print(f"   OTHER = {get_env('OTHER')}")
    
    # To load .env.local instead, remove .env first or use explicit path
    Path('.env').unlink()
    env = load_env()  # Now loads .env.local
    print(f"✅ Auto-detected: .env.local (after .env removed)")
    print(f"   TEST_VALUE = {get_env('TEST_VALUE')}")
    
    Path('.env.local').unlink()
    
    print("\n✅ Auto-search examples completed!")


# ============================================================================
# EXAMPLE 2: Auto-Detect Format from Extension
# ============================================================================

def example_auto_detect_format():
    """
    Example: load_env('config.toml') - auto-detects format
    
    Format detection rules:
    - .env → env format
    - .json → json format
    - .yaml, .yml → yaml format
    - .toml, .tml → toml format
    - .ini → ini format
    - Dotfiles: .toml, .json, etc. → detected by name
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Auto-Detect Format from Extension")
    print("="*70)
    
    # Test all formats
    test_cases = [
        # (filename, content, expected_format)
        ('.env', 'TEST_VALUE=env_format', 'env'),
        ('config.json', '{"TEST_VALUE": "json_format"}', 'json'),
        ('config.yaml', 'TEST_VALUE: yaml_format', 'yaml'),
        ('config.toml', 'TEST_VALUE = "toml_format"', 'toml'),
        ('config.ini', '[DEFAULT]\nTEST_VALUE = ini_format', 'ini'),
        # Dotfiles
        ('.json', '{"TEST_VALUE": "dotfile_json"}', 'json'),
        ('.toml', 'TEST_VALUE = "dotfile_toml"', 'toml'),
        ('.yaml', 'TEST_VALUE: dotfile_yaml', 'yaml'),
    ]
    
    for filename, content, expected_format in test_cases:
        print(f"\n--- Testing: {filename} ---")
        Path(filename).write_text(content)
        
        try:
            # Load without specifying format!
            env = load_env(filename)  # Auto-detects format from extension
            
            value = get_env('TEST_VALUE')
            print(f"✅ File: {filename}")
            print(f"   Detected format: {expected_format}")
            print(f"   TEST_VALUE = {value}")
            
        except ImportError as e:
            print(f"⚠️  Format {expected_format} not supported: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            Path(filename).unlink(missing_ok=True)
    
    print("\n✅ Auto-detect format examples completed!")


# ============================================================================
# EXAMPLE 3: Priority Order Demonstration
# ============================================================================

def example_priority_order():
    """
    Demonstrate priority order when multiple config files exist
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Priority Order Demonstration")
    print("="*70)
    
    print("\nCreating multiple config files with different values...")
    
    # Create all config files
    configs = {
        '.env': 'VALUE=from_env\nSOURCE=env',
        '.env.local': 'VALUE=from_env_local\nSOURCE=env_local',
        'config.toml': 'VALUE = "from_toml"\nSOURCE = "toml"',
        'pyproject.toml': 'VALUE = "from_pyproject"\nSOURCE = "pyproject"',
        'config.yaml': 'VALUE: from_yaml\nSOURCE: yaml',
        'config.json': '{"VALUE": "from_json", "SOURCE": "json"}',
        'config.ini': '[DEFAULT]\nVALUE = from_ini\nSOURCE = ini',
    }
    
    for filename, content in configs.items():
        Path(filename).write_text(content)
        print(f"   Created: {filename}")
    
    print("\n" + "-"*70)
    print("Loading with load_env() - which file wins?")
    print("-"*70)
    
    env = load_env()  # Auto-search
    
    value = get_env('VALUE')
    source = get_env('SOURCE')
    
    print(f"\n✅ Winner: {source}")
    print(f"   VALUE = {value}")
    print(f"   SOURCE = {source}")
    
    print("\n📋 Priority order (highest to lowest):")
    priority = [
        "1. .env (LOADED)",
        "2. .env.local",
        "3. config.toml",
        "4. pyproject.toml",
        "5. config.yaml",
        "6. config.json",
        "7. config.ini",
    ]
    for item in priority:
        print(f"   {item}")
    
    # Cleanup
    for filename in configs.keys():
        Path(filename).unlink(missing_ok=True)
    
    print("\n✅ Priority order demonstration completed!")


# ============================================================================
# EXAMPLE 4: Recursive Search
# ============================================================================

def example_recursive_search():
    """
    Demonstrate recursive search for config files
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Recursive Search")
    print("="*70)
    
    # Create nested directory structure
    dirs = ['subdir1', 'subdir1/subdir2']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Put config in nested directory
    Path('subdir1/subdir2/config.toml').write_text('NESTED_VALUE = "found_me"')
    
    print("\nDirectory structure:")
    print("   ./")
    print("   └── subdir1/")
    print("       └── subdir2/")
    print("           └── config.toml")
    
    print("\n--- Using recursive search ---")
    env = DotEnv()
    config_path = env.find_settings_recursive(start_path='.', max_depth=3)
    
    if config_path:
        print(f"✅ Found config: {config_path}")
        env.load(config_path)
        print(f"   NESTED_VALUE = {get_env('NESTED_VALUE')}")
    else:
        print("❌ No config found")
    
    # Cleanup
    import shutil
    shutil.rmtree('subdir1', ignore_errors=True)
    
    print("\n✅ Recursive search example completed!")


# ============================================================================
# EXAMPLE 5: Real-World Usage Patterns
# ============================================================================

def example_real_world_usage():
    """
    Real-world usage patterns
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Real-World Usage Patterns")
    print("="*70)
    
    # Pattern 1: Simple project - just load_env()
    print("\n--- Pattern 1: Simple Project ---")
    Path('.env').write_text('DATABASE_URL=postgres://localhost/mydb')
    
    # Just call load_env() - that's it!
    load_env()
    print(f"✅ DATABASE_URL = {get_env('DATABASE_URL')}")
    
    Path('.env').unlink()
    
    # Pattern 2: Python project with pyproject.toml
    print("\n--- Pattern 2: Python Project (pyproject.toml) ---")
    pyproject_content = """[project]
name = "myproject"
version = "1.0.0"

[tool.myproject]
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
"""
    Path('pyproject.toml').write_text(pyproject_content)
    
    load_env()  # Auto-detects pyproject.toml
    print(f"✅ Auto-detected: pyproject.toml")
    print(f"   PROJECT_NAME = {get_env('PROJECT_NAME', 'N/A')}")
    print(f"   TOOL_MYPROJECT_DATABASE_HOST = {get_env('TOOL_MYPROJECT_DATABASE_HOST', 'N/A')}")
    
    Path('pyproject.toml').unlink()
    
    # Pattern 3: Explicit file with auto-format detection
    print("\n--- Pattern 3: Explicit File (Auto-Format) ---")
    Path('custom.toml').write_text('CUSTOM_VALUE = "auto_detected"')
    
    load_env('custom.toml')  # Format auto-detected from .toml extension
    print(f"✅ Loaded: custom.toml (format auto-detected)")
    print(f"   CUSTOM_VALUE = {get_env('CUSTOM_VALUE')}")
    
    Path('custom.toml').unlink()
    
    # Pattern 4: Environment-specific configs
    print("\n--- Pattern 4: Environment-Specific Configs ---")
    Path('config.base.toml').write_text('APP_NAME = "MyApp"\nDEBUG = false')
    Path('.env.development').write_text('DEBUG=true\nDATABASE_HOST=localhost')
    
    # Load base config
    load_env('config.base.toml')
    print(f"Base config loaded:")
    print(f"   APP_NAME = {get_env('APP_NAME')}")
    print(f"   DEBUG = {get_env('DEBUG')}")
    
    # Override with environment-specific
    env = DotEnv()
    env.load('.env.development', override=True)
    print(f"\nAfter development overrides:")
    print(f"   DEBUG = {get_env('DEBUG')}")
    print(f"   DATABASE_HOST = {get_env('DATABASE_HOST')}")
    
    Path('config.base.toml').unlink()
    Path('.env.development').unlink()
    
    print("\n✅ Real-world usage patterns completed!")


# ============================================================================
# EXAMPLE 6: Format Detection Edge Cases
# ============================================================================

def example_edge_cases():
    """
    Edge cases in format detection
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Format Detection Edge Cases")
    print("="*70)
    
    # Edge case 1: File with no extension defaults to .env
    print("\n--- Edge Case 1: No Extension ---")
    Path('envfile').write_text('NO_EXT_VALUE=detected_as_env')
    
    env = load_env('envfile')
    print(f"✅ File with no extension → defaults to .env format")
    print(f"   NO_EXT_VALUE = {get_env('NO_EXT_VALUE')}")
    
    Path('envfile').unlink()
    
    # Edge case 2: Dotfiles
    print("\n--- Edge Case 2: Dotfiles ---")
    dotfiles = {
        '.toml': 'DOTFILE_TOML = "detected"',
        '.json': '{"DOTFILE_JSON": "detected"}',
        '.yaml': 'DOTFILE_YAML: detected',
    }
    
    for filename, content in dotfiles.items():
        Path(filename).write_text(content)
        try:
            env = load_env(filename)
            key = f"DOTFILE_{filename[1:].upper()}"
            print(f"✅ {filename} → auto-detected as {filename[1:]} format")
        except ImportError:
            print(f"⚠️  {filename} → format not supported")
        finally:
            Path(filename).unlink(missing_ok=True)
    
    print("\n✅ Edge cases completed!")


# ============================================================================
# Main - Run All Examples
# ============================================================================

def main():
    """Run all auto-detection examples"""
    print("\n" + "="*70)
    print("ENVDOT AUTO-DETECTION EXAMPLES")
    print("Comprehensive guide to auto-search and auto-detect features")
    print("="*70)
    
    examples = [
        ("Auto-Search Config Files", example_auto_search),
        ("Auto-Detect Format", example_auto_detect_format),
        ("Priority Order", example_priority_order),
        ("Recursive Search", example_recursive_search),
        ("Real-World Usage", example_real_world_usage),
        ("Edge Cases", example_edge_cases),
    ]
    
    for title, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {title}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✅ load_env() - Auto-searches in priority order:
   1. .env (highest priority)
   2. .env.local
   3. config.toml (recommended)
   4. pyproject.toml
   5. config.yaml/yml
   6. config.json
   7. config.ini
   8. Dotfiles: .toml, .yaml, .json, .ini

✅ load_env('config.toml') - Auto-detects format from extension:
   - .env → env format
   - .toml → toml format
   - .yaml/.yml → yaml format
   - .json → json format
   - .ini → ini format

✅ NO need to specify format= parameter!
✅ NO need to specify filepath if using standard names!

Just call: load_env()
""")
    print("="*70)


if __name__ == "__main__":
    main()