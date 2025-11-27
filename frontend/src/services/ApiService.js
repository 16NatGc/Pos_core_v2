// Servicio de API (GOF - Facade Pattern)
class ApiService {
    constructor() {
        this.baseURL = window.API_BASE_URL || 'http://localhost:8000/api';
        this.token = localStorage.getItem('pos_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': this.token ? `Bearer ${this.token}` : ''
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                this.handleUnauthorized();
                throw new Error('Sesion expirada');
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `Error ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    handleUnauthorized() {
        localStorage.removeItem('pos_token');
        localStorage.removeItem('pos_user');
        window.location.href = '/login.html';
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('pos_token', token);
    }

    clearAuth() {
        this.token = null;
        localStorage.removeItem('pos_token');
        localStorage.removeItem('pos_user');
    }
}

// Singleton instance
export const apiService = new ApiService();