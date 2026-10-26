"""Presentation helpers shared by public pages; commerce rules live elsewhere."""
from pathlib import Path
from decimal import Decimal
from flask import current_app, request, url_for
from .content import EXPERIENCE, VERSION

PUBLIC_ENDPOINTS = frozenset('main.' + name for name in (
    'packages', 'package_detail', 'gallery', 'video_detail',
    'testimonials', 'about', 'faq', 'contact'))


def public_context():
    def static_media(src, fallback):
        if not src:
            src = fallback
        if src.startswith(('https://', 'http://')):
            return src
        local = src.removeprefix('/static/').lstrip('/')
        if not (Path(current_app.static_folder) / local).is_file():
            local = fallback
        return url_for('static', filename=local, v=VERSION)

    featured = None

    def video_media(video, index=0):
        nonlocal featured
        if featured is None:
            from app.models.video import Video
            featured = {v.id: i for i, v in enumerate(Video.get_featured_videos(limit=12))}
        index = featured.get(video.id, index) % len(EXPERIENCE['ring']['cards'])
        card = EXPERIENCE['ring']['cards'][index]
        media = card['media']
        placeholder = f'experience/placeholders/ring-{index+1:02}.webp'
        custom = video.thumbnail_url
        # Seeded YouTube thumbnails are not real artwork. Real custom thumbnails remain usable.
        if custom and 'img.youtube.com' in custom:
            custom = None
        image = media.get('src') if media.get('type') == 'image' else custom
        return dict(image=static_media(image, placeholder), fallback=static_media(None, placeholder),
                    video=static_media(media['src'], placeholder) if media.get('src') and media.get('type') == 'video' else None)

    def checkout_link(package):
        from app.routes.payment import PACKAGES
        key = package.name.split()[0].lower()
        configured = PACKAGES.get(key)
        if configured and int(Decimal(str(package.price)) * 100) == configured['price']:
            return dict(url=url_for('payment.checkout', package=key), label='Book this session')
        return dict(url=url_for('main.contact', subject=f'Session enquiry: {package.name}'), label='Enquire about this session')

    return dict(alpine_page=request.endpoint in PUBLIC_ENDPOINTS,
                experience_version=VERSION, public_video_media=video_media,
                public_static_media=static_media, public_checkout_link=checkout_link,
                experience_content=EXPERIENCE)
