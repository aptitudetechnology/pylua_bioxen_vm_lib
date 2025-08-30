# Extended pylua_bioxen_vm_lib Specification: Xen-Server Integration

## Objective
Extend pylua_bioxen_vm_lib (v0.1.18) to support Xen-Server and Domain 0 (Dom0) integration using LLM-based intelligent glue layers, while maintaining full backward compatibility with existing VM types (basic, jit, container).

Don't build too much. We want a miniumum viable prototype for now.

## Core Architecture Extensions

### 1. Multi-VM Class Foundation
Implement the planned multi-VM architecture with these VM types:
- **BasicLuaVM**: Current implementation (backward compatible)
- **XenDom0VM**: NEW - Xen hypervisor integration via Dom0

### 2. Xen Integration Strategy
**Philosophy**: Leverage existing Dom0 capabilities without modifying Xen code. Use LLMs as intelligent middleware to bridge BioXen requirements with native Dom0/xl tooling.

**Integration Approach**:
- Use Dom0 as the control plane for all Xen operations
- Extend Dom0 capabilities through BioXen-specific tooling (via BioXen-luavm setup)
- Interface with enhanced Dom0 through intelligent API translation
- Maintain seamless user experience with zero manual VM configuration

### 3. LLM modals will code the Glue Layer Architecture
Plan middleware that can do:
- **Command Translation**: Converts pylua_bioxen_vm_lib API calls to appropriate Dom0/xl commands
- **Configuration Generation**: Creates Xen VM XML configs from BioXen VM specifications
- **Error Interpretation**: Parses Dom0/Xen error messages and provides meaningful Python exceptions
- **Workflow Orchestration**: Chains Dom0 operations for complex BioXen biological computing workflows
- **Dynamic Adaptation**: Learns from operation success/failure patterns

## Implementation Requirements

### Core Library Updates

#### vm_manager.py
- Extend VMManager to support XenDom0VM type
- Add Xen-specific configuration handling
- Integrate LLM glue layer for Dom0 communication
- Support hybrid template/dynamic VM deployment
- Maintain backward compatibility with existing create_vm() interface

#### lua_process.py  
- Abstract VM communication to support multiple backends
- Add Xen domain communication via console/SSH/agent methods
- Implement three-tier communication fallback strategy
- Support both process-based and domain-based Lua execution

#### New: xen_integration.py
- XenDom0VM class implementation
- LLM glue layer service interface
- Dom0 command translation utilities
- Xen configuration generation
- Template and deployment management

#### networking.py
- Extend networking to support Xen bridge configurations
- Interface with Dom0 network management
- Support biological workflow networking requirements

#### env.py & curator.py
- Support package installation across VM types
- Handle Xen domain-based package management
- Multi-modal installation (console/SSH/agent) for Xen VMs
- Environment isolation for Xen domains

### Factory Pattern Implementation

```python
class LuaVMFactory:
    @staticmethod
    def create_vm(vm_type, vm_id, config=None):
        vm_classes = {
            "basic": BasicLuaVM,
            "jit": LuaJITVM, 
            "container": ContainerizedLuaVM,
            "xen": XenDom0VM  # NEW
        }
        if vm_type not in vm_classes:
            raise ValueError(f"Unknown VM type: {vm_type}")
        return vm_classes[vm_type](vm_id, config)
```

### XenDom0VM Class Requirements

#### Core Interface (inherits from BaseLuaVM)
- `start()`: Create and start Xen domain using Dom0 tools
- `stop()`: Gracefully shutdown Xen domain
- `execute(lua_code)`: Execute Lua code in domain via console/SSH/agent
- `install_package(package)`: Install Lua packages using curator

#### Xen-Specific Features
- Template-based rapid deployment
- Dynamic VM creation with Lua pre-installation
- Resource management (memory, CPU, storage)
- Network configuration via Dom0 bridges
- Multi-modal communication (console/SSH/agent fallback)

