// Authentication utilities

async function getCurrentUser() {
    try {
        const response = await fetch('/auth/me');
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
    return null;
}

async function logout() {
    try {
        const response = await fetch('/auth/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error logging out:', error);
    }
}

// Form utilities

function showErrorMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = 'error-message';
    }
}

function showSuccessMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = 'success-message';
    }
}

function clearMessage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = '';
        element.className = 'message';
    }
}

// API utilities

async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        
        if (response.status === 401) {
            window.location.href = '/login';
            return { ok: false, error: 'Unauthorized' };
        }

        const result = await response.json();
        return { ok: response.ok, ...result };
    } catch (error) {
        console.error('API call error:', error);
        return { ok: false, error: 'An error occurred' };
    }
}

// Date utilities

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
