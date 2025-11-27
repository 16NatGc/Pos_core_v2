// Servicio de Autenticacion (GOF - Facade)
import { apiService } from './ApiService.js';
import { UserModel } from '../models/UserModel.js';

export class AuthService {
    async login(credentials) {
        const response = await apiService.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        if (response && response.token) {
            apiService.setToken(response.token);
            localStorage.setItem('pos_user', JSON.stringify(response.user));
            return new UserModel(response.user);
        }
        
        return null;
    }

    async logout() {
        try {
            await apiService.request('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            apiService.clearAuth();
        }
    }

    async verifyToken() {
        try {
            const response = await apiService.request('/auth/verify');
            return response.valid;
        } catch (error) {
            return false;
        }
    }

    getCurrentUser() {
        const userData = localStorage.getItem('pos_user');
        return userData ? new UserModel(JSON.parse(userData)) : null;
    }

    isAuthenticated() {
        return !!localStorage.getItem('pos_token') && !!this.getCurrentUser();
    }

    hasRole(requiredRole) {
        const user = this.getCurrentUser();
        return user && user.rol === requiredRole;
    }

    isAdmin() {
        return this.hasRole('admin');
    }

    isCajero() {
        return this.hasRole('cajero');
    }
}

export const authService = new AuthService();