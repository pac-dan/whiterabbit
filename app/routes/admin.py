from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.booking import Booking  # legacy (user-login flow)
from app.models.public_booking import PublicBooking
from app.models.public_booking_waiver import PublicBookingWaiver
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial
from app.models.waiver import Waiver
from app.utils.validators import (
    validate_required, validate_price, validate_integer,
    validate_youtube_id, validate_url, validate_rating,
    validate_text_length, sanitize_string
)
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.services.admin_forms import SCHEMAS, validate_record
from app.models.package_schedule import PackageSchedule
from app.services.email_service import EmailService
from urllib.parse import urlparse

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
    total_bookings = PublicBooking.query.count()
    total_videos = Video.query.count()
    total_testimonials = Testimonial.query.count()

    # Get revenue statistics
    revenue_cents = db.session.query(func.coalesce(func.sum(PublicBooking.amount_cents), 0))\
        .filter(PublicBooking.status.in_(['paid', 'waiver_signed', 'scheduled', 'completed']))\
        .scalar()
    total_revenue = float(revenue_cents or 0) / 100.0

    # Get upcoming bookings
    upcoming_bookings = PublicBooking.query.filter(
        PublicBooking.calendly_event_start.isnot(None),
        PublicBooking.calendly_event_start >= datetime.utcnow()
    ).order_by(PublicBooking.calendly_event_start.asc()).limit(10).all()

    # Get recent bookings
    recent_bookings = PublicBooking.query.order_by(PublicBooking.created_at.desc()).limit(10).all()

    # Get booking statistics by status
    booking_stats = db.session.query(
        PublicBooking.status,
        func.count(PublicBooking.id).label('count')
    ).group_by(PublicBooking.status).all()

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

    query = PublicBooking.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.order_by(PublicBooking.created_at.desc())\
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
    booking = PublicBooking.query.get_or_404(booking_id)
    waiver_links = PublicBookingWaiver.query.filter_by(public_booking_id=booking_id).all()
    waiver_ids = [wl.waiver_id for wl in waiver_links]
    waivers = Waiver.query.filter(Waiver.id.in_(waiver_ids)).order_by(Waiver.signed_at.desc()).all() if waiver_ids else []
    return render_template('admin/booking_detail.html', booking=booking, waivers=waivers)


