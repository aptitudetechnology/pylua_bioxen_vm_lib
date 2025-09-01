# Installation Guide - PyLua BioXen VM Library

## Phase 3: Complete Installation with XCP-ng Support

This guide covers installation and setup for the complete pylua_bioxen_vm_lib system with XCP-ng integration and CLI support.

## Table of Contents

- [Quick Installation](#quick-installation)
- [BioXen-luavm CLI Installation](#bioxen-luavm-cli-installation)
- [XCP-ng Infrastructure Setup](#xcp-ng-infrastructure-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Quick Installation

### Prerequisites

- **Python 3.7+**
- **pip** (Python package installer)
- **Git** (for development installation)

### Install from PyPI

```bash
# Install latest stable version
pip install pylua-bioxen-vm-lib

# Install development version from test PyPI
pip install --index-url https://test.pypi.org/simple/ pylua-bioxen-vm-lib
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/aptitudetechnology/pylua_bioxen_vm_lib.git
cd pylua_bioxen_vm_lib

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Dependencies

The following dependencies are automatically installed:

- **requests** (≥2.31.0) - XAPI communication
- **paramiko** (≥3.0.0) - SSH sessions
- **urllib3** - HTTP handling
- **questionary** - Interactive CLI (for BioXen-luavm CLI)

---

## BioXen-luavm CLI Installation

### CLI Dependencies

```bash
# Install CLI-specific dependencies
pip install questionary

# Or install all dependencies
pip install -r requirements.txt
```

### Download CLI Interface

The interactive CLI is included in the package:

```bash
# Make CLI executable
chmod +x interactive-bioxen-lua.py

# Test CLI
python interactive-bioxen-lua.py
```

### System Requirements for CLI

- **Terminal** with Unicode support (for emojis and formatting)
- **Interactive Python environment**
- **Network access** (for XCP-ng VM management)

---

## XCP-ng Infrastructure Setup

### XCP-ng Host Requirements

- **XCP-ng 8.2+** or **XenServer 8.0+**
- **XAPI access** enabled
- **Network connectivity** from client to XCP-ng host
- **SSH access** to created VMs

### XCP-ng Template Preparation

Create a Lua-ready template for VM deployment:

#### 1. Create Base VM

```bash
# In XCP-ng host or XenCenter
# Create new VM with Ubuntu 20.04/22.04 or Debian 11/12
```

#### 2. Install Lua Runtime

```bash
# Connect to the base VM and install required packages
sudo apt-get update
sudo apt-get install -y \
    lua5.3 \
    luarocks \
    openssh-server \
    git \
    build-essential \
    curl \
    wget

# Enable SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure SSH for root access (if needed)
sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Install common LuaRocks packages
sudo luarocks install luasocket
sudo luarocks install lua-cjson
sudo luarocks install penlight
```

#### 3. Configure VM Template

```bash
# Create a dedicated user for Lua execution (optional)
sudo useradd -m -s /bin/bash luauser
sudo usermod -aG sudo luauser

# Set up SSH keys or password authentication
# (Configure according to your security requirements)

# Clean up for template creation
sudo apt-get clean
sudo rm -rf /tmp/*
sudo history -c
```

#### 4. Convert to Template

In XCP-ng management interface:
1. Shut down the VM
2. Right-click VM → "Convert to Template"
3. Name template: `lua-bio-template`
4. Verify template appears in template list

#### 5. Test Template

```bash
# Create test VM from template
# Verify VM boots and SSH is accessible
# Confirm Lua runtime works: lua -v
```

### Network Configuration

Ensure VMs created from template have network access:

- **DHCP configuration** for automatic IP assignment
- **DNS resolution** configured
- **Firewall rules** allow SSH (port 22)
- **Gateway configuration** for internet access (if needed for package installation)

---

## Configuration

### Basic Configuration

For basic VMs (local processes), no additional configuration is required.

### XCP-ng Configuration

#### Method 1: Configuration File

Create `xcpng_config.json` in your working directory:

```json
{
    "xapi_url": "https://your-xcpng-host.local",
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

#### Method 2: Environment Variables

```bash
export XCPNG_HOST="your-xcpng-host.local"
export XCPNG_USERNAME="root"
export XCPNG_PASSWORD="your_password"
export XCPNG_TEMPLATE="lua-bio-template"
```

#### Method 3: Runtime Configuration

Configure through CLI prompts or programmatically:

```python
config = {
    "xapi_url": "https://xcpng-host",
    "username": "root",
    "password": "password",
    "template": "lua-bio-template"
}
```

### Security Considerations

- **Use SSH keys** instead of passwords when possible
- **Restrict network access** to XCP-ng management network
- **Use dedicated service accounts** rather than root
- **Enable SSL verification** in production environments
- **Store passwords securely** (consider using environment variables or secret management)

---

## Verification

### Test Basic Installation

```python
# Test basic VM functionality
from pylua_bioxen_vm_lib import create_vm

vm = create_vm("test_basic", vm_type="basic")
result = vm.execute_string('print("Hello, World!")')
print(result['stdout'])  # Should output: Hello, World!
```

### Test XCP-ng Integration

```python
# Test XCP-ng VM functionality (requires infrastructure)
config = {
    "xapi_url": "https://your-xcpng-host",
    "username": "root",
    "password": "your_password",
    "template": "lua-bio-template"
}

try:
    vm = create_vm("test_xcpng", vm_type="xcpng", config=config)
    vm.start()
    result = vm.execute_string('print("Hello from XCP-ng!")')
    print(result['stdout'])
    vm.stop()
    print("✅ XCP-ng integration working")
except Exception as e:
    print(f"❌ XCP-ng test failed: {e}")
```

### Test CLI Interface

```bash
# Test interactive CLI
python interactive-bioxen-lua.py

# Should show main menu:
# 🧬 BioXen-luavm Interactive CLI
# Multi-VM Lua Environment with XCP-ng Support
```

### Test VMManager

```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Test basic VM
    session = manager.create_interactive_vm("test", vm_type="basic")
    manager.send_input("test", "print('VMManager working')")
    output = manager.read_output("test")
    print(output)
```

---

## Troubleshooting

### Common Installation Issues

#### Missing Dependencies

```bash
# Error: ModuleNotFoundError: No module named 'questionary'
pip install questionary

# Error: ModuleNotFoundError: No module named 'paramiko'  
pip install paramiko>=3.0.0

# Error: ModuleNotFoundError: No module named 'requests'
pip install requests>=2.31.0
```

#### Python Version Issues

```bash
# Check Python version
python --version  # Should be 3.7+

# Use specific Python version
python3.8 -m pip install pylua-bioxen-vm-lib
```

### XCP-ng Connection Issues

#### XAPI Connection Failed

```bash
# Error: Connection refused
# Solution: Check host connectivity
ping your-xcpng-host
telnet your-xcpng-host 443

# Error: SSL verification failed
# Solution: Set verify_ssl: false in config or use proper certificates
```

#### Authentication Failed

```bash
# Error: Invalid credentials
# Solution: Verify username/password
# Test with XenCenter or xsconsole

# Error: Permission denied
# Solution: Ensure user has VM management permissions
```

#### Template Not Found

```bash
# Error: Template 'lua-bio-template' not found
# Solution: Verify template exists and is accessible
xe template-list name-label=lua-bio-template
```

### SSH Connection Issues

#### VM SSH Timeout

```bash
# Error: SSH connection timeout
# Solution: Check VM network configuration
# Verify SSH service is running in VM
# Check firewall rules

# Test SSH manually
ssh root@vm-ip-address
```

#### SSH Authentication Failed

```bash
# Error: SSH authentication failed
# Solution: Verify SSH credentials
# Check SSH key configuration
# Ensure SSH service allows desired authentication method
```

### CLI Issues

#### Unicode/Emoji Display Problems

```bash
# Issue: Emojis not displaying properly
# Solution: Use terminal with Unicode support
# Set proper locale: export LANG=en_US.UTF-8
```

#### Interactive Input Problems

```bash
# Issue: CLI not responding to input
# Solution: Ensure terminal supports interactive mode
# Try different terminal (bash, zsh, etc.)
```

### Performance Issues

#### Slow VM Creation

```bash
# Issue: XCP-ng VM creation takes too long
# Solution: 
# - Check XCP-ng host performance
# - Verify network connectivity
# - Use faster storage for VM templates
# - Reduce VM resource requirements
```

#### Memory Issues

```bash
# Issue: Out of memory errors
# Solution:
# - Reduce VM memory allocation in config
# - Check available host resources
# - Monitor VM memory usage
```

---

## Advanced Configuration

### Custom VM Templates

Create specialized templates for different use cases:

```bash
# Bioinformatics template with additional tools
sudo apt-get install -y \
    python3-biopython \
    emboss \
    ncbi-blast+ \
    samtools

# Data science template with R and libraries
sudo apt-get install -y \
    r-base \
    python3-pandas \
    python3-numpy
```

### Load Balancing

Distribute VMs across multiple XCP-ng hosts:

```python
# Configure multiple hosts
configs = [
    {
        "xapi_url": "https://xcpng-host1",
        "username": "root",
        "password": "password1",
        "template": "lua-bio-template"
    },
    {
        "xapi_url": "https://xcpng-host2", 
        "username": "root",
        "password": "password2",
        "template": "lua-bio-template"
    }
]

# Round-robin VM creation
for i, config in enumerate(configs):
    vm = create_vm(f"vm_{i}", vm_type="xcpng", config=config)
```

### Monitoring and Logging

Enable comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use with debug mode
manager = VMManager(debug_mode=True)
```

---

## Next Steps

After successful installation:

1. **Explore Examples**: Run the example scripts in `examples/`
2. **Try the CLI**: Use `python interactive-bioxen-lua.py` for interactive management
3. **Deploy Infrastructure**: Set up XCP-ng templates for production use
4. **Scale Up**: Configure multiple XCP-ng hosts for larger workloads
5. **Customize**: Create specialized VM templates for your use cases

For additional help:
- Check the [API Documentation](api.md)
- Review the [CLI Integration Guide](cli_integration.md)
- See example configurations in the project repository
