// Servicio de Ventas (GOF - Facade)
import { apiService } from './ApiService.js';
import { SaleModel } from '../models/SaleModel.js';

export class SalesService {
    async getVentas() {
        const response = await apiService.request('/sales');
        return response.map(ventaData => new SaleModel(ventaData));
    }

    async getVentaById(id) {
        const response = await apiService.request(`/sales/${id}`);
        return new SaleModel(response);
    }

    async createVenta(ventaData) {
        const venta = new SaleModel(ventaData);
        venta.validate();
        
        const response = await apiService.request('/sales', {
            method: 'POST',
            body: JSON.stringify(venta.toJSON())
        });
        
        return new SaleModel(response);
    }

    async getVentasHoy() {
        const response = await apiService.request('/sales/today');
        return response.map(ventaData => new SaleModel(ventaData));
    }

    async getEstadisticasVentas() {
        const ventasHoy = await this.getVentasHoy();
        
        return {
            totalVentas: ventasHoy.length,
            totalIngresos: ventasHoy.reduce((sum, venta) => sum + venta.total, 0),
            ventasPorHora: this.calcularVentasPorHora(ventasHoy),
            metodoPagoStats: this.calcularMetodoPagoStats(ventasHoy)
        };
    }

    calcularVentasPorHora(ventas) {
        const horas = Array.from({length: 12}, (_, i) => i + 8);
        return horas.map(hora => {
            const ventasHora = ventas.filter(venta => {
                const ventaHora = new Date(venta.fecha).getHours();
                return ventaHora === hora;
            });
            
            return {
                hora: `${hora}:00`,
                ventas: ventasHora.reduce((sum, v) => sum + v.total, 0),
                transacciones: ventasHora.length
            };
        });
    }

    calcularMetodoPagoStats(ventas) {
        const stats = {};
        ventas.forEach(venta => {
            stats[venta.metodo_pago] = (stats[venta.metodo_pago] || 0) + 1;
        });
        return stats;
    }
}

export const salesService = new SalesService();