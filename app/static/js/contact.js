/**
 * Contact Form JavaScript
 * Handles contact form validation and submission
 */

// Validate contact form
function validateContactForm(event) {
    const form = event.target;
    const email = form.elements['email'];
    const message = form.elements['message'];
    
    let isValid = true;
    let errors = [];
    
    // Validate email
    if (email && !isValidEmail(email.value)) {
        errors.push('Please enter a valid email address');
        isValid = false;
    }
    
    // Validate message length
    if (message && message.value.trim().length < 10) {
        errors.push('Message must be at least 10 characters long');
        isValid = false;
    }
    
    if (!isValid) {
        event.preventDefault();
        showFormErrors(errors);
        return false;
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Sending...';
    }
    
    return true;
}

// Validate email format
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show form errors
function showFormErrors(errors) {
    const errorContainer = document.getElementById('form-errors') || createErrorContainer();
    errorContainer.innerHTML = '<ul class="list-disc list-inside">' + 
        errors.map(error => `<li>${error}</li>`).join('') + 
        '</ul>';
    errorContainer.style.display = 'block';
    
    // Scroll to errors
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Create error container
function createErrorContainer() {
    const container = document.createElement('div');
    container.id = 'form-errors';
    container.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
    container.style.display = 'none';
    
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(container, form.firstChild);
    }
    
    return container;
}

// Initialize contact page
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', validateContactForm);
    }
    
    // Character counter for message textarea
    const messageTextarea = document.querySelector('textarea[name="message"]');
    if (messageTextarea) {
        const maxLength = messageTextarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'text-sm text-gray-600 mt-1';
            messageTextarea.parentNode.appendChild(counter);
            
            function updateCounter() {
                const remaining = maxLength - messageTextarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                counter.className = remaining < 50 ? 'text-sm text-red-600 mt-1' : 'text-sm text-gray-600 mt-1';
            }
            
            messageTextarea.addEventListener('input', updateCounter);
            updateCounter();
        }
    }
});

