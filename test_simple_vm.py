#!/usr/bin/env python3
"""
Simple VM Creation Test - Without Cloud-Init
Tests basic VM creation and boot to verify template compatibility
"""

import sys
import os
import time
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=project_dir / '.env')
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Loading .env manually...")
    # Manual .env loading
    env_file = project_dir / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#') and line:
                    key, value = line.split('=', 1)
                    # Clean up key and value
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:  # Only set non-empty values
                        os.environ[key] = value
                        print(f"   📝 Set {key}={'***' if 'PASSWORD' in key else value}")
        print("✅ Manually loaded .env file")
    else:
        print("❌ .env file not found")

def test_simple_vm_creation():
    """Test basic VM creation without cloud-init"""
    
    print("🚀 Simple VM Creation Test")
    print("=" * 40)
    
    # Get XCP-ng credentials
    xcp_host = os.getenv('XCP_HOST', '192.168.1.198')
    xcp_username = os.getenv('XCP_USERNAME', 'root')
    xcp_password = os.getenv('XCP_PASSWORD')
    
    print(f"🔍 Debug - XCP_HOST: {xcp_host}")
    print(f"🔍 Debug - XCP_USERNAME: {xcp_username}")
    print(f"🔍 Debug - XCP_PASSWORD exists: {'Yes' if xcp_password else 'No'}")
    
    if not xcp_password:
        print("❌ Missing XCP_PASSWORD in environment")
        print("💡 Create .env file with XCP_PASSWORD=your-password")
        print("💡 Or run: export XCP_PASSWORD=your-password")
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
        # Use the fixed Debian template
        template_uuid = "cea07a22-1811-e80e-2799-9b64117deab7"
        vm_name = f"simple-test-vm-{int(time.time())}"
        
        print(f"\n📦 Creating simple VM: {vm_name}")
        print(f"   📋 Template: {template_uuid}")
        
        # Create VM without cloud-init
        vm_uuid = client.create_vm_from_template(template_uuid, vm_name)
        print(f"   ✅ VM created: {vm_uuid}")
        
        # Start VM
        print(f"   🔄 Starting VM...")
        if client.start_vm(vm_uuid):
            print(f"   ✅ VM started successfully")
        else:
            print(f"   ❌ Failed to start VM")
            return False
        
        # Wait and check status
        print(f"\n⏳ Monitoring VM for 2 minutes...")
        
        for i in range(12):  # 2 minutes
            time.sleep(10)
            
            # Check VM status via SSH
            import subprocess
            result = subprocess.run([
                'ssh', 'root@192.168.1.198', 
                f'xe vm-param-get uuid={vm_uuid} param-name=power-state'
            ], capture_output=True, text=True, timeout=10)
            
            power_state = result.stdout.strip()
            print(f"   ⏱️  {(i+1)*10}s - Power state: {power_state}")
            
            if power_state == "halted":
                print(f"   ❌ VM halted - there may be an issue with the template")
                break
            elif power_state == "running":
                print(f"   ✅ VM running stable")
                
                # Try to get network info
                result = subprocess.run([
                    'ssh', 'root@192.168.1.198',
                    f'xe vm-param-get uuid={vm_uuid} param-name=networks'
                ], capture_output=True, text=True, timeout=10)
                
                networks = result.stdout.strip()
                if networks:
                    print(f"   🌐 Network info: {networks}")
                else:
                    print(f"   ⏳ No network info yet (still booting)")
        
        print(f"\n📊 SIMPLE VM TEST SUMMARY")
        print("=" * 30)
        print(f"VM Name: {vm_name}")
        print(f"VM UUID: {vm_uuid}")
        print(f"Template: Debian 12 (no cloud-init)")
        print(f"Result: {'✅ Success' if power_state == 'running' else '❌ Failed'}")
        
        return power_state == "running"
        
    except Exception as e:
        print(f"❌ VM creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple VM Creation Test (No Cloud-Init)")
    
    success = test_simple_vm_creation()
    
    if success:
        print(f"\n🎉 SIMPLE VM TEST PASSED!")
        print(f"✅ Basic VM creation working")
        print(f"💡 Next: Add cloud-init support to working template")
    else:
        print(f"\n❌ Simple VM test failed")
        print(f"💡 Template may need manual configuration")
        sys.exit(1)