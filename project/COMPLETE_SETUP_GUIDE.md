# 🚀 Cloud Website Deployment System — Complete Setup Guide

> **One-click website deployment with automatic custom domain setup.**  
> Deploy E-Commerce, School, College & Hotel websites instantly.

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [MySQL Database Setup](#2-mysql-database-setup)
3. [Project Setup](#3-project-setup)
4. [Nginx Installation & Configuration](#4-nginx-installation--configuration)
5. [Passwordless Sudo Setup](#5-passwordless-sudo-setup)
6. [Start the Application](#6-start-the-application)
7. [Using the System](#7-using-the-system)
8. [How It Works](#8-how-it-works)
9. [Project Structure](#9-project-structure)
10. [API Reference](#10-api-reference)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

Make sure these are installed on your **Ubuntu/Linux** system:

```bash
# Check Python 3
python3 --version    # Need 3.8+

# Check MySQL
mysql --version      # Need 8.0+

# Check pip
pip3 --version
```

### Install if missing:

```bash
# Python 3
sudo apt update
sudo apt install python3 python3-pip python3-venv

# MySQL Server
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

# Nginx
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 2. MySQL Database Setup

### 2.1 Create MySQL User

```bash
sudo mysql
```

Inside MySQL:

```sql
-- Create the application user
CREATE USER 'flaskapp'@'localhost' IDENTIFIED BY 'flaskapp123';

-- Grant all privileges
GRANT ALL PRIVILEGES ON *.* TO 'flaskapp'@'localhost' WITH GRANT OPTION;

-- Apply changes
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### 2.2 Verify Connection

```bash
mysql -u flaskapp -pflaskapp123 -e "SELECT 'Connection OK';"
```

> **Note:** The app will auto-create the `website_deployment_system` database and all tables on first run.

---

## 3. Project Setup

### 3.1 Navigate to Project

```bash
cd /home/ulu/rentalflow/project
```

### 3.2 Create Virtual Environment

```bash
python3 -m venv venv
```

### 3.3 Activate Virtual Environment

```bash
source venv/bin/activate
```

> You'll see `(venv)` in your terminal prompt.

### 3.4 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.2 | Web framework |
| mysql-connector-python | 8.0.33 | MySQL driver |
| Werkzeug | 2.3.6 | Password hashing |
| python-dotenv | 1.0.0 | Environment config |
| schedule | 1.2.0 | Background tasks |

### 3.5 Configure Database Connection

Edit `config.py` if your MySQL credentials are different:

```python
DB_HOST = 'localhost'
DB_USER = 'flaskapp'          # ← Change if different
DB_PASSWORD = 'flaskapp123'    # ← Change if different
DB_NAME = 'website_deployment_system'
DB_PORT = 3306
```

---

## 4. Nginx Installation & Configuration

Nginx serves deployed websites via custom domains (e.g., `http://mystore.com`).

### 4.1 Install Nginx

```bash
sudo apt install nginx
```

### 4.2 Start & Enable

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4.3 Verify Running

```bash
sudo systemctl status nginx
# Should show: active (running)
```

### 4.4 Remove Default Site (Optional)

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

---

## 5. Passwordless Sudo Setup

The app needs `sudo` access to:
- Add domains to `/etc/hosts`
- Create Nginx config files
- Enable sites and reload Nginx
- Set file permissions

### 5.1 Create Sudoers File

```bash
sudo bash -c 'cat > /etc/sudoers.d/deployment-system << EOF
ulu ALL=(ALL) NOPASSWD: /usr/bin/tee -a /etc/hosts, /usr/bin/tee /etc/nginx/sites-available/*, /bin/ln -sf /etc/nginx/sites-available/* /etc/nginx/sites-enabled/*, /usr/sbin/nginx -s reload, /bin/systemctl reload nginx, /bin/chmod *, /bin/cp *
EOF'
sudo chmod 0440 /etc/sudoers.d/deployment-system
```

> **Replace `ulu`** with your Linux username if different.

### 5.2 Verify

```bash
sudo -n systemctl status nginx
# Should work without asking for password
```

---

## 6. Start the Application

### 6.1 Activate Virtual Environment

```bash
cd /home/ulu/rentalflow/project
source venv/bin/activate
```

### 6.2 Run the App

```bash
python app.py
```

Output:
```
Database 'website_deployment_system' ready.
Database tables initialized successfully!
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:8080
```

### 6.3 Open in Browser

```
http://localhost:8080
```

### 6.4 Run in Background (Optional)

```bash
nohup python app.py > flask.log 2>&1 &
```

---

## 7. Using the System

### 7.1 Register an Account

1. Open `http://localhost:8080/register`
2. Fill in:
   - **Name**: Your name
   - **Email**: Your email
   - **Password**: At least 6 characters
   - **Confirm Password**: Same password
3. Click **Register**

### 7.2 Login

1. Open `http://localhost:8080/login`
2. Enter your email and password
3. Click **Login**
4. You'll be redirected to the Dashboard

### 7.3 Deploy a Website

1. On the **Dashboard**, you'll see 4 template cards:
   - 🛒 **E-Commerce Store** — Online shopping website
   - 🏫 **School Management** — Student/teacher management
   - 🎓 **College Management** — University courses system
   - 🏨 **Hotel Management** — Room booking system

2. Click **Select** on any template
3. Fill in:
   - **Website Name**: e.g., "My Online Store"
   - **Custom Domain**: e.g., `mystore.com`
4. Click **Deploy**

### 7.4 What Happens Automatically

When you click Deploy, the system:

```
✅ Copies template files → deployed_sites/site_xxxxx/
✅ Creates MySQL database → site_xxxxx
✅ Imports SQL schema with sample data
✅ Adds 127.0.0.1 mystore.com → /etc/hosts
✅ Creates Nginx config → /etc/nginx/sites-available/mystore.com
✅ Enables site → /etc/nginx/sites-enabled/mystore.com
✅ Reloads Nginx
✅ Sets file permissions
```

### 7.5 Visit Your Deployed Site

Open your browser and go to:
```
http://mystore.com
```

**That's it! Your website is live on the custom domain.** 🎉

### 7.6 Manage Deployments

- Visit `http://localhost:8080/deployments` to see all your deployed sites
- Click **Visit** to open a deployed site
- Click **Delete** to remove a deployment

---

## 8. How It Works

### Architecture

```
┌──────────────────────────────────────────────────────┐
│  Browser: http://mystore.com                         │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│  /etc/hosts                                          │
│  127.0.0.1    mystore.com                            │
│  (resolves domain to localhost)                      │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│  Nginx (Port 80)                                     │
│  Reads: /etc/nginx/sites-enabled/mystore.com         │
│  Serves: /home/.../deployed_sites/site_xxxxx/        │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  Flask Admin (Port 8080)                             │
│  http://localhost:8080                                │
│  • Register / Login                                  │
│  • Dashboard (choose template)                       │
│  • Deploy (creates files + domain + nginx config)    │
│  • My Deployments (manage sites)                     │
└──────────────────────────────────────────────────────┘
```

### Deployment Flow

```
User → Dashboard → Select Template → Enter Domain → Deploy
                                                       │
          ┌────────────────────────────────────────────┘
          │
          ├── 1. Copy template files to deployed_sites/
          ├── 2. Create MySQL database with sample data
          ├── 3. Add domain to /etc/hosts
          ├── 4. Create Nginx static file server config
          ├── 5. Enable site + reload Nginx
          └── 6. Save deployment record in database
                                    │
                                    ▼
                     http://yourdomain.com → LIVE! ✅
```

---

## 9. Project Structure

```
project/
│
├── app.py                          # Main Flask application
├── config.py                       # Database & app configuration
├── requirements.txt                # Python dependencies
├── scheduler.py                    # Background maintenance tasks
│
├── database/
│   ├── __init__.py
│   └── db_connection.py            # MySQL connection manager
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py              # Register, Login, Logout APIs
│   └── deploy_routes.py            # Deploy, List, Delete APIs
│
├── templates/                      # Flask admin UI pages
│   ├── base.html                   # Base layout
│   ├── login.html                  # Login page
│   ├── register.html               # Register page
│   ├── dashboard.html              # Template selection
│   └── deployments.html            # Manage deployments
│
├── static/
│   ├── css/style.css               # Admin panel styling
│   └── js/
│       ├── common.js               # Shared utilities
│       ├── login.js                # Login page logic
│       ├── register.js             # Register page logic
│       ├── dashboard.js            # Dashboard logic
│       └── deployments.js          # Deployments page logic
│
├── templates_websites/             # Website templates (source)
│   ├── ecommerce/                  # 🛒 E-Commerce template
│   │   ├── index.html
│   │   ├── products.html
│   │   ├── style.css
│   │   ├── script.js
│   │   └── database.sql
│   ├── school/                     # 🏫 School template
│   ├── college/                    # 🎓 College template
│   └── hotel/                      # 🏨 Hotel template
│
├── deployed_sites/                 # Deployed websites (auto-created)
│   ├── site_a1b2c3d4/
│   ├── site_e5f6g7h8/
│   └── ...
│
└── venv/                           # Python virtual environment
```

---

## 10. API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout |
| GET | `/auth/check-session` | Check login status |

### Deployment

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/deploy/templates` | List available templates |
| POST | `/deploy/create` | Deploy a website |
| GET | `/deploy/list` | List user's deployments |
| DELETE | `/deploy/delete/<id>` | Delete a deployment |

### Deploy Request Body

```json
{
  "website_type": "ecommerce",
  "website_name": "My Store",
  "custom_domain": "mystore.com"
}
```

### Deploy Response

```json
{
  "success": true,
  "message": "Website deployed successfully",
  "deployment": {
    "id": 1,
    "site_folder": "site_a1b2c3d4",
    "domain": "mystore.com",
    "url": "http://mystore.com",
    "database": "site_a1b2c3d4",
    "status": "active"
  }
}
```

---

## 11. Troubleshooting

### ❌ Flask won't start

```bash
# Make sure venv is activated
source venv/bin/activate

# Check if port 8080 is in use
lsof -i :8080
# Kill if needed:
kill -9 <PID>

# Try starting again
python app.py
```

### ❌ MySQL connection error

```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u flaskapp -pflaskapp123 -e "SELECT 1;"

# If user doesn't exist, create it (see Step 2)
```

### ❌ Domain not loading (site not found)

```bash
# 1. Check /etc/hosts has the domain
grep "yourdomain.com" /etc/hosts

# 2. Check Nginx config exists
ls /etc/nginx/sites-available/yourdomain.com

# 3. Check it's enabled
ls /etc/nginx/sites-enabled/yourdomain.com

# 4. Check Nginx is running
sudo systemctl status nginx

# 5. Test Nginx config
sudo nginx -t

# 6. Reload if needed
sudo systemctl reload nginx
```

### ❌ 500 Internal Server Error on domain

```bash
# Usually a file permission issue
# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Fix permissions
sudo chmod o+x /home/ulu /home/ulu/rentalflow /home/ulu/rentalflow/project
sudo chmod -R o+rx /home/ulu/rentalflow/project/deployed_sites/
sudo systemctl reload nginx
```

### ❌ Domain goes to real website instead of local

```bash
# The domain exists on the internet and /etc/hosts is not overriding
# Check if entry exists:
grep "yourdomain.com" /etc/hosts

# If not, add it:
echo "127.0.0.1       yourdomain.com" | sudo tee -a /etc/hosts

# Flush DNS cache
sudo systemd-resolve --flush-caches
```

### ❌ "sudo: a password is required"

```bash
# Sudoers file not set up (see Step 5)
sudo bash -c 'cat > /etc/sudoers.d/deployment-system << EOF
ulu ALL=(ALL) NOPASSWD: /usr/bin/tee -a /etc/hosts, /usr/bin/tee /etc/nginx/sites-available/*, /bin/ln -sf /etc/nginx/sites-available/* /etc/nginx/sites-enabled/*, /usr/sbin/nginx -s reload, /bin/systemctl reload nginx, /bin/chmod *, /bin/cp *
EOF'
sudo chmod 0440 /etc/sudoers.d/deployment-system
```

---

## ✅ Quick Start Summary

```bash
# 1. Setup (one-time)
cd /home/ulu/rentalflow/project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install nginx
sudo systemctl start nginx

# 2. Run
source venv/bin/activate
python app.py

# 3. Use
# Open http://localhost:8080
# Register → Login → Pick template → Enter domain → Deploy
# Visit http://yourdomain.com ✅
```

---

**Built with Flask + MySQL + Nginx** | **4 Website Templates** | **Automatic Domain Setup** 🚀
