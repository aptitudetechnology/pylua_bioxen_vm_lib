#!/usr/bin/env python3
"""
Test script to verify pylua_bioxen_vm_lib installation and basic functionality.
Run this after installing from PyPI test to verify everything works.
"""

def test_package_import():
    """Test that the package can be imported"""
    print("Testing package import...")
    try:
        import pylua_bioxen_vm_lib
        print(f"✅ Successfully imported pylua_bioxen_vm_lib version {pylua_bioxen_vm_lib.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import package: {e}")
        return False

def test_create_vm_basic():
    """Test basic VM creation"""
    print("\nTesting basic VM creation...")
    try:
        from pylua_bioxen_vm_lib import create_vm
        vm = create_vm("test_vm", vm_type="basic")
        print(f"✅ Successfully created basic VM: {vm.__class__.__name__}")
        return True
    except Exception as e:
        print(f"❌ Failed to create basic VM: {e}")
        return False

def test_create_vm_xcpng_placeholder():
    """Test XCP-ng VM placeholder creation"""
    print("\nTesting XCP-ng VM placeholder creation...")
    try:
        from pylua_bioxen_vm_lib import create_vm
        config = {
            "xcpng_host": "test.example.com",
            "username": "testuser",
            "password": "testpass",
            "template": "test-template"
        }
        vm = create_vm("test_xcpng", vm_type="xcpng", config=config)
        print(f"✅ Successfully created XCP-ng placeholder VM: {vm.__class__.__name__}")
        
        # Test placeholder behavior
        try:
            vm.start()
            print("❌ XCP-ng VM start() should raise NotImplementedError")
            return False
        except NotImplementedError as e:
            if "Phase 2" in str(e):
                print("✅ XCP-ng placeholder correctly raises NotImplementedError with Phase 2 message")
                return True
            else:
                print(f"❌ Unexpected NotImplementedError message: {e}")
                return False
    except Exception as e:
        print(f"❌ Failed to create XCP-ng VM: {e}")
        return False

def test_vm_manager():
    """Test VMManager functionality"""
    print("\nTesting VMManager...")
    try:
        from pylua_bioxen_vm_lib import VMManager
        manager = VMManager()
        
        # Test basic VM via manager
        basic_vm = manager.create_vm("manager_basic", vm_type="basic")
        print("✅ VMManager basic VM creation works")
        
        # Test VM info
        info = manager.get_vm_info("manager_basic")
        if info and info.get("vm_type") == "basic":
            print("✅ VM info tracking works")
            return True
        else:
            print(f"❌ VM info incorrect: {info}")
            return False
    except Exception as e:
        print(f"❌ VMManager test failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility"""
    print("\nTesting backward compatibility...")
    try:
        from pylua_bioxen_vm_lib import create_vm
        
        # Test default parameters (should work as before)
        vm = create_vm("backward_test")
        print("✅ Default create_vm() works (backward compatible)")
        
        # Test old-style parameters
        vm2 = create_vm("backward_test2", networked=False, debug_mode=True)
        print("✅ Old-style parameters work")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("pylua_bioxen_vm_lib Installation Test")
    print("=" * 60)
    
    tests = [
        test_package_import,
        test_create_vm_basic,
        test_create_vm_xcpng_placeholder,
        test_vm_manager,
        test_backward_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("✅ Package installation successful")
        print("✅ Phase 1 multi-VM support working")
        print("✅ Backward compatibility maintained")
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
