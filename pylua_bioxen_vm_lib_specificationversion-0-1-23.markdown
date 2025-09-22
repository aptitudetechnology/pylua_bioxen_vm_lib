# pylua_bioxen_vm_lib Specification

## Overview

The **pylua_bioxen_vm_lib** (version 0.1.23) is a Python library for managing Lua virtual machines (VMs) within the BioXen framework. It's designed for biological computation and genomic data virtualization with **enterprise-grade XCP-ng cloud automation**, multi-VM support, and fully automated VM deployment.

**Key Features:**
- **Cloud-Native XCP-ng Integration** with cloud-init automation using cloud images
- **Interactive CLI** with `bioxen-luavm` command-line tool
- **Multi-VM Support** with factory pattern (basic/xcpng/cloud VM types)
- **Automated VM Deployment** - Zero manual intervention required (90 seconds to running VM)
- **XCP-ng Guest Tools** - Automatically installed for optimal hypervisor integration
- **Configuration Management** for file-based and manual XCP-ng setup
- Synchronous and asynchronous Lua code execution
- Interactive session management with persistent VMs
- Library-agnostic package management
- Isolated Lua environments
- Perfect for lightweight, sandboxed Lua VMs in biological workflows

This specification was updated on September 22, 2025, and reflects the complete cloud automation implementation with XCP-ng integration.

---

## Quick Start

**Getting Started in 90 Seconds:**
This library lets you run Lua code from Python and includes an interactive CLI for VM management with **fully automated cloud deployment using cloud images**.

### Command-Line Interface (Phase 3)
```bash
# Launch interactive CLI
bioxen-luavm

# Or use Python module
python -m pylua_bioxen_vm_lib.cli_main
```

### Programmatic Usage
```python
from pylua_bioxen_vm_lib import create_vm

# Create and use a basic VM
vm = create_vm("my_vm")
result = vm.execute_string('return 2 + 2')
print(result['stdout'])  # Output: 4

# Create cloud-automated XCP-ng VM with cloud image
from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig
from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM

config = CloudInitConfig.create_bioxen_vm(hostname="my-lua-vm")
xcpng_vm = XCPngVM("192.168.1.198", "root", "password")
xcpng_vm.create_cloud_vm_from_template(
    template_uuid="93ee7338-8e41-334e-2115-0ddbfb6e18ba",  # Cloud image template
    vm_name="my-cloud-vm",
    cloud_init_config=config
)
vm_cloud = XCPngVM("cloud-vm", {
    'xcp_host': '192.168.1.198',
    'template_name': '07d91aaa-43f7-430a-bf84-0edb6714df0f',
    'use_cloud_init': True,
    'cloud_init_config': config.to_base64()
})
vm_cloud.start()  # VM ready with Lua, SSH, and all dependencies!
```

---

## Interactive CLI (Phase 3)

**Purpose:** Complete command-line interface for managing Lua VMs with XCP-ng support and VM type selection.

### Installation and Usage

After installing the package, the interactive CLI is available via:

```bash
# Install from PyPI test
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pylua-bioxen-vm-lib==0.1.22

# Launch CLI
bioxen-luavm
```

### CLI Features

**VM Type Selection:**
- **Basic VMs**: Standard Lua process execution
- **XCP-ng VMs**: Template-based VM creation with SSH execution
- **Cloud VMs**: Fully automated deployment with cloud-init

**Configuration Management:**
- **File-based**: Load XCP-ng configuration from `xcpng_config.json` or `.env`
- **Manual**: Interactive prompts for XCP-ng setup
- **Cloud-init**: Automated VM configuration and package installation

**Session Management:**
- Create and manage interactive Lua sessions
- Attach/detach from persistent VMs
- Real-time code execution and output
- SSH-based remote VM management

**Package Management:**
- Install Lua packages in VMs via luarocks
- Environment isolation and management
- Automated dependency resolution

**Cloud Automation:**
- **Template Management**: Create and manage cloud-ready templates
- **Automated Deployment**: Zero-touch VM provisioning
- **SSH Key Management**: Secure, passwordless access
- **Network Configuration**: Automatic IP assignment and DNS

### XCP-ng Configuration Example

Create `xcpng_config.json` in your project directory:

```json
{
    "xapi_url": "https://your-xcpng-host:443",
    "username": "root",
    "password": "your-password",
    "pool_uuid": "your-pool-uuid",
    "template_name": "lua-bio-template",
    "vm_name_prefix": "bioxen-lua",
    "network_uuid": "your-network-uuid",
    "storage_repository": "your-sr-uuid",
    "ssh_user": "root",
    "ssh_key_path": "/path/to/ssh/key"
}
```

