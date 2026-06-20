// app.js - Common Logic

async function logout() {
    try {
        const res = await fetch('/auth/logout', {
            method: 'POST'
        });
        if (res.ok) {
            window.location.reload();
        }
    } catch (e) {
        console.error('Logout failed', e);
    }
}

// Utility to format currency (VND không dùng số thập phân)
function formatCurrency(amount) {
    if (!amount || amount === 0) return 'Liên hệ';
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(amount);
}

// Utility to fetch API
async function apiGet(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error('API GET error:', e);
        return null;
    }
}

async function apiPost(url, data) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
        }
        return await res.json();
    } catch (e) {
        console.error('API POST error:', e);
        throw e;
    }
}
