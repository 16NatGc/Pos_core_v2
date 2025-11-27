// Servicio de Productos (GOF - Facade)
import { apiService } from './ApiService.js';
import { ProductModel } from '../models/ProductModel.js';

export class ProductService {
    async getProductos() {
        const response = await apiService.request('/products');
        return response.map(productData => new ProductModel(productData));
    }

    async getProductoById(id) {
        const response = await apiService.request(`/products/${id}`);
        return new ProductModel(response);
    }

    async createProducto(productoData) {
        const producto = new ProductModel(productoData);
        producto.validate();
        
        const response = await apiService.request('/products', {
            method: 'POST',
            body: JSON.stringify(producto.toJSON())
        });
        
        return new ProductModel(response);
    }

    async updateProducto(id, productoData) {
        const producto = new ProductModel(productoData);
        producto.validate();
        
        const response = await apiService.request(`/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(producto.toJSON())
        });
        
        return new ProductModel(response);
    }

    async deleteProducto(id) {
        const response = await apiService.request(`/products/${id}`, {
            method: 'DELETE'
        });
        
        return response;
    }

    async updateStock(id, nuevoStock) {
        const response = await apiService.request(`/inventory/product/${id}/stock`, {
            method: 'PATCH',
            body: JSON.stringify({ stock: nuevoStock })
        });
        
        return response;
    }

    async searchProductos(query) {
        const productos = await this.getProductos();
        return productos.filter(producto => 
            producto.nombre.toLowerCase().includes(query.toLowerCase()) ||
            producto.categoria.toLowerCase().includes(query.toLowerCase()) ||
            producto.sku.toLowerCase().includes(query.toLowerCase())
        );
    }
}

export const productService = new ProductService();