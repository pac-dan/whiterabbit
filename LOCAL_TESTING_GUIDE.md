# 🧪 Local Testing Guide - Momentum Clips

**Server**: http://localhost:5000  
**Status**: 🟢 Running

---

## 🚀 Quick Start

### Option 1: Double-click to start
```
📁 start_local_server.bat
```

### Option 2: Manual start
```bash
cd C:\Users\Dan\whiterabbit
venv\Scripts\activate
flask run
```

---

## ✅ Testing Checklist

### 1️⃣ **Homepage Test**
**URL**: http://localhost:5000/

**What to check:**
- [ ] Hero section loads with snowboard images
- [ ] Packages section displays 3 packages
- [ ] Featured videos show in gallery
- [ ] Testimonials visible
- [ ] Navigation menu works
- [ ] Footer displays correctly
- [ ] Mobile responsive (resize browser)

---

### 2️⃣ **User Registration Test**
**URL**: http://localhost:5000/register

**Steps:**
1. Click "Register" in nav
2. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: TestPass123!
   - Confirm Password: TestPass123!
3. Click "Register"

**Expected:** ✅ Redirected to dashboard with success message

---

### 3️⃣ **User Login Test**
**URL**: http://localhost:5000/login

**Test User Credentials:**
```
Email: test@example.com
Password: TestPass123!
```

**Admin Credentials:**
```
Email: admin@momentumclips.com
Password: Admin123!
```

**Expected:** ✅ Logged in successfully, see user menu

---

### 4️⃣ **Booking System Test** ⭐ MAIN FEATURE
**URL**: http://localhost:5000/booking/new

**Prerequisites:** Must be logged in

**Steps:**
1. Select a package (should see 3 options)
2. Choose date & time (should enforce 24hr minimum)
3. Fill in:
   - Number of riders: 1
   - Location: Select from dropdown
   - Experience level: Choose one
   - Special requests: "Test booking"
4. Check terms checkbox
5. Click "Proceed to Payment"

**Expected Results:**
- ✅ Date picker blocks dates less than 24 hours away
- ✅ Form shows CSRF token (hidden)
- ✅ Validation works on all fields
- ✅ Redirects to payment page

**Common Issues:**
- ❌ "CSRF token missing" → FIXED (we added it!)
- ❌ "Date too soon" → Working as designed (24hr minimum)

---

### 5️⃣ **Payment Page Test**
**URL**: http://localhost:5000/booking/{booking_id}/payment

**What to check:**
- [ ] Booking summary displays correctly
- [ ] Amount matches package price
- [ ] Stripe elements placeholder shows
- [ ] If no Stripe keys: Shows warning message

**Note:** Payment won't fully work without Stripe keys, but page should load!

---

### 6️⃣ **Packages Page Test**
**URL**: http://localhost:5000/packages

**What to check:**
- [ ] All 3 packages display
- [ ] Prices show correctly
- [ ] "Book Now" buttons work
- [ ] Package details expand/show

---

### 7️⃣ **Gallery Test**
**URL**: http://localhost:5000/gallery

**What to check:**
- [ ] Video thumbnails display
- [ ] Videos are clickable
- [ ] Modal or video page opens
- [ ] YouTube embeds work (if configured)

---

### 8️⃣ **Admin Dashboard Test** 🔐
**URL**: http://localhost:5000/admin

**Login with:**
```
Email: admin@momentumclips.com
Password: Admin123!
```

**What to check:**
- [ ] Dashboard shows statistics
- [ ] Bookings list (should be empty or show test bookings)
- [ ] Packages management
- [ ] Videos management
- [ ] Testimonials management
- [ ] Users list

**Admin Features:**
- Create/Edit/Delete packages
- View/Manage bookings
- Upload videos
- Manage testimonials

---

### 9️⃣ **Contact Form Test**
**URL**: http://localhost:5000/contact

**Steps:**
1. Fill in contact form
2. Submit

**Expected:**
- ✅ Form submits (may fail if email not configured)
- ✅ Shows success/error message

**Note:** Email won't work without MAIL_USERNAME and MAIL_PASSWORD configured

---

