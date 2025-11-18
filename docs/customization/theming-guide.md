# Momentum Clips - Customization Guide

Quick reference for editing your site content and styling.

## 🎯 Priority Files to Edit

### 1. **Homepage** (`app/templates/index.html`)

**What to change:**
- Line 3: Title tag - already says "SnowboardMedia"
- Line 17-19: Hero headline "Capture Your Epic Moments On The Slopes"
- Line 22: Subheadline text
- Line 36-40: Stats (rating, videos created count)
- Line 64: "Why Choose SnowboardMedia?" → "Why Choose Momentum Clips?"
- Throughout: Replace generic text with YOUR specific services

**Example changes:**
```html
<!-- OLD -->
<h1>Capture Your Epic Moments On The Slopes</h1>

<!-- NEW - Customize to YOUR business -->
<h1>Elevate Your Ride with Professional Video</h1>
```

### 2. **About Page** (`app/templates/about.html`)

Update:
- Your story/background
- Team information
- Mission statement
- Contact information

### 3. **Packages** (`app/templates/packages.html`)

Update:
- Package descriptions
- Pricing (currently shows $199, $499, $1299)
- Features included in each package
- Any special offers

### 4. **Styling** (`app/static/css/style.css`)

**Color scheme:** Currently blue/yellow
- Primary color: `#2563eb` (blue)
- Accent color: `#fbbf24` (yellow)

**To change colors:**
```css
/* Find and replace these colors in style.css */
/* Or use Tailwind classes in templates */

/* Current blue theme */
bg-blue-600  → Change to your brand color
text-blue-600 → Change to your brand color

/* Current yellow accent */
bg-yellow-400 → Change to your accent color
text-yellow-400 → Change to your accent color
```

### 5. **Navigation** (`app/templates/base.html`)

Already updated to "Momentum Clips" but you can:
- Change logo icon (line 64)
- Modify menu items
- Update footer content (bottom of file)

---

## 🎨 Quick Styling Changes

### Change Primary Colors

**Option 1: Use Tailwind (easiest)**
In any template file, change the color classes:

```html
<!-- Blue theme (current) -->
<div class="bg-blue-600 text-white">

<!-- Purple theme -->
<div class="bg-purple-600 text-white">

<!-- Red theme -->
<div class="bg-red-600 text-white">

<!-- Green theme -->
<div class="bg-green-600 text-white">
```

**Option 2: Custom CSS**
Edit `app/static/css/style.css`:

```css
/* Add at top of file */
:root {
    --primary-color: #your-color-hex;
    --accent-color: #your-accent-hex;
}

/* Then use throughout */
.btn-primary {
    background-color: var(--primary-color);
}
```

### Change Fonts

Currently using "Inter" font. To change:

In `app/templates/base.html`, line 21:
```html
<!-- Change this Google Font URL -->
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">

<!-- Then update in style block -->
<style>
    body {
        font-family: 'Poppins', sans-serif;  /* Change font name */
    }
</style>
```

Popular font choices:
- **Poppins** - Modern, friendly
- **Montserrat** - Professional, clean
- **Raleway** - Elegant, minimal
- **Roboto** - Classic, versatile

---

## 📸 Images to Replace

### Required Images (create and add to `app/static/images/`)

1. **Logo** - `logo.png` (your actual logo)
2. **Favicon** - `favicon.ico` (browser tab icon)
3. **Hero Image** - `hero-snowboarder.png` (main homepage image)
4. **OG Image** - `og-image.jpg` (1200x630px for social media sharing)
5. **Video Thumbnails** - For gallery section
6. **Team Photos** - For about page

### Image Sizes:
- Logo: 200x200px (transparent background)
- Favicon: 32x32px
- Hero: 1200x800px
- OG Image: 1200x630px (Facebook/Twitter sharing)

---

## ✏️ Content Sections to Personalize

### Homepage (`app/templates/index.html`)

**Section 1: Hero (Lines 7-58)**
- Your main headline
- Your value proposition
- Call-to-action buttons
- Key stats/achievements

**Section 2: Features (Lines 60-102)**
- What makes YOU special
- Your services/equipment
- Why customers should choose you

**Section 3: How It Works (Lines 104-180)**
- Your process (booking → filming → delivery)
- Timeline expectations

**Section 4: Testimonials (Lines 182-230)**
- Real customer reviews (will pull from database)

**Section 5: Packages (Lines 232-280)**
- Preview of your packages

**Section 6: CTA (Lines 282-320)**
- Final call to action
- Contact information

### About Page (`app/templates/about.html`)

```html
What to include:
- Your story (why you started)
- Your experience/credentials
- Your team members
- Your equipment/technology
- Your service area
- What makes you different
```

