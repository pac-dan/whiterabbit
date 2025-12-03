# 📋 Production Deployment - Quick Checklist

## ✅ Pre-Deployment Verification

### Code & Configuration
- [x] **requirements.txt** exists with pinned versions
- [x] **Procfile** configured for gunicorn
- [x] **.gitignore** includes .env, __pycache__/, *.pyc, instance/, venv/
- [x] **.env.example** lists all required variables
- [x] **app.run()** only in `if __name__ == '__main__'` blocks
- [x] **app variable** exported in wsgi.py
- [x] **DEBUG=False** in production config

### Security
- [x] No hardcoded secrets in code
- [x] All API keys from environment variables
- [x] SECRET_KEY from environment (not hardcoded)
- [x] DATABASE_URL from environment
- [x] Production secret validation enabled
- [x] CSRF protection enabled
- [x] HTTPS enforcement (Flask-Talisman)
- [x] Rate limiting configured
- [x] Secure password hashing (Bcrypt)

### File Handling
- [x] Static files properly configured
- [x] File paths use os.path.join()
- [x] No absolute paths in code
- [x] Directory traversal protection
- [x] Upload folder configurable

### Database
- [x] Database URI from environment
- [x] Connection pooling configured
- [x] Migrations set up (Flask-Migrate)
- [x] Supports PostgreSQL/MySQL/SQLite

### Error Handling
- [x] Custom error pages (404, 403, 500)
- [x] No debug info in production errors
- [x] No debug=True in routes
- [x] Proper logging configured

### Documentation
- [x] README.md with setup instructions
- [x] Environment variables documented
- [x] Deployment guide available
- [x] API keys documented

---

## 🚀 Render Deployment Steps

### 1. Prepare Repository
```bash
git add .
git commit -m "Production ready"
git push origin main
```

### 2. Create Render Services

#### Web Service
1. New + → Web Service
2. Connect repository
3. Settings:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** (auto-detected from Procfile)

#### PostgreSQL Database
1. New + → PostgreSQL
2. Name: `your-app-db`
3. Copy Internal Database URL

#### Redis Instance
1. New + → Redis
2. Name: `your-app-redis`
3. Copy Internal Redis URL

### 3. Add Environment Variables

**Required (Minimum):**
```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=<from-postgresql-service>
REDIS_URL=<from-redis-service>
ANTHROPIC_API_KEY=<your-api-key>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<your-email@gmail.com>
MAIL_PASSWORD=<gmail-app-password>
```

**Optional (Full Features):**
```env
RETELL_API_KEY=<your-retell-key>
RETELL_AGENT_ID=<your-agent-id>
RETELL_PUBLIC_KEY=<your-public-key>
STRIPE_SECRET_KEY=<your-stripe-key>
STRIPE_PUBLISHABLE_KEY=<your-publishable-key>
AYRSHARE_API_KEY=<your-ayrshare-key>
```

### 4. Deploy
Click "Create Web Service" and wait ~3-5 minutes

### 5. Initialize Database
Use Render Shell or SSH:
```bash
flask db upgrade
flask create-admin
flask seed-db  # Optional
```

---

## ✅ Post-Deployment Tests

### Functionality Checks
- [ ] App loads without errors at `https://your-app.onrender.com`
- [ ] Homepage displays correctly
- [ ] Static files load (CSS, JS, images)
- [ ] User registration works
- [ ] User login works
- [ ] Admin login works
- [ ] Booking system works
- [ ] Email notifications sent
- [ ] File uploads work
- [ ] Database queries work

