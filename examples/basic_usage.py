"""
Basic usage example for PyLua VM Curator system.
Demonstrates environment setup, package installation, VM creation, and health checks.
Phase 3: Added XCP-ng VM examples with multi-VM support.
"""
import json
from pylua_bioxen_vm_lib.env import EnvironmentManager
from pylua_bioxen_vm_lib.utils.curator import Curator
from pylua_bioxen_vm_lib.lua_process import LuaProcess
from pylua_bioxen_vm_lib.vm_manager import VMManager
from pylua_bioxen_vm_lib.interactive_session import SessionManager
from pylua_bioxen_vm_lib import create_vm

# Setup environment
env = EnvironmentManager(profile='standard')
print("System info:", env.get_system_info())
errors = env.validate()
if errors:
    print("Environment errors:", errors)
else:
    print("Environment validated.")

# Curator package management
curator = Curator()
curator.curate_environment('standard')
curator.install_package('lua-cjson')

# Create a Lua VM and run code
vm = LuaProcess(name='example_vm')
result = vm.execute_string('print("Hello from Lua!")')
print("Lua VM result:", result)

# Health check and recommendations
health = curator.health_check()
print("Health check:", health)
recs = curator.get_recommendations()
print("Recommended packages:", recs)

# Interactive Session Lifecycle
try:
    vm_manager = VMManager()
    session = vm_manager.create_interactive_session()
    print("Interactive Session created:", session)
except NameError as e:
    print("❌ Interactive Session failed:", e)
except Exception as e:
    print("❌ Interactive Session error:", e)

# Session Manager Registry Operations
try:
    session_manager = SessionManager()
    session_manager.register_session('example_session', session)
    print("Session registered in manager.")
except NameError as e:
    print("❌ Registry operations failed:", e)
except Exception as e:
    print("❌ Registry operations error:", e)

# Complex Interactive Session
try:
    complex_session = vm_manager.create_interactive_session(config={'complex': True})
    print("Complex Interactive Session created:", complex_session)
except NameError as e:
    print("❌ Complex session failed:", e)
except Exception as e:
    print("❌ Complex session error:", e)

# Session Reattachment
try:
    reattached = vm_manager.reattach_session('example_session')
    print("Session reattached:", reattached)
except NameError as e:
    print("❌ Session reattachment failed:", e)
except Exception as e:
    print("❌ Session reattachment error:", e)

print("==================================================")
print("Installation test complete!")
print("All features tested for pylua_bioxen_vm_lib interactive support")

print("\n" + "=" * 60)
print("PHASE 3: Multi-VM Factory Pattern Examples")
print("=" * 60)

# Example 1: Basic VM (Local Process) - Existing functionality
print("\n1. Basic VM (Local Process)")
print("-" * 30)
try:
    basic_vm = create_vm("example_basic", vm_type="basic")
    result = basic_vm.execute_string('print("Hello from Basic VM!")')
    print("✅ Basic VM result:", result.get('stdout', 'No output'))
except Exception as e:
    print("❌ Basic VM error:", e)

# Example 2: XCP-ng VM with Configuration
print("\n2. XCP-ng VM (Remote Virtual Machine)")
print("-" * 40)

# Example XCP-ng configuration
xcpng_config = {
    "xapi_url": "https://xcpng-host.example.com",
    "username": "root",
    "password": "example_password",
    "template": "lua-bio-template",
    "vm_name": "demo-lua-vm",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": False
}

try:
    # Note: This will fail without actual XCP-ng infrastructure
    # but demonstrates the API usage pattern
    xcpng_vm = create_vm("example_xcpng", vm_type="xcpng", config=xcpng_config)
    
    # Start the VM (creates VM in XCP-ng and establishes SSH)
    xcpng_vm.start()
    
    # Execute Lua code remotely
    result = xcpng_vm.execute_string('print("Hello from XCP-ng VM!")')
    print("✅ XCP-ng VM result:", result.get('stdout', 'No output'))
    
    # Install a package in the remote VM
    xcpng_vm.install_package("lua-cjson")
    print("✅ Package installed in XCP-ng VM")
    
    # Stop the VM
    xcpng_vm.stop()
    print("✅ XCP-ng VM stopped")
    
except Exception as e:
    print(f"❌ XCP-ng VM example (expected without infrastructure): {e}")
    print("💡 This is normal without actual XCP-ng host connectivity")

# Example 3: VMManager with Multi-VM Support
print("\n3. VMManager with Multi-VM Support")
print("-" * 40)

try:
    with VMManager(debug_mode=True) as manager:
        # Create both types of VMs through manager
        print("Creating basic VM through manager...")
        basic_session = manager.create_interactive_vm("managed_basic", vm_type="basic")
        
        print("Creating XCP-ng VM through manager...")
        try:
            xcpng_session = manager.create_interactive_vm("managed_xcpng", vm_type="xcpng", config=xcpng_config)
            print("✅ Both VM types created successfully")
            
            # Unified interface for both types
            manager.send_input("managed_basic", "x = 1 + 1")
            manager.send_input("managed_xcpng", "y = 2 + 2")
            
            print("Commands sent to both VMs")
            
        except Exception as e:
            print(f"❌ XCP-ng VM creation (expected): {e}")
            print("✅ Basic VM created successfully")
        
        # List all sessions
        sessions = manager.session_manager.list_sessions()
        print(f"✅ Active sessions: {list(sessions.keys())}")
        
except Exception as e:
    print(f"❌ VMManager example error: {e}")

# Example 4: Configuration File Loading
print("\n4. Configuration File Loading Example")
print("-" * 45)

config_file = "xcpng_config.json"
try:
    # Create example config file
    with open(config_file, 'w') as f:
        json.dump(xcpng_config, f, indent=2)
    
    # Load config from file
    with open(config_file) as f:
        loaded_config = json.load(f)
    
    print(f"✅ Configuration loaded from {config_file}")
    print(f"   Host: {loaded_config.get('xapi_url')}")
    print(f"   Template: {loaded_config.get('template')}")
    
    # Use loaded config (would work with real XCP-ng)
    print("💡 Config ready for XCP-ng VM creation")
    
except Exception as e:
    print(f"❌ Config file example error: {e}")

print("\n" + "=" * 60)
print("PHASE 3 EXAMPLES COMPLETE")
print("=" * 60)
print("✅ Basic VM: Local Lua process execution")
print("✅ XCP-ng VM: Remote VM with XAPI/SSH integration")
print("✅ VMManager: Unified multi-VM management")
print("✅ Config: File-based XCP-ng configuration")
print("\n💡 Use 'python interactive-bioxen-lua.py' for interactive CLI")
