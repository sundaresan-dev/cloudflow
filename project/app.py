from flask import Flask, render_template, session, redirect, url_for, request
from config import Config
from database.db_connection import DatabaseConnection
from routes.auth_routes import auth_bp
from routes.deploy_routes import deploy_bp
from routes.admin_routes import admin_bp
from routes.support_routes import support_bp
import os

def create_app():
    """Application Factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    DatabaseConnection.initialize_database()
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(deploy_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(support_bp)
    
    # Create deployed_sites directory if it doesn't exist
    if not os.path.exists(app.config['DEPLOYED_SITES_PATH']):
        os.makedirs(app.config['DEPLOYED_SITES_PATH'])
    
    def serve_deployed_site_by_domain(domain):
        """Serve deployed website based on domain name"""
        try:
            # Find deployment by domain (stored in URL)
            deployments = DatabaseConnection.execute_query(
                "SELECT site_folder FROM deployments WHERE url LIKE %s LIMIT 1",
                (f"%{domain}%",),
                fetch_one=True
            )
            
            if not deployments:
                # Try to match by domain prefix
                domain_prefix = domain.split('-')[0] if '-' in domain else domain.split('.')[0]
                deployments = DatabaseConnection.execute_query(
                    "SELECT site_folder FROM deployments WHERE site_folder LIKE %s LIMIT 1",
                    (f"%{domain[:15]}%",),
                    fetch_one=True
                )
            
            if deployments:
                site_folder = deployments['site_folder']
                deployed_path = os.path.join(app.config['DEPLOYED_SITES_PATH'], site_folder)
                requested_file = request.path.lstrip('/')
                
                if not requested_file or requested_file == '':
                    requested_file = 'index.html'
                
                file_path = os.path.join(deployed_path, requested_file)
                
                # Security check
                if not os.path.abspath(file_path).startswith(os.path.abspath(deployed_path)):
                    return "Forbidden", 403
                
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        return f.read()
                elif os.path.isdir(file_path):
                    index_file = os.path.join(file_path, 'index.html')
                    if os.path.exists(index_file):
                        with open(index_file, 'rb') as f:
                            return f.read()
                
            return "Deployed site not found", 404
        except Exception as e:
            print(f"Error serving deployed site: {e}")
            return "Error loading deployed site", 500
    
    
    @app.route('/')
    def index():
        """Home page or deployed site based on domain"""
        # Check if this is a request to a deployed site via fake domain
        host = request.host.split(':')[0]  # Get domain without port
        
        # If it's a deployed site domain, serve the deployed website
        if host.endswith('.local') and host != 'deployment.local':
            return serve_deployed_site_by_domain(host)
        
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        """Login page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        """Register page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('register.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page with statistics"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Fetch statistics
        try:
            user_id = session.get('user_id')
            stats = {
                'total_deployments': DatabaseConnection.execute_query(
                    "SELECT COUNT(*) as count FROM deployments WHERE user_id = %s",
                    (user_id,), fetch_one=True
                )['count'],
                'active_sites': DatabaseConnection.execute_query(
                    "SELECT COUNT(*) as count FROM deployments WHERE user_id = %s",
                    (user_id,), fetch_one=True
                )['count'], # For now same as total, can be filtered by status if added later
                'templates_available': len(os.listdir(app.config['TEMPLATES_PATH'])) if os.path.exists(app.config['TEMPLATES_PATH']) else 0
            }
            
            recent_deployments = DatabaseConnection.execute_query(
                "SELECT * FROM deployments WHERE user_id = %s ORDER BY created_at DESC LIMIT 5",
                (user_id,)
            )
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            stats = {'total_deployments': 0, 'active_sites': 0, 'templates_available': 0}
            recent_deployments = []
            
        return render_template('dashboard.html', stats=stats, recent_deployments=recent_deployments)
    
    @app.route('/create-website')
    def create_website():
        """Create website page with template selection"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('create.html')
    
    @app.route('/deployments')
    def deployments():
        """My deployments page"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('deployments.html')
    
    @app.route('/deployed_sites/<path:path>')
    def serve_deployed_site(path):
        """Serve deployed website files"""
        deployed_path = os.path.join(app.config['DEPLOYED_SITES_PATH'], path)
        
        # Security check: prevent path traversal
        if not os.path.abspath(deployed_path).startswith(os.path.abspath(app.config['DEPLOYED_SITES_PATH'])):
            return "Forbidden", 403
        
        if os.path.isfile(deployed_path):
            return open(deployed_path, 'rb').read()
        elif os.path.isdir(deployed_path):
            index_file = os.path.join(deployed_path, 'index.html')
            if os.path.exists(index_file):
                return open(index_file, 'rb').read()
            return "Not Found", 404
        return "Not Found", 404
    
    @app.context_processor
    def inject_user():
        """Inject user info into templates"""
        return {
            'user_name': session.get('user_name'),
            'user_email': session.get('user_email'),
            'is_admin': session.get('is_admin', False)
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host=Config.APP_HOST, port=Config.APP_PORT)
