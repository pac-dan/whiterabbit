# Deploy Momentum Clips to Hostinger

Complete step-by-step guide to deploy your Flask app to Hostinger with momentumclips.com domain.

## Prerequisites

- Hostinger account with momentumclips.com domain
- Hostinger VPS (recommended: VPS KVM 2 - $8.49/month) OR Premium/Business hosting
- SSH access to your hosting

## Deployment Options

### Option A: Hostinger VPS (BEST for Performance & SEO)

Perfect for full control, best performance, and enterprise features.

---

## VPS Deployment Steps

### 1. Access Your VPS via SSH

From Hostinger panel:
- Go to "VPS" → Select your VPS
- Click "SSH Access" to get credentials
- Use PowerShell or PuTTY to connect:

```bash
ssh root@your-vps-ip
```

### 2. Initial Server Setup

```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server git

# Install certbot for SSL
apt install -y certbot python3-certbot-nginx
```

### 3. Create Application User

```bash
# Create dedicated user for app
adduser momentum
usermod -aG sudo momentum

# Switch to app user
su - momentum
```

### 4. Clone Your Repository

```bash
# If using Git
git clone https://github.com/yourusername/whiterabbit.git
cd whiterabbit

# OR upload files via SFTP to /home/momentum/whiterabbit
```

### 5. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Configure Environment Variables

```bash
# Create production .env file
cp .env.example .env
nano .env
```

Edit with your REAL values:
```env
FLASK_ENV=production
SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=mysql+pymysql://momentum_user:password@localhost:3306/momentum_db
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=<your-real-stripe-key>
STRIPE_PUBLISHABLE_KEY=<your-real-stripe-pub-key>
ANTHROPIC_API_KEY=<your-real-claude-key>
AYRSHARE_API_KEY=<your-real-ayrshare-key>
VIMEO_ACCESS_TOKEN=<your-real-vimeo-token>
MAIL_USERNAME=support@momentumclips.com
MAIL_PASSWORD=<your-email-password>
APP_NAME=Momentum Clips
ADMIN_EMAIL=admin@momentumclips.com
SUPPORT_EMAIL=support@momentumclips.com
CORS_ORIGINS=https://momentumclips.com,https://www.momentumclips.com
```

### 7. Set Up MySQL Database

```bash
# Login to MySQL
sudo mysql

# In MySQL prompt:
CREATE DATABASE momentum_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'momentum_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON momentum_db.* TO 'momentum_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Update your `.env` with the database credentials you just created.

### 8. Initialize Database

```bash
# Activate venv if not already
source venv/bin/activate

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
flask create-admin
```

### 9. Test Application Locally

```bash
# Test in production mode
export FLASK_ENV=production
python wsgi.py

# Should see: [OK] All production secrets validated successfully
# Press Ctrl+C to stop
```

### 10. Set Up Gunicorn as Service

```bash
sudo nano /etc/systemd/system/momentum-clips.service
```

Add this content:
```ini
[Unit]
Description=Momentum Clips Flask Application
After=network.target

[Service]
User=momentum
Group=www-data
WorkingDirectory=/home/momentum/whiterabbit
Environment="PATH=/home/momentum/whiterabbit/venv/bin"
ExecStart=/home/momentum/whiterabbit/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable momentum-clips
sudo systemctl start momentum-clips
sudo systemctl status momentum-clips
```

### 11. Configure Nginx

```bash
# Copy your nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/momentum-clips

# Update the config for production
sudo nano /etc/nginx/sites-available/momentum-clips
```

Change these lines:
```nginx
upstream flask_app {
    server 127.0.0.1:5000;  # Change from web:5000
}

server {
    listen 80;
    server_name momentumclips.com www.momentumclips.com;  # Your domain
    
    # ... rest of config
}
```

Enable the site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/momentum-clips /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 12. Point Domain to VPS

In Hostinger domain panel:
1. Go to "Domain" → "DNS/Nameservers"
2. Add/Edit A records:
   - Type: `A`, Name: `@`, Points to: `your-vps-ip`, TTL: `14400`
   - Type: `A`, Name: `www`, Points to: `your-vps-ip`, TTL: `14400`
3. Save and wait 15-30 minutes for DNS propagation

### 13. Install SSL Certificate (CRITICAL for SEO!)

```bash
# Install Let's Encrypt SSL
sudo certbot --nginx -d momentumclips.com -d www.momentumclips.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)

