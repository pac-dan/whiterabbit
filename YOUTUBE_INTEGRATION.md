# YouTube Video Integration

## Overview

Momentum Clips now uses **YouTube** for video hosting instead of Vimeo. This provides several advantages:
- ✅ **Free hosting** - No monthly subscription costs
- ✅ **Auto-generated thumbnails** - YouTube provides multiple thumbnail qualities
- ✅ **Wide compatibility** - Works everywhere without API keys
- ✅ **Better embeds** - Native YouTube player with all features
- ✅ **SEO benefits** - Videos appear in Google/YouTube search

## How It Works

### Video Model

The `Video` model has been updated to use YouTube video IDs:

**Fields:**
- `youtube_id` - The YouTube video ID (e.g., "dQw4w9WgXcQ" from `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
- `youtube_url` - Optional full YouTube URL
- `thumbnail_url` - Optional custom thumbnail (auto-generated from YouTube if not set)

**Properties:**
- `embed_url` - Returns YouTube embed URL: `https://www.youtube.com/embed/{youtube_id}`
- `thumbnail` - Returns thumbnail URL (custom or YouTube auto-generated)

### YouTube Thumbnail URLs

YouTube provides several thumbnail qualities:

```python
# Maximum resolution (1920x1080) - recommended
https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg

# High quality (480x360)
https://img.youtube.com/vi/{VIDEO_ID}/hqdefault.jpg

# Medium quality (320x180)
https://img.youtube.com/vi/{VIDEO_ID}/mqdefault.jpg

# Standard quality (120x90)
https://img.youtube.com/vi/{VIDEO_ID}/default.jpg
```

## Adding Videos

### Method 1: Admin Dashboard

1. Go to Admin → Videos → Add New Video
2. Enter video details
3. For YouTube ID, use just the ID part:
   - From `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - Extract: `dQw4w9WgXcQ`
4. Save the video

### Method 2: Database Seeding

Update `app.py` or your seed script:

```python
Video(
    title="My Awesome Snowboard Video",
    description="Epic powder day in Bansko",
    youtube_id="dQw4w9WgXcQ",  # Just the ID
    location_tag="Backcountry",
    style_tag="Powder",
    rider_level="Advanced",
    is_featured=True
)
```

### Method 3: Python Shell

```bash
python
>>> from app import create_app, db
>>> from app.models.video import Video
>>> app = create_app()
>>> with app.app_context():
...     video = Video(
...         title="Test Video",
...         youtube_id="dQw4w9WgXcQ",
...         location_tag="Resort",
...         style_tag="Freestyle",
...         rider_level="Intermediate"
...     )
...     db.session.add(video)
...     db.session.commit()
```

## Template Usage

### Video Gallery (index.html, gallery/index.html)

Thumbnail display:
```html
<img src="https://img.youtube.com/vi/{{ video.youtube_id }}/maxresdefault.jpg" 
     alt="{{ video.title }}">
```

### Video Detail Page (gallery/video_detail.html)

Embed player:
```html
<iframe src="https://www.youtube.com/embed/{{ video.youtube_id }}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
</iframe>
```

### Before/After Comparison

For comparison videos:
```html
<!-- Before -->
<iframe src="https://www.youtube.com/embed/{{ video.before_youtube_id }}"></iframe>

<!-- After -->
<iframe src="https://www.youtube.com/embed/{{ video.after_youtube_id }}"></iframe>
```

## Getting YouTube Video IDs

### From YouTube URL

**Standard URL:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
                                 ↑ This is the ID
```

**Short URL:**
```
https://youtu.be/dQw4w9WgXcQ
                 ↑ This is the ID
```

**Embed URL:**
```
https://www.youtube.com/embed/dQw4w9WgXcQ
                              ↑ This is the ID
```

### Programmatically Extract ID

```python
import re

def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

# Usage
video_id = extract_youtube_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
# Returns: 'dQw4w9WgXcQ'
```

## Uploading Your Videos to YouTube

### 1. Create YouTube Channel

1. Go to [YouTube Studio](https://studio.youtube.com/)
2. Create a channel for "Momentum Clips"
3. Customize branding (logo, banner)

### 2. Upload Video

1. Click "Create" → "Upload Video"
2. Select your video file
3. Add title, description
4. Set visibility:
   - **Public** - Anyone can find and watch
   - **Unlisted** - Only people with the link can watch (recommended for client videos)
   - **Private** - Only you can watch

### 3. Get Video ID

After upload, the video URL will be:
```
https://www.youtube.com/watch?v=YOUR_VIDEO_ID
```

Copy the ID and add it to your database.

## Privacy Considerations

### For Client Videos

Use **Unlisted** visibility:
- Videos won't appear in YouTube search
- Only people with the link can watch
- Still embeddable on your website
- Perfect for private client work

### For Portfolio/Marketing

Use **Public** visibility:
- Appears in YouTube and Google search
- Great for SEO and discovery
- Helps attract new customers

## Migration from Vimeo

If you have existing Vimeo videos:

1. Download videos from Vimeo
2. Upload to YouTube
3. Update database with new YouTube IDs:

```python
from app import create_app, db
from app.models.video import Video

app = create_app()
with app.app_context():
    video = Video.query.filter_by(id=123).first()
    video.youtube_id = 'NEW_YOUTUBE_ID'
    db.session.commit()
```

## Benefits of YouTube Hosting

### Cost Savings
- Vimeo Pro: $20/month
- YouTube: **FREE** (unlimited uploads for videos under 12 hours)

### Features
- ✅ Automatic transcoding to multiple qualities
- ✅ Adaptive streaming based on connection speed
- ✅ Mobile optimization
- ✅ Closed captions/subtitles support
- ✅ Analytics (views, watch time, demographics)
- ✅ Comments (can be disabled)
- ✅ Playlist organization
- ✅ Live streaming

### SEO Benefits
- Videos appear in YouTube search (2nd largest search engine)
- Videos appear in Google video results
- Backlinks to your website
- Channel branding opportunities

## Technical Details

### Embed Parameters

You can customize the YouTube embed with parameters:

```html
<iframe src="https://www.youtube.com/embed/VIDEO_ID?autoplay=0&controls=1&rel=0"></iframe>
```

Common parameters:
- `autoplay=0` - Don't autoplay (1 = autoplay)
- `controls=1` - Show controls (0 = hide)
- `rel=0` - Don't show related videos at end
- `modestbranding=1` - Minimal YouTube branding
- `showinfo=0` - Hide title/uploader (deprecated)

### Responsive Embed

The current implementation uses a 16:9 aspect ratio container:

```html
<div style="padding:56.25% 0 0 0;position:relative;">
    <iframe src="..." style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe>
</div>
```

## Troubleshooting

### Thumbnail Not Loading

If max resolution thumbnail doesn't exist, YouTube returns 404. Fallback options:

```html
<!-- Try maxresdefault first -->
<img src="https://img.youtube.com/vi/{{ video.youtube_id }}/maxresdefault.jpg"
     onerror="this.src='https://img.youtube.com/vi/{{ video.youtube_id }}/hqdefault.jpg'">
```

### Video Won't Embed

Check:
1. Video is not set to "Private" (must be Public or Unlisted)
2. Video ID is correct (11 characters)
3. Video hasn't been removed or made unavailable

### Database Schema Issues

If you get column errors, reset the database:

```bash
python reset_and_seed.py
```

This drops old Vimeo columns and creates new YouTube columns.

##Status

✅ **Migration Complete**: All video functionality updated to YouTube  
✅ **Templates Updated**: Gallery, detail pages, homepage  
✅ **Model Updated**: YouTube fields and properties  
✅ **Database Seeded**: Sample videos with YouTube IDs  

---

**Recommendation**: Start uploading your snowboard videos to your YouTube channel and add them to the gallery!