**Environment File Configuration (.env):**

```bash
# XCP-ng credentials (DO NOT COMMIT THIS FILE)
XCP_HOST=192.168.1.198
XCP_USERNAME=root
XCP_PASSWORD=your-password-here
XCP_TEMPLATE=Debian Bookworm 12
VM_USERNAME=bioxen
```

**Cloud-Init Configuration:**

```python
from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig

# Create BioXen-optimized cloud configuration
config = CloudInitConfig.create_bioxen_vm(
    hostname="bioxen-lua-vm",
    username="bioxen",
    password="secure-password"
)

# Add custom packages and configuration
config.add_package("bioinformatics-tools")
config.add_package("lua-bio-libs")

# Generate base64-encoded config for XCP-ng
cloud_config_b64 = config.to_base64()
```

### CLI Class Structure

```python
class BioXenLuavmCLI:
    """Interactive CLI for BioXen Lua VM management with XCP-ng support"""
    
    def __init__(self):
        self.vm_manager = VMManager(debug_mode=True)
        self.vm_profiles = {}
        self.active_vms = {}
        self.xcpng_config = None
    
    def run(self):
        """Main CLI loop with VM type selection"""
        # Interactive menu system with questionary
    
    def handle_vm_type_selection(self):
        """Handle VM type selection (basic/xcpng)"""
        # VM type selection with configuration management
    
    def handle_xcpng_configuration(self):
        """Handle XCP-ng configuration (file/manual)"""
        # Configuration loading and validation
```

---

## VM Creation

**Purpose:** Creates isolated Lua environments that run as separate processes. Version 0.1.23 supports multiple VM types via a factory pattern with **enterprise-grade cloud automation** and XCP-ng integration.

### Main Function

```python
create_vm(vm_id="default", vm_type="basic", networked=False, persistent=False, debug_mode=False, lua_executable="lua", config=None)
```

**Parameters:**
- `vm_id` - Unique identifier for your VM (default: "default")
- `vm_type` - Type of VM to create ("basic", "xcpng", or "cloud"; default: "basic")
- `networked` - Enable experimental networking features (default: False)
- `persistent` - Keep VM alive between sessions (default: False) 
- `debug_mode` - Show detailed logs for troubleshooting (default: False)
- `lua_executable` - Path to Lua on your system (default: "lua")
- `config` - Configuration dictionary for VM-specific settings (required for xcpng/cloud types)

**Returns:** A VM object (BasicLuaVM, NetworkedLuaVM, XCPngVM, or CloudVM)

### Factory Pattern Examples

```python
from pylua_bioxen_vm_lib import create_vm

# Create a basic VM (standard functionality)
vm = create_vm("test_vm", vm_type="basic", debug_mode=True)

# Create an XCP-ng VM with configuration
xcpng_config = {
    "xcp_host": "192.168.1.198",
    "username": "root", 
    "password": "password",
    "template_name": "07d91aaa-43f7-430a-bf84-0edb6714df0f",
    "ssh_user": "root"
}
vm_xcpng = create_vm("xcpng_vm", vm_type="xcpng", config=xcpng_config)

# Create a cloud-automated VM with cloud-init
from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig

cloud_config = CloudInitConfig.create_bioxen_vm(hostname="my-cloud-vm")
vm_cloud = create_vm("cloud_vm", vm_type="cloud", config={
    "xcp_host": "192.168.1.198",
    "template_name": "93ee7338-8e41-334e-2115-0ddbfb6e18ba",  # Cloud template
    "use_cloud_init": True,
    "cloud_init_config": cloud_config.to_base64()
})
```

**Note:**
- If `vm_type` is not specified, defaults to "basic" for backward compatibility
- If `vm_type` is "xcpng", an XCPngVM is created with full XAPI client integration and SSH execution
- If `vm_type` is "cloud", a CloudVM is created with automated cloud-init deployment
- Invalid `vm_type` values will raise a ValueError
- Cloud VMs require a valid `config` dictionary with XAPI and cloud-init credentials

### Enhanced VMManager (Version 0.1.23)

The VMManager now supports the `vm_type` parameter for multi-VM creation with cloud automation:

