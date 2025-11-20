/**
 * Booking System JavaScript
 * Handles booking forms, payment processing, and calendar interactions
 */

// Initialize Stripe if available
let stripe = null;
if (typeof Stripe !== 'undefined' && window.STRIPE_PUBLISHABLE_KEY) {
    stripe = Stripe(window.STRIPE_PUBLISHABLE_KEY);
}

// Handle booking form submission
function handleBookingSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
    }
    
    return true; // Allow form to submit
}

// Handle payment form submission with Stripe
async function handlePaymentSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing Payment...';
    }
    
    try {
        // If using Stripe Elements, confirm the payment
        if (stripe && window.paymentIntentClientSecret) {
            const { error } = await stripe.confirmCardPayment(window.paymentIntentClientSecret);
            
            if (error) {
                showError(error.message);
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Complete Payment';
                }
            } else {
                // Payment successful, submit the form
                form.submit();
            }
        } else {
            // No Stripe or direct form submission
            form.submit();
        }
    } catch (error) {
        console.error('Payment error:', error);
        showError('An error occurred processing your payment. Please try again.');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = 'Complete Payment';
        }
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('payment-error') || createErrorDiv();
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Create error div if it doesn't exist
function createErrorDiv() {
    const errorDiv = document.createElement('div');
    errorDiv.id = 'payment-error';
    errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
    errorDiv.style.display = 'none';
    
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(errorDiv, form.firstChild);
    }
    
    return errorDiv;
}

// Set minimum booking date (24 hours from now)
function setMinimumBookingDate() {
    const bookingDateInput = document.getElementById('booking_date');
    if (bookingDateInput) {
        const now = new Date();
        now.setHours(now.getHours() + 24); // Add 24 hours
        
        // Format to datetime-local input format
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        bookingDateInput.min = minDateTime;
        
        // Set default to 48 hours from now (more convenient)
        const defaultDate = new Date();
        defaultDate.setHours(defaultDate.getHours() + 48);
        const defaultYear = defaultDate.getFullYear();
        const defaultMonth = String(defaultDate.getMonth() + 1).padStart(2, '0');
        const defaultDay = String(defaultDate.getDate()).padStart(2, '0');
        const defaultDateTime = `${defaultYear}-${defaultMonth}-${defaultDay}T10:00`;
        bookingDateInput.value = defaultDateTime;
    }
}

// Validate booking date on form submit
function validateBookingDate() {
    const bookingDateInput = document.getElementById('booking_date');
    if (!bookingDateInput || !bookingDateInput.value) {
        return true; // Let HTML5 validation handle required field
    }
    
    const selectedDate = new Date(bookingDateInput.value);
    const minDate = new Date();
    minDate.setHours(minDate.getHours() + 24);
    
    if (selectedDate < minDate) {
        alert('Booking date must be at least 24 hours in advance.');
        bookingDateInput.focus();
        return false;
    }
    
    // Check not more than 90 days in advance
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 90);
    
    if (selectedDate > maxDate) {
        alert('Bookings can only be made up to 90 days in advance.');
        bookingDateInput.focus();
        return false;
    }
    
    return true;
}

// Initialize booking page
document.addEventListener('DOMContentLoaded', function() {
    // Set minimum booking date
    setMinimumBookingDate();
    
    // Add form submit handlers
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            if (!validateBookingDate()) {
                e.preventDefault();
                return false;
            }
            return handleBookingSubmit(e);
        });
    }
    
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', handlePaymentSubmit);
    }
    
    // Initialize date picker if available
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        // Set min date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.min = tomorrow.toISOString().split('T')[0];
    }
});

