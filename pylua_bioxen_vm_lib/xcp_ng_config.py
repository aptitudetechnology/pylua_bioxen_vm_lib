"""
Configuration management for XCP-ng integration (Phase 1)
Handles XCP-ng server connection parameters, VM templates, and security credentials
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .exceptions import VMManagerError


class XCPngConfig:
    """Configuration manager for XCP-ng integration"""
    
    DEFAULT_CONFIG = {
        'xcp_host': None,
        'xcp_username': 'root',
        'xcp_password': None,
        'template_name': 'lua-bio-template',
        'vm_username': 'root',
        'vm_password': None,
        'vm_key_file': None,
        'memory': '2GB',
        'vcpus': 2,
        'verify_ssl': False,
        'ssh_timeout': 30,
        'vm_network': 'Pool-wide network associated with eth0',
        'vm_name_prefix': 'bioxen-lua'
    }
    
    def __init__(self, config_file: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize XCP-ng configuration
        
        Args:
            config_file: Path to JSON configuration file
            config_dict: Configuration dictionary (overrides file)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from environment variables first
        self.load_from_environment()
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
        
        # Override with provided dictionary
        if config_dict:
            self.config.update(config_dict)
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        config_path = Path(config_file)
        if not config_path.exists():
            raise VMManagerError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except json.JSONDecodeError as e:
            raise VMManagerError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise VMManagerError(f"Error loading configuration file: {e}")
    
    def load_from_environment(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'xcp_host': 'XCP_HOST',
            'xcp_username': 'XCP_USERNAME', 
            'xcp_password': 'XCP_PASSWORD',
            'template_name': 'XCP_TEMPLATE',
            'vm_username': 'VM_USERNAME',
            'vm_password': 'VM_PASSWORD',
            'vm_key_file': 'VM_KEY_FILE'
        }
        
        for config_key, env_var in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self.config[config_key] = env_value
    
    def validate(self) -> bool:
        """
        Validate configuration for required fields
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            VMManagerError: If required fields are missing
        """
        required_fields = ['xcp_host', 'xcp_password', 'template_name']
        
        for field in required_fields:
            if not self.config.get(field):
                raise VMManagerError(f"Required configuration field missing: {field}")
        
        return True
    
    def get_xcp_connection_config(self) -> Dict[str, Any]:
        """Get XCP-ng connection configuration"""
        return {
            'xcp_host': self.config['xcp_host'],
            'xcp_username': self.config['xcp_username'],
            'xcp_password': self.config['xcp_password'],
            'verify_ssl': self.config.get('verify_ssl', False)
        }
    
    def get_vm_config(self) -> Dict[str, Any]:
        """Get VM creation configuration"""
        return {
            'template_name': self.config['template_name'],
            'memory': self.config['memory'],
            'vcpus': self.config['vcpus'],
            'vm_network': self.config['vm_network'],
            'vm_name_prefix': self.config['vm_name_prefix']
        }
    
    def get_ssh_config(self) -> Dict[str, Any]:
        """Get SSH connection configuration"""
        return {
            'vm_username': self.config['vm_username'],
            'vm_password': self.config.get('vm_password'),
            'vm_key_file': self.config.get('vm_key_file'),
            'ssh_timeout': self.config.get('ssh_timeout', 30)
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self.config.copy()


class VMConfigTemplate:
    """Template for VM configuration generation"""
    
    @staticmethod
    def create_basic_vm_config(vm_id: str, config: XCPngConfig) -> Dict[str, Any]:
        """Create basic VM configuration for XCP-ng"""
        return {
            'vm_name': f"{config.get('vm_name_prefix', 'bioxen-lua')}-{vm_id}",
            'template_name': config.get('template_name'),
            'memory': config.get('memory', '2GB'),
            'vcpus': config.get('vcpus', 2),
            'network': config.get('vm_network'),
            'description': f"BioXen Lua VM: {vm_id}"
        }
    
    @staticmethod
    def create_development_vm_config(vm_id: str, config: XCPngConfig) -> Dict[str, Any]:
        """Create development VM configuration with enhanced resources"""
        base_config = VMConfigTemplate.create_basic_vm_config(vm_id, config)
        base_config.update({
            'memory': '4GB',
            'vcpus': 4,
            'description': f"BioXen Lua Development VM: {vm_id}"
        })
        return base_config
    
    @staticmethod
    def create_production_vm_config(vm_id: str, config: XCPngConfig) -> Dict[str, Any]:
        """Create production VM configuration with optimized resources"""
        base_config = VMConfigTemplate.create_basic_vm_config(vm_id, config)
        base_config.update({
            'memory': '8GB',
            'vcpus': 8,
            'description': f"BioXen Lua Production VM: {vm_id}"
        })
        return base_config
