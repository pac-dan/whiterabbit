from app import db
from datetime import datetime


class Video(db.Model):
    """Video model for portfolio showcase"""

    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)

    # Video information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # YouTube integration
    youtube_id = db.Column(db.String(50), nullable=False, unique=True, index=True)
    youtube_url = db.Column(db.String(255), nullable=True)

    # Thumbnail (auto-generated from YouTube or custom)
    thumbnail_url = db.Column(db.String(255), nullable=True)

    # Categorization for filtering
    location_tag = db.Column(db.String(100), nullable=True, index=True)  # Backcountry, Terrain Park, Resort, etc.
    style_tag = db.Column(db.String(100), nullable=True, index=True)  # Powder, Freestyle, Freeride, etc.
    rider_level = db.Column(db.String(50), nullable=True, index=True)  # Beginner, Intermediate, Advanced, Expert

    # Before/After comparison (optional)
    is_comparison = db.Column(db.Boolean, default=False)
    before_youtube_id = db.Column(db.String(50), nullable=True)
    after_youtube_id = db.Column(db.String(50), nullable=True)

    # Visibility and featuring
    is_featured = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)

    # Display order
    display_order = db.Column(db.Integer, default=0)

    # Video metadata
    duration = db.Column(db.Integer, nullable=True)  # Duration in seconds
    resolution = db.Column(db.String(20), nullable=True)  # 1080p, 4K, etc.
    fps = db.Column(db.Integer, nullable=True)  # Frames per second

    # Associated booking (optional - if video is from a customer session)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    booking = db.relationship('Booking', backref='videos', foreign_keys=[booking_id])

    def __repr__(self):
        return f'<Video {self.title}>'

    def to_dict(self):
        """Convert video to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'youtube_id': self.youtube_id,
            'youtube_url': self.youtube_url or f'https://www.youtube.com/watch?v={self.youtube_id}',
            'thumbnail_url': self.thumbnail_url or f'https://img.youtube.com/vi/{self.youtube_id}/maxresdefault.jpg',
            'location_tag': self.location_tag,
            'style_tag': self.style_tag,
            'rider_level': self.rider_level,
            'is_comparison': self.is_comparison,
            'before_youtube_id': self.before_youtube_id,
            'after_youtube_id': self.after_youtube_id,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'duration': self.duration,
            'resolution': self.resolution,
            'fps': self.fps,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

    @property
    def embed_url(self):
        """Get YouTube embed URL"""
        return f'https://www.youtube.com/embed/{self.youtube_id}'
    
    @property
    def thumbnail(self):
        """Get YouTube thumbnail URL"""
        # Use custom thumbnail if set, otherwise use YouTube auto-generated thumbnail
        if self.thumbnail_url:
            return self.thumbnail_url
        # maxresdefault.jpg is highest quality (1920x1080), fallback to hqdefault.jpg (480x360)
        return f'https://img.youtube.com/vi/{self.youtube_id}/maxresdefault.jpg'

    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()

    def increment_likes(self):
        """Increment like count"""
        self.like_count += 1
        db.session.commit()

    @staticmethod
    def get_featured_videos(limit=6):
        """Get featured videos"""
        return Video.query.filter_by(is_featured=True, is_published=True)\
            .order_by(Video.display_order, Video.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_by_filters(location=None, style=None, level=None, limit=None):
        """Get videos filtered by tags"""
        query = Video.query.filter_by(is_published=True)

        if location:
            query = query.filter_by(location_tag=location)

        if style:
            query = query.filter_by(style_tag=style)

        if level:
            query = query.filter_by(rider_level=level)

        query = query.order_by(Video.display_order, Video.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_recent_videos(limit=12):
        """Get most recent videos"""
        return Video.query.filter_by(is_published=True)\
            .order_by(Video.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_all_tags():
        """Get all unique tags for filters"""
        locations = db.session.query(Video.location_tag)\
            .filter(Video.location_tag.isnot(None), Video.is_published == True)\
            .distinct()\
            .all()

        styles = db.session.query(Video.style_tag)\
            .filter(Video.style_tag.isnot(None), Video.is_published == True)\
            .distinct()\
            .all()

        levels = db.session.query(Video.rider_level)\
            .filter(Video.rider_level.isnot(None), Video.is_published == True)\
            .distinct()\
            .all()

        return {
            'locations': [loc[0] for loc in locations if loc[0]],
            'styles': [style[0] for style in styles if style[0]],
            'levels': [level[0] for level in levels if level[0]]
        }
