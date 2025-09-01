# PyLua BioXen VM Library - API Documentation

## Phase 3: Complete API with XCP-ng Integration and CLI Support

This document provides comprehensive API documentation for the pylua_bioxen_vm_lib with full XCP-ng integration and CLI support.

## Table of Contents

- [VM Factory Pattern](#vm-factory-pattern)
- [VMManager](#vmmanager)
- [XCP-ng Integration](#xcp-ng-integration)
- [CLI Integration](#cli-integration)
- [Configuration Management](#configuration-management)
- [Error Handling](#error-handling)

---

## VM Factory Pattern

### create_vm()

Create a VM using the factory pattern with support for multiple VM types.

```python
create_vm(vm_id, vm_type="basic", config=None, **kwargs)
```

**Parameters:**
- `vm_id` (str): Unique VM identifier
- `vm_type` (str): VM type - "basic" (local process) or "xcpng" (XCP-ng VM)
- `config` (dict, optional): Configuration dictionary (required for xcpng)
- `**kwargs`: Additional parameters passed to VM constructor

**Returns:**
- `BasicLuaVM` or `XCPngVM` instance based on vm_type

**Examples:**

```python
from pylua_bioxen_vm_lib import create_vm

# Basic VM (local process)
basic_vm = create_vm("local_vm", vm_type="basic")
result = basic_vm.execute_string('print("Hello!")')

# XCP-ng VM (remote virtual machine)
config = {
    "xapi_url": "https://xcpng-host.example.com",
    "username": "root",
    "password": "password",
    "template": "lua-bio-template"
}
xcpng_vm = create_vm("remote_vm", vm_type="xcpng", config=config)
xcpng_vm.start()
result = xcpng_vm.execute_string('print("Hello from XCP-ng!")')
xcpng_vm.stop()
```

---

## VMManager

Enhanced VM manager with multi-VM support and interactive sessions.

### VMManager Class

```python
class VMManager:
    def __init__(self, debug_mode=False):
        """Initialize VM manager"""
```

### create_interactive_vm() - Updated

```python
create_interactive_vm(vm_id, vm_type="basic", config=None)
```

**Parameters:**
- `vm_id` (str): Unique VM identifier
- `vm_type` (str): VM type: "basic" (local process) or "xcpng" (XCP-ng VM)
- `config` (dict, optional): Configuration dictionary (required for xcpng)

**Returns:**
- Interactive session object

**Example:**

```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Create basic VM
    basic_session = manager.create_interactive_vm("vm1", vm_type="basic")
    
    # Create XCP-ng VM
    xcpng_config = {
        "xapi_url": "https://xcpng-host",
        "username": "root",
        "password": "password",
        "template": "lua-bio-template"
    }
    xcpng_session = manager.create_interactive_vm("vm2", vm_type="xcpng", config=xcpng_config)
    
    # Unified interface for both types
    manager.send_input("vm1", "x = 1 + 1")
    manager.send_input("vm2", "y = 2 + 2")
    
    print(manager.read_output("vm1"))
    print(manager.read_output("vm2"))
```

### Other VMManager Methods

```python
# VM lifecycle management
send_input(vm_id, input_text)          # Send Lua code to VM
read_output(vm_id)                     # Read output from VM
terminate_vm_session(vm_id)            # Stop and cleanup VM

# Session management
attach_to_vm(vm_id)                    # Attach to existing session
detach_from_vm(vm_id)                  # Detach from session
list_sessions()                        # List all active sessions
```

---

## XCP-ng Integration

### XCP-ng Configuration

XCP-ng VMs require configuration with connection and template details:

```python
xcpng_config = {
    # Required fields
    "xapi_url": "https://xcpng-host.example.com",
    "username": "root",
    "password": "your_password",
    "template": "lua-bio-template",
    
    # Optional fields
    "vm_name_prefix": "bioxen-lua",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": False,
    "ssh_timeout": 30,
    "vm_network": "Pool-wide network associated with eth0"
}
```

### XCPngVM Class

The XCPngVM class provides the same interface as BasicLuaVM but executes on remote XCP-ng infrastructure.

```python
class XCPngVM:
    def start()                              # Create and start VM in XCP-ng
    def stop()                               # Stop and cleanup VM
    def execute_string(lua_code)             # Execute Lua code via SSH
    def install_package(package_name)        # Install LuaRocks package
    def send_input(input_text)               # Send input to SSH session
    def read_output()                        # Read output from SSH session
```

### XAPI Client

Low-level XAPI client for direct XCP-ng management:

```python
from pylua_bioxen_vm_lib.xapi_client import XAPIClient

client = XAPIClient(
    xapi_url="https://xcpng-host",
    username="root", 
    password="password"
)

# VM lifecycle operations
vm_ref = client.create_vm_from_template("lua-template", "my-vm")
client.start_vm(vm_ref)
network_info = client.get_vm_network_info(vm_ref)
client.stop_vm(vm_ref)
client.delete_vm(vm_ref)
```

### SSH Session Manager

Manage persistent SSH connections for interactive Lua sessions:

```python
from pylua_bioxen_vm_lib.ssh_session import SSHSessionManager

ssh_manager = SSHSessionManager()
ssh_manager.connect("vm-host", "root", "password")
ssh_manager.start_lua_session()
ssh_manager.send_input("print('Hello')")
output = ssh_manager.read_output()
ssh_manager.close()
```

---

## CLI Integration

### BioXen-luavm CLI

Interactive command-line interface with XCP-ng support.

```bash
# Start the CLI
python interactive-bioxen-lua.py
```

**Features:**
- VM type selection (basic/xcpng)
- Configuration management (file or manual)
- Unified VM management interface
- Status tracking with VM type indicators

### CLI Workflow

1. **VM Creation with Type Selection**
   - Select "🚀 Create new Lua VM"
   - Choose VM type: 🖥️ Basic or ☁️ XCP-ng
   - Provide configuration for XCP-ng VMs

2. **Configuration Options**
   - 📁 Load from config file (`xcpng_config.json`)
   - ⚙️ Enter manually through prompts

3. **Unified VM Management**
   - Same attach/detach commands for both VM types
   - Identical interactive terminal experience
   - Common package installation process

### CLI Status Display

```
📋 VM ID: my_vm
   Type: ☁️ XCP-ng VM
   Profile: standard
   Status: 🟢 Running 🔗 Attached
   Created: 2025-09-01 10:30:00
   Uptime: 0d 2h 15m
   Host: https://xcpng-host.example.com
   Template: lua-bio-template
```

---

## Configuration Management

### Configuration File Format

Create `xcpng_config.json` for persistent XCP-ng settings:

```json
{
    "xapi_url": "https://192.168.1.100",
    "username": "root",
    "password": "your_secure_password",
    "template": "lua-bio-template",
    "vm_name_prefix": "bioxen-lua",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": false,
    "ssh_timeout": 30,
    "vm_network": "Pool-wide network associated with eth0"
}
```

### Loading Configuration

```python
import json

# Load from file
with open('xcpng_config.json') as f:
    config = json.load(f)

# Use with VM creation
vm = create_vm("my_vm", vm_type="xcpng", config=config)
```

### Configuration Validation

Required fields for XCP-ng configuration:
- `xapi_url`: XAPI endpoint URL
- `username`: XCP-ng username  
- `password`: XCP-ng password
- `template`: VM template name

Optional fields with defaults:
- `vm_name_prefix`: "bioxen-lua"
- `memory`: "2GB"
- `vcpus`: 2
- `verify_ssl`: False
- `ssh_timeout`: 30

---

## Error Handling

### Exception Types

```python
from pylua_bioxen_vm_lib.exceptions import (
    VMManagerError,
    SessionNotFoundError,
    InteractiveSessionError,
    AttachError,
    DetachError
)
```

### Common Error Patterns

```python
# VM creation errors
try:
    vm = create_vm("vm_id", vm_type="xcpng", config=config)
except VMManagerError as e:
    print(f"VM creation failed: {e}")
    # Check configuration and connectivity

# Session management errors  
try:
    manager.attach_to_vm("nonexistent_vm")
except SessionNotFoundError:
    print("VM session not found")

# XCP-ng specific errors
try:
    xcpng_vm.start()
except VMManagerError as e:
    print(f"XCP-ng VM start failed: {e}")
    # Check XAPI connectivity, template availability
```

### Troubleshooting Guide

**Connection Issues:**
- Verify XCP-ng host connectivity
- Check username/password credentials  
- Confirm XAPI service is running

**Template Issues:**
- Verify template exists in XCP-ng
- Check template has Lua runtime installed
- Confirm SSH is enabled in template

**SSH Issues:**
- Check VM network configuration
- Verify SSH service is running
- Confirm firewall settings

---

## Complete Usage Examples

### Biological Computation Workflow

```python
from pylua_bioxen_vm_lib import VMManager

# Biological sequence analysis across VM types
sequences = {
    "sample1": "ATCGATCGTAGCTAGCGGCGAATC",
    "sample2": "GGCCTTAAGCCGATCGTAGCCCGG"
}

bio_analysis = '''
function analyze_sequence(seq)
    local gc_count = 0
    local length = #seq
    
    for i = 1, length do
        local nucleotide = seq:sub(i, i):upper()
        if nucleotide == "G" or nucleotide == "C" then
            gc_count = gc_count + 1
        end
    end
    
    return (gc_count / length) * 100
end
'''

with VMManager(debug_mode=True) as manager:
    # Process on basic VM
    basic_vm = manager.create_interactive_vm("basic_bio", vm_type="basic")
    manager.send_input("basic_bio", bio_analysis)
    
    # Process on XCP-ng VM  
    xcpng_vm = manager.create_interactive_vm("xcpng_bio", vm_type="xcpng", config=config)
    manager.send_input("xcpng_bio", bio_analysis)
    
    # Analyze sequences
    for sample_id, sequence in sequences.items():
        analysis_code = f'''
        local result = analyze_sequence("{sequence}")
        print("{sample_id}: GC Content = " .. string.format("%.1f%%", result))
        '''
        
        # Run on both VM types
        manager.send_input("basic_bio", analysis_code)
        manager.send_input("xcpng_bio", analysis_code)
        
        print(f"Basic VM: {manager.read_output('basic_bio')}")
        print(f"XCP-ng VM: {manager.read_output('xcpng_bio')}")
```

### Multi-VM Package Management

```python
# Install packages across different VM types
package_code = '''
-- Install and use lua-cjson
os.execute("luarocks install lua-cjson")
local json = require("cjson")

local data = {
    sequence = "ATCGATCG",
    gc_content = 50.0,
    analysis_date = os.date()
}

print(json.encode(data))
'''

# Works identically on both VM types
manager.send_input("basic_bio", package_code)
manager.send_input("xcpng_bio", package_code)
```

---

This completes the Phase 3 API documentation with comprehensive XCP-ng integration and CLI support. The unified API allows seamless switching between local and remote VM execution while maintaining identical interfaces for both biological computation and general Lua development.
