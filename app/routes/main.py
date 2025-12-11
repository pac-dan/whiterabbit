from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial
from app.models.newsletter import Newsletter
from app.models.booking import Booking
from app.models.waiver import Waiver, WAIVER_TEXT, CURRENT_WAIVER_VERSION
from app import db, limiter, csrf
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import re
import hashlib

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage"""
    # Get featured content
    featured_packages = Package.get_featured_packages(limit=3)
    featured_videos = Video.get_featured_videos(limit=6)
    featured_testimonials = Testimonial.get_featured_testimonials(limit=6)
    average_rating = Testimonial.get_average_rating()

    return render_template(
        'index.html',
        packages=featured_packages,
        videos=featured_videos,
        testimonials=featured_testimonials,
        average_rating=average_rating
    )


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/gallery')
def gallery():
    """Video gallery page with filtering"""
    # Get filter parameters
    location = request.args.get('location', None)
    style = request.args.get('style', None)
    level = request.args.get('level', None)

    # Get all available tags for filter dropdowns
    all_tags = Video.get_all_tags()

    # Get filtered videos
    if any([location, style, level]):
        videos = Video.get_by_filters(location=location, style=style, level=level)
    else:
        videos = Video.get_recent_videos(limit=24)

    return render_template(
        'gallery/index.html',
        videos=videos,
        all_tags=all_tags,
        active_location=location,
        active_style=style,
        active_level=level
    )


@main_bp.route('/gallery/<int:video_id>')
def video_detail(video_id):
    """Individual video page"""
    video = Video.query.get_or_404(video_id)

    # Increment view count
    video.increment_views()

    # Get related videos (same tags)
    related_videos = Video.get_by_filters(
        location=video.location_tag,
        style=video.style_tag,
        limit=4
    )
    # Remove current video from related
    related_videos = [v for v in related_videos if v.id != video.id][:3]

    return render_template(
        'gallery/video_detail.html',
        video=video,
        related_videos=related_videos
    )


@main_bp.route('/packages')
def packages():
    """Packages listing page"""
    all_packages = Package.get_active_packages()

    return render_template(
        'packages.html',
        packages=all_packages
    )


@main_bp.route('/packages/<int:package_id>')
def package_detail(package_id):
    """Individual package detail page"""
    package = Package.query.get_or_404(package_id)

    # Get sample videos for this package type
    sample_videos = Video.get_featured_videos(limit=3)

    return render_template(
        'package_detail.html',
        package=package,
        sample_videos=sample_videos
    )


@main_bp.route('/testimonials')
def testimonials():
    """All testimonials page"""
    all_testimonials = Testimonial.get_recent_testimonials(limit=50)
    average_rating = Testimonial.get_average_rating()
    rating_distribution = Testimonial.get_rating_distribution()

    return render_template(
        'testimonials.html',
        testimonials=all_testimonials,
        average_rating=average_rating,
        rating_distribution=rating_distribution
    )


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


@main_bp.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq.html')


# API endpoints for AJAX requests

@main_bp.route('/api/videos')
def api_videos():
    """API endpoint to get videos with filters"""
    location = request.args.get('location', None)
    style = request.args.get('style', None)
    level = request.args.get('level', None)
    limit = request.args.get('limit', 12, type=int)

    videos = Video.get_by_filters(location=location, style=style, level=level, limit=limit)

    return jsonify({
        'success': True,
        'videos': [video.to_dict() for video in videos],
        'count': len(videos)
    })


@main_bp.route('/api/packages')
def api_packages():
    """API endpoint to get all active packages"""
    packages = Package.get_active_packages()

    return jsonify({
        'success': True,
        'packages': [pkg.to_dict() for pkg in packages]
    })


@main_bp.route('/api/testimonials')
def api_testimonials():
    """API endpoint to get testimonials"""
    limit = request.args.get('limit', 10, type=int)
    testimonials = Testimonial.get_recent_testimonials(limit=limit)

    return jsonify({
        'success': True,
        'testimonials': [test.to_dict() for test in testimonials],
        'average_rating': Testimonial.get_average_rating()
    })


@main_bp.route('/api/video/<int:video_id>/like', methods=['POST'])
@limiter.limit("10 per minute")
def like_video(video_id):
    """API endpoint to like a video"""
    video = Video.query.get_or_404(video_id)
    video.increment_likes()

    return jsonify({
        'success': True,
        'like_count': video.like_count
    })


@main_bp.route('/newsletter/subscribe', methods=['POST'])
@limiter.limit("5 per hour")
def newsletter_subscribe():
    """Subscribe to newsletter"""
    email = request.form.get('email', '').strip().lower()
    
    # Validate email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_regex, email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    
    try:
        # Check if already subscribed
        existing = Newsletter.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                flash('You are already subscribed to our newsletter!', 'info')
            else:
                # Reactivate subscription
                existing.is_active = True
                db.session.commit()
                flash('Welcome back! Your subscription has been reactivated.', 'success')
        else:
            # Create new subscription
            subscriber = Newsletter(email=email)
            db.session.add(subscriber)
            db.session.commit()
            
            # Send welcome email
            try:
                from app.services.email_service import EmailService
                email_service = EmailService()
                email_service.send_email(
                    to=email,
                    subject='Welcome to Momentum Clips!',
                    template='newsletter_welcome',
                    email=email
                )
            except Exception as e:
                current_app.logger.error(f'Newsletter welcome email error: {str(e)}')
            
            flash('Thanks for subscribing! Check your email for a welcome message.', 'success')
        
        return redirect(request.referrer or url_for('main.index'))
        
    except IntegrityError:
        db.session.rollback()
        flash('You are already subscribed!', 'info')
        return redirect(request.referrer or url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Newsletter subscription error: {str(e)}')
        flash('An error occurred. Please try again later.', 'danger')
        return redirect(request.referrer or url_for('main.index'))


# ============== WAIVER ROUTES ==============

@main_bp.route('/waiver/<token>')
def waiver_form(token):
    """Display waiver form for signing"""
    # Decode token to get booking ID
    try:
        booking_id = decode_waiver_token(token)
        booking = Booking.query.get_or_404(booking_id)
    except:
        flash('Invalid or expired waiver link.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if already signed
    existing_waiver = Waiver.get_by_booking(booking_id)
    if existing_waiver:
        return render_template(
            'waiver_complete.html',
            booking=booking,
            waiver=existing_waiver
        )
    
    return render_template(
        'waiver.html',
        booking=booking,
        token=token,
        waiver_text=WAIVER_TEXT,
        waiver_version=CURRENT_WAIVER_VERSION
    )


@main_bp.route('/waiver/<token>', methods=['POST'])
@limiter.limit("5 per hour")
def waiver_submit(token):
    """Process waiver signature submission"""
    # Decode token to get booking ID
    try:
        booking_id = decode_waiver_token(token)
        booking = Booking.query.get_or_404(booking_id)
    except:
        flash('Invalid or expired waiver link.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if already signed
    if Waiver.is_signed(booking_id):
        flash('This waiver has already been signed.', 'info')
        return redirect(url_for('main.waiver_form', token=token))
    
    # Get form data
    legal_name = request.form.get('legal_name', '').strip()
    agreement = request.form.get('agreement')
    
    # Validate
    if not legal_name or len(legal_name) < 3:
        flash('Please enter your full legal name.', 'danger')
        return redirect(url_for('main.waiver_form', token=token))
    
    if not agreement:
        flash('You must agree to the terms to proceed.', 'danger')
        return redirect(url_for('main.waiver_form', token=token))
    
    # Get client info
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()  # Get first IP if multiple
    user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length
    
    # Get client name/email from booking
    client_name = booking.user.name if booking.user else 'Unknown'
    client_email = booking.user.email if booking.user else 'unknown@unknown.com'
    
    try:
        # Create waiver record
        waiver = Waiver(
            booking_id=booking_id,
            client_name=client_name,
            client_email=client_email,
            legal_name_signature=legal_name,
            ip_address=ip_address,
            user_agent=user_agent,
            waiver_version=CURRENT_WAIVER_VERSION,
            signed_at=datetime.utcnow()
        )
        db.session.add(waiver)
        
        # Update booking status
        booking.waiver_signed = True
        
        db.session.commit()
        
        # Send confirmation email
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            email_service.send_email(
                to=client_email,
                subject='Waiver Signed - Momentum Clips',
                template='waiver_confirmation',
                client_name=client_name,
                legal_name=legal_name,
                signed_at=waiver.signed_at,
                booking=booking
            )
        except Exception as e:
            current_app.logger.error(f'Waiver confirmation email error: {str(e)}')
        
        flash('Thank you! Your waiver has been signed successfully.', 'success')
        return render_template(
            'waiver_complete.html',
            booking=booking,
            waiver=waiver
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Waiver submission error: {str(e)}')
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('main.waiver_form', token=token))


@main_bp.route('/waiver/standalone', methods=['GET', 'POST'])
def waiver_standalone():
    """Standalone waiver for walk-ins without a booking"""
    if request.method == 'GET':
        return render_template(
            'waiver_standalone.html',
            waiver_text=WAIVER_TEXT,
            waiver_version=CURRENT_WAIVER_VERSION
        )
    
    # POST - process submission
    legal_name = request.form.get('legal_name', '').strip()
    client_name = request.form.get('client_name', '').strip()
    client_email = request.form.get('client_email', '').strip().lower()
    agreement = request.form.get('agreement')
    
    # Validate
    if not legal_name or len(legal_name) < 3:
        flash('Please enter your full legal name.', 'danger')
        return redirect(url_for('main.waiver_standalone'))
    
    if not client_email or '@' not in client_email:
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('main.waiver_standalone'))
    
    if not agreement:
        flash('You must agree to the terms to proceed.', 'danger')
        return redirect(url_for('main.waiver_standalone'))
    
    # Get client info
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', '')[:500]
    
    try:
        # Create waiver record (without booking)
        waiver = Waiver(
            booking_id=None,
            client_name=client_name or legal_name,
            client_email=client_email,
            legal_name_signature=legal_name,
            ip_address=ip_address,
            user_agent=user_agent,
            waiver_version=CURRENT_WAIVER_VERSION,
            signed_at=datetime.utcnow()
        )
        db.session.add(waiver)
        db.session.commit()
        
        flash('Thank you! Your waiver has been signed successfully.', 'success')
        return render_template(
            'waiver_complete.html',
            booking=None,
            waiver=waiver
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Standalone waiver error: {str(e)}')
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('main.waiver_standalone'))


def generate_waiver_token(booking_id):
    """Generate a secure token for waiver link"""
    secret = current_app.config.get('SECRET_KEY', 'default-secret')
    data = f"{booking_id}-{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def decode_waiver_token(token):
    """Decode waiver token - for now just look up booking by checking all"""
    # In production, you'd want to store token->booking_id mapping
    # For now, iterate through recent bookings to find match
    from app.models.booking import Booking
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(1000).all()
    for booking in bookings:
        if generate_waiver_token(booking.id) == token:
            return booking.id
    raise ValueError("Invalid token")


@main_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancers
    Returns JSON with status of critical services
    """
    from app import db, redis_client
    import sys
    
    health_status = {
        'status': 'healthy',
        'services': {},
        'version': '1.0.0',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    # Check database connectivity
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['services']['database'] = 'ok'
    except Exception as e:
        health_status['services']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check Redis connectivity (if configured)
    if redis_client:
        try:
            redis_client.ping()
            health_status['services']['redis'] = 'ok'
        except Exception as e:
            health_status['services']['redis'] = f'error: {str(e)}'
            # Redis is optional, so don't mark as unhealthy
    else:
        health_status['services']['redis'] = 'not configured'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return jsonify(health_status), status_code
