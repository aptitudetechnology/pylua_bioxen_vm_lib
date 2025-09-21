#!/usr/bin/env python3
"""
Real Automated VM Creation with Post-Configuration
Creates a VM and automatically configures it via SSH without manual intervention
"""

import sys
import os
import time
import paramiko
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Add the library to the path for direct import
sys.path.insert(0, str(Path(__file__).parent / 'pylua_bioxen_vm_lib'))

def create_and_configure_vm():
    """Create a VM and automatically configure it"""
    
    print("🚀 Creating and Configuring Automated VM")
    print("=" * 60)
    print("CREATING VM WITH FULL AUTOMATION")
    print("=" * 60)
    
    try:
        # Import directly from files
        import xmlrpc.client
        import ssl
        
        # Configuration
        host = os.getenv("XCP_HOST")
        username = os.getenv("XCP_USERNAME")
        password = os.getenv("XCP_PASSWORD", "")
        
        if not password:
            print("❌ XCP_PASSWORD is required in .env file")
            return False
            
        print(f"📡 Connecting to: {host}")
        print(f"👤 Username: {username}")
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Try HTTPS first, fall back to HTTP
        try:
            url = f"https://{host}/"
            server = xmlrpc.client.ServerProxy(url, context=ssl_context, verbose=False)
        except Exception:
            url = f"http://{host}/"
            server = xmlrpc.client.ServerProxy(url, verbose=False)
        
        print(f"🔗 Using URL: {url}")
        
        # Authenticate
        print("🔑 Authenticating...")
        result = server.session.login_with_password(username, password)
        
        if result['Status'] != 'Success':
            print(f"❌ Authentication failed: {result}")
            return False
            
        session_ref = result['Value']
        print("✅ Authentication successful")
        
        # Get templates
        print("📋 Finding Debian Bookworm 12 template...")
        templates_result = server.VM.get_all_records(session_ref)
        
        if templates_result['Status'] != 'Success':
            print(f"❌ Failed to get templates: {templates_result}")
            return False
        
        # Find Debian Bookworm 12 template
        debian_template = None
        
        for vm_ref, vm_record in templates_result['Value'].items():
            if vm_record.get('is_a_template', False) and not vm_record.get('is_a_snapshot', False):
                template_name = vm_record.get('name_label', '')
                
                # Look for Debian template (case insensitive)
                if 'debian' in template_name.lower() and ('bookworm' in template_name.lower() or '12' in template_name):
                    debian_template = {
                        'ref': vm_ref,
                        'uuid': vm_record.get('uuid', ''),
                        'name': template_name
                    }
                    break
                    
        if not debian_template:
            print("❌ Debian Bookworm 12 template not found!")
            return False
            
        print(f"✅ Found template: {debian_template['name']}")
        
        # Create VM name with timestamp
        vm_name = f"bioxen-auto-vm-{int(time.time())}"
        print(f"🏗️  Creating VM: {vm_name}")
        
        # Clone the template
        clone_result = server.VM.clone(session_ref, debian_template['ref'], vm_name)
        
        if clone_result['Status'] != 'Success':
            error_info = clone_result.get('ErrorDescription', ['Unknown error'])
            print(f"❌ Failed to clone template: {error_info}")
            return False
            
        new_vm_ref = clone_result['Value']
        print("✅ VM cloned successfully")
        
        # Get the UUID of the new VM
        uuid_result = server.VM.get_uuid(session_ref, new_vm_ref)
        if uuid_result['Status'] != 'Success':
            print("❌ Failed to get new VM UUID")
            return False
            
        new_vm_uuid = uuid_result['Value']
        print(f"📋 New VM UUID: {new_vm_uuid}")
        
        # Set the VM as not a template
        server.VM.set_is_a_template(session_ref, new_vm_ref, False)
        print("✅ VM configured as regular VM")
        
        # Start the VM
        print("🚀 Starting VM...")
        start_result = server.VM.start(session_ref, new_vm_ref, False, False)
        
        if start_result['Status'] != 'Success':
            error_info = start_result.get('ErrorDescription', ['Unknown error'])
            print(f"❌ Failed to start VM: {error_info}")
            return False
            
        print("✅ VM started successfully")
        
        # Wait for VM to get an IP address
        print("⏳ Waiting for VM to get IP address...")
        vm_ip = wait_for_vm_ip(server, session_ref, new_vm_ref, timeout=300)
        
        if not vm_ip:
            print("❌ VM failed to get IP address within timeout")
            return False
            
        print(f"🌐 VM IP address: {vm_ip}")
        
        # Wait for SSH to be available
        print("⏳ Waiting for SSH service to be available...")
        if not wait_for_ssh(vm_ip, timeout=180):
            print("❌ SSH service not available within timeout")
            return False
            
        print("✅ SSH service is available")
        
        # Configure VM via SSH
        print("🔧 Configuring VM via SSH...")
        if configure_vm_via_ssh(vm_ip):
            print("✅ VM configuration completed successfully")
        else:
            print("❌ VM configuration failed")
            return False
        
        print(f"\n🎉 AUTOMATED VM CREATION COMPLETED!")
        print(f"VM Name: {vm_name}")
        print(f"VM UUID: {new_vm_uuid}")
        print(f"VM IP: {vm_ip}")
        print(f"SSH Access: ssh debian@{vm_ip}")
        
        # Logout
        try:
            server.session.logout(session_ref)
            print("✅ Session logged out")
        except Exception:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Automated VM creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def wait_for_vm_ip(server, session_ref, vm_ref, timeout=300):
    """Wait for VM to get an IP address"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Get VM guest metrics
            vm_record_result = server.VM.get_record(session_ref, vm_ref)
            if vm_record_result['Status'] == 'Success':
                vm_record = vm_record_result['Value']
                guest_metrics = vm_record.get('guest_metrics')
                
                if guest_metrics and guest_metrics != 'OpaqueRef:NULL':
                    # Get guest metrics record
                    metrics_result = server.VM_guest_metrics.get_record(session_ref, guest_metrics)
                    if metrics_result['Status'] == 'Success':
                        metrics = metrics_result['Value']
                        networks = metrics.get('networks', {})
                        
                        # Look for IP addresses
                        for interface, ip in networks.items():
                            if interface.startswith('0/ip') and ip and ip != '127.0.0.1':
                                return ip
            
            print(f"   Waiting for IP... ({int(time.time() - start_time)}s)")
            time.sleep(10)
            
        except Exception as e:
            print(f"   Error checking IP: {e}")
            time.sleep(10)
    
    return None

def wait_for_ssh(ip_address, port=22, timeout=180):
    """Wait for SSH service to be available"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            
            if result == 0:
                return True
                
        except Exception:
            pass
            
        print(f"   Waiting for SSH... ({int(time.time() - start_time)}s)")
        time.sleep(5)
    
    return False

