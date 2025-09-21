#!/usr/bin/env python3
"""
Remote Cloud Template Setup for XCP-ng
Uploads cloud image via SSH and creates template on XCP-ng server
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

def upload_and_create_template():
    """Upload cloud image and create template via SSH"""
    
    print("☁️  Remote Cloud Template Setup for XCP-ng")
    print("=" * 60)
    
    # Get connection details
    xcp_host = os.getenv('XCP_HOST')
    xcp_username = os.getenv('XCP_USERNAME', 'root')
    xcp_password = os.getenv('XCP_PASSWORD')
    
    if not all([xcp_host, xcp_username, xcp_password]):
        print("❌ Missing XCP-ng credentials in environment")
        print("💡 Set XCP_HOST, XCP_USERNAME, XCP_PASSWORD in .env file")
        return False
    
    # File details
    cloud_image_file = "debian-12-generic-amd64.qcow2"
    template_name = "Debian-12-Cloud-BioXen"
    remote_path = f"/tmp/{cloud_image_file}"
    
    if not os.path.exists(cloud_image_file):
        print(f"❌ Cloud image not found: {cloud_image_file}")
        print("💡 Run setup_cloud_template.py first to download the image")
        return False
    
    try:
        print(f"📤 Uploading {cloud_image_file} to XCP-ng server...")
        print(f"   Target: {xcp_username}@{xcp_host}:{remote_path}")
        
        # Upload file via SCP
        scp_cmd = [
            "scp", "-o", "StrictHostKeyChecking=no",
            cloud_image_file, f"{xcp_username}@{xcp_host}:{remote_path}"
        ]
        
        print("   ⬆️  Uploading... (this may take a few minutes)")
        upload_result = subprocess.run(scp_cmd, capture_output=True, text=True)
        
        if upload_result.returncode != 0:
            print(f"   ❌ Upload failed: {upload_result.stderr}")
            return False
        
        print("   ✅ Upload completed")
        
        # Create template via SSH
        print(f"\n📦 Creating template on XCP-ng server...")
        
        # Commands to run on XCP-ng server
        xe_commands = [
            # Import VM from qcow2
            f"xe vm-import filename={remote_path} new-name-label='{template_name}'",
            
            # Get the VM UUID (xe vm-import should output it)
            f"VM_UUID=$(xe vm-list name-label='{template_name}' params=uuid --minimal)",
            
            # Set as template
            f"xe vm-set-is-a-template uuid=$VM_UUID is-a-template=true",
            
            # Set description
            f"xe template-param-set uuid=$VM_UUID name-description='Debian 12 cloud image with cloud-init support'",
            
            # Clean up uploaded file
            f"rm -f {remote_path}",
            
            # Show template info
            f"echo 'Template created successfully:'",
            f"xe template-param-list uuid=$VM_UUID | grep -E '(name-label|uuid|name-description)'"
        ]
        
        # Combine commands into a single script
        remote_script = " && ".join(xe_commands)
        
        ssh_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{xcp_username}@{xcp_host}",
            remote_script
        ]
        
        print("   🔧 Running template creation commands...")
        ssh_result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        
        if ssh_result.returncode == 0:
            print("   ✅ Template created successfully!")
            print("\n📋 Template Information:")
            
            # Parse output to show template details
            output_lines = ssh_result.stdout.strip().split('\n')
            for line in output_lines:
                if line.strip():
                    print(f"   {line.strip()}")
            
            # Extract UUID for return
            for line in output_lines:
                if 'uuid' in line and ':' in line:
                    vm_uuid = line.split(':')[1].strip()
                    return vm_uuid
            
            return True
            
        else:
            print(f"   ❌ Template creation failed: {ssh_result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Remote setup failed: {e}")
        return False

def verify_template():
    """Verify template was created successfully"""
    
    print(f"\n🔍 Verifying template via XAPI...")
    
    try:
        # Import our XAPI client
        sys.path.append(str(Path(__file__).parent))
        from pylua_bioxen_vm_lib.xapi_client import XAPIClient
        
        xcp_host = os.getenv('XCP_HOST')
        xcp_username = os.getenv('XCP_USERNAME')
        xcp_password = os.getenv('XCP_PASSWORD')
        
        client = XAPIClient(xcp_host, xcp_username, xcp_password)
        client.authenticate()
        
        # List templates
        templates = client.list_templates()
        
        # Find our template
        template_name = "Debian-12-Cloud-BioXen"
        for template in templates:
            if template_name in template.get('name-label', ''):
                print(f"✅ Template verified via XAPI:")
                print(f"   Name: {template['name-label']}")
                print(f"   UUID: {template['uuid']}")
                print(f"   Description: {template.get('name-description', 'N/A')}")
                return template['uuid']
        
        print(f"⚠️  Template not found via XAPI")
        return None
        
    except Exception as e:
        print(f"⚠️  XAPI verification failed: {e}")
        return None

def show_usage_instructions(template_uuid):
    """Show how to use the template"""
    
    print(f"\n🚀 CLOUD TEMPLATE READY!")
    print("=" * 40)
    
    print(f"""
✅ Template Details:
   Name: Debian-12-Cloud-BioXen
   UUID: {template_uuid}
   
🔧 Python Usage:
   # Use this UUID in your VM configuration
   vm_config = {{
       'template_name': '{template_uuid}',
       'use_cloud_init': True,
       # ... other config
   }}

🧪 Test the Setup:
   python3 test_cloud_vm_creation.py
   python3 demo_cloud_vm.py

📋 Next Steps:
   1. Test VM creation with test_cloud_vm_creation.py
   2. Try the full demo with demo_cloud_vm.py  
   3. Integrate into your automation workflows
""")

if __name__ == "__main__":
    print("☁️  Remote Cloud Template Setup")
    
    # Upload and create template
    result = upload_and_create_template()
    
    if result:
        # Verify via XAPI
        template_uuid = verify_template()
        
        if template_uuid:
            show_usage_instructions(template_uuid)
            print(f"\n🎉 REMOTE SETUP COMPLETED!")
        else:
            print(f"\n⚠️  Template created but verification failed")
    else:
        print(f"\n❌ Remote setup failed")
        sys.exit(1)