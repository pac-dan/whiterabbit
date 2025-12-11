/**
 * Admin Waivers Page JavaScript
 * Handles waiver modal and copy functionality
 */

function copyWaiverLink() {
    const input = document.getElementById('waiver-link');
    if (input) {
        input.select();
        document.execCommand('copy');
        alert('Waiver link copied to clipboard!');
    }
}

function viewWaiverDetails(id, legalName, email, ip, userAgent, signedAt, version) {
    const modal = document.getElementById('waiver-modal');
    
    document.getElementById('modal-legal-name').textContent = legalName;
    document.getElementById('modal-email').textContent = email;
    document.getElementById('modal-ip').textContent = ip;
    document.getElementById('modal-user-agent').textContent = userAgent;
    document.getElementById('modal-signed-at').textContent = signedAt;
    document.getElementById('modal-version').textContent = 'v' + version;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeWaiverModal() {
    const modal = document.getElementById('waiver-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Close modal on backdrop click
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('waiver-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeWaiverModal();
            }
        });
    }
});

