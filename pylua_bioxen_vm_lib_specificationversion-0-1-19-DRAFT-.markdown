# pylua_bioxen_vm_lib Specification v2.0

## Overview

The **pylua_bioxen_vm_lib** (target version 0.2.0) is a Python library for managing Lua virtual machines within the BioXen framework, now extended with XCP-ng hypervisor support and xAPI activity tracking. It's designed for biological computation, genomic data virtualization, and distributed computing workflows with comprehensive activity monitoring.

**New Key Features (v2.0):**
- **Multi-VM Architecture**: Support for BasicLuaVM and XCPngVM types
- **XCP-ng Integration**: Full hypervisor support via XAPI REST interface
- **xAPI Activity Tracking**: IEEE 9274.1.1 compliant learning record generation
- **LLM-Generated Middleware**: Automated XAPI client code generation
- **Template-Based Deployment**: Rapid VM provisioning using XCP-ng templates
- **Enhanced Networking**: XCP-ng network management integration

**Existing Features (Maintained):**
- Synchronous and asynchronous Lua code execution
- Interactive session management
- Library-agnostic package management
- Isolated Lua environments
- Perfect for lightweight, sandboxed Lua VMs in biological workflows

---

## Architecture Overview

### Multi-VM Foundation

The library now supports multiple VM backend types through a unified interface:

```python
# VM Type Hierarchy
BaseLuaVM (Abstract)
├── BasicLuaVM (Process-based, original implementation)
└── XCPngVM (Hypervisor-based, new MVP implementation)
```

### Factory Pattern

```python
from pylua_bioxen_vm_lib import LuaVMFactory

# Create different VM types
basic_vm = LuaVMFactory.create_vm("basic", "my_basic_vm")
xcpng_vm = LuaVMFactory.create_vm("xcpng", "my_xcpng_vm", config={
    "template": "lua-bio-template",
    "xcpng_host": "192.168.1.100",
    "memory": "2GB",
    "vcpus": 2
})
```

---

## Quick Start

### Basic VM (Backward Compatible)
```python
from pylua_bioxen_vm_lib import create_vm

# Create and use a VM (same as v0.1.18)
vm = create_vm("my_vm")
result = vm.execute_string('return 2 + 2')
print(result['stdout'])  # Output: 4
```

### XCP-ng VM (New)
```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Create XCP-ng VM from template
    vm = manager.create_vm("xcpng_vm", vm_type="xcpng", config={
        "template": "lua-bio-template",
        "xcpng_host": "192.168.1.100",
        "memory": "2GB",
        "vcpus": 2
    })
    
    # Execute biological computation
    result = manager.execute_vm_sync("xcpng_vm", '''
        require("bio_compute")
        sequence = "ATCGTAGCTACG"
        analysis = bio_compute.analyze_dna(sequence)
        print("Analysis:", analysis)
    ''')
    
    print(result['stdout'])
```

### xAPI Activity Tracking (New)
```python
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.xapi import XAPITracker

# Enable activity tracking
tracker = XAPITracker(lrs_endpoint="https://my-lrs.com", auth_token="token123")

with VMManager(debug_mode=True, xapi_tracker=tracker) as manager:
    vm = manager.create_vm("tracked_vm")
    
    # VM activities automatically tracked as xAPI statements
    result = manager.execute_vm_sync("tracked_vm", 'print("Tracked execution")')
```

---

## Core Components

### 1. VM Management

#### VMManager (Enhanced)

**New Features:**
- Multi-VM type support through factory pattern
- XCP-ng configuration management
- xAPI activity tracking integration
- XAPI middleware orchestration

**Enhanced Methods:**
```python
class VMManager:
    def __init__(self, debug_mode=False, xapi_tracker=None):
        """Initialize with optional xAPI tracking"""
    
    def create_vm(self, vm_id, vm_type="basic", config=None):
        """Create VM of specified type (basic/xcpng)"""
    
    def get_vm_info(self, vm_id):
        """Get VM status and resource information"""
    
    def migrate_vm(self, vm_id, target_host):
        """Migrate XCP-ng VM to different host (XCP-ng only)"""
```

#### LuaVMFactory (New)

**Purpose:** Central factory for creating different VM types

```python
class LuaVMFactory:
    @staticmethod
    def create_vm(vm_type, vm_id, config=None):
        """Factory method for VM creation"""
        
    @staticmethod
    def get_supported_types():
        """Returns list of supported VM types"""
        
    @staticmethod
    def validate_config(vm_type, config):
        """Validates configuration for VM type"""
```

