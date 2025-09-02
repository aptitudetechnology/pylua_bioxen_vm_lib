# pylua_bioxen_vm_lib XO API Integration Specification

## Overview

Extension of pylua_bioxen_vm_lib (version 0.2.0) to support Xen Orchestra (XO) API integration alongside existing XAPI support. This Phase 4 enhancement adds multi-cluster management capabilities while maintaining backward compatibility with direct XCP-ng connections.

## Key Features (Phase 4)

- **XO API Integration** with REST-based VM management
- **Multi-Cluster Support** via centralized XO endpoint  
- **xo-cli Integration** for command-line operations
- **Dual API Support** - XO API and direct XAPI in same codebase
- **Enhanced CLI** with XO/XAPI selection
- **Backward Compatibility** with existing Phase 3 implementations
- **Simplified Configuration** for multi-cluster deployments

## VM Type Extension (Phase 4)

### New VM Type: "xo"

```python
# Create XO API VM
vm = create_vm("xo_vm", vm_type="xo", config=xo_config)
```

### Supported VM Types:
- `basic` - Local Lua process execution
- `xcpng` - Direct XAPI connection to single host (Phase 3)
- `xo` - XO API connection for multi-cluster management (Phase 4)

## XO API Configuration

### Configuration File: `xo_config.json`

```json
{
    "xo_api_url": "https://your-xo-server:443",
    "username": "admin@admin.net",
    "password": "your-xo-password",
    "default_pool": "pool-uuid-or-name",
    "template_name": "lua-bio-template",
    "vm_name_prefix": "bioxen-lua",
    "default_network": "network-name-or-uuid",
    "default_sr": "storage-name-or-uuid",
    "ssh_user": "root",
    "ssh_key_path": "/path/to/ssh/key",
    "xo_cli_path": "/usr/local/bin/xo-cli"
}
```

### XO API vs XAPI Configuration Comparison

| Feature | XAPI (Phase 3) | XO API (Phase 4) |
|---------|----------------|------------------|
| Endpoint | Direct host connection | Single XO server |
| Clusters | One per config | Multiple via XO |
| Authentication | Host credentials | XO user account |
| API Style | XML-RPC | REST/JSON |
| Management | Per-host basis | Centralized |

## XO API VM Class (Phase 4)

```python
import requests
import subprocess
from pylua_bioxen_vm_lib.xo_client import XOClient
from pylua_bioxen_vm_lib.ssh_session import SSHSession

class XOVM:
    """Xen Orchestra API VM integration (Phase 4)"""
    
    def __init__(self, vm_id, config=None):
        self.vm_id = vm_id
        self.config = config or {}
        
        # XO API client
        self.xo_client = XOClient(
            url=self.config.get('xo_api_url'),
            username=self.config.get('username'),
            password=self.config.get('password')
        )
        
        # SSH session for Lua execution
        self.ssh_session = SSHSession(
            user=self.config.get('ssh_user', 'root'),
            key_path=self.config.get('ssh_key_path')
        )
        
        # xo-cli integration
        self.xo_cli_path = self.config.get('xo_cli_path', 'xo-cli')
        
        self.vm_uuid = None
        self.vm_ip = None
    
    def start(self):
        """Start VM using XO API"""
        # Create VM from template via XO API
        vm_data = {
            "name": f"{self.config.get('vm_name_prefix', 'bioxen')}-{self.vm_id}",
            "template": self.config.get('template_name'),
            "pool": self.config.get('default_pool'),
            "network": self.config.get('default_network'),
            "sr": self.config.get('default_sr')
        }
        
        self.vm_uuid = self.xo_client.create_vm(vm_data)
        self.xo_client.start_vm(self.vm_uuid)
        self.vm_ip = self.xo_client.get_vm_ip(self.vm_uuid)
        
    def start_with_cli(self):
        """Alternative: Start VM using xo-cli"""
        cmd = [
            self.xo_cli_path, "vm.create",
            f"name={self.config.get('vm_name_prefix', 'bioxen')}-{self.vm_id}",
            f"template={self.config.get('template_name')}",
            f"sr={self.config.get('default_sr')}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.vm_uuid = result.stdout.strip()
            
    def execute_string(self, lua_code):
        """Execute Lua code via SSH (same as XCPngVM)"""
        if not self.vm_ip:
            raise VMManagerError("VM not started or IP not available")
        
        result = self.ssh_session.execute_command(
            host=self.vm_ip,
            command=f'lua -e "{lua_code}"'
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
        
    def stop(self):
        """Stop VM using XO API"""
        if self.vm_uuid:
            self.xo_client.shutdown_vm(self.vm_uuid)
```

