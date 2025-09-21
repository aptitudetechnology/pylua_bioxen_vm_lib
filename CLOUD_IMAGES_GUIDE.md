# Cloud Image Quick Setup Guide
## Automated BioXen VM Deployment with Cloud Images

This guide shows how to set up and use cloud images for fully automated BioXen VM deployment on XCP-ng.

## 🚀 Quick Start (5 minutes)

### 1. Setup Cloud Template (One-time)

```bash
# Make setup script executable
chmod +x setup_cloud_template.py

# Run cloud template setup (requires XCP-ng access)
python3 setup_cloud_template.py
```

This will:
- ✅ Download Debian 12 cloud image (650MB)
- ✅ Import to XCP-ng as template
- ✅ Configure cloud-init support
- ✅ Create ready-to-use template

### 2. Configure Environment

```bash
# Create .env file with XCP-ng credentials
cat > .env << EOF
XCP_HOST=your-xcpng-server.example.com
XCP_USERNAME=root
XCP_PASSWORD=your-password
EOF
```

### 3. Create Cloud VM

```python
#!/usr/bin/env python3
from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig
from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM

# Create cloud-init configuration
config = CloudInitConfig.create_bioxen_vm(
    hostname="my-bioxen-vm",
    ssh_keys=["ssh-rsa AAAAB3... your-key"]
)

# Configure VM
vm_config = {
    'xcp_host': 'your-xcpng-server.example.com',
    'xcp_username': 'root', 
    'xcp_password': 'your-password',
    'template_name': 'your-template-uuid',  # From setup script output
    'use_cloud_init': True,
    'cloud_init_config': config.to_base64()
}

# Create and start VM
vm = XCPngVM("my-vm", vm_config)
vm.start()

print(f"VM ready! SSH: ssh bioxen@{vm.vm_ip}")
```

## 📋 What You Get

### ✅ Fully Automated Setup
- **No manual console interaction** - Everything automated via cloud-init
- **SSH access ready** - Keys configured, passwordless login available
- **Lua environment installed** - lua5.4, luarocks, development tools
- **BioXen user created** - Ready workspace at `/home/bioxen/workspace`

### ⚡ Fast Deployment
- **~90 seconds** from VM creation to SSH access
- **Consistent configuration** - Identical setup every time
- **Template-based** - Clone from optimized cloud image
- **Pre-configured** - Guest tools, SSH, packages ready

### 🔧 Enterprise Features
- **Cloud-init standard** - Industry standard configuration management
- **Scalable** - Deploy hundreds of VMs identically
- **Version controlled** - Configuration as code
- **Secure** - SSH key authentication, configurable users

## 🧪 Test Scripts

### Complete Demo
```bash
# Full demonstration with all features
python3 demo_cloud_vm.py
```

### Simple VM Creation Test
```bash
# Basic cloud VM creation test
python3 test_cloud_vm_creation.py
```

### Template Setup Test
```bash
# Test if cloud template is working
python3 -c "
from pylua_bioxen_vm_lib.xapi_client import XAPIClient
import os
client = XAPIClient(os.getenv('XCP_HOST'), os.getenv('XCP_USERNAME'), os.getenv('XCP_PASSWORD'))
client.authenticate()
templates = client.list_templates()
for t in templates:
    if 'Cloud' in t.get('name-label', ''):
        print(f'✅ Found: {t[\"name-label\"]} ({t[\"uuid\"]})')
"
```

## 📚 Cloud-Init Configuration Examples

### Basic BioXen VM
```python
from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig

config = CloudInitConfig.create_bioxen_vm()
print(config.to_yaml())
```

### Custom Configuration
```python
config = CloudInitConfig()
config.add_user('developer', 'dev123', groups=['sudo'])
config.add_packages(['git', 'vim', 'htop'])
config.add_commands(['echo "Custom setup complete" > /tmp/status'])
config.set_hostname('dev-vm')

# Use in VM creation
vm_config['cloud_init_config'] = config.to_base64()
```

### SSH Key Integration
```python
# Read your public key
with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
    ssh_key = f.read().strip()

config = CloudInitConfig.create_bioxen_vm(
    hostname="secure-vm",
    ssh_keys=[ssh_key]
)
```

## 🔍 Troubleshooting

### Template Not Found
```bash
# List available templates
xe template-list name-description="*cloud*"

# Check template status
xe template-param-list uuid=<template-uuid>
```

### VM Not Getting IP
```bash
# Check VM guest metrics
xe vm-param-get uuid=<vm-uuid> param-name=guest-metrics
xe vm-guest-metrics-param-list uuid=<guest-metrics-uuid>

# Check VM network configuration
xe vm-param-get uuid=<vm-uuid> param-name=networks
```

### SSH Connection Failed
```bash
# Check if VM is accessible
ping <vm-ip>

# Check SSH service status (from VM console if needed)
systemctl status ssh

# Check cloud-init status
cloud-init status --long
```

### Cloud-Init Not Working
```bash
# Check cloud-init logs (from VM)
sudo tail -f /var/log/cloud-init-output.log
sudo cloud-init status --long

# Validate cloud-init config
sudo cloud-init schema --config-file /var/lib/cloud/instance/user-data.txt
```

## 🎯 Migration from Installer Templates

### Before (Manual Process)
1. Create VM from installer template
2. **Manual console interaction required** ❌
3. Install OS manually via VNC/console
4. Configure users, SSH, packages manually
5. Install Lua and dependencies manually
6. Configure environment manually

### After (Cloud Images)
1. Create VM from cloud template ✅
2. **Fully automated** - No manual steps ✅
3. OS boots ready with all packages ✅
4. Users and SSH configured automatically ✅
5. Lua and dependencies pre-installed ✅
6. Environment ready immediately ✅

## 🚀 Next Steps

1. **Set up cloud template** - Run `setup_cloud_template.py`
2. **Test basic VM creation** - Run `test_cloud_vm_creation.py`
3. **Try full demo** - Run `demo_cloud_vm.py`
4. **Integrate with your workflow** - Use in your automation scripts
5. **Scale up** - Create multiple VMs, networks, templates

## 📖 Additional Resources

- [Cloud-Init Documentation](https://cloudinit.readthedocs.io/)
- [XCP-ng XAPI Documentation](https://xapi-project.github.io/)
- [Debian Cloud Images](https://cloud.debian.org/images/cloud/)
- [SSH Key Setup Guide](https://www.ssh.com/academy/ssh/keygen)