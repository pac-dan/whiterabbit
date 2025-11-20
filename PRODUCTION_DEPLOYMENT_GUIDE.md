# 🚀 Production Deployment Guide - Momentum Clips

**Status**: ✅ Code is deployment-ready  
**Estimated Time**: 2-3 hours  
**Last Updated**: November 20, 2025

---

## 🎉 What's Been Fixed

### ✅ Booking System - COMPLETE
- **CSRF Protection**: Added to booking form
- **Date Validation**: Frontend validates 24-hour minimum advance booking
- **Stripe Webhook**: Handles automatic payment confirmations
- **Refund Logic**: Full refund processing for cancellations
- **Database**: Seeded with 3 packages, 6 videos, 3 testimonials

### ✅ Admin Access - READY
```
Email: admin@momentumclips.com
Password: Admin123!
```

---

## 📋 Pre-Deployment Checklist (Do These Now)

### Step 1: Generate Production Secrets (5 minutes)

```bash
# 1. Generate a strong SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and save it for .env file

# 2. Generate database passwords
python -c "import secrets; print('DB_ROOT_PASSWORD:', secrets.token_urlsafe(32))"
python -c "import secrets; print('DB_PASSWORD:', secrets.token_urlsafe(32))"
```

### Step 2: Configure Production .env (10 minutes)

Copy `.env.production.template` to your server as `.env` and fill in:

#### CRITICAL (Must Have):
- `SECRET_KEY` - Use generated value from Step 1
- `DATABASE_URL` - MySQL connection string
- `REDIS_URL` - Usually `redis://localhost:6379/0`
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
- `MAIL_USERNAME` & `MAIL_PASSWORD` - Gmail app password

#### IMPORTANT (Recommended):
- `STRIPE_SECRET_KEY` - For payments
- `STRIPE_PUBLISHABLE_KEY` - For payments
- `STRIPE_WEBHOOK_SECRET` - After creating webhook

#### OPTIONAL (Can Skip Initially):
- `RETELL_API_KEY` - Voice assistant
- `AYRSHARE_API_KEY` - Social media posting

### Step 3: Domain & DNS (30 minutes - allow 24-48 hours for propagation)

1. **Point your domain to your VPS IP:**
   ```
   A Record: @ → YOUR_VPS_IP
   A Record: www → YOUR_VPS_IP
   ```

2. **Wait for DNS propagation** (test with `ping yourdomain.com`)

### Step 4: SSL Certificates (15 minutes)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy to deployment folder
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/ssl/
```

### Step 5: Update Nginx Configuration (5 minutes)

Edit `deployment/nginx.conf`:
- Uncomment lines 83-137 (HTTPS configuration)
- Replace `yourdomain.com` with your actual domain

---

## 🐳 Docker Deployment (Recommended)

### On Your VPS:

```bash
# 1. Clone repository
git clone https://github.com/pac-dan/whiterabbit.git
cd whiterabbit

# 2. Create .env file with production values
nano .env
# (Paste your production configuration)

# 3. Update docker-compose.yml passwords
nano docker-compose.yml
# Update DB_PASSWORD and DB_ROOT_PASSWORD to match your .env

# 4. Build and start services
docker-compose build
docker-compose up -d

# 5. Check all services are running
docker-compose ps
# Should see: web, db, redis, nginx all "Up"

# 6. Initialize database (IMPORTANT!)
docker exec -it snowboard_media_web flask db upgrade

# 7. Create admin user
docker exec -it snowboard_media_web python quick_admin.py

