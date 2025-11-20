# Security & Quality Fixes - Action Plan
**Based on User Audit:** 2025-11-20
**Priority:** High

---

## Your Audit Findings - Implementation Plan

### ✅ FIXED (Already Resolved)
- Payment bypass vulnerability → Stripe Checkout
- Refund processing
- CSRF protection
- Rate limiting on critical endpoints
- Bcrypt password hashing
- Open redirect protection

---

## 🔴 PRIORITY 1: SECURITY (Must Fix)

### 1.1 Implement Password Reset with Secure Tokens
**Risk:** High - Users locked out of accounts
**Effort:** 4-6 hours
**Files to Modify:**
- `app/models/user.py` - Add token generation/verification
- `app/routes/auth.py` - Complete TODO at lines 192, 204
- `app/services/email_service.py` - Add reset email function
- Create `app/templates/emails/password_reset.html`
- Create `app/templates/auth/reset_password.html`

**Implementation:**
```python
# app/models/user.py
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_reset_token(self, expires_in=3600):
    """Generate password reset token valid for 1 hour"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(self.email, salt='password-reset-salt')

@staticmethod
def verify_reset_token(token, expires_in=3600):
    """Verify token and return user"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_in)
        return User.query.filter_by(email=email).first()
    except:
        return None
```

**Testing:**
- Generate token, verify it works
- Test expired token (should fail)
- Test invalid token (should fail)
- Test token used twice (should work - tokens not single-use yet, can enhance)

---

### 1.2 Add Database Constraint to Prevent Double-Booking
**Risk:** Medium - Revenue loss from double-bookings
**Effort:** 2-3 hours
**Files to Modify:**
- `app/models/booking.py` - Add unique constraint
- Create new migration file
- `app/routes/booking.py` - Handle IntegrityError

**Implementation:**
```python
# Migration: Add unique constraint
def upgrade():
    # Prevent same package booked at same time
    op.create_index(
        'idx_unique_booking_slot',
        'bookings',
        ['package_id', 'booking_date'],
        unique=True,
        postgresql_where=sa.text("status NOT IN ('cancelled', 'refunded')")
    )

# app/routes/booking.py - Handle race condition
try:
    db.session.add(booking)
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    flash('This time slot was just booked. Please choose another time.', 'warning')
    return redirect(url_for('booking.new_booking'))
```

**Alternative Approach:**
```python
# Optimistic locking - check availability within transaction
@booking_bp.route('/create', methods=['POST'])
def create_booking():
    # ... get booking_date, package_id ...
    
    # Lock row and check availability
    slot_available = db.session.query(
        ~exists().where(
            and_(
                Booking.package_id == package_id,
                Booking.booking_date == booking_date,
                Booking.status.in_(['pending', 'confirmed'])
            )
        )
    ).scalar()
    
    if not slot_available:
        flash('Slot no longer available', 'warning')
        return redirect(url_for('booking.new_booking'))
    
    # Create booking immediately
    booking = Booking(...)
    db.session.add(booking)
    db.session.commit()
```

**Testing:**
- Open two browser windows
- Attempt to book same slot simultaneously
- Verify one succeeds, one gets error message

---

## 🟡 PRIORITY 2: QUALITY (Should Fix)

### 2.1 Add Rate Limiting to Video Likes Endpoint
**Risk:** Low - Like count manipulation
**Effort:** 30 minutes
**Files to Modify:**
- `app/routes/main.py` - Add rate limit to like endpoint

**Implementation:**
```python
# app/routes/main.py
@main_bp.route('/api/videos/<int:video_id>/like', methods=['POST'])
@limiter.limit("10 per minute")  # Add this line
@login_required
def like_video(video_id):
    # ... existing code ...
```

**Testing:**
- Spam like button rapidly
- Verify rate limit kicks in after 10 attempts

---

### 2.2 Replace traceback.print_exc() with Proper Logging
**Risk:** Low - Debug info leak
**Effort:** 30 minutes
**Files to Find and Fix:**

