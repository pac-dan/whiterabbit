from flask import Blueprint, render_template, request, jsonify
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial
from app import db, limiter

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
