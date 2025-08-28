### Prompt for GitHub Copilot

```
"""
Objective: Add a "virtual-to-physical" conversion feature to `pylua_bioxen_vm_lib`.

Goal: Implement the `convert_vm_to_elua` function within the `VMCLI` class to generate a flashable eLua firmware binary from a virtual Lua VM state.

This task requires orchestrating external build tools and a cross-compiler. Do not implement the build tools or the cross-compiler itself; assume they are available on the system. Focus on the Python logic to prepare the project, execute the build process, and handle the output.

Step-by-step implementation:

1.  **Define a new class `EluaConverter`**:
    * Initialize with the path to the eLua build system root and the cross-compiler toolchain.
    * Create a method `convert_vm(vm_id, target_hardware)` that:
        * Accepts `vm_id` (string) and `target_hardware` (string, e.g., 'esp32', 'stm32f4').
        * Validates the target hardware against a list of supported platforms.
        * Creates a temporary directory to store the eLua project files.
        * Copies the eLua build system template files into this temporary directory.
        * Retrieves all Lua scripts and package configurations associated with the specified `vm_id`.
        * Writes these Lua scripts and configurations into the appropriate project structure within the temporary directory.
        * Constructs and executes the build command for the eLua build system (e.g., `scons` or a `Makefile`). This command should point to the correct cross-compiler and build a firmware for the specified `target_hardware`. Use Python's `subprocess` module for this.
        * Waits for the build process to complete and checks the return code for success or failure.
        * Locates the generated firmware binary file (e.g., `firmware.bin`) in the build output.
        * Returns the path to the generated firmware file on success, or raises an exception on failure.
    * Implement proper cleanup to remove the temporary directory.

2.  **Integrate `EluaConverter` into `VMCLI`**:
    * In the `VMCLI`'s `__init__`, instantiate `EluaConverter` with a placeholder path.
    * In the `convert_vm_to_elua` method (which currently only contains placeholder print statements):
        * Call `self.elua_converter.convert_vm(vm_id, hardware_choice)`.
        * Handle potential exceptions from the converter.
        * On success, print a message showing the path to the newly generated firmware binary.
        * On failure, print an informative error message.
    * Update the `show_environment_status` method to include a check for the presence of the required build tools (e.g., `scons`, `luac`, and the cross-compiler).

3.  **Refine the `VMCLI`'s `convert_vm_to_elua` method**:
    * Instead of a simple `input("Press Enter...")`, display the final path of the generated firmware and prompt the user to continue.
    * Add a new prompt to ask the user for the path to the eLua build system root and the cross-compiler toolchain, storing these in the `VMCLI` class.
    
Expected Output: A complete, runnable Python class that orchestrates the conversion from a virtual Lua VM to a physical eLua firmware binary.
"""
```