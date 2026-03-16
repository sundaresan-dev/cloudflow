// Register page functionality

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmPassword = document.getElementById('confirmPassword').value.trim();
    
    if (!name || !email || !password || !confirmPassword) {
        showAlert('Please fill in all fields', 'warning');
        return;
    }
    
    if (password !== confirmPassword) {
        showAlert('Passwords do not match', 'warning');
        return;
    }
    
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters', 'warning');
        return;
    }
    
    const result = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
            name,
            email,
            password,
            confirm_password: confirmPassword
        })
    });
    
    if (result.success) {
        showAlert('Registration successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = result.data.redirect;
        }, 1000);
    } else {
        showAlert(result.error || 'Registration failed', 'danger');
    }
}
