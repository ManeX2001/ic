// Dashboard JavaScript
// ICU Dashboard JavaScript
console.log('Dashboard loaded successfully');

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('ICU Dashboard initialized');
    
    // Update current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Initialize any dashboard features
    initializeDashboard();
});

function updateCurrentTime() {
    const now = new Date();
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = now.toLocaleString();
    }
}

function initializeDashboard() {
    // Dashboard initialization code
    console.log('Dashboard features initialized');
}

// Patient admission function
function admitPatient() {
    window.location.href = '/patient-form';
}

// View analytics function
function viewAnalytics() {
    window.location.href = '/analytics';
}