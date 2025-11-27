// Controlador de Productos (MVC - Controller)
import { productService } from '../services/ProductService.js';

export class ProductController {
    constructor() {
        this.productService = productService;
        this.productos = [];
        this.filtro = '';
    }

    async loadProductos() {
        try {
            this.productos = await this.productService.getProductos();
            this.onProductosLoaded(this.productos);
            return this.productos;
        } catch (error) {
            this.onError('Error al cargar productos: ' + error.message);
            return [];
        }
    }

    async createProducto(productoData) {
        try {
            const nuevoProducto = await this.productService.createProducto(productoData);
            this.productos.push(nuevoProducto);
            this.onProductoCreated(nuevoProducto);
            return { success: true, producto: nuevoProducto };
        } catch (error) {
            this.onError('Error al crear producto: ' + error.message);
            return { success: false, message: error.message };
        }
    }

    async updateProducto(id, productoData) {
        try {
            const productoActualizado = await this.productService.updateProducto(id, productoData);
            const index = this.productos.findIndex(p => p.id === id);
            if (index !== -1) {
                this.productos[index] = productoActualizado;
            }
            this.onProductoUpdated(productoActualizado);
            return { success: true, producto: productoActualizado };
        } catch (error) {
            this.onError('Error al actualizar producto: ' + error.message);
            return { success: false, message: error.message };
        }
    }

    async deleteProducto(id) {
        try {
            await this.productService.deleteProducto(id);
            this.productos = this.productos.filter(p => p.id !== id);
            this.onProductoDeleted(id);
            return { success: true };
        } catch (error) {
            this.onError('Error al eliminar producto: ' + error.message);
            return { success: false, message: error.message };
        }
    }

    async searchProductos(query) {
        this.filtro = query;
        const productosFiltrados = await this.productService.searchProductos(query);
        this.onProductosFiltered(productosFiltrados);
        return productosFiltrados;
    }

    getProductosBajoStock() {
        return this.productos.filter(p => p.stock <= p.stock_minimo);
    }

    // Event handlers (seran sobreescritos por las vistas)
    onProductosLoaded(productos) {}
    onProductoCreated(producto) {}
    onProductoUpdated(producto) {}
    onProductoDeleted(id) {}
    onProductosFiltered(productos) {}
    onError(message) {}
}

export const productController = new ProductController();