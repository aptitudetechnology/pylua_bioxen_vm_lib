"""
Integration test for XCP-ng support that validates BioXen-luavm compatibility
This test simulates how the BioXen-luavm project would use the XCP-ng features
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the pylua_bioxen_vm_lib to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pylua_bioxen_vm_lib.vm_manager import VMManager
from pylua_bioxen_vm_lib.xcp_ng_config import XCPngConfig, VMConfigTemplate
from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
from pylua_bioxen_vm_lib.exceptions import VMManagerError


class TestBioXenLuaVMCompatibility(unittest.TestCase):
    """Test XCP-ng integration maintains BioXen-luavm compatibility"""
    
    def setUp(self):
        """Setup test environment simulating BioXen-luavm usage"""
        self.vm_manager = VMManager(max_workers=4, debug_mode=True)
        
        # Configuration that BioXen-luavm might use
        self.xcpng_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'biox3n_s3cur3',
            'template_name': 'bioxen-lua-template',
            'vm_username': 'bioxen',
            'vm_password': 'bioxen_vm_pass',
            'memory': '4GB',
            'vcpus': 4,
            'vm_network': 'bioxen-network'
        }
    
    def test_backward_compatibility_basic_vms(self):
        """Test that basic VM creation still works (BioXen-luavm compatibility)"""
        # This simulates how BioXen-luavm currently creates VMs
        
        # Create basic VMs the old way
        basic_vm1 = self.vm_manager.create_vm('bioxen-analysis-1')
        basic_vm2 = self.vm_manager.create_vm('bioxen-analysis-2', networked=True)
        
        # Verify they work as before
        self.assertIn('bioxen-analysis-1', self.vm_manager.vms)
        self.assertIn('bioxen-analysis-2', self.vm_manager.vms)
        
        # Test basic execution (simulate biological analysis)
        lua_code = '''
        -- Simulate biological data processing
        local dna_sequence = "ATCGATCGATCG"
        local gc_content = 0
        for i = 1, #dna_sequence do
            local base = dna_sequence:sub(i, i)
            if base == "G" or base == "C" then
                gc_content = gc_content + 1
            end
        end
        local gc_percentage = (gc_content / #dna_sequence) * 100
        print("GC Content: " .. gc_percentage .. "%")
        '''
        
        result = basic_vm1.execute_string(lua_code)
        self.assertIn('stdout', result)
        self.assertIn('GC Content:', result['stdout'])
    
    def test_mixed_vm_environment(self):
        """Test BioXen-luavm using both basic and XCP-ng VMs together"""
        # Create a basic VM for local processing
        local_vm = self.vm_manager.create_vm('bioxen-local-analysis', vm_type='basic')
        
        # Create XCP-ng VM for distributed processing (mocked)
        with patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM') as mock_xcpng:
            mock_vm = Mock()
            mock_vm.execute_string.return_value = {'stdout': 'Distributed analysis complete', 'stderr': ''}
            mock_vm.session_active = True
            mock_vm.vm_id = 'bioxen-distributed-analysis'
            mock_xcpng.return_value = mock_vm
            
            distributed_vm = self.vm_manager.create_vm(
                'bioxen-distributed-analysis', 
                vm_type='xcpng', 
                config=self.xcpng_config
            )
        
        # Verify both VMs are managed
        self.assertEqual(len(self.vm_manager.vms), 2)
        self.assertIn('bioxen-local-analysis', self.vm_manager.vms)
        self.assertIn('bioxen-distributed-analysis', self.vm_manager.vms)
        
        # Simulate biological workflow using both VMs
        # Local VM: Data preprocessing
        preprocessing_code = '''
        local raw_data = {"ATCG", "GCTA", "TTAA", "CCGG"}
        local processed = {}
        for i, seq in ipairs(raw_data) do
            processed[i] = seq:upper()
        end
        print("Preprocessed " .. #processed .. " sequences")
        '''
        
        local_result = local_vm.execute_string(preprocessing_code)
        self.assertIn('Preprocessed 4 sequences', local_result['stdout'])
        
        # Distributed VM: Analysis
        analysis_code = '''
        -- Simulate complex biological analysis on XCP-ng
        print("Running distributed genomic analysis...")
        '''
        
        distributed_result = distributed_vm.execute_string(analysis_code)
        self.assertIn('Distributed analysis complete', distributed_result['stdout'])
    
    @patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM')
    def test_bioxen_package_management_workflow(self, mock_xcpng_class):
        """Test package management workflow that BioXen-luavm might use"""
        # Setup mock XCP-ng VM
        mock_vm = Mock()
        mock_vm.setup_packages.return_value = {
            'success': True,
            'profile': 'standard',
            'installed_packages': ['json', 'lpeg', 'luasocket'],
            'failed_packages': [],
            'total_packages': 3
        }
        mock_vm.install_package.return_value = True
        mock_vm.session_active = True
        mock_xcpng_class.return_value = mock_vm
        
        # Create XCP-ng VM
        vm = self.vm_manager.create_vm('bioxen-compute', vm_type='xcpng', config=self.xcpng_config)
        
        # Simulate BioXen package setup workflow
        setup_result = vm.setup_packages('standard')
        self.assertTrue(setup_result['success'])
        self.assertEqual(len(setup_result['installed_packages']), 3)
        
        # Install biological computing specific packages
        bio_packages = ['penlight', 'lfs']  # Packages BioXen might need
        for package in bio_packages:
            result = vm.install_package(package)
            self.assertTrue(result)
    
    def test_configuration_management_for_bioxen(self):
        """Test configuration management suitable for BioXen deployment"""
        # Test BioXen-specific configuration
        bioxen_config = XCPngConfig(config_dict={
            'xcp_host': 'bioxen-cluster.lab.local',
            'xcp_username': 'bioxen_admin',
            'xcp_password': 'bioxen_secure_2025',
            'template_name': 'bioxen-bioinformatics-template',
            'vm_username': 'bioxen',
            'memory': '8GB',  # Larger memory for biological data
            'vcpus': 8,       # More CPUs for computational biology
            'vm_network': 'bioxen-secure-network'
        })
        
        # Validate configuration
        self.assertTrue(bioxen_config.validate())
        
        # Test template generation for different BioXen workloads
        dev_config = VMConfigTemplate.create_development_vm_config('bioxen-dev', bioxen_config)
        prod_config = VMConfigTemplate.create_production_vm_config('bioxen-prod', bioxen_config)
        
        self.assertEqual(dev_config['memory'], '4GB')
        self.assertEqual(prod_config['memory'], '8GB')
        self.assertIn('bioxen-dev', dev_config['vm_name'])
        self.assertIn('bioxen-prod', prod_config['vm_name'])
    
    @patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM')
    def test_bioxen_distributed_computing_scenario(self, mock_xcpng_class):
        """Test distributed computing scenario typical of BioXen workflows"""
        # Setup multiple mock VMs for distributed computing
        mock_vms = []
        for i in range(3):
            mock_vm = Mock()
            mock_vm.vm_id = f'bioxen-worker-{i+1}'
            mock_vm.session_active = True
            mock_vm.execute_string.return_value = {
                'stdout': f'Worker {i+1} analysis complete', 
                'stderr': ''
            }
            mock_vms.append(mock_vm)
        
        mock_xcpng_class.side_effect = mock_vms
        
        # Create distributed computing cluster
        worker_vms = []
        for i in range(3):
            vm = self.vm_manager.create_vm(
                f'bioxen-worker-{i+1}', 
                vm_type='xcpng', 
                config=self.xcpng_config
            )
            worker_vms.append(vm)
        
        # Simulate distributed biological analysis
        analysis_tasks = [
            "-- Analyze chromosome 1",
            "-- Analyze chromosome 2", 
            "-- Analyze chromosome 3"
        ]
        
        results = []
        for i, (vm, task) in enumerate(zip(worker_vms, analysis_tasks)):
            result = vm.execute_string(task)
            results.append(result)
            self.assertIn(f'Worker {i+1} analysis complete', result['stdout'])
        
        # Verify all workers completed
        self.assertEqual(len(results), 3)
        self.assertEqual(len(self.vm_manager.vms), 3)
    
    def test_bioxen_vm_health_monitoring(self):
        """Test VM health monitoring for BioXen operational needs"""
        # Create basic VM for health testing
        vm = self.vm_manager.create_vm('bioxen-health-test', vm_type='basic')
        
        # Test health check functionality
        health_info = vm.check_environment_health()
        
        self.assertIn('vm_info', health_info)
        self.assertIn('system_health', health_info)
        self.assertEqual(health_info['vm_info']['name'], 'bioxen-health-test')
    
    @patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM')
    def test_bioxen_error_handling_and_recovery(self, mock_xcpng_class):
        """Test error handling scenarios for BioXen robustness"""
        # Test VM creation with invalid configuration
        invalid_config = {'xcp_host': 'invalid-host'}
        
        with self.assertRaises(ValueError):
            self.vm_manager.create_vm('bioxen-invalid', vm_type='xcpng', config=invalid_config)
        
        # Test graceful degradation - fallback to basic VM
        try:
            # Try XCP-ng first
            vm = self.vm_manager.create_vm('bioxen-fallback', vm_type='xcpng', config=invalid_config)
        except ValueError:
            # Fallback to basic VM
            vm = self.vm_manager.create_vm('bioxen-fallback', vm_type='basic')
        
        self.assertIn('bioxen-fallback', self.vm_manager.vms)
        
        # Verify basic functionality still works
        result = vm.execute_string('print("Fallback VM operational")')
        self.assertIn('Fallback VM operational', result['stdout'])
    
    def test_bioxen_performance_considerations(self):
        """Test performance aspects important for BioXen workflows"""
        # Create multiple VMs to test resource management
        vm_count = 5
        vms = []
        
        for i in range(vm_count):
            vm = self.vm_manager.create_vm(f'bioxen-perf-{i}', vm_type='basic')
            vms.append(vm)
        
        # Verify VM manager can handle multiple VMs
        self.assertEqual(len(self.vm_manager.vms), vm_count)
        
        # Test concurrent execution (simulate biological data processing)
        import threading
        import time
        
        def process_biological_data(vm, data_id):
            """Simulate biological data processing"""
            code = f'''
            -- Simulate processing biological dataset {data_id}
            local start_time = os.clock()
            local data_size = {data_id * 1000}
            local processed = 0
            for i = 1, data_size do
                processed = processed + 1
            end
            local end_time = os.clock()
            print("Processed dataset {data_id}: " .. processed .. " items in " .. (end_time - start_time) .. " seconds")
            '''
            return vm.execute_string(code)
        
        # Process multiple datasets concurrently
        threads = []
        results = {}
        
        for i, vm in enumerate(vms):
            thread = threading.Thread(
                target=lambda v, idx: results.update({idx: process_biological_data(v, idx)}),
                args=(vm, i)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all processing to complete
        for thread in threads:
            thread.join()
        
        # Verify all datasets were processed
        self.assertEqual(len(results), vm_count)
        for i in range(vm_count):
            self.assertIn('stdout', results[i])
            self.assertIn(f'Processed dataset {i}', results[i]['stdout'])


class TestBioXenLuaVMXCPngAdvanced(unittest.TestCase):
    """Advanced XCP-ng integration tests for BioXen-luavm"""
    
    def setUp(self):
        self.xcpng_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'bioxen-template',
            'vm_username': 'bioxen'
        }
    
    @patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM')
    def test_bioxen_vm_lifecycle_management(self, mock_xcpng_class):
        """Test complete VM lifecycle for BioXen workflows"""
        mock_vm = Mock()
        mock_vm.start.return_value = None
        mock_vm.stop.return_value = None
        mock_vm.session_active = False
        mock_vm.get_vm_info.return_value = {
            'vm_id': 'bioxen-lifecycle',
            'vm_type': 'xcpng',
            'session_active': False
        }
        mock_xcpng_class.return_value = mock_vm
        
        vm_manager = VMManager()
        
        # Create VM
        vm = vm_manager.create_vm('bioxen-lifecycle', vm_type='xcpng', config=self.xcpng_config)
        self.assertIsNotNone(vm)
        
        # Start VM
        vm.start()
        mock_vm.start.assert_called_once()
        
        # Get VM info
        info = vm.get_vm_info()
        self.assertEqual(info['vm_id'], 'bioxen-lifecycle')
        
        # Stop VM
        vm.stop()
        mock_vm.stop.assert_called_once()
    
    def test_bioxen_configuration_validation(self):
        """Test configuration validation for BioXen deployments"""
        # Valid BioXen configuration
        valid_config = XCPngConfig(config_dict={
            'xcp_host': 'bioxen-xcp.local',
            'xcp_username': 'admin',
            'xcp_password': 'secure_pass',
            'template_name': 'bioxen-compute-template',
            'vm_username': 'bioxen',
            'memory': '16GB',
            'vcpus': 16
        })
        
        self.assertTrue(valid_config.validate())
        
        # Test configuration sections
        xcp_config = valid_config.get_xcp_connection_config()
        vm_config = valid_config.get_vm_config()
        ssh_config = valid_config.get_ssh_config()
        
        self.assertEqual(xcp_config['xcp_host'], 'bioxen-xcp.local')
        self.assertEqual(vm_config['memory'], '16GB')
        self.assertEqual(ssh_config['vm_username'], 'bioxen')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
