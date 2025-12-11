/**
 * Homepage JavaScript
 * Handles video carousel (Swiper) initialization and FAQ accordion
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Video Carousel
    if (typeof Swiper !== 'undefined' && document.querySelector('.videoSwiper')) {
        const videoSwiper = new Swiper('.videoSwiper', {
            slidesPerView: 1,
            spaceBetween: 30,
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
                pauseOnMouseEnter: true,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
                dynamicBullets: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            breakpoints: {
                640: {
                    slidesPerView: 2,
                    spaceBetween: 20,
                },
                1024: {
                    slidesPerView: 3,
                    spaceBetween: 30,
                },
            },
        });
    }
});

// FAQ Toggle function
function toggleFAQ(button) {
    const content = button.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (content && icon) {
        // Toggle content
        content.classList.toggle('hidden');
        
        // Rotate icon
        icon.classList.toggle('rotate-180');
    }
}

