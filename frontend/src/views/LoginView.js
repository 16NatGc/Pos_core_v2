// Vista de Login (MVC - View)
import { authController } from '../controllers/AuthController.js';

export class LoginView {
    constructor() {
        this.authController = authController;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.loginForm = document.getElementById('loginForm');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.loginButton = document.getElementById('loginButton');
        this.messageContainer = document.getElementById('messageContainer');
    }

    attachEventListeners() {
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }
    }

    async handleLogin() {
        const credentials = {
            username: this.usernameInput.value.trim(),
            password: this.passwordInput.value
        };

        if (!credentials.username || !credentials.password) {
            this.showMessage('Por favor completa todos los campos', 'error');
            return;
        }

        this.setLoading(true);
        
        const result = await this.authController.login(credentials);
        
        this.setLoading(false);

        if (result.success) {
            this.showMessage(`Bienvenido ${result.user.nombre}`, 'success');
        } else {
            this.showMessage(result.message, 'error');
        }
    }

    setLoading(loading) {
        if (this.loginButton) {
            this.loginButton.disabled = loading;
            this.loginButton.innerHTML = loading ? 
                'Iniciando sesion...' : 
                'Iniciar Sesion';
        }
    }

    showMessage(message, type) {
        if (this.messageContainer) {
            this.messageContainer.innerHTML = `
                <div class="message ${type}">
                    <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}"></i>
                    <span>${message}</span>
                </div>
            `;
            lucide.createIcons();
        }
    }
}