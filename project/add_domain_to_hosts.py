#!/usr/bin/env python3

"""
add_domain_to_hosts.py
Helper script to add domains to /etc/hosts on Linux
Run with: sudo python3 add_domain_to_hosts.py domain.com
"""

import sys
import os
import subprocess
from datetime import datetime

HOSTS_FILE = '/etc/hosts'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'

def check_root():
    """Check if script is running as root"""
    if os.geteuid() != 0:
        print(f"{COLOR_RED}❌ Error: This script must be run with sudo{COLOR_RESET}")
        print("Usage: sudo python3 add_domain_to_hosts.py domain.com")
        sys.exit(1)

def backup_hosts():
    """Create backup of /etc/hosts"""
    backup_file = f"{HOSTS_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        subprocess.run(['cp', HOSTS_FILE, backup_file], check=True)
        print(f"{COLOR_GREEN}✓{COLOR_RESET} Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"{COLOR_YELLOW}⚠{COLOR_RESET} Warning: Could not backup: {e}")
        return None

def domain_exists(domain, ip='127.0.0.1'):
    """Check if domain already exists in /etc/hosts"""
    try:
        with open(HOSTS_FILE, 'r') as f:
            content = f.read()
            # Check for exact match or similar
            for line in content.split('\n'):
                if domain in line and not line.strip().startswith('#'):
                    return True
        return False
    except Exception as e:
        print(f"{COLOR_RED}❌ Error reading {HOSTS_FILE}: {e}{COLOR_RESET}")
        return False

def add_domain(domain, ip='127.0.0.1'):
    """Add domain to /etc/hosts"""
    if domain_exists(domain, ip):
        print(f"{COLOR_GREEN}✓{COLOR_RESET} Domain already exists: {domain}")
        return True
    
    try:
        with open(HOSTS_FILE, 'a') as f:
            f.write(f"{ip}       {domain}\n")
        print(f"{COLOR_GREEN}✓{COLOR_RESET} Added to /etc/hosts: {ip}       {domain}")
        return True
    except Exception as e:
        print(f"{COLOR_RED}❌ Error writing to {HOSTS_FILE}: {e}{COLOR_RESET}")
        return False

def verify_domain(domain):
    """Verify domain is in /etc/hosts"""
    try:
        result = subprocess.run(['grep', domain, HOSTS_FILE], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{COLOR_GREEN}✓{COLOR_RESET} Verification: Domain found in /etc/hosts")
            print(f"  {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"{COLOR_YELLOW}⚠{COLOR_RESET} Verification failed: {e}")
        return False

def main():
    """Main function"""
    print(f"{COLOR_GREEN}🐧 Linux /etc/hosts Manager{COLOR_RESET}")
    print("=" * 50)
    
    # Check if running as root
    check_root()
    
    # Get domain from command line
    if len(sys.argv) < 2:
        print(f"\n{COLOR_YELLOW}Usage:{COLOR_RESET} sudo python3 add_domain_to_hosts.py DOMAIN [IP]")
        print(f"\n{COLOR_YELLOW}Examples:{COLOR_RESET}")
        print("  sudo python3 add_domain_to_hosts.py sundar.com")
        print("  sudo python3 add_domain_to_hosts.py myshop.local")
        print("  sudo python3 add_domain_to_hosts.py custom.com 192.168.1.100")
        sys.exit(1)
    
    domain = sys.argv[1].lower()
    ip = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
    
    print(f"\n📝 Adding domain to /etc/hosts:")
    print(f"  Domain: {domain}")
    print(f"  IP: {ip}")
    print(f"  File: {HOSTS_FILE}")
    print()
    
    # Backup
    backup_file = backup_hosts()
    
    # Add domain
    if add_domain(domain, ip):
        # Verify
        verify_domain(domain)
        print(f"\n{COLOR_GREEN}✅ Success!{COLOR_RESET}")
        print(f"\nYou can now access: {COLOR_GREEN}http://{domain}{COLOR_RESET}")
        
        if backup_file:
            print(f"\n{COLOR_YELLOW}💾 Backup saved:{COLOR_RESET} {backup_file}")
            print(f"   Restore if needed: sudo cp {backup_file} {HOSTS_FILE}")
    else:
        print(f"\n{COLOR_RED}❌ Failed to add domain{COLOR_RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
