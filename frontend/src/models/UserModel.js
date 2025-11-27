// Modelo de Usuario (MVC - Model)
export class UserModel {
    constructor(data = {}) {
        this.id = data.id || '';
        this.nombre = data.nombre || '';
        this.usuario = data.usuario || '';
        this.rol = data.rol || '';
        this.email = data.email || '';
        this.activo = data.activo || true;
    }

    validate() {
        if (!this.usuario || !this.email) {
            throw new Error('Usuario y email son requeridos');
        }
        return true;
    }

    toJSON() {
        return {
            id: this.id,
            nombre: this.nombre,
            usuario: this.usuario,
            rol: this.rol,
            email: this.email,
            activo: this.activo
        };
    }
}