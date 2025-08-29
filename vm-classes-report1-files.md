# Report: Files Requiring Updates for Multi-VM Class Architecture

To implement the multi-VM class architecture in `pylua_bioxen_vm_lib`, the following files should be updated or extended:

<!-- ADDED SECTION: FILES REQUIRING UPDATES -->
## Core Library
- `pylua_bioxen_vm_lib/vm_manager.py`: Add/modify VM management logic to support multiple VM classes and the factory pattern.
- `pylua_bioxen_vm_lib/lua_process.py`: Refactor to use the new VM abstraction where appropriate.
- `pylua_bioxen_vm_lib/cli.py` and/or `cli.py2`: Update CLI to allow users to select and manage different VM types.
- `pylua_bioxen_vm_lib/networking.py`: Integrate networking features for advanced VM types.
- `pylua_bioxen_vm_lib/env.py`: Update environment setup for per-VM configuration.
- `pylua_bioxen_vm_lib/utils/curator.py` (and/or `curator.py2`): Refactor package management to support per-VM environments.

## Tests
- `tests/test_vm_manager.py`: Add tests for VM creation, lifecycle, and type selection.
- `tests/test_lua_process.py`: Test Lua execution for each VM type.
- `tests/test_env.py`: Test environment setup for different VM classes.
- `tests/test_networking.py`: Test networking features for VMs.
- `tests/test_curator.py`: Test package management for per-VM environments.

## Examples
- `examples/basic_usage.py`: Show usage of multiple VM types.
- `examples/distributed_compute.py`: Demonstrate advanced VM and networking features.
- `examples/integration_demo.py`, `fixed-integration-demo.py`, `p2p_messaging.py`: Update to use new VM classes as needed.

## Documentation
- `docs/api.md`: Document the new VM class architecture and API.
- `docs/examples.md`: Add examples for each VM type.
- `docs/installation.md`: Update installation and setup instructions for new VM types.
<!-- END ADDED SECTION -->
