pylua_bioxen_vm_lib Specification
Overview
The pylua_bioxen_vm_lib (version 0.1.18) is a Python library for managing Lua virtual machines (VMs) within the BioXen framework, designed for biological computation and genomic data virtualization. It supports synchronous and asynchronous Lua code execution, interactive session management, and library-agnostic package management for isolated Lua environments. This library is ideal for applications requiring lightweight, sandboxed Lua VMs integrated with biological workflows.
This specification, updated as of August 26, 2025, aligns with the development branch codebase, addresses compliance findings, and provides accurate guidance for developers.
Key Components
1. VM Creation
Module: pylua_bioxen_vm_lib
Key Function: create_vm(vm_id: str = "default", networked: bool = False, persistent: bool = False, debug_mode: bool = False, lua_executable: str = "lua") -> LuaProcess
Creates a Lua VM instance as an isolated subprocess.
Parameters:

vm_id: Unique identifier for the VM (default: "default").
networked: Enables experimental networking capabilities if True.
persistent: If True, the VM persists across sessions for interactive use.
debug_mode: If True, enables verbose logging for debugging.
lua_executable: Path to the Lua executable (default: "lua").

Returns: A LuaProcess object for executing Lua code.
Example Usage:
from pylua_bioxen_vm_lib import create_vm
vm = create_vm("test_vm", debug_mode=True)
result = vm.execute_string('print("Hello, BioXen!")')
print(result['stdout'])  # Output: Hello, BioXen!

2. VM Manager
Class: VMManager
Manages multiple Lua VMs and their sessions, providing lifecycle control and execution capabilities.
Key Methods:

create_vm(vm_id: str, networked: bool = False, persistent: bool = False) -> LuaProcess: Creates a managed VM.
execute_vm_sync(vm_id: str, code: str) -> dict: Executes Lua code synchronously, returning a dictionary with stdout and other metadata.
execute_vm_async(vm_id: str, code: str) -> Future: Executes Lua code asynchronously, returning a Future object.
create_interactive_vm(vm_id: str) -> InteractiveSession: Creates a persistent interactive session.
attach_to_vm(vm_id: str) -> InteractiveSession: Attaches to an existing interactive session.
detach_from_vm(vm_id: str): Detaches from an interactive session.
terminate_vm_session(vm_id: str): Terminates a session and its associated VM.
send_input(vm_id: str, input: str): Sends Lua code to an interactive session.
read_output(vm_id: str) -> str: Reads output from an interactive session.
list_sessions() -> List[dict]: Lists active sessions with their details.

Example Usage:
from pylua_bioxen_vm_lib import VMManager
with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("managed_vm")
    result = manager.execute_vm_sync("managed_vm", 'print("Result:", 2 + 2)')
    print(result['stdout'])  # Output: Result: 4

3. Interactive Session
Class: InteractiveSession
Manages real-time interaction with Lua VMs for dynamic scripting. Package loading and REPL functionality are implemented via send_input and read_output.
Key Methods:

send_input(input: str): Sends Lua code to the session.
read_output() -> str: Retrieves output from the session.
set_environment(env_name: str): Sets the Lua environment for the session.

Note: Package loading and interactive REPL loops are handled by sending appropriate Lua code via send_input and retrieving results via read_output. There are no direct load_package or interactive_loop methods.
Example Usage:
from pylua_bioxen_vm_lib import VMManager
manager = VMManager(debug_mode=True)
session = manager.create_interactive_vm("interactive_vm")
manager.send_input("interactive_vm", "x = 42\nprint('Value:', x)\n")
import time
time.sleep(0.5)  # Allow processing
print(manager.read_output("interactive_vm"))  # Output: Value: 42

4. Session Manager
Class: SessionManager
Manages the lifecycle of interactive sessions, accessible via VMManager.session_manager.
Key Methods:

list_sessions() -> dict: Returns a dictionary of active session IDs and their details.
terminate_session(vm_id: str): Terminates a specific session.

Example Usage:
from pylua_bioxen_vm_lib import VMManager
manager = VMManager(debug_mode=True)
session_manager = manager.session_manager
session = manager.create_interactive_vm("test_session")
sessions = session_manager.list_sessions()
print(sessions)  # Output: {'test_session': <session_details>}
session_manager.terminate_session("test_session")

5. Package Management
Modules: pylua_bioxen_vm_lib.utils.curator, pylua_bioxen_vm_lib.env, pylua_bioxen_vm_lib.package_manager
Manages Lua packages and isolated environments using a library-agnostic approach with external catalogs.
Key Classes/Functions:

Curator and get_curator(): Manages package metadata and repositories.
PackageInstaller: Handles installation, updates, and removal of Lua packages.
EnvironmentManager: Manages isolated Lua environments for VMs.
PackageManager: Orchestrates package-related operations.
RepositoryManager: Manages package repositories.
search_packages(query: str) -> List[Package]: Searches for available Lua packages.
bootstrap_lua_environment(env_name: str) -> bool: Bootstraps a Lua environment.

