"""
Phase 1 foundational tests for XCP-ng integration
Tests core XAPI client, XCPngVM basic functionality, and configuration management
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from pathlib import Path

from pylua_bioxen_vm_lib.xcp_ng_config import XCPngConfig, VMConfigTemplate
from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
from pylua_bioxen_vm_lib.xapi_client import XAPIClient
from pylua_bioxen_vm_lib.vm_manager import VMManager
from pylua_bioxen_vm_lib.exceptions import VMManagerError, XCPngConnectionError


class TestXCPngConfiguration(unittest.TestCase):
    """Test XCP-ng configuration management"""
    
    def setUp(self):
        self.test_config_dict = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test',
            'memory': '4GB',
            'vcpus': 4
        }
    
    def test_config_initialization_with_dict(self):
        """Test configuration initialization with dictionary"""
        config = XCPngConfig(config_dict=self.test_config_dict)
        
        self.assertEqual(config.get('xcp_host'), '192.168.1.100')
        self.assertEqual(config.get('memory'), '4GB')
        self.assertEqual(config.get('vcpus'), 4)
    
    def test_config_initialization_with_file(self):
        """Test configuration initialization with file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config_dict, f)
            temp_file = f.name
        
        try:
            config = XCPngConfig(config_file=temp_file)
            self.assertEqual(config.get('xcp_host'), '192.168.1.100')
        finally:
            os.unlink(temp_file)
    
    def test_config_validation_success(self):
        """Test successful configuration validation"""
        config = XCPngConfig(config_dict=self.test_config_dict)
        self.assertTrue(config.validate())
    
    def test_config_validation_failure(self):
        """Test configuration validation failure"""
        incomplete_config = {'xcp_host': '192.168.1.100'}  # Missing required fields
        config = XCPngConfig(config_dict=incomplete_config)
        
        with self.assertRaises(VMManagerError):
            config.validate()
    
    def test_config_sections(self):
        """Test configuration section extraction"""
        config = XCPngConfig(config_dict=self.test_config_dict)
        
        xcp_config = config.get_xcp_connection_config()
        self.assertIn('xcp_host', xcp_config)
        self.assertIn('xcp_username', xcp_config)
        
        vm_config = config.get_vm_config()
        self.assertIn('template_name', vm_config)
        self.assertIn('memory', vm_config)
        
        ssh_config = config.get_ssh_config()
        self.assertIn('vm_username', ssh_config)
    
    def test_vm_config_templates(self):
        """Test VM configuration templates"""
        config = XCPngConfig(config_dict=self.test_config_dict)
        
        basic_config = VMConfigTemplate.create_basic_vm_config('test-vm', config)
        self.assertIn('vm_name', basic_config)
        self.assertEqual(basic_config['template_name'], 'test-template')
        
        dev_config = VMConfigTemplate.create_development_vm_config('test-vm', config)
        self.assertEqual(dev_config['memory'], '4GB')
        
        prod_config = VMConfigTemplate.create_production_vm_config('test-vm', config)
        self.assertEqual(prod_config['memory'], '8GB')


class TestXAPIClientIntegration(unittest.TestCase):
    """Test XAPI client basic functionality"""
    
    def setUp(self):
        self.client = XAPIClient('test-host', 'test-user', 'test-pass')
    
    @patch('requests.Session.post')
    def test_authentication_success(self, mock_post):
        """Test successful XAPI authentication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'session_id': 'test-session-123'}
        mock_post.return_value = mock_response
        
        result = self.client.authenticate()
        self.assertTrue(result)
        self.assertEqual(self.client.session_id, 'test-session-123')
    
    @patch('requests.Session.post')
    def test_authentication_failure(self, mock_post):
        """Test XAPI authentication failure"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = self.client.authenticate()
        self.assertFalse(result)
        self.assertIsNone(self.client.session_id)
    
    def test_client_initialization(self):
        """Test XAPI client initialization"""
        self.assertEqual(self.client.host, 'test-host')
        self.assertEqual(self.client.username, 'test-user')
        self.assertFalse(self.client.verify_ssl)
        self.assertIsNone(self.client.session_id)