## XO Client Implementation

```python
class XOClient:
    """REST client for Xen Orchestra API"""
    
    def __init__(self, url, username, password):
        self.base_url = url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.authenticate(username, password)
    
    def authenticate(self, username, password):
        """Authenticate with XO API"""
        auth_data = {"email": username, "password": password}
        response = self.session.post(f"{self.base_url}/api/v0/auth", json=auth_data)
        response.raise_for_status()
        self.token = response.json().get('token')
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})
    
    def create_vm(self, vm_data):
        """Create VM from template via XO API"""
        response = self.session.post(f"{self.base_url}/api/v0/vms", json=vm_data)
        response.raise_for_status()
        return response.json().get('uuid')
    
    def start_vm(self, vm_uuid):
        """Start VM via XO API"""
        response = self.session.post(f"{self.base_url}/api/v0/vms/{vm_uuid}/start")
        response.raise_for_status()
        
    def get_vm_ip(self, vm_uuid):
        """Get VM IP address via XO API"""
        response = self.session.get(f"{self.base_url}/api/v0/vms/{vm_uuid}")
        response.raise_for_status()
        vm_info = response.json()
        return vm_info.get('addresses', {}).get('0/ip', None)
        
    def shutdown_vm(self, vm_uuid):
        """Shutdown VM via XO API"""
        response = self.session.post(f"{self.base_url}/api/v0/vms/{vm_uuid}/shutdown")
        response.raise_for_status()
        
    def list_pools(self):
        """List available pools"""
        response = self.session.get(f"{self.base_url}/api/v0/pools")
        response.raise_for_status()
        return response.json()
```

## Enhanced CLI with XO Support (Phase 4)

### VM Type Selection Enhancement

```python
class BioXenLuavmCLI:
    """Enhanced CLI with XO API support"""
    
    def handle_vm_type_selection(self):
        """Enhanced VM type selection including XO"""
        vm_type = questionary.select(
            "Select VM type:",
            choices=[
                Choice(value="basic", name="Basic - Local Lua VMs"),
                Choice(value="xcpng", name="XCP-ng - Direct XAPI connection"),
                Choice(value="xo", name="Xen Orchestra - REST API (multi-cluster)"),
            ]
        ).ask()
        
        if vm_type == "xo":
            return self.handle_xo_configuration()
        elif vm_type == "xcpng":
            return self.handle_xcpng_configuration()
        else:
            return vm_type, None
    
    def handle_xo_configuration(self):
        """Handle XO API configuration"""
        config_method = questionary.select(
            "XO API configuration method:",
            choices=[
                Choice(value="file", name="Load from xo_config.json"),
                Choice(value="manual", name="Enter XO details manually"),
            ]
        ).ask()
        
        if config_method == "file":
            return self.load_xo_config_from_file()
        else:
            return self.configure_xo_manually()
    
    def configure_xo_manually(self):
        """Manual XO configuration with prompts"""
        config = {}
        config['xo_api_url'] = questionary.text("XO Server URL:").ask()
        config['username'] = questionary.text("XO Username:").ask()
        config['password'] = questionary.password("XO Password:").ask()
        config['template_name'] = questionary.text("Template Name:").ask()
        return "xo", config
```

## Factory Pattern Update (Phase 4)

### Enhanced create_vm Function

