#!/usr/bin/env python3
"""
Quick VM Status Checker
Checks the status of our newly created VM
"""

import sys
import os
import time
import xmlrpc.client
import ssl
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

def check_vm_status():
    """Check status of the VM we just created"""
    
    print("🔍 Checking VM Status...")
    print("=" * 40)
    
    try:
        # Configuration
        host = os.getenv("XCP_HOST")
        username = os.getenv("XCP_USERNAME")
        password = os.getenv("XCP_PASSWORD", "")
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connect
        url = f"https://{host}/"
        server = xmlrpc.client.ServerProxy(url, context=ssl_context, verbose=False)
        
        # Authenticate
        result = server.session.login_with_password(username, password)
        session_ref = result['Value']
        
        # Get all VMs
        vms_result = server.VM.get_all_records(session_ref)
        
        if vms_result['Status'] == 'Success':
            print("📋 Recent VMs (last 5):")
            
            # Filter and sort VMs by creation time
            vms = []
            for vm_ref, vm_record in vms_result['Value'].items():
                if (not vm_record.get('is_a_template', False) and 
                    not vm_record.get('is_control_domain', False) and
                    not vm_record.get('is_a_snapshot', False)):
                    
                    vm_name = vm_record.get('name_label', '')
                    if 'bioxen' in vm_name.lower():
                        vms.append({
                            'name': vm_name,
                            'uuid': vm_record.get('uuid', ''),
                            'power_state': vm_record.get('power_state', ''),
                            'ref': vm_ref
                        })
            
            # Show recent VMs
            for vm in vms[-5:]:
                print(f"   📦 {vm['name']}")
                print(f"      UUID: {vm['uuid']}")
                print(f"      State: {vm['power_state']}")
                
                # Try to get IP if available
                vm_record_result = server.VM.get_record(session_ref, vm['ref'])
                if vm_record_result['Status'] == 'Success':
                    vm_record = vm_record_result['Value']
                    guest_metrics = vm_record.get('guest_metrics')
                    
                    if guest_metrics and guest_metrics != 'OpaqueRef:NULL':
                        metrics_result = server.VM_guest_metrics.get_record(session_ref, guest_metrics)
                        if metrics_result['Status'] == 'Success':
                            metrics = metrics_result['Value']
                            networks = metrics.get('networks', {})
                            
                            ips = []
                            for interface, ip in networks.items():
                                if interface.startswith('0/ip') and ip and ip != '127.0.0.1':
                                    ips.append(ip)
                            
                            if ips:
                                print(f"      IP: {', '.join(ips)}")
                            else:
                                print(f"      IP: Not yet assigned")
                        else:
                            print(f"      IP: Guest metrics not available")
                    else:
                        print(f"      IP: No guest metrics")
                
                print()
        
        # Logout
        server.session.logout(session_ref)
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    check_vm_status()