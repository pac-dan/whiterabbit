/**
 * Waiver Page JavaScript
 * Handles waiver scroll tracking and form validation
 * Works for both booking-linked and standalone waivers
 */

document.addEventListener('DOMContentLoaded', function() {
    const waiverContainer = document.getElementById('waiver-text-container');
    const scrollIndicator = document.getElementById('scroll-indicator');
    const agreementCheckbox = document.getElementById('agreement');
    const legalNameInput = document.getElementById('legal_name');
    const submitBtn = document.getElementById('submit-btn');
    const formStatus = document.getElementById('form-status');
    
    // For standalone waiver
    const clientNameInput = document.getElementById('client_name');
    const clientEmailInput = document.getElementById('client_email');
    
    // Check if this is a standalone waiver (has client name/email fields)
    const isStandalone = clientNameInput !== null && clientEmailInput !== null;
    
    let hasScrolledToBottom = false;
    
    // Update submit button state
    function updateSubmitButton() {
        if (!submitBtn) return;
        
        const isAgreed = agreementCheckbox && agreementCheckbox.checked;
        const hasName = legalNameInput && legalNameInput.value.trim().length >= 3;
        
        let allValid = hasScrolledToBottom && isAgreed && hasName;
        
        // For standalone waiver, also check client name and email
        if (isStandalone) {
            const hasClientName = clientNameInput.value.trim().length >= 2;
            const hasEmail = clientEmailInput.value.includes('@');
            allValid = allValid && hasClientName && hasEmail;
        }
        
        if (allValid) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
            submitBtn.classList.add('bg-[#00D4FF]', 'hover:bg-[#00B8E6]', 'cursor-pointer');
            if (formStatus) {
                formStatus.innerHTML = '<i class="fas fa-check-circle mr-1 text-green-500"></i> Ready to sign';
                formStatus.classList.remove('text-gray-500');
                formStatus.classList.add('text-green-600');
            }
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.add('bg-gray-400', 'cursor-not-allowed');
            submitBtn.classList.remove('bg-[#00D4FF]', 'hover:bg-[#00B8E6]', 'cursor-pointer');
            
            if (formStatus) {
                if (!hasScrolledToBottom) {
                    formStatus.innerHTML = '<i class="fas fa-lock mr-1"></i> Please read the entire waiver to enable signing';
                } else if (!isAgreed) {
                    formStatus.innerHTML = '<i class="fas fa-exclamation-circle mr-1"></i> Please check the agreement box';
                } else if (!hasName) {
                    formStatus.innerHTML = '<i class="fas fa-exclamation-circle mr-1"></i> Please enter your full legal name';
                } else {
                    formStatus.innerHTML = '<i class="fas fa-exclamation-circle mr-1"></i> Please fill in all required fields';
                }
                formStatus.classList.add('text-gray-500');
                formStatus.classList.remove('text-green-600');
            }
        }
    }
    
    // Check if user has scrolled to bottom of waiver
    if (waiverContainer) {
        waiverContainer.addEventListener('scroll', function() {
            const scrollTop = waiverContainer.scrollTop;
            const scrollHeight = waiverContainer.scrollHeight;
            const clientHeight = waiverContainer.clientHeight;
            
            // Consider "bottom" when within 50px of actual bottom
            if (scrollTop + clientHeight >= scrollHeight - 50) {
                hasScrolledToBottom = true;
                
                if (scrollIndicator) {
                    scrollIndicator.innerHTML = '<p class="text-sm text-green-600 font-medium"><i class="fas fa-check-circle mr-2"></i>You have read the entire waiver</p>';
                    scrollIndicator.classList.remove('bg-[#00D4FF]/10');
                    scrollIndicator.classList.add('bg-green-50');
                }
                
                // Enable form elements
                if (agreementCheckbox) agreementCheckbox.disabled = false;
                if (legalNameInput) legalNameInput.disabled = false;
                if (clientNameInput) clientNameInput.disabled = false;
                if (clientEmailInput) clientEmailInput.disabled = false;
                
                updateSubmitButton();
            }
        });
        
        // Auto-scroll indicator for short content
        if (waiverContainer.scrollHeight <= waiverContainer.clientHeight + 100) {
            hasScrolledToBottom = true;
            if (scrollIndicator) scrollIndicator.style.display = 'none';
            if (agreementCheckbox) agreementCheckbox.disabled = false;
            if (legalNameInput) legalNameInput.disabled = false;
            if (clientNameInput) clientNameInput.disabled = false;
            if (clientEmailInput) clientEmailInput.disabled = false;
        }
    }
    
    // Form validation listeners
    if (legalNameInput) {
        legalNameInput.addEventListener('input', updateSubmitButton);
    }
    
    if (agreementCheckbox) {
        agreementCheckbox.addEventListener('change', updateSubmitButton);
    }
    
    if (clientNameInput) {
        clientNameInput.addEventListener('input', updateSubmitButton);
    }
    
    if (clientEmailInput) {
        clientEmailInput.addEventListener('input', updateSubmitButton);
    }
    
    // Initial state
    updateSubmitButton();
});