```python
def create_vm(vm_id="default", vm_type="basic", networked=False, persistent=False, 
              debug_mode=False, lua_executable="lua", config=None):
    """Enhanced VM factory with XO API support"""
    
    if vm_type == "basic":
        if networked:
            return NetworkedLuaVM(vm_id, debug_mode=debug_mode, lua_executable=lua_executable)
        return BasicLuaVM(vm_id, debug_mode=debug_mode, lua_executable=lua_executable)
    
    elif vm_type == "xcpng":
        if config is None:
            raise ValueError("XCP-ng VM type requires configuration")
        return XCPngVM(vm_id, config=config)
    
    elif vm_type == "xo":
        if config is None:
            raise ValueError("XO VM type requires configuration")
        return XOVM(vm_id, config=config)
    
    else:
        raise ValueError(f"Unknown VM type: {vm_type}")
```

## Usage Examples (Phase 4)

### XO API Basic Usage

```python
from pylua_bioxen_vm_lib import create_vm

# XO API configuration
xo_config = {
    "xo_api_url": "https://xo-server.example.com",
    "username": "admin@admin.net",
    "password": "xo_password",
    "template_name": "lua-bio-template",
    "default_pool": "production-pool",
    "ssh_user": "root",
    "ssh_key_path": "/home/user/.ssh/xo_key"
}

# Create XO VM
vm_xo = create_vm("bio_xo_vm", vm_type="xo", config=xo_config)

# Standard usage (same interface as XCPngVM)
vm_xo.start()
result = vm_xo.execute_string('return "Hello from XO VM"')
print(result['stdout'])
vm_xo.stop()
```

### Multi-API Comparison

```python
from pylua_bioxen_vm_lib import VMManager

# Configurations for different API types
xcpng_config = {
    "xapi_url": "https://xcpng-host:443",
    "username": "root", 
    "password": "xcpng_password",
    "template_name": "lua-bio-template"
}

xo_config = {
    "xo_api_url": "https://xo-server:443",
    "username": "admin@admin.net",
    "password": "xo_password", 
    "template_name": "lua-bio-template",
    "default_pool": "main-pool"
}

with VMManager(debug_mode=True) as manager:
    # Create VMs using different APIs
    direct_vm = manager.create_vm("direct", vm_type="xcpng", config=xcpng_config)
    orchestrated_vm = manager.create_vm("orchestrated", vm_type="xo", config=xo_config)
    
    # Same execution interface regardless of API type
    direct_result = manager.execute_vm_sync("direct", 'return "Direct XAPI"')
    xo_result = manager.execute_vm_sync("orchestrated", 'return "XO API"')
```

## CLI Integration Enhancement (Phase 4)

### Enhanced Interactive CLI

```bash
# Launch CLI with XO support
bioxen-luavm

# CLI workflow now includes:
# 1. Select VM type (basic/xcpng/xo)
# 2. Configure API settings (XAPI/XO)
# 3. Multi-cluster pool selection (for XO)
# 4. Template and resource selection
# 5. VM creation and management
```

### xo-cli Integration

```python
class XOCLIWrapper:
    """Wrapper for xo-cli command-line tool"""
    
    def __init__(self, xo_cli_path="xo-cli", xo_url=None, token=None):
        self.cli_path = xo_cli_path
        self.xo_url = xo_url
        self.token = token
    
    def list_vms(self, pool=None):
        """List VMs using xo-cli"""
        cmd = [self.cli_path, "vm.list"]
        if pool:
            cmd.extend(["--pool", pool])
        return self._execute_cli(cmd)
    
    def create_vm(self, name, template, pool=None):
        """Create VM using xo-cli"""
        cmd = [
            self.cli_path, "vm.create",
            f"name={name}",
            f"template={template}"
        ]
        if pool:
            cmd.extend(["--pool", pool])
        return self._execute_cli(cmd)
    
    def _execute_cli(self, cmd):
        """Execute xo-cli command"""
        if self.xo_url:
            cmd.extend(["--url", self.xo_url])
        if self.token:
            cmd.extend(["--token", self.token])
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise VMManagerError(f"xo-cli error: {result.stderr}")
        return result.stdout
```

## Configuration Management (Phase 4)

### Multi-API Configuration Support

