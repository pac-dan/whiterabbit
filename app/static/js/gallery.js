/**
 * Gallery and Video Detail Page JavaScript
 * Handles video interactions, likes, sharing
 */

// Like a video
function likeVideo(videoId) {
    fetch(`/api/video/${videoId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const likeCountElement = document.getElementById('like-count');
            const sidebarLikesElement = document.getElementById('sidebar-likes');
            
            if (likeCountElement) likeCountElement.textContent = data.like_count;
            if (sidebarLikesElement) sidebarLikesElement.textContent = data.like_count;
            
            // Show animation
            const button = event.target.closest('button');
            if (button) {
                button.classList.add('scale-110');
                setTimeout(() => button.classList.remove('scale-110'), 200);
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Copy current page link to clipboard
function copyLink() {
    navigator.clipboard.writeText(window.location.href)
        .then(() => {
            alert('Link copied to clipboard!');
        })
        .catch(err => {
            console.error('Failed to copy link:', err);
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = window.location.href;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('Link copied to clipboard!');
        });
}

// Toggle chat widget
function toggleChat() {
    // Check if chat toggle exists (for Retell voice widget or other chat systems)
    const chatToggle = document.getElementById('chat-toggle') || 
                      document.querySelector('[data-retell-widget]') ||
                      document.querySelector('.voice-widget-button');
    
    if (chatToggle) {
        chatToggle.click();
    } else {
        // If no chat widget, redirect to contact page
        window.location.href = '/contact';
    }
}

// Navigate to video detail page
function goToVideo(videoId) {
    window.location.href = `/gallery/${videoId}`;
}

// Navigate to package detail page
function goToPackage(packageId) {
    window.location.href = `/packages/${packageId}`;
}

// Initialize gallery grid interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers to video cards that don't have explicit onclick
    const videoCards = document.querySelectorAll('[data-video-id]');
    videoCards.forEach(card => {
        if (!card.onclick) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function() {
                const videoId = this.getAttribute('data-video-id');
                goToVideo(videoId);
            });
        }
    });
});

