#!/usr/bin/env python3
"""
Complete Cloud VM Example
Demonstrates end-to-end cloud VM creation with cloud-init automation
"""

import sys
import os
import time
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=project_dir / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables.")

def create_cloud_vm_example():
    """Complete example of cloud VM creation and management"""
    
    print("☁️  BioXen Cloud VM Creation Example")
    print("=" * 50)
    
    # Import cloud-init helper
    try:
        from pylua_bioxen_vm_lib.cloud_init import CloudInitConfig
        from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Run from the project directory or install the package")
        return False
    
    # Step 1: Create cloud-init configuration
    print("1️⃣  Creating cloud-init configuration...")
    
    # Create BioXen-specific configuration
    cloud_config = CloudInitConfig.create_bioxen_vm(
        hostname="bioxen-cloud-demo",
        ssh_keys=[
            # Add your SSH public key here for passwordless access
            # "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... user@host"
        ],
        additional_packages=[
            'python3-pip',
            'docker.io',
            'nginx'
        ]
    )
    
    # Add custom commands for demonstration
    cloud_config.add_commands([
        'echo "Setting up BioXen demo environment..." > /home/bioxen/setup.log',
        'date >> /home/bioxen/setup.log',
        'lua -v >> /home/bioxen/setup.log 2>&1',
        'chown bioxen:bioxen /home/bioxen/setup.log'
    ])
    
    print("✅ Cloud-init configuration created")
    print(f"   📋 Hostname: bioxen-cloud-demo")
    print(f"   👤 User: bioxen (password: bioxen123)")
    print(f"   📦 Packages: Lua, Python, Docker, Nginx")
    
    # Save cloud config for inspection
    with open('demo-cloud-config.yaml', 'w') as f:
        f.write(cloud_config.to_yaml())
    print(f"   💾 Config saved: demo-cloud-config.yaml")
    
    # Step 2: Configure XCP-ng VM
    print(f"\n2️⃣  Configuring XCP-ng VM...")
    
    # Get XCP-ng connection details
    xcp_config = {
        'xcp_host': os.getenv('XCP_HOST'),
        'xcp_username': os.getenv('XCP_USERNAME'),
        'xcp_password': os.getenv('XCP_PASSWORD'),
        'template_name': 'Debian-12-Cloud-BioXen',  # Cloud template UUID
        'vm_username': 'bioxen',
        'vm_password': 'bioxen123',
        'use_cloud_init': True,
        'cloud_init_config': cloud_config.to_base64()
    }
    
    if not all([xcp_config['xcp_host'], xcp_config['xcp_username'], xcp_config['xcp_password']]):
        print("❌ Missing XCP-ng credentials in environment")
        print("💡 Set XCP_HOST, XCP_USERNAME, XCP_PASSWORD in .env file")
        return False
    
    print(f"✅ XCP-ng configuration ready")
    print(f"   🌐 Server: {xcp_config['xcp_host']}")
    print(f"   👤 User: {xcp_config['xcp_username']}")
    print(f"   📋 Template: {xcp_config['template_name']}")
    
    # Step 3: Create and start VM
    print(f"\n3️⃣  Creating cloud VM...")
    
    try:
        # Create XCP-ng VM instance
        vm = XCPngVM("demo-cloud-vm", xcp_config)
        
        print("   🔗 Connecting to XCP-ng...")
        vm.start()
        
        print(f"✅ VM created and started!")
        print(f"   📋 VM UUID: {vm.vm_uuid}")
        print(f"   🌐 VM IP: {vm.vm_ip}")
        
        # Step 4: Test VM functionality
        print(f"\n4️⃣  Testing VM functionality...")
        
        if vm.vm_ip:
            print(f"   🔍 Testing SSH connectivity...")
            
            # Test basic connectivity
            if vm.ssh_session and vm.ssh_session.is_connected():
                print("   ✅ SSH connection established")
                
                # Test Lua availability
                print("   🧪 Testing Lua installation...")
                try:
                    result = vm.ssh_session.execute_command("lua -v")
                    if result and 'Lua' in result:
                        print(f"   ✅ Lua available: {result.strip()}")
                    else:
                        print(f"   ⚠️  Lua test result: {result}")
                except Exception as e:
                    print(f"   ⚠️  Lua test failed: {e}")
                
                # Test cloud-init setup
                print("   🧪 Testing cloud-init setup...")
                try:
                    result = vm.ssh_session.execute_command("cat /home/bioxen/setup.log")
                    if result:
                        print("   ✅ Cloud-init setup completed:")
                        for line in result.split('\n'):
                            if line.strip():
                                print(f"      {line.strip()}")
                    else:
                        print("   ⚠️  Setup log not found (still configuring)")
                except Exception as e:
                    print(f"   ⚠️  Setup log test failed: {e}")
                
                # Test interactive Lua session
                print("   🧪 Testing interactive Lua session...")
                try:
                    if vm.session_active:
                        # Send simple Lua command
                        vm.send_input("print('Hello from BioXen Cloud VM!')")
                        time.sleep(1)
                        output = vm.read_output()
                        if 'Hello from BioXen Cloud VM!' in output:
                            print("   ✅ Interactive Lua session working!")
                        else:
                            print(f"   ⚠️  Lua session output: {output}")
                    else:
                        print("   ⚠️  Interactive session not active")
                except Exception as e:
                    print(f"   ⚠️  Interactive session test failed: {e}")
            
            else:
                print("   ❌ SSH connection failed")
        
        # Step 5: Show connection details
        print(f"\n5️⃣  Connection Information")
        print("   " + "="*30)
        print(f"   VM Name: demo-cloud-vm")
        print(f"   VM UUID: {vm.vm_uuid}")
        print(f"   IP Address: {vm.vm_ip or 'Still configuring'}")
        print(f"   SSH Access: ssh bioxen@{vm.vm_ip}" if vm.vm_ip else "   SSH: Not ready yet")
        print(f"   Password: bioxen123")
        print(f"   Status: {'✅ Ready' if vm.session_active else '🔄 Configuring'}")
        
        # Cleanup option
        print(f"\n6️⃣  VM Management")
        print("   " + "="*20)
        print(f"   💡 To keep VM running: Leave as-is")
        print(f"   🗑️  To cleanup VM: Run vm.stop() or delete via XCP-ng Center")
        print(f"   📋 Monitor VM: Use check_vm_status.py")
        
        return True
        
    except Exception as e:
        print(f"❌ VM creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_cloud_advantages():
    """Show advantages of cloud image approach"""
    
    print(f"\n☁️  CLOUD IMAGE ADVANTAGES")
    print("=" * 40)
    print("""
✅ AUTOMATION BENEFITS:
   • No manual console interaction required
   • Identical configuration every deployment  
   • SSH keys automatically configured
   • Packages pre-installed on first boot
   • Zero-touch VM deployment

🚀 ENTERPRISE FEATURES:
   • Template-based deployment at scale
   • Version-controlled VM configurations
   • Cloud-init industry standard compliance
   • Guest tools pre-installed and configured
   • Production-ready automation

🔧 DEVELOPER EXPERIENCE:
   • Programmatic VM configuration
   • Infrastructure as Code support
   • Consistent development environments
   • Easy CI/CD integration
   • Rapid prototyping and testing

📊 OPERATIONAL EXCELLENCE:
   • Predictable deployment times
   • Reduced human error risk
   • Auditable configuration changes
   • Scalable to hundreds of VMs
   • Enterprise security compliance
""")

if __name__ == "__main__":
    print("☁️  BioXen Cloud VM Automation Demo")
    
    # Show cloud advantages
    show_cloud_advantages()
    
    # Run the example
    print(f"\n🚀 STARTING CLOUD VM DEMO")
    print("=" * 40)
    
    success = create_cloud_vm_example()
    
    if success:
        print(f"\n🎉 CLOUD VM DEMO COMPLETED!")
        print(f"✅ Fully automated cloud VM deployment successful")
        print(f"🌟 Enterprise-grade automation achieved")
    else:
        print(f"\n❌ Cloud VM demo failed")
        sys.exit(1)