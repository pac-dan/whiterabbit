from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    # Get statistics
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    total_videos = Video.query.count()
    total_testimonials = Testimonial.query.count()

    # Get revenue statistics
    completed_bookings = Booking.query.filter_by(status=BookingStatus.COMPLETED.value).all()
    total_revenue = sum(float(booking.amount) for booking in completed_bookings)

    # Get upcoming bookings
    upcoming_bookings = Booking.get_upcoming_bookings(limit=10)

    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()

    # Get booking statistics by status
    booking_stats = db.session.query(
        Booking.status,
        func.count(Booking.id).label('count')
    ).group_by(Booking.status).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_bookings=total_bookings,
        total_videos=total_videos,
        total_testimonials=total_testimonials,
        total_revenue=total_revenue,
        upcoming_bookings=upcoming_bookings,
        recent_bookings=recent_bookings,
        booking_stats=dict(booking_stats)
    )


# Booking Management

@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    """Manage all bookings"""
    status_filter = request.args.get('status', None)
    page = request.args.get('page', 1, type=int)

    query = Booking.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.order_by(Booking.booking_date.desc())\
        .paginate(page=page, per_page=current_app.config['ADMIN_ITEMS_PER_PAGE'], error_out=False)

    return render_template(
        'admin/bookings.html',
        bookings=bookings,
        status_filter=status_filter
    )


@admin_bp.route('/bookings/<int:booking_id>')
@login_required
@admin_required
def view_booking(booking_id):
    """View and manage a specific booking"""
    booking = Booking.query.get_or_404(booking_id)
    return render_template('admin/booking_detail.html', booking=booking)


