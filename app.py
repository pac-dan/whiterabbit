"""
SnowboardMedia - Main Application Entry Point

A full-featured web platform for booking professional snowboard video sessions,
showcasing portfolio work, and managing customer interactions with AI-powered
customer service.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app, socketio, db

# Create Flask application
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    from app.models.user import User
    from app.models.booking import Booking
    from app.models.package import Package
    from app.models.video import Video
    from app.models.testimonial import Testimonial

    return {
        'db': db,
        'User': User,
        'Booking': Booking,
        'Package': Package,
        'Video': Video,
        'Testimonial': Testimonial
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized successfully!')


@app.cli.command()
def create_admin():
    """Create an admin user"""
    from app.models.user import User
    from getpass import getpass

    print("Create Admin User")
    print("-" * 50)

    email = input("Email: ")
    name = input("Name: ")
    password = getpass("Password: ")
    confirm_password = getpass("Confirm Password: ")

    if password != confirm_password:
        print("Passwords don't match!")
        return

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f"User with email {email} already exists!")
        return

    # Create admin user
    admin = User(
        email=email,
        name=name,
        is_admin=True
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print(f"Admin user '{name}' created successfully!")


@app.cli.command()
def seed_db():
    """Seed the database with sample data"""
    from app.models.package import Package
    from app.models.video import Video
    from app.models.testimonial import Testimonial
    from datetime import datetime

    print("Seeding database with sample data...")

    # Create sample packages
    packages = [
        Package(
            name="Beginner Bundle",
            description="Perfect for first-timers! We'll capture your initial runs and create a memorable highlight reel.",
            price=199.99,
            duration=2,
            features="2-hour session, 1 edited video (3-5 min), 10+ raw clips, Music & effects, Social media formats",
            is_active=True
        ),
        Package(
            name="Pro Session",
            description="Full-day coverage with professional editing for serious riders.",
            price=499.99,
            duration=6,
            features="6-hour session, 2 edited videos (5-10 min each), 50+ raw clips, Drone footage, Before/after comparisons, Priority editing",
            is_active=True
        ),
        Package(
            name="Epic Package",
            description="Multi-day coverage with cinematic editing. Perfect for week-long trips!",
            price=1299.99,
            duration=24,
            features="3-day coverage, 3 edited videos (10-15 min each), Unlimited raw footage, Drone & GoPro, Custom music selection, Photo package included",
            is_active=True
        ),
    ]

    for package in packages:
        db.session.add(package)

    # Create sample videos (using YouTube video IDs)
    # Note: Replace these with your actual YouTube video IDs
    videos = [
        Video(
            title="Epic Backcountry Run - Powder Day",
            description="Amazing powder day at the backcountry bowl with fresh tracks and perfect conditions",
            youtube_id="QlMPuDNU5F8",  # Example snowboarding video
            location_tag="Backcountry",
            style_tag="Powder",
            rider_level="Advanced",
            is_featured=True,
            view_count=1250,
            like_count=89
        ),
        Video(
            title="Park Session - Tricks & Rails",
            description="Shredding the terrain park with style, hitting rails and boxes with perfect execution",
            youtube_id="FLOkz2xQ6Fo",  # Example snowboarding video
            location_tag="Terrain Park",
            style_tag="Freestyle",
            rider_level="Intermediate",
            is_featured=True,
            view_count=890,
            like_count=62
        ),
        Video(
            title="First Timer's Success Story",
            description="From nervous beginner to confident rider - watch the incredible progression in just one day",
            youtube_id="7Q4ioF2OHlE",  # Example snowboarding video
            location_tag="Beginner Slopes",
            style_tag="Learning",
            rider_level="Beginner",
            is_featured=True,
            view_count=2100,
            like_count=145
        ),
        Video(
            title="Bansko Mountain Highlights",
            description="Epic runs down the slopes of Bansko, Bulgaria's premier snowboard destination",
            youtube_id="dQw4w9WgXcQ",  # Replace with your video
            location_tag="Resort",
            style_tag="All-Mountain",
            rider_level="Intermediate",
            is_featured=True,
            view_count=1580,
            like_count=98
        ),
        Video(
            title="Night Riding Under the Lights",
            description="Experience the magic of night snowboarding with perfectly groomed slopes and atmospheric lighting",
            youtube_id="8q8wq8qQ8q8",  # Replace with your video
            location_tag="Resort",
            style_tag="Night Riding",
            rider_level="Intermediate",
            is_featured=False,
            view_count=756,
            like_count=51
        ),
        Video(
            title="Pro Tricks Tutorial - 360 Spins",
            description="Learn how to nail perfect 360 spins with our expert instructor breaking down the technique",
            youtube_id="abc123def456",  # Replace with your video
            location_tag="Terrain Park",
            style_tag="Freestyle",
            rider_level="Advanced",
            is_featured=False,
            view_count=3200,
            like_count=287
        ),
    ]

    for video in videos:
        db.session.add(video)

    # Create sample testimonials
    testimonials = [
        Testimonial(
            client_name="Sarah Johnson",
            client_photo_url="/static/images/client-1.jpg",
            rating=5,
            testimonial_text="Absolutely incredible experience! The team captured every moment perfectly, and the edited video brought tears to my eyes. Worth every penny!",
            project_type="Pro Session",
            is_featured=True
        ),
        Testimonial(
            client_name="Mike Chen",
            client_photo_url="/static/images/client-2.jpg",
            rating=5,
            testimonial_text="As a beginner, I was nervous about being filmed, but they made me feel so comfortable. The final video shows my progression beautifully!",
            project_type="Beginner Bundle",
            is_featured=True
        ),
        Testimonial(
            client_name="Alex Thompson",
            client_photo_url="/static/images/client-3.jpg",
            rating=5,
            testimonial_text="I've worked with several video companies, and this is by far the best. Professional, creative, and they truly understand snowboarding culture.",
            project_type="Epic Package",
            is_featured=True
        ),
    ]

    for testimonial in testimonials:
        db.session.add(testimonial)

    db.session.commit()
    print("Database seeded successfully!")
    print(f"- Added {len(packages)} packages")
    print(f"- Added {len(videos)} videos")
    print(f"- Added {len(testimonials)} testimonials")


if __name__ == '__main__':
    # Run the application with SocketIO
    # For production, use gunicorn with eventlet worker
    socketio.run(
        app,
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=5000
    )
