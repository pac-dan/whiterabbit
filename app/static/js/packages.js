/**
 * Packages Page JavaScript
 * Handles package tab selection for Calendly widgets
 */

function selectPackage(pkg) {
    // Hide all calendly containers
    document.querySelectorAll('.calendly-container').forEach(el => el.classList.add('hidden'));
    
    // Reset all tabs
    document.querySelectorAll('.package-tab').forEach(tab => {
        tab.classList.remove('bg-[#00D4FF]', 'bg-[#8B5CF6]', 'bg-[#F59E0B]', 'text-white', 'shadow-lg');
        tab.classList.add('bg-gray-200', 'text-gray-700');
    });
    
    // Show selected calendly and style tab
    const activeTab = document.getElementById('tab-' + pkg);
    const calendlyContainer = document.getElementById('calendly-' + pkg);
    
    if (calendlyContainer) {
        calendlyContainer.classList.remove('hidden');
    }
    
    if (activeTab) {
        activeTab.classList.remove('bg-gray-200', 'text-gray-700');
        activeTab.classList.add('text-white', 'shadow-lg');
        
        if (pkg === 'basic') activeTab.classList.add('bg-[#00D4FF]');
        else if (pkg === 'pro') activeTab.classList.add('bg-[#8B5CF6]');
        else if (pkg === 'expert') activeTab.classList.add('bg-[#F59E0B]');
    }
}

// Auto-select package if coming from homepage
document.addEventListener('DOMContentLoaded', function() {
    const selectedPackage = localStorage.getItem('selectedPackage');
    if (selectedPackage) {
        selectPackage(selectedPackage);
        localStorage.removeItem('selectedPackage');
    }
});

