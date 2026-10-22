import { create } from 'zustand';
import { apiClient } from '../api/client';

interface User {
  id: number;
  login: string;
  display_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  
  login: async (username, password) => {
    // FastAPI OAuth2 требует данные в формате x-www-form-urlencoded
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    localStorage.setItem('access_token', response.data.access_token);
    set({ isAuthenticated: true });
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, isAuthenticated: false });
  },
  
  fetchMe: async () => {
    try {
      const response = await apiClient.get('/auth/me');
      set({ user: response.data });
    } catch (error) {
      console.error("Failed to fetch user", error);
    }
  }
}));