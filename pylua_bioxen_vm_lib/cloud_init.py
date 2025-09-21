"""
Cloud-Init Configuration Helper for BioXen VMs
Generates cloud-init configurations for automated VM setup
"""

import base64
import yaml
from typing import Dict, List, Optional, Any


class CloudInitConfig:
    """Cloud-init configuration generator for BioXen VMs"""
    
    def __init__(self):
        """Initialize with default BioXen configuration"""
        self.config = {
            'package_update': True,
            'package_upgrade': True,
            'packages': [
                'lua5.4',
                'lua5.4-dev', 
                'luarocks',
                'curl',
                'git',
                'htop',
                'vim',
                'sudo',
                'openssh-server'
            ],
            'users': [],
            'chpasswd': {
                'list': '',
                'expire': False
            },
            'ssh_pwauth': True,
            'disable_root': False,
            'runcmd': [
                'systemctl enable ssh',
                'systemctl start ssh'
            ],
            'final_message': 'BioXen VM is ready!'
        }
    
    def add_user(self, username: str, password: str = None, 
                 ssh_keys: List[str] = None, groups: List[str] = None) -> 'CloudInitConfig':
        """Add a user to the cloud-init configuration
        
        Args:
            username: Username to create
            password: User password (optional)
            ssh_keys: List of SSH public keys (optional)
            groups: List of groups to add user to (optional)
            
        Returns:
            Self for method chaining
        """
        user_config = {
            'name': username,
            'shell': '/bin/bash'
        }
        
        if groups:
            user_config['groups'] = groups
            if 'sudo' in groups:
                user_config['sudo'] = ['ALL=(ALL) NOPASSWD:ALL']
        
        if ssh_keys:
            user_config['ssh_authorized_keys'] = ssh_keys
        
        self.config['users'].append(user_config)
        
        # Add password to chpasswd if provided
        if password:
            current_passwords = self.config['chpasswd']['list']
            if current_passwords:
                current_passwords += f'\n{username}:{password}'
            else:
                current_passwords = f'{username}:{password}'
            self.config['chpasswd']['list'] = current_passwords
        
        return self
    
    def add_packages(self, packages: List[str]) -> 'CloudInitConfig':
        """Add packages to install
        
        Args:
            packages: List of package names to install
            
        Returns:
            Self for method chaining
        """
        self.config['packages'].extend(packages)
        return self
    
    def add_commands(self, commands: List[str]) -> 'CloudInitConfig':
        """Add commands to run during setup
        
        Args:
            commands: List of shell commands to execute
            
        Returns:
            Self for method chaining
        """
        # Insert before the final SSH commands
        ssh_commands = [cmd for cmd in self.config['runcmd'] if 'ssh' in cmd]
        other_commands = [cmd for cmd in self.config['runcmd'] if 'ssh' not in cmd]
        
        self.config['runcmd'] = other_commands + commands + ssh_commands
        return self
    
    def set_hostname(self, hostname: str) -> 'CloudInitConfig':
        """Set VM hostname
        
        Args:
            hostname: Hostname for the VM
            
        Returns:
            Self for method chaining
        """
        self.config['hostname'] = hostname
        return self
    
    def add_bioxen_user(self, password: str = 'bioxen123', 
                       ssh_keys: List[str] = None) -> 'CloudInitConfig':
        """Add default BioXen user with Lua environment setup
        
        Args:
            password: Password for bioxen user
            ssh_keys: Optional SSH public keys
            
        Returns:
            Self for method chaining
        """
        self.add_user('bioxen', password, ssh_keys, ['sudo'])
        
        # Add BioXen workspace setup commands
        bioxen_commands = [
            'mkdir -p /home/bioxen/workspace',
            'chown bioxen:bioxen /home/bioxen/workspace',
            'echo "export PATH=/home/bioxen/.luarocks/bin:$PATH" >> /home/bioxen/.bashrc',
            'echo "export LUA_PATH=\\"/home/bioxen/.luarocks/share/lua/5.4/?.lua;/home/bioxen/.luarocks/share/lua/5.4/?/init.lua;;\\\"" >> /home/bioxen/.bashrc',
            'echo "BioXen VM configured via cloud-init" > /home/bioxen/workspace/status.txt',
            'chown bioxen:bioxen /home/bioxen/workspace/status.txt'
        ]
        
        self.add_commands(bioxen_commands)
        return self
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML string
        
        Returns:
            YAML string of the cloud-init configuration
        """
        # Add cloud-config header
        yaml_content = "#cloud-config\n"
        yaml_content += "# BioXen VM Cloud-Init Configuration\n\n"
        yaml_content += yaml.dump(self.config, default_flow_style=False)
        return yaml_content
    
    def to_base64(self) -> str:
        """Convert configuration to base64-encoded string for XCP-ng
        
        Returns:
            Base64-encoded YAML configuration
        """
        yaml_content = self.to_yaml()
        return base64.b64encode(yaml_content.encode()).decode()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    @classmethod
    def create_bioxen_vm(cls, hostname: str = None, ssh_keys: List[str] = None,
                        additional_packages: List[str] = None) -> 'CloudInitConfig':
        """Create a standard BioXen VM configuration
        
        Args:
            hostname: VM hostname (optional)
            ssh_keys: SSH public keys for bioxen user (optional)
            additional_packages: Extra packages to install (optional)
            
        Returns:
            Configured CloudInitConfig instance
        """
        config = cls()
        
        # Add BioXen user
        config.add_bioxen_user(ssh_keys=ssh_keys)
        
        # Set hostname if provided
        if hostname:
            config.set_hostname(hostname)
        
        # Add additional packages
        if additional_packages:
            config.add_packages(additional_packages)
        
        return config
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CloudInitConfig':
        """Create CloudInitConfig from dictionary
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            CloudInitConfig instance
        """
        instance = cls()
        instance.config.update(config_dict)
        return instance


# Convenience functions
def create_bioxen_cloud_config(hostname: str = None, ssh_keys: List[str] = None,
                              additional_packages: List[str] = None) -> str:
    """Create a base64-encoded cloud-init config for BioXen VMs
    
    Args:
        hostname: VM hostname (optional)
        ssh_keys: SSH public keys for bioxen user (optional)
        additional_packages: Extra packages to install (optional)
        
    Returns:
        Base64-encoded cloud-init configuration
    """
    config = CloudInitConfig.create_bioxen_vm(hostname, ssh_keys, additional_packages)
    return config.to_base64()


def create_custom_cloud_config(users: List[Dict[str, Any]], 
                              packages: List[str] = None,
                              commands: List[str] = None,
                              hostname: str = None) -> str:
    """Create a custom cloud-init configuration
    
    Args:
        users: List of user configurations
        packages: Additional packages to install (optional)
        commands: Additional commands to run (optional)
        hostname: VM hostname (optional)
        
    Returns:
        Base64-encoded cloud-init configuration
    """
    config = CloudInitConfig()
    
    # Add users
    for user in users:
        config.add_user(
            user['username'],
            user.get('password'),
            user.get('ssh_keys'),
            user.get('groups')
        )
    
    # Add packages
    if packages:
        config.add_packages(packages)
    
    # Add commands
    if commands:
        config.add_commands(commands)
    
    # Set hostname
    if hostname:
        config.set_hostname(hostname)
    
    return config.to_base64()