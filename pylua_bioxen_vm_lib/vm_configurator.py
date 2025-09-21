"""
Automated VM Configuration Module
Handles post-deployment configuration without manual console interaction
"""

import time
import socket
import paramiko
import yaml
from typing import Dict, List, Optional, Any
from .exceptions import VMConfigurationError, XCPngConnectionError


class VMConfigurator:
    """Handles automated VM configuration after deployment"""
    
    def __init__(self, xapi_client):
        self.xapi_client = xapi_client
        self.ssh_timeout = 300  # 5 minutes
        self.boot_timeout = 600  # 10 minutes
    
    def create_configured_vm(self, template_uuid: str, vm_name: str, config: Dict[str, Any]) -> str:
        """Create and fully configure a VM automatically
        
        Args:
            template_uuid: Template to use for VM creation
            vm_name: Name for the new VM
            config: Configuration dictionary with user settings
            
        Returns:
            UUID of the configured VM
        """
        # Step 1: Create VM from template
        vm_uuid = self.xapi_client.create_vm_from_template(template_uuid, vm_name)
        
        # Step 2: Choose configuration method based on template type
        if self._is_cloud_ready_template(template_uuid):
            return self._configure_via_cloud_init(vm_uuid, config)
        elif self._has_preseed_support(template_uuid):
            return self._configure_via_preseed(vm_uuid, config)
        else:
            return self._configure_via_ssh(vm_uuid, config)
    
    def _configure_via_cloud_init(self, vm_uuid: str, config: Dict[str, Any]) -> str:
        """Configure VM using cloud-init (preferred method)"""
        
        # Generate cloud-init configuration
        cloud_config = self._generate_cloud_init_config(config)
        
        # Create cloud-init ISO
        iso_path = self._create_cloud_init_iso(vm_uuid, cloud_config)
        
        # Attach ISO to VM
        self._attach_iso_to_vm(vm_uuid, iso_path)
        
        # Start VM - cloud-init will handle configuration
        self.xapi_client.start_vm(vm_uuid)
        
        # Wait for configuration to complete
        self._wait_for_cloud_init_complete(vm_uuid, timeout=self.boot_timeout)
        
        return vm_uuid
    
    def _configure_via_preseed(self, vm_uuid: str, config: Dict[str, Any]) -> str:
        """Configure VM using Debian preseed"""
        
        # Generate preseed configuration
        preseed_config = self._generate_preseed_config(config)
        
        # Create preseed ISO
        iso_path = self._create_preseed_iso(vm_uuid, preseed_config)
        
        # Attach ISO to VM
        self._attach_iso_to_vm(vm_uuid, iso_path)
        
        # Start VM - preseed will handle automated installation
        self.xapi_client.start_vm(vm_uuid)
        
        # Wait for installation to complete
        self._wait_for_preseed_complete(vm_uuid, timeout=self.boot_timeout)
        
        return vm_uuid
    
    def _configure_via_ssh(self, vm_uuid: str, config: Dict[str, Any]) -> str:
        """Configure VM via SSH after first boot (fallback method)"""
        
        # Start VM first
        self.xapi_client.start_vm(vm_uuid)
        
        # Wait for VM to boot and get IP address
        ip_address = self._wait_for_vm_ip(vm_uuid, timeout=self.boot_timeout)
        
        # Wait for SSH service to be available
        self._wait_for_ssh_service(ip_address, timeout=self.ssh_timeout)
        
        # Establish SSH connection
        ssh_client = self._create_ssh_connection(ip_address, config.get('credentials', {}))
        
        try:
            # Perform configuration steps
            self._configure_system_via_ssh(ssh_client, config)
            self._install_lua_environment_via_ssh(ssh_client, config)
            self._configure_bioxen_services_via_ssh(ssh_client, config)
            
        finally:
            ssh_client.close()
        
        return vm_uuid
    
    def _generate_cloud_init_config(self, config: Dict[str, Any]) -> str:
        """Generate cloud-init YAML configuration"""
        
        cloud_config = {
            'users': [
                {
                    'name': config.get('username', 'bioxen'),
                    'sudo': 'ALL=(ALL) NOPASSWD:ALL',
                    'shell': '/bin/bash',
                    'ssh_authorized_keys': config.get('ssh_keys', [])
                }
            ],
            'package_update': True,
            'package_upgrade': True,
            'packages': [
                'lua5.4',
                'luarocks',
                'git',
                'curl',
                'wget',
                'build-essential'
            ],
            'runcmd': [
                # Configure Lua environment
                'luarocks install luasocket',
                'luarocks install luafilesystem',
                
                # Configure BioXen environment
                f"echo 'export BIOXEN_VM_ID={config.get('vm_id', 'default')}' >> /etc/environment",
                
                # Enable SSH service
                'systemctl enable ssh',
                'systemctl start ssh',
                
                # Signal completion
                'touch /var/lib/cloud/instance/bioxen-ready'
            ]
        }
        
        return yaml.dump(cloud_config)
    
    def _generate_preseed_config(self, config: Dict[str, Any]) -> str:
        """Generate Debian preseed configuration"""
        
        preseed = f"""
# Localization
d-i debian-installer/locale string en_US
d-i keyboard-configuration/xkb-keymap select us

# Network configuration
d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string {config.get('hostname', 'bioxen-vm')}
d-i netcfg/get_domain string {config.get('domain', 'local')}

# Mirror settings
d-i mirror/country string manual
d-i mirror/http/hostname string deb.debian.org
d-i mirror/http/directory string /debian
d-i mirror/http/proxy string

# Account setup
d-i passwd/user-fullname string {config.get('fullname', 'BioXen User')}
d-i passwd/username string {config.get('username', 'bioxen')}
d-i passwd/user-password password {config.get('password', 'bioxen123')}
d-i passwd/user-password-again password {config.get('password', 'bioxen123')}
d-i user-setup/allow-password-weak boolean true

# Partitioning
d-i partman-auto/method string regular
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

# Package selection
tasksel tasksel/first multiselect standard, ssh-server
d-i pkgsel/include string lua5.4 luarocks git curl wget build-essential
d-i pkgsel/upgrade select full-upgrade

# Boot loader installation
d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true

# Finish
d-i finish-install/reboot_in_progress note
"""
        return preseed
    
    def _wait_for_vm_ip(self, vm_uuid: str, timeout: int = 300) -> str:
        """Wait for VM to get an IP address"""
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                vm_info = self.xapi_client.get_vm_info(vm_uuid)
                # In real implementation, extract IP from VM guest metrics
                # This is a placeholder for the actual XAPI call
                networks = vm_info.get('networks', {})
                for interface, details in networks.items():
                    if 'ip' in details and details['ip']:
                        return details['ip']
                        
            except Exception:
                pass
            
            time.sleep(5)
        
        raise VMConfigurationError(f"VM {vm_uuid} did not get IP address within {timeout} seconds")
    
    def _wait_for_ssh_service(self, ip_address: str, timeout: int = 300):
        """Wait for SSH service to become available"""
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((ip_address, 22))
                sock.close()
                
                if result == 0:
                    return True
                    
            except Exception:
                pass
            
            time.sleep(5)
        
        raise VMConfigurationError(f"SSH service not available on {ip_address} within {timeout} seconds")
    
    def _create_ssh_connection(self, ip_address: str, credentials: Dict[str, str]):
        """Create SSH connection to VM"""
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh_client.connect(
                hostname=ip_address,
                username=credentials.get('username', 'root'),
                password=credentials.get('password'),
                key_filename=credentials.get('key_file'),
                timeout=30
            )
            return ssh_client
            
        except Exception as e:
            raise VMConfigurationError(f"Failed to connect via SSH to {ip_address}: {e}")
    
    def _configure_system_via_ssh(self, ssh_client, config: Dict[str, Any]):
        """Configure system settings via SSH"""
        
        commands = [
            # Update system
            'apt-get update',
            'apt-get upgrade -y',
            
            # Install required packages
            'apt-get install -y lua5.4 luarocks git curl wget build-essential',
            
            # Configure Lua environment
            'luarocks install luasocket',
            'luarocks install luafilesystem',
            
            # Set environment variables
            f"echo 'export BIOXEN_VM_ID={config.get('vm_id', 'default')}' >> /etc/environment",
        ]
        
        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status != 0:
                error_output = stderr.read().decode()
                raise VMConfigurationError(f"Command failed: {command}\nError: {error_output}")


