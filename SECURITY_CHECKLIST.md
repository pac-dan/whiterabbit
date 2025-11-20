# Production Security Checklist
**For:** Momentum Clips Deployment
**Last Updated:** 2025-11-20

---

## Pre-Deployment Security Verification

Complete this checklist before deploying to production. Each item must be checked ✅ before launch.

---

## 1. Environment & Configuration

### 1.1 Secret Management
- [ ] All secrets moved to environment variables (no hardcoded values)
- [ ] `.env` file NOT committed to git
- [ ] `.gitignore` includes `.env`, `*.db`, `instance/`
- [ ] Production secrets use strong random values (not defaults)
- [ ] `SECRET_KEY` is cryptographically random (32+ bytes)
- [ ] Database password is strong (16+ characters, mixed case, numbers, symbols)
- [ ] Stripe keys are production keys (sk_live_, pk_live_)
- [ ] SMTP credentials secured

**Verification Command:**
```bash
# Check for hardcoded secrets
grep -r "sk_test_\|sk_live_\|password.*=.*['\"]" app/ --exclude-dir=__pycache__
# Should return no results
```

### 1.2 Configuration Validation
- [ ] `FLASK_ENV=production` set
- [ ] `DEBUG=False` in production
- [ ] `config/config.py` validation function working
- [ ] `validate_production_secrets()` prevents launch with placeholders
- [ ] All required environment variables documented

**Test:**
```bash
# Try launching with placeholder secrets - should fail
FLASK_ENV=production SECRET_KEY=dev-secret-key python app.py
# Expected: ValueError with validation error
```

---

## 2. HTTPS & Transport Security

### 2.1 SSL/TLS Configuration
- [ ] Flask-Talisman enabled in production
- [ ] `force_https=True` configured
- [ ] HSTS enabled with 1-year max-age
- [ ] SSL certificate valid and not self-signed
- [ ] SSL certificate includes all subdomains (if applicable)
- [ ] Certificate expiration date monitored

**Verification:**
```bash
# After deployment, test SSL
curl -I https://yourdomain.com | grep "Strict-Transport-Security"
# Should return: Strict-Transport-Security: max-age=31536000
```

### 2.2 Security Headers
- [ ] `Strict-Transport-Security` header present
- [ ] `X-Frame-Options: DENY` or `SAMEORIGIN`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] Content Security Policy (CSP) configured
- [ ] CSP allows only trusted sources

**Test with:**
```bash
curl -I https://yourdomain.com | grep -E "X-Frame|X-Content|X-XSS|Content-Security"
```

---

## 3. Authentication & Authorization

### 3.1 Password Security
- [ ] Passwords hashed with bcrypt (not MD5, SHA1, or plain text)
- [ ] Bcrypt work factor ≥ 12 rounds
- [ ] Password reset tokens expire (recommended: 1 hour)
- [ ] Password reset tokens single-use only
- [ ] No password displayed in logs or error messages

**Verification:**
```python
# Check bcrypt configuration
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
# Default is 12 rounds - verify in User.set_password()
```

### 3.2 Session Management
- [ ] Session cookies have `HttpOnly` flag
- [ ] Session cookies have `Secure` flag (HTTPS only)
- [ ] Session cookies have `SameSite=Lax` or `Strict`
- [ ] Session timeout configured (< 24 hours recommended)
- [ ] Session invalidated on logout
- [ ] Session regenerated after privilege escalation

**Verification:**
```python
# In config/config.py (ProductionConfig)
SESSION_COOKIE_SECURE = True  ✅
SESSION_COOKIE_HTTPONLY = True  ✅
SESSION_COOKIE_SAMESITE = 'Lax'  ✅
```

### 3.3 Access Control
- [ ] All admin routes protected with `@admin_required` decorator
- [ ] User can only access their own bookings
- [ ] Admin actions logged (who did what, when)
- [ ] No sensitive data in URL parameters
- [ ] File uploads restricted to authenticated users

**Test:**
```bash
# Try accessing admin page without auth
curl https://yourdomain.com/admin
# Should redirect to login or return 403
```

---

## 4. Input Validation & XSS Prevention

### 4.1 Form Protection
- [ ] CSRF tokens on ALL POST/PUT/DELETE forms
- [ ] CSRF validation enabled globally (`WTF_CSRF_ENABLED=True`)
- [ ] API endpoints properly exempted with `@csrf.exempt`
- [ ] File upload MIME type validation
- [ ] File upload size limits enforced (MAX_CONTENT_LENGTH)
- [ ] Filename sanitization for uploads

