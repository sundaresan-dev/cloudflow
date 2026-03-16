from flask import Blueprint, request, jsonify, session
from config import Config
from database.db_connection import DatabaseConnection
import os
import shutil
from datetime import datetime
import uuid
import subprocess
import socket
import random
import string

deploy_bp = Blueprint('deploy', __name__, url_prefix='/deploy')

def check_public_dns(domain):
    """Check if a domain has active public DNS records (exists in real TLDs)"""
    try:
        # Check for A or AAAA records
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False

def generate_suggestions(domain):
    """Generate alternative domain names if the requested one is taken"""
    parts = domain.split('.')
    name = parts[0]
    tld = '.'.join(parts[1:]) if len(parts) > 1 else 'com'
    
    suffixes = ['hub', 'flow', 'plus', 'site', 'app', 'online', 'cloud', 'pro']
    prefixes = ['get', 'my', 'the', 'go']
    
    suggestions = []
    
    # 1. Add suffix
    for _ in range(3):
        suffix = random.choice(suffixes)
        suggestions.append(f"{name}{suffix}.{tld}")
    
    # 2. Add prefix
    for _ in range(2):
        prefix = random.choice(prefixes)
        suggestions.append(f"{prefix}{name}.{tld}")
    
    # 3. Add random digits
    suggestions.append(f"{name}{''.join(random.choices(string.digits, k=3))}.{tld}")
    
    # Filter out duplicates and the original
    unique_suggestions = list(set(suggestions))
    if domain in unique_suggestions:
        unique_suggestions.remove(domain)
        
    return unique_suggestions[:5]

WEBSITE_TYPES = {
    'ecommerce': 'E-commerce',
    'school': 'School Management',
    'college': 'College Management',
    'hotel': 'Hotel Management'
}

def get_available_templates():
    """Get list of available website templates"""
    templates_path = Config.TEMPLATES_PATH
    templates = []
    
    if os.path.exists(templates_path):
        for template_name in os.listdir(templates_path):
            template_path = os.path.join(templates_path, template_name)
            if os.path.isdir(template_path) and template_name in WEBSITE_TYPES:
                templates.append({
                    'id': template_name,
                    'name': WEBSITE_TYPES[template_name],
                    'path': template_path
                })
    
    return templates

def generate_domain_name(website_name, site_id):
    """Generate a unique domain name from website name"""
    # Convert website name to domain-friendly format
    domain = website_name.lower().replace(' ', '-').replace('_', '-')
    domain = ''.join(c for c in domain if c.isalnum() or c == '-')
    domain = domain[:20]  # Limit length
    domain = f"{domain}-{site_id[:4]}.local"
    return domain

def add_domain_to_dnsmasq(domain):
    """Add custom domain to dnsmasq configuration for DNS resolution"""
    try:
        dnsmasq_conf = '/etc/dnsmasq.d/deployment-system'
        
        # Check if domain already exists in dnsmasq config
        try:
            with open(dnsmasq_conf, 'r') as f:
                if f"address=/{domain}/" in f.read():
                    print(f"✓ Domain {domain} already in dnsmasq config")
                    return True
        except:
            pass
        
        # Add domain to dnsmasq configuration
        dnsmasq_entry = f"address=/{domain}/127.0.0.1"
        
        try:
            # Try with sudo
            cmd = f"echo '{dnsmasq_entry}' | sudo tee -a {dnsmasq_conf} > /dev/null 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Reload dnsmasq
                subprocess.run(['sudo', 'systemctl', 'reload', 'dnsmasq'], 
                             capture_output=True, timeout=5)
                print(f"✓ Added domain to dnsmasq: {domain}")
                return True
        except Exception as e:
            print(f"Note: Could not add to dnsmasq: {e}")
        
        return False
    except Exception as e:
        print(f"Error in add_domain_to_dnsmasq: {e}")
        return False

def add_domain_to_hosts(domain, deployed_path):
    """Add custom domain to /etc/hosts and set up Nginx to serve the site"""
    try:
        hosts_file = '/etc/hosts'
        
        # Check if domain already exists in /etc/hosts
        try:
            with open(hosts_file, 'r') as f:
                hosts_content = f.read()
                if domain in hosts_content:
                    print(f"✓ Domain {domain} already in /etc/hosts")
                    generate_nginx_config(domain, deployed_path)
                    return True
        except Exception as e:
            print(f"Note: Could not read /etc/hosts: {e}")
        
        # Add to /etc/hosts using sudo -n tee (passwordless)
        try:
            cmd = f"echo '127.0.0.1       {domain}' | sudo -n tee -a {hosts_file} > /dev/null 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ Added domain to /etc/hosts: {domain}")
                generate_nginx_config(domain, deployed_path)
                return True
        except Exception as e:
            print(f"Note: Sudo tee failed: {e}")
        
        # Fallback: direct write
        try:
            with open(hosts_file, 'a') as f:
                f.write(f"127.0.0.1       {domain}\n")
            print(f"✓ Added domain to /etc/hosts: {domain}")
            generate_nginx_config(domain, deployed_path)
            return True
        except PermissionError:
            print(f"⚠ Cannot write to /etc/hosts (permission denied)")
            print(f"  Run: sudo bash -c 'echo \"127.0.0.1       {domain}\" >> /etc/hosts'")
            generate_nginx_config(domain, deployed_path)
            return False
        
    except Exception as e:
        print(f"Error in add_domain_to_hosts: {e}")
        return False

