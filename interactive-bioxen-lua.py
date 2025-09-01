#!/usr/bin/env python3
"""
BioXen-luavm Interactive CLI
Interactive command-line interface for managing Lua VMs with XCP-ng support.

Phase 3: Complete CLI integration with multi-VM support
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("❌ Missing dependency: questionary")
    print("Install with: pip install questionary")
    sys.exit(1)

from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.exceptions import VMManagerError, SessionNotFoundError


class VMStatus:
    """Track VM status and metadata"""
    def __init__(self, profile: str, vm_type: str = "basic"):
        self.profile = profile
        self.vm_type = vm_type  # Track VM type (basic/xcpng)
        self.running = False
        self.attached = False
        self.pid = None
        self.created_at = datetime.now()
        self.packages_installed = 0
        self.xcpng_config = None  # Store XCP-ng configuration if applicable
    
    def get_uptime(self) -> str:
        """Get human-readable uptime"""
        delta = datetime.now() - self.created_at
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{delta.days}d {hours}h {minutes}m"


class BioXenLuavmCLI:
    """Interactive CLI for BioXen Lua VM management with XCP-ng support"""
    
    def __init__(self):
        self.vm_manager = VMManager(debug_mode=True)
        self.vm_status: Dict[str, VMStatus] = {}
        self.current_vm = None
        self.running = True
        
        # Load existing VM status if available
        self._load_vm_status()
    
    def _load_vm_status(self):
        """Load VM status from previous sessions"""
        # For Phase 3, we'll implement basic in-memory tracking
        # Could be extended to persist state in future versions
        pass
    
    def _save_vm_status(self):
        """Save VM status for persistence"""
        # Placeholder for future state persistence
        pass
    
    def _get_xcpng_config(self) -> Optional[Dict[str, Any]]:
        """Get XCP-ng configuration from user or config file"""
        
        config_choice = questionary.select(
            "XCP-ng configuration:",
            choices=[
                Choice("📁 Load from config file", "file"),
                Choice("⚙️  Enter manually", "manual"),
                Choice("❌ Cancel", "cancel")
            ]
        ).ask()
        
        if config_choice == "cancel":
            return None
        
        if config_choice == "file":
            config_path = questionary.path(
                "Path to XCP-ng config file (JSON):",
                default="xcpng_config.json"
            ).ask()
            
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    print(f"✅ Loaded configuration from {config_path}")
                    return config
            except FileNotFoundError:
                print(f"❌ Config file not found: {config_path}")
                return None
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in config file: {e}")
                return None
            except Exception as e:
                print(f"❌ Could not load config file: {e}")
                return None
        
        elif config_choice == "manual":
            print("\n🔧 Manual XCP-ng Configuration")
            print("=" * 40)
            
            # Manual configuration entry
            host = questionary.text(
                "XCP-ng host IP/hostname:",
                validate=lambda x: len(x.strip()) > 0 or "Host is required"
            ).ask()
            
            username = questionary.text(
                "Username:",
                default="root"
            ).ask()
            
            password = questionary.password(
                "Password:"
            ).ask()
            
            template = questionary.text(
                "VM template name:",
                default="lua-bio-template",
                validate=lambda x: len(x.strip()) > 0 or "Template name is required"
            ).ask()
            
            # Optional advanced settings
            advanced = questionary.confirm(
                "Configure advanced settings?",
                default=False
            ).ask()
            
            config = {
                "xapi_url": f"https://{host.strip()}",
                "username": username.strip(),
                "password": password,
                "template": template.strip(),
                "vm_name_prefix": "bioxen-lua",
                "memory": "2GB",
                "vcpus": 2,
                "verify_ssl": False
            }
            
            if advanced:
                memory = questionary.text(
                    "Memory allocation:",
                    default="2GB"
                ).ask()
                
                vcpus = questionary.text(
                    "Number of vCPUs:",
                    default="2"
                ).ask()
                
                config.update({
                    "memory": memory,
                    "vcpus": int(vcpus) if vcpus.isdigit() else 2
                })
            
            if not all([host, username, password, template]):
                print("❌ All required fields must be provided")
                return None
                
            return config
        
        return None
    
    def create_lua_vm(self):
        """Create a new Lua VM with type selection"""
        print("\n🚀 Create New Lua VM")
        print("=" * 30)
        
        vm_id = questionary.text(
            "Enter VM ID (unique identifier):",
            validate=lambda x: (x and x.strip() and x not in self.vm_status) or 
                              "VM ID must be unique and non-empty"
        ).ask()
        
        if not vm_id:
            return
        
        vm_id = vm_id.strip()
        
        # VM Type Selection
        vm_type = questionary.select(
            "Select VM type:",
            choices=[
                Choice("🖥️  Local Process VM (basic)", "basic"),
                Choice("☁️  XCP-ng Virtual Machine (xcpng)", "xcpng"),
            ],
            default="basic"
        ).ask()
        
        if not vm_type:
            return
        
        # Handle XCP-ng configuration
        config = {}
        if vm_type == "xcpng":
            print(f"\n☁️  XCP-ng VM Configuration Required")
            config = self._get_xcpng_config()
            if not config:
                print("❌ XCP-ng configuration required for xcpng VM type")
                return
        
        profile_name = questionary.text(
            "Enter profile name for this VM:",
            default="standard"
        ).ask()
        
        if not profile_name:
            profile_name = "standard"
        
        try:
            print(f"\n🔄 Creating {vm_type} VM '{vm_id}' with profile '{profile_name}'...")
            
            # Create VM with type and config
            if vm_type == "xcpng":
                session = self.vm_manager.create_interactive_vm(vm_id, vm_type=vm_type, config=config)
            else:
                session = self.vm_manager.create_interactive_vm(vm_id, vm_type=vm_type)
            
            # Track VM status
            status = VMStatus(profile_name, vm_type)
            status.running = True
            if vm_type == "xcpng":
                status.xcpng_config = config
            
            self.vm_status[vm_id] = status
            
            vm_type_display = "🖥️ Local Process" if vm_type == "basic" else "☁️ XCP-ng VM"
            print(f"✅ {vm_type_display} VM '{vm_id}' created successfully!")
            print(f"📊 Profile: {profile_name}")
            
            if vm_type == "xcpng":
                print(f"🏠 Host: {config.get('xapi_url', 'Unknown')}")
                print(f"📋 Template: {config.get('template', 'Unknown')}")
            
            self._save_vm_status()
            
        except VMManagerError as e:
            print(f"❌ VM creation failed: {e}")
            if vm_type == "xcpng":
                print("💡 Check XCP-ng host connectivity and configuration")
                print("   - Verify host is reachable")
                print("   - Check credentials")
                print("   - Confirm template exists")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def list_vms(self):
        """List all VMs with their status"""
        if not self.vm_status:
            print("\n📭 No VMs created")
            print("💡 Use 'Create new Lua VM' to get started")
            return
        
        print("\n🖥️  VM List")
        print("=" * 80)
        
        for vm_id, status in self.vm_status.items():
            state_indicators = []
            if status.running:
                state_indicators.append("🟢 Running")
            else:
                state_indicators.append("🔴 Stopped")
            
            if status.attached:
                state_indicators.append("🔗 Attached")
            
            # Show VM type with icon
            vm_type_icon = "🖥️" if status.vm_type == "basic" else "☁️"
            vm_type_display = "Local Process" if status.vm_type == "basic" else "XCP-ng VM"
            
            print(f"\n📋 VM ID: {vm_id}")
            print(f"   Type: {vm_type_icon} {vm_type_display}")
            print(f"   Profile: {status.profile}")
            print(f"   Status: {' '.join(state_indicators)}")
            print(f"   Created: {status.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Uptime: {status.get_uptime()}")
            
            if status.vm_type == "xcpng" and status.xcpng_config:
                print(f"   Host: {status.xcpng_config.get('xapi_url', 'Unknown')}")
                print(f"   Template: {status.xcpng_config.get('template', 'Unknown')}")
        
        print()
    
    def attach_to_vm(self):
        """Attach to an existing VM for interactive use"""
        if not self.vm_status:
            print("❌ No VMs available. Create a VM first.")
            return
        
        vm_choices = []
        for vm_id, status in self.vm_status.items():
            vm_type_icon = "🖥️" if status.vm_type == "basic" else "☁️"
            state = "🟢" if status.running else "🔴"
            vm_choices.append(Choice(
                f"{vm_type_icon} {vm_id} ({status.vm_type}) {state}",
                vm_id
            ))
        
        vm_id = questionary.select(
            "Select VM to attach to:",
            choices=vm_choices
        ).ask()
        
        if not vm_id:
            return
        
        try:
            print(f"\n🔗 Attaching to VM '{vm_id}'...")
            
            # Start interactive session
            self.current_vm = vm_id
            self.vm_status[vm_id].attached = True
            
            print(f"✅ Attached to {self.vm_status[vm_id].vm_type} VM '{vm_id}'")
            print("💡 Type 'exit' to detach from VM")
            print("💡 Enter Lua commands directly")
            print("-" * 50)
            
            # Interactive loop
            self._interactive_session(vm_id)
            
        except SessionNotFoundError:
            print(f"❌ VM '{vm_id}' session not found")
            if vm_id in self.vm_status:
                self.vm_status[vm_id].running = False
        except Exception as e:
            print(f"❌ Failed to attach to VM: {e}")
    
    def _interactive_session(self, vm_id: str):
        """Handle interactive Lua session"""
        while True:
            try:
                # Get user input
                lua_input = questionary.text(
                    f"lua[{vm_id}]> ",
                    qmark=""
                ).ask()
                
                if not lua_input:
                    continue
                
                if lua_input.strip().lower() in ['exit', 'quit', 'detach']:
                    break
                
                # Send input to VM
                self.vm_manager.send_input(vm_id, lua_input)
                
                # Wait briefly for output
                time.sleep(0.2)
                
                # Read and display output
                output = self.vm_manager.read_output(vm_id)
                if output and output.strip():
                    print(output)
                
            except KeyboardInterrupt:
                print("\n💡 Use 'exit' to detach from VM")
                continue
            except Exception as e:
                print(f"❌ Session error: {e}")
                break
        
        # Detach from VM
        self.vm_status[vm_id].attached = False
        self.current_vm = None
        print(f"\n🔗 Detached from VM '{vm_id}'")
    
    def terminate_vm(self):
        """Terminate a VM"""
        if not self.vm_status:
            print("❌ No VMs available")
            return
        
        vm_choices = []
        for vm_id, status in self.vm_status.items():
            vm_type_icon = "🖥️" if status.vm_type == "basic" else "☁️"
            state = "🟢" if status.running else "🔴"
            vm_choices.append(Choice(
                f"{vm_type_icon} {vm_id} ({status.vm_type}) {state}",
                vm_id
            ))
        
        vm_id = questionary.select(
            "Select VM to terminate:",
            choices=vm_choices
        ).ask()
        
        if not vm_id:
            return
        
        confirm = questionary.confirm(
            f"⚠️  Terminate VM '{vm_id}'? This will stop all processes.",
            default=False
        ).ask()
        
        if not confirm:
            return
        
        try:
            print(f"🛑 Terminating VM '{vm_id}'...")
            self.vm_manager.terminate_vm_session(vm_id)
            
            # Update status
            if vm_id in self.vm_status:
                self.vm_status[vm_id].running = False
                self.vm_status[vm_id].attached = False
            
            print(f"✅ VM '{vm_id}' terminated successfully")
            
        except Exception as e:
            print(f"❌ Failed to terminate VM: {e}")
    
    def show_main_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 60)
        print("🧬 BioXen-luavm Interactive CLI")
        print("Multi-VM Lua Environment with XCP-ng Support")
        print("=" * 60)
        
        if self.vm_status:
            running_count = sum(1 for s in self.vm_status.values() if s.running)
            total_count = len(self.vm_status)
            basic_count = sum(1 for s in self.vm_status.values() if s.vm_type == "basic")
            xcpng_count = sum(1 for s in self.vm_status.values() if s.vm_type == "xcpng")
            
            print(f"📊 Status: {running_count}/{total_count} VMs running")
            print(f"   🖥️  Local: {basic_count} | ☁️  XCP-ng: {xcpng_count}")
        else:
            print("📭 No VMs created yet")
        
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("🚀 Create new Lua VM", "create"),
                Choice("📋 List VMs", "list"),
                Choice("🔗 Attach to VM", "attach"),
                Choice("🛑 Terminate VM", "terminate"),
                Choice("❌ Exit", "exit")
            ]
        ).ask()
        
        return choice
    
    def run(self):
        """Main CLI loop"""
        print("🧬 Welcome to BioXen-luavm!")
        print("Interactive Lua VM Management with XCP-ng Support")
        
        while self.running:
            try:
                choice = self.show_main_menu()
                
                if choice == "create":
                    self.create_lua_vm()
                elif choice == "list":
                    self.list_vms()
                elif choice == "attach":
                    self.attach_to_vm()
                elif choice == "terminate":
                    self.terminate_vm()
                elif choice == "exit":
                    self._cleanup_and_exit()
                    break
                else:
                    print("❌ Invalid choice")
                
            except KeyboardInterrupt:
                print("\n👋 Exiting BioXen-luavm...")
                self._cleanup_and_exit()
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue
    
    def _cleanup_and_exit(self):
        """Cleanup resources before exit"""
        print("\n🔄 Cleaning up...")
        
        # Detach from current VM if attached
        if self.current_vm:
            print(f"🔗 Detaching from VM '{self.current_vm}'")
            if self.current_vm in self.vm_status:
                self.vm_status[self.current_vm].attached = False
        
        # Save VM status
        self._save_vm_status()
        
        print("✅ Cleanup complete")
        print("👋 Thank you for using BioXen-luavm!")
        self.running = False


def main():
    """Main entry point"""
    try:
        cli = BioXenLuavmCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
