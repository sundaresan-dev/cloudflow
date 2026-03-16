from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database.db_connection import DatabaseConnection

support_bp = Blueprint('support', __name__, url_prefix='/support')

@support_bp.before_request
def require_login():
    """Ensure all /support routes require a logged-in user"""
    if 'user_id' not in session:
        # Check if it's an API request or page load
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        return redirect(url_for('auth.login'))

@support_bp.route('/')
def support_page():
    """View user's support tickets"""
    user_id = session['user_id']
    user_tickets = DatabaseConnection.execute_query(
        "SELECT * FROM tickets WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    return render_template('support.html', tickets=user_tickets)

@support_bp.route('/create', methods=['POST'])
def create_ticket():
    """Create a new support ticket"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        message = data.get('message')
        user_id = session['user_id']
        
        if not subject or not message:
            return jsonify({"success": False, "error": "Missing subject or message"})
            
        DatabaseConnection.execute_update(
            "INSERT INTO tickets (user_id, subject, message) VALUES (%s, %s, %s)",
            (user_id, subject, message)
        )
        
        return jsonify({"success": True, "message": "Ticket submitted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
