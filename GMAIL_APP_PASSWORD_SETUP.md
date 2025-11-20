# 📧 Gmail App Password Setup Guide

## ⚠️ Current Issue

Your email configuration is correct, but Gmail is rejecting the password because it requires an **App Password** instead of your regular Gmail password.

**Error Message:**
```
534-5.7.9 Application-specific password required
```

---

## ✅ Solution: Generate Gmail App Password

### Step 1: Enable 2-Factor Authentication (if not already enabled)

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left menu
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the steps to enable 2FA (required for App Passwords)

---

### Step 2: Generate App Password

1. **Go to App Passwords page:**
   - Visit: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords

2. **Create new App Password:**
   - Select app: **Mail**
   - Select device: **Other (Custom name)**
   - Enter name: `Momentum Clips` or `WhiteRabbit`
   - Click **Generate**

3. **Copy the 16-character password:**
   - Google will show you a 16-character password like: `abcd efgh ijkl mnop`
   - **Remove spaces:** `abcdefghijklmnop`
   - Copy this password

---

### Step 3: Update Your .env File

Open your `.env` file and update the `MAIL_PASSWORD` with the App Password (no spaces):

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=devvsman@gmail.com
MAIL_PASSWORD=abcdefghijklmnop    # <-- Use App Password here (no spaces!)
MAIL_DEFAULT_SENDER=devvsman@gmail.com
SUPPORT_EMAIL=devvsman@gmail.com
ADMIN_EMAIL=devvsman@gmail.com
```

**Important:**
- Use the 16-character App Password, NOT your regular Gmail password
- Remove all spaces from the App Password
- Keep the App Password secret (never commit to git)

---

### Step 4: Restart Server & Test

1. **Restart your Flask server:**
   ```bash
   # Stop current server (Ctrl+C if running)
   cd C:\Users\Dan\whiterabbit
   .\venv\Scripts\Activate.ps1
   flask run
   ```

2. **Test email again:**
   ```bash
   python send_test_email.py
   ```

3. **Enter your email when prompted** to receive a test email

---

## 🧪 Quick Test Commands

After updating your `.env` with the App Password:

```bash
cd C:\Users\Dan\whiterabbit
.\venv\Scripts\Activate.ps1

# Test email configuration
python send_test_email.py

# Or test password reset email (using Flask shell)
flask shell
```

In Flask shell:
```python
from app.models.user import User
from app.services.email_service import EmailService

# Get a user
user = User.query.first()

# Generate reset token
token = user.generate_reset_token()

# Send reset email
email_service = EmailService()
result = email_service.send_password_reset(user, token)

print(f"Email sent: {result}")
```

---

## 🔒 Security Notes

**App Passwords are MORE secure than regular passwords because:**
- ✅ They only work for specific apps (not full Google account access)
- ✅ You can revoke them individually without changing your main password
- ✅ They bypass 2FA for the specific app only
- ✅ They're app-specific and can't be used to sign into your Google Account

**Keep your App Password safe:**
- ❌ Never commit `.env` to git (already in `.gitignore`)
- ❌ Never share your App Password publicly
- ✅ Rotate App Passwords periodically
- ✅ Revoke unused App Passwords from Google Account settings

---

## 🎯 What Happens After Setup

Once you have the App Password configured, these features will work automatically:

1. **Password Reset Emails** 🔐
   - Users can reset forgotten passwords
   - Secure time-limited tokens (1 hour)
   - Professional email template

2. **Booking Confirmation Emails** 📧
   - Sent after successful payment
   - Includes all booking details
   - Beautiful HTML template

3. **Welcome Emails** 👋 (if enabled)
   - Sent to new users after registration

4. **Admin Notifications** 🔔
   - Alerts for new bookings, cancellations, etc.

---

## ❓ Troubleshooting

### "Application-specific password required"
- **Solution:** You're using your regular Gmail password. Follow steps above to generate App Password.

### "Invalid credentials"
- **Solution:** 
  - Make sure you copied the App Password correctly (no spaces)
  - Verify `MAIL_USERNAME` matches the Gmail account that created the App Password

### "Less secure app access"
- **Note:** This setting is deprecated. Gmail now requires App Passwords with 2FA.

### Emails going to spam
- Add your domain to SPF records (for production)
- Use a custom domain email (instead of Gmail) for production
- For now, check spam/junk folder during testing

---

## 🚀 Alternative: Use a Different Email Provider

If you prefer not to use Gmail, you can use:

### **SendGrid** (Recommended for Production)
```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### **Mailgun**
```bash
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@your-domain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### **AWS SES**
```bash
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USERNAME=your-ses-username
MAIL_PASSWORD=your-ses-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

---

## 📝 Current Configuration Status

✅ **Email Server:** smtp.gmail.com  
✅ **Email Username:** devvsman@gmail.com  
✅ **Port:** 587 (TLS enabled)  
❌ **App Password:** Needs to be generated and added to .env

---

## 🎉 Next Steps

1. Generate Gmail App Password (follow Step 2 above)
2. Update `MAIL_PASSWORD` in `.env` with App Password
3. Restart Flask server
4. Test email: `python send_test_email.py`
5. ✅ Email features will work automatically!

---

**Need help?** Run `python send_test_email.py` after updating the password to test.

