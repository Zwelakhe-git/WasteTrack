import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import AnalyticsCards from '../components/AnalyticsCards';
import AnalyticsCharts from '../components/AnalyticsCharts';

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  
  const [data, setData] = useState<any>(null);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get(`/analytics/summary?days=${days}`);
        setData(res.data);
      } catch (err) {
        console.error("Ошибка загрузки аналитики", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [days]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ padding: 30, background: '#f8f9fa', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      
      {/* Шапка */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 30 }}>
        <div>
          <h1 style={{ margin: 0 }}>WasteTrack</h1>
          <p style={{ margin: 0, color: '#666' }}>Добро пожаловать, {user?.display_name}</p>
        </div>
        <div style={{ display: 'flex', gap: 15, alignItems: 'center' }}>
          <select 
            value={days} 
            onChange={(e) => setDays(Number(e.target.value))}
            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ccc', fontSize: 16 }}
          >
            <option value={1}>За сегодня</option>
            <option value={7}>За неделю</option>
            <option value={30}>За месяц</option>
          </select>
          <button onClick={handleLogout} style={{ padding: '8px 16px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
            Выйти
          </button>
        </div>
      </header>

      {/* Контент */}
      {loading ? (
        <p>Загрузка аналитики...</p>
      ) : data ? (
        <>
          <AnalyticsCards data={data} />
          {data.total_records > 0 ? (
             <AnalyticsCharts data={data} />
          ) : (
            <div style={{ textAlign: 'center', padding: 50, background: '#fff', borderRadius: 12 }}>
              <h3>За выбранный период списаний не найдено</h3>
              <p>Попробуйте изменить фильтр по датам.</p>
            </div>
          )}
        </>
      ) : (
        <p>Ошибка загрузки данных</p>
      )}
    </div>
  );
}