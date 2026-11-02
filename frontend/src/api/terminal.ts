import axios from 'axios';

const API_BASE = "http://localhost:3020/api";
const TERMINAL_KEY = "secret_terminal_key";

const terminalClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'x-terminal-key': TERMINAL_KEY,
    'Content-Type': 'application/json'
  }
});

export const terminalApi = {
  createWaste: async (data: { product_id: number; reason_id: number; restaurant_id: number; quantity: number; created_at?: string }) => {
    const res = await terminalClient.post('/waste/', data);
    return res.data;
  },
  
  // Добавили метод удаления
  deleteWaste: async (recordId: number) => {
    const res = await terminalClient.delete(`/waste/${recordId}`);
    return res.data;
  }
};