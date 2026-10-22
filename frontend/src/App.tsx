import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import CatalogsPage from './pages/CatalogsPage';


// Временные компоненты (создадим их ниже)
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TerminalPage from './pages/TerminalPage';

function App() {
  const { isAuthenticated, fetchMe, user } = useAuthStore();

  useEffect(() => {
    // Если токен есть, но данных юзера нет, запрашиваем их
    if (isAuthenticated && !user) {
      fetchMe();
    }
  }, [isAuthenticated, user, fetchMe]);

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/catalogs" 
          element={isAuthenticated ? <CatalogsPage /> : <Navigate to="/login" replace />} 
        />
        {/* Публичный роут для кухни */}
        <Route path="/terminal" element={<TerminalPage />} />
        
        {/* Страница входа */}
        <Route path="/login" element={<LoginPage />} />

        {/* Защищенные роуты */}
        <Route 
          path="/" 
          element={
            isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;