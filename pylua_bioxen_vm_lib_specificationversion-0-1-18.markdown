pylua_bioxen_vm_lib Specification

Overview

The pylua_bioxen_vm_lib (version 0.1.15[metadata]
name = pylua_bioxen_vm_lib
version = 0.1.15 
description = Process-isolated networked Lua VMs managed from Python (extracted from BioXen)
long_description = file: README.md
long_description_content_type = text/markdown

[options][metadata]
name = pylua_bioxen_vm_lib
version = 0.1.15 
description = Process-isolated networked Lua VMs managed from Python (extracted from BioXen)
long_description = file: README.md
long_description_content_type = text/markdown

[options]
packages = find:
python_requires = >=3.7
include_package_data = True

[options.packages.find]
exclude = tests*
packages = find:
python_requires = >=3.7
include_package_data = True

[options.packages.find]
exclude = tests*) is a Python library for managing Lua virtual machines (VMs) within the BioXen framework, supporting biological computation and genomic data virtualization. It provides synchronous and asynchronous Lua code execution, interactive session management, and package management for Lua environments. This library is designed for applications integrating lightweight, sandboxed Lua VMs with biological workflows.

This specification, updated for the development branch, aligns with the codebase and addresses compliance findings for accurate developer guidance.

Key Components

1. VM Creation





Module: pylua_bioxen_vm_lib



Key Function: create_vm(vm_id: str = "default", networked: bool = False, persistent: bool = False, debug_mode: bool = False, lua_executable: str = "lua") -> LuaProcess





Creates a Lua VM instance.



Parameters:





vm_id: Unique VM identifier (defaults to "default").



networked: Enables experimental networking if True.



persistent: If True, creates a VM that persists across sessions.



debug_mode: Enables verbose logging if True.



lua_executable: Path to the Lua executable (defaults to "lua").



Returns: A LuaProcess object for executing Lua code.



Example:

from pylua_bioxen_vm_lib import create_vm
vm = create_vm("test_vm", debug_mode=True)
result = vm.execute_string('print("Hello, BioXen!")')
print(result['stdout'])  # Output: Hello, BioXen!

2. VM Manager





Class: VMManager





Manages multiple Lua VMs and sessions.



Key Methods:





create_vm(vm_id: str, networked: bool = False, persistent: bool = False) -> LuaProcess: Creates a managed VM.



execute_vm_sync(vm_id: str, code: str) -> dict: Executes Lua code synchronously, returning { 'stdout': str, ... }.



execute_vm_async(vm_id: str, code: str) -> Future: Executes Lua code asynchronously, returning a Future object.



create_interactive_vm(vm_id: str) -> InteractiveSession: Creates a persistent interactive session.



attach_to_vm(vm_id: str) -> InteractiveSession: Attaches to an existing session.



detach_from_vm(vm_id: str): Detaches from a session.



terminate_vm_session(vm_id: str): Terminates a session.



send_input(vm_id: str, input: str): Sends input to an interactive session.



read_output(vm_id: str) -> str: Reads output from a session.



list_sessions() -> List[dict]: Lists active sessions.



Usage:

from pylua_bioxen_vm_lib import VMManager
with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("managed_vm")
    result = manager.execute_vm_sync("managed_vm", 'print("Result:", 2 + 2)')
    print(result['stdout'])  # Output: Result: 4

3. Interactive Session





Class: InteractiveSession





Manages interactive Lua VM sessions.



Key Methods:





send_input(input: str): Sends Lua code to the session.



read_output() -> str: Retrieves session output.



interactive_loop(): Starts an interactive REPL loop (may use send_input/read_output internally).



load_package(package_name: str): Loads a Lua package (may use send_input).



set_environment(env_name: str): Sets the Lua environment.



Note: load_package and interactive_loop may be implemented via send_input/read_output in some configurations.



Usage:

from pylua_bioxen_vm_lib import VMManager
manager = VMManager(debug_mode=True)
session = manager.create_interactive_vm("interactive_vm")
manager.send_input("interactive_vm", "x = 42\nprint('Value:', x)\n")
import time
time.sleep(0.5)
print(manager.read_output("interactive_vm"))  # Output: Value: 42

4. Session Manager





Class: SessionManager





Manages interactive session lifecycles.



Key Methods:





list_sessions() -> dict: Returns active session IDs and details.



terminate_session(vm_id: str): Terminates a session.



Usage:

