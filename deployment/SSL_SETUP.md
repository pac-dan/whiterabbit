# SSL/HTTPS Setup Guide for Momentum Clips

## Overview

This guide explains how to set up HTTPS for your Momentum Clips deployment on Hostinger VPS using Let's Encrypt SSL certificates.

## Prerequisites

- Domain name pointed to your VPS IP address
- SSH access to your VPS
- Docker and Docker Compose installed

## Option 1: Let's Encrypt with Certbot (Recommended)

### Step 1: Install Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### Step 2: Stop Nginx (Temporarily)

```bash
docker-compose stop nginx
```

### Step 3: Generate Certificates

```bash
sudo certbot certonly --standalone -d momentumclips.com -d www.momentumclips.com
```

Follow the prompts:
- Enter email address for renewal notifications
- Agree to terms of service
- Choose whether to share email with EFF

### Step 4: Copy Certificates to Deployment Directory

```bash
sudo cp /etc/letsencrypt/live/momentumclips.com/fullchain.pem deployment/ssl/
sudo cp /etc/letsencrypt/live/momentumclips.com/privkey.pem deployment/ssl/
sudo chown $USER:$USER deployment/ssl/*.pem
```

### Step 5: Enable HTTPS in Nginx Configuration

Edit `deployment/nginx.conf` and uncomment the HTTPS server block (lines 83-137):

```nginx
# Uncomment this block:
server {
    listen 443 ssl http2;
    server_name momentumclips.com www.momentumclips.com;
    
    # SSL certificates
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # ... rest of configuration
}
```

Also update the HTTP server to redirect to HTTPS:

```nginx
server {
    listen 80;
    server_name _;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}
```

### Step 6: Update docker-compose.yml SSL Volume Mount

Ensure this line exists in `docker-compose.yml` under nginx volumes:

```yaml
- ./deployment/ssl:/etc/nginx/ssl:ro
```

### Step 7: Restart Services

```bash
docker-compose up -d
```

### Step 8: Test HTTPS

Visit: https://momentumclips.com

You should see:
- 🔒 Padlock icon in browser
- Valid SSL certificate
- HTTP automatically redirects to HTTPS

## Option 2: Manual SSL Certificate

If you have SSL certificates from another provider:

### Step 1: Copy Certificates

Place your certificates in `deployment/ssl/`:
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

```bash
cp /path/to/your/fullchain.pem deployment/ssl/
cp /path/to/your/privkey.pem deployment/ssl/
chmod 600 deployment/ssl/privkey.pem
chmod 644 deployment/ssl/fullchain.pem
```

### Step 2: Follow Steps 5-8 from Option 1

## Certificate Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

### Create Renewal Script

```bash
sudo nano /etc/cron.monthly/renew-ssl.sh
```

Add:

```bash
#!/bin/bash
# Stop nginx
cd /path/to/whiterabbit
docker-compose stop nginx

# Renew certificates
certbot renew --quiet

# Copy new certificates
cp /etc/letsencrypt/live/momentumclips.com/fullchain.pem deployment/ssl/
cp /etc/letsencrypt/live/momentumclips.com/privkey.pem deployment/ssl/

# Restart nginx
docker-compose start nginx
```

Make executable:

```bash
sudo chmod +x /etc/cron.monthly/renew-ssl.sh
```

### Test Renewal

```bash
sudo certbot renew --dry-run
```

## Troubleshooting

### Certificate Not Found Error

```
Error: SSL certificate not found at /etc/nginx/ssl/fullchain.pem
```

**Solution**: Verify certificates exist and volume mount is correct in docker-compose.yml

### Invalid Certificate Warning

**Solution**: 
- Ensure domain name matches certificate
- Check certificate hasn't expired
- Verify fullchain.pem includes intermediate certificates

### Mixed Content Warnings

**Solution**: Update `config.py` to use HTTPS in production:

```python
PREFERRED_URL_SCHEME = 'https'
SESSION_COOKIE_SECURE = True
```

### Port 443 Already in Use

```bash
# Check what's using port 443
sudo lsof -i :443

# Kill process if needed
sudo kill -9 <PID>
```

## Security Best Practices

1. **Strong SSL Configuration** ✓ 
   - TLS 1.2 and 1.3 only
   - Strong cipher suites
   - HSTS enabled

2. **HTTP to HTTPS Redirect** ✓
   - All HTTP traffic redirected to HTTPS

3. **Security Headers** ✓
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: 1; mode=block

4. **Certificate Monitoring**
   - Set up expiration alerts
   - Test renewal process monthly

## Verification Checklist

- [ ] HTTPS loads without warnings
- [ ] HTTP redirects to HTTPS
- [ ] SSL certificate is valid
- [ ] Certificate matches domain name
- [ ] Certificate chain is complete
- [ ] Strong cipher suites enabled
- [ ] HSTS header present
- [ ] No mixed content warnings
- [ ] WebSocket connections work over HTTPS (wss://)
- [ ] Payment processing works with HTTPS

## SSL Test Tools

- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **Security Headers**: https://securityheaders.com/
- **Certificate Decoder**: https://www.sslshopper.com/certificate-decoder.html

Expected Grade: **A** or **A+**

## Notes

- Let's Encrypt certificates are free and renew automatically
- Certificates are valid for 90 days
- Renewal should happen automatically with cron job
- Keep backup of certificates in secure location
- Update `.env` CORS_ORIGINS to use HTTPS URLs

## Support

If you encounter issues:
- Check Nginx logs: `docker-compose logs nginx`
- Check certbot logs: `sudo cat /var/log/letsencrypt/letsencrypt.log`
- Verify DNS: `dig momentumclips.com +short`
