"""Update testimonial photos to use hero_2.jpg"""
from app import create_app, db
from app.models.testimonial import Testimonial

def update_photos():
    """Update all testimonial photos to use hero_2.jpg"""
    app = create_app()
    
    with app.app_context():
        # Get all testimonials
        testimonials = Testimonial.query.all()
        
        if not testimonials:
            print("No testimonials found in database.")
            return
        
        # Update all testimonials to use hero_2.jpg
        for testimonial in testimonials:
            testimonial.client_photo_url = '/static/images/hero_2.jpg'
        
        db.session.commit()
        
        print("=" * 70)
        print("[SUCCESS] Testimonial Photos Updated!")
        print("=" * 70)
        print(f"\nUpdated {len(testimonials)} testimonial(s) to use hero_2.jpg")
        print("\nTestimonials updated:")
        for testimonial in testimonials:
            print(f"  - {testimonial.client_name}")
        print("\n" + "=" * 70)

if __name__ == '__main__':
    update_photos()

