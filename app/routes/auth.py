from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db, limiter
from app.models.user import User
from app.services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Admin login page (public user accounts are disabled)"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        # Validate inputs
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('auth/login.html')

        # Find user
        user = User.query.filter_by(email=email.lower().strip()).first()

        # Check credentials
        if user and user.check_password(password):
            # Only admins may log in (public user login is disabled)
            if not user.is_admin:
                flash('Admin access only.', 'danger')
                return render_template('auth/login.html')

            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return render_template('auth/login.html')

            # Log user in
            login_user(user, remember=remember)
            user.update_last_login()

            flash(f'Welcome back, {user.name}!', 'success')

            # Redirect to next page or homepage
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')

            return redirect(next_page)
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """Disabled: public user registration is not supported."""
    abort(404)
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        experience_level = request.form.get('experience_level')

        # Validate inputs
        if not all([name, email, password, confirm_password]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email.lower().strip()).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html')

        # Create new user
        user = User(
            name=name,
            email=email.lower().strip(),
            phone=phone,
            experience_level=experience_level
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Log the user in
        login_user(user)
        user.update_last_login()

        flash(f'Welcome to Momentum Clips, {user.name}! Your account has been created successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Disabled: public user profiles are not supported."""
    abort(404)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Disabled: public user profile editing is not supported."""
    abort(404)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()

        user = User.query.filter_by(email=email).first()

        # Always show success message for security
        flash('If an account with that email exists, a password reset link has been sent.', 'info')

        if user:
            try:
                email_service = EmailService()
                reset_token = user.generate_reset_token()
                email_service.send_password_reset(user, reset_token)
            except Exception:
                current_app.logger.exception('Failed to send password reset email')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    """Reset password with token"""
    user = User.verify_reset_token(token)

    if not user:
        flash('This password reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Please enter and confirm your new password.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(password)
        db.session.commit()

        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