**Search for traceback usage:**
```bash
grep -r "traceback.print_exc\|import traceback" app/ --include="*.py"
```

**Replace with:**
```python
# Instead of:
import traceback
traceback.print_exc()

# Use:
current_app.logger.error(f'Error creating checkout session: {str(e)}', exc_info=True)
```

**Files likely affected:**
- `app/routes/booking.py` (line 325)
- Any other exception handlers

---

### 2.3 Add Input Validation to Admin Forms
**Risk:** Low - Data integrity
**Effort:** 2-3 hours
**Files to Modify:**
- `app/routes/admin.py` - Add validation to all form processing

**Implementation:**
```python
# Example for video creation
@admin_bp.route('/videos/new', methods=['POST'])
def create_video():
    title = request.form.get('title', '').strip()
    youtube_id = request.form.get('youtube_id', '').strip()
    
    # Validation
    errors = []
    if not title or len(title) < 3:
        errors.append('Title must be at least 3 characters')
    if not youtube_id or not re.match(r'^[a-zA-Z0-9_-]{11}$', youtube_id):
        errors.append('Invalid YouTube ID format')
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('admin.new_video'))
    
    # Continue with creation...
```

**Forms to validate:**
- Video form (title, youtube_id, display_order)
- Package form (name, price, duration, max_riders)
- Testimonial form (client_name, rating 1-5, text length)

---

## 🟢 PRIORITY 3: FEATURES (Nice to Have)

### 3.1 Implement Booking Confirmation Emails
**Risk:** None - UX improvement
**Effort:** 3-4 hours
**Files to Modify:**
- `app/services/email_service.py` - Add email functions
- `app/routes/booking.py` - Call email functions
- Create email templates

**Implementation:**
```python
# app/services/email_service.py
from flask_mail import Message
from flask import current_app, render_template
from app import mail

def send_booking_confirmation(booking):
    """Send booking confirmation email"""
    msg = Message(
        subject=f'Booking Confirmed - {booking.package.name}',
        recipients=[booking.user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg.html = render_template(
        'emails/booking_confirmation.html',
        booking=booking,
        user=booking.user,
        package=booking.package
    )
    
    try:
        mail.send(msg)
        current_app.logger.info(f'Confirmation email sent for booking {booking.id}')
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send confirmation email: {str(e)}')
        return False

# app/routes/booking.py:434
# Replace TODO with:
from app.services.email_service import send_booking_confirmation
send_booking_confirmation(booking)
```

**Email Templates Needed:**
- `app/templates/emails/booking_confirmation.html`
- `app/templates/emails/booking_cancelled.html`
- `app/templates/emails/booking_reminder.html`

---

### 3.2 Fix Brand Inconsistency
**Risk:** None - Branding/UX
**Effort:** 1-2 hours
**Investigation Needed:**

Where are the inconsistencies?
- "Momentum Clips" vs "SnowboardMedia"?
- Logo variations?
- Color scheme inconsistencies?

**Files to check:**
- `config/config.py` - APP_NAME setting
- `app/templates/base.html` - Site title
- All templates - Look for hardcoded names
- Database seed data

---

### 3.3 Complete Social Media Integration
**Risk:** None - Marketing feature
**Effort:** 4-6 hours
**Files to Modify:**
- `app/routes/admin.py` - Complete TODO at line 413
- `app/services/social_service.py` - Already exists!

**Implementation:**
```python
# app/routes/admin.py:413
from app.services.social_service import SocialMediaService

@admin_bp.route('/social/post', methods=['POST'])
@login_required
@admin_required
def post_to_social():
    content = request.form.get('content')
    platforms = request.form.getlist('platforms')  # ['instagram', 'tiktok', 'facebook']
    media_urls = request.form.getlist('media_urls')
    
    try:
        social_service = SocialMediaService()
        result = social_service.post(
            content=content,
            platforms=platforms,
            media_urls=media_urls
        )
        flash('Posted to social media successfully!', 'success')
    except Exception as e:
        flash(f'Social media post failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin.social'))
```

