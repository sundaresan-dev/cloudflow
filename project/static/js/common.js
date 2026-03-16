// Common utility functions

// Show alert notification
function showAlert(message, type = 'success', containerId = 'alertContainer') {
    const alertContainer = document.getElementById(containerId);
    if (!alertContainer) return;
    
    // Check if message contains HTML
    const isHTML = /<[a-z][\s\S]*>/i.test(message);
    
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}!</strong> 
            <div class="mt-2">${isHTML ? message : message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.innerHTML = alertHTML;
    
    // Auto dismiss after 8 seconds (longer for complex messages)
    const timeout = isHTML ? 10000 : 5000;
    setTimeout(() => {
        const alert = alertContainer.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, timeout);
}

// Make API request
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            return { success: false, error: data.message || 'Request failed', data: data };
        }
        
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Check if user is logged in
async function checkSession() {
    const result = await apiRequest('/auth/check-session');
    return result.data?.logged_in || false;
}

// Logout functionality
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const result = await apiRequest('/auth/logout', { method: 'POST' });
            if (result.success) {
                window.location.href = '/login';
            }
        });
    }
});
