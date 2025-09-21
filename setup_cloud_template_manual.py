#!/usr/bin/env python3
"""
Manual Cloud Template Setup Helper
Provides step-by-step instructions for manual template creation
"""

import os
import sys
from pathlib import Path

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / '.env')
except ImportError:
    pass

def show_manual_setup_guide():
    """Show manual setup instructions"""
    
    print("📋 Manual Cloud Template Setup Guide")
    print("=" * 50)
    
    # Get connection details
    xcp_host = os.getenv('XCP_HOST', 'your-xcpng-server.com')
    xcp_username = os.getenv('XCP_USERNAME', 'root')
    
    cloud_image_file = "debian-12-generic-amd64.qcow2"
    template_name = "Debian-12-Cloud-BioXen"
    
    # Check if image exists
    if os.path.exists(cloud_image_file):
        file_size = os.path.getsize(cloud_image_file) / (1024 * 1024)
        print(f"✅ Cloud image found: {cloud_image_file} ({file_size:.1f} MB)")
    else:
        print(f"❌ Cloud image not found: {cloud_image_file}")
        print("💡 Download it first:")
        print("   wget https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2")
        return
    
    print(f"\n📤 STEP 1: Upload cloud image to XCP-ng")
    print("   Run this command:")
    print(f"   scp {cloud_image_file} {xcp_username}@{xcp_host}:/tmp/")
    
    print(f"\n📦 STEP 2: Create template on XCP-ng server")
    print("   SSH to your XCP-ng server:")
    print(f"   ssh {xcp_username}@{xcp_host}")
    print(f"   ")
    print(f"   Then run these commands:")
    print(f"   # Import the cloud image")
    print(f"   xe vm-import filename=/tmp/{cloud_image_file} new-name-label='{template_name}'")
    print(f"   ")
    print(f"   # Get the VM UUID (replace with actual UUID from import output)")
    print(f"   VM_UUID=$(xe vm-list name-label='{template_name}' params=uuid --minimal)")
    print(f"   echo \"VM UUID: $VM_UUID\"")
    print(f"   ")
    print(f"   # Set as template")
    print(f"   xe vm-set-is-a-template uuid=$VM_UUID is-a-template=true")
    print(f"   ")
    print(f"   # Set description")
    print(f"   xe template-param-set uuid=$VM_UUID name-description='Debian 12 cloud image with cloud-init support'")
    print(f"   ")
    print(f"   # Clean up")
    print(f"   rm /tmp/{cloud_image_file}")
    print(f"   ")
    print(f"   # Verify template")
    print(f"   xe template-list name-label='{template_name}'")
    
    print(f"\n🔍 STEP 3: Verify template via Python")
    print("   Run this verification script:")
    print("   python3 -c \"")
    print("import sys, os")
    print("sys.path.append('.')") 
    print("from pylua_bioxen_vm_lib.xapi_client import XAPIClient")
    print("client = XAPIClient(os.getenv('XCP_HOST'), os.getenv('XCP_USERNAME'), os.getenv('XCP_PASSWORD'))")
    print("client.authenticate()")
    print("templates = client.list_templates()")
    print("for t in templates:")
    print(f"    if '{template_name}' in t.get('name-label', ''):")
    print("        print(f'✅ Template found: {{t[\\\"name-label\\\"]}} ({{t[\\\"uuid\\\"]}})')")
    print("   \"")
    
    print(f"\n🧪 STEP 4: Test VM creation")
    print("   python3 test_cloud_vm_creation.py")
    
    print(f"\n💡 Alternative: Use automated script")
    print("   python3 setup_cloud_template_remote.py")

def check_prerequisites():
    """Check if prerequisites are available"""
    
    print("\n🔍 Checking prerequisites...")
    
    # Check environment variables
    xcp_host = os.getenv('XCP_HOST')
    xcp_username = os.getenv('XCP_USERNAME')
    xcp_password = os.getenv('XCP_PASSWORD')
    
    if all([xcp_host, xcp_username, xcp_password]):
        print(f"✅ XCP-ng credentials configured")
        print(f"   Host: {xcp_host}")
        print(f"   Username: {xcp_username}")
    else:
        print(f"⚠️  XCP-ng credentials missing")
        print(f"   Create .env file with:")
        print(f"   XCP_HOST=your-xcpng-server.com")
        print(f"   XCP_USERNAME=root")
        print(f"   XCP_PASSWORD=your-password")
    
    # Check SSH connectivity
    if xcp_host and xcp_username:
        print(f"\n🔗 Test SSH connectivity:")
        print(f"   ssh {xcp_username}@{xcp_host} 'xe host-list'")
    
    # Check SCP capability
    cloud_image_file = "debian-12-generic-amd64.qcow2"
    if os.path.exists(cloud_image_file):
        print(f"✅ Cloud image ready for upload")
    else:
        print(f"❌ Cloud image missing - download first")

if __name__ == "__main__":
    print("🛠️  Cloud Template Setup Helper")
    
    check_prerequisites()
    show_manual_setup_guide()
    
    print(f"\n📚 Additional Resources:")
    print(f"   • Cloud Images Guide: CLOUD_IMAGES_GUIDE.md")
    print(f"   • Implementation Plan: XCP-NG_IMPLEMENTATION_PLAN.md")
    print(f"   • Automated Setup: setup_cloud_template_remote.py")