#### BaseLuaVM (New Abstract Class)

**Purpose:** Common interface for all VM types

```python
from abc import ABC, abstractmethod

class BaseLuaVM(ABC):
    @abstractmethod
    def start(self): pass
    
    @abstractmethod
    def stop(self): pass
    
    @abstractmethod
    def execute(self, lua_code): pass
    
    @abstractmethod
    def install_package(self, package): pass
    
    @abstractmethod
    def get_status(self): pass
```

### 2. XCP-ng Integration

#### XCPngVM Class (New)

**Purpose:** XCP-ng hypervisor integration via XAPI

```python
class XCPngVM(BaseLuaVM):
    def __init__(self, vm_id, config):
        """Initialize XCP-ng VM with XAPI configuration"""
    
    def start(self):
        """Create and start VM using XCP-ng template via XAPI"""
    
    def stop(self):
        """Gracefully shutdown VM via XAPI"""
    
    def execute(self, lua_code):
        """Execute Lua code via SSH connection"""
    
    def install_package(self, package):
        """Install Lua packages via SSH and curator"""
    
    def snapshot(self, snapshot_name):
        """Create VM snapshot via XAPI"""
    
    def restore_snapshot(self, snapshot_name):
        """Restore VM from snapshot via XAPI"""
```

#### XAPI Client (LLM-Generated Middleware)

**Purpose:** HTTP client for XCP-ng XAPI communication

```python
class XAPIClient:
    def __init__(self, host, username, password):
        """Initialize XAPI session"""
    
    def create_vm_from_template(self, template_name, vm_name, config):
        """Create VM from XCP-ng template"""
    
    def start_vm(self, vm_ref): 
        """Start VM instance"""
    
    def stop_vm(self, vm_ref):
        """Stop VM instance"""
    
    def get_vm_status(self, vm_ref):
        """Get VM status and metrics"""
    
    def create_snapshot(self, vm_ref, snapshot_name):
        """Create VM snapshot"""
```

#### Configuration Management

**XCP-ng VM Configuration:**
```python
xcpng_config = {
    "xcpng_host": "192.168.1.100",
    "xcpng_username": "admin", 
    "xcpng_password": "password",
    "template": "lua-bio-template",
    "memory": "2GB",
    "vcpus": 2,
    "storage": "20GB",
    "network": "default",
    "ssh_key": "/path/to/ssh/key"
}
```

### 3. xAPI Integration

#### XAPITracker Class (New)

**Purpose:** IEEE 9274.1.1 compliant activity tracking

```python
class XAPITracker:
    def __init__(self, lrs_endpoint, auth_token=None, auth_user=None, auth_pass=None):
        """Initialize xAPI LRS connection"""
    
    def track_vm_creation(self, vm_id, vm_type, agent, config):
        """Track VM creation activity"""
    
    def track_code_execution(self, vm_id, lua_code, result, agent):
        """Track Lua code execution"""
    
    def track_package_installation(self, vm_id, package_name, result, agent):
        """Track package installation activity"""
    
    def send_statement(self, statement):
        """Send xAPI statement to LRS"""
    
    def get_agent_profile(self, agent_id):
        """Retrieve agent profile from LRS"""
```

#### xAPI Statement Generation

**VM Activity Mapping:**
- **VM Creation** → `experienced` activity with VM configuration as context
- **Code Execution** → `attempted`/`completed` activity with code and results
- **Package Installation** → `completed` activity with package metadata
- **Session Management** → `started`/`terminated` session activities

**Statement Structure:**
```json
{
    "actor": {"name": "researcher@biolab.org", "mbox": "mailto:researcher@biolab.org"},
    "verb": {"id": "http://adlnet.gov/expapi/verbs/experienced"},
    "object": {
        "id": "http://bioxen.org/activities/vm-creation",
        "definition": {
            "name": {"en": "VM Creation"},
            "description": {"en": "Created Lua VM for biological computation"}
        }
    },
    "context": {
        "extensions": {
            "http://bioxen.org/vm_type": "xcpng",
            "http://bioxen.org/vm_id": "my_xcpng_vm"
        }
    }
}
```

---

## Enhanced Components

### 1. Enhanced VM Creation