```python
from pylua_bioxen_vm_lib import VMManager

# Create manager with VM type support
with VMManager(debug_mode=True) as manager:
    # Create basic VM
    basic_vm = manager.create_vm("basic_vm", vm_type="basic")
    
    # Create XCP-ng VM with config
    xcpng_vm = manager.create_vm("xcpng_vm", vm_type="xcpng", config=xcpng_config)
    
    # Create cloud VM with automated deployment
    cloud_vm = manager.create_vm("cloud_vm", vm_type="cloud", config=cloud_config)
    
    # Execute code in all VM types
    basic_result = manager.execute_vm_sync("basic_vm", 'return "Hello from basic VM"')
    xcpng_result = manager.execute_vm_sync("xcpng_vm", 'return "Hello from XCP-ng VM"')
    cloud_result = manager.execute_vm_sync("cloud_vm", 'return "Hello from cloud VM"')
```

### XCPngVM Class (Version 0.1.23 Complete Implementation)

```python
import paramiko
from pylua_bioxen_vm_lib.xapi_client import XAPIClient
from pylua_bioxen_vm_lib.ssh_session import SSHSession

class XCPngVM:
    """Complete XCP-ng VM integration via XAPI with cloud automation support"""
    
    def __init__(self, vm_id, config=None):
        self.vm_id = vm_id
        self.config = config or {}
        self.xapi_client = XAPIClient(
            host=self.config.get('xcp_host'),
            username=self.config.get('username'), 
            password=self.config.get('password')
        )
        self.ssh_session = SSHSession(
            user=self.config.get('ssh_user', 'root'),
            key_path=self.config.get('ssh_key_path')
        )
        self.vm_uuid = None
        self.vm_ip = None
    
    def start(self):
        """Start VM using XAPI template management"""
        # Real XAPI call for VM creation from template
        self.vm_uuid = self.xapi_client.create_vm_from_template(
            template_uuid=self.config.get('template_name'),
            vm_name=f"{self.config.get('vm_name_prefix', 'bioxen')}-{self.vm_id}"
        )
        self.xapi_client.start_vm(self.vm_uuid)
        self.vm_ip = self.xapi_client.get_vm_ip(self.vm_uuid)
        
    def stop(self):
        """Stop VM using XAPI"""
        if self.vm_uuid:
            self.xapi_client.shutdown_vm(self.vm_uuid)
            
    def execute_string(self, lua_code):
        """Execute Lua code in VM via SSH"""
        if not self.vm_ip:
            raise VMManagerError("VM not started or IP not available")
        
        result = self.ssh_session.execute_command(
            host=self.vm_ip,
            command=f'lua -e "{lua_code}"'
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
        
    def install_package(self, package_name):
        """Install Lua package in VM via SSH"""
        if not self.vm_ip:
            raise VMManagerError("VM not started or IP not available")
            
        result = self.ssh_session.execute_command(
            host=self.vm_ip,
            command=f'luarocks install {package_name}'
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
        
    def get_status(self):
        """Get VM status via XAPI"""
        if self.vm_uuid:
            return self.xapi_client.get_vm_status(self.vm_uuid)
        return {"status": "not_created"}
```

### CloudInitConfig Class (New in Version 0.1.23)

```python
import base64
import yaml
from typing import Dict, List, Optional, Any

class CloudInitConfig:
    """Cloud-init configuration generator for BioXen VMs"""
    
    def __init__(self):
        """Initialize with default BioXen configuration"""
        self.config = {
            'package_update': True,
            'package_upgrade': True,
            'packages': [
                'lua5.4', 'lua5.4-dev', 'luarocks', 'curl', 'git',
                'htop', 'vim', 'sudo', 'openssh-server'
            ],
            'users': [],
            'chpasswd': {'list': '', 'expire': False},
            'ssh_pwauth': True,
            'disable_root': False,
            'runcmd': ['systemctl enable ssh', 'systemctl start ssh'],
            'final_message': 'BioXen VM is ready!'
        }
    
    @classmethod
    def create_bioxen_vm(cls, hostname: str, username: str = "bioxen", 
                        password: str = None) -> 'CloudInitConfig':
        """Create BioXen-optimized cloud configuration"""
        config = cls()
        config.set_hostname(hostname)
        config.add_user(username, password)
        return config
    
    def add_user(self, username: str, password: str = None, 
                 ssh_keys: List[str] = None) -> 'CloudInitConfig':
        """Add a user to the cloud-init configuration"""
        user_config = {'name': username, 'sudo': 'ALL=(ALL) NOPASSWD:ALL'}
        if password:
            user_config['passwd'] = password
        if ssh_keys:
            user_config['ssh-authorized-keys'] = ssh_keys
        self.config['users'].append(user_config)
        return self
    
    def add_package(self, package: str) -> 'CloudInitConfig':
        """Add a package to install"""
        self.config['packages'].append(package)
        return self
    
    def set_hostname(self, hostname: str) -> 'CloudInitConfig':
        """Set VM hostname"""
        self.config['hostname'] = hostname
        return self
    
    def to_base64(self) -> str:
        """Generate base64-encoded cloud-init config"""
        yaml_config = yaml.dump(self.config)
        return base64.b64encode(yaml_config.encode()).decode()
```