class BioXenVMFactory:
    """Factory for creating pre-configured BioXen VMs"""
    
    def __init__(self, xapi_client):
        self.configurator = VMConfigurator(xapi_client)
    
    def create_bioxen_vm(self, vm_name: str, template_name: str = "Debian Bookworm 12", 
                        vm_config: Optional[Dict[str, Any]] = None) -> str:
        """Create a fully configured BioXen VM ready for Lua execution
        
        Args:
            vm_name: Name for the new VM
            template_name: Template to use (default: Debian Bookworm 12)
            vm_config: Optional configuration overrides
            
        Returns:
            UUID of the created and configured VM
        """
        
        # Default BioXen configuration
        default_config = {
            'username': 'bioxen',
            'password': 'bioxen123',
            'hostname': vm_name,
            'domain': 'bioxen.local',
            'vm_id': vm_name,
            'packages': [
                'lua5.4',
                'luarocks', 
                'git',
                'curl',
                'wget',
                'build-essential',
                'openssh-server'
            ],
            'lua_packages': [
                'luasocket',
                'luafilesystem',
                'lua-cjson'
            ]
        }
        
        # Merge with user config
        if vm_config:
            default_config.update(vm_config)
        
        # Find template UUID
        templates = self.configurator.xapi_client.list_templates()
        template_uuid = None
        
        for template in templates:
            if template.get('name-label') == template_name:
                template_uuid = template.get('uuid')
                break
        
        if not template_uuid:
            raise VMConfigurationError(f"Template '{template_name}' not found")
        
        # Create and configure VM
        return self.configurator.create_configured_vm(template_uuid, vm_name, default_config)