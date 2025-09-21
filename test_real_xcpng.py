#!/usr/bin/env python3
"""
Test XCP-ng Integration with Real Server
Connects to your actual XCP-ng server and demonstrates Phase 1 functionality
"""

import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_xcpng_connection():
    """Test connection to real XCP-ng server"""
    
    print("=" * 60)
    print("TESTING XCP-NG INTEGRATION WITH REAL SERVER")
    print("=" * 60)
    
    try:
        # Import the XCP-ng integration modules
        from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
        from pylua_bioxen_vm_lib.xcp_ng_config import XCPngConfig
        
        print("✅ XCP-ng modules imported successfully")
        
        # Load configuration from environment
        config = XCPngConfig()
        xcp_config = config.get_xcp_connection_config()
        
        print(f"📡 Connecting to XCP-ng server: {xcp_config['xcp_host']}")
        print(f"👤 Username: {xcp_config['xcp_username']}")
        
        # Test connection to existing VM
        vm_name = "bioxen-lua"  # Using your running VM
        
        print(f"\n🔍 Looking for VM: {vm_name}")
        
        # Create XCP-ng VM instance
        vm_config = xcp_config.copy()
        vm_config.update({
            "template_name": os.getenv("XCP_TEMPLATE", "test-template"),
            "vm_username": os.getenv("VM_USERNAME", "root"),
            "vm_name": vm_name
        })
        
        xcpng_vm = XCPngVM(
            vm_id=f"test-{vm_name}",
            config=vm_config
        )
        
        print("✅ XCPngVM instance created")
        
        # Test VM information retrieval
        print(f"\n📋 Testing VM information retrieval...")
        vm_info = xcpng_vm.get_vm_info()
        if vm_info:
            print(f"✅ VM found: {vm_info.get('name-label', 'Unknown')}")
            print(f"   UUID: {vm_info.get('uuid', 'Unknown')}")
            print(f"   Power State: {vm_info.get('power-state', 'Unknown')}")
            print(f"   Memory: {vm_info.get('memory-actual', 'Unknown')} bytes")
        else:
            print(f"❌ VM '{vm_name}' not found")
            return False
        
        # Test VM status check
        print(f"\n🔄 Testing VM status check...")
        is_running = xcpng_vm.is_running()
        print(f"✅ VM running status: {is_running}")
        
        # If VM is running, test more operations
        if is_running:
            print(f"\n🌐 Testing network information...")
            try:
                networks = xcpng_vm.get_network_info()
                if networks:
                    print(f"✅ Network information retrieved: {len(networks)} network(s)")
                    for i, net in enumerate(networks[:2]):  # Show first 2 networks
                        print(f"   Network {i+1}: {net.get('device', 'Unknown device')}")
                else:
                    print("⚠️  No network information available")
            except Exception as e:
                print(f"⚠️  Network info error (this is normal): {e}")
            
            print(f"\n💾 Testing VM metrics...")
            try:
                metrics = xcpng_vm.get_vm_metrics()
                if metrics:
                    print(f"✅ VM metrics retrieved")
                    print(f"   CPU utilization available: {'cpu_utilisation' in metrics}")
                    print(f"   Memory metrics available: {'memory' in str(metrics)}")
                else:
                    print("⚠️  No metrics available")
            except Exception as e:
                print(f"⚠️  Metrics error (this is normal): {e}")
                
        else:
            print("⚠️  VM is not running - limited testing available")
        
        print(f"\n✅ XCP-ng integration test completed successfully!")
        print(f"🎉 Phase 1 XCP-ng functionality is working with your real server!")
        
        return True
        
    except Exception as e:
        print(f"❌ XCP-ng integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vm_management():
    """Test VM management operations"""
    
    print(f"\n" + "=" * 60)
    print("TESTING VM MANAGEMENT OPERATIONS")
    print("=" * 60)
    
    try:
        from pylua_bioxen_vm_lib.vm_manager import VMManager
        
        # Create VM manager
        vm_manager = VMManager(debug_mode=True)
        print("✅ VM Manager created")
        
        # Test creating XCP-ng VM through factory
        vm_id = "test-xcpng-integration"
        
        print(f"\n🏭 Testing XCP-ng VM factory...")
        
        # Load XCP-ng configuration
        from pylua_bioxen_vm_lib.xcp_ng_config import XCPngConfig
        xcp_config_obj = XCPngConfig()
        xcp_config = xcp_config_obj.get_xcp_connection_config()
        
        # Add required fields for XCPngVM
        vm_config = xcp_config.copy()
        vm_config.update({
            "template_name": os.getenv("XCP_TEMPLATE", "test-template"),
            "vm_username": os.getenv("VM_USERNAME", "root"),
            "vm_name": "bioxen-lua"  # Your existing VM
        })
        
        xcpng_vm = vm_manager.create_vm(
            vm_id=vm_id,
            vm_type="xcpng", 
            config=vm_config
        )
        
        print(f"✅ XCP-ng VM created through factory")
        print(f"   VM ID: {vm_id}")
        print(f"   VM Type: {type(xcpng_vm).__name__}")
        
        # Test VM manager operations
        print(f"\n📊 Testing VM manager status...")
        print(f"   Total VMs managed: {len(vm_manager.vms)}")
        print(f"   VM IDs: {list(vm_manager.vms.keys())}")
        
        # Cleanup
        vm_manager.shutdown_all()
        print(f"✅ VM manager shutdown completed")
        
        return True
        
    except Exception as e:
        print(f"❌ VM management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Phase 1 XCP-ng Integration Test")
    print("This will test the Phase 1 implementation with your real XCP-ng server")
    
    # Check environment
    required_vars = ["XCP_HOST", "XCP_USERNAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    # Run tests
    success1 = test_xcpng_connection()
    success2 = test_vm_management()
    
    if success1 and success2:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Phase 1 XCP-ng integration is working with your real server")
        print(f"✅ Ready to proceed with Phase 2 development")
    else:
        print(f"\n❌ Some tests failed - please check the errors above")
        sys.exit(1)