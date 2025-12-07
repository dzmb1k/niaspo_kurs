const API_URL = '/api';
let token = localStorage.getItem('token');
let currentUser = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        verifyToken();
    }

    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('ticket-form').addEventListener('submit', handleTicketPurchase);
});

function showMessage(text, type = 'info') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';

    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 4000);
}

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.querySelectorAll('.tab-btn')[1].classList.remove('active');
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    document.querySelectorAll('.tab-btn')[0].classList.remove('active');
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
}

async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Регистрация успешна! Теперь войдите в систему', 'success');
            showLogin();
        } else {
            showMessage(data.error || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        showMessage('Ошибка связи с сервером', 'error');
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            token = data.token;
            currentUser = { id: data.user_id, username: data.username };
            localStorage.setItem('token', token);
            showApp();
            showMessage('Вход выполнен успешно!', 'success');
        } else {
            showMessage(data.error || 'Неверные учетные данные', 'error');
        }
    } catch (error) {
        showMessage('Ошибка связи с сервером', 'error');
    }
}

async function verifyToken() {
    try {
        const response = await fetch(`${API_URL}/verify`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = { id: data.user_id };
            showApp();
        } else {
            logout();
        }
    } catch (error) {
        logout();
    }
}

function showApp() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('app-section').style.display = 'block';
    document.getElementById('user-menu').style.display = 'flex';

    if (currentUser) {
        document.getElementById('username-display').textContent = currentUser.username || 'User';
    }

    loadTickets();
    loadPayments();
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');

    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('app-section').style.display = 'none';
    document.getElementById('user-menu').style.display = 'none';
}

async function handleTicketPurchase(e) {
    e.preventDefault();

    const ticketType = document.getElementById('ticket-type').value;
    const route = document.getElementById('ticket-route').value;
    const paymentMethod = document.getElementById('payment-method').value;

    try {
        // Create ticket
        const ticketResponse = await fetch(`${API_URL}/tickets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ ticket_type: ticketType, route })
        });

        const ticketData = await ticketResponse.json();

        if (!ticketResponse.ok) {
            showMessage(ticketData.error || 'Ошибка создания билета', 'error');
            return;
        }

        // Process payment
        const paymentResponse = await fetch(`${API_URL}/payments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                ticket_id: ticketData.id,
                payment_method: paymentMethod
            })
        });

        const paymentData = await paymentResponse.json();

        if (paymentResponse.ok) {
            showMessage('Билет успешно приобретен!', 'success');
            loadTickets();
            loadPayments();
        } else {
            showMessage('Ошибка оплаты. Попробуйте еще раз', 'error');
        }
    } catch (error) {
        showMessage('Ошибка связи с сервером', 'error');
    }
}

async function loadTickets() {
    try {
        const response = await fetch(`${API_URL}/tickets`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const tickets = await response.json();
        const container = document.getElementById('tickets-list');

        if (!response.ok || tickets.length === 0) {
            container.innerHTML = '<p class="empty-state">У вас пока нет билетов</p>';
            return;
        }

        container.innerHTML = tickets.map(ticket => `
            <div class="ticket-card ${ticket.status}">
                <div class="ticket-type">${getTicketTypeName(ticket.ticket_type)}</div>
                <div class="ticket-route">📍 ${ticket.route}</div>
                <div class="ticket-price">${ticket.price}₽</div>
                <span class="ticket-status status-${ticket.status}">
                    ${getStatusName(ticket.status)}
                </span>
                <div class="ticket-dates">
                    ${new Date(ticket.created_at).toLocaleDateString('ru-RU')}
                    ${ticket.valid_until ? '→ ' + new Date(ticket.valid_until).toLocaleDateString('ru-RU') : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading tickets:', error);
    }
}

async function loadPayments() {
    try {
        const response = await fetch(`${API_URL}/payments`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const payments = await response.json();
        const container = document.getElementById('payments-list');

        if (!response.ok || payments.length === 0) {
            container.innerHTML = '<p class="empty-state">История платежей пуста</p>';
            return;
        }

        container.innerHTML = payments.map(payment => `
            <div class="payment-item ${payment.status}">
                <div class="payment-info">
                    <div class="payment-amount">${payment.amount}₽</div>
                    <div class="payment-method">${getPaymentMethodName(payment.payment_method)}</div>
                    <div class="payment-date">${new Date(payment.created_at).toLocaleString('ru-RU')}</div>
                </div>
                <span class="ticket-status status-${payment.status}">
                    ${getStatusName(payment.status)}
                </span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading payments:', error);
    }
}

function getTicketTypeName(type) {
    const names = {
        'single': 'Разовый билет',
        'daily': 'Дневной проездной',
        'weekly': 'Недельный проездной',
        'monthly': 'Месячный проездной'
    };
    return names[type] || type;
}

function getPaymentMethodName(method) {
    const names = {
        'card': 'Банковская карта',
        'apple_pay': 'Apple Pay',
        'google_pay': 'Google Pay'
    };
    return names[method] || method;
}

function getStatusName(status) {
    const names = {
        'active': 'Активен',
        'used': 'Использован',
        'pending': 'Ожидает оплаты',
        'expired': 'Истек',
        'completed': 'Завершена',
        'failed': 'Ошибка',
        'cancelled': 'Отменен'
    };
    return names[status] || status;
}
