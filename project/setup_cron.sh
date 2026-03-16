#!/bin/bash

# setup_cron.sh
# Setup automated cron jobs for deployment system maintenance
# Run with: chmod +x setup_cron.sh && ./setup_cron.sh

echo "🤖 Setting up Cron Jobs for Deployment System"
echo "=============================================="
echo ""

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
SCHEDULER_SCRIPT="$PROJECT_DIR/scheduler.py"
LOG_DIR="$PROJECT_DIR/logs"
CRON_LOG="/var/log/deployment-system.log"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "📁 Project directory: $PROJECT_DIR"
echo "🐍 Python binary: $PYTHON_BIN"
echo ""

# Check if Python venv exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Error: Python virtual environment not found at $PYTHON_BIN"
    echo "Run: cd $PROJECT_DIR && python3 -m venv venv"
    exit 1
fi

# Check if scheduler.py exists
if [ ! -f "$SCHEDULER_SCRIPT" ]; then
    echo "❌ Error: scheduler.py not found at $SCHEDULER_SCRIPT"
    exit 1
fi

# Menu
echo "Choose cron setup method:"
echo ""
echo "1) Setup using crontab (personal user cronjobs)"
echo "2) Setup using systemd service + timer (recommended)"
echo "3) Setup both"
echo "4) Remove all cron jobs"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1|3)
        echo ""
        echo "📝 Setting up crontab entries..."
        
        # Get current user
        CURRENT_USER=$(whoami)
        
        # Create temporary cron file
        TEMP_CRON=$(mktemp)
        
        # Get existing crontab (if any)
        crontab -l 2>/dev/null > "$TEMP_CRON" || true
        
        # Check if our jobs already exist
        if grep -q "deployment-scheduler" "$TEMP_CRON" 2>/dev/null; then
            echo "⚠ Cron jobs already exist for this user"
            echo "Remove old entries first? (y/n)"
            read -p "> " remove_old
            if [ "$remove_old" = "y" ]; then
                grep -v "deployment-scheduler" "$TEMP_CRON" > "${TEMP_CRON}.new"
                mv "${TEMP_CRON}.new" "$TEMP_CRON"
            fi
        fi
        
        # Add new cron jobs
        cat >> "$TEMP_CRON" << 'EOF'

# ===== Deployment System - Automated Tasks =====
# Daily: Old deployment cleanup (2:00 AM)
0 2 * * * cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python scheduler.py cleanup_old_deployments >> /var/log/deployment-system.log 2>&1

# Daily: Database maintenance (2:15 AM)
15 2 * * * cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python -c "from scheduler import DeploymentScheduler; DeploymentScheduler.database_maintenance()" >> /var/log/deployment-system.log 2>&1

# Daily: Database backup (2:30 AM)
30 2 * * * cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python -c "from scheduler import DeploymentScheduler; DeploymentScheduler.backup_databases()" >> /var/log/deployment-system.log 2>&1

# Hourly: Deployment health check
0 * * * * cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python -c "from scheduler import DeploymentScheduler; DeploymentScheduler.check_deployment_health()" >> /var/log/deployment-system.log 2>&1

# Hourly: Disk space check
30 * * * * cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python -c "from scheduler import DeploymentScheduler; DeploymentScheduler.disk_space_check()" >> /var/log/deployment-system.log 2>&1

# Weekly: Log cleanup (Sunday 3:00 AM)
0 3 * * 0 cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python -c "from scheduler import DeploymentScheduler; DeploymentScheduler.cleanup_logs()" >> /var/log/deployment-system.log 2>&1

# Weekly: Status report (Sunday 3:30 AM)
30 3 * * 0 cd /home/ulu/rentalflow/project && /home/ulu/rentalflow/project/venv/bin/python -c "from scheduler import DeploymentScheduler; DeploymentScheduler.generate_status_report()" >> /var/log/deployment-system.log 2>&1
# ===== End Deployment System Tasks =====

EOF
        
        # Install crontab
        crontab "$TEMP_CRON"
        rm "$TEMP_CRON"
        
        echo "✅ Crontab updated successfully"
        echo ""
        echo "Installed cron jobs (all times in system timezone):"
        crontab -l 2>/dev/null | grep -A 10 "deployment-scheduler" || crontab -l | tail -15
        echo ""
        ;;
    2|3)
        echo ""
        echo "🔧 Setting up systemd service + timer..."
        
        # Create systemd service file
        SERVICE_FILE="/etc/systemd/system/deployment-scheduler.service"
        TIMER_FILE="/etc/systemd/system/deployment-scheduler.timer"
        
        echo "Creating systemd service..."
        
        # Check if running as root (needed for systemd)
        if [ "$EUID" -ne 0 ]; then
            echo "⚠ Warning: systemd setup requires sudo"
            echo "Run with: sudo $0"
            echo ""
        fi
        
        # Create service file
        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Deployment System Background Scheduler
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON_BIN $SCHEDULER_SCRIPT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        echo "✓ Service file created: $SERVICE_FILE"
        echo ""
        echo "Next steps to enable systemd service:"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable deployment-scheduler.service"
        echo "  sudo systemctl start deployment-scheduler.service"
        echo ""
        echo "Monitor service:"
        echo "  sudo systemctl status deployment-scheduler.service"
        echo "  sudo journalctl -u deployment-scheduler.service -f"
        echo ""
        ;;
    4)
        echo ""
        echo "❌ Removing cron jobs..."
        
        # Remove from crontab
        if crontab -l 2>/dev/null | grep -q "deployment-scheduler"; then
            TEMP_CRON=$(mktemp)
            crontab -l 2>/dev/null | grep -v "deployment-scheduler" > "$TEMP_CRON"
            crontab "$TEMP_CRON"
            rm "$TEMP_CRON"
            echo "✓ Removed crontab entries"
        fi
        
        # Remove systemd files
        if [ -f "/etc/systemd/system/deployment-scheduler.service" ]; then
            echo "Removing systemd service..."
            sudo systemctl stop deployment-scheduler.service 2>/dev/null || true
            sudo systemctl disable deployment-scheduler.service 2>/dev/null || true
            sudo rm /etc/systemd/system/deployment-scheduler.service
            sudo systemctl daemon-reload
            echo "✓ Removed systemd service"
        fi
        
        echo "✓ All cron jobs removed"
        echo ""
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo "════════════════════════════════════"
echo "✅ Cron setup completed!"
echo ""
echo "📋 Scheduled Tasks:"
echo "  • Daily cleanup of old deployments (2:00 AM)"
echo "  • Daily database maintenance (2:15 AM)"
echo "  • Daily database backup (2:30 AM)"
echo "  • Hourly deployment health check"
echo "  • Hourly disk space check"
echo "  • Weekly log cleanup (Sunday 3:00 AM)"
echo "  • Weekly status report (Sunday 3:30 AM)"
echo ""
echo "📝 View logs:"
echo "  tail -f /var/log/deployment-system.log"
echo ""
