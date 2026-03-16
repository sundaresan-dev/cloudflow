#!/usr/bin/env python3
import os
import subprocess
import sys
import time

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")
REQS_FILE = os.path.join(BASE_DIR, "requirements.txt")
USER = "ulu"  # Default user for sudoers

def run_command(cmd, shell=True, check=True, capture_output=False):
    """Utility to run shell commands and handle errors."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=shell, check=check, text=True, capture_output=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=shell, check=check)
            return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error executing: {cmd}")
        if capture_output:
            print(f"Error output: {e.stderr}")
        return False

def print_header(text):
    print("\n" + "="*60)
    print(f"🚀 {text}")
    print("="*60 + "\n")

def check_sudo():
    if os.geteuid() != 0:
        print("❌ This script MUST be run with sudo.")
        print("Usage: sudo python3 start.py")
        sys.exit(1)

def setup_system_packages():
    print_header("Step 1: Installing System Dependencies")
    run_command("apt update -y")
    run_command("apt install -y python3-pip python3-venv mysql-server nginx")
    
    # Ensure services are started
    run_command("systemctl start mysql")
    run_command("systemctl enable mysql")
    run_command("systemctl start nginx")
    run_command("systemctl enable nginx")

def setup_mysql():
    print_header("Step 2: Configuring MySQL Database")
    # Create flaskapp user if not exists and grant permissions
    mysql_cmds = [
        "CREATE USER IF NOT EXISTS 'flaskapp'@'localhost' IDENTIFIED BY 'flaskapp123';",
        "GRANT ALL PRIVILEGES ON *.* TO 'flaskapp'@'localhost' WITH GRANT OPTION;",
        "FLUSH PRIVILEGES;"
    ]
    for cmd in mysql_cmds:
        run_command(f'mysql -e "{cmd}"')
    
    print("✅ MySQL user 'flaskapp' configured successfully.")

def setup_python_env():
    print_header("Step 3: Setting Up Python Virtual Environment")
    if not os.path.exists(VENV_DIR):
        print("📦 Creating virtual environment...")
        run_command(f"python3 -m venv {VENV_DIR}")
    
    print("📦 Installing python dependencies...")
    run_command(f"{VENV_DIR}/bin/pip install -r {REQS_FILE}")
    print("✅ Virtual environment ready.")

def setup_sudoers():
    print_header("Step 4: Configuring Passwordless Sudo for Nginx")
    sudoers_path = "/etc/sudoers.d/deployment-system"
    sudoers_content = f"{USER} ALL=(ALL) NOPASSWD: /usr/bin/tee -a /etc/hosts, /usr/bin/tee /etc/nginx/sites-available/*, /bin/ln -sf /etc/nginx/sites-available/* /etc/nginx/sites-enabled/*, /usr/sbin/nginx -s reload, /bin/systemctl reload nginx, /bin/chmod *, /bin/cp *\n"
    
    with open("/tmp/deployment-system-sudoers", "w") as f:
        f.write(sudoers_content)
    
    run_command(f"mv /tmp/deployment-system-sudoers {sudoers_path}")
    run_command(f"chmod 0440 {sudoers_path}")
    print(f"✅ Sudoers configured for user: {USER}")

def cleanup_broken_symlinks():
    """Remove broken symlinks in Nginx sites-enabled directory."""
    print("🧹 Checking for broken Nginx symlinks...")
    sites_enabled = "/etc/nginx/sites-enabled/"
    if not os.path.exists(sites_enabled):
        return

    for filename in os.listdir(sites_enabled):
        path = os.path.join(sites_enabled, filename)
        if os.path.islink(path) and not os.path.exists(os.path.realpath(path)):
            print(f"⚠️ Removing broken symlink: {path}")
            # Use sudo rm since we are running as root/sudo
            run_command(f"rm {path}")

def setup_nginx():
    print_header("Step 5: Finalizing Nginx Configuration")
    
    # 1. Cleanup broken symlinks that prevent Nginx from starting
    cleanup_broken_symlinks()
    
    # 2. Remove default site if it exists
    if os.path.exists("/etc/nginx/sites-enabled/default"):
        run_command("rm /etc/nginx/sites-enabled/default")
    
    # 3. Validate Nginx configuration before reloading
    print("🔍 Validating Nginx configuration...")
    if run_command("nginx -t"):
        run_command("systemctl reload nginx")
        print("✅ Nginx ready and configuration reloaded.")
    else:
        print("❌ Nginx configuration is invalid! Attempting to start service anyway...")
        run_command("systemctl start nginx")

def launch_apps():
    print_header("Step 6: Launching Cloud Deployment System")
    
    # Start app.py in background
    flask_log = "/home/ulu/rentalflow/project/logs/flask.log"
    os.makedirs(os.path.dirname(flask_log), exist_ok=True)
    
    print("🔥 Starting Flask Admin App (Port 8080)...")
    subprocess.Popen(
        [f"{VENV_DIR}/bin/python", "app.py"],
        stdout=open(flask_log, "a"),
        stderr=subprocess.STDOUT,
        cwd=BASE_DIR
    )
    
    # Start scheduler.py in background
    scheduler_log = "/home/ulu/rentalflow/project/logs/scheduler.log"
    print("🔥 Starting Background Maintenance Scheduler...")
    subprocess.Popen(
        [f"{VENV_DIR}/bin/python", "scheduler.py"],
        stdout=open(scheduler_log, "a"),
        stderr=subprocess.STDOUT,
        cwd=BASE_DIR
    )
    
    print("\n" + "*"*60)
    print("🎉 ALL SYSTEMS ONLINE!")
    print(f"🔗 Admin UI: http://localhost:8080")
    print(f"📄 Logs: {BASE_DIR}/logs/")
    print("*"*60 + "\n")
    print("The system is now running in the background. You can close this terminal.")

if __name__ == "__main__":
    try:
        check_sudo()
        setup_system_packages()
        setup_mysql()
        setup_python_env()
        setup_sudoers()
        setup_nginx()
        launch_apps()
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
