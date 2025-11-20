# Troubleshooting Guide

## Common Issues and Solutions

---

## 🎥 YouTube Video Issues

### Error: `Failed to load resource: net::ERR_BLOCKED_BY_CLIENT`

**Cause:** Browser extensions (ad blockers, privacy tools) are blocking YouTube resources.

**Solutions:**

1. **Disable Ad Blocker for localhost**
   - Click your ad blocker icon (uBlock Origin, AdBlock Plus, etc.)
   - Click "Disable on this site" or add `localhost` to whitelist
   - Refresh the page

2. **Disable Privacy Extensions Temporarily**
   - Privacy Badger, Ghostery, etc. may block YouTube
   - Disable for testing on localhost
   - Re-enable after confirming it works

3. **Try a Different Browser**
   - Test in Chrome Incognito (Ctrl+Shift+N)
   - Or Firefox Private Window
   - Extensions are usually disabled in private mode

4. **Check Browser Settings**
   - Some browsers have built-in tracking protection
   - Chrome: Settings → Privacy → Site Settings → JavaScript (ensure enabled)
   - Firefox: Settings → Privacy → Enhanced Tracking Protection (set to "Standard")

### YouTube Videos Not Playing

**If thumbnails load but videos don't play:**

```html
<!-- Add this to your base.html <head> section -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               frame-src https://www.youtube.com https://www.youtube-nocookie.com;
               img-src 'self' data: https://img.youtube.com https:;">
```

**Already implemented in your app** - Check `app/__init__.py` line 71-108 for CSP configuration.

### YouTube Thumbnails Not Loading

**If thumbnails show broken image:**

Some videos don't have `maxresdefault.jpg`. Use fallback:

```html
<img src="https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg"
     onerror="this.src='https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg'"
     alt="Video thumbnail">
```

**To fix in your templates:**

Update `app/templates/gallery/index.html`:
```html
<!-- Line 122 -->
<img src="https://img.youtube.com/vi/{{ video.youtube_id }}/maxresdefault.jpg" 
     onerror="this.src='https://img.youtube.com/vi/{{ video.youtube_id }}/hqdefault.jpg'"
     alt="{{ video.title }}" 
     class="w-full h-full object-cover group-hover:scale-110 transition duration-300">
```

---

## 🔒 CSRF Token Issues

### Error: `The CSRF token is missing`

**Cause:** Form submission without CSRF token.

**Solutions:**

1. **Check form has hidden tag:**
   ```html
   <form method="POST">
       {{ form.hidden_tag() }}  <!-- This includes CSRF token -->
       <!-- your fields -->
   </form>
   ```

2. **For AJAX requests, include token:**
   ```javascript
   fetch('/api/endpoint', {
       method: 'POST',
       headers: {
           'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
       }
   });
   ```

3. **Add meta tag to base.html:**
   ```html
   <meta name="csrf-token" content="{{ csrf_token() }}">
   ```

---

## 🎤 Retell Voice Widget Issues

### Widget Not Appearing

**Check:**

1. **API Keys in .env:**
   ```env
   RETELL_API_KEY=key_xxxxx
   RETELL_AGENT_ID=agent_xxxxx
   RETELL_PUBLIC_KEY=key_xxxxx
   ```

2. **Check browser console for errors**

3. **Verify widget script loads:**
   - Open DevTools → Network tab
   - Look for `retell-widget.js` or similar
   - Should return 200 status

### TypeError: Cannot read properties of null (reading 'click')

**This is the toggleChat error you're seeing.**

**Fixed in:** `app/templates/gallery/video_detail.html`

The function now checks if chat element exists before trying to click it.

---

## 🗄️ Database Issues

### Error: `no such column: videos.youtube_id`

**Cause:** Old database schema (still using Vimeo columns).

**Solution:**
```bash
python reset_and_seed.py
```

This will:
- Drop all tables
- Recreate with YouTube schema
- Seed with sample data

### Database Locked Error

**Cause:** Multiple processes accessing SQLite database.

**Solution:**
```bash
# Stop all Flask servers
Get-Process python | Stop-Process -Force

# Restart server
python app.py
```

---

## 🔐 Login Issues

### Can't Login / Wrong Password

**Reset admin password:**

Run the database query:
```python
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@momentumclips.com').first()
    user.set_password('NewPassword123')
    db.session.commit()
    print(f"Password updated for {user.email}")
```

