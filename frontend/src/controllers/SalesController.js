// Controlador de Ventas (MVC - Controller)
import { salesService } from '../services/SalesService.js';
import { productService } from '../services/ProductService.js';
import { SaleModel } from '../models/SaleModel.js';

export class SalesController {
    constructor() {
        this.salesService = salesService;
        this.productService = productService;
        this.carrito = [];
        this.productos = [];
    }

    async initialize() {
        await this.loadProductos();
    }

    async loadProductos() {
        try {
            this.productos = await this.productService.getProductos();
            this.onProductosLoaded(this.productos);
        } catch (error) {
            this.onError('Error al cargar productos: ' + error.message);
        }
    }

    agregarAlCarrito(producto, cantidad = 1) {
        const itemExistente = this.carrito.find(item => item.producto.id === producto.id);
        
        if (itemExistente) {
            if (itemExistente.cantidad + cantidad > producto.stock) {
                this.onError('No hay suficiente stock disponible');
                return false;
            }
            itemExistente.cantidad += cantidad;
            itemExistente.subtotal = itemExistente.cantidad * producto.precio;
        } else {
            if (cantidad > producto.stock) {
                this.onError('No hay suficiente stock disponible');
                return false;
            }
            this.carrito.push({
                producto: producto,
                cantidad: cantidad,
                subtotal: cantidad * producto.precio
            });
        }
        
        this.calcularTotal();
        this.onCarritoUpdated(this.carrito, this.total);
        return true;
    }

    removerDelCarrito(productoId) {
        this.carrito = this.carrito.filter(item => item.producto.id !== productoId);
        this.calcularTotal();
        this.onCarritoUpdated(this.carrito, this.total);
    }

    actualizarCantidad(productoId, nuevaCantidad) {
        const item = this.carrito.find(item => item.producto.id === productoId);
        if (item && nuevaCantidad > 0 && nuevaCantidad <= item.producto.stock) {
            item.cantidad = nuevaCantidad;
            item.subtotal = nuevaCantidad * item.producto.precio;
            this.calcularTotal();
            this.onCarritoUpdated(this.carrito, this.total);
            return true;
        }
        return false;
    }

    calcularTotal() {
        this.total = this.carrito.reduce((sum, item) => sum + item.subtotal, 0);
    }

    limpiarCarrito() {
        this.carrito = [];
        this.total = 0;
        this.onCarritoUpdated(this.carrito, this.total);
    }

    async procesarVenta(metodoPago = 'efectivo') {
        if (this.carrito.length === 0) {
            this.onError('El carrito esta vacio');
            return { success: false };
        }

        try {
            const ventaData = {
                productos: this.carrito.map(item => ({
                    producto_id: item.producto.id,
                    cantidad: item.cantidad,
                    precio_unitario: item.producto.precio,
                    subtotal: item.subtotal
                })),
                total: this.total,
                metodo_pago: metodoPago
            };

            const venta = await this.salesService.createVenta(ventaData);
            
            // Actualizar stock localmente
            for (const item of this.carrito) {
                const productoIndex = this.productos.findIndex(p => p.id === item.producto.id);
                if (productoIndex !== -1) {
                    this.productos[productoIndex].stock -= item.cantidad;
                }
            }

            this.limpiarCarrito();
            this.onVentaProcesada(venta);
            return { success: true, venta };

        } catch (error) {
            this.onError('Error al procesar venta: ' + error.message);
            return { success: false, message: error.message };
        }
    }

    async getEstadisticas() {
        try {
            return await this.salesService.getEstadisticasVentas();
        } catch (error) {
            this.onError('Error al obtener estadisticas: ' + error.message);
            return null;
        }
    }

    // Event handlers
    onProductosLoaded(productos) {}
    onCarritoUpdated(carrito, total) {}
    onVentaProcesada(venta) {}
    onError(message) {}
}

export const salesController = new SalesController();