**Verification:**
```bash
# Check all forms have csrf_token
grep -r "method=\"POST\"" app/templates/ | \
  xargs -I {} grep -L "csrf_token" {}
# Should return no results
```

### 4.2 XSS Protection
- [ ] Jinja2 auto-escaping enabled (default in Flask)
- [ ] No `| safe` filters on user input
- [ ] User-generated content sanitized before display
- [ ] Content-Type headers set correctly
- [ ] `X-Content-Type-Options: nosniff` prevents MIME sniffing

**Test:**
```bash
# Check for unsafe filters
grep -r "| safe" app/templates/
# Verify each use is intentional and secure
```

### 4.3 SQL Injection Prevention
- [ ] SQLAlchemy ORM used (no raw SQL)
- [ ] If raw SQL used, parameterized queries only
- [ ] User input never concatenated into SQL
- [ ] Database user has minimal permissions

**Verification:**
```bash
# Check for raw SQL
grep -r "execute\|executemany" app/ --include="*.py"
# Verify all use parameterized queries
```

---

## 5. API & External Services

### 5.1 Stripe Integration
- [ ] Stripe webhook signature verification enabled
- [ ] Webhook endpoint exempt from CSRF
- [ ] Webhook endpoint has rate limiting exemption
- [ ] `STRIPE_WEBHOOK_SECRET` configured
- [ ] Payment amounts validated server-side
- [ ] Idempotency keys used for payment requests
- [ ] Stripe API keys are production keys

**Test Webhook:**
```bash
# Stripe CLI
stripe listen --forward-to localhost:5000/booking/webhook/stripe
stripe trigger payment_intent.succeeded
```

### 5.2 Third-Party API Keys
- [ ] All API keys in environment variables
- [ ] API keys not logged or exposed in errors
- [ ] API rate limits respected
- [ ] API requests use HTTPS only
- [ ] API errors handled gracefully

---

## 6. Rate Limiting & DOS Protection

### 6.1 Rate Limiting
- [ ] Flask-Limiter configured with Redis (production)
- [ ] Rate limits on authentication endpoints (login, register)
- [ ] Rate limits on booking/payment endpoints
- [ ] Rate limits on API endpoints
- [ ] Webhook endpoints exempted from rate limiting

**Verification:**
```python
# In app/__init__.py
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config['REDIS_URL']  # Redis required!
)
```

### 6.2 DOS Prevention
- [ ] Request size limits enforced
- [ ] Slow request timeout configured
- [ ] Concurrent connection limits (web server level)
- [ ] CloudFlare or similar CDN/WAF enabled

**Recommended Limits:**
- Max request body: 500MB (configured in MAX_CONTENT_LENGTH)
- Request timeout: 30 seconds
- Login attempts: 5 per 15 minutes

---

## 7. Database Security

### 7.1 Connection Security
- [ ] Database connection uses SSL/TLS
- [ ] Database password is strong and unique
- [ ] Database user has minimal required permissions
- [ ] Database not exposed to public internet
- [ ] Connection pooling configured

**Verification:**
```python
# In config/config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'ssl': {'ssl_mode': 'REQUIRED'}}  # If supported
}
```

### 7.2 Data Protection
- [ ] Sensitive data encrypted at rest (database level)
- [ ] Backups automated and encrypted
- [ ] Backup restoration tested
- [ ] Personal data retention policy defined
- [ ] Data deletion process implemented (GDPR)

---

## 8. Error Handling & Logging

### 8.1 Error Disclosure
- [ ] Generic error messages shown to users
- [ ] Stack traces NOT shown in production
- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] Detailed errors logged server-side only
- [ ] Error logs include timestamp, IP, user_id

**Verification:**
```python
# app.config['DEBUG'] must be False
# Custom error handlers in app/__init__.py:218-232 ✅
```

### 8.2 Logging Security
- [ ] Passwords never logged
- [ ] API keys never logged
- [ ] Credit card numbers never logged
- [ ] Logs rotated and archived
- [ ] Logs monitored for security events

**Test:**
```bash
# Check logs for sensitive data
grep -i "password\|api_key\|secret" /var/log/app.log
# Should find no actual secrets
```