Or delete and recreate:
```bash
python reset_and_seed.py
# Then create new admin
```

### Session Expires Immediately

**Check Redis connection:**

If Redis isn't available, sessions fall back to cookies. This is normal for development.

To enable Redis:
```bash
# Install Redis on Windows
# Download from: https://github.com/microsoftarchive/redis/releases

# Or use Docker
docker run -d -p 6379:6379 redis:alpine

# Restart Flask
python app.py
```

---

## 📱 Mobile/Responsive Issues

### Layout Broken on Mobile

**Check:**
1. Viewport meta tag exists in base.html
2. Tailwind CSS is loading
3. Test in browser DevTools mobile view

### Images Too Large

**Optimize images:**
```bash
pip install Pillow

# In Python:
from PIL import Image
img = Image.open('large.jpg')
img.thumbnail((1920, 1080))
img.save('optimized.jpg', quality=85)
```

---

## 🚀 Performance Issues

### Slow Page Load

**Solutions:**

1. **Enable Flask-Compress** (already enabled in your app)

2. **Use CDN for static assets:**
   - Move CSS/JS to CDN when deploying
   - Use Cloudflare or similar

3. **Optimize database queries:**
   ```python
   # Use eager loading for relationships
   videos = Video.query.options(
       db.joinedload(Video.booking)
   ).all()
   ```

4. **Enable caching:**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   
   @cache.cached(timeout=300)
   def get_videos():
       return Video.query.all()
   ```

---

## 🐛 JavaScript Errors

### Common Console Errors

**1. `Uncaught ReferenceError: $ is not defined`**
- jQuery not loaded
- Add to base.html: `<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>`

**2. `Failed to execute 'postMessage'`**
- Usually from YouTube iframe
- Safe to ignore if videos play correctly

**3. `Mixed Content` warnings**
- Loading HTTP resources on HTTPS page
- Ensure all resources use HTTPS URLs

---

## 📧 Email Not Sending

### SMTP Connection Error

**Check .env configuration:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password  # Not your regular password!
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use that password in .env

---

## 💳 Stripe Payment Issues

### Webhook Not Working

**For local testing:**
```bash
# Install Stripe CLI
# Download from: https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks to localhost
stripe listen --forward-to localhost:5000/webhook/stripe
```

### Test Cards Not Working

**Use Stripe test cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Any future date for expiry, any 3 digits for CVC

---

## 🔧 Development Server Issues

### Port 5000 Already in Use

**Solution:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual number)
Stop-Process -Id <PID> -Force

# Or use different port
python app.py --port 5001
```

### Server Crashes on Startup

**Check:**
1. Virtual environment activated
2. All dependencies installed: `pip install -r requirements.txt`
3. .env file exists with required variables
4. Database file exists or can be created

**View full error:**
```bash
python app.py 2>&1 | Out-File -FilePath error.log
notepad error.log
```

---

## 🌐 Browser-Specific Issues

### Works in Chrome but not Firefox

**Common causes:**
1. Firefox blocks mixed content more strictly
2. Different CSP handling
3. WebSocket connection differences

**Test with Firefox Developer Edition** for better debugging tools.

### Works Locally but not in Production

**Check:**
1. Environment variables set correctly
2. HTTPS enabled (required for many features)
3. Database connection string updated
4. Static files served correctly (use CDN or proper static hosting)

---

## 📊 Quick Diagnostic Commands

```bash
# Check if server is running
netstat -ano | findstr :5000

# Check database
sqlite3 instance/snowboard_media.db ".tables"

# Check Python version
python --version

# Check installed packages
pip list | findstr -i "flask"

# Test database connection
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine)"

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('DEBUG:', os.getenv('DEBUG'))"
```

---

## 🆘 Still Having Issues?

### Enable Debug Mode

In `.env`:
```env
DEBUG=True
FLASK_ENV=development
```

### Check Logs

Flask logs appear in the terminal where you ran `python app.py`.

### Browser DevTools

1. Press F12
2. Check Console tab for JavaScript errors
3. Check Network tab for failed requests
4. Check Application tab for cookies/storage issues

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [YouTube IFrame API](https://developers.google.com/youtube/iframe_api_reference)
- [Stripe Testing](https://stripe.com/docs/testing)

---

**Last Updated:** After YouTube integration and CSRF fixes
**Status:** All known issues documented with solutions

