#!/usr/bin/env python3

"""
verify_domains.py
Check deployed databases and ensure all domains are properly configured in /etc/hosts
Run with sudo: sudo python3 verify_domains.py
"""

import os
import sys
import subprocess
import re
from datetime import datetime
from database.db_connection import DatabaseConnection
from config import Config

class DomainVerifier:
    """Verify and fix domain configurations"""
    
    def __init__(self):
        self.hosts_file = '/etc/hosts'
        self.check_sudo()
        self.verified_domains = []
        self.added_domains = []
        self.failed_domains = []
    
    def check_sudo(self):
        """Check if running with sudo"""
        if os.geteuid() != 0:
            print("❌ Error: This script must be run with sudo")
            print("Usage: sudo python3 verify_domains.py")
            sys.exit(1)
    
    def backup_hosts(self):
        """Create backup of /etc/hosts before modifications"""
        try:
            backup_file = f"{self.hosts_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            subprocess.run(['cp', self.hosts_file, backup_file], check=True)
            print(f"✓ Backup created: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"⚠ Warning: Could not backup: {e}")
            return None
    
    def get_deployed_domains(self):
        """Get all deployed domains from database"""
        try:
            print("\n🔍 Checking deployed domains in database...")
            deployments = DatabaseConnection.execute_query(
                "SELECT id, url, site_folder, status FROM deployments WHERE status = 'active'"
            )
            
            domains = []
            for deployment in deployments:
                url = deployment['url']
                
                # Extract domain from URL (remove http://, https://, and port)
                domain = url.replace('http://', '').replace('https://', '')
                if ':' in domain:
                    domain = domain.split(':')[0]
                
                domains.append({
                    'domain': domain,
                    'url': url,
                    'site_folder': deployment['site_folder'],
                    'id': deployment['id'],
                    'status': deployment['status']
                })
                print(f"   Found: {domain} ({deployment['site_folder']})")
            
            print(f"✓ Total deployments: {len(domains)}")
            return domains
            
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            return []
    
    def check_db_exists(self, site_folder):
        """Check if database exists for deployment"""
        try:
            # Extract site ID from folder name
            site_id = site_folder.split('_')[-1]
            db_name = f"site_{site_id}"
            
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                print(f"   ✓ Database exists: {db_name}")
                return True
            else:
                print(f"   ⚠ Database NOT found: {db_name}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking database: {e}")
            return False
    
    def check_hosts_entry(self, domain, ip='127.0.0.1'):
        """Check if domain is in /etc/hosts"""
        try:
            with open(self.hosts_file, 'r') as f:
                content = f.read()
                
            # Look for the domain (not commented out)
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    if domain in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            entry_ip = parts[0]
                            entry_domain = parts[1]
                            
                            if entry_domain == domain:
                                print(f"   ✓ Entry exists: {entry_ip}  {domain}")
                                return True, entry_ip
            
            print(f"   ⚠ Entry NOT found in /etc/hosts: {domain}")
            return False, None
            
        except Exception as e:
            print(f"   ❌ Error reading /etc/hosts: {e}")
            return False, None
    
    def add_hosts_entry(self, domain, ip='127.0.0.1'):
        """Add domain to /etc/hosts"""
        try:
            entry = f"{ip}       {domain}"
            
            # Use echo with sudo to append
            cmd = f"echo '{entry}' >> {self.hosts_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✓ Added to /etc/hosts: {entry}")
                self.added_domains.append(domain)
                return True
            else:
                print(f"   ❌ Failed to add entry: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error adding entry: {e}")
            return False
    
    def verify_domain_resolution(self, domain):
        """Verify domain resolves to localhost"""
        try:
            result = subprocess.run(['nslookup', domain], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                # Check if resolves to 127.0.0.1
                if '127.0.0.1' in result.stdout or 'localhost' in result.stdout:
                    print(f"   ✓ Domain resolves correctly: {domain}")
                    return True
                else:
                    print(f"   ⚠ Domain resolves but not to 127.0.0.1")
                    return False
            else:
                print(f"   ⚠ Domain resolution check inconclusive")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⚠ Domain resolution timeout")
            return False
        except Exception as e:
            print(f"   ⚠ Cannot verify domain resolution: {e}")
            return False
    
    def verify_all_domains(self):
        """Verify all deployed domains"""
        print("\n" + "="*60)
        print("🔐 DOMAIN VERIFICATION & SETUP")
        print("="*60)
        
        # Get deployments from database
        domains = self.get_deployed_domains()
        
        if not domains:
            print("❌ No active deployments found")
            return
        
        # Backup /etc/hosts
        self.backup_hosts()
        
        print("\n📋 Verifying each domain:")
        print("-" * 60)
        
        for domain_info in domains:
            domain = domain_info['domain']
            site_folder = domain_info['site_folder']
            
            print(f"\n🌐 Domain: {domain}")
            print(f"   Folder: {site_folder}")
            
            # 1. Check if database exists
            print("   Checking database...")
            db_exists = self.check_db_exists(site_folder)
            
            # 2. Check if in /etc/hosts
            print("   Checking /etc/hosts...")
            in_hosts, current_ip = self.check_hosts_entry(domain)
            
            # 3. If in database but not in /etc/hosts, add it
            if db_exists and not in_hosts:
                print(f"   ➕ Adding domain to /etc/hosts...")
                if self.add_hosts_entry(domain):
                    self.verified_domains.append(domain)
                else:
                    self.failed_domains.append(domain)
            elif db_exists and in_hosts:
                self.verified_domains.append(domain)
            else:
                self.failed_domains.append(domain)
            
            # 4. Verify resolution
            if in_hosts or db_exists:
                print("   Verifying resolution...")
                self.verify_domain_resolution(domain)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*60)
        print("📊 VERIFICATION SUMMARY")
        print("="*60)
        
        print(f"\n✓ Verified Domains: {len(self.verified_domains)}")
        for domain in self.verified_domains:
            print(f"   ✓ {domain}")
        
        if self.added_domains:
            print(f"\n✅ Newly Added: {len(self.added_domains)}")
            for domain in self.added_domains:
                print(f"   ➕ {domain}")
        
        if self.failed_domains:
            print(f"\n❌ Failed/Missing: {len(self.failed_domains)}")
            for domain in self.failed_domains:
                print(f"   ✗ {domain}")
        
        print("\n" + "="*60)
        print("📝 Current /etc/hosts entries:")
        print("-" * 60)
        
        try:
            result = subprocess.run(['grep', '127.0.0.1', self.hosts_file], 
                                  capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith('#'):
                        print(f"   {line}")
        except:
            pass
        
        print("="*60)
        print("\n✅ Domain verification completed!")
        print("\nNext steps:")
        print("  1. Verify domains in browser: http://yourdomain.com")
        print("  2. If still not working, try: sudo systemctl restart systemd-resolved")
        print("  3. Check logs: tail -f /var/log/deployment-system.log")

def main():
    """Main entry point"""
    try:
        verifier = DomainVerifier()
        verifier.verify_all_domains()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
