"""Public redesign contracts: content, links, fallbacks and existing boundaries."""
import re
from app import db
from app.models.package import Package
from app.experience.public import public_context


def test_empty_public_pages(client):
    for path in ['/packages', '/gallery', '/testimonials', '/about', '/faq', '/contact']:
        r = client.get(path)
        assert r.status_code == 200
        text = r.get_data(as_text=True)
        assert 'alpine-page' in text and '<h1>' in text
        assert 'css/public.css' in text and 'js/public.js' in text
        assert 'cdn.tailwindcss.com' not in text
        assert 'experience/js/main.js' not in text
        assert not re.search(r'\son\w+\s*=', text)


def test_package_prices_and_checkout_guard(client, sample_package, app):
    text = client.get('/packages').get_data(as_text=True)
    assert 'Test Package' in text and '299.99' in text
    assert f'/packages/{sample_package.id}' in text
    assert 'Session+enquiry' in text or 'Session%20enquiry' in text
    assert '/payment/checkout/test' not in text
    text = client.get(f'/packages/{sample_package.id}').get_data(as_text=True)
    assert 'Feature 1' in text and '299.99' in text
    basic = Package(name='Basic Session', description='A configured live session', price=150, duration=2, features=None)
    db.session.add(basic); db.session.commit()
    text = client.get('/packages').get_data(as_text=True)
    assert '/payment/checkout/basic' in text
    basic.price = 200; db.session.commit()
    text = client.get('/packages').get_data(as_text=True)
    assert '/payment/checkout/basic' not in text


def test_gallery_filter_and_detail(client, sample_video):
    text = client.get('/gallery?style=Test+Style').get_data(as_text=True)
    assert sample_video.title in text
    assert 'selected>Test Style' in text
    assert 'experience/media/moments/moment-' in text
    assert 'CONCEPT ARTWORK / PREVIEW PENDING' in text
    for src in re.findall(r'<img[^>]+src="([^"]+)"', text):
        if src.startswith('/static/'):
            assert client.get(src.replace('&amp;', '&')).status_code == 200
    assert 'img.youtube.com' not in text
    assert f'/gallery/{sample_video.id}' in text
    r = client.get(f'/gallery/{sample_video.id}')
    text = r.get_data(as_text=True)
    assert r.status_code == 200
    assert 'data-embed="https://www.youtube-nocookie.com/embed/' in text
    assert '<iframe' not in text  # Third party only loads on explicit play.
    assert f'data-like-url="/api/video/{sample_video.id}/like"' in text
    assert '<meta name="csrf-token"' in text
    assert client.get('/gallery?style=does-not-exist').status_code == 200


def test_testimonials_preserve_content(client, sample_testimonial):
    text = client.get('/testimonials').get_data(as_text=True)
    assert sample_testimonial.testimonial_text in text
    assert sample_testimonial.client_name in text
    assert '5.0' in text and '<meter' in text
    assert 'client-1.jpg' not in text


def test_supporting_pages_and_safe_draft(client):
    faq = client.get('/faq').get_data(as_text=True)
    assert faq.count('<details data-faq>') == 13
    assert 'How do I book a session?' in faq
    contact = client.get('/contact?subject=%22%3E%3Cscript%3Ebad%3C/script%3E').get_data(as_text=True)
    assert 'Prepare email draft' in contact
    assert '<script>bad</script>' not in contact
    assert 'id="contact-draft" class="ap-text-link" hidden' in contact


def test_homepage_and_commerce_still_use_their_own_shell(client):
    home = client.get('/').get_data(as_text=True)
    assert 'experience/js/main.js' in home and 'experience-data' in home
    assert 'alpine-page' not in re.search(r'<body[^>]*>', home)[0]
    login = client.get('/auth/login').get_data(as_text=True)
    assert 'css/public.css' not in login
    assert 'cdn.tailwindcss.com' in login
