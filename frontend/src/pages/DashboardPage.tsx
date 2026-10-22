import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Панель управления WasteTrack</h1>
      <p>Привет, {user?.display_name} (Роль: {user?.role})</p>
      <button onClick={handleLogout}>Выйти</button>
      
      <div style={{ marginTop: 40, padding: 20, background: '#f0f0f0' }}>
        <h3>Здесь будет Аналитика и Справочники</h3>
      </div>
    </div>
  );
}