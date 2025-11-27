// Controlador de Autenticacion (MVC - Controller)
import { authService } from '../services/AuthService.js';

export class AuthController {
    constructor() {
        this.authService = authService;
    }

    async login(credentials) {
        try {
            const user = await this.authService.login(credentials);
            if (user) {
                this.onLoginSuccess(user);
                return { success: true, user };
            } else {
                return { success: false, message: 'Credenciales incorrectas' };
            }
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async logout() {
        await this.authService.logout();
        this.onLogout();
    }

    checkAuth() {
        if (!this.authService.isAuthenticated()) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }

    onLoginSuccess(user) {
        // Redirigir segun el rol
        setTimeout(() => {
            window.location.href = '/index.html';
        }, 1000);
    }

    onLogout() {
        window.location.href = '/login.html';
    }

    getCurrentUser() {
        return this.authService.getCurrentUser();
    }

    hasPermission(requiredRole) {
        return this.authService.hasRole(requiredRole);
    }
}

export const authController = new AuthController();