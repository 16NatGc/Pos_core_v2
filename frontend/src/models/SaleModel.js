// Modelo de Venta (MVC - Model)
export class SaleModel {
    constructor(data = {}) {
        this.id = data.id || '';
        this.fecha = data.fecha || new Date();
        this.total = data.total || 0;
        this.metodo_pago = data.metodo_pago || 'efectivo';
        this.estado = data.estado || 'completada';
        this.usuario_id = data.usuario_id || '';
        this.productos = data.productos || [];
    }

    addProducto(producto, cantidad) {
        const subtotal = producto.precio * cantidad;
        this.productos.push({
            producto_id: producto.id,
            nombre: producto.nombre,
            cantidad: cantidad,
            precio_unitario: producto.precio,
            subtotal: subtotal
        });
        this.calculateTotal();
    }

    calculateTotal() {
        this.total = this.productos.reduce((sum, item) => sum + item.subtotal, 0);
    }

    validate() {
        if (this.productos.length === 0) {
            throw new Error('La venta debe tener al menos un producto');
        }
        return true;
    }

    toJSON() {
        return {
            productos: this.productos,
            total: this.total,
            metodo_pago: this.metodo_pago,
            usuario_id: this.usuario_id
        };
    }
}
