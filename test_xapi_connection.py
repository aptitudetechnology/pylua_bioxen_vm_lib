#!/usr/bin/env python3
"""
Simple XAPI Connection Test
Tests basic XAPI connectivity and VM discovery
"""

import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_xapi_connection():
    """Test basic XAPI connection and VM listing"""
    
    print("=" * 60)
    print("TESTING XAPI CONNECTION AND VM DISCOVERY")
    print("=" * 60)
    
    try:
        from pylua_bioxen_vm_lib.xapi_client import XAPIClient
        
        # Create XAPI client
        xapi_client = XAPIClient(
            host=os.getenv("XCP_HOST"),
            username=os.getenv("XCP_USERNAME"), 
            password=os.getenv("XCP_PASSWORD", "")
        )
        
        print(f"📡 Connecting to: {os.getenv('XCP_HOST')}")
        print(f"👤 Username: {os.getenv('XCP_USERNAME')}")
        
        # Test authentication
        if not xapi_client.authenticate():
            print("❌ Failed to authenticate with XCP-ng")
            return False
            
        print("✅ Authentication successful")
        
        # List all VMs
        print(f"\n📋 Listing all VMs...")
        vms = xapi_client.list_vms()
        print(f"✅ Found {len(vms)} VMs")
        
        for vm in vms:
            name = vm.get('name-label', 'Unknown')
            power_state = vm.get('power-state', 'Unknown')
            uuid = vm.get('uuid', 'Unknown')
            print(f"   - {name}: {power_state} ({uuid[:8]}...)")
        
        # Look specifically for bioxen-lua
        print(f"\n🔍 Looking for 'bioxen-lua' VM...")
        bioxen_vm = None
        for vm in vms:
            if vm.get('name-label') == 'bioxen-lua':
                bioxen_vm = vm
                break
        
        if bioxen_vm:
            print("✅ Found 'bioxen-lua' VM:")
            print(f"   Name: {bioxen_vm.get('name-label')}")
            print(f"   UUID: {bioxen_vm.get('uuid')}")
            print(f"   Power State: {bioxen_vm.get('power-state')}")
            print(f"   Memory: {bioxen_vm.get('memory-actual', 'Unknown')} bytes")
            
            # Test getting detailed VM info
            if bioxen_vm.get('uuid'):
                print(f"\n📊 Getting detailed VM info...")
                detailed_info = xapi_client.get_vm_info(bioxen_vm['uuid'])
                if detailed_info:
                    print("✅ Detailed VM info retrieved successfully")
                else:
                    print("⚠️  Could not get detailed VM info")
        else:
            print("❌ 'bioxen-lua' VM not found")
            
        # List templates
        print(f"\n🏗️  Listing templates...")
        templates = xapi_client.list_templates()
        print(f"✅ Found {len(templates)} templates")
        
        # Look for Debian Bookworm 12
        debian_template = None
        for template in templates:
            if 'Debian Bookworm 12' in template.get('name-label', ''):
                debian_template = template
                break
        
        if debian_template:
            print("✅ Found 'Debian Bookworm 12' template:")
            print(f"   Name: {debian_template.get('name-label')}")
            print(f"   UUID: {debian_template.get('uuid')}")
        else:
            print("⚠️  'Debian Bookworm 12' template not found")
            print("   Available templates:")
            for template in templates[:5]:
                print(f"     - {template.get('name-label', 'Unknown')}")
        
        print(f"\n✅ XAPI connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ XAPI connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting XAPI Connection Test")
    
    # Check environment
    required_vars = ["XCP_HOST", "XCP_USERNAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    success = test_xapi_connection()
    
    if success:
        print(f"\n🎉 XAPI CONNECTION TEST PASSED!")
    else:
        print(f"\n❌ XAPI connection test failed")
        sys.exit(1)