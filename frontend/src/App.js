// Aplicacion Principal (GOF - Singleton)
import { authController } from './controllers/AuthController.js';
import { LoginView } from './views/LoginView.js';
import { DashboardView } from './views/DashboardView.js';

class PosCoreApp {
    constructor() {
        if (PosCoreApp.instance) {
            return PosCoreApp.instance;
        }
        PosCoreApp.instance = this;
        
        this.authController = authController;
        this.currentView = null;
        this.initialize();
    }

    async initialize() {
        // Verificar autenticacion
        if (!this.authController.checkAuth()) {
            return;
        }

        // Inicializar la aplicacion
        this.setupNavigation();
        this.setupEventListeners();
        this.loadCurrentView();
    }

    setupNavigation() {
        // Configurar navegacion SPA
        document.addEventListener('click', (e) => {
            const navButton = e.target.closest('[data-section]');
            if (navButton) {
                e.preventDefault();
                const section = navButton.dataset.section;
                this.navigateTo(section);
            }
        });
    }

    setupEventListeners() {
        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.authController.logout();
            });
        }

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }

    async loadCurrentView() {
        const path = window.location.pathname;
        
        if (path.includes('login.html')) {
            this.currentView = new LoginView();
        } else if (path.includes('index.html') || path === '/') {
            const dashboardView = new DashboardView();
            await dashboardView.render();
            this.currentView = dashboardView;
        }
    }

    navigateTo(section) {
        // Ocultar todas las secciones
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Mostrar seccion seleccionada
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Actualizar navegacion activa
        document.querySelectorAll('.nav-button').forEach(button => {
            button.classList.remove('active');
        });
        
        const activeButton = document.querySelector(`[data-section="${section}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    showNotification(message, type = 'info') {
        // Implementar sistema de notificaciones
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i data-lucide="${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        lucide.createIcons();
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'x-circle', 
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || 'info';
    }
}

// Inicializar aplicacion
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PosCoreApp();
});

export default PosCoreApp;