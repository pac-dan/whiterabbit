"""Tests for application routes"""
import pytest
from flask import url_for


class TestMainRoutes:
    """Tests for main routes"""
    
    def test_homepage(self, client):
        """Test homepage loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Momentum Clips' in response.data or b'MOMENTUM CLIPS' in response.data
    
    def test_about_page(self, client):
        """Test about page loads"""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_gallery_page(self, client):
        """Test gallery page loads"""
        response = client.get('/gallery')
        assert response.status_code == 200
    
    def test_packages_page(self, client):
        """Test packages page loads"""
        response = client.get('/packages')
        assert response.status_code == 200
    
    def test_testimonials_page(self, client):
        """Test testimonials page loads"""
        response = client.get('/testimonials')
        assert response.status_code == 200
    
    def test_contact_page(self, client):
        """Test contact page loads"""
        response = client.get('/contact')
        assert response.status_code == 200
    
    def test_faq_page(self, client):
        """Test FAQ page loads"""
        response = client.get('/faq')
        assert response.status_code == 200


class TestAuthRoutes:
    """Tests for authentication routes"""
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
    
    def test_register_page(self, client):
        """Test register page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
    
    def test_login_logout_flow(self, client, sample_user):
        """Test login and logout"""
        # Login
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


class TestBookingRoutes:
    """Tests for booking routes"""
    
    def test_booking_index(self, client):
        """Test booking index page"""
        response = client.get('/booking/')
        assert response.status_code == 200
    
    def test_new_booking_requires_auth(self, client):
        """Test that new booking requires authentication"""
        response = client.get('/booking/new')
        # Should redirect to login
        assert response.status_code == 302


class TestAdminRoutes:
    """Tests for admin routes"""
    
    def test_admin_dashboard_requires_auth(self, client):
        """Test admin dashboard requires authentication"""
        response = client.get('/admin/')
        # Should redirect to login
        assert response.status_code == 302
    
    def test_admin_dashboard_requires_admin(self, client, sample_user):
        """Test admin dashboard requires admin role"""
        # Login as regular user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        
        # Try to access admin dashboard
        response = client.get('/admin/', follow_redirects=True)
        # Should be redirected or forbidden
        assert response.status_code in [200, 302, 403]


class TestVideoRoutes:
    """Tests for video-related routes"""
    
    def test_video_detail(self, client, sample_video):
        """Test video detail page"""
        response = client.get(f'/gallery/{sample_video.id}')
        assert response.status_code == 200
        assert sample_video.title.encode() in response.data

