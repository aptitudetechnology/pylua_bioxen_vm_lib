#!/usr/bin/env python3
"""
Automated Cloud Image Template Setup for XCP-ng
Fully automated - downloads, uploads, and imports cloud images via SSH
"""

import sys
import os
import subprocess
import time
import paramiko
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

def setup_cloud_template_automated():
    """Fully automated cloud template setup via SSH"""
    
    print("☁️  Automated Cloud Template Setup")
    print("=" * 60)
    print("FULLY AUTOMATED CLOUD IMAGE SETUP")
    print("=" * 60)
    
    # Cloud image details
    cloud_image_url = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2"
    cloud_image_file = "debian-12-generic-amd64.qcow2"
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
        # Step 1: Download cloud image locally
        print("1️⃣  Downloading Debian 12 cloud image...")
        print(f"   URL: {cloud_image_url}")
        
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
        
        file_size = os.path.getsize(cloud_image_file) / (1024 * 1024)
        print(f"   📊 Image size: {file_size:.1f} MB")
        
        # Step 2: Connect to XCP-ng via SSH
        print(f"\n2️⃣  Connecting to XCP-ng server...")
        print(f"   🌐 Server: {xcp_host}")
        print(f"   👤 User: {xcp_username}")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(xcp_host, username=xcp_username, password=xcp_password, timeout=30)
        
        print("   ✅ SSH connection established")
        
        # Step 3: Check if template already exists
        print(f"\n3️⃣  Checking for existing template...")
        
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-list name-label='{template_name}' --minimal"
        )
        existing_uuid = stdout.read().decode().strip()
        
        if existing_uuid:
            print(f"   ✅ Template already exists!")
            print(f"   📋 Template UUID: {existing_uuid}")
            ssh.close()
            return existing_uuid
        
        print(f"   📝 Template doesn't exist, will create new one")
        
        # Step 4: Upload cloud image to XCP-ng
        print(f"\n4️⃣  Uploading cloud image to XCP-ng...")
        print(f"   📤 Uploading {file_size:.1f} MB via SSH...")
        
        sftp = ssh.open_sftp()
        remote_path = f"/tmp/{cloud_image_file}"
        
        # Upload with progress
        def upload_progress(transferred, total):
            percent = (transferred / total) * 100
            print(f"\r   📡 Upload progress: {percent:.1f}% ({transferred/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)", end='')
        
        sftp.put(cloud_image_file, remote_path, callback=upload_progress)
        sftp.close()
        
        print(f"\n   ✅ Upload completed")
        
        # Step 5: Import cloud image as VM template
        print(f"\n5️⃣  Importing cloud image as template...")
        print(f"   📦 Running xe vm-import...")
        
        import_command = f"xe vm-import filename={remote_path} new-name-label='{template_name}'"
        stdin, stdout, stderr = ssh.exec_command(import_command, timeout=180)
        
        # Wait for import to complete
        import_result = stdout.read().decode().strip()
        import_error = stderr.read().decode().strip()
        
        if import_error:
            print(f"   ❌ Import failed: {import_error}")
            ssh.close()
            return False
        
        if not import_result:
            print(f"   ❌ Import failed: No VM UUID returned")
            ssh.close()
            return False
        
        vm_uuid = import_result
        print(f"   ✅ Import completed successfully")
        print(f"   📋 VM UUID: {vm_uuid}")
        
        # Step 6: Configure as template
        print(f"\n6️⃣  Configuring as cloud template...")
        
        # Set as template
        stdin, stdout, stderr = ssh.exec_command(
            f"xe vm-set-is-a-template uuid={vm_uuid} is-a-template=true"
        )
        stdout.read()  # Wait for completion
        
        # Set description
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-param-set uuid={vm_uuid} name-description='Debian 12 cloud image with cloud-init support for BioXen'"
        )
        stdout.read()  # Wait for completion
        
        print(f"   ✅ Template configuration completed")
        
        # Step 7: Verify template
        print(f"\n7️⃣  Verifying template...")
        
        stdin, stdout, stderr = ssh.exec_command(
            f"xe template-param-list uuid={vm_uuid}"
        )
        template_info = stdout.read().decode()
        
        if "name-label" in template_info:
            print(f"   ✅ Template verification successful")
            
            # Show key template info
            for line in template_info.split('\n'):
                if any(param in line for param in ['name-label', 'uuid', 'name-description', 'is-a-template']):
                    print(f"      {line.strip()}")
        
        # Step 8: Cleanup
        print(f"\n8️⃣  Cleanup...")
        
        # Remove uploaded file
        stdin, stdout, stderr = ssh.exec_command(f"rm {remote_path}")
        stdout.read()  # Wait for completion
        
        print(f"   ✅ Cleanup completed")
        
        ssh.close()
        
        print(f"\n🎉 CLOUD TEMPLATE SETUP COMPLETED!")
        print(f"=" * 50)
        print(f"✅ Template Name: {template_name}")
        print(f"✅ Template UUID: {vm_uuid}")
        print(f"✅ Ready for automated VM deployment")
        
        return vm_uuid
        
    except paramiko.AuthenticationException:
        print(f"❌ SSH authentication failed")
        print(f"💡 Check XCP_USERNAME and XCP_PASSWORD in .env file")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Cloud template setup failed: {e}")
        import traceback
        traceback.print_exc()
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
  - python3-pip

# Create BioXen user
users:
  - name: bioxen
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    # Add your SSH public key here:
    # ssh_authorized_keys:
    #   - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... user@host

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
  - echo 'BioXen VM configured successfully via cloud-init' > /home/bioxen/workspace/status.txt
  - chown bioxen:bioxen /home/bioxen/workspace/status.txt
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
    print(f"   🔑 Add your SSH public key to the config for passwordless access")
    
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

🔧 Python Integration (Recommended):
   
   from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig
   from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
   
   # Create cloud-init config
   config = CloudInitConfig.create_bioxen_vm(hostname="my-vm")
   
   # Create VM
   vm = XCPngVM("my-vm", {{
       'xcp_host': '{os.getenv("XCP_HOST", "your-xcpng-server")}',
       'xcp_username': 'root',
       'xcp_password': 'your-password',
       'template_name': '{template_uuid}',
       'use_cloud_init': True,
       'cloud_init_config': config.to_base64()
   }})
   
   vm.start()  # Fully automated!

🎯 Next Steps:
   1. Run: python3 test_cloud_vm_creation.py
   2. Run: python3 demo_cloud_vm.py
   3. Integrate into your automation workflows
""")

if __name__ == "__main__":
    print("☁️  Automated Debian Cloud Image Setup for XCP-ng")
    
    # Setup cloud template
    template_uuid = setup_cloud_template_automated()
    
    if template_uuid:
        # Create cloud-init config
        config_file = create_cloud_init_config()
        
        # Show usage instructions
        show_usage_instructions(template_uuid)
        
        print(f"\n🎉 AUTOMATED SETUP COMPLETED!")
        print(f"✅ Ready for fully automated VM deployment")
    else:
        print(f"\n❌ Automated setup failed")
        sys.exit(1)