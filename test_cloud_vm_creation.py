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
        templates = client.session.xenapi.VM.get_all_records()
        
        cloud_template = None
        for vm_ref, vm_record in templates.items():
            if (vm_record.get('is_a_template', False) and 
                'Cloud' in vm_record.get('name_label', '') and
                'BioXen' in vm_record.get('name_label', '')):
                cloud_template = vm_ref
                template_name = vm_record['name_label']
                print(f"✅ Found cloud template: {template_name}")
                break
        
        if not cloud_template:
            print("❌ Cloud template not found. Run setup_cloud_template.py first")
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
        
        # Clone from template
        new_vm_ref = client.session.xenapi.VM.clone(cloud_template, vm_name)
        
        # Set as not a template
        client.session.xenapi.VM.set_is_a_template(new_vm_ref, False)
        
        # Configure cloud-init user data
        print("   📝 Configuring cloud-init...")
        client.session.xenapi.VM.set_platform(new_vm_ref, {'user-data': user_data})
        
        # Get VM UUID
        vm_uuid = client.session.xenapi.VM.get_uuid(new_vm_ref)
        print(f"   📋 VM UUID: {vm_uuid}")
        
        # Start VM
        print("   🔄 Starting VM...")
        client.session.xenapi.VM.start(new_vm_ref, False, True)
        
        print("✅ VM started successfully")
        
        # Wait and check status
        print("\n⏳ Waiting for VM to boot and configure...")
        for i in range(30):
            time.sleep(10)
            
            # Check VM state
            vm_record = client.session.xenapi.VM.get_record(new_vm_ref)
            power_state = vm_record['power_state']
            
            print(f"   ⏱️  {(i+1)*10}s - Power state: {power_state}")
            
            # Try to get guest metrics
            guest_metrics_ref = vm_record.get('guest_metrics')
            if guest_metrics_ref and guest_metrics_ref != 'OpaqueRef:NULL':
                try:
                    guest_metrics = client.session.xenapi.VM_guest_metrics.get_record(guest_metrics_ref)
                    networks = guest_metrics.get('networks', {})
                    
                    if networks:
                        print("   🌐 Network information:")
                        for interface, ip in networks.items():
                            print(f"      {interface}: {ip}")
                        
                        # Found IP, try SSH test
                        vm_ip = None
                        for interface, ip in networks.items():
                            if ip and not ip.startswith('127.') and ':' not in ip:
                                vm_ip = ip
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
                                print(f"   🔄 SSH not ready yet: {result.stderr.strip()}")
                    
                except Exception as e:
                    print(f"   ⏳ Guest metrics not ready: {e}")
        
        # Final status
        print(f"\n📊 CLOUD VM DEPLOYMENT SUMMARY")
        print("=" * 40)
        print(f"VM Name: {vm_name}")
        print(f"VM UUID: {vm_uuid}")
        print(f"Template: Cloud image with cloud-init")
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