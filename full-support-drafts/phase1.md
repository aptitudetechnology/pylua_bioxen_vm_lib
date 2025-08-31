# Phase 1 MVP Implementation Plan: Basic Multi-VM Support (Minimum Viable Prototype)

## Overview
Phase 1 MVP establishes the absolute minimum multi-VM architecture by adding `vm_type` parameter support and a basic placeholder XCPngVM. Focus on proving the concept works with minimal code changes.

## Phase 1 MVP Objectives
- Add `vm_type` parameter to `create_vm()` function
- Create minimal placeholder `XCPngVM` class
- Maintain 100% backward compatibility
- Enable testing of multi-VM concept

## Phase 1 MVP Implementation Steps

### Step 1.1: Update create_vm() Function (1 day)

```python
# Update: pylua_bioxen_vm_lib/__init__.py or vm_manager.py
def create_vm(vm_id="default", vm_type="basic", networked=False, persistent=False, 
              debug_mode=False, lua_executable="lua", config=None):
    """Create VM using factory pattern (MVP - minimal changes)"""
    
    if vm_type == "basic":
        # Existing logic - no changes
        from .lua_process import LuaProcess
        return LuaProcess(
            vm_id=vm_id,
            networked=networked,
            persistent=persistent,
            debug_mode=debug_mode,
            lua_executable=lua_executable
        )
    
    elif vm_type == "xcpng":
        # MVP: Import and create placeholder
        from .xcp_ng_integration import XCPngVM
        return XCPngVM(vm_id, config)
    
    else:
        raise ValueError(f"Unknown VM type: {vm_type}. Supported: basic, xcpng")
```

### Step 1.2: Create Minimal XCP-ng Placeholder (1 day)

```python
# New file: pylua_bioxen_vm_lib/xcp_ng_integration.py
"""XCP-ng VM integration placeholder (Phase 1 MVP)"""

class XCPngVM:
    """Minimal XCP-ng VM placeholder for Phase 1 MVP"""
    
    def __init__(self, vm_id, config=None):
        self.vm_id = vm_id
        self.config = config or {}
        self.status = "placeholder"
        print(f"XCP-ng VM {vm_id} created (MVP placeholder)")
    
    def start(self):
        """Start VM (placeholder)"""
        print(f"Starting XCP-ng VM {self.vm_id} (placeholder)")
        self.status = "running"
        return {"status": "placeholder", "message": "MVP placeholder - Phase 2 will implement"}
    
    def stop(self):
        """Stop VM (placeholder)"""
        print(f"Stopping XCP-ng VM {self.vm_id} (placeholder)")
        self.status = "stopped"
        return {"status": "placeholder", "message": "MVP placeholder - Phase 2 will implement"}
    
    def execute_string(self, lua_code):
        """Execute Lua code (placeholder)"""
        print(f"Executing in XCP-ng VM {self.vm_id}: {lua_code[:30]}... (placeholder)")
        return {
            "stdout": f"MVP placeholder result: {lua_code[:20]}...",
            "stderr": "",
            "exit_code": 0,
            "success": True
        }
    
    def install_package(self, package_name):
        """Install package (placeholder)"""
        print(f"Installing {package_name} in XCP-ng VM {self.vm_id} (placeholder)")
        return {"status": "placeholder", "package": package_name}
    
    def get_status(self):
        """Get status (placeholder)"""
        return {"vm_id": self.vm_id, "status": self.status, "type": "xcpng_placeholder"}
```

### Step 1.3: Add Dependencies (30 minutes)

```txt
# Add to requirements.txt
requests>=2.31.0
paramiko>=3.0.0
```

### Step 1.4: Create MVP Test (1 day)

```python
# Update: tests/test_vm_manager.py (or create new test file)
import unittest
from pylua_bioxen_vm_lib import create_vm

class TestMVPMultiVM(unittest.TestCase):
    
    def test_basic_vm_still_works(self):
        """Test backward compatibility"""
        vm = create_vm("test", vm_type="basic")
        self.assertIsNotNone(vm)
    
    def test_xcpng_vm_placeholder(self):
        """Test XCP-ng placeholder creation"""
        config = {"xcpng_host": "test", "username": "test", "password": "test", "template": "test"}
        vm = create_vm("test", vm_type="xcpng", config=config)
        self.assertIsNotNone(vm)
        self.assertEqual(vm.vm_id, "test")
    
    def test_invalid_vm_type_error(self):
        """Test error for invalid type"""
        with self.assertRaises(ValueError):
            create_vm("test", vm_type="invalid")

if __name__ == "__main__":
    unittest.main()
```