```python
from pylua_bioxen_vm_lib import create_vm, VMManager
from pylua_bioxen_vm_lib.xapi import XAPITracker

# Enhanced create_vm function (backward compatible)
def create_vm(vm_id="default", vm_type="basic", networked=False, 
              persistent=False, debug_mode=False, lua_executable="lua",
              config=None, xapi_tracker=None):
    """Create VM with optional type specification and xAPI tracking"""
```

### 2. Enhanced VMManager

```python
class VMManager:
    def __init__(self, debug_mode=False, xapi_tracker=None):
        """Initialize with optional xAPI tracking"""
        self.xapi_tracker = xapi_tracker
        self.vm_factory = LuaVMFactory()
        self.session_manager = SessionManager()
    
    def create_vm(self, vm_id, vm_type="basic", config=None):
        """Create VM with activity tracking"""
        vm = self.vm_factory.create_vm(vm_type, vm_id, config)
        
        # Track VM creation if xAPI enabled
        if self.xapi_tracker:
            self.xapi_tracker.track_vm_creation(vm_id, vm_type, self._get_current_agent(), config)
        
        return vm
```

### 3. Enhanced Package Management

#### Extended Curator

**XCP-ng Package Management:**
```python
class PackageInstaller:
    def install_package_in_vm(self, package_name, vm_id, vm_type="basic"):
        """Install package with VM type awareness"""
        if vm_type == "xcpng":
            return self._install_via_ssh(package_name, vm_id)
        else:
            return self._install_local(package_name, vm_id)
    
    def _install_via_ssh(self, package_name, vm_id):
        """Install package in XCP-ng VM via SSH"""
```

### 4. Enhanced Networking

#### XCP-ng Network Management

```python
class NetworkManager:
    def __init__(self, vm_type="basic"):
        """Initialize network manager for VM type"""
    
    def configure_xcpng_network(self, vm_id, network_config):
        """Configure XCP-ng VM networking via XAPI"""
    
    def create_private_network(self, network_name, vm_ids):
        """Create isolated network for XCP-ng VMs"""
```

---

## New Modules

### 1. xcp_ng_integration.py (New)

**Core XCP-ng functionality module:**

```python
# Main classes and functions
class XCPngVM(BaseLuaVM)
class XAPIClient  # LLM-generated middleware
class XCPngConfig
class XCPngTemplateManager

# Utility functions
def validate_xcpng_connection(host, credentials)
def list_available_templates(xapi_client)
def map_bioxen_config_to_xapi(config)
```

### 2. xapi_integration.py (New)

**xAPI activity tracking module:**

```python
# Main classes
class XAPITracker
class XAPIStatementBuilder
class XAPIAgent
class XAPIActivity

# Utility functions  
def create_vm_activity_statement(vm_id, vm_type, agent, config)
def create_execution_statement(vm_id, code, result, agent)
def create_package_statement(vm_id, package, result, agent)
```

### 3. vm_factory.py (New)

**VM creation factory module:**

```python
class LuaVMFactory
class VMConfig
class VMTypeRegistry

# Registration functions
def register_vm_type(vm_type, vm_class)
def get_supported_vm_types()
def validate_vm_config(vm_type, config)
```

---

## Updated API Reference

### Core Functions

#### create_vm() - Enhanced
```python
def create_vm(vm_id="default", vm_type="basic", networked=False, 
              persistent=False, debug_mode=False, lua_executable="lua",
              config=None, xapi_tracker=None):
    """
    Create a Lua VM with specified backend type
    
    Parameters:
    - vm_id: Unique VM identifier
    - vm_type: "basic" (process) or "xcpng" (hypervisor) 
    - config: VM-specific configuration dict
    - xapi_tracker: Optional XAPITracker for activity logging
    
    Returns: BaseLuaVM instance
    """
```

### VMManager Class - Enhanced

#### New Methods
```python
def create_vm(self, vm_id, vm_type="basic", config=None):
    """Create VM with type specification and tracking"""

def get_vm_info(self, vm_id):
    """Get comprehensive VM information including status, resources, type"""

def migrate_vm(self, vm_id, target_host):
    """Migrate XCP-ng VM to different host (XCP-ng only)"""

def snapshot_vm(self, vm_id, snapshot_name):
    """Create VM snapshot (XCP-ng only)"""

def restore_vm(self, vm_id, snapshot_name): 
    """Restore VM from snapshot (XCP-ng only)"""

def get_vm_metrics(self, vm_id):
    """Get VM performance metrics"""
```

### XCPngVM Class - New

