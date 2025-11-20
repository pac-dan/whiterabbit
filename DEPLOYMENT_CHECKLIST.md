# Pre-Deployment Checklist for Momentum Clips

## ✅ Critical Issues Fixed

- [x] Stripe payment page JavaScript error (duplicate variable declaration)
- [x] File upload security validation added
- [x] Stripe keys made optional in production validation
- [x] Flask-Migrate initialized for database migrations
- [x] .dockerignore created
- [x] Rate limiter configured for Redis storage
- [x] Health check endpoint added (`/health`)

## 🔐 Environment Variables (`.env` file)

### Required for Production
- [ ] `SECRET_KEY` - Strong random string (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] `DATABASE_URL` - MySQL connection string: `mysql+pymysql://user:password@host:3306/database`
- [ ] `REDIS_URL` - Redis connection string: `redis://localhost:6379/0`
- [ ] `ANTHROPIC_API_KEY` - From https://console.anthropic.com/
- [ ] `MAIL_USERNAME` - Email for notifications (e.g., Gmail)
- [ ] `MAIL_PASSWORD` - App-specific password
- [ ] `FLASK_ENV=production` - Set to production mode

### Optional (Recommended)
- [ ] `STRIPE_SECRET_KEY` - From https://dashboard.stripe.com/ (for payments)
- [ ] `STRIPE_PUBLISHABLE_KEY` - Stripe public key
- [ ] `AYRSHARE_API_KEY` - From https://www.ayrshare.com/ (social media automation)
- [ ] `RETELL_API_KEY` - From https://beta.retellai.com/ (voice assistant)
- [ ] `RETELL_AGENT_ID` - Retell AI agent ID
- [ ] `RETELL_PUBLIC_KEY` - Retell AI public key

### Environment Configuration
- [ ] `CORS_ORIGINS` - Production domains (e.g., `https://momentumclips.com,https://www.momentumclips.com`)
- [ ] `ADMIN_EMAIL` - Admin contact email
- [ ] `SUPPORT_EMAIL` - Customer support email

## 🗄️ Database Setup

- [ ] MySQL 8.0+ installed on VPS
- [ ] Database created with utf8mb4 character set
- [ ] Database user created with appropriate permissions
- [ ] `DATABASE_URL` updated in `.env`
- [ ] Run migrations: `flask db upgrade` (if needed)
- [ ] Seed database: `python app.py seed-db` or `python reset_and_seed.py`
- [ ] Create admin user: `flask create-admin`

## 🐳 Docker Configuration

- [ ] Review `Dockerfile` - CMD uses correct entry point (`wsgi:app`)
- [ ] Review `docker-compose.yml` - Verify all environment variables
- [ ] Update `docker-compose.yml` with production passwords
- [ ] SSL certificates ready in `deployment/ssl/` directory
- [ ] Test Docker build locally: `docker-compose build`

## 🔒 Security Checklist

- [ ] All placeholder values removed from `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] HTTPS/SSL certificates obtained (Let's Encrypt recommended)
- [ ] Nginx HTTPS configuration enabled in `deployment/nginx.conf` (lines 83-137)
- [ ] CORS origins set to production domains only
- [ ] File upload limits configured (`MAX_CONTENT_LENGTH`)
- [ ] Rate limiting configured with Redis (not memory)
- [ ] CSRF protection enabled
- [ ] Flask-Talisman security headers active in production

## 🌐 DNS & Domain Setup

- [ ] Domain pointed to VPS IP address
- [ ] A record configured
- [ ] WWW subdomain configured (if desired)
- [ ] DNS propagation complete (24-48 hours)

## 📦 VPS Setup (Hostinger)

- [ ] SSH access configured
- [ ] Docker and Docker Compose installed
- [ ] Git repository cloned to VPS
- [ ] `.env` file created on VPS with production values
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] Redis running in Docker
- [ ] MySQL running in Docker

## 🚀 Deployment Steps

1. **Build and Start Containers**
   ```bash
   cd /path/to/whiterabbit
   docker-compose build
   docker-compose up -d
   ```

2. **Verify Services Running**
   ```bash
   docker-compose ps
   # All services should show "Up"
   ```

3. **Check Logs**
   ```bash
   docker-compose logs -f web
   # Look for: [OK] All required production secrets validated successfully
   ```

4. **Test Health Endpoint**
   ```bash
   curl http://localhost:5000/health
   # Should return: {"status":"healthy","database":"healthy","version":"1.0.0"}
   ```

5. **Initialize Database (if needed)**
   ```bash
   docker exec -it snowboard_media_web flask db upgrade
   docker exec -it snowboard_media_web python app.py seed-db
   docker exec -it snowboard_media_web flask create-admin
   ```

## 🔍 Post-Deployment Testing

- [ ] Homepage loads correctly: `https://your-domain.com`
- [ ] Health check responds: `https://your-domain.com/health`
- [ ] HTTPS redirects working
- [ ] Admin dashboard accessible: `https://your-domain.com/admin`
- [ ] Login/Register working
- [ ] Booking flow functional
- [ ] Payment processing working (if Stripe configured)
- [ ] Gallery videos load
- [ ] Contact form sends emails
- [ ] AI chat widget appears (if Retell configured)
- [ ] Mobile responsive design working

## 📊 Monitoring Setup

- [ ] Health check endpoint monitoring configured
- [ ] Server resource monitoring: `htop`, `docker stats`
- [ ] Log rotation configured
- [ ] Backup strategy in place:
  - Database: `docker exec snowboard_media_db mysqldump -u user -p database > backup.sql`
  - Uploads: `tar -czf uploads-backup.tar.gz app/static/uploads/`

## ⚠️ Known Warnings (Non-Blocking)

These are expected in development/initial setup:

- "Rate limiter using memory storage" - Resolved once Redis is running
- "Redis not available" - Normal if Redis not started yet
- "cdn.tailwindcss.com should not be used in production" - Consider self-hosting Tailwind CSS in future

## 🐛 Troubleshooting

### Application Won't Start
```bash
docker-compose logs web
# Check for missing environment variables or invalid secrets
```

### Database Connection Errors
```bash
docker-compose logs db
# Verify MySQL is running and DATABASE_URL is correct
```

### Redis Connection Errors
```bash
docker-compose logs redis
# Verify Redis is running
```

### SSL Certificate Issues
```bash
# Generate Let's Encrypt certificates
certbot certonly --standalone -d your-domain.com -d www.your-domain.com
# Copy to deployment/ssl/
```

## 📝 Rollback Procedure

If deployment fails:

1. **Stop containers**: `docker-compose down`
2. **Restore database backup**: `docker exec -i snowboard_media_db mysql -u user -p database < backup.sql`
3. **Revert code**: `git checkout previous-stable-commit`
4. **Rebuild**: `docker-compose build`
5. **Start**: `docker-compose up -d`

## ✅ Final Verification

- [ ] All checklist items completed
- [ ] No critical errors in logs
- [ ] Website accessible via HTTPS
- [ ] All core features functional
- [ ] Admin can log in
- [ ] Backup strategy documented
- [ ] Team notified of deployment

## 📞 Support Contacts

- **Email**: support@momentumclips.com
- **Phone**: 0873684392
- **Location**: Bansko, Bulgaria

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Git Commit**: _______________  
**Notes**: _______________

