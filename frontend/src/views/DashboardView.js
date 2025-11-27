// Vista del Dashboard (MVC - View)
import { authController } from '../controllers/AuthController.js';
import { salesController } from '../controllers/SalesController.js';

export class DashboardView {
    constructor() {
        this.authController = authController;
        this.salesController = salesController;
        this.currentUser = this.authController.getCurrentUser();
        this.initializeElements();
    }

    initializeElements() {
        this.dashboardSection = document.getElementById('dashboard');
        this.userNameElement = document.getElementById('userName');
        this.userRoleElement = document.getElementById('userRole');
    }

    async render() {
        if (!this.dashboardSection) return;

        const stats = await this.salesController.getEstadisticas();
        const user = this.currentUser;

        this.dashboardSection.innerHTML = this.generateDashboardHTML(user, stats);
        this.attachEventListeners();
        lucide.createIcons();
    }

    generateDashboardHTML(user, stats) {
        const isAdmin = user.rol === 'admin';
        const isCajero = user.rol === 'cajero';

        if (isAdmin) {
            return this.generateAdminDashboard(user, stats);
        } else if (isCajero) {
            return this.generateCajeroDashboard(user, stats);
        } else {
            return this.generateDefaultDashboard(user, stats);
        }
    }

    generateAdminDashboard(user, stats) {
        return `
            <div class="dashboard-header">
                <h2>Panel de Administracion</h2>
                <p>Vision completa del sistema</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="trending-up"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Ingresos del Dia</h3>
                        <div class="stat-value">$${stats?.totalIngresos || 0}</div>
                        <div class="stat-trend positive">
                            <i data-lucide="arrow-up-right"></i>
                            +12% vs ayer
                        </div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="shopping-cart"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Ventas Hoy</h3>
                        <div class="stat-value">${stats?.totalVentas || 0}</div>
                        <div class="stat-trend positive">
                            <i data-lucide="arrow-up-right"></i>
                            +8% vs ayer
                        </div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="package"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Stock Bajo</h3>
                        <div class="stat-value">15</div>
                        <div class="stat-trend negative">
                            <i data-lucide="alert-triangle"></i>
                            Revisar
                        </div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="users"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Usuarios Activos</h3>
                        <div class="stat-value">4</div>
                        <div class="stat-trend">En sistema</div>
                    </div>
                </div>
            </div>

            <div class="dashboard-actions">
                <button class="action-button primary" onclick="app.navigateTo('ventas')">
                    <i data-lucide="plus-circle"></i>
                    Nueva Venta
                </button>
                <button class="action-button" onclick="app.navigateTo('inventario')">
                    <i data-lucide="package"></i>
                    Gestionar Inventario
                </button>
                <button class="action-button" onclick="app.navigateTo('reportes')">
                    <i data-lucide="bar-chart-3"></i>
                    Ver Reportes
                </button>
            </div>
        `;
    }

    generateCajeroDashboard(user, stats) {
        return `
            <div class="dashboard-header">
                <h2>Punto de Venta</h2>
                <p>Turno activo - ${user.nombre}</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card highlight">
                    <div class="stat-icon">
                        <i data-lucide="dollar-sign"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Ventas del Turno</h3>
                        <div class="stat-value">$${stats?.totalIngresos || 0}</div>
                        <div class="stat-trend">Total acumulado</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="shopping-cart"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Transacciones</h3>
                        <div class="stat-value">${stats?.totalVentas || 0}</div>
                        <div class="stat-trend">Hoy</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="clock"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Turno Activo</h3>
                        <div class="stat-value">4:30</div>
                        <div class="stat-trend">Horas</div>
                    </div>
                </div>
            </div>

            <div class="dashboard-actions">
                <button class="action-button primary" onclick="app.navigateTo('ventas')">
                    <i data-lucide="plus-circle"></i>
                    Nueva Venta
                </button>
                <button class="action-button" onclick="salesController.openQuickSale()">
                    <i data-lucide="bolt"></i>
                    Venta Rapida
                </button>
            </div>
        `;
    }

    generateDefaultDashboard(user, stats) {
        return `
            <div class="dashboard-header">
                <h2>Dashboard</h2>
                <p>Bienvenido ${user.nombre}</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="shopping-cart"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Ventas Hoy</h3>
                        <div class="stat-value">${stats?.totalVentas || 0}</div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon">
                        <i data-lucide="dollar-sign"></i>
                    </div>
                    <div class="stat-content">
                        <h3>Ingresos</h3>
                        <div class="stat-value">$${stats?.totalIngresos || 0}</div>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Event listeners especificos del dashboard
    }

    updateUserInfo() {
        if (this.userNameElement) {
            this.userNameElement.textContent = this.currentUser.nombre;
        }
        if (this.userRoleElement) {
            this.userRoleElement.textContent = this.currentUser.rol;
        }
    }
}