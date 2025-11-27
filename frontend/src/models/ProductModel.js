// Modelo de Producto (MVC - Model)
export class ProductModel {
    constructor(data = {}) {
        this.id = data.id || '';
        this.nombre = data.nombre || '';
        this.descripcion = data.descripcion || '';
        this.precio = data.precio || 0;
        this.stock = data.stock || 0;
        this.stock_minimo = data.stock_minimo || 5;
        this.categoria = data.categoria || '';
        this.proveedor = data.proveedor || '';
        this.sku = data.sku || '';
        this.activo = data.activo || true;
    }

    validate() {
        if (!this.nombre || this.precio <= 0) {
            throw new Error('Nombre y precio válido son requeridos');
        }
        return true;
    }

    toJSON() {
        return {
            id: this.id,
            nombre: this.nombre,
            descripcion: this.descripcion,
            precio: this.precio,
            stock: this.stock,
            stock_minimo: this.stock_minimo,
            categoria: this.categoria,
            proveedor: this.proveedor,
            sku: this.sku,
            activo: this.activo
        };
    }
}