# Test automatic renewal
sudo certbot renew --dry-run
```

### 14. Verify Deployment

Visit: `https://momentumclips.com`

Check:
- Site loads over HTTPS
- No certificate errors
- Security headers present:
  ```bash
  curl -I https://momentumclips.com
  ```
- Sitemap accessible: `https://momentumclips.com/sitemap.xml`
- Robots.txt works: `https://momentumclips.com/robots.txt`

---

## Option B: Hostinger Premium/Business Hosting (Simpler but Limited)

If you have shared hosting instead of VPS:

### 1. Enable Python in hPanel
- Go to "Advanced" → "Select PHP Version"
- Change to Python (if available)

### 2. Upload Files via File Manager
- Upload your entire project to `public_html/`

### 3. Use .htaccess for Routing
Create `public_html/.htaccess`:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]
```

**Note**: Shared hosting has limitations. VPS is strongly recommended for this application.

---

## Post-Deployment Tasks

### 1. Submit to Google Search Console
1. Go to [Google Search Console](https://search.google.com/search-console)
2. Add property: `https://momentumclips.com`
3. Verify ownership
4. Submit sitemap: `https://momentumclips.com/sitemap.xml`

### 2. Set Up Email
Configure email@momentumclips.com in Hostinger:
- Go to "Email" → "Email Accounts"
- Create: `support@momentumclips.com`
- Create: `admin@momentumclips.com`
- Use these credentials in your `.env` file

### 3. Monitor Application
```bash
# View logs
sudo journalctl -u momentum-clips -f

# View nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 4. Set Up Backups
```bash
# Create backup script
nano ~/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u momentum_user -p momentum_db > ~/backups/db_$DATE.sql
tar -czf ~/backups/app_$DATE.tar.gz /home/momentum/whiterabbit
```

### 5. Performance Optimization
- Enable Redis for session storage (already configured)
- Set up CloudFlare for CDN (optional)
- Monitor with Google Analytics

---

## Updating Your App

When you make code changes:

```bash
# SSH to server
ssh momentum@your-vps-ip

# Go to app directory
cd whiterabbit

# Pull latest changes
git pull

# Activate venv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Run migrations if needed
flask db migrate
flask db upgrade

# Restart service
sudo systemctl restart momentum-clips
```

---

## Troubleshooting

### App won't start
```bash
# Check logs
sudo journalctl -u momentum-clips -xe

# Common issues:
# 1. Missing environment variables
# 2. Database connection issues
# 3. Port already in use
```

### 502 Bad Gateway
```bash
# Check if gunicorn is running
sudo systemctl status momentum-clips

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Database connection errors
```bash
# Test MySQL connection
mysql -u momentum_user -p momentum_db

# Check .env DATABASE_URL format
```

---

## Security Checklist

- [x] HTTPS enabled (Let's Encrypt)
- [x] Firewall configured (UFW)
- [x] Database user with limited privileges
- [x] .env file with proper permissions (chmod 600)
- [x] Regular backups scheduled
- [x] SSH key authentication (disable password login)
- [x] Fail2ban installed (optional but recommended)

---

## Cost Summary

**Monthly Costs:**
- Hostinger VPS KVM 2: $8.49/month
- Domain (momentumclips.com): Already owned
- SSL Certificate: FREE (Let's Encrypt)
- **Total: ~$8.49/month**

Plus API costs:
- Vimeo Pro: $20/month
- Ayrshare: $10/month
- Claude API: ~$20-50/month (usage-based)

**Grand Total: ~$60-90/month**

---

## Need Help?

Check these resources:
- Hostinger Knowledge Base: https://support.hostinger.com
- Flask Documentation: https://flask.palletsprojects.com
- Nginx Documentation: https://nginx.org/en/docs/

Your app is now production-ready and SEO-optimized!

