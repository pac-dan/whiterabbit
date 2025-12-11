/**
 * Momentum Clips - Navbar & UI Interactions
 */

// NAVBAR HIDE ON SCROLL DOWN, SHOW ON SCROLL UP
let lastScrollY = window.scrollY;
let ticking = false;

function updateNavbar() {
    const nav = document.getElementById('mainNav');
    if (!nav) return;
    
    const currentScrollY = window.scrollY;
    
    // Only hide/show after scrolling past 100px
    if (currentScrollY > 100) {
        if (currentScrollY > lastScrollY) {
            // Scrolling DOWN - hide navbar
            nav.classList.add('nav-hidden');
            nav.classList.remove('nav-visible');
        } else {
            // Scrolling UP - show navbar
            nav.classList.remove('nav-hidden');
            nav.classList.add('nav-visible');
        }
    } else {
        // At top of page - always show
        nav.classList.remove('nav-hidden');
        nav.classList.remove('nav-visible');
    }
    
    lastScrollY = currentScrollY;
    ticking = false;
}

window.addEventListener('scroll', function() {
    if (!ticking) {
        requestAnimationFrame(updateNavbar);
        ticking = true;
    }
});

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Auto-hide flash messages
    setTimeout(function() {
        const flashMessages = document.getElementById('flash-messages');
        if (flashMessages) {
            flashMessages.style.transition = 'opacity 0.5s';
            flashMessages.style.opacity = '0';
            setTimeout(() => flashMessages.remove(), 500);
        }
    }, 5000);
    
    // Button hover scale effects
    document.querySelectorAll('.btn-primary, .btn-secondary, .package-card, .glass-card').forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05) translateY(-5px)';
        });
        el.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
});