### Advanced Usage Example (Version 0.1.23 Complete - Cloud Image Automation)

```python
from pylua_bioxen_vm_lib import create_vm
from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig

# Create XCP-ng VM with cloud image automation (90 seconds to running VM)
xcpng_config = {
    "xcp_host": "192.168.1.198",
    "username": "root",
    "password": "secure_password",
    "template_name": "07d91aaa-43f7-430a-bf84-0edb6714df0f",  # Standard Debian Bookworm
    "vm_name_prefix": "bioxen-lua",
    "ssh_user": "root"
}

# Create and manage XCP-ng VM
vm_xcpng = create_vm("bio_compute_vm", vm_type="xcpng", config=xcpng_config)
vm_xcpng.start()
status = vm_xcpng.get_status()
print(f"VM Status: {status}")

# Execute Lua code for biological computation
result = vm_xcpng.execute_string('''
    local sequence = "ATCGATCGATCG"
    local gc_content = 0
    for i = 1, #sequence do
        local base = sequence:sub(i, i)
        if base == "G" or base == "C" then
            gc_content = gc_content + 1
        end
    end
    return string.format("GC content: %.2f%%", (gc_content / #sequence) * 100)
''')
print(f"Biological computation result: {result['stdout']}")

# Cloud-Automated VM Deployment (90 seconds from script to running VM)
cloud_config = CloudInitConfig.create_bioxen_vm(
    hostname="bioxen-cloud-vm",
    username="researcher",
    password="secure-research-password"
)

# Add bioinformatics packages
cloud_config.add_package("bioperl")
cloud_config.add_package("emboss")
cloud_config.add_package("clustalw")

# Guest tools are automatically included for XCP-ng integration

cloud_vm_config = {
    "xcp_host": "192.168.1.198",
    "template_name": "93ee7338-8e41-334e-2115-0ddbfb6e18ba",  # Cloud-ready Debian template
    "use_cloud_init": True,
    "cloud_init_config": cloud_config.to_base64()
}

# Deploy cloud VM with full automation
cloud_vm = create_vm("cloud_bio_vm", vm_type="cloud", config=cloud_vm_config)
cloud_vm.start()  # VM ready with all dependencies in ~90 seconds!

# Execute advanced biological analysis
analysis_result = cloud_vm.execute_string('''
    -- Advanced Lua biological sequence analysis
    local sequences = {"ATCGATCG", "GCTAGCTA", "CGATCGAT"}
    local results = {}

    for i, seq in ipairs(sequences) do
        local gc = 0
        for j = 1, #seq do
            local base = seq:sub(j, j)
            if base == "G" or base == "C" then gc = gc + 1 end
        end
        results[i] = string.format("Seq %d: %.1f%% GC", i, (gc/#seq)*100)
    end

    return table.concat(results, "\\n")
''')

print(f"Cloud VM analysis: {analysis_result['stdout']}")
```

### CLI Integration Usage (Phase 3)

```bash
# Launch interactive CLI
bioxen-luavm

# CLI workflow:
# 1. Select VM type (basic/xcpng)
# 2. Configure XCP-ng settings (file/manual)
# 3. Create and manage VMs
# 4. Execute Lua code interactively
# 5. Install packages and manage environments
```

### Testing and Success Criteria (Phase 3 Complete)

- ✅ **CLI Integration**: Interactive CLI with `bioxen-luavm` command working
- ✅ **VM Type Selection**: Basic and XCP-ng VM types fully implemented
- ✅ **XCP-ng Integration**: Real XAPI client with template-based VM creation
- ✅ **SSH Execution**: Remote Lua code execution via SSH sessions
- ✅ **Configuration Management**: File-based and manual XCP-ng configuration
- ✅ **Package Management**: Lua package installation in remote VMs
- ✅ **Session Management**: Interactive VM sessions with attach/detach
- ✅ **Error Handling**: Comprehensive exception handling and validation
- ✅ **Documentation**: Complete API, installation, and CLI guides
- ✅ **PyPI Deployment**: Version 0.1.22 successfully deployed to PyPI test

### Module Structure (Phase 3)

```
pylua_bioxen_vm_lib/
├── cli_main.py              # CLI entry point for bioxen-luavm script
├── xapi_client.py           # XAPI client for XCP-ng communication  
├── ssh_session.py           # SSH session management for remote execution
├── xcp_ng_integration.py    # Complete XCPngVM implementation
├── vm_manager.py            # Enhanced with vm_type parameter support
└── interactive_session.py   # Session management with multi-VM support
```