```python
class XCPngVM(BaseLuaVM):
    def __init__(self, vm_id, config):
        """Initialize with XCP-ng configuration and XAPI client"""
    
    def start(self):
        """Create VM from template and start via XAPI"""
    
    def stop(self):
        """Gracefully shutdown VM via XAPI"""
    
    def execute(self, lua_code):
        """Execute Lua code via SSH connection"""
    
    def install_package(self, package):
        """Install packages via SSH and curator"""
    
    def get_console_access(self):
        """Get VNC console URL for VM"""
    
    def resize_vm(self, memory=None, vcpus=None):
        """Resize VM resources via XAPI"""
```

### XAPITracker Class - New

```python
class XAPITracker:
    def __init__(self, lrs_endpoint, auth_token=None, auth_user=None, auth_pass=None):
        """Initialize LRS connection"""
    
    def track_vm_creation(self, vm_id, vm_type, agent, config):
        """Generate and send VM creation statement"""
    
    def track_code_execution(self, vm_id, lua_code, result, agent, duration=None):
        """Track code execution with performance data"""
    
    def track_package_installation(self, vm_id, package_name, result, agent):
        """Track package installation outcomes"""
    
    def track_session_lifecycle(self, vm_id, action, agent):
        """Track session start/stop/attach/detach"""
    
    def query_activities(self, agent=None, activity=None, since=None):
        """Query LRS for activity history"""
    
    def get_vm_analytics(self, vm_id, timeframe=None):
        """Get analytics for specific VM usage"""
```

---

## Configuration Management

### Basic VM Configuration (Existing)
```python
basic_config = {
    "lua_executable": "lua",
    "working_directory": "/tmp/lua_vm",
    "environment_vars": {"LUA_PATH": "/custom/path"}
}
```

### XCP-ng VM Configuration (New)
```python
xcpng_config = {
    # XCP-ng Connection
    "xcpng_host": "192.168.1.100",
    "xcpng_username": "admin",
    "xcpng_password": "password",  # Or use SSH key auth
    
    # VM Specification
    "template": "lua-bio-template",
    "memory": "2GB",
    "vcpus": 2,
    "storage": "20GB",
    
    # Networking
    "network": "default",
    "ip_address": "dhcp",  # or static IP
    
    # Access
    "ssh_username": "ubuntu",
    "ssh_key_path": "/path/to/ssh/key",
    
    # Optional: Advanced features
    "enable_snapshots": True,
    "enable_migration": True,
    "resource_limits": {
        "cpu_cap": 80,
        "memory_max": "4GB"
    }
}
```

### xAPI Configuration (New)
```python
xapi_config = {
    "lrs_endpoint": "https://my-lrs.com/xapi",
    "auth_method": "basic",  # or "oauth", "token"
    "auth_user": "username",
    "auth_pass": "password",
    "auth_token": "bearer_token",
    
    # Activity Mapping
    "activity_base_uri": "http://bioxen.org/activities",
    "agent_base_uri": "http://bioxen.org/agents",
    
    # Tracking Options
    "track_vm_lifecycle": True,
    "track_code_execution": True,
    "track_package_management": True,
    "track_performance_metrics": True,
    
    # Statement Buffering
    "buffer_statements": True,
    "buffer_size": 100,
    "flush_interval": 30  # seconds
}
```

---

## Package Management Extensions

### Enhanced Package Installation

#### For XCP-ng VMs
```python
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller

installer = PackageInstaller()

# Install in XCP-ng VM via SSH
installer.install_package_in_vm("bio_sequence_analysis", 
                                vm_id="xcpng_vm", 
                                vm_type="xcpng")

# Install with tracking
installer.install_package_in_vm("genomic_tools",
                                vm_id="xcpng_vm",
                                vm_type="xcpng", 
                                track_with_xapi=True,
                                agent="researcher@biolab.org")
```

### Environment Management for XCP-ng

```python
from pylua_bioxen_vm_lib.env import EnvironmentManager

env_manager = EnvironmentManager(vm_type="xcpng")

# Create isolated environment in XCP-ng VM
env_manager.create_environment("bio_env", vm_id="xcpng_vm")
env_manager.activate_environment("bio_env", vm_id="xcpng_vm")
```

---

## Interactive Sessions with XCP-ng

### Enhanced Interactive Session Support