### 🔟 **Health Check Test**
**URL**: http://localhost:5000/health

**Expected Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "redis": "not configured"
  },
  "version": "1.0.0"
}
```

**Note:** Redis "not configured" is normal for local development

---

## 🐛 Common Issues & Solutions

### Issue: "Page Not Found"
**Solution:** Make sure server is running at http://localhost:5000

### Issue: "CSRF Token Missing"
**Solution:** ✅ FIXED! We added it to the form

### Issue: "Can't select date in booking"
**Solution:** Date must be at least 24 hours in the future (working as designed)

### Issue: "Payment doesn't work"
**Solution:** Normal without Stripe keys. Add to .env:
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Issue: "Email not sending"
**Solution:** Configure in .env:
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Issue: "Redis warnings"
**Solution:** Normal for development. Can ignore or install Redis locally

---

## 📊 Test Results Tracker

Track your test results here:

### Core Features
- [ ] ✅ Homepage loads
- [ ] ✅ User registration works
- [ ] ✅ User login works
- [ ] ✅ Booking form displays packages
- [ ] ✅ Date validation enforces 24hr minimum
- [ ] ✅ CSRF protection working
- [ ] ✅ Payment page accessible
- [ ] ✅ Admin dashboard functional

### Optional Features
- [ ] 🟡 Stripe payments (needs keys)
- [ ] 🟡 Email notifications (needs config)
- [ ] 🟡 AI chat widget (needs Retell keys)

---

## 🎯 Success Criteria

Your local test is successful if:

✅ Homepage loads with content  
✅ Can register/login users  
✅ Can view packages  
✅ Can create booking (gets to payment page)  
✅ Admin dashboard accessible  
✅ No critical errors in console

---

## 🔥 Advanced Testing

### Test Booking Flow End-to-End

**Scenario:** User books "Action Package"

1. **Register** new user: rider1@test.com
2. **Login** with new user
3. **Browse** packages page
4. **Click** "Book Now" on Action Package
5. **Fill** booking form with tomorrow's date
6. **Submit** booking
7. **Verify** redirects to payment
8. **As Admin**: Login and check bookings list

**Expected:** Booking shows in admin with "pending" status

---

### Test Multiple Users

1. Register 3 different users
2. Have each create a booking
3. Login as admin
4. View all bookings in admin dashboard

**Expected:** All 3 bookings visible to admin

---

### Test Validation

**Try these (should fail gracefully):**
- Booking date less than 24 hours away
- Booking date more than 90 days away
- Empty required fields
- Invalid email format
- Password too short

**Expected:** Helpful error messages, no crashes

---

## 🎉 When Testing is Complete

### All tests passing? Time to:

1. **Review results** - Any issues found?
2. **Fix any bugs** - Small tweaks needed?
3. **Prepare for production** - Follow PRODUCTION_DEPLOYMENT_GUIDE.md
4. **Deploy!** - You're ready! 🚀

---

## 💡 Pro Tips

### Use Browser DevTools
- **F12** to open console
- Check for JavaScript errors
- Monitor network requests
- Test responsive design

### Test in Multiple Browsers
- Chrome
- Firefox  
- Safari (if on Mac)
- Mobile browser (phone)

### Check Database
```bash
# View bookings created
sqlite3 instance/snowboard_media.db
SELECT * FROM bookings;
.quit
```

---

## 📞 Need Help?

**Server not starting?**
- Check if port 5000 is free
- Try: `flask run --port=5001`

**Database errors?**
- Run: `flask db upgrade`
- Or: `python reset_and_seed.py`

**Module not found?**
- Activate venv: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

---

## ✅ Quick Command Reference

```bash
# Start server
flask run

# Stop server
CTRL + C

# Reset database
python reset_and_seed.py

# Create admin
python quick_admin.py

# Check database
sqlite3 instance/snowboard_media.db

# View logs
(logs appear in terminal where flask runs)
```

---

**Happy Testing! 🧪**

**Server:** http://localhost:5000  
**Admin:** admin@momentumclips.com / Admin123!  
**Health:** http://localhost:5000/health

---

**🎯 Goal:** Test everything works locally before deploying to production!

