# GitHub Copilot Instructions - Phase 2: XCP-ng Integration Basics

## Context Files to Read
Please analyze these specification files in the project root:
- `spec-report.md` - Current pylua_bioxen_vm_lib specification (v0.1.18)
- `xcp-ng-support.md` - Extended specification for XCP-ng integration MVP
- `xcp-ng-support-report.md` - Audit report with implementation requirements

## Phase 2 Objectives
Implement basic XCP-ng integration via XAPI. This phase transforms the XCPngVM placeholder from Phase 1 into a working implementation that can:
1. Create and manage XCP-ng VMs using XAPI REST calls
2. Execute Lua code in XCP-ng VMs via SSH
3. Handle basic VM lifecycle (start, stop, cleanup)
4. Install packages in XCP-ng VMs using existing curator over SSH

## Prerequisites
Phase 1 must be complete with:
- Factory pattern working with BasicLuaVM and XCPngVM placeholder
- `vm_type` parameter in create_vm()
- Backward compatibility maintained

## Files to Create/Modify

### 1. Create `pylua_bioxen_vm_lib/xcp_ng_integration.py` (NEW FILE)
**Task**: Implement XCPngVM class and XAPI client

**Core Components Needed**:

#### XAPIClient Class
```python
class XAPIClient:
    """HTTP client for XCP-ng XAPI communication"""
    
    def __init__(self, host, username, password, verify_ssl=False):
        # XAPI session management
        # HTTP connection setup using requests
    
    def authenticate(self):
        # POST to /api/session for authentication
        # Store session token for subsequent calls
    
    def create_vm_from_template(self, template_name, vm_name, config):
        # POST to create VM from template
        # Return VM UUID for management
    
    def start_vm(self, vm_uuid):
        # POST to start VM
    
    def stop_vm(self, vm_uuid):
        # POST to gracefully stop VM
    
    def get_vm_ip(self, vm_uuid):
        # GET VM network info to find IP for SSH
    
    def destroy_vm(self, vm_uuid):
        # DELETE VM completely
```

#### XCPngVM Class
```python
class XCPngVM:
    """XCP-ng VM implementation using XAPI"""
    
    def __init__(self, vm_id, config=None):
        # Initialize XAPI client
        # Store VM configuration
        # Setup SSH client (paramiko)
    
    def start(self):
        # Create VM from template using XAPI
        # Wait for VM to boot and get IP
        # Test SSH connectivity
    
    def stop(self):
        # Gracefully shutdown VM via XAPI
        # Cleanup SSH connections
    
    def execute_string(self, lua_code):
        # SSH to VM and execute Lua code
        # Return result in same format as BasicLuaVM
        # Handle SSH errors and map to existing exceptions
    
    def install_package(self, package_name):
        # Use curator over SSH to install packages
        # Leverage existing package management logic
```

**Requirements**:
- Use `requests` library for XAPI HTTP communication
- Use `paramiko` library for SSH to VMs
- Handle XAPI authentication and session management
- Map XAPI errors to existing exception types from `exceptions.py`
- Return execution results in same format as BasicLuaVM
- Support basic resource configuration (memory, CPU, template)

### 2. Update `pylua_bioxen_vm_lib/vm_manager.py`
**Task**: Replace XCPngVM placeholder with actual import and usage

**Requirements**:
- Import XCPngVM from xcp_ng_integration module
- Update factory pattern to use real XCPngVM class
- Add XCP-ng configuration validation
- Handle XCP-ng connection parameters in config dict
- Maintain all existing VMManager functionality

**Expected Config Structure**:
```python
config = {
    "xcpng_host": "192.168.1.100",
    "xcpng_username": "root", 
    "xcpng_password": "password",
    "template": "lua-bio-template",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": False
}
```

### 3. Update `pylua_bioxen_vm_lib/networking.py`
**Task**: Add XCP-ng network configuration support

**Requirements**:
- Add placeholder methods for XCP-ng network management
- Support basic network configuration via XAPI
- Maintain existing networking functionality
- Document XCP-ng networking integration points

### 4. Update `pylua_bioxen_vm_lib/env.py` and `pylua_bioxen_vm_lib/utils/curator.py`
**Task**: Support SSH-based package management for XCP-ng VMs

**Requirements**:
- Extend package installation to work over SSH connections
- Add VM type detection in package management functions
- Use SSH for XCP-ng VMs, local execution for BasicLuaVM
- Maintain existing package management API

### 5. Update `requirements.txt`
**Task**: Add new dependencies

**Add**:
```
requests>=2.31.0
paramiko>=3.0.0
urllib3>=1.26.0
```

## Implementation Guidelines

### XAPI Communication Pattern
```python
# Example XAPI call structure
response = requests.post(
    f"https://{host}/api/vm/create",
    headers={"Authorization": f"Bearer {session_token}"},
    json={"template": template_name, "name": vm_name, "config": config},
    verify=verify_ssl
)
```

### SSH Execution Pattern
```python
# Example SSH execution
ssh = paramiko.SSHClient()
ssh.connect(vm_ip, username="root", key_filename=ssh_key)
stdin, stdout, stderr = ssh.exec_command(f"lua -e '{lua_code}'")
result = {"stdout": stdout.read().decode(), "stderr": stderr.read().decode()}
```

### Error Handling Requirements
- Map XAPI HTTP errors (4xx, 5xx) to existing VM exceptions
- Map SSH errors to LuaVMError or appropriate existing exceptions
- Provide helpful error messages for common XCP-ng issues
- Handle timeouts gracefully (VM boot, SSH connection)

### LLM-Generated Middleware Approach
For the XAPI client code, focus on:
- Simple, direct HTTP calls using requests library
- JSON request/response handling
- Basic authentication and session management
- Minimal error handling and retry logic

## Testing Strategy for Phase 2
- Mock XAPI responses for unit testing
- Test SSH communication with mock SSH servers
- Verify error handling and exception mapping
- Test VM lifecycle: create → start → execute → stop → destroy

## Success Criteria for Phase 2
- [ ] XCPngVM can be created with proper configuration
- [ ] XAPI client can authenticate and make basic API calls
- [ ] VM creation from template works (can be tested with XCP-ng instance)
- [ ] SSH connection to created VM succeeds
- [ ] Simple Lua code execution works via SSH
- [ ] Basic error handling and cleanup works
- [ ] All existing BasicLuaVM functionality remains unchanged

## Implementation Notes
- Start with the simplest XAPI calls first (authentication, then VM creation)
- Use XCP-ng's REST API documentation for endpoint details
- Test SSH connectivity before implementing complex Lua execution
- Keep configuration simple - focus on proving the integration works
- Use existing logging infrastructure from VMLogger
- Follow existing code patterns and style from the codebase

## Phase 2 Validation Test
Create this simple validation script:
```python
from pylua_bioxen_vm_lib import VMManager

# Test XCP-ng VM creation and execution
with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("test_xcpng", vm_type="xcpng", config={
        "xcpng_host": "your-xcpng-host",
        "xcpng_username": "root",
        "xcpng_password": "password", 
        "template": "lua-template"
    })
    
    result = manager.execute_vm_sync("test_xcpng", 'return 2 + 2')
    print(f"XCP-ng VM result: {result['stdout']}")  # Should output: 4
```

## Next Steps After Phase 2
Phase 3 will add usage examples and documentation updates to complete the MVP.