@admin_bp.route('/bookings/<int:booking_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    """Update booking status"""
    booking = PublicBooking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')

    if new_status not in ('paid', 'waiver_signed', 'scheduled', 'cancelled') or not booking.paid_at:
        flash('Choose a valid status for a verified paid order.', 'danger')
        return redirect(url_for('admin.view_booking', booking_id=booking_id))
    if new_status == 'waiver_signed' and not booking.latest_waiver_id:
        flash('This order has no signed waiver.', 'danger')
        return redirect(url_for('admin.view_booking', booking_id=booking_id))
    if new_status == 'scheduled':
        try:
            booking.calendly_event_start = datetime.strptime(request.form.get('scheduled_at', ''), '%Y-%m-%dT%H:%M')
            booking.calendly_timezone = 'UTC'
        except ValueError:
            flash('Enter the confirmed session date and time in UTC.', 'danger')
            return redirect(url_for('admin.view_booking', booking_id=booking_id))
    booking.status = new_status
    if admin_notes is not None: booking.admin_notes = admin_notes[:10000]
    db.session.commit()
    flash('Booking updated successfully.', 'success')

    return redirect(url_for('admin.view_booking', booking_id=booking_id))


@admin_bp.route('/bookings/<int:booking_id>/deliver', methods=['POST'])
@login_required
@admin_required
def deliver_booking(booking_id):
    """Mark booking as completed and add video links"""
    booking = PublicBooking.query.get_or_404(booking_id)
    links = [line.strip() for line in request.form.get('video_links', '').splitlines() if line.strip()]
    if not booking.paid_at or not booking.customer_email or not links or any(urlparse(link).scheme != 'https' or not urlparse(link).hostname for link in links):
        flash('A verified order, customer email and valid HTTPS film links are required.', 'danger')
        return redirect(url_for('admin.view_booking', booking_id=booking_id))
    booking.video_links = '\n'.join(links)
    db.session.commit()
    if booking.delivered_at and request.form.get('resend') != 'on':
        flash('Delivery already sent. Select resend to send it again.', 'info')
    elif EmailService().send_email(to=booking.customer_email, subject='Your Momentum Clips films', body=f'Your films for {booking.package_name}:\n\n{booking.video_links}\n\nThank you for riding with us.'):
        booking.status = 'completed'
        booking.delivered_at = datetime.utcnow()
        db.session.commit()
        flash('Film links emailed to the customer.', 'success')
    else:
        flash('Links saved, but email delivery failed. Check mail settings and retry; delivery is not marked complete.', 'warning')
    return redirect(url_for('admin.view_booking', booking_id=booking_id))


def _edit_record(kind, record=None):
    model, endpoint = {'package': (Package, 'admin.packages'), 'video': (Video, 'admin.videos'), 'testimonial': (Testimonial, 'admin.testimonials')}[kind]
    calendar = db.session.get(PackageSchedule, record.id) if kind == 'package' and record else None
    if request.method == 'POST':
        values, errors = validate_record(kind, request.form)
        if not errors:
            record = record or model()
            calendar_url = values.pop('calendly_url', '')
            for key, value in values.items(): setattr(record, key, value)
            if kind == 'video' and not record.is_comparison:
                record.before_youtube_id = record.after_youtube_id = None
            db.session.add(record)
            try:
                db.session.flush()
                if kind == 'package':
                    calendar = calendar or PackageSchedule(package_id=record.id)
                    calendar.calendly_url = calendar_url
                    db.session.add(calendar)
                db.session.commit()
                flash('Saved successfully.', 'success')
                return redirect(url_for(endpoint))
            except IntegrityError:
                db.session.rollback()
                errors.append('This record already exists. Check the video ID or other unique fields.')
        for error in errors: flash(error, 'danger')
    values = {field[0]: getattr(record, field[0], field[5]) if record else field[5] for field in SCHEMAS[kind]}
    if kind == 'package': values['calendly_url'] = calendar.calendly_url if calendar else ''
    if request.method == 'POST':
        values.update({f[0]: request.form.get(f[0], '') == 'on' if f[2] == 'checkbox' else request.form.get(f[0], '') for f in SCHEMAS[kind]})
    return render_template('admin/record_form.html', kind=kind, record=record, fields=SCHEMAS[kind], values=values)


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
    return _edit_record('package')


@admin_bp.route('/packages/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(package_id):
    return _edit_record('package', Package.query.get_or_404(package_id))


@admin_bp.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_package(package_id):
    """Delete a package"""
    package = Package.query.get_or_404(package_id)

    # Check if package has bookings
    if package.booking_count > 0 or PublicBooking.query.filter_by(package_key=str(package.id)).first():
        flash('Cannot delete package with existing bookings. Deactivate it instead.', 'warning')
        return redirect(url_for('admin.packages'))

    PackageSchedule.query.filter_by(package_id=package.id).delete()
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
    return _edit_record('video')


@admin_bp.route('/videos/<int:video_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_video(video_id):
    return _edit_record('video', Video.query.get_or_404(video_id))


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
    return _edit_record('testimonial')


@admin_bp.route('/testimonials/<int:testimonial_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_testimonial(testimonial_id):
    return _edit_record('testimonial', Testimonial.query.get_or_404(testimonial_id))


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


# Waiver Management

@admin_bp.route('/waivers')
@login_required
@admin_required
def waivers():
    """View all signed waivers"""
    all_waivers = Waiver.query.order_by(Waiver.signed_at.desc()).all()

    # Map waiver_id -> public_booking_id (if linked)
    links = PublicBookingWaiver.query.all()
    waiver_to_booking = {l.waiver_id: l.public_booking_id for l in links}

    # Group by email (case-insensitive)
    groups = {}
    for w in all_waivers:
        key = (w.client_email or '').strip().lower()
        groups.setdefault(key, []).append(w)

    waiver_groups = []
    for key, ws in groups.items():
        if not key:
            continue
        ws_sorted = sorted(ws, key=lambda x: x.signed_at or datetime.min, reverse=True)
        latest = ws_sorted[0]
        latest_booking_id = waiver_to_booking.get(latest.id)
        waiver_groups.append({
            'email': latest.client_email,
            'count': len(ws_sorted),
            'latest': latest,
            'latest_booking_id': latest_booking_id
        })

    waiver_groups.sort(key=lambda g: g['latest'].signed_at or datetime.min, reverse=True)

    linked_count = len(waiver_to_booking)
    return render_template('admin/waivers.html', waiver_groups=waiver_groups, total_waivers=len(all_waivers), linked_count=linked_count)


@admin_bp.route('/waivers/email/<path:email>')
@login_required
@admin_required
def waivers_by_email(email):
    """View all waiver signatures for a given email."""
    waivers = Waiver.query.filter(func.lower(Waiver.client_email) == email.strip().lower())\
        .order_by(Waiver.signed_at.desc()).all()
    links = PublicBookingWaiver.query.all()
    waiver_to_booking = {l.waiver_id: l.public_booking_id for l in links}
    return render_template('admin/waiver_email.html', email=email, waivers=waivers, waiver_to_booking=waiver_to_booking)


# Social Media Management (Future Integration)

@admin_bp.route('/social')
@login_required
@admin_required
def social_media():
    """Social media management dashboard"""
    # TODO: Integrate with Ayrshare API

    return render_template('admin/social.html')
