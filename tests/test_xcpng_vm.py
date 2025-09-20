"""
Tests for XCPngVM basic functionality (Phase 1)
Focuses on VM lifecycle, SSH communication, and package management
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time

from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
from pylua_bioxen_vm_lib.exceptions import VMManagerError, InteractiveSessionError, XCPngConnectionError


class TestXCPngVMBasicFunctionality(unittest.TestCase):
    """Test XCPngVM basic operations"""
    
    def setUp(self):
        self.test_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test',
            'vm_password': 'testpass'
        }
        self.vm = XCPngVM('test-vm', self.test_config)
    
    def test_vm_initialization(self):
        """Test XCPngVM proper initialization"""
        self.assertEqual(self.vm.vm_id, 'test-vm')
        self.assertIsNone(self.vm.vm_uuid)
        self.assertIsNone(self.vm.vm_ip)
        self.assertIsNone(self.vm.ssh_session)
        self.assertFalse(self.vm.session_active)
        self.assertIsNotNone(self.vm.xapi_client)
    
    @patch.object(XCPngVM, '_initialize_curator')
    @patch.object(XCPngVM, '_establish_ssh_connection')
    @patch.object(XCPngVM, '_wait_for_network')
    def test_vm_start_success(self, mock_wait_network, mock_ssh_conn, mock_curator):
        """Test successful VM start sequence"""
        # Mock XAPI client methods
        self.vm.xapi_client.authenticate = Mock(return_value=True)
        self.vm.xapi_client.create_vm_from_template = Mock(return_value='test-uuid-123')
        self.vm.xapi_client.start_vm = Mock(return_value=True)
        
        # Mock SSH session
        mock_ssh_session = Mock()
        mock_ssh_session.start_lua_session = Mock(return_value=True)
        self.vm.ssh_session = mock_ssh_session
        
        # Execute start
        self.vm.start()
        
        # Verify state
        self.assertTrue(self.vm.session_active)
        self.assertEqual(self.vm.vm_uuid, 'test-uuid-123')
        
        # Verify method calls
        self.vm.xapi_client.authenticate.assert_called_once()
        self.vm.xapi_client.create_vm_from_template.assert_called_once()
        self.vm.xapi_client.start_vm.assert_called_once()
        mock_wait_network.assert_called_once()
        mock_ssh_conn.assert_called_once()
        mock_curator.assert_called_once()
    
    def test_vm_start_authentication_failure(self):
        """Test VM start failure due to authentication"""
        self.vm.xapi_client.authenticate = Mock(return_value=False)
        
        with self.assertRaises(XCPngConnectionError):
            self.vm.start()
        
        self.assertFalse(self.vm.session_active)
    
    def test_vm_start_vm_creation_failure(self):
        """Test VM start failure during VM creation"""
        self.vm.xapi_client.authenticate = Mock(return_value=True)
        self.vm.xapi_client.create_vm_from_template = Mock(return_value=None)
        
        with self.assertRaises(VMManagerError):
            self.vm.start()
    
    @patch.object(XCPngVM, '_cleanup')
    def test_vm_stop(self, mock_cleanup):
        """Test VM stop operation"""
        self.vm.stop()
        mock_cleanup.assert_called_once()
    
    def test_send_input_no_session(self):
        """Test send_input fails without active session"""
        with self.assertRaises(InteractiveSessionError):
            self.vm.send_input("print('hello')")
    
    def test_read_output_no_session(self):
        """Test read_output fails without active session"""
        with self.assertRaises(InteractiveSessionError):
            self.vm.read_output()
    
    def test_send_input_with_session(self):
        """Test send_input with active session"""
        # Setup mock SSH session
        mock_ssh = Mock()
        mock_ssh.send_input = Mock(return_value=True)
        self.vm.ssh_session = mock_ssh
        self.vm.session_active = True
        
        result = self.vm.send_input("print('test')")
        
        self.assertTrue(result)
        mock_ssh.send_input.assert_called_once_with("print('test')")
    
    def test_read_output_with_session(self):
        """Test read_output with active session"""
        # Setup mock SSH session
        mock_ssh = Mock()
        mock_ssh.read_output = Mock(return_value="test output")
        self.vm.ssh_session = mock_ssh
        self.vm.session_active = True
        
        result = self.vm.read_output(timeout=2.0)
        
        self.assertEqual(result, "test output")
        mock_ssh.read_output.assert_called_once_with(2.0)
    
    def test_execute_string_autostart(self):
        """Test execute_string auto-starts VM if not active"""
        # Mock start method
        self.vm.start = Mock()
        self.vm.send_input = Mock()
        self.vm.read_output = Mock(return_value="test output")
        
        result = self.vm.execute_string("print('hello')")
        
        # Should auto-start
        self.vm.start.assert_called_once()
        
        # Should return proper format
        self.assertIn('stdout', result)
        self.assertIn('stderr', result)
        self.assertEqual(result['stdout'], 'test output')
    
    def test_execute_string_with_active_session(self):
        """Test execute_string with already active session"""
        self.vm.session_active = True
        self.vm.send_input = Mock()
        self.vm.read_output = Mock(return_value="hello")
        
        result = self.vm.execute_string("print('hello')")
        
        self.vm.send_input.assert_called_once_with("print('hello')\n")
        self.assertEqual(result['stdout'], 'hello')
        self.assertEqual(result['stderr'], '')
    
    def test_execute_string_exception_handling(self):
        """Test execute_string handles exceptions properly"""
        self.vm.session_active = True
        self.vm.send_input = Mock(side_effect=Exception("Test error"))
        
        result = self.vm.execute_string("print('hello')")
        
        self.assertEqual(result['stdout'], '')
        self.assertIn('Test error', result['stderr'])


class TestXCPngVMPackageManagement(unittest.TestCase):
    """Test XCPngVM package management functionality"""
    
    def setUp(self):
        self.test_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test'
        }
        self.vm = XCPngVM('test-vm', self.test_config)
    
    def test_install_package_no_session(self):
        """Test install_package fails without active session"""
        with self.assertRaises(InteractiveSessionError):
            self.vm.install_package('json')
    
    def test_install_package_success(self):
        """Test successful package installation"""
        self.vm.session_active = True
        self.vm.send_input = Mock()
        self.vm.read_output = Mock(return_value="json successfully installed")
        
        result = self.vm.install_package('json')
        
        self.assertTrue(result)
        self.vm.send_input.assert_called_once_with("os.execute('luarocks install json')")
    
    def test_install_package_failure(self):
        """Test package installation failure"""
        self.vm.session_active = True
        self.vm.send_input = Mock()
        self.vm.read_output = Mock(return_value="Error: Could not find package")
        
        result = self.vm.install_package('nonexistent-package')
        
        self.assertFalse(result)
    
    def test_install_package_exception(self):
        """Test package installation exception handling"""
        self.vm.session_active = True
        self.vm.send_input = Mock(side_effect=Exception("SSH error"))
        
        with self.assertRaises(InteractiveSessionError):
            self.vm.install_package('json')


class TestXCPngVMNetworking(unittest.TestCase):
    """Test XCPngVM networking functionality"""
    
    def setUp(self):
        self.test_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test'
        }
        self.vm = XCPngVM('test-vm', self.test_config)
        self.vm.vm_uuid = 'test-uuid-123'
    
    @patch('time.sleep')  # Speed up test
    def test_wait_for_network_success(self, mock_sleep):
        """Test successful network wait"""
        # Mock XAPI client to return IP address
        self.vm.xapi_client.get_vm_network_info = Mock()
        self.vm.xapi_client.get_vm_network_info.side_effect = [
            {'ip_address': None},  # First call: no IP
            {'ip_address': '127.0.0.1'},  # Second call: localhost (should be ignored)
            {'ip_address': '192.168.1.200'}  # Third call: valid IP
        ]
        
        self.vm._wait_for_network(timeout=60)
        
        self.assertEqual(self.vm.vm_ip, '192.168.1.200')
        self.assertEqual(self.vm.xapi_client.get_vm_network_info.call_count, 3)
    
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_network_timeout(self, mock_time, mock_sleep):
        """Test network wait timeout"""
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 61, 122]  # Start, first check, timeout
        
        self.vm.xapi_client.get_vm_network_info = Mock(return_value={'ip_address': None})
        
        with self.assertRaises(VMManagerError):
            self.vm._wait_for_network(timeout=60)


class TestXCPngVMInfo(unittest.TestCase):
    """Test XCPngVM information methods"""
    
    def setUp(self):
        self.test_config = {
            'xcp_host': '192.168.1.100',
            'xcp_username': 'root',
            'xcp_password': 'testpass',
            'template_name': 'test-template',
            'vm_username': 'test'
        }
        self.vm = XCPngVM('test-vm', self.test_config)
    
    def test_get_vm_info_basic(self):
        """Test basic VM info retrieval"""
        self.vm.vm_uuid = 'test-uuid-123'
        self.vm.vm_ip = '192.168.1.200'
        self.vm.session_active = True
        
        info = self.vm.get_vm_info()
        
        expected_keys = ['vm_id', 'vm_uuid', 'vm_ip', 'session_active', 'vm_type']
        for key in expected_keys:
            self.assertIn(key, info)
        
        self.assertEqual(info['vm_id'], 'test-vm')
        self.assertEqual(info['vm_uuid'], 'test-uuid-123')
        self.assertEqual(info['vm_ip'], '192.168.1.200')
        self.assertTrue(info['session_active'])
        self.assertEqual(info['vm_type'], 'xcpng')
    
    def test_get_vm_info_with_xcp_info(self):
        """Test VM info with XCP-ng details"""
        self.vm.vm_uuid = 'test-uuid-123'
        self.vm.xapi_client.get_vm_info = Mock(return_value={
            'name': 'test-vm',
            'memory': '2GB',
            'vcpus': 2,
            'power_state': 'Running'
        })
        
        info = self.vm.get_vm_info()
        
        self.assertIn('xcp_info', info)
        self.assertEqual(info['xcp_info']['name'], 'test-vm')
        self.assertEqual(info['xcp_info']['power_state'], 'Running')
    
    def test_get_vm_info_xcp_error(self):
        """Test VM info when XCP-ng info fails"""
        self.vm.vm_uuid = 'test-uuid-123'
        self.vm.xapi_client.get_vm_info = Mock(side_effect=Exception("XAPI error"))
        
        info = self.vm.get_vm_info()
        
        # Should not include xcp_info on error
        self.assertNotIn('xcp_info', info)
        # But should still have basic info
        self.assertEqual(info['vm_id'], 'test-vm')


if __name__ == '__main__':
    unittest.main()
