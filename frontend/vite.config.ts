import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // BACKEND_URL — адрес бэкенда для прокси dev-сервера (из frontend/.env).
  // Браузер обращается к /api на том же адресе, что и фронтенд,
  // а Vite пересылает запрос на бэкенд: CORS при этом не нужен.
  const env = loadEnv(mode, process.cwd(), "");
  const backendUrl = env.BACKEND_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
        },
      },
    },
  };
});
