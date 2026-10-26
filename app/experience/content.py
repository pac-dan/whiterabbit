"""The owner's single content manifest. Paths are relative to Flask static/.

Drop files in static/experience/media/, then replace the relevant src=None.
Database package/video/testimonial copy stays managed by the existing admin.
"""
from copy import deepcopy

VERSION = 'bansko-refine-1'
EXPERIENCE = {
    'journey': {
        'mode': 'video',  # 'procedural' restores the previous terrain/rider engine.
        'src': 'experience/media/bansko-descent-720-v3.mp4',
        'mobile_src': 'experience/media/bansko-descent-540-v3.mp4',
        'poster': 'experience/media/bansko-journey-poster.webp',
        'town_poster': 'experience/media/bansko-town-poster.webp',
        'fps': 24,
        # Progress spans hero top to town arrival, independently of later content.
        # Hold the opening through the first quarter of that scroll distance.
        'cues': [[0, 0], [.25, 0], [.42, .15], [.80, .72], [1, .995], [1.1, .995]],
        # object-position X percentages; source rider stays near the centre.
        'framing': [[0, 52], [.277, 57], [.61, 50], [.75, 53], [1, 58]],
    },
    'hero': {
        'headline': 'We film your best run.',
        'subline': 'Snowboard video production in Bansko.',
        'button': 'Book your session',
        'background_video': {'type': 'video', 'src': None, 'poster': None},
    },
    'rider': {'type': 'model', 'src': None, 'scale': 1.0, 'animation': None,
              'height': 2.5, 'board_node': 'Snowboard', 'poses': None},
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
    'arrival': {'headline': 'Back in Bansko.', 'subline': 'The run ends. The feeling stays.'},
    'films': {'title': 'Recent edits', 'subline': 'Follow the feeling. Find your film.',
              'concept': {'title': 'From mountain to town', 'label': 'Generated concept film',
                          'poster': 'experience/media/bansko-journey-poster.webp',
                          'src': 'experience/media/bansko-descent-720-v3.mp4'},
              'missing_poster_label': 'Film preview unavailable'},
    'labels': {'location': 'Bansko, Bulgaria', 'range': 'Pirin mountains',
               'scroll': 'Scroll to drop in', 'drop': 'Leave a little more than tracks.',
               'loading': 'Finding your line', 'placeholder': 'Footage slot',
               'empty_package': 'Package coming soon', 'empty_package_note': 'Something worth waiting for.',
               'empty_review': 'Your story starts on the mountain.',
               'collection_caption': 'A few seconds. A whole feeling.'},
    'chapters': ['The opening', 'The descent', 'Bansko arrival', 'The films', 'Your session', 'Book your session'],
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
    # A supplied concept film is labelled honestly; DB entries are never duplicated
    # to pad a carousel. Seeded YouTube artwork is not presented as client imagery.
    concept = data['films']['concept']
    films = [dict(title=concept['title'], tags=concept['label'], poster=concept['poster'],
                  src=concept['src'], youtube_id=None, link=gallery_url, concept=True,
                  fallback=concept['poster'], missing=False)]
    for i, video in enumerate(videos):
        override = cards[i % len(cards)].get('media', {})
        poster = override.get('poster') or (override.get('src') if override.get('type') == 'image' else None)
        custom = video.thumbnail_url
        if not poster and custom and 'img.youtube.com' not in custom:
            poster = custom
        fallback = 'images/hero_2.jpg' if i % 2 else 'images/hero_1.jpg'
        films.append(dict(title=video.title, tags=' / '.join(filter(None,[video.location_tag,video.style_tag])),
                          poster=poster or fallback, fallback=fallback, missing=not bool(poster),
                          src=override.get('src') if override.get('type') == 'video' else None,
                          youtube_id=video.youtube_id, link=f'{gallery_url}/{video.id}', concept=False))
    data['films']['cards'] = films
    data['packages'] = [dict(name=p.name, price=float(p.price), duration=p.duration,
                            features=p.to_dict()['features'][:3], link=package_url(p.id)) for p in packages]
    return data
