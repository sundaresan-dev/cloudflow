from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database.db_connection import DatabaseConnection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin():
    """Helper to check if current user is an admin"""
    if 'user_id' not in session:
        return False
    
    user_id = session['user_id']
    user = DatabaseConnection.execute_query(
        "SELECT is_admin FROM users WHERE id = %s",
        (user_id,), fetch_one=True
    )
    return user and user.get('is_admin')

@admin_bp.before_request
def require_admin():
    """Ensure all /admin routes require admin privileges"""
    if not is_admin():
        return "Unauthorized", 403

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with global stats"""
    stats = {
        'total_users': DatabaseConnection.execute_query("SELECT COUNT(*) as count FROM users", fetch_one=True)['count'],
        'total_deployments': DatabaseConnection.execute_query("SELECT COUNT(*) as count FROM deployments", fetch_one=True)['count'],
        'open_tickets': DatabaseConnection.execute_query("SELECT COUNT(*) as count FROM tickets WHERE status = 'open'", fetch_one=True)['count']
    }
    
    recent_deployments = DatabaseConnection.execute_query(
        """SELECT d.*, u.name as user_name 
           FROM deployments d 
           JOIN users u ON d.user_id = u.id 
           ORDER BY d.created_at DESC LIMIT 5"""
    )
    
    recent_users = DatabaseConnection.execute_query(
        "SELECT id, name, email, created_at FROM users ORDER BY created_at DESC LIMIT 5"
    )
    
    return render_template('admin_dashboard.html', 
                           stats=stats, 
                           recent_deployments=recent_deployments,
                           recent_users=recent_users)

@admin_bp.route('/tickets')
def tickets():
    """View and manage all support tickets"""
    all_tickets = DatabaseConnection.execute_query(
        """SELECT t.*, u.name as user_name, u.email as user_email
           FROM tickets t
           JOIN users u ON t.user_id = u.id
           ORDER BY t.created_at DESC"""
    )
    return render_template('admin_tickets.html', tickets=all_tickets)

@admin_bp.route('/tickets/<int:ticket_id>/close', methods=['POST'])
def close_ticket(ticket_id):
    """Close a support ticket"""
    try:
        DatabaseConnection.execute_update(
            "UPDATE tickets SET status = 'closed' WHERE id = %s",
            (ticket_id,)
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route('/users')
def users():
    """View all registered users"""
    all_users = DatabaseConnection.execute_query(
        """SELECT u.*, COUNT(d.id) as deployment_count 
           FROM users u 
           LEFT JOIN deployments d ON u.id = d.user_id 
           GROUP BY u.id 
           ORDER BY u.created_at DESC"""
    )
    return render_template('admin_users.html', users=all_users)
