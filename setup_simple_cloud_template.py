#!/usr/bin/env python3
"""
Simple Cloud Template Setup for XCP-ng
Uses existing XCP-ng templates and makes them cloud-init ready
"""

import sys
import os
import paramiko
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

def setup_simple_cloud_template():
    """Setup cloud template using existing XCP-ng templates"""
    
    print("☁️  Simple Cloud Template Setup")
    print("=" * 50)
    print("CLOUD-INIT READY TEMPLATE CREATION")
    print("=" * 50)
    
    template_name = "Debian-12-Cloud-BioXen"
    
    # Get XCP-ng credentials
    xcp_host = os.getenv('XCP_HOST')
    xcp_username = os.getenv('XCP_USERNAME')
    xcp_password = os.getenv('XCP_PASSWORD')
    
    if not all([xcp_host, xcp_username, xcp_password]):
        print("❌ Missing XCP-ng credentials")
        print("💡 Set XCP_HOST, XCP_USERNAME, XCP_PASSWORD in .env file")
        return False
    
    try:
        # Step 1: Connect to XCP-ng
        print(f"1️⃣  Connecting to XCP-ng server...")
        print(f"   🌐 Server: {xcp_host}")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(xcp_host, username=xcp_username, password=xcp_password, timeout=30)
        
        print("   ✅ SSH connection established")
        
        # Step 2: Check for existing cloud template
        print(f"\n2️⃣  Checking for existing cloud template...")
        
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-list name-label='{template_name}' --minimal"
        )
        existing_uuid = stdout.read().decode().strip()
        
        if existing_uuid:
            print(f"   ✅ Cloud template already exists!")
            print(f"   📋 Template UUID: {existing_uuid}")
            ssh.close()
            return existing_uuid
        
        # Step 3: Find suitable base template
        print(f"\n3️⃣  Finding suitable base template...")
        
        # Look for Debian Bookworm template
        stdin, stdout, stderr = ssh.exec_command(
            "xe template-list | grep -A5 -B5 -i 'debian.*12\\|bookworm'"
        )
        debian_output = stdout.read().decode()
        
        if not debian_output:
            # Look for any Debian template
            stdin, stdout, stderr = ssh.exec_command(
                "xe template-list | grep -A5 -B5 -i debian"
            )
            debian_output = stdout.read().decode()
        
        # Extract template UUID
        import re
        uuid_matches = re.findall(r'uuid \( RO\)\s*:\s*([a-f0-9-]+)', debian_output)
        name_matches = re.findall(r'name-label \( RW\)\s*:\s*([^\n]+)', debian_output)
        
        if not uuid_matches:
            print(f"   ❌ No Debian templates found")
            print(f"   📋 Available templates:")
            stdin, stdout, stderr = ssh.exec_command("xe template-list --minimal")
            all_templates = stdout.read().decode()
            print(f"   {all_templates}")
            ssh.close()
            return False
        
        base_template_uuid = uuid_matches[0]
        base_template_name = name_matches[0] if name_matches else "Unknown"
        
        print(f"   ✅ Found base template: {base_template_name}")
        print(f"   📋 Template UUID: {base_template_uuid}")
        
        # Step 4: Clone template for cloud use
        print(f"\n4️⃣  Creating cloud template...")
        
        stdin, stdout, stderr = ssh.exec_command(
            f"xe vm-clone vm={base_template_uuid} new-name-label='{template_name}'"
        )
        
        new_uuid = stdout.read().decode().strip()
        clone_error = stderr.read().decode().strip()
        
        if clone_error or not new_uuid:
            print(f"   ❌ Template clone failed: {clone_error}")
            ssh.close()
            return False
        
        print(f"   ✅ Template cloned successfully")
        print(f"   📋 New template UUID: {new_uuid}")
        
        # Step 5: Configure as cloud-init ready template
        print(f"\n5️⃣  Configuring cloud-init support...")
        
        # Set as template
        stdin, stdout, stderr = ssh.exec_command(
            f"xe vm-set-is-a-template uuid={new_uuid} is-a-template=true"
        )
        stdout.read()  # Wait for completion
        
        # Set cloud-init description
        description = "Debian 12 cloud-init ready template for BioXen VMs with automated package installation"
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-param-set uuid={new_uuid} name-description='{description}'"
        )
        stdout.read()  # Wait for completion
        
        # Add platform parameters for cloud-init support
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-param-set uuid={new_uuid} platform:device_id=0002"
        )
        stdout.read()  # Wait for completion
        
        print(f"   ✅ Cloud-init configuration completed")
        
        # Step 6: Verify template
        print(f"\n6️⃣  Verifying cloud template...")
        
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-param-list uuid={new_uuid}"
        )
        template_info = stdout.read().decode()
        
        # Show key information
        print(f"   📋 Template Details:")
        for line in template_info.split('\n'):
            if any(param in line for param in ['name-label', 'name-description', 'is-a-template']):
                print(f"      {line.strip()}")
        
        ssh.close()
        
        print(f"\n🎉 CLOUD TEMPLATE SETUP COMPLETED!")
        print(f"=" * 50)
        print(f"✅ Template Name: {template_name}")
        print(f"✅ Template UUID: {new_uuid}")
        print(f"✅ Cloud-init ready: Yes")
        print(f"✅ Base template: {base_template_name}")
        
        return new_uuid
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_cloud_init_config():
    """Create a sample cloud-init configuration"""
    
    print(f"\n☁️  Creating sample cloud-init configuration...")
    
    cloud_config = """#cloud-config
# BioXen Cloud-Init Configuration
# This will be injected into VMs created from the cloud template

# Update packages on first boot
package_update: true
package_upgrade: true

# Install required packages
packages:
  - lua5.4
  - lua5.4-dev
  - luarocks
  - curl
  - git
  - vim
  - htop
  - sudo
  - openssh-server

# Create bioxen user
users:
  - name: bioxen
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    # Add your SSH public key here for passwordless access:
    # ssh_authorized_keys:
    #   - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... your-key

# Set passwords (change these!)
chpasswd:
  list: |
    debian:bioxen123
    bioxen:bioxen123
  expire: False

# Enable SSH
ssh_pwauth: true
disable_root: false

# Setup BioXen environment
runcmd:
  - mkdir -p /home/bioxen/workspace
  - chown bioxen:bioxen /home/bioxen/workspace
  - echo 'export PATH=/home/bioxen/.luarocks/bin:$PATH' >> /home/bioxen/.bashrc
  - echo 'export LUA_PATH="/home/bioxen/.luarocks/share/lua/5.4/?.lua;;"' >> /home/bioxen/.bashrc
  - echo 'BioXen VM ready!' > /home/bioxen/workspace/status.txt
  - chown bioxen:bioxen /home/bioxen/workspace/status.txt
  - systemctl enable ssh
  - systemctl start ssh

# Final message
final_message: "BioXen VM is ready! SSH: ssh bioxen@$HOSTNAME"
"""
    
    config_file = "sample-cloud-init.yaml"
    with open(config_file, 'w') as f:
        f.write(cloud_config)
    
    print(f"   ✅ Sample config saved: {config_file}")
    print(f"   📝 Edit this file to customize your VM setup")
    
    return config_file

