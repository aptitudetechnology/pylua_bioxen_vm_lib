#!/usr/bin/env python3
"""
Cloud Image Template Setup for XCP-ng
Downloads and imports Debian cloud images for automated VM deployment
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

def setup_cloud_template():
    """Download and import Debian cloud image to XCP-ng"""
    
    print("☁️  Setting up Debian Cloud Image Template")
    print("=" * 60)
    print("CLOUD IMAGE AUTOMATED SETUP")
    print("=" * 60)
    
    # Cloud image details
    cloud_image_url = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2"
    cloud_image_file = "debian-12-generic-amd64.qcow2"
    template_name = "Debian-12-Cloud-BioXen"
    
    try:
        print("📥 Downloading Debian 12 cloud image...")
        print(f"   URL: {cloud_image_url}")
        
        # Check if already downloaded
        if os.path.exists(cloud_image_file):
            print(f"   ✅ Cloud image already exists: {cloud_image_file}")
        else:
            print("   ⬇️  Downloading... (this may take a few minutes)")
            result = subprocess.run([
                "wget", "-O", cloud_image_file, cloud_image_url
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Download completed")
            else:
                print(f"   ❌ Download failed: {result.stderr}")
                return False
        
        # Get file size
        file_size = os.path.getsize(cloud_image_file) / (1024 * 1024)
        print(f"   📊 Image size: {file_size:.1f} MB")
        
        print(f"\n📦 Importing cloud image to XCP-ng...")
        print(f"   Template name: {template_name}")
        
        # Import to XCP-ng
        import_cmd = [
            "xe", "vm-import", 
            f"filename={cloud_image_file}",
            f"vm-name={template_name}"
        ]
        
        print(f"   Running: {' '.join(import_cmd)}")
        result = subprocess.run(import_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Import completed successfully")
            
            # Get the UUID of the imported VM
            vm_uuid = result.stdout.strip()
            print(f"   📋 VM UUID: {vm_uuid}")
            
            # Configure as template
            print("   🔧 Configuring as template...")
            
            # Set as template
            subprocess.run([
                "xe", "vm-set-is-a-template", 
                f"uuid={vm_uuid}", 
                "is-a-template=true"
            ])
            
            # Set description
            subprocess.run([
                "xe", "template-param-set", 
                f"uuid={vm_uuid}", 
                "name-description=Debian 12 cloud image with cloud-init support"
            ])
            
            print("   ✅ Template configuration completed")
            
            # Show template info
            print(f"\n📋 Template Information:")
            result = subprocess.run([
                "xe", "template-param-list", f"uuid={vm_uuid}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if any(param in line for param in ['name-label', 'uuid', 'name-description']):
                        print(f"   {line.strip()}")
            
            return vm_uuid
            
        else:
            print(f"   ❌ Import failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Cloud image setup failed: {e}")
        return False

def create_cloud_init_config():
    """Create cloud-init configuration for BioXen VMs"""
    
    print(f"\n☁️  Creating Cloud-Init Configuration")
    print("=" * 40)
    
    # Cloud-init user data for BioXen setup
    cloud_init_config = """#cloud-config
# BioXen VM Cloud-Init Configuration

# System update and package installation
package_update: true
package_upgrade: true

packages:
  - lua5.4
  - lua5.4-dev
  - luarocks
  - curl
  - git
  - htop
  - vim
  - sudo
  - openssh-server

# Create BioXen user
users:
  - name: bioxen
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh_authorized_keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... # Add your SSH public key here

# Default user (debian) configuration
chpasswd:
  list: |
    debian:bioxen123
    bioxen:bioxen123
  expire: False

# SSH configuration
ssh_pwauth: true
disable_root: false

# Create BioXen workspace
runcmd:
  - mkdir -p /home/bioxen/workspace
  - chown bioxen:bioxen /home/bioxen/workspace
  - echo 'export PATH=/home/bioxen/.luarocks/bin:$PATH' >> /home/bioxen/.bashrc
  - echo 'export LUA_PATH="/home/bioxen/.luarocks/share/lua/5.4/?.lua;/home/bioxen/.luarocks/share/lua/5.4/?/init.lua;;"' >> /home/bioxen/.bashrc
  - echo 'BioXen VM configured successfully' > /home/bioxen/workspace/status.txt
  - systemctl enable ssh
  - systemctl start ssh

# Final message
final_message: "BioXen cloud VM is ready! SSH: ssh bioxen@$HOSTNAME"
"""
    
    # Save cloud-init config
    config_file = "bioxen-cloud-init.yaml"
    with open(config_file, 'w') as f:
        f.write(cloud_init_config)
    
    print(f"   ✅ Cloud-init config saved: {config_file}")
    print(f"   📝 Edit this file to customize VM configuration")
    print(f"   🔑 Add your SSH public key to the config")
    
    return config_file

def show_usage_instructions(template_uuid):
    """Show how to use the cloud template"""
    
    print(f"\n🚀 USAGE INSTRUCTIONS")
    print("=" * 40)
    
    print(f"""
✅ Cloud template is ready! Here's how to use it:

📋 Template Details:
   Name: Debian-12-Cloud-BioXen
   UUID: {template_uuid}
   Features: Cloud-init, Guest tools, Pre-installed Lua

🔧 Create VM with cloud-init:
   xe vm-install template="{template_uuid}" new-name-label="my-bioxen-vm"
   
🔑 Inject SSH keys (recommended):
   xe vm-param-set uuid=<new-vm-uuid> platform:user-data="$(cat bioxen-cloud-init.yaml | base64 -w 0)"

🚀 Start VM:
   xe vm-start uuid=<new-vm-uuid>

🌐 Access VM:
   - VM will get IP automatically via DHCP
   - SSH: ssh bioxen@<vm-ip>
   - Default password: bioxen123

📝 Python Integration:
   Update your automation scripts to use template UUID: {template_uuid}
""")

if __name__ == "__main__":
    print("☁️  Debian Cloud Image Setup for XCP-ng")
    
    # Setup cloud template
    template_uuid = setup_cloud_template()
    
    if template_uuid:
        # Create cloud-init config
        config_file = create_cloud_init_config()
        
        # Show usage instructions
        show_usage_instructions(template_uuid)
        
        print(f"\n🎉 CLOUD TEMPLATE SETUP COMPLETED!")
        print(f"✅ Ready for automated VM deployment")
    else:
        print(f"\n❌ Cloud template setup failed")
        sys.exit(1)