class TestXCPngVMBasics(unittest.TestCase):
    """Test XCPngVM basic functionality"""
    
    def setUp(self):
        self.test_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test'
        }
    
    def test_xcpng_vm_initialization(self):
        """Test XCPngVM initialization"""
        vm = XCPngVM('test-vm', self.test_config)
        
        self.assertEqual(vm.vm_id, 'test-vm')
        self.assertEqual(vm.config['xcp_host'], '192.168.1.100')
        self.assertFalse(vm.session_active)
        self.assertIsNone(vm.vm_uuid)
    
    def test_xcpng_vm_missing_config(self):
        """Test XCPngVM initialization with missing config"""
        incomplete_config = {'xcp_host': '192.168.1.100'}  # Missing required fields
        
        with self.assertRaises(VMManagerError):
            XCPngVM('test-vm', incomplete_config)
    
    @patch.object(XCPngVM, '_establish_ssh_connection')
    @patch.object(XCPngVM, '_wait_for_network')
    @patch('pylua_bioxen_vm_lib.xcp_ng_integration.XAPIClient')
    def test_xcpng_vm_start_sequence(self, mock_xapi_class, mock_wait_network, mock_ssh):
        """Test XCPngVM start sequence"""
        # Setup mocks
        mock_xapi = Mock()
        mock_xapi.authenticate.return_value = True
        mock_xapi.create_vm_from_template.return_value = 'test-uuid-123'
        mock_xapi.start_vm.return_value = True
        mock_xapi_class.return_value = mock_xapi
        
        mock_wait_network.return_value = None  # Successful network wait
        
        mock_ssh_session = Mock()
        mock_ssh_session.start_lua_session.return_value = True
        
        vm = XCPngVM('test-vm', self.test_config)
        vm.ssh_session = mock_ssh_session
        
        # Test start sequence
        vm.start()
        
        # Verify calls
        mock_xapi.authenticate.assert_called_once()
        mock_xapi.create_vm_from_template.assert_called_once()
        mock_xapi.start_vm.assert_called_once_with('test-uuid-123')
        mock_wait_network.assert_called_once()
        mock_ssh.assert_called_once()
        
        self.assertTrue(vm.session_active)
        self.assertEqual(vm.vm_uuid, 'test-uuid-123')
    
    def test_xcpng_vm_get_info(self):
        """Test XCPngVM get_vm_info"""
        vm = XCPngVM('test-vm', self.test_config)
        vm.vm_uuid = 'test-uuid-123'
        vm.vm_ip = '192.168.1.200'
        vm.session_active = True
        
        info = vm.get_vm_info()
        
        self.assertEqual(info['vm_id'], 'test-vm')
        self.assertEqual(info['vm_uuid'], 'test-uuid-123')
        self.assertEqual(info['vm_ip'], '192.168.1.200')
        self.assertTrue(info['session_active'])
        self.assertEqual(info['vm_type'], 'xcpng')


