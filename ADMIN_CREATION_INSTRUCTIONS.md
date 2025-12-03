# Admin User Creation Instructions

## 🎯 Quick Start (Render Free Tier)

Since you're on Render's free tier without shell access, I've created a temporary web route to create your admin user.

### Step 1: Deploy the Changes

```bash
git add .
git commit -m "Add temporary admin creation route"
git push
```

This will automatically deploy to Render.

### Step 2: Create Admin User

Once deployed (wait ~2-3 minutes), visit this URL in your browser:

```
https://www.momentumclips.com/temporary-create-admin-delete-after-use
```

You'll see a JSON response like:

```json
{
  "status": "success",
  "message": "Admin user created successfully!",
  "email": "admin@momentumclips.com",
  "password": "TempAdmin123!",
  "login_url": "https://www.momentumclips.com/auth/login",
  "warning": "⚠️ DELETE THIS ROUTE FROM CODE IMMEDIATELY AND REDEPLOY!",
  "security_note": "Change password after first login!"
}
```

**Save these credentials immediately!**

### Step 3: Test Login

Go to: https://www.momentumclips.com/auth/login

Login with:
- Email: `admin@momentumclips.com`
- Password: `TempAdmin123!`

### Step 4: Remove the Temporary Route (IMPORTANT!)

After successfully creating the admin and logging in, **immediately** remove the temporary route for security:

1. Open `app/__init__.py`
2. Delete lines containing the `temporary_create_admin` route (around line 328-378)
3. Commit and push:
   ```bash
   git add app/__init__.py
   git commit -m "Remove temporary admin creation route"
   git push
   ```

### Step 5: Change Your Password

After logging in as admin:
1. Go to your profile
2. Change the password from `TempAdmin123!` to something secure
3. Consider using a password manager

---

## 🔐 Custom Credentials (Optional)

If you want to use custom credentials instead of the defaults, add these environment variables in your Render dashboard **before** visiting the URL:

1. Go to Render Dashboard → Your Service → Environment
2. Add:
   - `ADMIN_EMAIL` = your-email@example.com
   - `ADMIN_NAME` = Your Name
   - `ADMIN_PASSWORD` = YourSecurePassword123!
3. Save and wait for automatic redeploy
4. Then visit the temporary URL

---

## 🛠️ Alternative: Command Line Script

If you gain shell access later (paid tier), you can use:

```bash
python create_production_admin.py
```

This script will:
- Check if admin already exists
- Create admin with credentials from environment variables or defaults
- Provide login information

---

## 🚨 Security Notes

1. **Delete the temporary route immediately after use** - it's a security risk!
2. **Change the default password** as soon as you log in
3. **Don't share your admin credentials**
4. Consider enabling 2FA if you implement it later

---

## ❓ Troubleshooting

### "User already exists"
If you see this message, an admin user already exists. Use the "Forgot Password" feature to reset it.

### "Error" response
Check Render logs for details:
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Look for error messages

### Route returns 404
- Wait a few more minutes for deployment to complete
- Check Render dashboard to ensure deployment succeeded
- Check the exact URL spelling

---

## 📝 What Was Changed

### Files Created:
1. `create_production_admin.py` - Standalone script for creating admin (for when you have shell access)
2. `ADMIN_CREATION_INSTRUCTIONS.md` - This file

### Files Modified:
1. `app/__init__.py` - Added temporary admin creation route (REMOVE AFTER USE!)

---

## ✅ Checklist

- [ ] Deploy changes to Render
- [ ] Wait for deployment to complete
- [ ] Visit temporary URL to create admin
- [ ] Save credentials
- [ ] Test login at /auth/login
- [ ] **DELETE temporary route from code**
- [ ] Redeploy after removing route
- [ ] Change admin password
- [ ] Done! 🎉