@admin_bp.route('/bookings/<int:booking_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    """Update booking status"""
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')

    if new_status in [status.value for status in BookingStatus]:
        booking.status = new_status
        if admin_notes:
            booking.admin_notes = admin_notes
        db.session.commit()
        flash('Booking status updated successfully.', 'success')
    else:
        flash('Invalid status.', 'danger')

    return redirect(url_for('admin.view_booking', booking_id=booking_id))


@admin_bp.route('/bookings/<int:booking_id>/deliver', methods=['POST'])
@login_required
@admin_required
def deliver_booking(booking_id):
    """Mark booking as completed and add video links"""
    booking = Booking.query.get_or_404(booking_id)
    video_links = request.form.get('video_links')

    booking.mark_completed(video_links=video_links)

    flash('Booking marked as completed and video links delivered.', 'success')
    return redirect(url_for('admin.view_booking', booking_id=booking_id))


# Package Management

@admin_bp.route('/packages')
@login_required
@admin_required
def packages():
    """Manage packages"""
    packages = Package.query.order_by(Package.display_order, Package.name).all()
    return render_template('admin/packages.html', packages=packages)


@admin_bp.route('/packages/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_package():
    """Create a new package"""
    if request.method == 'POST':
        package = Package(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price', type=float),
            duration=request.form.get('duration', type=int),
            features=request.form.get('features'),
            max_riders=request.form.get('max_riders', 1, type=int),
            includes_drone=request.form.get('includes_drone', False, type=bool),
            video_count=request.form.get('video_count', 1, type=int),
            is_active=request.form.get('is_active', True, type=bool),
            display_order=request.form.get('display_order', 0, type=int)
        )

        db.session.add(package)
        db.session.commit()

        flash('Package created successfully.', 'success')
        return redirect(url_for('admin.packages'))

    return render_template('admin/package_form.html', package=None)


@admin_bp.route('/packages/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(package_id):
    """Edit a package"""
    package = Package.query.get_or_404(package_id)

    if request.method == 'POST':
        package.name = request.form.get('name', package.name)
        package.description = request.form.get('description', package.description)
        package.price = request.form.get('price', package.price, type=float)
        package.duration = request.form.get('duration', package.duration, type=int)
        package.features = request.form.get('features', package.features)
        package.max_riders = request.form.get('max_riders', package.max_riders, type=int)
        package.includes_drone = request.form.get('includes_drone', package.includes_drone, type=bool)
        package.video_count = request.form.get('video_count', package.video_count, type=int)
        package.is_active = request.form.get('is_active', package.is_active, type=bool)
        package.display_order = request.form.get('display_order', package.display_order, type=int)

        db.session.commit()

        flash('Package updated successfully.', 'success')
        return redirect(url_for('admin.packages'))

    return render_template('admin/package_form.html', package=package)


@admin_bp.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_package(package_id):
    """Delete a package"""
    package = Package.query.get_or_404(package_id)

    # Check if package has bookings
    if package.booking_count > 0:
        flash('Cannot delete package with existing bookings. Deactivate it instead.', 'warning')
        return redirect(url_for('admin.packages'))

    db.session.delete(package)
    db.session.commit()

    flash('Package deleted successfully.', 'success')
    return redirect(url_for('admin.packages'))


# Video Management

@admin_bp.route('/videos')
@login_required
@admin_required
def videos():
    """Manage videos"""
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('admin/videos.html', videos=videos)


@admin_bp.route('/videos/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_video():
    """Add a new video"""
    if request.method == 'POST':
        video = Video(
            title=request.form.get('title'),
            description=request.form.get('description'),
            vimeo_id=request.form.get('vimeo_id'),
            thumbnail_url=request.form.get('thumbnail_url'),
            location_tag=request.form.get('location_tag'),
            style_tag=request.form.get('style_tag'),
            rider_level=request.form.get('rider_level'),
            is_featured=request.form.get('is_featured', False, type=bool),
            is_published=request.form.get('is_published', True, type=bool),
            display_order=request.form.get('display_order', 0, type=int)
        )

        if request.form.get('is_comparison'):
            video.is_comparison = True
            video.before_vimeo_id = request.form.get('before_vimeo_id')
            video.after_vimeo_id = request.form.get('after_vimeo_id')

        db.session.add(video)
        db.session.commit()

        flash('Video added successfully.', 'success')
        return redirect(url_for('admin.videos'))

    return render_template('admin/video_form.html', video=None)


@admin_bp.route('/videos/<int:video_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_video(video_id):
    """Edit a video"""
    video = Video.query.get_or_404(video_id)

    if request.method == 'POST':
        video.title = request.form.get('title', video.title)
        video.description = request.form.get('description', video.description)
        video.vimeo_id = request.form.get('vimeo_id', video.vimeo_id)
        video.thumbnail_url = request.form.get('thumbnail_url', video.thumbnail_url)
        video.location_tag = request.form.get('location_tag', video.location_tag)
        video.style_tag = request.form.get('style_tag', video.style_tag)
        video.rider_level = request.form.get('rider_level', video.rider_level)
        video.is_featured = request.form.get('is_featured', video.is_featured, type=bool)
        video.is_published = request.form.get('is_published', video.is_published, type=bool)
        video.display_order = request.form.get('display_order', video.display_order, type=int)

        db.session.commit()

        flash('Video updated successfully.', 'success')
        return redirect(url_for('admin.videos'))

    return render_template('admin/video_form.html', video=video)


@admin_bp.route('/videos/<int:video_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_video(video_id):
    """Delete a video"""
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()

    flash('Video deleted successfully.', 'success')
    return redirect(url_for('admin.videos'))


# Testimonial Management

@admin_bp.route('/testimonials')
@login_required
@admin_required
def testimonials():
    """Manage testimonials"""
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)


@admin_bp.route('/testimonials/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_testimonial():
    """Add a new testimonial"""
    if request.method == 'POST':
        testimonial = Testimonial(
            client_name=request.form.get('client_name'),
            client_photo_url=request.form.get('client_photo_url'),
            client_location=request.form.get('client_location'),
            testimonial_text=request.form.get('testimonial_text'),
            rating=request.form.get('rating', type=int),
            project_type=request.form.get('project_type'),
            is_featured=request.form.get('is_featured', False, type=bool),
            is_published=request.form.get('is_published', True, type=bool),
            verified_purchase=request.form.get('verified_purchase', False, type=bool)
        )

        db.session.add(testimonial)
        db.session.commit()

        flash('Testimonial added successfully.', 'success')
        return redirect(url_for('admin.testimonials'))

    return render_template('admin/testimonial_form.html', testimonial=None)


@admin_bp.route('/testimonials/<int:testimonial_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_testimonial(testimonial_id):
    """Edit a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)

    if request.method == 'POST':
        testimonial.client_name = request.form.get('client_name', testimonial.client_name)
        testimonial.testimonial_text = request.form.get('testimonial_text', testimonial.testimonial_text)
        testimonial.rating = request.form.get('rating', testimonial.rating, type=int)
        testimonial.is_featured = request.form.get('is_featured', testimonial.is_featured, type=bool)
        testimonial.is_published = request.form.get('is_published', testimonial.is_published, type=bool)

        db.session.commit()

        flash('Testimonial updated successfully.', 'success')
        return redirect(url_for('admin.testimonials'))

    return render_template('admin/testimonial_form.html', testimonial=testimonial)


@admin_bp.route('/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_testimonial(testimonial_id):
    """Delete a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()

    flash('Testimonial deleted successfully.', 'success')
    return redirect(url_for('admin.testimonials'))


# User Management

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    return render_template('admin/user_detail.html', user=user, bookings=user_bookings)


# Social Media Management (Future Integration)

@admin_bp.route('/social')
@login_required
@admin_required
def social_media():
    """Social media management dashboard"""
    # TODO: Integrate with Ayrshare API
    flash('Social media automation coming soon!', 'info')
    return render_template('admin/social.html')
