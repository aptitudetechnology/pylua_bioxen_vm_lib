#!/usr/bin/env python3
"""
Create Pre-configured BioXen Template
This script helps create a custom template that's pre-installed and ready for automation
"""

import sys
import os
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path for direct import
sys.path.insert(0, str(Path(__file__).parent / 'pylua_bioxen_vm_lib'))

def create_bioxen_template():
    """Create a pre-configured BioXen template"""
    
    print("🏗️  Creating Pre-configured BioXen Template")
    print("=" * 60)
    print("SOLUTION: Create a ready-to-use template")
    print("=" * 60)
    
    print("""
🎯 TEMPLATE CREATION STRATEGY

The issue: Debian templates are installer templates that require manual setup.
The solution: Create a pre-configured template from an existing VM.

📋 STEP-BY-STEP PROCESS:

1️⃣  MANUAL SETUP (One-time only):
   - Create VM from Debian Bookworm 12 template
   - Complete manual installation via console:
     • Language: English
     • Network: DHCP
     • User: debian / password: debian123
     • Packages: SSH Server, Standard utilities
   - Install required software:
     • apt update && apt upgrade -y
     • apt install -y lua5.4 lua5.4-dev luarocks curl git sudo
     • usermod -aG sudo debian
   - Configure SSH:
     • Enable SSH key authentication
     • Set up sudo without password for debian user
   - Clean up and shut down

2️⃣  CONVERT TO TEMPLATE (Automated):
   - Power off the configured VM
   - Convert VM to template using XCP-ng
   - Name it "BioXen-Debian-Ready"

3️⃣  AUTOMATED DEPLOYMENT (Forever after):
   - Use the pre-configured template
   - VMs boot directly to login screen
   - SSH access immediately available
   - No installer interaction needed

📝 COMMANDS TO RUN:

# After manual setup, convert VM to template:
xe vm-shutdown vm=<your-configured-vm-name>
xe vm-set-is-a-template vm=<your-configured-vm-name> is-a-template=true
xe template-param-set uuid=<template-uuid> name-label="BioXen-Debian-Ready"
""")
    
    # Check if we have any existing configured VMs
    try:
        import xmlrpc.client
        import ssl
        
        # Configuration
        host = os.getenv("XCP_HOST")
        username = os.getenv("XCP_USERNAME")
        password = os.getenv("XCP_PASSWORD", "")
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connect
        url = f"https://{host}/"
        server = xmlrpc.client.ServerProxy(url, context=ssl_context, verbose=False)
        
        # Authenticate
        result = server.session.login_with_password(username, password)
        session_ref = result['Value']
        
        print("🔍 CHECKING FOR EXISTING CONFIGURED VMs:")
        
        # Get all VMs
        vms_result = server.VM.get_all_records(session_ref)
        
        if vms_result['Status'] == 'Success':
            configured_vms = []
            
            for vm_ref, vm_record in vms_result['Value'].items():
                if (not vm_record.get('is_a_template', False) and 
                    not vm_record.get('is_control_domain', False) and
                    not vm_record.get('is_a_snapshot', False)):
                    
                    vm_name = vm_record.get('name_label', '')
                    power_state = vm_record.get('power_state', '')
                    
                    # Look for VMs that might be configured
                    if any(keyword in vm_name.lower() for keyword in ['bioxen', 'debian', 'configured']):
                        configured_vms.append({
                            'name': vm_name,
                            'uuid': vm_record.get('uuid', ''),
                            'power_state': power_state,
                            'ref': vm_ref
                        })
            
            if configured_vms:
                print("   ✅ Found potential VMs to convert to template:")
                for vm in configured_vms:
                    print(f"      📦 {vm['name']} ({vm['power_state']})")
                    print(f"          UUID: {vm['uuid']}")
                
                print(f"\n💡 TO CONVERT A VM TO TEMPLATE:")
                print(f"   1. Make sure VM is shut down")
                print(f"   2. Run: xe vm-set-is-a-template vm=<vm-name> is-a-template=true")
                print(f"   3. Run: xe template-param-set uuid=<template-uuid> name-label=\"BioXen-Debian-Ready\"")
            else:
                print("   ❌ No configured VMs found")
                print("   💡 You'll need to manually create and configure a VM first")
        
        # Logout
        server.session.logout(session_ref)
        
    except Exception as e:
        print(f"❌ Error checking VMs: {e}")
    
    print(f"""
🚀 ALTERNATIVE: Use Cloud Images

Instead of installer templates, you can use cloud-ready images:

1️⃣  Download Debian cloud image:
   wget https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2

2️⃣  Import to XCP-ng:
   xe vm-import filename=debian-12-generic-amd64.qcow2

3️⃣  Configure cloud-init:
   - These images support cloud-init for automation
   - No manual installation required
   - SSH keys can be injected at boot time

📚 DOCUMENTATION:
   - XCP-ng Cloud-init guide: https://docs.xcp-ng.org/guides/cloud-init/
   - Debian Cloud Images: https://cloud.debian.org/images/cloud/
""")

if __name__ == "__main__":
    create_bioxen_template()