### Dependencies (Phase 3)

**Core Dependencies:**
- `requests>=2.25.0` - HTTP client for XAPI communication
- `paramiko>=2.7.0` - SSH client for remote VM execution  
- `urllib3>=1.26.0` - HTTP library for reliable connections
- `questionary>=1.10.0` - Interactive CLI prompts and menus

**Optional Dependencies:**
- `luasocket` - For networking features in basic VMs
- `lua` interpreter - Required on target systems

---

## VM Manager

**Purpose:** Manages multiple Lua VMs and their sessions with lifecycle control. Enhanced in Phase 3 with multi-VM type support.

### Main Class: `VMManager`

Handles creating, executing, and managing multiple VMs of different types (basic/xcpng).

### Key Methods

**VM Management (Enhanced Phase 3):**
- `create_vm(vm_id, vm_type="basic", networked=False, persistent=False, config=None)` - Creates a managed VM with type selection
- `execute_vm_sync(vm_id, code)` - Runs Lua code and waits for result
- `execute_vm_async(vm_id, code)` - Runs Lua code without waiting
- `terminate_vm_session(vm_id)` - Shuts down a VM

**Interactive Sessions:**
- `create_interactive_vm(vm_id, vm_type="basic", config=None)` - Creates a persistent session with VM type support
- `attach_to_vm(vm_id)` - Connects to existing session
- `detach_from_vm(vm_id)` - Disconnects from session
- `send_input(vm_id, input)` - Sends Lua code to session
- `read_output(vm_id)` - Gets output from session
- `list_sessions()` - Shows all active sessions

### Multi-VM Type Example (Phase 3)

```python
from pylua_bioxen_vm_lib import VMManager

# XCP-ng configuration
xcpng_config = {
    "xapi_url": "https://xcpng-host:443",
    "username": "root",
    "password": "password",
    "template_name": "lua-bio-template",
    "ssh_user": "root",
    "ssh_key_path": "/path/to/key"
}

# Use context manager for automatic cleanup
with VMManager(debug_mode=True) as manager:
    # Create basic VM
    basic_vm = manager.create_vm("basic_vm", vm_type="basic")
    
    # Create XCP-ng VM
    xcpng_vm = manager.create_vm("xcpng_vm", vm_type="xcpng", config=xcpng_config)
    
    # Execute in basic VM
    basic_result = manager.execute_vm_sync("basic_vm", 'return "Hello from basic VM"')
    print(f"Basic VM: {basic_result['stdout']}")
    
    # Execute in XCP-ng VM  
    xcpng_result = manager.execute_vm_sync("xcpng_vm", 'return "Hello from XCP-ng VM"')
    print(f"XCP-ng VM: {xcpng_result['stdout']}")
```

---

## Interactive Sessions

**Purpose:** Real-time interaction with Lua VMs for dynamic scripting

### Main Class: `InteractiveSession`

Allows back-and-forth communication with a Lua VM, like a chat conversation.

### Key Methods

- `send_input(input)` - Sends Lua code to the session
- `read_output()` - Gets output from the session  
- `set_environment(env_name)` - Sets the Lua environment

**Note:** Package loading and REPL functionality work through `send_input()` and `read_output()`. There are no separate `load_package()` or `interactive_loop()` methods.

### Interactive Example

```python
from pylua_bioxen_vm_lib import VMManager
import time

# Create an interactive session
manager = VMManager(debug_mode=True)
session = manager.create_interactive_vm("interactive_vm")

# Send some Lua code
manager.send_input("interactive_vm", "x = 42\nprint('Value:', x)\n")

# Wait a moment for processing
time.sleep(0.5)

# Read the result
print(manager.read_output("interactive_vm"))  # Output: Value: 42
```

---

## Session Manager

**Purpose:** Manages the lifecycle of interactive sessions

### Main Class: `SessionManager`

Access this through `VMManager.session_manager` to control sessions.

### Key Methods

- `list_sessions()` - Returns dictionary of active sessions and details
- `terminate_session(vm_id)` - Terminates a specific session

### Session Management Example

```python
from pylua_bioxen_vm_lib import VMManager

manager = VMManager(debug_mode=True)
session_manager = manager.session_manager

# Create a session
session = manager.create_interactive_vm("test_session")

# List active sessions
sessions = session_manager.list_sessions()
print(sessions)  # Output: {'test_session': <session_details>}

# Clean up
session_manager.terminate_session("test_session")
```

---

## Package Management