### Step 1.5: Create MVP Demo (1 day)

```python
# New file: examples/mvp_demo.py
"""Phase 1 MVP Demo - Multi-VM Support"""

from pylua_bioxen_vm_lib import create_vm

def mvp_demo():
    print("=== Phase 1 MVP Demo ===\n")
    
    # 1. Test basic VM (existing functionality)
    print("1. Basic VM (existing functionality):")
    basic_vm = create_vm("basic_test", vm_type="basic")
    result = basic_vm.execute_string('print("Hello Basic VM")')
    print(f"   Result: {result.get('stdout', 'No output')}\n")
    
    # 2. Test XCP-ng placeholder
    print("2. XCP-ng VM (placeholder):")
    config = {
        "xcpng_host": "192.168.1.100",
        "username": "root",
        "password": "password",
        "template": "Ubuntu-BioXen"
    }
    
    xcpng_vm = create_vm("xcpng_test", vm_type="xcpng", config=config)
    xcpng_vm.start()
    result = xcpng_vm.execute_string('print("Hello XCP-ng")')
    print(f"   Result: {result.get('stdout')}")
    status = xcpng_vm.get_status()
    print(f"   Status: {status}")
    xcpng_vm.stop()
    
    print("\n=== MVP Success: Multi-VM architecture working ===")

if __name__ == "__main__":
    mvp_demo()
```

### Step 1.6: Update Documentation (30 minutes)

```markdown
# Update: README.md or docs/api.md

## Multi-VM Support (Phase 1 MVP)

### New vm_type Parameter

```python
from pylua_bioxen_vm_lib import create_vm

# Basic VM (existing functionality)
basic_vm = create_vm("test", vm_type="basic")

# XCP-ng VM (placeholder)
config = {"xcpng_host": "host", "username": "user", "password": "pass", "template": "template"}
xcpng_vm = create_vm("test", vm_type="xcpng", config=config)
```

**Phase 1 Status:**
- `vm_type="basic"`: Fully functional (no changes)
- `vm_type="xcpng"`: Placeholder implementation

**Phase 2:** Will implement full XAPI integration for XCP-ng VMs.
```

## Phase 1 MVP Success Criteria

### Functional Requirements
- [x] `create_vm()` accepts `vm_type` parameter
- [x] `vm_type="basic"` works exactly as before (backward compatibility)
- [x] `vm_type="xcpng"` creates placeholder VM without errors
- [x] Error handling for invalid `vm_type`

### Testing Requirements
- [x] Basic VM creation still works
- [x] XCP-ng placeholder VM creation works
- [x] Invalid VM type raises appropriate error

## Phase 1 MVP Deliverables

1. **Updated create_vm() function** with `vm_type` parameter
2. **Minimal XCPngVM placeholder class**
3. **Basic test coverage** for multi-VM functionality
4. **Simple demo script** showing both VM types
5. **Updated dependencies** for Phase 2 preparation

## Phase 1 MVP Timeline: 3-4 days total

### Day 1: Core Implementation
- Update `create_vm()` function
- Create `XCPngVM` placeholder class

### Day 2: Testing & Demo
- Write MVP tests
- Create demo script

### Day 3: Documentation & Cleanup
- Update documentation
- Verify backward compatibility
- Add dependencies

### Day 4: Validation
- Test full MVP functionality
- Prepare for Phase 2

## Files Modified/Created (MVP Only)

### Core Changes
- **pylua_bioxen_vm_lib/__init__.py** or **vm_manager.py** - Add `vm_type` to `create_vm()`
- **pylua_bioxen_vm_lib/xcp_ng_integration.py** - New minimal placeholder class

### Testing & Examples
- **tests/test_mvp_multivm.py** - MVP functionality tests
- **examples/mvp_demo.py** - Simple demo script

### Dependencies
- **requirements.txt** - Add requests, paramiko for Phase 2

### Documentation
- **README.md** or **docs/api.md** - Document `vm_type` parameter

This MVP proves the multi-VM concept works and provides the foundation for Phase 2 implementation with minimal risk and maximum backward compatibility.