---

## Implementation Order (Recommended)

### Week 1: Security Fixes
**Day 1-2: Password Reset** (6 hours)
- Morning: Add token methods to User model
- Afternoon: Implement reset routes
- Test thoroughly

**Day 3: Double-Booking Prevention** (3 hours)
- Morning: Create migration with constraint
- Afternoon: Add error handling
- Test race conditions

### Week 2: Quality Improvements
**Day 4: Quick Fixes** (2 hours)
- Rate limit video likes (30 min)
- Replace traceback calls (30 min)
- Fix any linter errors (1 hour)

**Day 5: Input Validation** (3 hours)
- Add validation to admin forms
- Test edge cases

### Week 3: Features (Optional)
**Day 6-7: Email Confirmations** (4 hours)
- Set up email templates
- Implement email sending
- Test email delivery

**Day 8: Social Media** (4 hours)
- Complete Ayrshare integration
- Test posting to platforms

---

## Testing Checklist

### Password Reset
- [ ] Request reset link
- [ ] Receive email with link
- [ ] Click link, redirected to reset form
- [ ] Submit new password
- [ ] Login with new password works
- [ ] Old link expires after use
- [ ] Invalid token shows error
- [ ] Expired token (>1 hour) shows error

### Double-Booking Prevention
- [ ] Single booking works normally
- [ ] Simultaneous bookings - one fails gracefully
- [ ] Error message is user-friendly
- [ ] Failed attempt doesn't leave partial data

### Rate Limiting
- [ ] Normal like usage works
- [ ] Rapid likes trigger rate limit
- [ ] Error message explains limit
- [ ] Limit resets after time period

### Email Confirmations
- [ ] Confirmation sent after payment
- [ ] Cancellation email sent after cancel
- [ ] Emails have correct formatting
- [ ] Links in emails work
- [ ] Email goes to correct recipient

---

## Risk Assessment

| Fix | Risk of Not Fixing | Risk of Fixing |
|-----|-------------------|----------------|
| Password Reset | HIGH (user lockout) | LOW (well-tested pattern) |
| Double-Booking | MEDIUM (revenue loss) | LOW (standard constraint) |
| Video Likes Rate Limit | LOW (data manipulation) | VERY LOW (simple decorator) |
| Traceback Logging | LOW (debug leak) | VERY LOW (logging change) |
| Input Validation | LOW (data quality) | LOW (straightforward) |
| Email Confirmation | NONE (UX only) | LOW (email service risk) |
| Brand Consistency | NONE (cosmetic) | VERY LOW (text changes) |
| Social Media | NONE (optional feature) | LOW (API integration) |

---

## Effort Summary

| Priority | Item | Effort | Files Changed |
|----------|------|--------|---------------|
| 🔴 P1 | Password Reset | 4-6 hours | 5 files |
| 🔴 P1 | Double-Booking Fix | 2-3 hours | 3 files |
| 🟡 P2 | Video Likes Rate Limit | 30 min | 1 file |
| 🟡 P2 | Traceback Logging | 30 min | 2-3 files |
| 🟡 P2 | Input Validation | 2-3 hours | 1 file |
| 🟢 P3 | Email Confirmations | 3-4 hours | 4 files |
| 🟢 P3 | Brand Consistency | 1-2 hours | Multiple |
| 🟢 P3 | Social Media | 4-6 hours | 2 files |
| **TOTAL P1** | **6-9 hours** | **Critical** |
| **TOTAL P1+P2** | **11-15 hours** | **Recommended** |
| **TOTAL ALL** | **18-27 hours** | **Complete** |

---

## Ready to Start?

I can begin implementing these fixes in order of priority. Would you like me to:

1. **Start with Priority 1** (Security fixes: password reset + double-booking)
2. **Do a specific fix** you're most concerned about
3. **Review code first** to confirm the exact issues before fixing

Let me know and I'll proceed!