### Contact Page (`app/templates/contact.html`)

Update:
- Email addresses
- Phone numbers
- Location/service areas
- Social media links
- Business hours

---

## 🎬 Content Writing Tips

### Write Like YOU Talk to Customers

**Instead of generic:**
> "Professional snowboard video production services"

**Write specifically:**
> "I follow you down the mountain with 4K cameras and drones, then edit your best runs into a sharable highlight reel"

### Focus on Benefits, Not Features

**Feature-focused (boring):**
> "We use Sony A7S III cameras"

**Benefit-focused (exciting):**
> "Our cinema cameras capture every detail of your tricks in stunning slow-motion"

### Use Your Real Voice

**Generic:**
> "SnowboardMedia provides quality service"

**Personal:**
> "I've been filming riders for 10 years and I know exactly which angles make your runs look epic"

---

## 🔥 Hot Reload Tips

When editing templates:
1. Save the file
2. Refresh your browser (Ctrl+Shift+R for hard refresh)
3. Changes appear immediately!

When editing CSS:
1. Save the file
2. Hard refresh browser (Ctrl+Shift+R)

When editing Python code:
- Flask auto-reloads in development mode
- If it doesn't reload, press Ctrl+C in terminal and restart

---

## 📋 Content Checklist

Go through each page and update:

### ✅ Homepage
- [ ] Hero headline
- [ ] Hero subtext
- [ ] Call-to-action buttons
- [ ] Feature descriptions (4 boxes)
- [ ] How it works steps
- [ ] Stats (rating, video count, etc.)

### ✅ About Page
- [ ] Your story
- [ ] Team members
- [ ] Mission statement
- [ ] Service area

### ✅ Packages Page
- [ ] Package names
- [ ] Descriptions
- [ ] Prices
- [ ] Features list
- [ ] What's included/excluded

### ✅ Gallery
- [ ] Video descriptions
- [ ] Location tags
- [ ] Style categories

### ✅ Contact
- [ ] Email addresses
- [ ] Phone number
- [ ] Physical address (if any)
- [ ] Social media links
- [ ] Business hours

### ✅ Footer (in base.html)
- [ ] Copyright text
- [ ] Quick links
- [ ] Contact info
- [ ] Social media

---

## 🎨 Styling Quick Reference

### Tailwind CSS Classes (Already in Use)

**Colors:**
```html
bg-blue-600     (background)
text-blue-600   (text color)
border-blue-600 (border color)
```

**Spacing:**
```html
p-4    (padding)
m-4    (margin)
px-8   (padding left/right)
py-4   (padding top/bottom)
```

**Text:**
```html
text-xl   text-2xl   text-3xl   text-4xl   (sizes)
font-bold   font-semibold   (weights)
text-center   text-left   text-right   (alignment)
```

**Layout:**
```html
flex   grid   (layout types)
items-center   justify-center   (alignment)
gap-4   space-x-4   space-y-4   (spacing between items)
```

---

## 🚀 Testing Your Changes

1. **View in browser:** http://127.0.0.1:5000
2. **Test mobile:** Press F12, click device toggle icon
3. **Check all pages:**
   - Homepage: `/`
   - About: `/about`
   - Packages: `/packages`
   - Gallery: `/gallery`
   - Contact: `/contact`
4. **Test forms:** Register, login, booking

---

## 💡 Pro Tips

1. **Start with content, then style**
   - Get your words right first
   - Then make it pretty

2. **Use real photos ASAP**
   - Stock photos are okay to start
   - Replace with YOUR actual work quickly

3. **Mobile first**
   - Most users will be on phones
   - Test on mobile constantly

4. **Keep it simple**
   - Don't over-design
   - Focus on clear message and easy booking

5. **Get feedback**
   - Show friends/customers
   - Ask what's confusing
   - Iterate quickly

---

## 🆘 Need Help?

**Common issues:**

**"My changes don't show"**
- Hard refresh: Ctrl+Shift+R
- Clear browser cache
- Check you saved the file

**"Site looks broken"**
- Check browser console (F12)
- Look for HTML syntax errors
- Make sure you didn't break closing tags

**"CSS not working"**
- Make sure Tailwind CDN is loaded
- Check class names are correct
- Try inline styles to test

---

## Next Steps After Customization

1. Take screenshots of the site
2. Test booking flow end-to-end
3. Have a friend try to book
4. Upload real videos to gallery
5. Get testimonials from real customers
6. Set up Google Analytics
7. Deploy to production (follow HOSTINGER_DEPLOYMENT.md)

---

**Remember:** Perfect is the enemy of done. Get it good enough, launch, then improve based on real feedback!

