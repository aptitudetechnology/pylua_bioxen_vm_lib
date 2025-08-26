# GitHub Copilot Prompt: Fix LuaRocks Installation Permissions Issue

## Problem Description
The `pylua_bioxen_vm_lib.utils.curator` module is failing to install LuaRocks packages due to permissions errors when trying to write to system directories like `/usr/local/lib/luarocks/rocks-5.1`.

**Error Message:**
```
Error: Your user does not have write permissions in /usr/local/lib/luarocks/rocks-5.1 
-- you may want to run as a privileged user or use your local tree with --local.
```

**Current Failing Behavior:**
- Curator tries to install packages system-wide without checking permissions
- All package installations fail with permission errors
- Environment setup reports 0/3 packages installed successfully
- No fallback to local user installation

## Required Solution

### Primary Objective
Modify the curator's package installation logic to:
1. **Always use `--local` flag** for LuaRocks installations to install in user's home directory
2. **Automatically configure Lua environment paths** to find locally installed packages
3. **Provide proper error handling** and fallback mechanisms
4. **Validate local installations** work correctly with the Lua VM

### Technical Requirements

#### 1. Installation Command Changes
```python
# BEFORE (failing):
subprocess.run(["luarocks", "install", package_name])

# AFTER (should work):
subprocess.run(["luarocks", "install", "--local", package_name, version])
```

#### 2. Environment Path Configuration
The curator should set these environment variables for the Lua VM:
```python
lua_env = {
    "LUA_PATH": f"{os.path.expanduser('~')}/.luarocks/share/lua/5.1/?.lua;{os.path.expanduser('~')}/.luarocks/share/lua/5.1/?/init.lua;{os.environ.get('LUA_PATH', '')}",
    "LUA_CPATH": f"{os.path.expanduser('~')}/.luarocks/lib/lua/5.1/?.so;{os.environ.get('LUA_CPATH', '')}"
}
```

#### 3. Validation Logic
```python
def verify_local_package_installation(package_name: str) -> bool:
    """Verify a package is installed locally and accessible"""
    local_rocks_path = os.path.expanduser("~/.luarocks/lib/luarocks/rocks-5.1")
    # Check if package directory exists
    # Test Lua import capability
    return package_exists and lua_can_import
```

### Implementation Context

**File Location:** `pylua_bioxen_vm_lib/utils/curator.py`

**Key Methods to Modify:**
- `install_package(self, package_name: str, version: str = "latest") -> bool`
- `curate_environment(self, profile_name: str) -> bool`
- `health_check(self) -> Dict[str, Any]`
- `list_installed_packages(self) -> List[Dict[str, str]]`

**Expected Package Types:**
- Core packages: `lua-cjson`, `luafilesystem`, `luasocket`
- BioXen packages: `bio-utils`, `sequence-parser`, `phylo-tree`
- Extended packages: `gabby-lua`, `lua-radio`, `penlight`

### Enhanced Features to Add

#### 1. Permission Detection
```python
def can_write_to_system_luarocks() -> bool:
    """Check if user has write permissions to system LuaRocks directory"""
    system_path = "/usr/local/lib/luarocks/rocks-5.1"
    return os.access(system_path, os.W_OK) if os.path.exists(system_path) else False
```

#### 2. Local Environment Setup
```python
def ensure_local_luarocks_environment():
    """Ensure ~/.luarocks directory structure exists and is configured"""
    luarocks_home = os.path.expanduser("~/.luarocks")
    os.makedirs(f"{luarocks_home}/lib/lua/5.1", exist_ok=True)
    os.makedirs(f"{luarocks_home}/share/lua/5.1", exist_ok=True)
```

#### 3. Installation Retry Logic
```python
def install_package_with_fallback(package_name: str, version: str) -> bool:
    """Try local installation with proper error handling and path setup"""
    try:
        # Ensure local environment exists
        ensure_local_luarocks_environment()
        
        # Install with --local flag
        result = subprocess.run([
            "luarocks", "install", "--local", package_name, version
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Verify installation worked
            return verify_local_package_installation(package_name)
        else:
            logger.error(f"LuaRocks installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Package installation exception: {e}")
        return False
```

#### 4. VM Environment Integration
The curator should pass the local LuaRocks paths to any created Lua VMs so they can find locally installed packages.

### Testing Requirements

**Test Cases Needed:**
1. Install package locally without system permissions
2. Verify Lua VM can import locally installed packages
3. Check `luarocks list --local` shows installed packages
4. Validate environment paths are set correctly
5. Test package installation rollback on failure

**Expected Success Criteria:**
- All packages install successfully with `--local` flag
- Lua VM can `require()` all installed packages
- `health_check()` reports correct number of installed packages
- No permission errors during installation
- Proper error messages for actual installation failures (not permission issues)

### Logging and Error Handling

**Enhanced Logging:**
```python
logger.info(f"Installing {package_name} v{version} locally...")
logger.debug(f"Using LuaRocks command: luarocks install --local {package_name} {version}")
logger.info(f"Package {package_name} installed successfully in ~/.luarocks/")
```

**Error Messages:**
- Clear distinction between permission errors and actual package failures
- Helpful suggestions when LuaRocks is not available
- Guidance for users on local vs system installation

---

**Generate the complete updated curator.py methods with all the above requirements implemented, maintaining compatibility with existing curator interface while fixing the permissions issue through local installation.**