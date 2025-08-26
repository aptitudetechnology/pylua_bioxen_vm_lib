# GitHub Copilot Instructions: Codebase Audit Against Specification

## Task Overview
Audit the pylua_bioxen_vm_lib codebase against the provided specification document to identify discrepancies, missing implementations, and architectural inconsistencies.

## Critical Areas to Investigate

### 1. Import Dependencies Validation
**Instruction**: Check if these imports exist in the actual codebase:
```python
# Verify these modules exist:
from pylua_bioxen_vm_lib.vm_manager import VMCluster
from pylua_bioxen_vm_lib.networking import NetworkedLuaVM, validate_host, validate_port
from pkgdict.bioxen_packages import ALL_PACKAGES, BIOXEN_PACKAGES
from pkgdict.bioxen_profiles import ALL_PROFILES, BIOXEN_PROFILES, PROFILE_CATEGORIES
```

**Action**: 
- Search the entire codebase for these module files
- If missing, identify what the correct import paths should be
- Check if equivalent functionality exists under different names

### 2. Exception Classes Verification
**Instruction**: Verify all exception classes referenced in the CLI script exist in `pylua_bioxen_vm_lib/exceptions.py`:

```python
# Check if these exceptions are actually defined:
ProcessRegistryError
LuaProcessError
NetworkingError
```

**Action**:
- List all actual exception classes in the exceptions module
- Flag any referenced exceptions that don't exist
- Identify missing exception handling that should exist

### 3. VMManager API Surface Area
**Instruction**: Compare the CLI script's assumed VMManager methods against the actual implementation:

**CLI Script Assumptions**:
```python
# Methods the CLI expects to exist:
manager.create_interactive_session()  # No vm_id parameter
manager.attach_interactive_session(vm_id)
manager.detach_interactive_session(vm_id)
```

**Specification Claims**:
```python
# What the spec says exists:
manager.create_interactive_vm(vm_id)  # Requires vm_id
manager.attach_to_vm(vm_id)
manager.detach_from_vm(vm_id)
```

**Action**:
- Examine the actual VMManager class implementation
- Document the real method signatures and parameters
- Identify which version (CLI assumptions vs spec) is correct

### 4. Curator System Implementation
**Instruction**: Verify the curator system integration matches CLI usage:

```python
# CLI script assumes these exist:
from pylua_bioxen_vm_lib.utils.curator import (
    Curator, get_curator, bootstrap_lua_environment, Package
)
curator.curate_environment(profile_name)
curator.get_recommendations()
curator.list_installed_packages()
```

**Action**:
- Check if `pylua_bioxen_vm_lib/utils/curator.py` exists
- Verify the Curator class has these methods with correct signatures
- Document any missing methods or different parameter requirements

### 5. Interactive Session Behavior
**Instruction**: Examine the InteractiveSession class implementation:

**CLI Assumptions**:
```python
# CLI expects these patterns:
session = manager.create_interactive_vm(vm_id)
session.load_package(package_name)  # Direct method call
session.interactive_loop()  # Blocking REPL
```

**Specification Claims**:
```python
# Spec suggests these patterns:
manager.send_input(vm_id, input_string)
manager.read_output(vm_id)
# load_package may use send_input internally
```

**Action**:
- Document the actual InteractiveSession class interface
- Determine if load_package() is a real method or implemented via send_input()
- Verify how interactive_loop() actually behaves

### 6. Package Management Architecture
**Instruction**: Investigate the actual package management system:

**Questions to Answer**:
- Does `pkgdict` module exist as a separate package or is it part of the main library?
- Is there a `EnvironmentManager` class in `pylua_bioxen_vm_lib.env`?
- What's the real structure of package profiles and catalogs?

**Action**:
- Map the complete package management architecture
- Identify where BIOXEN_PACKAGES and BIOXEN_PROFILES are actually defined
- Document the real workflow for environment setup

### 7. Session Management Integration
**Instruction**: Verify session lifecycle management:

```python
# CLI expects:
sessions = manager.session_manager.list_sessions()
session_manager = manager.session_manager
session_manager.terminate_session(vm_id)
```

**Action**:
- Confirm SessionManager is accessible via VMManager.session_manager
- Verify the list_sessions() return format
- Check terminate_session() vs terminate_vm_session() naming

## Output Format

For each investigation area, provide:

```markdown
### [Area Name] - Status: [MATCHES/CONFLICTS/MISSING]

**Actual Implementation:**
```python
# Real code found in codebase
```

**CLI Script Expects:**
```python  
# What the CLI script assumes
```

**Specification Claims:**
```python
# What the spec document states
```

**Resolution Required:**
- [ ] Update CLI script to match actual API
- [ ] Fix specification document  
- [ ] Implement missing functionality
- [ ] Other: [describe]
```

## Priority Levels

**P0 - Critical**: Import failures, missing core classes
**P1 - High**: Method signature mismatches, incorrect exception handling  
**P2 - Medium**: Feature assumptions, behavior differences
**P3 - Low**: Documentation inconsistencies, naming conventions

## Expected Deliverable

A comprehensive audit report identifying:
1. All discrepancies between specification and implementation
2. CLI script assumptions that don't match reality  
3. Missing functionality that needs implementation
4. Recommended fixes with priority levels
5. Updated API documentation based on actual codebase