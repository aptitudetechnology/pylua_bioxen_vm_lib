"""
XCP-ng XAPI Client for VM lifecycle management
Handles authentication and XML-RPC communication with XCP-ng hosts
"""

import xmlrpc.client
import ssl
import time
from typing import Dict, List, Optional, Any

from .exceptions import VMManagerError, XCPngConnectionError


class XAPIClient:
    """Client for XCP-ng XAPI XML-RPC communication"""
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """Initialize XAPI client
        
        Args:
            host: XCP-ng host IP or hostname
            username: XCP-ng username
            password: XCP-ng password  
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session_ref = None
        
        # Create SSL context
        if not verify_ssl:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self.ssl_context = ssl.create_default_context()
        
        # Try HTTPS first, fall back to HTTP
        try:
            self.url = f"https://{host}/"
            self.server = xmlrpc.client.ServerProxy(self.url, context=self.ssl_context, verbose=False)
        except Exception:
            self.url = f"http://{host}/"
            self.server = xmlrpc.client.ServerProxy(self.url, verbose=False)
    
    def authenticate(self) -> bool:
        """Authenticate with XCP-ng host using XML-RPC
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            XCPngConnectionError: If authentication fails
        """
        try:
            # XAPI session.login_with_password
            result = self.server.session.login_with_password(self.username, self.password)
            
            if result['Status'] == 'Success':
                self.session_ref = result['Value']
                return True
            else:
                error_info = result.get('ErrorDescription', ['Unknown error'])
                raise XCPngConnectionError(f"Authentication failed: {error_info}")
                
        except xmlrpc.client.Fault as e:
            raise XCPngConnectionError(f"XAPI Fault: {e}")
        except Exception as e:
            raise XCPngConnectionError(f"Authentication error: {e}")
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available VM templates
        
        Returns:
            List of template dictionaries
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get all VM records
            result = self.server.VM.get_all_records(self.session_ref)
            
            if result['Status'] != 'Success':
                raise XCPngConnectionError(f"Failed to get VM records: {result}")
            
            templates = []
            for vm_ref, vm_record in result['Value'].items():
                # Templates have is_a_template = True
                if vm_record.get('is_a_template', False) and not vm_record.get('is_a_snapshot', False):
                    templates.append({
                        'uuid': vm_record.get('uuid', ''),
                        'name-label': vm_record.get('name_label', ''),
                        'name-description': vm_record.get('name_description', ''),
                        'ref': vm_ref
                    })
            
            return templates
            
        except Exception as e:
            raise XCPngConnectionError(f"Failed to list templates: {e}")
    
    def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs (excluding templates)
        
        Returns:
            List of VM dictionaries
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get all VM records
            result = self.server.VM.get_all_records(self.session_ref)
            
            if result['Status'] != 'Success':
                raise XCPngConnectionError(f"Failed to get VM records: {result}")
            
            vms = []
            for vm_ref, vm_record in result['Value'].items():
                # Regular VMs have is_a_template = False and is_control_domain = False
                if (not vm_record.get('is_a_template', False) and 
                    not vm_record.get('is_control_domain', False) and
                    not vm_record.get('is_a_snapshot', False)):
                    
                    vms.append({
                        'uuid': vm_record.get('uuid', ''),
                        'name-label': vm_record.get('name_label', ''),
                        'name-description': vm_record.get('name_description', ''),
                        'power_state': vm_record.get('power_state', ''),
                        'ref': vm_ref
                    })
            
            return vms
            
        except Exception as e:
            raise XCPngConnectionError(f"Failed to list VMs: {e}")
    
    def start_vm(self, vm_uuid: str) -> bool:
        """Start a VM
        
        Args:
            vm_uuid: UUID of the VM to start
            
        Returns:
            bool: True if started successfully
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get VM reference by UUID
            vm_ref_result = self.server.VM.get_by_uuid(self.session_ref, vm_uuid)
            if vm_ref_result['Status'] != 'Success':
                raise XCPngConnectionError(f"VM not found: {vm_uuid}")
            
            vm_ref = vm_ref_result['Value']
            
            # Start the VM
            result = self.server.VM.start(self.session_ref, vm_ref, False, False)
            
            if result['Status'] == 'Success':
                return True
            else:
                error_info = result.get('ErrorDescription', ['Unknown error'])
                raise XCPngConnectionError(f"Failed to start VM: {error_info}")
                
        except Exception as e:
            raise XCPngConnectionError(f"Failed to start VM: {e}")
    
    def stop_vm(self, vm_uuid: str) -> bool:
        """Stop a VM
        
        Args:
            vm_uuid: UUID of the VM to stop
            
        Returns:
            bool: True if stopped successfully
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get VM reference by UUID
            vm_ref_result = self.server.VM.get_by_uuid(self.session_ref, vm_uuid)
            if vm_ref_result['Status'] != 'Success':
                raise XCPngConnectionError(f"VM not found: {vm_uuid}")
            
            vm_ref = vm_ref_result['Value']
            
            # Clean shutdown first
            result = self.server.VM.clean_shutdown(self.session_ref, vm_ref)
            
            if result['Status'] == 'Success':
                return True
            else:
                error_info = result.get('ErrorDescription', ['Unknown error'])
                raise XCPngConnectionError(f"Failed to stop VM: {error_info}")
                
        except Exception as e:
            raise XCPngConnectionError(f"Failed to stop VM: {e}")
    
    def get_vm_info(self, vm_uuid: str) -> Dict[str, Any]:
        """Get detailed VM information
        
        Args:
            vm_uuid: UUID of the VM
            
        Returns:
            Dictionary with VM information
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get VM reference by UUID
            vm_ref_result = self.server.VM.get_by_uuid(self.session_ref, vm_uuid)
            if vm_ref_result['Status'] != 'Success':
                raise XCPngConnectionError(f"VM not found: {vm_uuid}")
            
            vm_ref = vm_ref_result['Value']
            
            # Get VM record
            record_result = self.server.VM.get_record(self.session_ref, vm_ref)
            if record_result['Status'] != 'Success':
                raise XCPngConnectionError(f"Failed to get VM record: {vm_uuid}")
            
            vm_record = record_result['Value']
            
            return {
                'uuid': vm_record.get('uuid', ''),
                'name-label': vm_record.get('name_label', ''),
                'name-description': vm_record.get('name_description', ''),
                'power_state': vm_record.get('power_state', ''),
                'memory_static_max': vm_record.get('memory_static_max', 0),
                'memory_dynamic_max': vm_record.get('memory_dynamic_max', 0),
                'VCPUs_max': vm_record.get('VCPUs_max', 0),
                'ref': vm_ref
            }
            
        except Exception as e:
            raise XCPngConnectionError(f"Failed to get VM info: {e}")
    
    def create_vm_from_template(self, template_uuid: str, vm_name: str) -> str:
        """Create a new VM from a template
        
        Args:
            template_uuid: UUID of the template to use
            vm_name: Name for the new VM
            
        Returns:
            UUID of the created VM
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get template reference by UUID
            template_ref_result = self.server.VM.get_by_uuid(self.session_ref, template_uuid)
            if template_ref_result['Status'] != 'Success':
                raise XCPngConnectionError(f"Template not found: {template_uuid}")
            
            template_ref = template_ref_result['Value']
            
            # Clone the template
            clone_result = self.server.VM.clone(self.session_ref, template_ref, vm_name)
            if clone_result['Status'] != 'Success':
                error_info = clone_result.get('ErrorDescription', ['Unknown error'])
                raise XCPngConnectionError(f"Failed to clone template: {error_info}")
            
            new_vm_ref = clone_result['Value']
            
            # Get the UUID of the new VM
            uuid_result = self.server.VM.get_uuid(self.session_ref, new_vm_ref)
            if uuid_result['Status'] != 'Success':
                raise XCPngConnectionError("Failed to get new VM UUID")
            
            new_vm_uuid = uuid_result['Value']
            
            # Set the VM as not a template
            self.server.VM.set_is_a_template(self.session_ref, new_vm_ref, False)
            
            return new_vm_uuid
            
        except Exception as e:
            raise XCPngConnectionError(f"Failed to create VM from template: {e}")
    
    def create_cloud_vm_from_template(self, template_uuid: str, vm_name: str, 
                                     cloud_init_config: str = None) -> str:
        """Create a new VM from a cloud image template with cloud-init configuration
        
        Args:
            template_uuid: UUID of the cloud template to use
            vm_name: Name for the new VM
            cloud_init_config: Base64-encoded cloud-init YAML configuration
            
        Returns:
            UUID of the created VM
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Create VM from template
            vm_uuid = self.create_vm_from_template(template_uuid, vm_name)
            
            # Configure cloud-init if provided
            if cloud_init_config:
                # Get VM reference by UUID
                vm_ref_result = self.server.VM.get_by_uuid(self.session_ref, vm_uuid)
                if vm_ref_result['Status'] != 'Success':
                    raise XCPngConnectionError(f"VM not found: {vm_uuid}")
                
                vm_ref = vm_ref_result['Value']
                
                # Set cloud-init user data in platform parameters
                platform_result = self.server.VM.get_platform(self.session_ref, vm_ref)
                if platform_result['Status'] == 'Success':
                    platform = platform_result['Value']
                else:
                    platform = {}
                
                # Add cloud-init configuration
                platform['user-data'] = cloud_init_config
                
                # Update platform
                set_result = self.server.VM.set_platform(self.session_ref, vm_ref, platform)
                if set_result['Status'] != 'Success':
                    raise XCPngConnectionError("Failed to set cloud-init configuration")
            
            return vm_uuid
            
        except Exception as e:
            raise XCPngConnectionError(f"Failed to create cloud VM from template: {e}")
    
    def delete_vm(self, vm_uuid: str) -> bool:
        """Delete a VM and its associated VDIs
        
        Args:
            vm_uuid: UUID of the VM to delete
            
        Returns:
            bool: True if deleted successfully
        """
        if not self.session_ref:
            raise XCPngConnectionError("Not authenticated")
        
        try:
            # Get VM reference by UUID
            vm_ref_result = self.server.VM.get_by_uuid(self.session_ref, vm_uuid)
            if vm_ref_result['Status'] != 'Success':
                raise XCPngConnectionError(f"VM not found: {vm_uuid}")
            
            vm_ref = vm_ref_result['Value']
            
            # Get VM record to find VBDs
            record_result = self.server.VM.get_record(self.session_ref, vm_ref)
            if record_result['Status'] == 'Success':
                vm_record = record_result['Value']
                
                # Delete associated VDIs
                for vbd_ref in vm_record.get('VBDs', []):
                    try:
                        vbd_record_result = self.server.VBD.get_record(self.session_ref, vbd_ref)
                        if vbd_record_result['Status'] == 'Success':
                            vbd_record = vbd_record_result['Value']
                            if not vbd_record.get('empty', True):
                                vdi_ref = vbd_record.get('VDI')
                                if vdi_ref and vdi_ref != 'OpaqueRef:NULL':
                                    self.server.VDI.destroy(self.session_ref, vdi_ref)
                    except Exception:
                        pass  # Continue even if VDI deletion fails
            
            # Destroy the VM
            result = self.server.VM.destroy(self.session_ref, vm_ref)
            
            if result['Status'] == 'Success':
                return True
            else:
                error_info = result.get('ErrorDescription', ['Unknown error'])
                raise XCPngConnectionError(f"Failed to delete VM: {error_info}")
                
        except Exception as e:
            raise XCPngConnectionError(f"Failed to delete VM: {e}")
    
    def logout(self):
        """Logout and cleanup session"""
        if self.session_ref:
            try:
                self.server.session.logout(self.session_ref)
            except Exception:
                pass  # Ignore logout errors
            finally:
                self.session_ref = None