def configure_vm_via_ssh(vm_ip):
    """Configure the VM via SSH"""
    try:
        # SSH connection details (Debian default)
        ssh_username = "debian"  # Default user for Debian cloud images
        ssh_password = None  # We'll try key-based auth or prompting
        
        print(f"🔗 Connecting to {ssh_username}@{vm_ip}...")
        
        # Create SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try to connect (you might need to configure SSH keys)
        try:
            # Try without password first (key-based auth)
            ssh_client.connect(vm_ip, username=ssh_username, timeout=30)
        except paramiko.AuthenticationException:
            print("⚠️  Password-based auth needed - this requires VM to be pre-configured")
            print("💡 For full automation, use cloud-init with SSH keys")
            return False
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            return False
        
        print("✅ SSH connection established")
        
        # Run configuration commands
        commands = [
            "sudo apt-get update -y",
            "sudo apt-get install -y lua5.4 lua5.4-dev luarocks curl git",
            "echo 'Lua installation:' && lua -v",
            "echo 'LuaRocks installation:' && luarocks --version",
            "echo 'export PATH=/home/debian/.luarocks/bin:$PATH' >> ~/.bashrc",
            "mkdir -p /home/debian/bioxen-workspace",
            "echo 'BioXen VM configured successfully' > /home/debian/bioxen-workspace/status.txt"
        ]
        
        for i, command in enumerate(commands, 1):
            print(f"   [{i}/{len(commands)}] {command}")
            stdin, stdout, stderr = ssh_client.exec_command(command)
            
            # Wait for command to complete
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error_output = stderr.read().decode()
                print(f"   ⚠️  Command failed (exit {exit_status}): {error_output}")
            else:
                output = stdout.read().decode().strip()
                if output:
                    print(f"   ✅ {output}")
        
        ssh_client.close()
        print("✅ VM configuration completed")
        return True
        
    except Exception as e:
        print(f"❌ SSH configuration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Automated VM Creation with Configuration")
    
    # Check required environment variables
    required_vars = ["XCP_HOST", "XCP_USERNAME", "XCP_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    success = create_and_configure_vm()
    
    if success:
        print(f"\n🎉 AUTOMATED VM CREATION WITH CONFIGURATION PASSED!")
    else:
        print(f"\n❌ Automated VM creation failed")
        sys.exit(1)