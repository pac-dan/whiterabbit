"""Tests for database models"""
import pytest
from app.models.user import User
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial


class TestUserModel:
    """Tests for User model"""
    
    def test_create_user(self, app, sample_user):
        """Test user creation"""
        assert sample_user.id is not None
        assert sample_user.email == 'test@example.com'
        assert sample_user.name == 'Test User'
        assert sample_user.is_admin == False
    
    def test_password_hashing(self, app, sample_user):
        """Test password hashing and verification"""
        assert sample_user.check_password('testpassword123')
        assert not sample_user.check_password('wrongpassword')
    
    def test_admin_user(self, app, admin_user):
        """Test admin user creation"""
        assert admin_user.is_admin == True


class TestPackageModel:
    """Tests for Package model"""
    
    def test_create_package(self, app, sample_package):
        """Test package creation"""
        assert sample_package.id is not None
        assert sample_package.name == 'Test Package'
        assert sample_package.price == 299.99
        assert sample_package.is_active == True
    
    def test_get_active_packages(self, app, sample_package):
        """Test getting active packages"""
        packages = Package.get_active_packages()
        assert len(packages) > 0
        assert sample_package in packages


class TestVideoModel:
    """Tests for Video model"""
    
    def test_create_video(self, app, sample_video):
        """Test video creation"""
        assert sample_video.id is not None
        assert sample_video.title == 'Test Video'
        assert sample_video.youtube_id == 'dQw4w9WgXcQ'
    
    def test_video_embed_url(self, app, sample_video):
        """Test YouTube embed URL generation"""
        assert sample_video.embed_url == 'https://www.youtube.com/embed/dQw4w9WgXcQ'
    
    def test_video_thumbnail(self, app, sample_video):
        """Test YouTube thumbnail URL generation"""
        expected = 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
        assert sample_video.thumbnail == expected
    
    def test_increment_views(self, app, sample_video):
        """Test view count increment"""
        initial_views = sample_video.view_count
        sample_video.increment_views()
        assert sample_video.view_count == initial_views + 1


class TestTestimonialModel:
    """Tests for Testimonial model"""
    
    def test_create_testimonial(self, app, sample_testimonial):
        """Test testimonial creation"""
        assert sample_testimonial.id is not None
        assert sample_testimonial.client_name == 'Test Client'
        assert sample_testimonial.rating == 5
    
    def test_get_featured_testimonials(self, app, sample_testimonial):
        """Test getting featured testimonials"""
        testimonials = Testimonial.get_featured_testimonials()
        assert len(testimonials) > 0
        assert sample_testimonial in testimonials