#### Middleware Integration Points
- Configuration translation (BioXen specs → Xen XML)
- Command generation (API calls → xl/libvirt commands)
- Error translation (Xen errors → Python exceptions)
- Workflow orchestration (complex multi-step operations)

## Dependencies and Integration

### System Dependencies (handled by BioXen-luavm)
```bash
# Xen packages
sudo apt-get install xen-hypervisor xen-utils xen-tools
# Development tools  
sudo apt-get install build-essential libvirt-dev libxen-dev
# Python development
sudo apt-get install python-dev python3-dev
```

### Python Dependencies
```python
# Add to requirements.txt
libvirt-python>=9.0.0
python-xenapi>=22.0.0
libxml2-python>=2.9.0
```

### BioXen-luavm Integration
- BioXen-luavm handles interactive setup and Dom0 configuration
- Generates configuration files for pylua_bioxen_vm_lib consumption
- Creates VM templates and networking setup
- Provides troubleshooting and validation tools

## Usage Patterns

### Pattern 5: Xen VM Execution
```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Create Xen VM with template
    vm = manager.create_vm("xen_vm", vm_type="xen", 
                          config={"template": "lua-bio-template"})
    
    # Execute biological computation
    result = manager.execute_vm_sync("xen_vm", '''
        require("bio_compute")
        sequence = "ATCGTAGCTACG"
        analysis = bio_compute.analyze_dna(sequence)
        print("Analysis:", analysis)
    ''')
    
    print(result['stdout'])
```

### Pattern 6: Multi-Modal Package Installation
```python
# Curator automatically selects best communication method
installer = PackageInstaller()
installer.install_package_in_vm("bio_sequence_analysis", 
                                vm_id="xen_vm", 
                                vm_type="xen",
                                fallback_methods=["agent", "ssh", "console"])
```

## Testing Requirements

### Xen-Specific Tests
- `tests/test_xen_vm.py`: XenDom0VM class functionality
- `tests/test_xen_integration.py`: Dom0 communication and LLM glue layer
- `tests/test_xen_networking.py`: Xen bridge networking
- `tests/test_xen_templates.py`: Template creation and deployment

### Integration Tests
- Cross-VM type compatibility testing
- Package management across all VM types
- Performance benchmarking (basic vs jit vs container vs xen)
- Resource isolation validation

## Documentation Updates

### New Documentation Sections
- **Xen Setup Guide**: Integration with BioXen-luavm setup process
- **VM Type Selection Guide**: When to use each VM type
- **Xen Configuration Reference**: Dom0 integration parameters
- **LLM Glue Layer Documentation**: How intelligent translation works
- **Troubleshooting Xen Integration**: Common issues and solutions

## Implementation Strategy

### Phase 1: Foundation
1. Implement BaseLuaVM abstract class
2. Refactor existing code into BasicLuaVM
3. Create VM factory pattern
4. Update VMManager to use factory

### Phase 2: Xen Integration
1. Implement XenDom0VM class in code created by LLMs (like a glue)
2. Add libvirt-python integration
3. Implement multi-modal communication (console/SSH/agent)
4. Update curator for Xen package management

### Phase 3: Advanced Features
1. Template management system
2. Advanced networking features
3. Performance optimization
4. Enhanced monitoring and logging

### Phase 4: Production Readiness
1. Comprehensive testing across all VM types
2. Documentation completion
3. Performance benchmarking
4. Security validation

## Success Criteria
- Zero disruption to existing BasicLuaVM users
- Seamless Xen VM creation and management
- Successful package installation across all VM types
- Middleware code successfully translates between Python API and Dom0 operations
- Integration with BioXen-luavm setup process
- Biological computing workflows run efficiently on Xen VMs

## Notes
- Maintain the library's focus on biological computation and genomic data virtualization
- Ensure all VM types support the same package ecosystem where possible
- Keep the Python API clean and consistent across VM types
- Leverage Dom0's existing capabilities rather than reimplementing Xen functionality
- Use experimental approaches until proven patterns emerge