```python
from pylua_bioxen_vm_lib import VMManager
import time

manager = VMManager(debug_mode=True)

# Create interactive XCP-ng session
session = manager.create_interactive_vm("xcpng_interactive", vm_type="xcpng", config={
    "template": "lua-bio-template",
    "xcpng_host": "192.168.1.100",
    "memory": "2GB"
})

# Send commands via SSH
manager.send_input("xcpng_interactive", "x = 100\nprint('XCP-ng VM Value:', x)\n")
time.sleep(1.0)  # Allow for network latency

# Read results
output = manager.read_output("xcpng_interactive")
print(output)

# Clean up
manager.terminate_vm_session("xcpng_interactive")
```

---

## Networking Extensions

### XCP-ng Network Management

```python
from pylua_bioxen_vm_lib.networking import NetworkManager

# Configure XCP-ng networking
network_manager = NetworkManager(vm_type="xcpng")

# Create private network for biological workflow
network_manager.create_private_network("bio_compute_net", 
                                      vm_ids=["vm1", "vm2", "vm3"])

# Configure inter-VM communication
network_manager.configure_vm_networking("xcpng_vm", {
    "network": "bio_compute_net",
    "ip_address": "10.0.1.10",
    "ports": [22, 8080, 9000]  # SSH + custom app ports
})
```

---

## Error Handling Extensions

### New Exception Classes

```python
# XCP-ng specific exceptions
class XCPngConnectionError(VMManagerError):
    """XCP-ng host connection failed"""

class XCPngAPIError(VMManagerError):
    """XAPI operation failed"""

class XCPngTemplateError(VMManagerError):
    """Template not found or invalid"""

class XCPngResourceError(VMManagerError):
    """Insufficient resources for VM"""

# xAPI specific exceptions  
class XAPIConnectionError(Exception):
    """LRS connection failed"""

class XAPIStatementError(Exception):
    """Invalid xAPI statement format"""

class XAPIAuthenticationError(Exception):
    """LRS authentication failed"""
```

### Enhanced Error Handling

```python
from pylua_bioxen_vm_lib.exceptions import XCPngConnectionError, XAPIConnectionError

try:
    with VMManager() as manager:
        vm = manager.create_vm("xcpng_vm", vm_type="xcpng", config=xcpng_config)
        result = manager.execute_vm_sync("xcpng_vm", lua_code)
        
except XCPngConnectionError as e:
    print(f"Failed to connect to XCP-ng: {e}")
except XAPIConnectionError as e:
    print(f"Failed to send activity data: {e}")
```

---

## Usage Patterns

### Pattern 5: XCP-ng VM with Activity Tracking

```python
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.xapi import XAPITracker

# Set up activity tracking
tracker = XAPITracker(
    lrs_endpoint="https://research-lrs.biolab.org/xapi",
    auth_user="research_team",
    auth_pass="secure_password"
)

# Configure XCP-ng VM
xcpng_config = {
    "xcpng_host": "192.168.1.100",
    "template": "lua-bio-template",
    "memory": "4GB",
    "vcpus": 4
}

with VMManager(debug_mode=True, xapi_tracker=tracker) as manager:
    # Create tracked XCP-ng VM
    vm = manager.create_vm("bio_analysis_vm", vm_type="xcpng", config=xcpng_config)
    
    # Execute biological analysis (automatically tracked)
    result = manager.execute_vm_sync("bio_analysis_vm", '''
        require("genomics")
        sequence = "ATCGTAGCTACGATTGC"
        gc_content = genomics.calculate_gc_content(sequence)
        motifs = genomics.find_motifs(sequence, {"ATCG", "TACG"})
        
        print("GC Content:", gc_content)
        print("Motifs found:", #motifs)
        
        return {gc_content = gc_content, motif_count = #motifs}
    ''')
    
    print("Analysis Results:", result['stdout'])
    
    # Create snapshot for reproducibility
    manager.snapshot_vm("bio_analysis_vm", "post_analysis_snapshot")
```

### Pattern 6: Distributed Biological Computing

