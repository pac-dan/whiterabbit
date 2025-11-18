# Momentum Clips - Professional Snowboard Video Production

> Premium slope footage & editing services platform with AI-powered customer service

A full-featured web platform for booking professional snowboard video sessions in Bansko, Bulgaria. Features interactive booking, video gallery, AI customer support, and automated social media management.

![Flask](https://img.shields.io/badge/Flask-3.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-Proprietary-red)

## Features

- **📅 Interactive Booking System**: Browse packages, select dates/locations, book with Stripe integration
- **🎥 Video Portfolio Gallery**: Showcase work with filtering by location, style, and rider level
- **🤖 AI Customer Service**: 24/7 real-time chat powered by Claude AI (Anthropic)
- **📱 Social Media Automation**: Auto-post to Instagram, TikTok, Facebook, LinkedIn
- **⭐ Testimonials & Reviews**: Customer success stories with ratings
- **🔒 Secure Payments**: Stripe integration with PCI compliance
- **📊 Admin Dashboard**: Complete content & booking management

## Tech Stack

**Backend**
- Flask 3.0, SQLAlchemy ORM, MySQL/SQLite
- Flask-SocketIO + Redis for real-time chat
- Gunicorn WSGI server with Eventlet worker

**APIs & Services**
- **AI**: Anthropic Claude API (Sonnet 4.5)  
- **Voice AI**: Retell AI (voice assistant widget)
- **Payments**: Stripe (optional - can be skipped)
- **Social Media**: Ayrshare API (optional)
- **Video**: YouTube (free hosting)

**Frontend**
- HTML5, CSS3 (Tailwind CSS), JavaScript ES6+
- Socket.IO client, Swiper.js, FullCalendar.js
- Cyberpunk-inspired UI with glass-morphism effects

**Infrastructure**
- Docker + Docker Compose
- Nginx reverse proxy
- Let's Encrypt SSL
- Hostinger VPS ready

## Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0+ (or SQLite for development)
- Redis (for real-time features)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd whiterabbit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
python app.py
```

Visit `http://localhost:5000`

## Documentation

📚 **Complete documentation organized by topic:**

### Getting Started
- [Quick Start Guide](docs/getting-started/quickstart.md) - 5-minute setup
- [Detailed Setup](docs/getting-started/setup.md) - Complete installation guide

### Deployment
- [Hostinger VPS Deployment](docs/deployment/hostinger-vps.md) - Production deployment to Hostinger
- [Platform Deployment Guide](docs/deployment/platforms.md) - Deploy to Render, Railway, Fly.io, Heroku

### Customization
- [Theming & Styling Guide](docs/customization/theming-guide.md) - Customize colors, fonts, and UI

### Development
- [Architecture Overview](docs/development/architecture.md) - Project structure and technical details

## Project Structure

```
whiterabbit/
├── app/
│   ├── models/          # Database models (User, Booking, Package, Video, Testimonial)
│   ├── routes/          # Flask blueprints (main, auth, booking, admin, chat)
│   ├── services/        # Business logic (AI, payments, email, social media)
│   ├── static/          # CSS, JS, images, videos
│   └── templates/       # Jinja2 HTML templates
├── config/              # Configuration classes (Development, Production, Testing)
├── deployment/          # Nginx, supervisor, docker-compose configs
├── docs/                # 📚 Organized documentation
│   ├── getting-started/
│   ├── deployment/
│   ├── customization/
│   └── development/
├── tests/               # Test suite
├── app.py               # Development entry point
├── wsgi.py              # Production WSGI entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── Procfile             # For Render/Railway/Heroku deployment
└── .env.example         # Environment variables template
```

## Required API Keys

Get your API keys before deployment:

1. **Anthropic Claude API** - https://console.anthropic.com/ (for AI chat)
2. **Retell AI** - https://beta.retellai.com/ (for voice assistant)
3. **Stripe** - https://stripe.com/ (optional - for payments)
4. **Ayrshare** - https://www.ayrshare.com/ (optional - for social media automation)
5. **YouTube** - No API key needed! Just upload videos and use video IDs

See [Setup Guide](docs/getting-started/setup.md) for detailed configuration.

## Deployment

### Production-Ready Features

✅ **Security**
- Flask-Talisman (HTTPS enforcement, HSTS, CSP headers)
- Rate limiting on auth & payment routes
- Bcrypt password hashing
- CSRF protection, SQL injection prevention
- Secret validation (refuses to start with placeholder values)

✅ **Production WSGI**
- Gunicorn with Eventlet worker for WebSocket support
- Auto-detected `Procfile` for instant deployment

✅ **Error Handling**
- Custom 404, 403, 500 pages
- No debug info exposed in production
- Comprehensive logging

### Quick Deploy

**Render / Railway / Heroku** - Push to deploy:
```bash
git push origin main
# Platform auto-detects Procfile and deploys
```

**Hostinger VPS** - See [VPS Deployment Guide](docs/deployment/hostinger-vps.md):
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

## Contact Information

**Location**: Bansko, Bulgaria - Premier ski resort destination  
**Phone**: 0873684392  
**Email**: support@momentumclips.com  
**Hours**: Monday - Sunday, 7:00 AM - 5:00 PM EET

## Monthly Operating Costs

- Hostinger VPS KVM 2: $8.49
- YouTube: **FREE** (unlimited video hosting)
- Ayrshare Basic: $10 (optional)
- Claude API: $20-50 (usage-based)
- Retell AI: Variable (usage-based, optional)
- **Total**: ~$40-70/month (or $10-30/month without optional services)

## License

Proprietary - All Rights Reserved

## Support

- **Documentation**: See [docs/](docs/) folder
- **Email**: support@momentumclips.com
- **AI Chat**: Available 24/7 on website

---

**Built with Flask & Claude AI | Powered by Anthropic**

*A production-ready platform demonstrating modern web development and AI integration capabilities.*
