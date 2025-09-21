#!/usr/bin/env python3
"""
Direct VM Creation Test
Tests VM creation using direct file imports to avoid package issues
"""

import sys
import os
from pathlib import Path
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path for direct import
sys.path.insert(0, str(Path(__file__).parent / 'pylua_bioxen_vm_lib'))

def test_vm_creation():
    """Test VM creation directly using file imports"""
    
    print("🚀 Starting Direct VM Creation Test")
    print("=" * 60)
    print("TESTING VM CREATION WITH DEBIAN BOOKWORM 12")
    print("=" * 60)
    
    try:
        # Import directly from files
        import xmlrpc.client
        import ssl
        
        # Configuration
        host = os.getenv("XCP_HOST")
        username = os.getenv("XCP_USERNAME")
        password = os.getenv("XCP_PASSWORD", "")
        
        if not password:
            print("❌ XCP_PASSWORD is required in .env file")
            return False
            
        print(f"📡 Connecting to: {host}")
        print(f"👤 Username: {username}")
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Try HTTPS first, fall back to HTTP
        try:
            url = f"https://{host}/"
            server = xmlrpc.client.ServerProxy(url, context=ssl_context, verbose=False)
        except Exception:
            url = f"http://{host}/"
            server = xmlrpc.client.ServerProxy(url, verbose=False)
        
        print(f"🔗 Using URL: {url}")
        
        # Authenticate
        print("🔑 Authenticating...")
        result = server.session.login_with_password(username, password)
        
        if result['Status'] != 'Success':
            print(f"❌ Authentication failed: {result}")
            return False
            
        session_ref = result['Value']
        print("✅ Authentication successful")
        
        # Get templates
        print("📋 Listing templates...")
        templates_result = server.VM.get_all_records(session_ref)
        
        if templates_result['Status'] != 'Success':
            print(f"❌ Failed to get templates: {templates_result}")
            return False
        
        # Find Debian Bookworm 12 template
        debian_template = None
        all_templates = []
        
        for vm_ref, vm_record in templates_result['Value'].items():
            if vm_record.get('is_a_template', False) and not vm_record.get('is_a_snapshot', False):
                template_name = vm_record.get('name_label', '')
                template_uuid = vm_record.get('uuid', '')
                all_templates.append(f"   - {template_name} (UUID: {template_uuid})")
                
                # Look for Debian template (case insensitive)
                if 'debian' in template_name.lower() and ('bookworm' in template_name.lower() or '12' in template_name):
                    debian_template = {
                        'ref': vm_ref,
                        'uuid': template_uuid,
                        'name': template_name
                    }
                    
        print(f"📋 Found {len(all_templates)} templates:")
        for template in all_templates:
            print(template)
            
        if not debian_template:
            print("❌ Debian Bookworm 12 template not found!")
            print("Available templates listed above.")
            return False
            
        print(f"\n✅ Found Debian template: {debian_template['name']}")
        print(f"📋 Template UUID: {debian_template['uuid']}")
        
        # Create VM name with timestamp
        vm_name = f"bioxen-test-vm-{int(time.time())}"
        print(f"🏗️  Creating VM: {vm_name}")
        
        # Clone the template
        clone_result = server.VM.clone(session_ref, debian_template['ref'], vm_name)
        
        if clone_result['Status'] != 'Success':
            error_info = clone_result.get('ErrorDescription', ['Unknown error'])
            print(f"❌ Failed to clone template: {error_info}")
            return False
            
        new_vm_ref = clone_result['Value']
        print("✅ VM cloned successfully")
        
        # Get the UUID of the new VM
        uuid_result = server.VM.get_uuid(session_ref, new_vm_ref)
        if uuid_result['Status'] != 'Success':
            print("❌ Failed to get new VM UUID")
            return False
            
        new_vm_uuid = uuid_result['Value']
        print(f"📋 New VM UUID: {new_vm_uuid}")
        
        # Set the VM as not a template
        server.VM.set_is_a_template(session_ref, new_vm_ref, False)
        print("✅ VM configured as regular VM (not template)")
        
        # Get VM information
        vm_record_result = server.VM.get_record(session_ref, new_vm_ref)
        if vm_record_result['Status'] == 'Success':
            vm_record = vm_record_result['Value']
            print(f"📋 VM Name: {vm_record.get('name_label', 'Unknown')}")
            print(f"📋 Power State: {vm_record.get('power_state', 'Unknown')}")
            print(f"💾 Memory: {vm_record.get('memory_static_max', 0)} bytes")
            print(f"⚡ VCPUs: {vm_record.get('VCPUs_max', 0)}")
        
        # Ask user if they want to start the VM
        print(f"\n🤔 VM created successfully!")
        print(f"VM Name: {vm_name}")
        print(f"VM UUID: {new_vm_uuid}")
        print(f"VM Ref: {new_vm_ref}")
        
        # Note: In a real scenario, you might want to start the VM
        # For testing, we'll leave it stopped
        print(f"\n✅ VM CREATION TEST COMPLETED SUCCESSFULLY!")
        print(f"🎉 Created VM '{vm_name}' from Debian Bookworm 12 template")
        
        # Logout
        try:
            server.session.logout(session_ref)
            print("✅ Session logged out")
        except Exception:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ VM creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct VM Creation Test")
    
    # Check required environment variables
    required_vars = ["XCP_HOST", "XCP_USERNAME", "XCP_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    success = test_vm_creation()
    
    if success:
        print(f"\n🎉 VM CREATION TEST PASSED!")
    else:
        print(f"\n❌ VM creation test failed")
        sys.exit(1)