/**
 * Utility Functions
 * General-purpose JavaScript utilities used across the site
 */

// Navigate to a URL
function navigateTo(url) {
    window.location.href = url;
}

// Reload current page
function reloadPage() {
    window.location.reload();
}

// Print current page
function printPage() {
    window.print();
}

// Go back in history
function goBack() {
    window.history.back();
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// Format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Toggle chat widget (Retell AI or fallback)
function toggleChat() {
    // Try to find and click the Retell AI widget
    const retellWidget = document.querySelector('[data-retell-widget]') ||
                        document.querySelector('#retell-widget-bubble') ||
                        document.querySelector('.retell-chat-bubble');
    
    if (retellWidget) {
        retellWidget.click();
        return;
    }
    
    // Fallback: redirect to contact page if widget not available
    window.location.href = '/contact';
}

// Format date
function formatDate(date, format = 'long') {
    const dateObj = date instanceof Date ? date : new Date(date);
    
    const options = {
        short: { year: 'numeric', month: '2-digit', day: '2-digit' },
        long: { year: 'numeric', month: 'long', day: 'numeric' },
        time: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
    };
    
    return dateObj.toLocaleDateString('en-US', options[format] || options.long);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Show notification/toast
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in ${getNotificationClass(type)}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Get notification class based on type
function getNotificationClass(type) {
    const classes = {
        success: 'bg-green-600 text-white',
        error: 'bg-red-600 text-white',
        warning: 'bg-yellow-600 text-white',
        info: 'bg-blue-600 text-white'
    };
    return classes[type] || classes.info;
}

// Copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text)
            .then(() => showNotification('Copied to clipboard!', 'success'))
            .catch(err => console.error('Failed to copy:', err));
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('Copied to clipboard!', 'success');
    }
}

// Get CSRF token from meta tag or cookie
function getCSRFToken() {
    // Try meta tag first
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Fall back to cookie
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let cookie of cookieArray) {
        cookie = cookie.trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length);
        }
    }
    
    return null;
}

// Make AJAX request with CSRF token
async function fetchWithCSRF(url, options = {}) {
    const csrfToken = getCSRFToken();
    
    options.headers = options.headers || {};
    if (csrfToken) {
        options.headers['X-CSRFToken'] = csrfToken;
    }
    
    try {
        const response = await fetch(url, options);
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Lazy load images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize utilities on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize lazy loading if images exist
    if (document.querySelectorAll('img[data-src]').length > 0) {
        lazyLoadImages();
    }
    
    // Add CSS animations for notifications
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-20px); }
            }
            .animate-fade-in { animation: fadeIn 0.3s ease-out; }
            .animate-fade-out { animation: fadeOut 0.3s ease-out; }
        `;
        document.head.appendChild(style);
    }
});

