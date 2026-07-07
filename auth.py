from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password):
    """Validate password strength"""
    return len(password) >= 6


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup"""
    if current_user.is_authenticated:
        return redirect(url_for('tasks.today'))
    
    if request.method == 'POST':
        # Get and validate form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not name or len(name) < 2:
            flash('Name must be at least 2 characters long.', 'danger')
            return redirect(url_for('auth.signup'))
        
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('auth.signup'))
        
        if not is_strong_password(password):
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in or use a different email.', 'danger')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        try:
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Create default categories for the user
            from models import Category
            default_categories = [
                {'name': 'Academics', 'color_hex': '#3498db', 'icon': '📚'},
                {'name': 'Creative/Non-tech', 'color_hex': '#e74c3c', 'icon': '🎨'},
                {'name': 'Health/Fitness', 'color_hex': '#2ecc71', 'icon': '💪'},
                {'name': 'Personal Growth', 'color_hex': '#f39c12', 'icon': '🌱'},
            ]
            
            for cat_data in default_categories:
                category = Category(
                    user_id=new_user.id,
                    name=cat_data['name'],
                    color_hex=cat_data['color_hex'],
                    icon=cat_data['icon'],
                    is_default=True
                )
                db.session.add(category)
            
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return redirect(url_for('auth.signup'))
    
    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('tasks.today'))
    
    if request.method == 'POST':
        # Get and validate form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check user credentials
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('tasks.today'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