def show_usage_instructions(template_uuid):
    """Show how to use the cloud template"""
    
    print(f"\n🚀 USAGE INSTRUCTIONS")
    print("=" * 40)
    
    print(f"""
🎯 Your cloud template is ready! Here's how to use it:

📋 Template Details:
   Name: Debian-12-Cloud-BioXen
   UUID: {template_uuid}
   Type: Cloud-init ready Debian 12

🔧 Create VM with Python:
   
   from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig
   from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
   
   # Create cloud configuration
   config = CloudInitConfig.create_bioxen_vm(hostname="my-vm")
   
   # Create VM
   vm = XCPngVM("test-vm", {{
       'xcp_host': '{os.getenv("XCP_HOST", "your-server")}',
       'xcp_username': 'root',
       'xcp_password': 'your-password',
       'template_name': '{template_uuid}',
       'use_cloud_init': True,
       'cloud_init_config': config.to_base64()
   }})
   
   vm.start()  # Automated VM with Lua ready!

🚀 Test Scripts:
   1. python3 test_cloud_vm_creation.py
   2. python3 demo_cloud_vm.py

💡 Next Steps:
   1. Edit sample-cloud-init.yaml with your SSH keys
   2. Test VM creation with the scripts above
   3. Integrate into your automation workflows
""")

if __name__ == "__main__":
    print("☁️  Simple Cloud Template Setup for XCP-ng")
    
    # Setup cloud template
    template_uuid = setup_simple_cloud_template()
    
    if template_uuid:
        # Create sample config
        config_file = create_cloud_init_config()
        
        # Show usage instructions
        show_usage_instructions(template_uuid)
        
        print(f"\n🎉 SETUP COMPLETED!")
        print(f"✅ Cloud template ready for automated VM deployment")
    else:
        print(f"\n❌ Setup failed")
        sys.exit(1)