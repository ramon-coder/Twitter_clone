// Main Application JavaScript for Subscription Management System

// API Base URL
const API_BASE = '';

// Authentication
let token = localStorage.getItem('token');
let currentUser = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

async function initApp() {
    if (token) {
        try {
            await loadCurrentUser();
            setupNavigation();
            navigateTo('dashboard');
        } catch (error) {
            logout();
        }
    } else {
        showLoginModal();
    }
}

// Authentication Functions
async function loadCurrentUser() {
    const response = await fetch(`${API_BASE}/users/me`, {
        headers: getAuthHeaders()
    });
    if (response.ok) {
        currentUser = await response.json();
        document.getElementById('userDropdown').innerHTML = `<i class="bi bi-person-circle"></i> ${currentUser.username}`;
    } else {
        throw new Error('Failed to load user');
    }
}

function getAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function login(username, password) {
    const response = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });
    
    if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        await loadCurrentUser();
        setupNavigation();
        navigateTo('dashboard');
        const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        modal.hide();
    } else {
        throw new Error('Invalid credentials');
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    showLoginModal();
}

// Navigation
function setupNavigation() {
    document.querySelectorAll('[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            navigateTo(page);
        });
    });
    
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
    
    document.getElementById('refreshBtn').addEventListener('click', function() {
        navigateTo(currentPage);
    });
}

let currentPage = 'dashboard';

async function navigateTo(page) {
    currentPage = page;
    document.getElementById('pageTitle').textContent = getPageTitle(page);
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    const content = document.getElementById('pageContent');
    content.innerHTML = '<div class="loading-spinner"><div class="spinner-border text-primary" role="status"></div></div>';
    
    try {
        switch (page) {
            case 'dashboard':
                await renderDashboard();
                break;
            case 'plans':
                await renderPlans();
                break;
            case 'subscriptions':
                await renderSubscriptions();
                break;
            case 'payments':
                await renderPayments();
                break;
            case 'profile':
                await renderProfile();
                break;
            case 'settings':
                await renderSettings();
                break;
        }
    } catch (error) {
        content.innerHTML = `<div class="alert alert-danger">Error loading page: ${error.message}</div>`;
    }
}

function getPageTitle(page) {
    const titles = {
        'dashboard': 'Dashboard',
        'plans': 'Planes de Suscripción',
        'subscriptions': 'Mis Suscripciones',
        'payments': 'Pagos',
        'profile': 'Mi Perfil',
        'settings': 'Configuración'
    };
    return titles[page] || 'Dashboard';
}

// Page Renderers
async function renderDashboard() {
    const response = await fetch(`${API_BASE}/subscriptions?status=active`, {
        headers: getAuthHeaders()
    });
    const subscriptions = await response.json();
    
    const paymentsResponse = await fetch(`${API_BASE}/payments`, {
        headers: getAuthHeaders()
    });
    const payments = await paymentsResponse.json();
    
    const totalSpent = payments.reduce((sum, p) => sum + (p.status === 'succeeded' ? p.amount : 0), 0);
    
    document.getElementById('pageContent').innerHTML = `
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-white bg-primary">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h5 class="card-title">Suscripciones Activas</h5>
                                <h2 class="mb-0">${subscriptions.length}</h2>
                            </div>
                            <i class="bi bi-collection" style="font-size: 2rem;"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h5 class="card-title">Total Pagado</h5>
                                <h2 class="mb-0">$${totalSpent.toFixed(2)}</h2>
                            </div>
                            <i class="bi bi-credit-card" style="font-size: 2rem;"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h5 class="card-title">Total Pagos</h5>
                                <h2 class="mb-0">${payments.length}</h2>
                            </div>
                            <i class="bi bi-receipt" style="font-size: 2rem;"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Suscripciones Recientes</h5>
            </div>
            <div class="card-body">
                ${subscriptions.length > 0 ? `
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Plan</th>
                                <th>Fecha Inicio</th>
                                <th>Fecha Fin</th>
                                <th>Renovación Auto.</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${subscriptions.slice(0, 5).map(sub => `
                                <tr>
                                    <td>Plan #${sub.plan_id}</td>
                                    <td>${new Date(sub.start_date).toLocaleDateString()}</td>
                                    <td>${new Date(sub.end_date).toLocaleDateString()}</td>
                                    <td><span class="badge bg-${sub.auto_renew ? 'success' : 'secondary'}">${sub.auto_renew ? 'Sí' : 'No'}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                ` : '<p class="text-muted">No hay suscripciones activas.</p>'}
            </div>
        </div>
    `;
}

async function renderPlans() {
    const response = await fetch(`${API_BASE}/plans`, {
        headers: getAuthHeaders()
    });
    const plans = await response.json();
    
    document.getElementById('pageContent').innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4>Planes Disponibles</h4>
            ${currentUser && currentUser.is_admin ? `
                <button class="btn btn-primary" onclick="showCreatePlanModal()">
                    <i class="bi bi-plus"></i> Nuevo Plan
                </button>
            ` : ''}
        </div>
        <div class="row">
            ${plans.map(plan => `
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0">${plan.name}</h5>
                        </div>
                        <div class="card-body">
                            <h3 class="text-primary">$${plan.price.toFixed(2)}</h3>
                            <p class="text-muted">${plan.duration} días</p>
                            <p>${plan.description || 'Sin descripción'}</p>
                            ${plan.features ? `<small class="text-muted">${plan.features}</small>` : ''}
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100" onclick="subscribeToPlan(${plan.id})">
                                Suscribirse
                            </button>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function subscribeToPlan(planId) {
    try {
        const response = await fetch(`${API_BASE}/subscriptions`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ plan_id: planId, auto_renew: true })
        });
        
        if (response.ok) {
            showAlert('Suscripción creada exitosamente', 'success');
            navigateTo('subscriptions');
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error al crear suscripción');
        }
    } catch (error) {
        showAlert(error.message, 'danger');
    }
}

