// Main JavaScript functions
// Main application JavaScript
console.log('Main JS loaded');

// Global functions for the application
window.ICUApp = {
    // API base URL
    apiBase: '/api',
    
    // Make API calls
    makeRequest: async function(endpoint, data = null) {
        try {
            const options = {
                method: data ? 'POST' : 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(this.apiBase + endpoint, options);
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            return { error: 'Request failed' };
        }
    },
    
    // Show notifications
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    },
    
    // Initialize common features
    init: function() {
        console.log('ICU App initialized');
        
        // Add click handlers for navigation
        document.querySelectorAll('[data-nav]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = this.getAttribute('data-nav');
            });
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    ICUApp.init();
});