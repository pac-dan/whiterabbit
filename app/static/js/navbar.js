/**
 * Momentum Clips - Navbar & UI Interactions
 */

// CYBERPUNK NAVBAR SCROLL EFFECT
window.addEventListener('scroll', function() {
    const nav = document.getElementById('mainNav');
    if (nav) {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
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