```python
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.networking import NetworkManager

# Create compute cluster
with VMManager(debug_mode=True) as manager:
    # Create network for cluster
    network_manager = NetworkManager(vm_type="xcpng")
    network_manager.create_private_network("bio_cluster", 
                                          ["worker1", "worker2", "coordinator"])
    
    # Deploy worker VMs
    for i in range(2):
        vm = manager.create_vm(f"worker{i+1}", vm_type="xcpng", config={
            "template": "lua-worker-template",
            "memory": "8GB",
            "vcpus": 8,
            "network": "bio_cluster"
        })
    
    # Deploy coordinator VM
    coordinator = manager.create_vm("coordinator", vm_type="xcpng", config={
        "template": "lua-coordinator-template", 
        "memory": "4GB",
        "vcpus": 2,
        "network": "bio_cluster"
    })
    
    # Distribute genomic analysis task
    sequences = ["ATCGTAGC", "GCTACGAT", "TACGATCG"]
    for i, seq in enumerate(sequences):
        manager.execute_vm_async(f"worker{i%2+1}", f'''
            require("distributed_genomics")
            result = distributed_genomics.analyze_sequence("{seq}")
            distributed_genomics.send_result_to_coordinator(result)
        ''')
```

### Pattern 7: Research Workflow with Full Tracking

```python
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.xapi import XAPITracker
import time

# Research workflow with comprehensive tracking
tracker = XAPITracker(
    lrs_endpoint="https://university-lrs.edu/xapi",
    auth_token="research_project_token"
)

with VMManager(xapi_tracker=tracker) as manager:
    # Create research VM
    vm = manager.create_vm("research_vm", vm_type="xcpng", config={
        "template": "research-lua-template",
        "memory": "16GB",
        "vcpus": 8,
        "storage": "100GB"
    })
    
    # Install research packages (tracked)
    from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
    installer = PackageInstaller()
    installer.install_package_in_vm("bioinformatics_suite", "research_vm", "xcpng")
    installer.install_package_in_vm("statistical_analysis", "research_vm", "xcpng")
    
    # Execute research computation (tracked)
    research_code = '''
        require("bioinformatics_suite")
        require("statistical_analysis")
        
        -- Load genomic dataset
        dataset = bioinformatics_suite.load_dataset("sample_genomes.fasta")
        
        -- Perform analysis
        results = {}
        for i, genome in ipairs(dataset) do
            analysis = bioinformatics_suite.full_analysis(genome)
            stats = statistical_analysis.compute_stats(analysis)
            table.insert(results, {genome_id = i, analysis = analysis, stats = stats})
        end
        
        -- Export results
        bioinformatics_suite.export_results(results, "research_output.json")
        print("Analysis complete. Processed", #results, "genomes")
        
        return results
    '''
    
    result = manager.execute_vm_sync("research_vm", research_code)
    
    # Create research snapshot
    manager.snapshot_vm("research_vm", "final_analysis_state")
    
    print("Research workflow completed!")
    print("Results:", result['stdout'])
```

---

## Installation & Dependencies

### System Requirements
- **Python 3.7+**
- **Lua interpreter** (for BasicLuaVM)
- **XCP-ng host** (for XCPngVM) 
- **SSH client tools**
- **Network connectivity** to XCP-ng host and LRS

### Enhanced Installation

```bash
# Install the Python library
pip install pylua_bioxen_vm_lib

# Basic VM dependencies
luarocks install luasocket

# XCP-ng integration dependencies  
sudo apt-get install curl jq ssh-client sshpass

# Verify XCP-ng connectivity
pylua-bioxen verify-xcpng --host 192.168.1.100 --user admin
```

### Python Dependencies (Updated)

```python
# requirements.txt
requests>=2.31.0
paramiko>=3.0.0      # SSH communication for XCP-ng VMs
urllib3>=1.26.0      # HTTP client for XAPI
pexpect>=4.8.0       # Interactive session management
cryptography>=3.4.8  # SSH key management
```

---

## Configuration Files

### Global Configuration

**~/.pylua_bioxen/config.yaml**
```yaml
# Default VM type
default_vm_type: basic

# XCP-ng hosts
xcpng_hosts:
  default:
    host: "192.168.1.100" 
    username: "admin"
    password_env: "XCPNG_PASSWORD"  # Environment variable
    ssh_key: "~/.ssh/xcpng_key"
    
  production:
    host: "xcpng-prod.biolab.org"
    username: "admin"
    auth_method: "ssh_key"
    ssh_key: "~/.ssh/xcpng_prod_key"

# xAPI Configuration
xapi:
  default_lrs: "https://research-lrs.biolab.org/xapi"
  auth_method: "basic"
  username: "research_team"
  password_env: "LRS_PASSWORD"
  
  # Activity tracking settings
  track_by_default: true
  buffer_statements: true
  buffer_size: 100
  flush_interval: 30

#