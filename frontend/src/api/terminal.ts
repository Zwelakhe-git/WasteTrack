import axios from 'axios';

const API_BASE = "http://localhost:3020/api";
const TERMINAL_KEY = "secret_terminal_key"; // Должен совпадать с .env на бэкенде

// Отдельный клиент для терминала
const terminalClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'x-terminal-key': TERMINAL_KEY,
    'Content-Type': 'application/json'
  }
});

export const terminalApi = {
  // Получаем только активные продукты
  getProducts: async () => {
    const res = await terminalClient.get('/products/'); 
    return res.data;
  },
  
  getReasons: async () => {
    const res = await terminalClient.get('/reasons');
    return res.data;
  },

  createWaste: async (data: { product_id: number; reason_id: number; restaurant_id: number; quantity: number; comment?: string }) => {
    const res = await terminalClient.post('/waste/', data);
    return res.data;
  }
};