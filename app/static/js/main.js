/**
 * Main JavaScript for Momentum Clips
 * General site functionality and utilities
 */

(function() {
    'use strict';

    /**
     * Initialize application
     */
    function init() {
        initSmoothScroll();
        initVideoFilters();
        initLazyLoading();
        initFormValidation();
        initScrollAnimations();
    }

    /**
     * Smooth scroll for anchor links
     */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const target = document.querySelector(this.getAttribute('href'));

                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Video gallery filtering
     */
    function initVideoFilters() {
        const filterButtons = document.querySelectorAll('[data-filter]');
        const videoItems = document.querySelectorAll('[data-video-item]');

        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filter = this.getAttribute('data-filter');

                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active', 'bg-blue-600', 'text-white'));
                this.classList.add('active', 'bg-blue-600', 'text-white');

                // Filter videos
                videoItems.forEach(item => {
                    const location = item.getAttribute('data-location');
                    const style = item.getAttribute('data-style');
                    const level = item.getAttribute('data-level');

                    if (filter === 'all' || location === filter || style === filter || level === filter) {
                        item.style.display = 'block';
                        setTimeout(() => {
                            item.classList.remove('opacity-0');
                            item.classList.add('opacity-100');
                        }, 10);
                    } else {
                        item.classList.add('opacity-0');
                        setTimeout(() => {
                            item.style.display = 'none';
                        }, 300);
                    }
                });
            });
        });
    }

    /**
     * Lazy loading for images and videos
     */
    function initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.getAttribute('data-src');

                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    /**
     * Scroll animations
     * Animate elements when they come into view
     */
    function initScrollAnimations() {
        const scrollElements = document.querySelectorAll('.scroll-fade-in');
        
        if (!scrollElements.length) return;

        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const delay = entry.target.getAttribute('data-delay') || 0;
                    
                    setTimeout(() => {
                        entry.target.classList.add('animate');
                    }, parseInt(delay));
                    
                    // Unobserve after animation
                    scrollObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1, // Trigger when 10% of element is visible
            rootMargin: '0px 0px -50px 0px' // Start animation slightly before element fully in view
        });

        scrollElements.forEach(element => {
            scrollObserver.observe(element);
        });
    }

    /**
     * Form validation
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');

        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                let isValid = true;
                const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        showFieldError(input, 'This field is required');
                    } else {
                        clearFieldError(input);
                    }

                    // Email validation
                    if (input.type === 'email' && input.value) {
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (!emailRegex.test(input.value)) {
                            isValid = false;
                            showFieldError(input, 'Please enter a valid email address');
                        }
                    }

                    // Password confirmation
                    if (input.name === 'confirm_password' || input.name === 'confirm_new_password') {
                        const passwordField = form.querySelector('input[name="password"], input[name="new_password"]');
                        if (passwordField && input.value !== passwordField.value) {
                            isValid = false;
                            showFieldError(input, 'Passwords do not match');
                        }
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                }
            });
        });
    }

    /**
     * Show field error
     */
    function showFieldError(input, message) {
        clearFieldError(input);

        input.classList.add('border-red-500');

        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        errorDiv.setAttribute('data-error-for', input.name);

        input.parentNode.appendChild(errorDiv);
    }

    /**
     * Clear field error
     */
    function clearFieldError(input) {
        input.classList.remove('border-red-500');

        const existingError = input.parentNode.querySelector(`[data-error-for="${input.name}"]`);
        if (existingError) {
            existingError.remove();
        }
    }

    /**
     * Utility: Format currency
     */
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    /**
     * Utility: Format date
     */
    window.formatDate = function(dateString, format = 'long') {
        const date = new Date(dateString);
        const options = format === 'long'
            ? { year: 'numeric', month: 'long', day: 'numeric' }
            : { year: 'numeric', month: 'short', day: 'numeric' };

        return date.toLocaleDateString('en-US', options);
    };

    /**
     * Utility: Show notification
     */
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 z-50 bg-white border-l-4 p-4 shadow-lg rounded-r-lg max-w-md animate-slide-in`;

        const borderColor = {
            'success': 'border-green-500',
            'error': 'border-red-500',
            'warning': 'border-yellow-500',
            'info': 'border-blue-500'
        }[type] || 'border-blue-500';

        notification.classList.add(borderColor);

        const iconClass = {
            'success': 'fa-check-circle text-green-500',
            'error': 'fa-exclamation-circle text-red-500',
            'warning': 'fa-exclamation-triangle text-yellow-500',
            'info': 'fa-info-circle text-blue-500'
        }[type] || 'fa-info-circle text-blue-500';

        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <i class="fas ${iconClass} mr-3"></i>
                    <p class="text-gray-800">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.transition = 'opacity 0.5s';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    };

    /**
     * Utility: Confirm action
     */
    window.confirmAction = function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    };

    /**
     * AJAX helper
     */
    window.fetchJSON = async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    };

    /**
     * Video player helpers
     */
    window.playVideo = function(vimeoId, title) {
        // Create modal for video playback
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="relative w-full max-w-4xl mx-4">
                <button onclick="this.parentElement.parentElement.remove()" class="absolute -top-10 right-0 text-white text-2xl">
                    <i class="fas fa-times"></i>
                </button>
                <div class="relative" style="padding-bottom: 56.25%;">
                    <iframe src="https://player.vimeo.com/video/${vimeoId}?autoplay=1"
                            class="absolute inset-0 w-full h-full"
                            frameborder="0"
                            allow="autoplay; fullscreen"
                            allowfullscreen></iframe>
                </div>
                <h3 class="text-white text-xl mt-4">${title}</h3>
            </div>
        `;

        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                modal.remove();
            }
        }, { once: true });
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