function showCreatePlanModal() {
    showAlert('Funcionalidad de crear plan disponible en versión futura', 'info');
}

async function renderSubscriptions() {
    const response = await fetch(`${API_BASE}/subscriptions`, {
        headers: getAuthHeaders()
    });
    const subscriptions = await response.json();
    
    document.getElementById('pageContent').innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4>Mis Suscripciones</h4>
        </div>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Plan ID</th>
                        <th>Inicio</th>
                        <th>Fin</th>
                        <th>Estado</th>
                        <th>Auto-Renovar</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${subscriptions.map(sub => `
                        <tr>
                            <td>#${sub.id}</td>
                            <td>${sub.plan_id}</td>
                            <td>${new Date(sub.start_date).toLocaleDateString()}</td>
                            <td>${new Date(sub.end_date).toLocaleDateString()}</td>
                            <td><span class="badge bg-${getStatusColor(sub.status)}">${sub.status}</span></td>
                            <td><span class="badge bg-${sub.auto_renew ? 'success' : 'secondary'}">${sub.auto_renew ? 'Sí' : 'No'}</span></td>
                            <td>
                                ${sub.status === 'active' ? `
                                    <button class="btn btn-sm btn-outline-danger" onclick="cancelSubscription(${sub.id})">
                                        Cancelar
                                    </button>
                                ` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getStatusColor(status) {
    const colors = {
        'active': 'success',
        'cancelled': 'danger',
        'expired': 'secondary',
        'pending': 'warning'
    };
    return colors[status] || 'secondary';
}

async function cancelSubscription(subscriptionId) {
    if (!confirm('¿Estás seguro de cancelar esta suscripción?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/cancel`, {
            method: 'PUT',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            showAlert('Suscripción cancelada exitosamente', 'success');
            navigateTo('subscriptions');
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error al cancelar suscripción');
        }
    } catch (error) {
        showAlert(error.message, 'danger');
    }
}

async function renderPayments() {
    const response = await fetch(`${API_BASE}/payments`, {
        headers: getAuthHeaders()
    });
    const payments = await response.json();
    
    document.getElementById('pageContent').innerHTML = `
        <h4 class="mb-3">Historial de Pagos</h4>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Monto</th>
                        <th>Moneda</th>
                        <th>Estado</th>
                        <th>Método</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    ${payments.map(payment => `
                        <tr>
                            <td>#${payment.id}</td>
                            <td>$${payment.amount.toFixed(2)}</td>
                            <td>${payment.currency}</td>
                            <td><span class="badge bg-${getPaymentStatusColor(payment.status)}">${payment.status}</span></td>
                            <td>${payment.payment_method}</td>
                            <td>${new Date(payment.created_at).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getPaymentStatusColor(status) {
    const colors = {
        'succeeded': 'success',
        'pending': 'warning',
        'failed': 'danger',
        'refunded': 'info'
    };
    return colors[status] || 'secondary';
}

async function renderProfile() {
    document.getElementById('pageContent').innerHTML = `
        <h4 class="mb-3">Mi Perfil</h4>
        <div class="card">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Usuario:</strong> ${currentUser.username}</p>
                        <p><strong>Email:</strong> ${currentUser.email}</p>
                        <p><strong>Nombre:</strong> ${currentUser.full_name || '-'}</p>
                        <p><strong>Teléfono:</strong> ${currentUser.phone_number || '-'}</p>
                        <p><strong>Admin:</strong> ${currentUser.is_admin ? 'Sí' : 'No'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function renderSettings() {
    document.getElementById('pageContent').innerHTML = `
        <h4 class="mb-3">Configuración</h4>
        <div class="card">
            <div class="card-body">
                <h5>Cambiar Contraseña</h5>
                <form id="changePasswordForm">
                    <div class="mb-3">
                        <label class="form-label">Contraseña Actual</label>
                        <input type="password" class="form-control" id="currentPassword" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Nueva Contraseña</label>
                        <input type="password" class="form-control" id="newPassword" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Cambiar Contraseña</button>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('changePasswordForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        
        try {
            const response = await fetch(`${API_BASE}/change-password`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
            });
            
            if (response.ok) {
                showAlert('Contraseña cambiada exitosamente', 'success');
                this.reset();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Error al cambiar contraseña');
            }
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });
}

// Modal Functions
function showLoginModal() {
    const modalHtml = `
        <div class="modal fade" id="loginModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Iniciar Sesión</h5>
                    </div>
                    <div class="modal-body">
                        <form id="loginForm">
                            <div class="mb-3">
                                <label class="form-label">Usuario</label>
                                <input type="text" class="form-control" id="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Contraseña</label>
                                <input type="password" class="form-control" id="password" required>
                            </div>
                            <div id="loginError" class="alert alert-danger d-none"></div>
                            <button type="submit" class="btn btn-primary w-100">Entrar</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');
        
        try {
            await login(username, password);
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('d-none');
        }
    });
    
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const content = document.getElementById('pageContent');
    content.insertBefore(alertContainer, content.firstChild);
    
    setTimeout(() => {
        alertContainer.remove();
    }, 5000);
}