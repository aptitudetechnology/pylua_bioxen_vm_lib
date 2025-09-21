#!/usr/bin/env python3
"""
List Available Templates in XCP-ng
Helps identify proper base templates for VM creation
"""

import sys
import os
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
print("🔧 Loading environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=project_dir / '.env')
    print("✅ Loaded .env file with python-dotenv")
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
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:
                        os.environ[key] = value
        print("✅ Manually loaded .env file")

def list_templates():
    """List all available templates in XCP-ng"""
    
    print("📋 XCP-ng Template Analysis")
    print("=" * 50)
    
    # Get XCP-ng credentials
    xcp_host = os.getenv('XCP_HOST', '192.168.1.198')
    xcp_username = os.getenv('XCP_USERNAME', 'root')
    xcp_password = os.getenv('XCP_PASSWORD')
    
    if not xcp_password:
        print("❌ Missing XCP_PASSWORD in environment")
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
        # Get all templates
        print("\n🔍 Fetching template list...")
        templates = client.list_templates()
        
        # Filter and sort templates
        template_list = []
        for template in templates:
            template_list.append({
                'uuid': template.get('uuid', ''),
                'name': template.get('name-label', ''),
                'description': template.get('name-description', ''),
                'ref': template.get('ref', '')
            })
        
        # Sort by name
        template_list.sort(key=lambda x: x['name'].lower())
        
        print(f"\n📊 Found {len(template_list)} templates:")
        print("=" * 80)
        
        debian_templates = []
        cloud_templates = []
        other_templates = []
        
        for i, template in enumerate(template_list, 1):
            name = template['name']
            uuid = template['uuid']
            desc = template['description']
            
            # Categorize templates
            if 'debian' in name.lower() or 'bookworm' in name.lower():
                debian_templates.append(template)
                category = "🐧 DEBIAN"
            elif 'cloud' in name.lower() or 'cloud-init' in desc.lower():
                cloud_templates.append(template)
                category = "☁️  CLOUD"
            else:
                other_templates.append(template)
                category = "📦 OTHER"
            
            print(f"{i:2d}. {category} {name}")
            print(f"    UUID: {uuid}")
            if desc and desc != name:
                print(f"    Desc: {desc[:60]}{'...' if len(desc) > 60 else ''}")
            print()
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("=" * 50)
        
        if debian_templates:
            print("🐧 Debian Templates Found:")
            for template in debian_templates:
                if 'install' not in template['name'].lower():
                    print(f"   ✅ GOOD: {template['name']} ({template['uuid']})")
                else:
                    print(f"   ⚠️  INSTALLER: {template['name']} (may need completion)")
        
        if cloud_templates:
            print("\n☁️  Cloud-Ready Templates:")
            for template in cloud_templates:
                print(f"   ✅ CLOUD: {template['name']} ({template['uuid']})")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Try templates marked as 'GOOD' for basic VM creation")
        print("2. Avoid templates with 'install' in the name")
        print("3. Cloud templates should work with cloud-init")
        print("4. If none work, create a fresh VM and make your own template")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list templates: {e}")
        return False

if __name__ == "__main__":
    if list_templates():
        print("\n✅ Template analysis complete")
    else:
        print("\n❌ Template analysis failed")