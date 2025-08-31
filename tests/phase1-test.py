# Phase 1 Test: Basic Multi-VM Support

def test_vm_factory_basic():
    from pylua_bioxen_vm_lib.vm_manager import VMManager
    manager = VMManager()
    vm = manager.create_vm(vm_id="test_basic_vm", vm_type="basic")
    assert vm is not None
    print("Phase 1: Basic VM creation passed.")

if __name__ == "__main__":
    test_vm_factory_basic()
