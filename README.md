# RentalFlow - Cloud-Based Website Deployment System

A powerful, automated platform for deploying and managing multiple custom websites with personalized domains. Deploy fully-functional websites in minutes with real-time domain management and scheduled automation.

## 🎯 Features

- **One-Click Deployment**: Deploy custom websites with a simple form
- **Custom Domain Support**: Automatically map custom domains to deployed sites
- **Multiple Templates**: Pre-built templates for E-commerce, School, College, and Hotel websites
- **MySQL Integration**: Individual databases for each deployment
- **Domain Auto-Management**: Automatic /etc/hosts configuration (Linux)
- **Reverse Proxy Support**: Nginx integration for seamless domain routing
- **Scheduled Automation**: 7 automated tasks (database backups, cleanup, health checks)
- **User Authentication**: Secure login and registration system
- **Dashboard**: Central hub for managing all deployments
- **Health Monitoring**: Hourly deployment health checks and disk space monitoring

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 2.3.2 |
| **Database** | MySQL 8.0+ |
| **Frontend** | Bootstrap 5, Vanilla JavaScript |
| **Reverse Proxy** | Nginx |
| **Task Scheduling** | Python Schedule 1.2.0 |
| **Automation** | Cron Jobs |

## 📋 Requirements

- Python 3.7+
- MySQL 8.0+
- Nginx
- Linux (or Linux-compatible system)
- Git (for cloning)

## 🚀 Quick Start

### Step 1: Clone & Setup

```bash
git clone https://github.com/yourusername/rentalflow.git
cd rentalflow/project
```

### Step 2: Automated Setup (One Command!)

```bash
sudo python3 start.py
```

The `start.py` script automatically handles:
- ✅ System package installation (Python, MySQL, Nginx)
- ✅ MySQL database and user setup
- ✅ Python virtual environment creation
- ✅ Python dependencies installation
- ✅ Sudoers configuration for seamless domain management
- ✅ Nginx configuration and validation
- ✅ Launches Flask app (port 8080) in background
- ✅ Launches background scheduler for automation tasks

**That's it!** The system is now running automatically.

### Step 3: Verify & Setup Domains (One-time)

```bash
sudo python3 verify_domains.py
```

This script:
- Verifies /etc/hosts accessibility
- Sets up necessary permissions
- Tests domain configuration
- Sets up sudo integration for domain management

### Step 4: Install Cron Automation (Optional)

```bash
sudo ./setup_cron.sh
```

Choose from 3 automation levels:
1. **Full**: All 7 scheduled tasks
2. **Essential**: Backups, cleanup, health checks
3. **Minimal**: Database maintenance only

### Access the System

Once `start.py` completes:
- **Admin Dashboard**: http://localhost:8080
- **Deployed Sites**: http://localhost:5001+ (auto-assigned ports)
- **Logs**: `/home/ulu/rentalflow/project/logs/` (flask.log, scheduler.log)

## ⚙️ What start.py Does

The setup script is fully automated and performs **6 major setup steps**:

| Step | Task | Details |
|------|------|---------|
| 1 | System Packages | Installs Python, pip, MySQL, Nginx via apt |
| 2 | MySQL Setup | Creates `flaskapp` user and grants permissions |
| 3 | Python Environment | Sets up virtual environment and installs dependencies |
| 4 | Sudoers Config | Enables passwordless sudo for deploying sites |
| 5 | Nginx Setup | Validates and configures reverse proxy |
| 6 | Launch Apps | Starts Flask (port 8080) and Scheduler in background |

**Output after setup:**
```
Admin UI: http://localhost:8080
Logs: /home/ulu/rentalflow/project/logs/
```

The system runs entirely in the background - you can close the terminal after setup completes!

## 📁 Project Structure

```
rentalflow/project/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── scheduler.py                    # Automation scheduler (runs background tasks)
├── verify_domains.py              # Domain verification & setup script
├── start.py                       # Combined startup script
├── requirements.txt               # Python dependencies
│
├── routes/
│   ├── auth_routes.py            # Login/Register endpoints
│   └── deploy_routes.py          # Deployment endpoints
│
├── database/
│   └── db_connection.py          # MySQL connection handler
│
├── templates/                     # Admin Dashboard templates
│   ├── base.html                 # Base layout
│   ├── login.html                # Login page
│   ├── register.html             # Registration page
│   ├── dashboard.html            # Main dashboard
│   ├── create.html               # Deployment form
│   └── deployments.html          # View deployments
│
├── static/
│   ├── css/
│   │   └── style.css            # Dashboard styling
│   └── js/
│       ├── common.js            # Shared utilities
│       ├── dashboard.js         # Dashboard interactions
│       ├── create.js            # Deployment form logic
│       ├── login.js             # Login handling
│       └── register.js          # Registration handling
│
├── templates_websites/           # Website templates
│   ├── ecommerce/               # E-commerce template
│   ├── school/                  # School website template
│   ├── college/                 # College website template
│   └── hotel/                   # Hotel website template
│
├── deployed_sites/              # Active deployments (auto-generated)
│   ├── site_XXXXXXXXXXXXX/
│   │   ├── index.html
│   │   ├── config.txt
│   │   ├── database.sql
│   │   └── (other template assets)
│   └── ...
│
├── logs/                        # Application logs
│
└── docs/                        # Documentation (15+ guides)
    ├── COMPLETE_SETUP_GUIDE.md
    └── ...
```

