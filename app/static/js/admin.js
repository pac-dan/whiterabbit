/**
 * Admin Dashboard JavaScript
 * Handles admin forms, confirmations, and AJAX operations
 */

// Confirm deletion
function confirmDelete(itemType, itemName) {
    return confirm(`Are you sure you want to delete this ${itemType}?\n\n${itemName || ''}\n\nThis action cannot be undone.`);
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Handle video form YouTube ID extraction
function extractYouTubeId() {
    const urlInput = document.getElementById('youtube_url');
    const idInput = document.getElementById('youtube_id');
    
    if (!urlInput || !idInput) return;
    
    const url = urlInput.value.trim();
    if (!url) return;
    
    // Extract YouTube ID from various URL formats
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
        /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
        /^([a-zA-Z0-9_-]{11})$/ // Direct ID
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
            idInput.value = match[1];
            
            // Show preview thumbnail
            const preview = document.getElementById('thumbnail-preview');
            if (preview) {
                preview.src = `https://img.youtube.com/vi/${match[1]}/hqdefault.jpg`;
                preview.style.display = 'block';
            }
            
            return;
        }
    }
    
    alert('Could not extract YouTube ID from URL. Please check the URL format.');
}

// Preview image before upload
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Toggle element visibility
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

// Auto-save draft (debounced)
let autoSaveTimeout;
function autoSaveDraft(formId) {
    clearTimeout(autoSaveTimeout);
    
    autoSaveTimeout = setTimeout(() => {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Save to localStorage
        localStorage.setItem(`draft_${formId}`, JSON.stringify(data));
        
        // Show save indicator
        const indicator = document.getElementById('save-indicator');
        if (indicator) {
            indicator.textContent = 'Draft saved';
            indicator.className = 'text-green-600 text-sm';
            setTimeout(() => {
                indicator.textContent = '';
            }, 2000);
        }
    }, 1000);
}

// Restore draft from localStorage
function restoreDraft(formId) {
    const draft = localStorage.getItem(`draft_${formId}`);
    if (!draft) return;
    
    try {
        const data = JSON.parse(draft);
        const form = document.getElementById(formId);
        if (!form) return;
        
        Object.keys(data).forEach(key => {
            const input = form.elements[key];
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = data[key] === 'on';
                } else {
                    input.value = data[key];
                }
            }
        });
        
        const restoreMessage = confirm('A draft was found. Would you like to restore it?');
        if (!restoreMessage) {
            localStorage.removeItem(`draft_${formId}`);
        }
    } catch (error) {
        console.error('Error restoring draft:', error);
    }
}

// Initialize admin page
document.addEventListener('DOMContentLoaded', function() {
    // Add confirmation to delete buttons
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const itemType = this.getAttribute('data-item-type') || 'item';
            const itemName = this.getAttribute('data-item-name') || '';
            
            if (!confirmDelete(itemType, itemName)) {
                e.preventDefault();
            }
        });
    });
    
    // Initialize YouTube ID extraction
    const youtubeUrlInput = document.getElementById('youtube_url');
    if (youtubeUrlInput) {
        youtubeUrlInput.addEventListener('blur', extractYouTubeId);
    }
    
    // Initialize image preview
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.getAttribute('data-preview');
            if (previewId) {
                previewImage(this, previewId);
            }
        });
    });
    
    // Auto-save functionality for long forms
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', () => autoSaveDraft(form.id));
        });
        
        // Try to restore draft on load
        restoreDraft(form.id);
    });
});