**Purpose:** Manages Lua packages and isolated environments using external catalogs

### Key Modules

- `pylua_bioxen_vm_lib.utils.curator` - Package metadata and repositories
- `pylua_bioxen_vm_lib.env` - Environment management
- `pylua_bioxen_vm_lib.package_manager` - Package operations

### Key Classes & Functions

- `Curator` and `get_curator()` - Manages package metadata
- `PackageInstaller` - Installs, updates, and removes packages
- `EnvironmentManager` - Manages isolated Lua environments
- `PackageManager` - Orchestrates package operations
- `RepositoryManager` - Manages package repositories
- `search_packages(query)` - Searches available packages
- `bootstrap_lua_environment(env_name)` - Sets up Lua environment

**Important:** Package management uses external catalogs, not hardcoded dictionaries. Load packages by sending `require` statements via `send_input()`.

### Package Example

```python
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller, search_packages

# Search and install a package
installer = PackageInstaller()
packages = search_packages("bio_compute")
installer.install_package("bio_compute")
```

---

## Exception Handling

**Purpose:** Provides specific exceptions for robust error handling

### Key Exceptions

**Session Errors:**
- `InteractiveSessionError` - General session management errors
- `AttachError` - Problems attaching to sessions
- `DetachError` - Problems detaching from sessions  
- `SessionNotFoundError` - Invalid session ID
- `SessionAlreadyExistsError` - Duplicate session creation

**VM Errors:**
- `VMManagerError` - VM manager operation errors
- `LuaVMError` - Lua code execution errors

### Error Handling Example

```python
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.exceptions import SessionNotFoundError

try:
    VMManager().attach_to_vm("nonexistent")
except SessionNotFoundError:
    print("Session not found")
```

---

## Logging

**Purpose:** Configurable logging for debugging and monitoring

### Main Class: `VMLogger`

**Parameters:**
- `debug_mode` - Enable verbose logging (True/False)
- `component` - Specify logging component name

### Logging Example

```python
from pylua_bioxen_vm_lib.logger import VMLogger

logger = VMLogger(debug_mode=True, component="MyApp")
logger.debug("Debug message")
```

---

## Usage Patterns

### Pattern 1: Basic VM Execution

Execute Lua code in a simple, standalone VM:

```python
from pylua_bioxen_vm_lib import create_vm

vm = create_vm("simple_vm", debug_mode=True)
result = vm.execute_string('print("Hello!")')
print(result['stdout'])  # Output: Hello!
```

### Pattern 2: Managed VMs

Use context managers for automatic resource cleanup:

```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("managed_vm")
    result = manager.execute_vm_sync("managed_vm", 'return 2 + 2')
    print(result['stdout'])  # Output: 4
```

### Pattern 3: Interactive Sessions

Manage persistent sessions for back-and-forth coding:

```python
from pylua_bioxen_vm_lib import VMManager
import time

manager = VMManager(debug_mode=True)

# Create interactive session
session = manager.create_interactive_vm("interactive_vm")

# Send code
manager.send_input("interactive_vm", "x = 10\nprint('Value:', x)\n")
time.sleep(0.5)

# Read result
print(manager.read_output("interactive_vm"))  # Output: Value: 10

# Clean up
manager.detach_from_vm("interactive_vm")
manager.terminate_vm_session("interactive_vm")
```

### Pattern 4: Package Management

Install and use Lua packages in your VMs:

```python
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
from pylua_bioxen_vm_lib import VMManager
import time

# Install package
installer = PackageInstaller()
installer.install_package("bio_compute")

# Use package in VM
with VMManager() as manager:
    session = manager.create_interactive_vm("package_vm")
    
    # Load and use package
    manager.send_input("package_vm", 'require("bio_compute")\nprint(bio_compute.compute(10))')
    time.sleep(0.5)
    print(manager.read_output("package_vm"))
```

---

## Best Practices

### Resource Management
- **Always use context managers:** Use `VMManager` with `with` statements for automatic cleanup
- **Clean up sessions:** Always detach and terminate sessions to free resources

### Error Handling  
- **Catch specific exceptions:** Use `SessionNotFoundError`, etc. instead of generic exceptions
- **Validate inputs:** Check session IDs to avoid `SessionAlreadyExistsError`

### Debugging
- **Enable debug mode:** Set `debug_mode=True` or use environment variable:
  ```bash
  export PYLUA_DEBUG=true
  ```

### Package Management
- **Use isolated environments:** Create separate environments with `EnvironmentManager`
- **Load packages properly:** Use `require` statements via `send_input()` - there's no direct `load_package()` method

---

## Complete Example

