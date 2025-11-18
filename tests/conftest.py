"""Pytest configuration and fixtures"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create a sample user"""
    user = User(
        email='test@example.com',
        name='Test User',
        is_admin=False
    )
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app):
    """Create an admin user"""
    admin = User(
        email='admin@example.com',
        name='Admin User',
        is_admin=True
    )
    admin.set_password('adminpass123')
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def sample_package(app):
    """Create a sample package"""
    package = Package(
        name='Test Package',
        description='A test package for unit testing',
        price=299.99,
        duration=4,
        features='Feature 1, Feature 2, Feature 3',
        is_active=True
    )
    db.session.add(package)
    db.session.commit()
    return package


@pytest.fixture
def sample_video(app):
    """Create a sample video"""
    video = Video(
        title='Test Video',
        description='A test video for unit testing',
        youtube_id='dQw4w9WgXcQ',
        location_tag='Test Location',
        style_tag='Test Style',
        rider_level='Intermediate',
        is_featured=True
    )
    db.session.add(video)
    db.session.commit()
    return video


@pytest.fixture
def sample_testimonial(app):
    """Create a sample testimonial"""
    testimonial = Testimonial(
        client_name='Test Client',
        rating=5,
        testimonial_text='This is a test testimonial',
        project_type='Test Package',
        is_featured=True
    )
    db.session.add(testimonial)
    db.session.commit()
    return testimonial

