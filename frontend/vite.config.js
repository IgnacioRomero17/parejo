import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    // Sin changeOrigin: el Host queda igual que el Origin y el control CSRF de Django pasa.
    // Va como objeto porque la forma abreviada ("/api": "http://...") activa changeOrigin.
    proxy: {
      "/api": { target: "http://localhost:8000" },
    },
  },
  test: {
    environment: "jsdom",
    // Con globals, Testing Library desmonta los componentes después de cada test.
    globals: true,
  },
});