def generate_nginx_config(domain, deployed_path):
    """Generate Nginx configuration for a domain to serve static files"""
    try:
        nginx_conf_dir = '/etc/nginx/sites-available'
        config_file = os.path.join(nginx_conf_dir, domain)
        
        nginx_config = f"""server {{
    listen 80;
    server_name {domain} www.{domain};

    root {deployed_path};
    index index.html;

    location / {{
        try_files $uri $uri/ /index.html;
    }}

    location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
        
        # Write config to temp file, then sudo copy it
        import tempfile
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as tmp:
                tmp.write(nginx_config)
                tmp_path = tmp.name
            
            cmd = f"sudo -n cp {tmp_path} {config_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            os.unlink(tmp_path)  # Clean up temp file
            
            if result.returncode == 0:
                print(f"✓ Created Nginx config: {config_file}")
            else:
                print(f"⚠ Could not write Nginx config: {result.stderr}")
        except Exception as e:
            print(f"⚠ Error writing Nginx config: {e}")
        
        # Enable the site by creating symlink
        try:
            enabled_link = f'/etc/nginx/sites-enabled/{domain}'
            cmd = f"sudo -n ln -sf {config_file} {enabled_link}"
            subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            print(f"✓ Enabled Nginx site: {domain}")
        except Exception as e:
            print(f"⚠ Error enabling site: {e}")
        
        # Reload Nginx
        try:
            subprocess.run(['sudo', '-n', 'systemctl', 'reload', 'nginx'],
                         capture_output=True, timeout=5)
            print(f"✓ Nginx reloaded")
        except Exception as e:
            print(f"⚠ Error reloading Nginx: {e}")
        
        return True
    except Exception as e:
        print(f"Error generating Nginx config: {e}")
        return False

def create_deployment_database(user_id, site_id, website_type):
    """Create a new database for the deployment"""
    db_name = f"site_{site_id}"
    
    try:
        # Create database
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"Database created: {db_name}")
        return db_name
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return None

@deploy_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get list of available templates"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    templates = get_available_templates()
    return jsonify({
        'success': True,
        'templates': templates
    }), 200

@deploy_bp.route('/create', methods=['POST'])
def create_deployment():
    """Deploy a website"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    website_type = data.get('website_type', '').lower()
    website_name = data.get('website_name', '').strip()
    custom_domain = data.get('custom_domain', '').strip().lower()
    
    if website_type not in WEBSITE_TYPES:
        return jsonify({'success': False, 'message': 'Invalid website type'}), 400
    
    if not website_name:
        return jsonify({'success': False, 'message': 'Website name is required'}), 400
    
    if not custom_domain:
        return jsonify({'success': False, 'message': 'Custom domain is required'}), 400
    
    # Validate domain format
    import re
    domain_regex = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\.[a-z]{2,}$'
    if not re.match(domain_regex, custom_domain):
        return jsonify({'success': False, 'message': 'Invalid domain format. Use format like: sundar.com or mysite.co.uk'}), 400
    
    # Check if domain already exists
    existing_domain = DatabaseConnection.execute_query(
        "SELECT id FROM deployments WHERE url LIKE %s",
        (f"%{custom_domain}%",),
        fetch_one=True
    )
    if existing_domain:
        suggestions = generate_suggestions(custom_domain)
        return jsonify({
            'success': False, 
            'message': 'This domain is already registered in our system',
            'suggestions': suggestions
        }), 400
    
    # Check if domain exists in real TLDs
    if check_public_dns(custom_domain):
        suggestions = generate_suggestions(custom_domain)
        return jsonify({
            'success': False, 
            'message': 'This domain is already registered in real-world TLDs (e.g., .com, .net)',
            'suggestions': suggestions
        }), 400
    
    user_id = session['user_id']
    
    # Check deployment limit
    deployments = DatabaseConnection.execute_query(
        "SELECT COUNT(*) as count FROM deployments WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    
    if deployments and deployments['count'] >= Config.MAX_DEPLOYMENTS_PER_USER:
        return jsonify({
            'success': False,
            'message': f'You have reached the deployment limit of {Config.MAX_DEPLOYMENTS_PER_USER}'
        }), 403
    
    try:
        # Generate unique site ID
        site_id = str(uuid.uuid4())[:8]
        site_folder = f"site_{site_id}"
        
        # Assign a unique port for this deployment (starting from 5001)
        allocation = DatabaseConnection.execute_query(
            "SELECT MAX(CAST(SUBSTRING_INDEX(url, ':', -1) AS UNSIGNED)) as max_port FROM deployments WHERE url LIKE '%:50%'",
            fetch_one=True
        )
        assigned_port = 5001 if not allocation or not allocation['max_port'] else allocation['max_port'] + 1
        
        # Paths
        template_path = os.path.join(Config.TEMPLATES_PATH, website_type)
        deployed_path = os.path.join(Config.DEPLOYED_SITES_PATH, site_folder)
        
        if not os.path.exists(template_path):
            return jsonify({'success': False, 'message': 'Template not found'}), 404
        
        # Step 1 & 2: Copy template to deployed_sites
        if os.path.exists(deployed_path):
            shutil.rmtree(deployed_path)
        
        shutil.copytree(template_path, deployed_path)
        print(f"Template copied to: {deployed_path}")
        
        # Step 3: Create database for this deployment
        db_name = create_deployment_database(user_id, site_id, website_type)
        if not db_name:
            raise Exception("Failed to create database")
        
        # Import SQL file if exists
        sql_file = os.path.join(deployed_path, 'database.sql')
        if os.path.exists(sql_file):
            DatabaseConnection.import_sql_file(sql_file, db_name)
        
        # Ensure deployed_sites directory is readable by Nginx
        try:
            subprocess.run(f"sudo -n chmod o+x /home/ulu /home/ulu/rentalflow /home/ulu/rentalflow/project",
                         shell=True, capture_output=True, timeout=5)
            subprocess.run(f"sudo -n chmod -R o+rx {deployed_path}",
                         shell=True, capture_output=True, timeout=5)
        except:
            pass
        
        # Add custom domain to /etc/hosts and generate Nginx config
        add_domain_to_hosts(custom_domain, deployed_path)
        
        # Step 4 & 5: Save deployment record with custom domain URL
        deployment_url = f"http://{custom_domain}"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        deployment_id = DatabaseConnection.execute_update(
            """INSERT INTO deployments 
               (user_id, website_type, site_folder, status, url, created_at) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, website_type, site_folder, 'active', deployment_url, now)
        )
        
        if not deployment_id:
            raise Exception("Failed to save deployment record")
        
        # Create a simple index.html in deployed folder to serve the website
        create_deployment_server_file(deployed_path, db_name)
        
        # Prepare setup instructions for Linux users
        setup_instructions = {
            'domain': custom_domain,
            'backend_port': assigned_port,
            'method_1': f"sudo python3 add_domain_to_hosts.py {custom_domain}",
            'method_2': f"sudo bash -c 'echo \"127.0.0.1       {custom_domain}\" >> /etc/hosts'",
            'method_3': "Edit /etc/hosts file manually: sudo nano /etc/hosts"
        }
        
        return jsonify({
            'success': True,
            'message': 'Website deployed successfully',
            'deployment': {
                'id': deployment_id,
                'site_folder': site_folder,
                'domain': custom_domain,
                'url': deployment_url,
                'port': assigned_port,
                'database': db_name,
                'status': 'active'
            },
            'setup_instructions': setup_instructions
        }), 201
        
    except Exception as e:
        print(f"Error creating deployment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@deploy_bp.route('/list', methods=['GET'])
def list_deployments():
    """Get list of user's deployments"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    deployments = DatabaseConnection.execute_query(
        """SELECT id, website_type, site_folder, status, url, created_at 
           FROM deployments WHERE user_id = %s ORDER BY created_at DESC""",
        (user_id,)
    )
    
    if not deployments:
        deployments = []
    
    return jsonify({
        'success': True,
        'deployments': deployments
    }), 200

@deploy_bp.route('/delete/<int:deployment_id>', methods=['DELETE'])
def delete_deployment(deployment_id):
    """Delete a deployment"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Check if deployment belongs to user
    deployment = DatabaseConnection.execute_query(
        "SELECT site_folder FROM deployments WHERE id = %s AND user_id = %s",
        (deployment_id, user_id),
        fetch_one=True
    )
    
    if not deployment:
        return jsonify({'success': False, 'message': 'Deployment not found'}), 404
    
    try:
        # Delete deployed files
        deployed_path = os.path.join(Config.DEPLOYED_SITES_PATH, deployment['site_folder'])
        if os.path.exists(deployed_path):
            shutil.rmtree(deployed_path)
        
        # Delete from database
        DatabaseConnection.execute_update(
            "DELETE FROM deployments WHERE id = %s",
            (deployment_id,)
        )
        
        return jsonify({
            'success': True,
            'message': 'Deployment deleted successfully'
        }), 200
        
    except Exception as e:
        print(f"Error deleting deployment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def create_deployment_server_file(deployed_path, db_name):
    """Create a server file for the deployment with database connection"""
    # Create a simple config file
    config_content = f"""<!-- Deployment Configuration -->
<!-- This deployment uses database: {db_name} -->
<!-- Database Host: {Config.DB_HOST} -->
<!-- Database User: {Config.DB_USER} -->
"""
    
    config_path = os.path.join(deployed_path, 'config.txt')
    with open(config_path, 'w') as f:
        f.write(config_content)
