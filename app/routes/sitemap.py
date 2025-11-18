"""
Sitemap and robots.txt routes for SEO
"""
from flask import Blueprint, render_template, make_response, url_for
from datetime import datetime
from app.models.video import Video
from app.models.package import Package

seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/sitemap.xml')
def sitemap():
    """Generate dynamic sitemap for search engines"""
    pages = []
    
    # Static pages
    static_pages = [
        {'loc': url_for('main.index', _external=True), 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': url_for('main.packages', _external=True), 'priority': '0.9', 'changefreq': 'weekly'},
        {'loc': url_for('main.gallery', _external=True), 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': url_for('main.about', _external=True), 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': url_for('main.contact', _external=True), 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': url_for('auth.login', _external=True), 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': url_for('auth.register', _external=True), 'priority': '0.6', 'changefreq': 'monthly'},
    ]
    
    for page in static_pages:
        pages.append({
            'loc': page['loc'],
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'priority': page['priority'],
            'changefreq': page['changefreq']
        })
    
    # Dynamic package pages
    try:
        packages = Package.get_active_packages()
        for package in packages:
            pages.append({
                'loc': url_for('main.package_detail', package_id=package.id, _external=True),
                'lastmod': package.updated_at.strftime('%Y-%m-%d') if hasattr(package, 'updated_at') else datetime.utcnow().strftime('%Y-%m-%d'),
                'priority': '0.8',
                'changefreq': 'weekly'
            })
    except Exception:
        pass
    
    # Dynamic video pages
    try:
        videos = Video.query.filter_by(is_featured=True).limit(50).all()
        for video in videos:
            pages.append({
                'loc': url_for('main.video_detail', video_id=video.id, _external=True),
                'lastmod': video.created_at.strftime('%Y-%m-%d') if hasattr(video, 'created_at') else datetime.utcnow().strftime('%Y-%m-%d'),
                'priority': '0.7',
                'changefreq': 'monthly'
            })
    except Exception:
        pass
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response


@seo_bp.route('/robots.txt')
def robots():
    """Generate robots.txt for search engine crawlers"""
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /booking/
Disallow: /auth/
Disallow: /api/

Sitemap: {url_for('seo.sitemap', _external=True)}
"""
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

