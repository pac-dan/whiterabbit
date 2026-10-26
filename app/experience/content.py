"""The owner's single content manifest. Paths are relative to Flask static/.

Drop files in static/experience/media/, then replace the relevant src=None.
Database package/video/testimonial copy stays managed by the existing admin.
"""
from copy import deepcopy

VERSION = 'bansko-1'
EXPERIENCE = {
    'hero': {
        'headline': 'We film your best run.',
        'subline': 'Snowboard video production in Bansko.',
        'background_video': {'type': 'video', 'src': None, 'poster': None},
    },
    'rider': {'type': 'model', 'src': None, 'scale': 1.0, 'animation': None},
    'beats': [
        {'label': '4K follow-cam', 'media': {'type': 'video', 'src': None}},
        {'label': 'Drone shots', 'media': {'type': 'video', 'src': None}},
        {'label': 'Edited the same day', 'media': {'type': 'image', 'src': None}},
    ],
    'ring': {
        'title': 'Recent edits', 'source': 'videos', 'count': 12,
        'cards': [{'title': f'Your next great run / {i:02}',
                   'tags': 'Bansko / Snowboard films',
                   'media': {'type': 'video', 'src': None}, 'link': None}
                  for i in range(1, 13)],
    },
    'gates': {'title': 'Find your line.', 'media': [{'type': 'image', 'src': None} for _ in range(3)]},
    'portal': {'title': 'A run worth reliving.', 'media': {'type': 'image', 'src': None}},
    'finale': {'headline': 'Book your session', 'button': 'See packages',
               'subline': 'You ride. We make it unforgettable.'},
    'labels': {'location': 'Bansko, Bulgaria', 'range': 'Pirin mountains',
               'scroll': 'Scroll to drop in', 'drop': 'Leave a little more than tracks.',
               'loading': 'Finding your line', 'placeholder': 'Footage slot',
               'empty_package': 'Package coming soon', 'empty_package_note': 'Something worth waiting for.',
               'empty_review': 'Your story starts on the mountain.',
               'collection_caption': 'A few seconds. A whole feeling.'},
    'chapters': ['Summit', 'Drop in', 'The ring', 'Packages', 'Portal', 'Bansko at night'],
}


def build_experience(videos, packages, gallery_url, package_url):
    """Copy before resolving DB content so requests never mutate the manifest."""
    data = deepcopy(EXPERIENCE)
    cards = data['ring']['cards']
    count = max(8, min(12, int(data['ring']['count'])))
    data['ring']['count'] = count
    resolved = []
    for i in range(count):
        card = deepcopy(cards[i] if i < len(cards) else cards[i % len(cards)])
        if data['ring']['source'] == 'videos' and videos:
            video = videos[i % len(videos)]
            card['title'] = video.title
            card['tags'] = ' / '.join(filter(None, [video.location_tag, video.style_tag, video.rider_level]))
            card['link'] = card.get('link') or (f'https://www.youtube.com/watch?v={video.youtube_id}' if video.youtube_id else gallery_url)
        card['link'] = card.get('link') or gallery_url
        card['placeholder'] = f'experience/placeholders/ring-{i+1:02}.webp'
        resolved.append(card)
    data['ring']['cards'] = resolved
    data['packages'] = [dict(name=p.name, price=float(p.price), duration=p.duration,
                            features=p.to_dict()['features'][:3], link=package_url(p.id)) for p in packages]
    return data