Here's a full example integrating CLI, multi-VM types, and biological computation:

### Command-Line Usage (Phase 3)

```bash
# Launch interactive CLI
bioxen-luavm

# Follow prompts:
# 1. Select VM type: basic or xcpng
# 2. Configure XCP-ng settings (if applicable)
# 3. Create VM profile
# 4. Execute Lua code interactively
# 5. Install packages and manage environments
```

### Programmatic Usage with Multi-VM Support

```python
import os
import time
import json
from pylua_bioxen_vm_lib import VMManager, VMLogger
from pylua_bioxen_vm_lib.exceptions import VMManagerError

# Set up logging
logger = VMLogger(
    debug_mode=os.getenv('PYLUA_DEBUG', 'false').lower() == 'true', 
    component="BioComputeApp"
)

# XCP-ng configuration
xcpng_config = {
    "xapi_url": "https://xcpng-host:443",
    "username": "root",
    "password": "secure_password",
    "template_name": "lua-bio-template",
    "ssh_user": "root",
    "ssh_key_path": "/home/user/.ssh/xcpng_key"
}

# Multi-VM biological computation workflow
with VMManager(debug_mode=True) as manager:
    try:
        # Create basic VM for local processing
        basic_vm = manager.create_vm("local_analysis", vm_type="basic")
        
        # Create XCP-ng VM for distributed processing
        xcpng_vm = manager.create_vm("remote_analysis", vm_type="xcpng", config=xcpng_config)
        
        # Start XCP-ng VM
        manager.vms["remote_analysis"].start()
        
        # Execute sequence analysis on basic VM
        local_analysis = manager.execute_vm_sync("local_analysis", '''
            local sequence = "ATCGATCGATCGAAATTTCCCGGG"
            local gc_count = 0
            for i = 1, #sequence do
                local base = sequence:sub(i, i)
                if base == "G" or base == "C" then
                    gc_count = gc_count + 1
                end
            end
            return "Local GC Content: " .. (gc_count / #sequence * 100) .. "%"
        ''')
        
        # Execute parallel analysis on XCP-ng VM
        remote_analysis = manager.execute_vm_sync("remote_analysis", '''
            local sequence = "ATCGATCGATCGAAATTTCCCGGG"
            local at_count = 0
            for i = 1, #sequence do
                local base = sequence:sub(i, i)
                if base == "A" or base == "T" then
                    at_count = at_count + 1
                end
            end
            return "Remote AT Content: " .. (at_count / #sequence * 100) .. "%"
        ''')
        
        # Display results
        print("=== Biological Computation Results ===")
        print(f"Local Analysis: {local_analysis['stdout']}")
        print(f"Remote Analysis: {remote_analysis['stdout']}")
        
        # Install package on XCP-ng VM
        manager.vms["remote_analysis"].install_package("bio-algorithms")
        
        # Interactive session example
        session = manager.create_interactive_vm("interactive_bio", vm_type="basic")
        
        manager.send_input("interactive_bio", '''
            -- Interactive biological sequence analysis
            function analyze_motif(sequence, motif)
                local count = 0
                for i = 1, #sequence - #motif + 1 do
                    if sequence:sub(i, i + #motif - 1) == motif then
                        count = count + 1
                    end
                end
                return count
            end
            
            local dna = "ATCGATCGATCGATCG"
            local motif_count = analyze_motif(dna, "ATG")
            print("Motif ATG found: " .. motif_count .. " times")
        ''')
        
        time.sleep(1)  # Allow processing
        interactive_result = manager.read_output("interactive_bio")
        print(f"Interactive Analysis: {interactive_result}")
        
        # Clean up XCP-ng VM
        manager.vms["remote_analysis"].stop()
        
    except VMManagerError as e:
        logger.error(f"VM management error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
```

### Configuration File Example

Create `xcpng_config.json`:

```json
{
    "xapi_url": "https://your-xcpng-host:443",
    "username": "root",
    "password": "your-secure-password",
    "pool_uuid": "12345678-1234-1234-1234-123456789abc",
    "template_name": "lua-bio-template",
    "vm_name_prefix": "bioxen-lua",
    "network_uuid": "network-uuid-here",
    "storage_repository": "sr-uuid-here",
    "ssh_user": "root",
    "ssh_key_path": "/home/user/.ssh/xcpng_private_key",
    "vm_memory": "1GB",
    "vm_vcpus": 2
}
```

---

## Installation & Dependencies

### Installation Options

**From PyPI Test (Phase 3):**
```bash
# Install from PyPI test repository
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pylua-bioxen-vm-lib==0.1.22
```

