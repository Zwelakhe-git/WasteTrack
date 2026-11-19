// Настройки фронтенда. Значения можно переопределить в frontend/.env (см. .env.example).
export const API_BASE: string = import.meta.env.VITE_API_URL ?? 'http://localhost:3020/api';

// Ключ терминала кухни — должен совпадать с TERMINAL_API_KEY в backend/.env
export const TERMINAL_KEY: string = import.meta.env.VITE_TERMINAL_KEY ?? '424b6b4c-7470-47d0-9077-739ea8e19626';

// Ресторан, к которому привязан этот терминал
export const RESTAURANT_ID: number = Number(import.meta.env.VITE_RESTAURANT_ID ?? 1);