Note: Package management relies on external catalogs, not hardcoded dictionaries (e.g., no pkgdict or ALL_PACKAGES/BIOXEN_PACKAGES constants). Package loading is performed by sending Lua code via send_input.
Example Usage:
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller, search_packages
installer = PackageInstaller()
packages = search_packages("bio_compute")
installer.install_package("bio_compute")

6. Exception Handling
Module: pylua_bioxen_vm_lib.exceptions
Provides specific exceptions for robust error handling.
Key Exceptions:

InteractiveSessionError: General errors in session management.
AttachError: Errors during session attachment.
DetachError: Errors during session detachment.
SessionNotFoundError: Raised when a session ID is invalid.
SessionAlreadyExistsError: Raised when creating a duplicate session.
VMManagerError: Errors in VM manager operations.
LuaVMError: Errors during Lua code execution.

Example Usage:
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.exceptions import SessionNotFoundError
try:
    VMManager().attach_to_vm("nonexistent")
except SessionNotFoundError:
    print("Session not found")

7. Logging
Class: VMLogger
Provides configurable logging for debugging and monitoring.
Parameters:

debug_mode: bool: Enables verbose logging if True.
component: str: Specifies the logging component (e.g., "MyApp").

Example Usage:
from pylua_bioxen_vm_lib.logger import VMLogger
logger = VMLogger(debug_mode=True, component="MyApp")
logger.debug("Debug message")

Usage Patterns
Basic VM Execution
Execute Lua code in a standalone VM:
from pylua_bioxen_vm_lib import create_vm
vm = create_vm("simple_vm", debug_mode=True)
result = vm.execute_string('print("Hello!")')
print(result['stdout'])  # Output: Hello!

Managed VMs
Use a context manager for resource management:
from pylua_bioxen_vm_lib import VMManager
with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("managed_vm")
    result = manager.execute_vm_sync("managed_vm", 'return 2 + 2')
    print(result['stdout'])  # Output: 4

Interactive Sessions
Manage persistent interactive sessions:
from pylua_bioxen_vm_lib import VMManager
manager = VMManager(debug_mode=True)
session = manager.create_interactive_vm("interactive_vm")
manager.send_input("interactive_vm", "x = 10\nprint('Value:', x)\n")
import time
time.sleep(0.5)
print(manager.read_output("interactive_vm"))  # Output: Value: 10
manager.detach_from_vm("interactive_vm")
manager.terminate_vm_session("interactive_vm")

Package Management
Install and use Lua packages:
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
from pylua_bioxen_vm_lib import VMManager
installer = PackageInstaller()
installer.install_package("bio_compute")
with VMManager() as manager:
    session = manager.create_interactive_vm("package_vm")
    manager.send_input("package_vm", 'require("bio_compute")\nprint(bio_compute.compute(10))')
    time.sleep(0.5)
    print(manager.read_output("package_vm"))

Best Practices

Context Managers: Use VMManager with with statements to ensure proper resource cleanup.
Exception Handling: Catch specific exceptions (e.g., SessionNotFoundError) for robust error handling.
Debug Mode: Enable debug logging by setting the environment variable PYLUA_DEBUG=true:export PYLUA_DEBUG=true


Session Lifecycle: Always detach and terminate sessions to free resources.
Package Isolation: Use EnvironmentManager to create isolated Lua environments.
Input Validation: Validate session IDs to avoid SessionAlreadyExistsError.
Package Loading: Load packages by sending require statements via send_input, as there is no direct load_package method.

Example Application
Integrate Lua VMs with package management for biological computation:
import os
from pylua_bioxen_vm_lib import VMManager, VMLogger
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
logger = VMLogger(debug_mode=os.getenv('PYLUA_DEBUG', 'false').lower() == 'true', component="BioApp")
installer = PackageInstaller()
installer.install_package("bio_compute")
with VMManager(debug_mode=True) as manager:
    session = manager.create_interactive_vm("bio_vm")
    manager.send_input("bio_vm", 'require("bio_compute")\nprint("Result:", bio_compute.analyze_sequence("ATCG"))\n')
    import time
    time.sleep(0.5)
    print(manager.read_output("bio_vm"))
    manager.terminate_vm_session("bio_vm")

Dependencies

Python 3.7+
Lua interpreter (installed on the system)
LuaSocket (install via luarocks install luasocket)
pylua_bioxen_vm_lib (install via pip install pylua_bioxen_vm_lib)

Installation
pip install pylua_bioxen_vm_lib
luarocks install luasocket

Notes

Integrates with the BioXen framework for biological computing and genomic data virtualization.
Networking (networked=True) is experimental and requires LuaSocket.
Package management is library-agnostic, using external catalogs managed by Curator and EnvironmentManager. Legacy hardcoded dictionaries (e.g., pkgdict) are not used.
Package loading and REPL functionality are implemented via send_input and read_output.
For API access, visit xAI API.
