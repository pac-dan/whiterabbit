"""Homepage contracts: DB/manifest boundaries, empty content, CSP and caching."""
from copy import deepcopy
import json
import re
from pathlib import Path
from app import db
from app.experience.content import EXPERIENCE, VERSION, build_experience


def manifest(response):
    return json.loads(re.search(rb'id="experience-data"[^>]*>(.*?)</script>', response.data, re.S)[1])


def test_homepage_empty_database(client):
    response = client.get('/')
    assert response.status_code == 200
    data = manifest(response)
    assert len(data['ring']['cards']) == 12
    assert data['packages'] == []
    assert response.data.count(b'<h3>Package coming soon</h3>') == 3
    assert response.data.count(b'data-chapter=') == 6
    assert b'Book your session' in response.data


def test_homepage_real_database_content(client, sample_package, sample_video, sample_testimonial):
    response = client.get('/')
    assert response.status_code == 200
    data = manifest(response)
    assert data['packages'][0]['name'] == sample_package.name
    assert data['packages'][0]['link'] == f'/packages/{sample_package.id}'
    assert data['ring']['cards'][0]['title'] == sample_video.title
    assert sample_video.youtube_id in data['ring']['cards'][0]['link']
    assert sample_testimonial.testimonial_text.encode() in response.data
    assert client.get(data['packages'][0]['link']).status_code == 200


def test_manifest_not_mutated_by_requests(client, sample_video):
    before = deepcopy(EXPERIENCE)
    client.get('/')
    assert EXPERIENCE == before


def test_manual_cards_and_index_overrides(app, monkeypatch):
    from app.experience import content
    custom = deepcopy(EXPERIENCE)
    custom['ring']['source'] = 'manual'
    custom['ring']['cards'][0]['media']['src'] = 'experience/media/first.mp4'
    custom['ring']['cards'][0]['title'] = 'Owner title'
    monkeypatch.setattr(content, 'EXPERIENCE', custom)
    data = build_experience([], [], '/gallery', lambda i: f'/packages/{i}')
    assert data['ring']['cards'][0]['media']['src'].endswith('first.mp4')
    assert data['ring']['cards'][0]['title'] == 'Owner title'
    assert data['ring']['cards'][0]['link'] == '/gallery'


def test_homepage_no_executable_inline_scripts_or_handlers(client):
    text = client.get('/').get_data(as_text=True)
    assert not re.search(r'\son\w+\s*=', text)
    for attributes, body in re.findall(r'<script([^>]*)>(.*?)</script>', text, re.S):
        assert 'src=' in attributes or 'application/json' in attributes or 'application/ld+json' in attributes
    assert 'cdn.tailwindcss.com' not in text
    assert f'?v={VERSION}' in text


def test_experience_cache_only(client):
    for path in ['/static/experience/js/main.js', '/static/vendor/lenis.mjs', '/static/experience/terrain/bansko-height.bin']:
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers['Cache-Control'] == 'public, max-age=31536000, immutable'
    assert 'immutable' not in client.get('/static/css/style.css').headers['Cache-Control']


def test_other_pages(client):
    for path in ['/packages', '/gallery', '/about', '/faq', '/contact', '/testimonials', '/auth/login']:
        response = client.get(path)
        assert response.status_code == 200, path
        assert b'experience/js/main.js' not in response.data
        if path == '/auth/login':
            assert b'cdn.tailwindcss.com' in response.data
        else:
            assert b'cdn.tailwindcss.com' not in response.data
            assert b'alpine-page' in response.data


def test_terrain_binary_and_extrema():
    folder = Path(__file__).resolve().parents[1] / 'app/static/experience/terrain'
    metadata = json.loads((folder/'bansko-height.json').read_text())
    assert (folder/'bansko-height.bin').stat().st_size == 512*512*2
    assert (folder/'bansko-height-256.bin').stat().st_size == 256*256*2
    assert 750 < metadata['minM'] < 1250
    assert 2700 < metadata['maxM'] < 3100


def test_video_journey_manifest_and_poster(client):
    response = client.get('/')
    data = manifest(response)['journey']
    assert data['mode'] == 'video'
    assert data['cues'][0] == [0, 0]
    assert data['cues'][-1][1] == data['cues'][-2][1]
    assert [p[0] for p in data['cues']] == sorted(p[0] for p in data['cues'])
    assert b'id="journey-video"' in response.data
    for name in ['src', 'poster', 'town_poster']:
        assert not data[name].startswith(('C:', 'file:'))
        asset = client.get('/static/' + data[name])
        assert asset.status_code == 200
        assert 'immutable' in asset.headers['Cache-Control']
    video = re.search(rb'<video[^>]*id="journey-video"[^>]*>', response.data)[0]
    assert b'autoplay' not in video and b'loop' not in video


def test_journey_media_range_request(client):
    path = '/static/' + EXPERIENCE['journey']['src']
    response = client.get(path, headers={'Range': 'bytes=0-1023'})
    assert response.status_code == 206
    assert len(response.data) == 1024
    assert response.headers['Content-Type'].startswith('video/mp4')
    assert response.headers['Cache-Control'] == 'public, max-age=31536000, immutable'
