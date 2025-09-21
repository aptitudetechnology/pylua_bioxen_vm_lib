"""
Utilities package for pylua_bioxen_vm_lib.

Contains utility classes and functions for package management and other common operations.
"""

try:
    from .curator import Curator
    __all__ = ['Curator']
except ImportError:
    # Curator is optional for Phase 1 testing
    __all__ = []