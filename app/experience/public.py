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
        placeholder = EXPERIENCE['films']['moments'][index % len(EXPERIENCE['films']['moments'])]['poster']
        custom = video.thumbnail_url
        # Seeded YouTube thumbnails are not real artwork. Real custom thumbnails remain usable.
        if custom and 'img.youtube.com' in custom:
            custom = None
        image = media.get('src') if media.get('type') == 'image' else media.get('poster') or custom
        return dict(image=static_media(image, placeholder), fallback=static_media(None, placeholder),
                    concept_artwork=not bool(image),
                    video=static_media(media['src'], placeholder) if media.get('src') and media.get('type') == 'video' else None)

    def checkout_link(package):
        return dict(url=url_for('payment.checkout', package=package.id), label='Book this session')

    return dict(alpine_page=request.endpoint in PUBLIC_ENDPOINTS or (request.blueprint in ('admin', 'auth', 'payment')),
                experience_version=VERSION, public_video_media=video_media,
                public_static_media=static_media, public_checkout_link=checkout_link,
                experience_content=EXPERIENCE)