class TestVMManagerFactoryPattern(unittest.TestCase):
    """Test VM manager factory pattern for VM type selection"""
    
    def setUp(self):
        self.manager = VMManager(max_workers=2, debug_mode=True)
    
    def test_create_basic_vm(self):
        """Test creating basic VM through factory"""
        vm = self.manager.create_vm('test-basic', vm_type='basic')
        
        self.assertIn('test-basic', self.manager.vms)
        self.assertEqual(vm.name, 'test-basic')
    
    def test_create_networked_basic_vm(self):
        """Test creating networked basic VM"""
        vm = self.manager.create_vm('test-networked', vm_type='basic', networked=True)
        
        self.assertIn('test-networked', self.manager.vms)
        # Should be NetworkedLuaVM instance
        from pylua_bioxen_vm_lib.networking import NetworkedLuaVM
        self.assertIsInstance(vm, NetworkedLuaVM)
    
    @patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM')
    def test_create_xcpng_vm(self, mock_xcpng_class):
        """Test creating XCP-ng VM through factory"""
        mock_vm = Mock()
        mock_xcpng_class.return_value = mock_vm
        
        config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template'
        }
        
        vm = self.manager.create_vm('test-xcpng', vm_type='xcpng', config=config)
        
        self.assertIn('test-xcpng', self.manager.vms)
        mock_xcpng_class.assert_called_once_with('test-xcpng', config)
    
    def test_create_xcpng_vm_missing_config(self):
        """Test XCP-ng VM creation fails without config"""
        with self.assertRaises(ValueError):
            self.manager.create_vm('test-xcpng', vm_type='xcpng')
    
    def test_create_vm_invalid_type(self):
        """Test creating VM with invalid type"""
        with self.assertRaises(ValueError):
            self.manager.create_vm('test-invalid', vm_type='invalid-type')
    
    def test_create_vm_duplicate_id(self):
        """Test creating VM with duplicate ID"""
        self.manager.create_vm('test-duplicate', vm_type='basic')
        
        with self.assertRaises(ValueError):
            self.manager.create_vm('test-duplicate', vm_type='basic')
    
    def test_vm_manager_backward_compatibility(self):
        """Test that VM manager maintains backward compatibility"""
        # Test that existing BioXen-luavm patterns still work
        vm1 = self.manager.create_vm('compat-test-1')  # Default basic type
        vm2 = self.manager.create_vm('compat-test-2', networked=True)  # Networked basic
        
        self.assertIn('compat-test-1', self.manager.vms)
        self.assertIn('compat-test-2', self.manager.vms)
        
        # Verify basic functionality is preserved
        result = vm1.execute_string('print("hello")')
        self.assertIn('stdout', result)


class TestPhase1Integration(unittest.TestCase):
    """Integration tests for Phase 1 components"""
    
    def setUp(self):
        self.manager = VMManager(debug_mode=True)
        self.test_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test'
        }
    
    def test_configuration_to_vm_creation(self):
        """Test full configuration to VM creation workflow"""
        # Create configuration
        config = XCPngConfig(config_dict=self.test_config)
        config.validate()
        
        # Use configuration in VM creation
        with patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM') as mock_xcpng:
            mock_vm = Mock()
            mock_xcpng.return_value = mock_vm
            
            vm = self.manager.create_vm('integration-test', vm_type='xcpng', config=config.to_dict())
            
            self.assertIsNotNone(vm)
            mock_xcpng.assert_called_once_with('integration-test', config.to_dict())
    
    def test_mixed_vm_types_in_manager(self):
        """Test managing both basic and XCP-ng VMs simultaneously"""
        # Create basic VM
        basic_vm = self.manager.create_vm('basic-test', vm_type='basic')
        
        # Create XCP-ng VM (mocked)
        with patch('pylua_bioxen_vm_lib.xcp_ng_integration.XCPngVM') as mock_xcpng:
            mock_vm = Mock()
            mock_xcpng.return_value = mock_vm
            
            xcpng_vm = self.manager.create_vm('xcpng-test', vm_type='xcpng', config=self.test_config)
        
        # Verify both VMs are managed
        self.assertEqual(len(self.manager.vms), 2)
        self.assertIn('basic-test', self.manager.vms)
        self.assertIn('xcpng-test', self.manager.vms)
        
        # Verify VM manager can handle both types
        vm_info = {
            'basic': self.manager.vms['basic-test'],
            'xcpng': self.manager.vms['xcpng-test']
        }
        
        # Both should be manageable through the same interface
        for vm_type, vm in vm_info.items():
            self.assertIsNotNone(vm)


if __name__ == '__main__':
    unittest.main()