# 8. Check logs
docker-compose logs -f web
```

### Verify Deployment:

```bash
# Test health endpoint
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","services":{"database":"ok","redis":"ok"},"version":"1.0.0"}
```

---

## 🌐 Manual VPS Deployment (Alternative)

If not using Docker:

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server git

# 2. Clone and setup
git clone https://github.com/pac-dan/whiterabbit.git
cd whiterabbit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure MySQL
sudo mysql
CREATE DATABASE snowboard_media CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'snowboard_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON snowboard_media.* TO 'snowboard_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 4. Setup .env file
cp .env.production.template .env
nano .env  # Fill in your values

# 5. Initialize database
flask db upgrade
python reset_and_seed.py
python quick_admin.py

# 6. Install and configure Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app

# 7. Setup Nginx reverse proxy
sudo cp deployment/nginx.conf /etc/nginx/sites-available/momentumclips
sudo ln -s /etc/nginx/sites-available/momentumclips /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Stripe Webhook Configuration

**AFTER deployment**, configure Stripe webhook:

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter URL: `https://yourdomain.com/booking/webhook/stripe`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy the webhook secret
6. Add to `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_XXXXX
   ```
7. Restart application

---

## ✅ Post-Deployment Testing

Test these endpoints after deployment:

```bash
# 1. Health Check
curl https://yourdomain.com/health

# 2. Homepage
curl https://yourdomain.com

# 3. Login page
curl https://yourdomain.com/login

# 4. Admin dashboard (after login)
https://yourdomain.com/admin

# 5. Booking page (after login)
https://yourdomain.com/booking/new
```

### Manual Testing Checklist:
- [ ] User registration works
- [ ] User login works
- [ ] Homepage loads with packages
- [ ] Gallery displays videos
- [ ] Booking form shows packages
- [ ] Date picker enforces 24-hour minimum
- [ ] Payment page loads (if Stripe configured)
- [ ] Admin dashboard accessible
- [ ] Contact form sends emails
- [ ] Mobile responsive design works

---

## 📊 Monitoring & Maintenance

### Check Logs:
```bash
# Docker
docker-compose logs -f web
docker-compose logs -f nginx

# Manual
tail -f /var/log/nginx/error.log
journalctl -u gunicorn -f
```

### Database Backup:
```bash
# Docker
docker exec snowboard_media_db mysqldump -u root -p snowboard_media > backup_$(date +%Y%m%d).sql

# Manual
mysqldump -u snowboard_user -p snowboard_media > backup_$(date +%Y%m%d).sql
```

### Update Application:
```bash
cd /path/to/whiterabbit
git pull origin main
docker-compose build
docker-compose up -d
```

---

## 🆘 Troubleshooting

### Application won't start:
```bash
docker-compose logs web
# Check for missing environment variables or invalid API keys
```

### Database connection errors:
```bash
docker-compose logs db
# Verify DATABASE_URL matches db service name and password
```

### Stripe payments not working:
- Verify STRIPE_SECRET_KEY starts with `sk_live_` (production) or `sk_test_` (testing)
- Check webhook is configured and receiving events
- View Stripe Dashboard > Developers > Logs

### SSL certificate errors:
```bash
sudo certbot renew --dry-run
# Test certificate renewal
```

---

## 📞 Support Resources

- **Documentation**: `/docs` folder in repository
- **Email**: support@momentumclips.com
- **Phone**: 0873684392
- **Location**: Bansko, Bulgaria

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ All services show "Up" in `docker-compose ps`  
✅ Health endpoint returns `{"status":"healthy"}`  
✅ You can login at https://yourdomain.com/login  
✅ Booking form displays packages  
✅ Admin dashboard accessible  
✅ HTTPS redirect works (HTTP → HTTPS)  
✅ No critical errors in logs

---

## 🚨 Important Security Notes

1. **Change default admin password** immediately after first login
2. **Never commit .env file** to version control
3. **Enable firewall**: Only ports 80, 443, 22 should be open
4. **Setup automatic backups** (daily recommended)
5. **Monitor error logs** for first week after launch
6. **Keep dependencies updated**: Run `pip list --outdated` monthly

---

**You're ready to deploy! 🎉**

If you encounter any issues, refer to:
- `DEPLOYMENT_CHECKLIST.md` - Detailed checklist
- `TROUBLESHOOTING.md` - Common issues
- `deployment/SSL_SETUP.md` - SSL configuration

**Good luck with your launch!** 🚀