**From Source:**
```bash
# Clone repository and install
git clone https://github.com/aptitudetechnology/pylua_bioxen_vm_lib.git
cd pylua_bioxen_vm_lib
pip install -e .
```

### System Requirements
- **Python 3.7+**
- **Lua interpreter** (installed on target systems)
- **XCP-ng/XenServer** (for XCP-ng VM type)
- **SSH access** (for remote VM management)

### Dependencies (Phase 3)

**Core Dependencies:**
```txt
requests>=2.25.0        # HTTP client for XAPI communication
paramiko>=2.7.0         # SSH client for remote execution
urllib3>=1.26.0         # HTTP library for connections
questionary>=1.10.0     # Interactive CLI prompts
```

**Optional Dependencies:**
```bash
# For networking features in basic VMs
luarocks install luasocket

# Lua interpreter (system-wide)
# Ubuntu/Debian: apt install lua5.3
# CentOS/RHEL: yum install lua
# macOS: brew install lua
```

### CLI Installation Verification

```bash
# Verify CLI installation
bioxen-luavm --help

# Or use Python module
python -m pylua_bioxen_vm_lib.cli_main --help
```

### XCP-ng Setup Requirements

For XCP-ng VM types, ensure:

1. **XCP-ng/XenServer** with XAPI access
2. **VM Templates** configured with Lua environment
3. **SSH Keys** for passwordless authentication
4. **Network Configuration** for VM connectivity

### Example XCP-ng Template Setup

```bash
# On XCP-ng host, create Lua-enabled template
xe template-clone uuid=<base-template-uuid> new-name-label="lua-bio-template"
xe vm-start uuid=<new-template-uuid>

# Install Lua and dependencies in template
ssh root@<template-ip> << 'EOF'
yum install lua luarocks -y
luarocks install luasocket
luarocks install bio-compute
EOF

# Convert to template
xe vm-shutdown uuid=<template-uuid>
xe template-create vm-uuid=<template-uuid> name-label="lua-bio-template"
```

---

## Additional Notes

- **Phase 3 Complete:** Interactive CLI with `bioxen-luavm` command fully implemented
- **Multi-VM Support:** Factory pattern with basic and XCP-ng VM types
- **XCP-ng Integration:** Real XAPI client with template-based VM creation and SSH execution
- **Configuration Management:** File-based and manual XCP-ng configuration with validation
- **BioXen Integration:** Designed specifically for biological computing and genomic data virtualization
- **CLI Entry Point:** Available via `bioxen-luavm` script after installation
- **PyPI Test Deployment:** Version 0.1.21 successfully deployed and tested
- **Experimental Networking:** The `networked=True` option works with LuaSocket for basic VMs
- **Library-Agnostic:** Package management uses external catalogs and SSH for remote installation
- **Interactive Features:** Full CLI integration with questionary-based prompts
- **Documentation:** Complete API, installation, and CLI integration guides included
- **Validation:** All Phase 3 functionality tested and validated (7/7 tests passed)

### Version History
- **0.1.18:** Phase 1 complete (basic VM management with factory pattern)
- **0.1.19:** Phase 2 complete (XCP-ng integration with XAPI client)
- **0.1.20:** Phase 2 refinements and additional XCP-ng features
- **0.1.21:** Phase 3 complete (interactive CLI and multi-VM support)
- **0.1.22:** Specification alignment and version consistency update

### Phase 3 Achievements
✅ **Interactive CLI** - Complete `bioxen-luavm` command-line interface  
✅ **Multi-VM Factory** - Enhanced VMManager with vm_type parameter support  
✅ **XCP-ng Integration** - Real XAPI client with template-based VM creation  
✅ **Configuration Management** - File-based and manual XCP-ng setup  
✅ **SSH Execution** - Remote Lua code execution via SSH sessions  
✅ **Package Management** - Lua package installation in remote VMs  
✅ **Documentation** - Complete API, installation, and CLI guides  
✅ **PyPI Deployment** - Successfully deployed to PyPI test repository  
✅ **Validation** - All functionality tested and working correctly  

### Next Steps
- **Production Deployment:** Deploy to main PyPI repository
- **Advanced Features:** Enhanced template management and resource allocation
- **Performance Optimization:** Improve SSH connection pooling and caching
- **Additional VM Types:** Support for Docker, Kubernetes, and other platforms
- **Monitoring Integration:** Add metrics and monitoring for distributed VMs
- **Security Enhancements:** Implement advanced authentication and encryption

---

*This specification reflects the complete Phase 3 implementation of pylua_bioxen_vm_lib version 0.1.22, updated September 1, 2025. All features are implemented, tested, and available via PyPI test deployment.*