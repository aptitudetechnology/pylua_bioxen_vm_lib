"""
XCP-ng VM implementation with interactive session support
Integrates XAPI client and SSH session manager for remote VM management
"""

import time
import os
from typing import Dict, Any, Optional

from .xapi_client import XAPIClient
from .ssh_session import SSHSessionManager
from .exceptions import VMManagerError, InteractiveSessionError, XCPngConnectionError
try:
    from .utils.curator import Curator
except ImportError:
    # Create a placeholder Curator for Phase 1 testing
    class Curator:
        def __init__(self, *args, **kwargs):
            pass
        def install_packages(self, *args, **kwargs):
            return True


class XCPngVM:
    """XCP-ng VM with interactive session support via XAPI and SSH"""
    
    def __init__(self, vm_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize XCP-ng VM
        
        Args:
            vm_id: Unique identifier for this VM
            config: Configuration dictionary containing:
                - xcp_host: XCP-ng host IP/hostname
                - xcp_username: XCP-ng username  
                - xcp_password: XCP-ng password
                - template_name: VM template name
                - vm_username: VM SSH username
                - vm_password: VM SSH password (optional)
                - vm_key_file: VM SSH key file (optional)
                - vm_config: Additional VM configuration
        """
        self.vm_id = vm_id
        self.config = config or {}
        
        # Validate required configuration
        required_keys = ['xcp_host', 'xcp_username', 'xcp_password', 'template_name']
        for key in required_keys:
            if key not in self.config:
                raise VMManagerError(f"Missing required configuration: {key}")
        
        # XCP-ng connection
        self.xapi_client = XAPIClient(
            host=self.config['xcp_host'],
            username=self.config['xcp_username'],
            password=self.config['xcp_password']
        )
        
        # VM state
        self.vm_uuid = None
        self.vm_ip = None
        self.ssh_session = None
        self.session_active = False
        
        # Package curator for SSH-based package management
        self.curator = None
    
    def start(self):
        """Start the XCP-ng VM and establish SSH session
        
        Raises:
            VMManagerError: If VM creation or startup fails
            InteractiveSessionError: If SSH session fails
        """
        try:
            # Authenticate with XCP-ng
            if not self.xapi_client.authenticate():
                raise XCPngConnectionError("Failed to authenticate with XCP-ng")
            
            # Create VM from template
            vm_name = f"{self.vm_id}_lua_vm"
            template_name = self.config['template_name']
            vm_config = self.config.get('vm_config', {})
            
            self.vm_uuid = self.xapi_client.create_vm_from_template(
                vm_name=vm_name,
                template_name=template_name,
                config=vm_config
            )
            
            # Start the VM
            if not self.xapi_client.start_vm(self.vm_uuid):
                raise VMManagerError(f"Failed to start VM {self.vm_uuid}")
            
            # Wait for VM to get IP address
            self._wait_for_network(timeout=180)
            
            # Establish SSH connection
            self._establish_ssh_connection()
            
            # Start Lua session
            if not self.ssh_session.start_lua_session():
                raise InteractiveSessionError("Failed to start Lua interpreter")
            
            self.session_active = True
            
            # Initialize package curator for SSH-based operations
            self._initialize_curator()
            
        except Exception as e:
            # Cleanup on failure
            self._cleanup()
            raise
    
    def stop(self):
        """Stop the VM and cleanup resources"""
        self._cleanup()
    
    def send_input(self, input_text: str) -> bool:
        """Send input to interactive Lua session
        
        Args:
            input_text: Text to send to Lua interpreter
            
        Returns:
            bool: True if input sent successfully
            
        Raises:
            InteractiveSessionError: If no active session or send fails
        """
        if not self.session_active:
            raise InteractiveSessionError("No active session")
        
        try:
            return self.ssh_session.send_input(input_text)
        except Exception as e:
            raise InteractiveSessionError(f"Failed to send input: {e}")
    
    def read_output(self, timeout: float = 1.0) -> str:
        """Read output from interactive Lua session
        
        Args:
            timeout: Maximum time to wait for output
            
        Returns:
            str: Output from Lua interpreter
            
        Raises:
            InteractiveSessionError: If no active session or read fails
        """
        if not self.session_active:
            raise InteractiveSessionError("No active session")
        
        try:
            return self.ssh_session.read_output(timeout)
        except Exception as e:
            raise InteractiveSessionError(f"Failed to read output: {e}")
    
    def execute_string(self, lua_code: str) -> Dict[str, str]:
        """Execute Lua code and return result (for compatibility)
        
        Args:
            lua_code: Lua code to execute
            
        Returns:
            Dictionary with 'stdout' and 'stderr' keys
        """
        if not self.session_active:
            self.start()
        
        try:
            self.send_input(lua_code + "\n")
            time.sleep(0.1)  # Brief wait for execution
            output = self.read_output()
            
            return {"stdout": output, "stderr": ""}
            
        except Exception as e:
            return {"stdout": "", "stderr": str(e)}
    
    def install_package(self, package_name: str) -> bool:
        """Install package using curator over SSH
        
        Args:
            package_name: Name of package to install
            
        Returns:
            bool: True if installation successful
        """
        if not self.session_active:
            raise InteractiveSessionError("No active session")
        
        try:
            # Use SSH to execute luarocks install
            install_cmd = f"luarocks install {package_name}"
            
            # Execute via SSH session
            self.send_input(f"os.execute('{install_cmd}')")
            time.sleep(2)  # Wait for installation
            output = self.read_output(timeout=30)
            
            # Check if installation was successful
            return "successfully installed" in output.lower() or "is now installed" in output.lower()
            
        except Exception as e:
            raise InteractiveSessionError(f"Failed to install package {package_name}: {e}")
    
    def get_vm_info(self) -> Dict[str, Any]:
        """Get VM information
        
        Returns:
            Dictionary with VM information
        """
        info = {
            'vm_id': self.vm_id,
            'vm_uuid': self.vm_uuid,
            'vm_ip': self.vm_ip,
            'session_active': self.session_active,
            'vm_type': 'xcpng'
        }
        
        if self.vm_uuid:
            try:
                xcp_info = self.xapi_client.get_vm_info(self.vm_uuid)
                info['xcp_info'] = xcp_info
            except:
                pass
        
        return info
    
    def _wait_for_network(self, timeout: int = 180):
        """Wait for VM to get network connectivity
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Raises:
            VMManagerError: If network is not available within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                network_info = self.xapi_client.get_vm_network_info(self.vm_uuid)
                ip_address = network_info.get('ip_address')
                
                if ip_address and not ip_address.startswith('127.'):
                    self.vm_ip = ip_address
                    return
                    
            except Exception:
                pass
            
            time.sleep(5)
        
        raise VMManagerError(f"VM {self.vm_uuid} did not get IP address within {timeout} seconds")
    
    def _establish_ssh_connection(self):
        """Establish SSH connection to VM
        
        Raises:
            InteractiveSessionError: If SSH connection fails
        """
        if not self.vm_ip:
            raise InteractiveSessionError("VM IP address not available")
        
        # Get SSH credentials
        vm_username = self.config.get('vm_username', 'root')
        vm_password = self.config.get('vm_password')
        vm_key_file = self.config.get('vm_key_file')
        
        if not vm_password and not vm_key_file:
            raise InteractiveSessionError("No SSH authentication method provided")
        
        # Create SSH session
        self.ssh_session = SSHSessionManager(
            host=self.vm_ip,
            username=vm_username,
            password=vm_password,
            key_file=vm_key_file
        )
        
        # Connect with retries
        max_retries = 10
        for attempt in range(max_retries):
            try:
                if self.ssh_session.connect():
                    return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise InteractiveSessionError(f"Failed to establish SSH connection after {max_retries} attempts: {e}")
                time.sleep(10)  # Wait before retry
    
    def _initialize_curator(self):
        """Initialize package curator for SSH-based operations"""
        try:
            # Create a curator instance that can work over SSH
            self.curator = Curator()
            # Note: curator methods would need to be adapted to work over SSH
            # For now, we use direct luarocks commands via SSH
        except Exception:
            # Curator is optional
            pass
    
    def _cleanup(self):
        """Cleanup VM and connections"""
        try:
            # Close SSH session
            if self.ssh_session:
                self.ssh_session.disconnect()
                self.ssh_session = None
            
            # Stop and delete VM
            if self.vm_uuid and self.xapi_client:
                try:
                    self.xapi_client.delete_vm(self.vm_uuid)
                except:
                    pass  # Ignore cleanup errors
            
            # Disconnect XAPI client
            if self.xapi_client:
                self.xapi_client.disconnect()
            
            self.session_active = False
            
        except Exception:
            pass  # Ignore cleanup errors
    
    # ==================== COMPATIBILITY METHODS ====================
    # These methods ensure XCPngVM is compatible with existing LuaProcess interface
    # for seamless integration with BioXen-luavm project
    
    @property
    def name(self) -> str:
        """Get VM name (compatibility with LuaProcess.name)"""
        return self.vm_id
    
    def is_interactive_running(self) -> bool:
        """Check if interactive session is running (compatibility)"""
        return self.session_active
    
    def setup_packages(self, profile: str = 'standard') -> dict:
        """Setup packages using curator-like interface (compatibility)"""
        if not self.session_active:
            raise InteractiveSessionError("No active session")
        
        # Simulate curator package setup over SSH
        packages_to_install = {
            'minimal': ['json'],
            'standard': ['json', 'lpeg', 'luasocket'],
            'full': ['json', 'lpeg', 'luasocket', 'lfs', 'penlight']
        }
        
        target_packages = packages_to_install.get(profile, packages_to_install['standard'])
        installed_packages = []
        failed_packages = []
        
        for package in target_packages:
            try:
                if self.install_package(package):
                    installed_packages.append(package)
                else:
                    failed_packages.append(package)
            except Exception:
                failed_packages.append(package)
        
        return {
            'success': len(failed_packages) == 0,
            'profile': profile,
            'installed_packages': installed_packages,
            'failed_packages': failed_packages,
            'total_packages': len(target_packages),
            'curator_recommendations': []
        }
    
    def get_package_recommendations(self) -> list:
        """Get package recommendations (compatibility)"""
        # Basic recommendations for biological computing
        return [
            {
                'name': 'json',
                'description': 'JSON encoding/decoding',
                'rationale': 'Essential for data interchange in biological workflows'
            },
            {
                'name': 'luasocket',
                'description': 'Network communication',
                'rationale': 'Required for distributed biological computing'
            }
        ]
    
    def check_environment_health(self) -> dict:
        """Check environment health (compatibility)"""
        health_info = {
            'vm_info': {
                'name': self.vm_id,
                'type': 'xcpng',
                'session_active': self.session_active,
                'vm_uuid': self.vm_uuid,
                'vm_ip': self.vm_ip
            },
            'system_health': 'healthy' if self.session_active else 'inactive',
            'package_manager': 'luarocks',
            'curator_available': self.curator is not None
        }
        
        if self.session_active:
            try:
                # Test basic Lua functionality
                result = self.execute_string('print("health_check")')
                health_info['lua_responsive'] = 'health_check' in result.get('stdout', '')
            except:
                health_info['lua_responsive'] = False
        
        return health_info
    
    def execute_file(self, script_path: str) -> dict:
        """Execute Lua file (compatibility with LuaProcess)"""
        if not self.session_active:
            self.start()
        
        try:
            # Read file content (assuming local file for now)
            with open(script_path, 'r') as f:
                lua_code = f.read()
            
            return self.execute_string(lua_code)
        except Exception as e:
            return {'stdout': '', 'stderr': f'File execution error: {str(e)}'}
    
    def cleanup_temp_files(self):
        """Cleanup temporary files (compatibility)"""
        # For XCP-ng VMs, temp files would be on the remote VM
        # This could be enhanced to clean up remote temp files via SSH
        pass
