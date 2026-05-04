// Admin Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Función para cargar contenido basado en el enlace seleccionado
    function loadPage(page) {
        const contentDiv = document.getElementById('pageContent');
        const titleDiv = document.getElementById('pageTitle');
        
        // Actualizar título
        titleDiv.textContent = page.charAt(0).toUpperCase() + page.slice(1) + ' - Panel de Administración';
        
        // Mostrar contenido según la página
        switch(page) {
            case 'dashboard':
                contentDiv.innerHTML = `
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <i class="bi bi-people text-primary"></i>
                                <h3>Usuarios Totales</h3>
                                <h2>1,234</h2>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <i class="bi bi-card-list text-success"></i>
                                <h3>Planes Activos</h3>
                                <h2>24</h2>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <i class="bi bi-collection text-info"></i>
                                <h3>Suscripciones Activas</h3>
                                <h2>5,678</h2>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <i class="bi bi-credit-card text-warning"></i>
                                <h3>Pagos Este Mes</h3>
                                <h2>$45,678</h2>
                            </div>
                        </div>
                    </div>
                `;
                break;
            case 'users':
                contentDiv.innerHTML = '<div class="alert alert-info">Gestión de Usuarios - En desarrollo</div>';
                break;
            case 'plans':
                contentDiv.innerHTML = '<div class="alert alert-info">Gestión de Planes - En desarrollo</div>';
                break;
            case 'subscriptions':
                contentDiv.innerHTML = '<div class="alert alert-info">Gestión de Suscripciones - En desarrollo</div>';
                break;
            case 'payments':
                contentDiv.innerHTML = '<div class="alert alert-info">Gestión de Pagos - En desarrollo</div>';
                break;
            case 'reports':
                contentDiv.innerHTML = '<div class="alert alert-info">Reportes - En desarrollo</div>';
                break;
            case 'settings':
                contentDiv.innerHTML = '<div class="alert alert-info">Configuración - En desarrollo</div>';
                break;
            default:
                contentDiv.innerHTML = '<div class="alert alert-warning">Página no encontrada</div>';
        }
    }

    // Manejar clics en el menú lateral
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover clase active de todos los enlaces
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            
            // Añadir clase active al enlace clickeado
            this.classList.add('active');
            
            // Cargar la página correspondiente
            const page = this.getAttribute('data-page');
            loadPage(page);
        });
    });

    // Manejar refresco
    document.getElementById('refreshBtn').addEventListener('click', function() {
        const activeLink = document.querySelector('.nav-link.active');
        if (activeLink) {
            const page = activeLink.getAttribute('data-page');
            loadPage(page);
        }
    });

    // Manejar cierre de sesión
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        // Aquí iría la lógica de cierre de sesión
        alert('Cerrando sesión...');
        // Redirigir a login o página principal
        window.location.href = '/';
    });

    // Cargar dashboard por defecto
    loadPage('dashboard');
});