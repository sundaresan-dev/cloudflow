#!/bin/bash

# setup_domains_linux.sh
# Add deployed domains to /etc/hosts on Linux systems
# Run with: chmod +x setup_domains_linux.sh && sudo ./setup_domains_linux.sh

echo "🐧 Linux /etc/hosts Setup for Deployed Domains"
echo "================================================"

HOSTS_FILE="/etc/hosts"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${HOSTS_FILE}.backup_${BACKUP_DATE}"

# Backup /etc/hosts
echo ""
echo "📦 Creating backup of /etc/hosts..."
sudo cp "$HOSTS_FILE" "$BACKUP_FILE"
echo "✓ Backup created: $BACKUP_FILE"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run with sudo"
   echo "Usage: sudo ./setup_domains_linux.sh"
   exit 1
fi

# Function to add domain to /etc/hosts
add_domain() {
    local domain=$1
    local ip=${2:-"127.0.0.1"}
    
    # Check if domain already exists
    if grep -q "^${ip}.*${domain}" "$HOSTS_FILE"; then
        echo "✓ Domain already exists: $domain"
        return 0
    fi
    
    # Add domain
    echo "${ip}       ${domain}" >> "$HOSTS_FILE"
    echo "✓ Added domain: $domain → $ip"
    return 0
}

# Add common development domains
echo ""
echo "📝 Adding standard domains to /etc/hosts..."
add_domain "localhost" "127.0.0.1"
add_domain "deployment.local" "127.0.0.1"

# Add domains from user (if provided as arguments)
for domain in "$@"; do
    echo ""
    echo "Adding custom domain: $domain"
    add_domain "$domain" "127.0.0.1"
done

# Instructions for admin
echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📌 Your /etc/hosts has been updated:"
echo ""
echo "File location: $HOSTS_FILE"
echo "Backup: $BACKUP_FILE"
echo ""
echo "Current domains in /etc/hosts:"
grep -E "127.0.0.1|localhost" "$HOSTS_FILE" | grep -v "^#" | tail -10
echo ""
echo "🌐 Add more domains anytime:"
echo ""
echo "   Option 1: Use this script again"
echo "   $ sudo ./setup_domains_linux.sh domain1.com domain2.com"
echo ""
echo "   Option 2: Manually add to /etc/hosts"
echo "   $ sudo bash -c 'echo \"127.0.0.1       yourdomain.com\" >> /etc/hosts'"
echo ""
echo "   Option 3: Edit directly"
echo "   $ sudo nano /etc/hosts"
echo ""
echo "✨ Next steps:"
echo "   1. Deploy websites at: http://deployment.local:8080"
echo "   2. For each deployed domain:"
echo "      $ sudo ./setup_domains_linux.sh yourdomain.com"
echo "   3. Access sites at: http://yourdomain.com"
echo ""
