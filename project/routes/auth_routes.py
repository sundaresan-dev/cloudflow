from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_connection import DatabaseConnection
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength (at least 6 characters)"""
    return len(password) >= 6

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.json
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validation
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'}), 400
    
    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
    
    # Check if email already exists
    existing_user = DatabaseConnection.execute_query(
        "SELECT id FROM users WHERE email = %s",
        (email,),
        fetch_one=True
    )
    
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Create user
    hashed_password = generate_password_hash(password)
    try:
        user_id = DatabaseConnection.execute_update(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            session['is_admin'] = False
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'redirect': '/dashboard'
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    # Check user
    user = DatabaseConnection.execute_query(
        "SELECT id, name, email, password, is_admin FROM users WHERE email = %s",
        (email,),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    if not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Set session
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['is_admin'] = user['is_admin']
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'redirect': '/dashboard'
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_name': session.get('user_name'),
            'user_email': session.get('user_email')
        }), 200
    return jsonify({'logged_in': False}), 200
