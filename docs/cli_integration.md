# BioXen-luavm CLI: XCP-ng Integration Guide

## Phase 3: Complete CLI Integration

This guide explains XCP-ng VM support in the BioXen-luavm CLI, enabling seamless management of both local and remote Lua VMs through a unified interface.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [VM Type Selection](#vm-type-selection)
- [Configuration Management](#configuration-management)
- [Unified VM Management](#unified-vm-management)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Overview

The BioXen-luavm CLI integrates XCP-ng VM support through:

1. **VM Type Selection**: Choose between local and XCP-ng VMs during creation
2. **Configuration Management**: Load XCP-ng settings from JSON files or manual entry
3. **Unified Interface**: Same commands work for both VM types
4. **Status Tracking**: CLI shows VM type in status displays with visual indicators

### Key Features

- **🖥️ Local Process VMs**: Traditional local Lua execution (Phase 1)
- **☁️ XCP-ng VMs**: Remote virtual machines with XAPI/SSH integration (Phase 2)
- **🔧 Configuration**: File-based and interactive configuration options
- **📊 Status**: Real-time VM monitoring with type indicators
- **🔗 Sessions**: Persistent interactive sessions for both VM types

---

## Getting Started

### Launch the CLI

```bash
# Start the interactive CLI
python interactive-bioxen-lua.py
```

### Main Menu

```
🧬 BioXen-luavm Interactive CLI
Multi-VM Lua Environment with XCP-ng Support
========================================

📊 Status: 0/0 VMs running
   🖥️  Local: 0 | ☁️  XCP-ng: 0

What would you like to do?
❯ 🚀 Create new Lua VM
  📋 List VMs
  🔗 Attach to VM
  🛑 Terminate VM
  ❌ Exit
```

---

## VM Type Selection

### Creating a New VM

When you select "🚀 Create new Lua VM", you'll be prompted for:

1. **VM ID**: Unique identifier for the VM
2. **VM Type**: Choose between basic and XCP-ng
3. **Configuration**: XCP-ng VMs require additional setup
4. **Profile**: VM profile name (optional)

### VM Type Options

```
Select VM type:
❯ 🖥️  Local Process VM (basic)
  ☁️  XCP-ng Virtual Machine (xcpng)
```

#### 🖥️ Local Process VM (basic)
- Runs Lua as local process
- No additional configuration required
- Immediate startup
- Uses local system resources

#### ☁️ XCP-ng Virtual Machine (xcpng)
- Creates VM on XCP-ng infrastructure
- Requires XCP-ng configuration
- Network-based execution
- Scalable and isolated

---

## Configuration Management

### XCP-ng Configuration Options

When creating an XCP-ng VM, you'll see:

```
XCP-ng configuration:
❯ 📁 Load from config file
  ⚙️  Enter manually
  ❌ Cancel
```

### Method 1: Configuration File

#### Create Configuration File

Create `xcpng_config.json` in your working directory:

```json
{
    "xapi_url": "https://192.168.1.100",
    "username": "root",
    "password": "your_secure_password",
    "template": "lua-bio-template",
    "vm_name_prefix": "bioxen-lua",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": false,
    "ssh_timeout": 30,
    "vm_network": "Pool-wide network associated with eth0"
}
```

#### Load in CLI

```
Path to XCP-ng config file (JSON): xcpng_config.json
✅ Loaded configuration from xcpng_config.json
```

### Method 2: Manual Entry

#### Interactive Configuration

```
🔧 Manual XCP-ng Configuration
========================================
XCP-ng host IP/hostname: 192.168.1.100
Username: root
Password: [hidden]
VM template name: lua-bio-template
Configure advanced settings? No
```

#### Advanced Settings (Optional)

```
Memory allocation: 4GB
Number of vCPUs: 4
```

### Configuration Fields

#### Required Fields
- **XCP-ng host**: IP address or hostname of XCP-ng server
- **Username**: XCP-ng user account (typically 'root')
- **Password**: Authentication password
- **Template**: Name of Lua-ready VM template

#### Optional Fields
- **Memory**: RAM allocation (default: "2GB")
- **vCPUs**: Virtual CPU count (default: 2)
- **VM name prefix**: Prefix for created VMs (default: "bioxen-lua")
- **SSL verification**: Enable/disable SSL checks (default: false)
- **SSH timeout**: Connection timeout in seconds (default: 30)

---

## Unified VM Management

### VM Creation Flow

#### Basic VM Creation
```
🔄 Creating basic VM 'my_basic_vm' with profile 'standard'...
✅ 🖥️ Local Process VM 'my_basic_vm' created successfully!
📊 Profile: standard
```

#### XCP-ng VM Creation
```
🔄 Creating xcpng VM 'my_xcpng_vm' with profile 'standard'...
✅ ☁️ XCP-ng VM 'my_xcpng_vm' created successfully!
📊 Profile: standard
🏠 Host: https://192.168.1.100
📋 Template: lua-bio-template
```

### VM Status Display

```
🖥️  VM List
=====================================

📋 VM ID: my_basic_vm
   Type: 🖥️ Local Process
   Profile: standard
   Status: 🟢 Running
   Created: 2025-09-01 10:30:00
   Uptime: 0d 2h 15m

📋 VM ID: my_xcpng_vm
   Type: ☁️ XCP-ng VM
   Profile: standard  
   Status: 🟢 Running 🔗 Attached
   Created: 2025-09-01 10:32:00
   Uptime: 0d 2h 13m
   Host: https://192.168.1.100
   Template: lua-bio-template
```

### Interactive Sessions

Both VM types provide identical interactive experiences:

#### Attaching to a VM
```
Select VM to attach to:
❯ 🖥️ my_basic_vm (basic) 🟢
  ☁️ my_xcpng_vm (xcpng) 🟢

🔗 Attaching to VM 'my_xcpng_vm'...
✅ Attached to xcpng VM 'my_xcpng_vm'
💡 Type 'exit' to detach from VM
💡 Enter Lua commands directly
--------------------------------------------------
lua[my_xcpng_vm]> 
```

#### Interactive Commands
```
lua[my_xcpng_vm]> print("Hello from XCP-ng VM!")
Hello from XCP-ng VM!

lua[my_xcpng_vm]> x = 42
lua[my_xcpng_vm]> print("Answer:", x)
Answer: 42

lua[my_xcpng_vm]> for i=1,3 do print("Count:", i) end
Count: 1
Count: 2
Count: 3

lua[my_xcpng_vm]> exit
🔗 Detached from VM 'my_xcpng_vm'
```

### VM Lifecycle Management

#### Terminating VMs
```
Select VM to terminate:
❯ 🖥️ my_basic_vm (basic) 🟢
  ☁️ my_xcpng_vm (xcpng) 🟢

⚠️  Terminate VM 'my_xcpng_vm'? This will stop all processes. No

🛑 Terminating VM 'my_xcpng_vm'...
✅ VM 'my_xcpng_vm' terminated successfully
```

---

## Troubleshooting

### Common Issues

#### XCP-ng Connection Failed
```
❌ VM creation failed: Connection to XCP-ng host failed
💡 Check XCP-ng host connectivity and configuration
   - Verify host is reachable
   - Check credentials  
   - Confirm template exists
```

**Solutions:**
1. **Verify Host Connectivity**
   ```bash
   ping 192.168.1.100
   telnet 192.168.1.100 443
   ```

2. **Check Credentials**
   - Verify username/password in configuration
   - Test with XenCenter or XCP-ng Center

3. **Confirm Template Exists**
   ```bash
   # On XCP-ng host
   xe template-list name-label=lua-bio-template
   ```

#### Template Not Found
```
❌ XCP-ng VM creation failed: Template 'lua-bio-template' not found
💡 Check XCP-ng host connectivity and configuration
```

**Solutions:**
1. **Verify Template Name**
   - Check exact template name in XCP-ng
   - Template names are case-sensitive

2. **Create Template**
   - Follow [Installation Guide](installation.md#xcp-ng-template-preparation)
   - Ensure template has Lua runtime installed

#### SSH Connection Timeout
```
❌ VM creation failed: SSH connection to VM timed out
```

**Solutions:**
1. **Check VM Network**
   - Verify VM has network connectivity
   - Check DHCP configuration

2. **Verify SSH Service**
   - Ensure SSH is enabled in template
   - Check firewall rules

3. **Increase Timeout**
   ```json
   {
     "ssh_timeout": 60
   }
   ```

### Configuration Issues

#### Invalid JSON Configuration
```
❌ Invalid JSON in config file: Expecting ',' delimiter
```

**Solution:**
Validate JSON syntax:
```bash
# Test configuration file
python -m json.tool xcpng_config.json
```

#### Missing Required Fields
```
❌ All required fields must be provided
```

**Solution:**
Ensure all required fields are present:
- `xapi_url` (or derived from host)
- `username`
- `password`
- `template`

### Performance Issues

#### Slow VM Creation
- **Reduce VM Resources**: Lower memory/vCPU allocation
- **Check Host Performance**: Monitor XCP-ng host resources
- **Network Latency**: Use local network for XCP-ng access

#### Interactive Session Lag
- **Network Issues**: Check network connectivity to VM
- **VM Resources**: Increase VM memory/CPU allocation
- **SSH Configuration**: Optimize SSH settings

---

## Advanced Usage

### Multiple XCP-ng Hosts

Configure different hosts for different VMs:

#### Host-Specific Configurations
```json
// Production host config
{
    "xapi_url": "https://prod-xcpng.company.com",
    "username": "admin",
    "password": "prod_password",
    "template": "lua-bio-prod-template"
}
```

```json
// Development host config  
{
    "xapi_url": "https://dev-xcpng.company.com",
    "username": "root",
    "password": "dev_password", 
    "template": "lua-bio-dev-template"
}
```

### Batch VM Creation

Create multiple VMs through CLI automation:

```bash
# Script to create multiple VMs
for i in {1..5}; do
    echo "Creating VM batch_$i"
    # Use CLI with predefined responses
done
```

### Custom VM Profiles

Configure different VM profiles for various use cases:

#### Bioinformatics Profile
```json
{
    "memory": "8GB",
    "vcpus": 4,
    "template": "lua-bio-heavy-template"
}
```

#### Lightweight Profile  
```json
{
    "memory": "1GB",
    "vcpus": 1,
    "template": "lua-bio-light-template"
}
```

### Integration with External Tools

#### Export VM Information
Extract VM status for external monitoring:

```python
# CLI could be extended to export status
# python interactive-bioxen-lua.py --export-status > vm_status.json
```

#### Automated Deployment
Integrate with deployment pipelines:

```bash
# Configuration through environment
export XCPNG_HOST="deployment-host"
export XCPNG_TEMPLATE="production-template"
python interactive-bioxen-lua.py --create-vm auto_deploy_vm
```

---

## Security Best Practices

### Configuration Security

1. **Secure Password Storage**
   ```bash
   # Use environment variables
   export XCPNG_PASSWORD="secure_password"
   ```

2. **File Permissions**
   ```bash
   # Restrict config file access
   chmod 600 xcpng_config.json
   ```

3. **SSH Key Authentication**
   ```json
   {
     "ssh_key_path": "/path/to/private/key",
     "ssh_username": "luauser"
   }
   ```

### Network Security

1. **VPN Access**: Access XCP-ng through VPN
2. **Firewall Rules**: Restrict access to management network
3. **SSL Certificates**: Use proper SSL certificates in production

### VM Security

1. **Dedicated Users**: Create non-root users for Lua execution
2. **Resource Limits**: Set appropriate CPU/memory limits
3. **Network Isolation**: Use isolated networks for VMs

---

## CLI Reference

### Quick Commands

```bash
# Start CLI
python interactive-bioxen-lua.py

# With debug mode
PYLUA_DEBUG=true python interactive-bioxen-lua.py
```

### Menu Navigation

- **↑/↓**: Navigate menu options
- **Enter**: Select option
- **Ctrl+C**: Cancel current operation
- **Type 'exit'**: Detach from VM session

### Status Indicators

- **🟢**: VM running
- **🔴**: VM stopped
- **🔗**: Session attached
- **🖥️**: Local process VM
- **☁️**: XCP-ng VM

---

This completes the CLI integration guide for Phase 3. The BioXen-luavm CLI provides a seamless interface for managing both local and remote Lua VMs, making distributed biological computation accessible through an intuitive command-line interface.