## 🔧 Configuration

> **Note**: `start.py` automatically handles all configuration! Manual setup is only needed for customization.

### Default Configuration (Auto-Setup)

The `start.py` script automatically configures:

```python
# MySQL 
MYSQL_HOST = 'localhost'
MYSQL_USER = 'flaskapp'        # Auto-created
MYSQL_PASSWORD = 'flaskapp123' # Auto-set
MYSQL_DB = 'deployment_system'

# Application Settings
SECRET_KEY = 'your-secret-key'
DEPLOYMENT_PATH = '/home/ulu/rentalflow/project/deployed_sites/'
```

### Manual Customization (Optional)

If you need custom settings, edit `config.py`:

```python
# MySQL Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'flaskapp'
MYSQL_PASSWORD = 'your-secure-password'
MYSQL_DB = 'deployment_system'

# Application Settings
SECRET_KEY = 'your-strong-random-key'
DEPLOYMENT_PATH = '/home/ulu/rentalflow/project/deployed_sites/'
LOG_FILE = '/var/log/deployment-system.log'
```

### Custom Domain Setup

When deploying a website:
1. Enter site name and domain (e.g., `sundar.com`)
2. Select template
3. System automatically:
   - Creates deployment directory
   - Generates unique ID (e.g., `site_0b8be4ea`)
   - Assigns port (5001+)
   - Updates /etc/hosts
   - Configures Nginx proxy
   - Creates MySQL database

Access via: `http://sundar.com` (no port needed!)

## 🤖 Automation Tasks

The scheduler runs 7 tasks on a cron schedule:

| Task | Schedule | Purpose |
|------|----------|---------|
| Deploy Cleanup | Daily 2:00 AM | Remove deployments >30 days old |
| DB Maintenance | Daily 2:15 AM | Optimize MySQL tables |
| DB Backup | Daily 2:30 AM | Backup all deployment databases |
| Health Check | Hourly | Monitor deployment status |
| Disk Monitoring | Every 30 min | Track available disk space |
| Log Cleanup | Weekly Sun 3:00 AM | Archive old logs |
| Status Reports | Weekly Sun 3:30 AM | Generate system reports |

View logs:

```bash
tail -f /var/log/deployment-system.log
```

## 📊 Monitoring

### Application Logs

The `start.py` script automatically manages logs in `/home/ulu/rentalflow/project/logs/`:

```bash
# View Flask app logs
tail -f /home/ulu/rentalflow/project/logs/flask.log

# View scheduler/automation logs
tail -f /home/ulu/rentalflow/project/logs/scheduler.log

# View all logs
ls -la /home/ulu/rentalflow/project/logs/
```

### Check Deployment Status

```bash
# View running deployments and background processes
ps aux | grep python3

# Check MySQL databases and deployments
mysql -u flaskapp -pflaskapp123 -e "SHOW DATABASES;"

# Monitor disk space
df -h /home/ulu/rentalflow/project/
```

## 🨛 Database Schema

Each deployment gets its own MySQL database with:

```sql
-- Users table (per deployment)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table (for e-commerce)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings table (for hotel/rental)
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    check_in DATE,
    check_out DATE,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### Domain Not Resolving

```bash
# Verify hosts file
cat /etc/hosts | grep -i "yourdomain.com"

# Verify Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Database Connection Error

```bash
# Test MySQL connection
mysql -u flaskapp -pflaskapp123 -e "SELECT 1;"

# Check MySQL status
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql
```

### Permission Denied on /etc/hosts

Ensure verify_domains.py has been run with sudo:

```bash
sudo python3 verify_domains.py
```

## 🔐 Security Notes

- **Change default MySQL password** before production
- **Update SECRET_KEY** in config.py with a strong random string
- **Restrict /etc/hosts access** using Unix permissions
- **Use HTTPS** for production (add SSL certificates to Nginx)
- **Validate all user inputs** on the backend
- **Regularly backup databases** (automated daily at 2:30 AM)

## 📚 Documentation

- **[Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md)** - In-depth installation
- **[API Documentation](docs/API.md)** - All endpoints and parameters
- **[Domain Management](docs/DOMAIN_MANAGEMENT.md)** - Custom domain setup
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues
- **[Automation Tasks](docs/AUTOMATION.md)** - Background jobs configuration

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**SUNDARESN K**
**If you want to start or run the application in loacl server**


```bash
sudo python3 start.py
```


## 🙏 Acknowledgments

- Flask documentation and community
- Bootstrap team for UI components
- MySQL for reliable database management
- Nginx for powerful web server capabilities

## 📧 Contact & Support

For issues, questions, or suggestions:

- Submit an issue on GitHub
- Email: sundhar2005k@gmail.com

---

**Built with ❤️ for easy website deployment**

*Last Updated: March 2026*
