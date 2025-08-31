# GitHub Copilot Instructions - Phase 3: Simple Usage Pattern

## Context Files to Read
Please analyze these specification files in the project root:
- `spec-report.md` - Current pylua_bioxen_vm_lib specification (v0.1.18)
- `xcp-ng-support.md` - Extended specification for XCP-ng integration MVP
- `xcp-ng-support-report.md` - Audit report with implementation requirements

## Phase 3 Objectives
Complete the MVP by adding usage examples and documentation updates. This phase makes the XCP-ng integration discoverable and usable by:
1. Adding XCP-ng usage examples to existing example scripts
2. Updating documentation to reflect new VM type support
3. Adding installation and setup instructions for XCP-ng dependencies
4. Creating simple validation examples

## Prerequisites
Phase 1 and 2 must be complete with:
- Working factory pattern with BasicLuaVM and XCPngVM
- XCPngVM class implemented with XAPI client
- SSH-based Lua execution working in XCP-ng VMs

## Files to Update

### 1. `examples/basic_usage.py`
**Task**: Add XCP-ng VM usage alongside existing BasicLuaVM examples

**Requirements**:
- Keep all existing BasicLuaVM examples intact
- Add new section demonstrating XCP-ng VM creation and execution
- Show simple Lua code execution via XCP-ng
- Include error handling example
- Demonstrate configuration options

**Expected Addition**:
```python
# XCP-ng VM Usage Example
print("\n=== XCP-ng VM Example ===")
try:
    # Create XCP-ng VM
    xcpng_vm = create_vm("xcpng_example", vm_type="xcpng", config={
        "xcpng_host": "192.168.1.100",
        "xcpng_username": "root",
        "xcpng_password": "password",
        "template": "lua-bio-template",
        "memory": "2GB",
        "vcpus": 2
    })
    
    # Execute Lua code
    result = xcpng_vm.execute_string('print("Hello from XCP-ng VM!"); return 2 + 2')
    print(f"XCP-ng Result: {result['stdout']}")
    
except Exception as e:
    print(f"XCP-ng VM example failed (expected if no XCP-ng host): {e}")
```

### 2. `examples/integration_demo.py`
**Task**: Add XCP-ng integration to existing VMManager demo

**Requirements**:
- Keep existing VMManager examples
- Add XCP-ng VM creation via VMManager
- Show both BasicLuaVM and XCPngVM in same workflow
- Demonstrate package installation in XCP-ng VM

**Expected Pattern**:
```python
with VMManager(debug_mode=True) as manager:
    # Existing basic VM example...
    
    # NEW: XCP-ng VM example
    try:
        xcpng_vm = manager.create_vm("xcpng_demo", vm_type="xcpng", config={
            "xcpng_host": "your-xcpng-host",
            "template": "lua-bio-template"
        })
        
        result = manager.execute_vm_sync("xcpng_demo", '''
            require("bio_compute")
            result = bio_compute.analyze_sequence("ATCG")
            print("XCP-ng Analysis:", result)
        ''')
        
        print(result['stdout'])
    except Exception as e:
        print(f"XCP-ng demo skipped: {e}")
```

### 3. `examples/fixed-integration-demo.py`
**Task**: Update to include XCP-ng VM type in the demo

**Requirements**:
- Add XCP-ng VM alongside existing examples
- Show cross-VM type compatibility
- Include basic error handling for missing XCP-ng infrastructure

### 4. `docs/api.md`
**Task**: Document new VM type support and XCP-ng API

**Sections to Add/Update**:

#### VM Creation Updates
```markdown
### create_vm() - Updated
```python
create_vm(vm_id="default", vm_type="basic", networked=False, persistent=False, debug_mode=False, lua_executable="lua", config=None)
```

**New Parameters:**
- `vm_type` - VM type: "basic" (default) or "xcpng"
- `config` - Dictionary of VM-specific configuration

**VM Types:**
- `"basic"` - Local process-based Lua VM (existing functionality)
- `"xcpng"` - XCP-ng virtualized Lua VM via XAPI

#### XCP-ng Configuration
```markdown
### XCP-ng VM Configuration
For `vm_type="xcpng"`, provide config dictionary:

```python
config = {
    "xcpng_host": "192.168.1.100",        # XCP-ng host IP/hostname
    "xcpng_username": "root",             # XCP-ng admin username  
    "xcpng_password": "password",         # XCP-ng admin password
    "template": "lua-bio-template",       # VM template name
    "memory": "2GB",                      # VM memory allocation
    "vcpus": 2,                          # Virtual CPU count
    "verify_ssl": False                   # SSL verification for XAPI
}
```
```

#### XCPngVM Class Documentation
- Document all public methods
- Explain XAPI integration approach
- Document SSH execution mechanism
- List configuration requirements

### 5. `docs/examples.md`
**Task**: Add XCP-ng usage examples and patterns

**New Sections to Add**:

#### Pattern 5: XCP-ng VM Execution
- Complete example of XCP-ng VM creation and usage
- Show biological computation workflow
- Include configuration and error handling

#### XCP-ng Setup Requirements
- XCP-ng host setup prerequisites
- VM template requirements for Lua execution
- SSH access configuration
- Network configuration basics

### 6. `docs/installation.md`
**Task**: Add XCP-ng dependency and setup instructions

**Sections to Add**:

#### XCP-ng Integration Dependencies
```markdown
### XCP-ng Integration (Optional)
For XCP-ng VM support, install additional dependencies:

```bash
pip install requests>=2.31.0 paramiko>=3.0.0
```

### XCP-ng Host Requirements
- XCP-ng 8.2+ with XAPI enabled
- VM template with Lua runtime installed
- SSH access configured for root user
- Network connectivity between Python host and XCP-ng
```

#### XCP-ng Template Setup
- Document requirements for Lua VM templates
- SSH key configuration
- Basic template creation guidance

### 7. `requirements.txt`
**Task**: Update with XCP-ng dependencies (if not done in Phase 2)

**Add**:
```
requests>=2.31.0
paramiko>=3.0.0
urllib3>=1.26.0
```

## Testing Updates

### Create Basic XCP-ng Tests
Add minimal tests in existing test files:

#### `tests/test_vm_manager.py`
- Test XCPngVM creation via factory pattern
- Test configuration validation
- Mock XAPI responses for unit testing

#### `tests/test_xcp_ng_integration.py` (NEW FILE)
```python
import unittest
from unittest.mock import Mock, patch
from pylua_bioxen_vm_lib.xcp_ng_integration import XAPIClient, XCPngVM

class TestXCPngIntegration(unittest.TestCase):
    def test_xapi_client_auth(self):
        # Mock XAPI authentication
    
    def test_vm_creation(self):
        # Mock VM creation from template
    
    def test_ssh_execution(self):
        # Mock SSH Lua execution
```

## Implementation Guidelines

### XAPI Integration Best Practices
- Use session-based authentication for XAPI calls
- Handle HTTP timeouts gracefully (VM creation can be slow)
- Validate XCP-ng connectivity before VM operations
- Use appropriate HTTP status code handling

### SSH Communication Best Practices  
- Implement connection pooling for SSH clients
- Handle SSH timeouts and connection failures
- Use key-based authentication when possible
- Clean up SSH connections properly

### Error Handling Strategy
```python
# Map XAPI errors to existing exceptions
if response.status_code == 401:
    raise VMManagerError("XCP-ng authentication failed")
elif response.status_code == 404:
    raise SessionNotFoundError(f"XCP-ng template '{template}' not found")
elif response.status_code >= 500:
    raise LuaVMError(f"XCP-ng server error: {response.text}")
```

### Configuration Validation
- Validate required XCP-ng config parameters
- Provide helpful error messages for missing configuration
- Support reasonable defaults where possible

## Documentation Style Guidelines
- Keep examples simple and focused
- Include error handling in all examples
- Provide complete, runnable code samples
- Explain XCP-ng prerequisites clearly
- Maintain consistency with existing documentation style

## Success Criteria for Phase 3
- [ ] Examples demonstrate XCP-ng VM creation and Lua execution
- [ ] Documentation covers all new VM type features
- [ ] Installation instructions include XCP-ng dependencies
- [ ] Error handling examples show common failure modes
- [ ] All examples are runnable (with proper XCP-ng setup)
- [ ] Documentation maintains consistency with existing style
- [ ] Basic tests validate core XCP-ng functionality

## MVP Validation Test
Create this comprehensive validation example:

```python
# MVP Validation: Complete XCP-ng Workflow
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller

# Test complete workflow
with VMManager(debug_mode=True) as manager:
    # Create XCP-ng VM
    vm = manager.create_vm("mvp_test", vm_type="xcpng", config={
        "xcpng_host": "test-host",
        "template": "lua-bio-template"
    })
    
    # Execute biological computation
    result = manager.execute_vm_sync("mvp_test", '''
        -- Simple biological sequence analysis
        sequence = "ATCGTAGCTACG"
        gc_content = 0
        for i = 1, #sequence do
            local base = sequence:sub(i,i)
            if base == "G" or base == "C" then
                gc_content = gc_content + 1
            end
        end
        print("GC Content:", gc_content / #sequence * 100, "%")
    ''')
    
    print("MVP Success:", result['stdout'])
```

## Phase 3 Completion Criteria
After Phase 3, users should be able to:
1. Read the documentation and understand how to use XCP-ng VMs
2. Install dependencies and configure XCP-ng integration
3. Run the provided examples successfully (with XCP-ng infrastructure)
4. Execute biological computations in XCP-ng VMs
5. Troubleshoot common configuration and connectivity issues

This completes the MVP for XCP-ng integration in pylua_bioxen_vm_lib.
