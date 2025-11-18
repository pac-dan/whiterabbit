# SnowboardMedia Quick Start Guide

Get up and running with SnowboardMedia in under 10 minutes!

## Prerequisites

- Python 3.11 or higher
- Git
- A code editor (VS Code recommended)

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
cd C:\Users\Dan
cd whiterabbit

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment (2 minutes)

```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux
```

Edit `.env` with minimum required settings:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-later

# For development, use SQLite (no MySQL needed!)
DATABASE_URL=sqlite:///snowboard_media.db

# Get free API keys:
# Claude AI: https://console.anthropic.com/ ($5 free credit)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Stripe Test Mode: https://dashboard.stripe.com/test/apikeys (free)
STRIPE_SECRET_KEY=sk_test_your-key-here
STRIPE_PUBLISHABLE_KEY=pk_test_your-key-here

# Optional for now (can add later)
# AYRSHARE_API_KEY=
# VIMEO_ACCESS_TOKEN=

# For development, use in-memory Redis (or skip WebSocket chat for now)
REDIS_URL=redis://localhost:6379/0
```

## Step 3: Initialize Database (1 minute)

```bash
# Create database tables
python app.py init-db

# Add sample data (packages, videos, testimonials)
python app.py seed-db

# Create admin account
python app.py create-admin
# Enter your email, name, and password when prompted
```

## Step 4: Run the Application! (30 seconds)

```bash
python app.py
```

Open your browser: **http://localhost:5000**

## What You Can Do Now

### Without API Keys
✅ Browse the homepage
✅ View packages and gallery
✅ Read testimonials
✅ Register/login
✅ View profile

### With Claude API Key
✅ **AI Chat Assistant** - Click the blue chat button

### With Stripe Test Keys
✅ **Create Bookings** - Book a session (use test card: `4242 4242 4242 4242`)

### With Ayrshare Key
✅ **Social Media Posting** - Auto-post to Instagram, TikTok, etc.

## Quick Test Workflow

1. **Visit Homepage**: http://localhost:5000
2. **Register Account**: Click "Sign up now"
3. **Login**: Use your credentials
4. **Test AI Chat**: Click the chat bubble (bottom right)
5. **Book a Package**: Click "Book Now" on any package
6. **View Profile**: See your bookings and stats

## Sample Data Included

After running `seed-db`, you'll have:

- ✅ 3 Sample Packages (Beginner Bundle, Pro Session, Epic Package)
- ✅ 3 Sample Videos (Backcountry, Park, Beginner runs)
- ✅ 3 Sample Testimonials (5-star reviews)

## Common Issues & Fixes

### "ModuleNotFoundError: No module named 'X'"
```bash
pip install -r requirements.txt
```

### "Could not connect to Redis"
**Option 1**: Install Redis locally:
- Windows: https://github.com/microsoftarchive/redis/releases
- Mac: `brew install redis && brew services start redis`
- Linux: `sudo apt install redis-server`

**Option 2**: Skip chat feature for now (rest of site works fine)

### "Database is locked" (SQLite)
Close any other processes using the database, or:
```bash
rm snowboard_media.db
python app.py init-db
python app.py seed-db
```

### Port 5000 already in use
Change port in `app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=8000)
```

## Getting API Keys

### 1. Claude AI (Required for Chat)
1. Visit: https://console.anthropic.com/
2. Sign up (get $5 free credit!)
3. Go to API Keys
4. Create new key
5. Copy to `.env` as `ANTHROPIC_API_KEY`

### 2. Stripe (Required for Payments)
1. Visit: https://dashboard.stripe.com/register
2. Sign up for free
3. Enable Test Mode (toggle in top right)
4. Go to Developers → API Keys
5. Copy "Secret key" and "Publishable key"
6. Add to `.env`

**Test Card Numbers**:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Any future expiry, any CVC

### 3. Ayrshare (Optional - Social Media)
1. Visit: https://www.ayrshare.com/
2. Sign up (free tier: 1 profile)
3. Get API key from dashboard
4. Add to `.env` as `AYRSHARE_API_KEY`

## Next Steps

### Development
- [ ] Customize homepage content
- [ ] Add your own packages and pricing
- [ ] Upload real video content to Vimeo
- [ ] Customize styling in `app/static/css/style.css`
- [ ] Add more templates (see `app/templates/`)

### Before Production
- [ ] Change `SECRET_KEY` to random string
- [ ] Get production Stripe keys
- [ ] Set up MySQL database
- [ ] Configure email (SMTP)
- [ ] Add domain and SSL certificate
- [ ] Set `FLASK_ENV=production`

### Deployment
See `docs/DEPLOYMENT.md` for full production deployment guide.

## File Structure Quick Reference

```
whiterabbit/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── booking.py
│   │   ├── package.py
│   │   ├── video.py
│   │   └── testimonial.py
│   ├── routes/              # URL routes
│   │   ├── main.py          # Homepage, gallery
│   │   ├── auth.py          # Login, register
│   │   ├── booking.py       # Booking system
│   │   ├── admin.py         # Admin dashboard
│   │   └── chat.py          # AI chat WebSocket
│   ├── services/            # API integrations
│   │   ├── ai_service.py    # Claude AI
│   │   ├── payment_service.py  # Stripe
│   │   ├── social_service.py   # Ayrshare
│   │   └── email_service.py    # Email
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
│       ├── css/style.css
│       ├── js/main.js
│       └── js/chat.js
├── config/
│   └── config.py            # Configuration
├── app.py                   # Main entry point
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## Admin Dashboard

After creating admin account:

1. Login with admin credentials
2. Visit: http://localhost:5000/admin
3. Manage:
   - Bookings
   - Packages
   - Videos
   - Testimonials
   - Users

## Testing the AI Chat

Once you have `ANTHROPIC_API_KEY` set:

1. Click chat bubble (bottom right)
2. Try these prompts:
   - "What packages do you offer?"
   - "I'm a beginner, which package should I choose?"
   - "How much does the Pro Session cost?"
   - "Can you help me book a session?"

The AI knows about your packages and can answer customer questions!

## Useful Commands

```bash
# Create new admin user
python app.py create-admin

# Access Python shell with app context
python app.py shell

# Reset database (WARNING: deletes all data)
rm snowboard_media.db  # or del on Windows
python app.py init-db
python app.py seed-db
```

## Need Help?

1. **Check logs**: Terminal output shows errors
2. **Read error messages**: They usually tell you what's wrong
3. **Common issues**: See "Common Issues & Fixes" above
4. **Documentation**: See `docs/DEPLOYMENT.md` for more details

## What's Next?

You now have a fully functional snowboard media business website with:
- ✅ AI-powered customer service
- ✅ Booking system with payments
- ✅ Video gallery
- ✅ User authentication
- ✅ Admin dashboard
- ✅ Social media integration (with API key)

**Start customizing it to make it yours!**

---

**Ready for production?** See `docs/DEPLOYMENT.md` for deployment to Hostinger VPS.

**Happy coding! 🏂**
