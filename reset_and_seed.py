"""Reset database and seed with sample data"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.package import Package
from app.models.video import Video
from app.models.testimonial import Testimonial
from app.models.user import User
from app.models.booking import Booking

def reset_and_seed():
    """Drop all tables, recreate them, and seed with sample data"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("DATABASE RESET & SEED")
        print("=" * 70)
        
        # Drop all tables
        print("\n1. Dropping all existing tables...")
        db.drop_all()
        print("   [OK] All tables dropped")
        
        # Create all tables
        print("\n2. Creating all tables...")
        db.create_all()
        print("   [OK] All tables created with new schema")
        
        # Seed with sample data
        print("\n3. Seeding database with sample data...")
        
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
        print(f"   [OK] Added {len(packages)} packages")
        
        # Create sample videos (using VERIFIED EMBEDDABLE YouTube video IDs)
        videos = [
            Video(
                title="Epic Backcountry Run - Powder Day",
                description="Amazing powder day at the backcountry bowl with fresh tracks and perfect conditions",
                youtube_id="dMH0bHeiRNg",  # GoPro snowboarding (embedding allowed)
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
                youtube_id="yPYZpwSpKmA",  # Red Bull snowboarding (embedding allowed)
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
                youtube_id="SQyTWk7OxSI",  # Snowboarding tutorial (verified embeddable)
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
                youtube_id="X-iJD0CgL6Y",  # Mountain snowboarding (verified embeddable)
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
                youtube_id="ScMzIvxBSi4",  # Night snowboarding POV (verified embeddable)
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
                youtube_id="HGL8r5LRZGA",  # Snowboard tricks tutorial (verified embeddable)
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
        print(f"   [OK] Added {len(videos)} videos")
        
        # Create sample testimonials
        testimonials = [
            Testimonial(
                client_name="Sarah Johnson",
                client_photo_url="/static/images/hero_2.jpg",
                rating=5,
                testimonial_text="Absolutely incredible experience! The team captured every moment perfectly, and the edited video brought tears to my eyes. Worth every penny!",
                project_type="Pro Session",
                is_featured=True
            ),
            Testimonial(
                client_name="Mike Chen",
                client_photo_url="/static/images/hero_2.jpg",
                rating=5,
                testimonial_text="As a beginner, I was nervous about being filmed, but they made me feel so comfortable. The final video shows my progression beautifully!",
                project_type="Beginner Bundle",
                is_featured=True
            ),
            Testimonial(
                client_name="Alex Thompson",
                client_photo_url="/static/images/hero_2.jpg",
                rating=5,
                testimonial_text="I've worked with several video companies, and this is by far the best. Professional, creative, and they truly understand snowboarding culture.",
                project_type="Epic Package",
                is_featured=True
            ),
        ]
        
        for testimonial in testimonials:
            db.session.add(testimonial)
        print(f"   [OK] Added {len(testimonials)} testimonials")
        
        db.session.commit()
        
        # Print summary
        print("\n" + "=" * 70)
        print("[SUCCESS] DATABASE RESET & SEED COMPLETE!")
        print("=" * 70)
        print(f"\nDatabase Summary:")
        print(f"  Packages: {Package.query.count()}")
        print(f"  Videos: {Video.query.count()}")
        print(f"  Testimonials: {Testimonial.query.count()}")
        print(f"  Users: {User.query.count()}")
        print(f"  Bookings: {Booking.query.count()}")
        print("\n" + "=" * 70)
        print("Next step: Create an admin user with:")
        print("  python create_admin.py")
        print("=" * 70)

if __name__ == '__main__':
    reset_and_seed()

