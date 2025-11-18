# SnowboardMedia Deployment Guide

Complete guide for deploying SnowboardMedia to Hostinger VPS or any Linux server.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Hostinger VPS Setup](#hostinger-vps-setup)
4. [Docker Deployment](#docker-deployment)
5. [SSL Configuration](#ssl-configuration)
6. [Environment Variables](#environment-variables)
7. [Database Setup](#database-setup)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Local Development
- Python 3.11+
- MySQL 8.0+ or SQLite (for development)
- Redis 7+
- Git

### Production (Hostinger VPS)
- Hostinger VPS KVM 2 or higher
- Ubuntu 22.04 LTS
- Root or sudo access
- Domain name (optional but recommended)

### API Keys Required
- Anthropic Claude API key
- Stripe API keys (secret & publishable)
- Ayrshare API key
- Vimeo access token (optional)

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd whiterabbit
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Use SQLite for local development
DATABASE_URL=sqlite:///snowboard_media.db

# API Keys
ANTHROPIC_API_KEY=your-claude-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
AYRSHARE_API_KEY=your-ayrshare-api-key

# Redis (install locally or use Docker)
REDIS_URL=redis://localhost:6379/0
```

### 5. Initialize Database
```bash
python app.py init-db
python app.py seed-db
python app.py create-admin
```

### 6. Run Development Server
```bash
python app.py
```

Visit `http://localhost:5000`

---

## Hostinger VPS Setup

### 1. Order VPS
1. Go to Hostinger and order **VPS KVM 2** ($8.49/month)
2. Choose Ubuntu 22.04 LTS
3. Set root password
4. Wait for provisioning (5-10 minutes)

### 2. Connect to VPS
```bash
ssh root@your-vps-ip
```

### 3. Update System
```bash
apt update && apt upgrade -y
```

### 4. Install Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 5. Install Git
```bash
apt install git -y
```

### 6. Clone Your Repository
```bash
cd /var/www
git clone <your-repo-url> snowboard
cd snowboard
```

---

## Docker Deployment

### 1. Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Update with production values:
```env
FLASK_ENV=production
SECRET_KEY=generate-strong-random-key-here
DATABASE_URL=mysql+pymysql://snowboard_user:${DB_PASSWORD}@db:3306/snowboard_media
REDIS_URL=redis://redis:6379/0

# Set strong passwords
DB_ROOT_PASSWORD=strong-root-password-here
DB_PASSWORD=strong-db-password-here

# Your API keys
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
AYRSHARE_API_KEY=...
```

### 2. Build and Start Containers
```bash
docker-compose up -d --build
```

### 3. Initialize Database
```bash
# Access Flask container
docker exec -it snowboard_media_web bash

# Inside container
python app.py init-db
python app.py seed-db
python app.py create-admin

# Exit container
exit
```

### 4. Check Status
```bash
docker-compose ps
docker-compose logs -f web
```

Your site should now be accessible at `http://your-vps-ip`

---

## SSL Configuration

### 1. Point Domain to VPS
In your domain registrar, add an A record:
```
@ (or yourdomain.com)  →  your-vps-ip
www                     →  your-vps-ip
```

### 2. Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### 3. Obtain SSL Certificate
```bash
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

### 4. Copy Certificates
```bash
mkdir -p deployment/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/ssl/
```

### 5. Update Nginx Configuration
Edit `deployment/nginx.conf` and uncomment the HTTPS server block.

Update `server_name`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

### 6. Restart Nginx
```bash
docker-compose restart nginx
```

### 7. Auto-Renew Certificates
```bash
# Test renewal
certbot renew --dry-run

# Add cron job
crontab -e

# Add this line:
0 0 * * * certbot renew --quiet --post-hook "docker-compose -f /var/www/snowboard/docker-compose.yml restart nginx"
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `production` |
| `SECRET_KEY` | Flask secret key | Random 32+ characters |
| `DATABASE_URL` | Database connection string | `mysql+pymysql://user:pass@host/db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ANTHROPIC_API_KEY` | Claude AI API key | `sk-ant-api03-...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` or `sk_test_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_live_...` or `pk_test_...` |
| `AYRSHARE_API_KEY` | Ayrshare API key | Your Ayrshare key |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MAIL_SERVER` | Email SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | SMTP username | - |
| `MAIL_PASSWORD` | SMTP password | - |
| `VIMEO_ACCESS_TOKEN` | Vimeo API token | - |

---

## Database Setup

### Development (SQLite)
No setup needed - SQLite creates the database automatically.

### Production (MySQL)
Docker Compose handles MySQL setup automatically. To access:

```bash
# Enter MySQL container
docker exec -it snowboard_media_db mysql -u snowboard_user -p

# Enter password when prompted
# Run SQL commands
USE snowboard_media;
SHOW TABLES;
```

### Backup Database
```bash
# Backup
docker exec snowboard_media_db mysqldump -u snowboard_user -p snowboard_media > backup.sql

# Restore
docker exec -i snowboard_media_db mysql -u snowboard_user -p snowboard_media < backup.sql
```

---

## Useful Commands

### Docker Management
```bash
# View logs
docker-compose logs -f web
docker-compose logs -f db

# Restart services
docker-compose restart web
docker-compose restart nginx

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (DANGEROUS)
docker-compose down -v
```

### Application Management
```bash
# Access Flask shell
docker exec -it snowboard_media_web python app.py shell

# Create admin user
docker exec -it snowboard_media_web python app.py create-admin

# Run database migrations
docker exec -it snowboard_media_web python app.py db upgrade
```

---

## Monitoring

### Check Application Health
```bash
curl http://localhost:5000
curl http://your-domain.com
```

### Monitor Logs
```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Resource Usage
```bash
docker stats
htop
df -h
```

---

## Troubleshooting

### Application Won't Start
```bash
# Check logs
docker-compose logs web

# Common issues:
# - Missing .env file
# - Invalid API keys
# - Database connection failed
```

### Database Connection Failed
```bash
# Check MySQL is running
docker-compose ps

# Check credentials in .env
cat .env | grep DATABASE_URL

# Test connection
docker exec -it snowboard_media_web python -c "from app import db; print(db)"
```

### Socket.IO Chat Not Working
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker exec -it snowboard_media_redis redis-cli ping
# Should return: PONG
```

### SSL Certificate Issues
```bash
# Check certificate expiry
certbot certificates

# Renew manually
certbot renew

# Check Nginx config
docker exec -it snowboard_media_nginx nginx -t
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

---

## Performance Optimization

### Enable Caching
Add to `config.py`:
```python
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.getenv('REDIS_URL')
```

### Optimize Images
```bash
# Install image optimization tools
apt install optipng jpegoptim -y

# Optimize images
find app/static/images -name "*.png" -exec optipng {} \;
find app/static/images -name "*.jpg" -exec jpegoptim {} \;
```

### Database Indexing
Indexes are already created in models, but verify:
```sql
SHOW INDEX FROM bookings;
SHOW INDEX FROM videos;
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set FLASK_ENV=production
- [ ] Configure firewall (UFW)
- [ ] Enable fail2ban for SSH protection
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use Stripe production keys only in production

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check Flask/Docker documentation
4. Contact support at support@snowboardmedia.com

---

**Last Updated**: January 2025
**Version**: 1.0.0
