// Login page functionality

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!email || !password) {
        showAlert('Please fill in all fields', 'warning');
        return;
    }
    
    const result = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
            email,
            password
        })
    });
    
    if (result.success) {
        showAlert('Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = result.data.redirect;
        }, 1000);
    } else {
        showAlert(result.error || 'Login failed', 'danger');
    }
}
