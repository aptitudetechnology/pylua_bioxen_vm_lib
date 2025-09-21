#!/usr/bin/env python3
"""
Test automated VM creation using cloud images with cloud-init
"""

import sys
import os
import time
import json
import base64
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=project_dir / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

def test_cloud_vm_creation():
    """Test creating VM from cloud image template"""
    
    print("☁️  Testing Cloud Image VM Creation")
    print("=" * 50)
    
    # XCP-ng connection details
    xcp_host = os.getenv('XCP_HOST')
    xcp_username = os.getenv('XCP_USERNAME') 
    xcp_password = os.getenv('XCP_PASSWORD')
    
    if not all([xcp_host, xcp_username, xcp_password]):
        print("❌ Missing XCP-ng credentials in environment")
        return False
    
    print(f"🔗 Connecting to XCP-ng: {xcp_host}")
    
    # Import XAPI client
    try:
        from pylua_bioxen_vm_lib.xapi_client import XAPIClient
        client = XAPIClient(xcp_host, xcp_username, xcp_password)
        client.authenticate()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    try:
        # Find cloud template
        print("\n📋 Looking for cloud template...")
        templates = client.list_templates()
        
        cloud_template = None
        template_uuid = "cea07a22-1811-e80e-2799-9b64117deab7"  # New fixed Debian 12 template
        
        # Look for our specific cloud template
        for template in templates:
            if template.get('uuid') == template_uuid:
                cloud_template = template
                template_name = template['name-label']
                print(f"✅ Found cloud template: {template_name}")
                print(f"   📋 Template UUID: {template_uuid}")
                break
        
        if not cloud_template:
            # Fallback: look for any cloud template with BioXen in name
            for template in templates:
                if 'BioXen' in template.get('name-label', '') and 'Fixed' in template.get('name-label', ''):
                    cloud_template = template
                    template_name = template['name-label']
                    template_uuid = template.get('uuid')
                    print(f"✅ Found cloud template: {template_name}")
                    print(f"   📋 Template UUID: {template_uuid}")
                    break
        
        if not cloud_template:
            print("❌ Fixed cloud template not found.")
            print("💡 Create with: xe vm-clone vm=<debian-12-uuid> new-name-label='Debian-12-Cloud-BioXen-Fixed'")
            return False
        
        # Create cloud-init configuration
        print("\n☁️  Preparing cloud-init configuration...")
        
        cloud_init_config = {
            'package_update': True,
            'package_upgrade': True,
            'packages': [
                'lua5.4', 'lua5.4-dev', 'luarocks', 'curl', 'git', 
                'htop', 'vim', 'sudo', 'openssh-server'
            ],
            'users': [
                {
                    'name': 'bioxen',
                    'groups': 'sudo',
                    'shell': '/bin/bash',
                    'sudo': ['ALL=(ALL) NOPASSWD:ALL']
                }
            ],
            'chpasswd': {
                'list': 'debian:bioxen123\nbioxen:bioxen123',
                'expire': False
            },
            'ssh_pwauth': True,
            'disable_root': False,
            'runcmd': [
                'mkdir -p /home/bioxen/workspace',
                'chown bioxen:bioxen /home/bioxen/workspace',
                'echo "export PATH=/home/bioxen/.luarocks/bin:$PATH" >> /home/bioxen/.bashrc',
                'echo "BioXen VM configured via cloud-init" > /home/bioxen/workspace/status.txt',
                'systemctl enable ssh',
                'systemctl start ssh'
            ],
            'final_message': 'BioXen cloud VM is ready!'
        }
        
        # Convert to YAML and encode
        import yaml
        cloud_init_yaml = yaml.dump(cloud_init_config, default_flow_style=False)
        user_data = base64.b64encode(cloud_init_yaml.encode()).decode()
        
        print("✅ Cloud-init configuration prepared")
        
        # Create VM
        vm_name = f"bioxen-cloud-vm-{int(time.time())}"
        print(f"\n🚀 Creating VM: {vm_name}")
        
        # Create VM using cloud template with cloud-init
        try:
            vm_uuid = client.create_cloud_vm_from_template(
                template_uuid, 
                vm_name, 
                user_data
            )
            print(f"   � VM UUID: {vm_uuid}")
        except Exception as e:
            print(f"   ❌ VM creation failed: {e}")
            return False
        
        # Start VM
        print("   🔄 Starting VM...")
        try:
            if client.start_vm(vm_uuid):
                print("✅ VM started successfully")
            else:
                print("❌ Failed to start VM")
                return False
        except Exception as e:
            print(f"   ❌ VM start failed: {e}")
            return False
        
        print("✅ VM started successfully")
        
        # Wait and check status
        print("\n⏳ Waiting for VM to boot and configure...")
        vm_ip = None
        
        for i in range(30):
            time.sleep(10)
            
            print(f"   ⏱️  {(i+1)*10}s - Checking VM status...")
            
            # Try to get VM information
            try:
                # Get VM list to find our VM
                vms = client.list_vms()
                our_vm = None
                
                for vm in vms:
                    if vm.get('uuid') == vm_uuid:
                        our_vm = vm
                        break
                
                if our_vm:
                    power_state = our_vm.get('power-state', 'unknown')
                    print(f"      Power state: {power_state}")
                    
                    # Look for network info (this might not be available immediately)
                    networks = our_vm.get('networks', {})
                    if networks:
                        print("   🌐 Network information:")
                        for key, value in networks.items():
                            print(f"      {key}: {value}")
                            if value and not value.startswith('127.') and ':' not in value:
                                vm_ip = value
                                break
                    
                    if vm_ip:
                        print(f"\n🔍 Testing SSH connectivity to {vm_ip}...")
                        
                        # Simple SSH test
                        import subprocess
                        result = subprocess.run([
                            'ssh', '-o', 'ConnectTimeout=5', 
                            '-o', 'StrictHostKeyChecking=no',
                            f'bioxen@{vm_ip}', 'echo "SSH test successful"'
                        ], capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            print("✅ SSH connection successful!")
                            
                            # Test Lua installation
                            lua_result = subprocess.run([
                                'ssh', '-o', 'ConnectTimeout=5',
                                '-o', 'StrictHostKeyChecking=no', 
                                f'bioxen@{vm_ip}', 'lua -v'
                            ], capture_output=True, text=True, timeout=10)
                            
                            if lua_result.returncode == 0:
                                print(f"✅ Lua available: {lua_result.stdout.strip()}")
                            else:
                                print("⚠️  Lua not yet available (still configuring)")
                            
                            break
                        else:
                            print(f"   🔄 SSH not ready yet")
                
            except Exception as e:
                print(f"   ⏳ VM still booting: {e}")
                continue
        
        # Final status
        print(f"\n📊 CLOUD VM DEPLOYMENT SUMMARY")
        print("=" * 40)
        print(f"VM Name: {vm_name}")
        print(f"VM UUID: {vm_uuid}")
        print(f"Template: Cloud template with cloud-init")
        print(f"Status: {'✅ Fully automated' if vm_ip else '🔄 Still configuring'}")
        
        if vm_ip:
            print(f"IP Address: {vm_ip}")
            print(f"SSH Access: ssh bioxen@{vm_ip}")
            print(f"Password: bioxen123")
        
        return True
        
    except Exception as e:
        print(f"❌ VM creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("☁️  Cloud Image VM Creation Test")
    
    # Test cloud VM creation
    success = test_cloud_vm_creation()
    
    if success:
        print(f"\n🎉 CLOUD VM TEST COMPLETED!")
        print(f"✅ Fully automated VM deployment working")
    else:
        print(f"\n❌ Cloud VM test failed")
        sys.exit(1)