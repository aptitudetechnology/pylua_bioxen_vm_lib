"""
Custom exceptions for pylua_bioxen_vm_lib library.
"""

class LuaVMError(Exception):
    """Base exception for all Lua VM related errors."""
    pass

class LuaProcessError(LuaVMError):
    """Raised when there's an error with Lua subprocess execution."""
    def __init__(self, message, return_code=None, stderr=None):
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr

class NetworkingError(LuaVMError):
    """Raised for networking-related errors in Lua VMs."""
    pass

class LuaNotFoundError(LuaVMError):
    """Raised when the Lua interpreter is not found."""
    pass

class PTYError(LuaVMError):
    """Raised when there's an error with PTY (pseudo-terminal) operations."""
    pass

class LuaSocketNotFoundError(LuaVMError):
    """Raised when LuaSocket is not available."""
    pass

class VMConnectionError(LuaVMError):
    """Raised when a VM connection fails."""
    pass

class VMTimeoutError(LuaVMError):
    """Raised when a VM operation times out."""
    pass

class ScriptGenerationError(LuaVMError):
    """Raised when there's an error generating dynamic Lua scripts."""
    pass

class InteractiveSessionError(LuaVMError):
    """Raised for errors in interactive session management."""
    pass

class AttachError(InteractiveSessionError):
    """Raised when attaching to a session fails."""
    pass

class DetachError(InteractiveSessionError):
    """Raised when detaching from a session fails."""
    pass

class SessionNotFoundError(InteractiveSessionError):
    """Raised when trying to access a session that doesn't exist."""
    pass

class SessionAlreadyExistsError(InteractiveSessionError):
    """Raised when trying to create a session with an ID that already exists."""
    pass

class IOThreadError(InteractiveSessionError):
    """Raised when there's an error with I/O threading operations."""
    pass

class SessionStateError(InteractiveSessionError):
    """Raised when there's an error with session state management."""
    pass

class XCPngConnectionError(LuaVMError):
    """Raised when XCP-ng connection or authentication fails."""
    pass

class VMManagerError(LuaVMError):
    """Raised when there's an error with VM manager operations."""
    pass

class ProcessRegistryError(VMManagerError):
    """Raised when there's an error with the persistent VM registry."""
    pass