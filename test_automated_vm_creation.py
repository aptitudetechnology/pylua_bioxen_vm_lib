#!/usr/bin/env python3
"""
Automated VM Creation Example
Demonstrates how to create fully configured VMs without manual console interaction
"""

import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path
sys.path.insert(0, str(Path(__file__).parent / 'pylua_bioxen_vm_lib'))

def test_automated_vm_creation():
    """Test automated VM creation and configuration"""
    
    print("🚀 Testing Automated VM Creation")
    print("=" * 60)
    print("CREATING FULLY CONFIGURED VM WITHOUT MANUAL INTERVENTION")
    print("=" * 60)
    
    try:
        from xapi_client import XAPIClient
        from vm_configurator import BioXenVMFactory
        
        # Configuration
        host = os.getenv("XCP_HOST")
        username = os.getenv("XCP_USERNAME")
        password = os.getenv("XCP_PASSWORD", "")
        
        print(f"📡 Connecting to: {host}")
        
        # Create XAPI client
        xapi_client = XAPIClient(host=host, username=username, password=password)
        
        # Authenticate
        if not xapi_client.authenticate():
            print("❌ Failed to authenticate")
            return False
            
        print("✅ Authentication successful")
        
        # Create VM factory
        vm_factory = BioXenVMFactory(xapi_client)
        
        # VM configuration for automated setup
        vm_config = {
            'username': 'bioxen',
            'password': 'secure123',
            'hostname': 'bioxen-auto',
            'domain': 'bioxen.local',
            'vm_id': 'auto-configured-vm',
            'ssh_keys': [
                # Add your SSH public key here for passwordless access
                # 'ssh-rsa AAAAB3NzaC1yc2E...'
            ]
        }
        
        print("🏗️  Creating automated VM...")
        print("   This VM will be fully configured without manual intervention:")
        print("   ✅ User account created")
        print("   ✅ SSH access configured") 
        print("   ✅ Lua environment installed")
        print("   ✅ Required packages installed")
        print("   ✅ BioXen services configured")
        
        # Create fully configured VM
        vm_uuid = vm_factory.create_bioxen_vm(
            vm_name="bioxen-automated-test",
            template_name="Debian Bookworm 12",
            vm_config=vm_config
        )
        
        print(f"✅ Automated VM created successfully!")
        print(f"📋 VM UUID: {vm_uuid}")
        print(f"🔑 SSH Access: ssh bioxen@<vm-ip>")
        print(f"🐚 Default Password: secure123")
        
        return True
        
    except Exception as e:
        print(f"❌ Automated VM creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_configuration_methods():
    """Show different automated configuration methods"""
    
    print("\n" + "=" * 60)
    print("AUTOMATED CONFIGURATION METHODS")
    print("=" * 60)
    
    methods = [
        {
            'name': 'Cloud-Init (Recommended)',
            'description': 'Uses cloud-init for automated configuration',
            'pros': ['Industry standard', 'Very reliable', 'Extensive configuration options'],
            'cons': ['Requires cloud-init enabled templates'],
            'use_case': 'Production environments'
        },
        {
            'name': 'Preseed (Debian/Ubuntu)',
            'description': 'Uses Debian preseed for automated installation',
            'pros': ['Built into Debian installer', 'Complete automation', 'No post-install needed'],
            'cons': ['Debian-specific', 'Complex configuration'],
            'use_case': 'Debian-based deployments'
        },
        {
            'name': 'SSH Post-Configuration',
            'description': 'SSH-based configuration after first boot',
            'pros': ['Works with any template', 'Flexible', 'Easy to debug'],
            'cons': ['Requires initial credentials', 'Network dependency'],
            'use_case': 'Development and testing'
        },
        {
            'name': 'Custom Templates',
            'description': 'Pre-configured templates ready to use',
            'pros': ['Fastest deployment', 'Consistent configuration', 'No automation needed'],
            'cons': ['Template maintenance overhead', 'Storage requirements'],
            'use_case': 'Standardized deployments'
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{i}. {method['name']}")
        print(f"   📝 {method['description']}")
        print(f"   ✅ Pros: {', '.join(method['pros'])}")
        print(f"   ⚠️  Cons: {', '.join(method['cons'])}")
        print(f"   🎯 Best for: {method['use_case']}")

if __name__ == "__main__":
    print("🚀 Automated VM Configuration Demo")
    
    # Check required environment variables
    required_vars = ["XCP_HOST", "XCP_USERNAME", "XCP_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        show_configuration_methods()
        sys.exit(1)
    
    show_configuration_methods()
    
    print(f"\n🤔 This demo shows how to create VMs that are fully configured automatically.")
    print(f"No manual console interaction required!")
    
    # Uncomment to test actual VM creation
    # success = test_automated_vm_creation()
    # 
    # if success:
    #     print(f"\n🎉 AUTOMATED VM CREATION TEST PASSED!")
    # else:
    #     print(f"\n❌ Automated VM creation test failed")
    #     sys.exit(1)