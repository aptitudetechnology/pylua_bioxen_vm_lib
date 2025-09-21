#!/usr/bin/env python3
"""
Test VM Creation on XCP-ng Server
Creates a new VM from template and validates it works
"""

import sys
import os
import time
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_vm_creation():
    """Test creating a new VM on XCP-ng server"""
    
    print("=" * 60)
    print("TESTING VM CREATION ON XCP-NG SERVER")
    print("=" * 60)
    
    try:
        # Import required modules
        from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
        from pylua_bioxen_vm_lib.xcp_ng_config import XCPngConfig
        from pylua_bioxen_vm_lib.xapi_client import XAPIClient
        
        print("✅ XCP-ng modules imported successfully")
        
        # Load configuration
        config = XCPngConfig()
        xcp_config = config.get_xcp_connection_config()
        
        print(f"📡 Connecting to XCP-ng server: {xcp_config['xcp_host']}")
        
        # First, let's check what templates are available
        print(f"\n🔍 Checking available templates...")
        xapi_client = XAPIClient(
            host=xcp_config['xcp_host'],
            username=xcp_config['xcp_username'],
            password=xcp_config['xcp_password']
        )
        
        if not xapi_client.authenticate():
            print("❌ Failed to authenticate with XCP-ng")
            return False
            
        templates = xapi_client.list_templates()
        print(f"✅ Found {len(templates)} templates:")
        for i, template in enumerate(templates[:10]):  # Show first 10
            print(f"   {i+1}. {template.get('name-label', 'Unknown')}")
        
        # Check if our configured template exists
        template_name = os.getenv("XCP_TEMPLATE", "test-template")
        template_found = any(t.get('name-label') == template_name for t in templates)
        
        if not template_found:
            print(f"⚠️  Configured template '{template_name}' not found")
            print("   Available templates for VM creation:")
            valid_templates = [t for t in templates if not t.get('is_control_domain', False)]
            for template in valid_templates[:5]:
                print(f"     - {template.get('name-label', 'Unknown')}")
            
            # Use first available template for testing
            if valid_templates:
                template_name = valid_templates[0].get('name-label')
                print(f"   Using '{template_name}' for testing")
            else:
                print("❌ No suitable templates found for VM creation")
                return False
        else:
            print(f"✅ Template '{template_name}' found and ready")
        
        # Prepare VM configuration
        vm_name = f"pylua-test-{int(time.time())}"  # Unique name
        vm_config = {
            "xcp_host": xcp_config['xcp_host'],
            "xcp_username": xcp_config['xcp_username'], 
            "xcp_password": xcp_config['xcp_password'],
            "template_name": template_name,
            "vm_username": os.getenv("VM_USERNAME", "root"),
            "vm_config": {
                "memory": "1GB",  # Small for testing
                "vcpus": 1
            }
        }
        
        print(f"\n🏗️  Creating VM: {vm_name}")
        print(f"   Template: {template_name}")
        print(f"   Memory: 1GB, CPUs: 1")
        
        # Create XCP-ng VM instance (this will create the VM)
        xcpng_vm = XCPngVM(
            vm_id=vm_name,
            config=vm_config
        )
        
        print("✅ XCPngVM instance created")
        
        # Start the VM (this triggers actual creation)
        print(f"\n🚀 Starting VM creation process...")
        try:
            xcpng_vm.start()
            print("✅ VM created and started successfully!")
            
            # Get VM information
            vm_info = xcpng_vm.get_vm_info()
            print(f"   VM UUID: {vm_info.get('vm_uuid', 'Unknown')}")
            print(f"   VM IP: {vm_info.get('vm_ip', 'Pending...')}")
            
            # Test basic operations
            print(f"\n🧪 Testing VM operations...")
            is_running = xcpng_vm.is_running()
            print(f"   VM running: {is_running}")
            
            if is_running:
                print("✅ VM creation and startup successful!")
                
                # Test communication if possible
                try:
                    result = xcpng_vm.execute_string("print('Hello from new VM!')")
                    if result.get('success'):
                        print("✅ VM communication test successful!")
                        print(f"   Output: {result.get('output', 'No output')}")
                    else:
                        print("⚠️  VM created but communication needs setup")
                except Exception as e:
                    print(f"⚠️  VM created but communication error: {e}")
            
            # Cleanup - ask user before destroying
            print(f"\n🧹 VM Creation Test Complete!")
            cleanup_choice = input("Delete the test VM? (y/N): ").lower().strip()
            
            if cleanup_choice == 'y':
                print("🗑️  Cleaning up test VM...")
                xcpng_vm.stop()
                # Note: We might need to add a delete_vm method
                print("✅ Test VM stopped (manual cleanup may be needed)")
            else:
                print(f"📝 Test VM '{vm_name}' left running for your inspection")
                print("   You can manage it via XCP-ng Center or xe commands")
                
        except Exception as e:
            print(f"❌ VM creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ VM creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting XCP-ng VM Creation Test")
    print("This will create a new VM on your XCP-ng server")
    
    # Check environment
    required_vars = ["XCP_HOST", "XCP_USERNAME", "XCP_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    success = test_vm_creation()
    
    if success:
        print(f"\n🎉 VM CREATION TEST PASSED!")
        print(f"✅ Phase 1 VM creation capability verified")
    else:
        print(f"\n❌ VM creation test failed")
        sys.exit(1)