```python
class ConfigManager:
    """Enhanced configuration management for multiple API types"""
    
    @staticmethod
    def load_config(vm_type):
        """Load configuration based on VM type"""
        config_files = {
            "xcpng": "xcpng_config.json",
            "xo": "xo_config.json"
        }
        
        config_file = config_files.get(vm_type)
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def validate_xo_config(config):
        """Validate XO API configuration"""
        required_fields = [
            'xo_api_url', 'username', 'password', 'template_name'
        ]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required XO config field: {field}")
        return True
```

## Enhanced Usage Patterns (Phase 4)

### Pattern 1: XO Multi-Cluster Management

```python
from pylua_bioxen_vm_lib import VMManager

# XO configuration for multi-cluster
xo_config = {
    "xo_api_url": "https://xo-central.company.com",
    "username": "biocompute@company.com",
    "password": "secure_password",
    "template_name": "lua-bio-template"
}

with VMManager(debug_mode=True) as manager:
    # Create VMs across different pools/clusters
    dev_vm = manager.create_vm("dev_analysis", vm_type="xo", config={
        **xo_config,
        "default_pool": "development-cluster",
        "vm_name_prefix": "dev-bioxen"
    })
    
    prod_vm = manager.create_vm("prod_analysis", vm_type="xo", config={
        **xo_config, 
        "default_pool": "production-cluster",
        "vm_name_prefix": "prod-bioxen"
    })
    
    # Execute biological analysis across clusters
    dev_result = manager.execute_vm_sync("dev_analysis", '''
        -- Development sequence analysis
        local test_sequence = "ATCGATCG"
        return "Dev analysis complete: " .. #test_sequence .. " bases"
    ''')
    
    prod_result = manager.execute_vm_sync("prod_analysis", '''
        -- Production sequence analysis  
        local prod_sequence = "ATCGATCGATCGATCGATCG"
        return "Prod analysis complete: " .. #prod_sequence .. " bases"
    ''')
```

### Pattern 2: API Selection Based on Environment

```python
from pylua_bioxen_vm_lib import create_vm
import os

def create_bio_vm(vm_id, environment="dev"):
    """Create VM with appropriate API based on environment"""
    
    if environment == "local":
        return create_vm(vm_id, vm_type="basic")
    
    elif environment == "dev":
        # Use direct XAPI for development
        config = load_xcpng_config()
        return create_vm(vm_id, vm_type="xcpng", config=config)
    
    elif environment == "prod":
        # Use XO API for production multi-cluster
        config = load_xo_config()
        return create_vm(vm_id, vm_type="xo", config=config)
    
    else:
        raise ValueError(f"Unknown environment: {environment}")

# Usage
vm = create_bio_vm("sequence_analyzer", environment=os.getenv("ENV", "local"))
```

### Pattern 3: Hybrid API Usage

```python
from pylua_bioxen_vm_lib import VMManager

# Use both APIs in same workflow
with VMManager(debug_mode=True) as manager:
    # Direct XAPI for dedicated host
    dedicated_vm = manager.create_vm("dedicated_compute", 
                                   vm_type="xcpng", 
                                   config=xcpng_config)
    
    # XO API for cluster resources
    cluster_vm = manager.create_vm("cluster_compute",
                                 vm_type="xo", 
                                 config=xo_config)
    
    # Coordinate analysis across both
    dedicated_result = manager.execute_vm_sync("dedicated_compute", 
                                             'return "Dedicated analysis"')
    cluster_result = manager.execute_vm_sync("cluster_compute", 
                                           'return "Cluster analysis"')
```

## Dependencies (Phase 4)

### Additional Dependencies for XO Support

```
requests>=2.25.0        # HTTP client (existing)
paramiko>=2.7.0         # SSH client (existing)
urllib3>=1.26.0         # HTTP library (existing)
questionary>=1.10.0     # Interactive CLI (existing)
pyjwt>=2.4.0           # JWT token handling for XO API
```

### Optional xo-cli Integration

