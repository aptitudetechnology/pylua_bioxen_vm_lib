"""
pylua_vm.utils - Intelligent utilities for Lua VM management

This package contains sophisticated utilities for managing Lua environments,
with a focus on intelligent curation and bootstrapping capabilities for AGI development.
"""

try:
    from .curator import (
        Curator,
        Package,
        get_curator,
        quick_install,
        bootstrap_lua_environment
    )
except ImportError:
    # Curator is optional for Phase 1 testing
    Curator = None
    Package = None
    get_curator = None
    quick_install = None
    bootstrap_lua_environment = None

# Public API
__all__ = [
    'Curator',
    'Package', 
    'get_curator',
    'quick_install',
    'bootstrap_lua_environment'
]

# Version info
__version__ = '1.0.0'
__author__ = 'AGI Bootstrap Project'

# Convenience aliases for common operations
def create_curator(lua_path=None, manifest_path=None):
    """Create a new curator instance - alias for get_curator"""
    if get_curator:
        return get_curator(lua_path, manifest_path)
    else:
        print("Curator not available - running in Phase 1 mode")
        return None

def install_packages(*packages, profile=None):
    """Install packages or apply profile - alias for quick_install"""
    if quick_install:
        return quick_install(list(packages), profile)
    else:
        print("Package installation not available - running in Phase 1 mode")
        return False

def setup_environment(profile='standard'):
    """Setup complete Lua environment - alias for bootstrap_lua_environment"""
    if bootstrap_lua_environment:
        return bootstrap_lua_environment(profile)
    else:
        print("Environment setup not available - running in Phase 1 mode")
        return False

# Add convenience functions to __all__
__all__.extend(['create_curator', 'install_packages', 'setup_environment'])