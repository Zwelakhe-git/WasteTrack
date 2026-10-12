#!/bin/bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install axios react-router-dom zustand
npm install -D @types/node

echo 'import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:3020",
        changeOrigin: true,
      },
    },
  },
});' > vite.config.ts

echo 'import axios from "axios";

export const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});' > src/api/client.ts

echo 'import { useEffect, useState } from "react";
import { apiClient } from "./api/client";

function App() {
  const [status, setStatus] = useState<string>("...");

  useEffect(() => {
    apiClient
      .get("/health")
      .then((res) => setStatus(res.data.status))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>WasteTrack</h1>
      <p>Backend status: {status}</p>
    </div>
  );
}

export default App;' > src/App.tsx