```bash
# Install xo-cli globally (optional)
npm install -g xo-cli

# Or specify custom path in configuration
{
    "xo_cli_path": "/usr/local/bin/xo-cli"
}
```

## Module Structure (Phase 4)

```
pylua_bioxen_vm_lib/
├── cli_main.py              # Enhanced CLI with XO support
├── xapi_client.py           # XAPI client (Phase 3)
├── xo_client.py             # XO API client (Phase 4)
├── xo_cli_wrapper.py        # xo-cli integration (Phase 4)
├── ssh_session.py           # SSH session management
├── xcp_ng_integration.py    # XCPngVM implementation  
├── xo_integration.py        # XOVM implementation (Phase 4)
├── config_manager.py        # Multi-API configuration (Phase 4)
├── vm_manager.py            # Enhanced with XO support
└── interactive_session.py   # Session management
```

## Configuration Comparison

### When to Use Each API Type

| Use Case | Recommended API | Reason |
|----------|----------------|---------|
| Single XCP-ng host | `xcpng` (XAPI) | Direct, simple setup |
| Multiple clusters | `xo` (XO API) | Centralized management |
| Complex deployments | `xo` (XO API) | Better tooling and UI |
| Simple MVP testing | `xcpng` (XAPI) | Fewer dependencies |
| Production workflows | `xo` (XO API) | More robust and scalable |

### Migration Path

```python
# Phase 3 (current)
vm = create_vm("test", vm_type="xcpng", config=xcpng_config)

# Phase 4 (XO API)
vm = create_vm("test", vm_type="xo", config=xo_config)

# Same interface, different backend!
vm.start()
result = vm.execute_string('return 2 + 2')
vm.stop()
```

## Advantages of XO API Integration

### For Your Use Case:
- **Simplified Configuration** - One endpoint for multiple clusters
- **Better REST API** - JSON instead of XML-RPC
- **Proven Reliability** - Used by Terraform/Pulumi providers
- **Community Support** - Follows XCP-ng community best practices

### For Biological Computing:
- **Multi-Cluster Compute** - Distribute analysis across clusters
- **Resource Management** - Better allocation via XO's resource tracking
- **Monitoring Integration** - XO provides better VM monitoring
- **Backup Integration** - XO backup scheduling for analysis environments

## Testing Strategy (Phase 4)

### MVP Testing with Both APIs

```python
# Test both API types with same biological computation
test_sequence = "ATCGATCGATCGAAATTTCCCGGG"

# Test with direct XAPI
xcpng_vm = create_vm("xcpng_test", vm_type="xcpng", config=xcpng_config)
xcpng_result = test_sequence_analysis(xcpng_vm, test_sequence)

# Test with XO API  
xo_vm = create_vm("xo_test", vm_type="xo", config=xo_config)
xo_result = test_sequence_analysis(xo_vm, test_sequence)

# Compare results
assert xcpng_result == xo_result, "API implementations should produce same results"
```

### Success Criteria (Phase 4)

- [ ] XO API client successfully authenticates
- [ ] VM creation via XO REST API works
- [ ] SSH execution identical to XAPI implementation
- [ ] CLI prompts for XO configuration
- [ ] Multi-cluster pool selection
- [ ] Package installation via XO VMs
- [ ] Backward compatibility with Phase 3 code
- [ ] Configuration file migration tools

## Future Enhancements

### Phase 5 Possibilities:
- **GraphQL API Support** - If XO adds GraphQL endpoints
- **Kubernetes Integration** - Container-based Lua VMs
- **Cloud Provider APIs** - AWS, Azure, GCP VM creation
- **Monitoring Integration** - Prometheus/Grafana for VM metrics
- **Auto-scaling** - Dynamic VM creation based on workload

## Version Timeline

- **0.1.22** - Phase 3 complete (XAPI integration)
- **0.2.0** - Phase 4 planned (XO API integration)
- **0.3.0** - Phase 5 future (Advanced features)

---

*This specification outlines the planned Phase 4 XO API integration for pylua_bioxen_vm_lib. Implementation would follow the same thorough testing approach used in Phases 1-3, with backward compatibility maintained for existing XAPI users.*