from pylua_bioxen_vm_lib import VMManager
manager = VMManager(debug_mode=True)
session_manager = manager.session_manager
session = manager.create_interactive_vm("test_session")
sessions = session_manager.list_sessions()
print(sessions)  # Output: {'test_session': <session_details>}
session_manager.terminate_session("test_session")

5. Package Management





Modules: pylua_bioxen_vm_lib.utils.curator, pylua_bioxen_vm_lib.env, pylua_bioxen_vm_lib.package_manager





Manages Lua packages and environments.



Key Classes/Functions:





Curator and get_curator(): Manages package metadata and repositories.



PackageInstaller: Handles package installation, updates, and removal.



EnvironmentManager: Manages isolated Lua environments.



PackageManager: Orchestrates package operations.



RepositoryManager: Manages repositories.



search_packages(query: str) -> List[Package]: Searches for packages.



bootstrap_lua_environment(env_name: str) -> bool: Bootstraps an environment.



Note: Features like dependency resolution and package validation may be integrated into Curator or PackageInstaller.



Usage:

from pylua_bioxen_vm_lib.utils.curator import PackageInstaller, search_packages
installer = PackageInstaller()
packages = search_packages("math")
installer.install_package("math_package")

6. Exception Handling





Module: pylua_bioxen_vm_lib.exceptions





Key Exceptions:





InteractiveSessionError: General session errors.



AttachError: Attachment errors.



DetachError: Detachment errors.



SessionNotFoundError: Invalid session ID.



SessionAlreadyExistsError: Duplicate session creation.



VMManagerError: VM manager errors.



LuaVMError: Lua execution errors.



Usage:

from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.exceptions import SessionNotFoundError
try:
    VMManager().attach_to_vm("nonexistent")
except SessionNotFoundError:
    print("Session not found")

7. Logging





Class: VMLogger





Configurable logging.



Parameters:





debug_mode: bool: Enables verbose logging.



component: str: Logging component (e.g., "MyApp").



Usage:

from pylua_bioxen_vm_lib.logger import VMLogger
logger = VMLogger(debug_mode=True, component="MyApp")
logger.debug("Debug message")

Usage Patterns

Basic VM Execution

Execute Lua code:

from pylua_bioxen_vm_lib import create_vm
vm = create_vm("simple_vm", debug_mode=True)
result = vm.execute_string('print("Hello!")')
print(result['stdout'])  # Output: Hello!

Managed VMs

Use context manager:

from pylua_bioxen_vm_lib import VMManager
with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("managed_vm")
    result = manager.execute_vm_sync("managed_vm", 'return 2 + 2')
    print(result['stdout'])  # Output: 4

Interactive Sessions

Manage persistent sessions:

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

Install and use packages:

from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
from pylua_bioxen_vm_lib import VMManager
installer = PackageInstaller()
installer.install_package("math_package")
with VMManager() as manager:
    session = manager.create_interactive_vm("package_vm")
    session.load_package("math_package")
    manager.send_input("package_vm", "print(math_package.compute(10))")
    time.sleep(0.5)
    print(manager.read_output("package_vm"))

Best Practices





Context Managers: Use VMManager with with statements for resource cleanup.



Exception Handling: Catch specific exceptions (e.g., SessionNotFoundError).



Debug Mode: Set PYLUA_DEBUG=true for detailed logging:

export PYLUA_DEBUG=true



Session Lifecycle: Detach and terminate sessions to free resources.



Package Isolation: Use EnvironmentManager for isolated environments.



Input Validation: Check session IDs to avoid SessionAlreadyExistsError.

Example Application

Integrate Lua VMs and packages:

import os
from pylua_bioxen_vm_lib import VMManager, VMLogger
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
logger = VMLogger(debug_mode=os.getenv('PYLUA_DEBUG', 'false').lower() == 'true', component="App")
installer = PackageInstaller()
installer.install_package("math_package")
with VMManager(debug_mode=True) as manager:
    session = manager.create_interactive_vm("app_vm")
    session.load_package("math_package")
    manager.send_input("app_vm", 'print("Result:", math_package.compute(10))\n')
    import time
    time.sleep(0.5)
    print(manager.read_output("app_vm"))
    manager.terminate_vm_session("app_vm")

Dependencies





Python 3.6+



pylua-bioxen-vm-lib (install via pip install pylua-bioxen-vm-lib)

Notes





Integrates with BioXen for biological computing.



Networking (networked=True) is experimental.



Package management features (e.g., dependency resolution) may be part of Curator or PackageInstaller.



load_package and interactive_loop may use send_input/read_output internally.



For API access, visit xAI API.