### Security Checks
- [ ] HTTPS is enforced (http:// redirects to https://)
- [ ] No debug info in error pages
- [ ] CSRF protection working
- [ ] Rate limiting active
- [ ] Admin routes protected

### Integration Checks
- [ ] AI chat works (if Anthropic API key set)
- [ ] Voice widget loads (if Retell keys set)
- [ ] Stripe checkout works (if Stripe keys set)
- [ ] Social media posting works (if Ayrshare key set)

### Performance Checks
- [ ] Page load time < 3 seconds
- [ ] Database queries optimized
- [ ] Redis connection working
- [ ] SocketIO working (real-time features)

---

## 🐛 Common Issues & Solutions

### Issue: "PRODUCTION SECURITY ERROR"
**Cause:** Missing or placeholder environment variables  
**Solution:** Add all required env vars in Render dashboard

### Issue: 500 Internal Server Error
**Cause:** Database not connected or migrations not run  
**Solution:** Check DATABASE_URL and run `flask db upgrade`

### Issue: Static files not loading
**Cause:** Incorrect static folder path  
**Solution:** Verify `app/static/` exists and contains files

### Issue: Redis connection failed
**Cause:** REDIS_URL not set or incorrect  
**Solution:** Add Redis service and set REDIS_URL

### Issue: Email not sending
**Cause:** Gmail app password not configured  
**Solution:** Generate app password at https://myaccount.google.com/apppasswords

---

## 📊 Environment Variables Reference

### Core Application
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | ✅ | `production` | Environment mode |
| `SECRET_KEY` | ✅ | `<random-64-chars>` | Flask secret key |
| `DATABASE_URL` | ✅ | `postgresql://...` | Database connection |
| `REDIS_URL` | ✅ | `redis://...` | Redis connection |

### Email Configuration
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `MAIL_SERVER` | ✅ | `smtp.gmail.com` | SMTP server |
| `MAIL_PORT` | ✅ | `587` | SMTP port |
| `MAIL_USE_TLS` | ✅ | `True` | Use TLS |
| `MAIL_USERNAME` | ✅ | `your@gmail.com` | Email address |
| `MAIL_PASSWORD` | ✅ | `<app-password>` | Gmail app password |

### AI Services
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | `sk-ant-...` | Claude AI API key |
| `RETELL_API_KEY` | ❌ | `key_...` | Retell voice AI (optional) |
| `RETELL_AGENT_ID` | ❌ | `agent_...` | Retell agent ID (optional) |
| `RETELL_PUBLIC_KEY` | ❌ | `...` | Retell public key (optional) |

### Payment & Social
| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | ❌ | `sk_live_...` | Stripe payments (optional) |
| `STRIPE_PUBLISHABLE_KEY` | ❌ | `pk_live_...` | Stripe public key (optional) |
| `AYRSHARE_API_KEY` | ❌ | `...` | Social media posting (optional) |

---

## 🔗 Quick Links

- **Render Dashboard:** https://dashboard.render.com/
- **Anthropic API Keys:** https://console.anthropic.com/
- **Stripe Dashboard:** https://dashboard.stripe.com/
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Retell AI:** https://beta.retellai.com/

---

## 📈 Monitoring & Maintenance

### Daily
- [ ] Check Render logs for errors
- [ ] Monitor error rate
- [ ] Check uptime status

### Weekly
- [ ] Review security logs
- [ ] Check database size
- [ ] Monitor API usage costs
- [ ] Review user feedback

### Monthly
- [ ] Update dependencies (`pip-review --auto`)
- [ ] Review and rotate secrets
- [ ] Backup database
- [ ] Check SSL certificate expiry

---

## 💰 Cost Breakdown

### Render Services (Monthly)
- Web Service (Starter): $7
- PostgreSQL (Starter): $7
- Redis (Starter): $7
- **Subtotal: $21/month**

### API Services (Monthly)
- Anthropic Claude: $20-50 (usage-based)
- Stripe: Free (2.9% + $0.30 per transaction)
- Retell AI: Variable (usage-based, optional)
- Ayrshare: $10 (optional)

### Total: $41-91/month
*(Minimum $28/month without optional services)*

---

## ✅ You're Ready to Deploy!

All security, configuration, and best practices are implemented.  
Your app is production-ready for Render, Railway, Fly.io, or any platform.

**Deploy with confidence! 🚀**


