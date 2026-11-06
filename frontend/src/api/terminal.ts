import axios from 'axios';
import { API_BASE, TERMINAL_KEY } from '../config';

// Отдельный клиент для терминала: авторизация по ключу, без логина сотрудника
const terminalClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'x-terminal-key': TERMINAL_KEY,
    'Content-Type': 'application/json'
  }
});

export interface WasteCreatePayload {
  product_id: number;
  reason_id: number;
  restaurant_id: number;
  quantity: number;
  created_at?: string;
}

export const terminalApi = {
  getProducts: async () => {
    const res = await terminalClient.get('/products/', { params: { status: 'active' } });
    return res.data;
  },

  getReasons: async () => {
    const res = await terminalClient.get('/reasons/');
    return res.data;
  },

  getGrid: async (restaurantId: number, date: string) => {
    const res = await terminalClient.get('/waste/grid', { params: { restaurant_id: restaurantId, date } });
    return res.data;
  },

  createWaste: async (data: WasteCreatePayload) => {
    const res = await terminalClient.post('/waste/', data);
    return res.data;
  },

  updateWaste: async (recordId: number, quantity: number) => {
    const res = await terminalClient.patch(`/waste/${recordId}`, { quantity });
    return res.data;
  },

  deleteWaste: async (recordId: number) => {
    const res = await terminalClient.delete(`/waste/${recordId}`);
    return res.data;
  }
};