---

## 9. Monitoring & Incident Response

### 9.1 Error Monitoring
- [ ] Sentry or similar error tracking configured
- [ ] Critical errors trigger immediate alerts
- [ ] Error dashboard reviewed daily
- [ ] Error trends analyzed weekly

### 9.2 Security Monitoring
- [ ] Failed login attempts logged and monitored
- [ ] Unusual activity patterns detected
- [ ] Uptime monitoring configured (UptimeRobot, Pingdom)
- [ ] SSL expiration monitoring
- [ ] Security alerts go to dedicated channel/email

### 9.3 Incident Response Plan
- [ ] Security contact email documented
- [ ] Incident response procedure documented
- [ ] Data breach notification process defined
- [ ] Backup restoration procedure tested

---

## 10. Compliance & Legal

### 10.1 GDPR Compliance
- [ ] Privacy Policy published and linked
- [ ] Cookie consent banner implemented
- [ ] User data export functionality (if storing EU data)
- [ ] User data deletion functionality
- [ ] Data retention policy documented
- [ ] Data processing agreements with third parties

### 10.2 Payment Compliance
- [ ] Terms of Service published
- [ ] Refund Policy published
- [ ] PCI DSS compliance (Stripe handles this)
- [ ] Business information displayed (address, contact)
- [ ] Stripe account verified and active

---

## 11. Infrastructure Security

### 11.1 Server Hardening
- [ ] Operating system updates applied
- [ ] Unused services disabled
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSH key-based authentication only
- [ ] Root login disabled
- [ ] Fail2ban or similar intrusion prevention

### 11.2 Deployment Security
- [ ] Deployment uses non-root user
- [ ] Application runs with minimal permissions
- [ ] Static files served by web server (not Flask)
- [ ] Gunicorn/uWSGI configured correctly
- [ ] Reverse proxy (Nginx) configured

**Nginx Security Headers:**
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

---

## 12. Pre-Launch Testing

### 12.1 Security Scans
- [ ] Run OWASP ZAP or similar security scanner
- [ ] Check for known vulnerabilities (`safety check`)
- [ ] Test HTTPS configuration (SSL Labs)
- [ ] Verify security headers (securityheaders.com)
- [ ] Test authentication bypass attempts
- [ ] Test authorization bypass attempts

**Commands:**
```bash
# Check Python dependencies for vulnerabilities
pip install safety
safety check --json

# Check npm dependencies (if applicable)
npm audit

# SSL test
curl https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
```

### 12.2 Penetration Testing
- [ ] Test SQL injection on all inputs
- [ ] Test XSS on all user inputs
- [ ] Test CSRF on all state-changing operations
- [ ] Test file upload bypasses
- [ ] Test authentication brute force
- [ ] Test session hijacking

### 12.3 Functional Security Testing
- [ ] Non-admin cannot access admin pages
- [ ] User cannot access other users' bookings
- [ ] Payment amount cannot be manipulated client-side
- [ ] Expired tokens are rejected
- [ ] Logout invalidates session

---

## Security Checklist Summary

**CRITICAL (Must Fix):**
- [ ] All secrets in environment variables ✅
- [ ] HTTPS enforced with valid SSL ✅
- [ ] CSRF protection enabled ✅
- [ ] Passwords hashed with bcrypt ✅
- [ ] Admin routes protected ✅
- [ ] Stripe webhook signature verified ✅

**HIGH (Should Fix):**
- [ ] Cookie consent banner
- [ ] Privacy Policy published
- [ ] Terms of Service published
- [ ] Error monitoring (Sentry)
- [ ] Rate limiting with Redis
- [ ] Security headers configured

**MEDIUM (Nice to Have):**
- [ ] 2FA for admin accounts
- [ ] Account lockout after failed logins
- [ ] Security audit logs
- [ ] Automated security scans
- [ ] Penetration testing

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | _________ | ___/___/___ | _________ |
| Security Review | _________ | ___/___/___ | _________ |
| Project Owner | _________ | ___/___/___ | _________ |

**Deployment Authorization:** 🔐

I confirm that all CRITICAL and HIGH priority items have been completed and tested.

Signature: _________________ Date: ___________

---

**Generated:** 2025-11-20
**Next Review:** After any security-related changes or quarterly
**Framework:** OWASP Top 10, CWE/SANS Top 25

