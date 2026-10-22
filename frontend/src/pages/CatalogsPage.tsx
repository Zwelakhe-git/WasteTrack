import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';

export default function CatalogsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [reasons, setReasons] = useState<any[]>([]);
  const [units, setUnits] = useState<any[]>([]);

  // Состояния для формы добавления продукта
  const [prodName, setProdName] = useState('');
  const [prodCategory, setProdCategory] = useState('');
  const [prodUnitId, setProdUnitId] = useState<number | ''>('');

  // Состояния для формы добавления причины
  const [reasonName, setReasonName] = useState('');
  const [reasonDesc, setReasonDesc] = useState('');

  const loadData = async () => {
    const [p, r, u] = await Promise.all([
      apiClient.get('/products/'),
      apiClient.get('/reasons/'),
      apiClient.get('/products/units')
    ]);
    setProducts(p.data);
    setReasons(r.data);
    setUnits(u.data);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/products/', { name: prodName, category: prodCategory, unit_id: Number(prodUnitId) });
      setProdName(''); setProdCategory(''); setProdUnitId('');
      loadData();
      alert('Продукт добавлен');
    } catch (err) { alert('Ошибка добавления продукта'); }
  };

  const handleAddReason = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/reasons/', { name: reasonName, description: reasonDesc });
      setReasonName(''); setReasonDesc('');
      loadData();
      alert('Причина добавлена');
    } catch (err) { alert('Ошибка добавления причины'); }
  };

  return (
    <div style={{ padding: 30, fontFamily: 'sans-serif', background: '#f8f9fa', minHeight: '100vh' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 30 }}>
        <h1>Управление справочниками</h1>
        <Link to="/" style={{ textDecoration: 'none', padding: '10px 20px', background: '#007bff', color: '#fff', borderRadius: 6 }}>На главную</Link>
      </header>

      <div style={{ display: 'flex', gap: 30 }}>
        {/* Блок продуктов */}
        <div style={{ flex: 1, background: '#fff', padding: 20, borderRadius: 12 }}>
          <h2>Продукты</h2>
          <form onSubmit={handleAddProduct} style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
            <input placeholder="Название" value={prodName} onChange={e => setProdName(e.target.value)} required style={{ padding: 10 }} />
            <input placeholder="Категория" value={prodCategory} onChange={e => setProdCategory(e.target.value)} required style={{ padding: 10 }} />
            <select value={prodUnitId} onChange={e => setProdUnitId(Number(e.target.value))} required style={{ padding: 10 }}>
              <option value="">Выберите единицу измерения</option>
              {units.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
            </select>
            <button type="submit" style={{ padding: 10, background: '#28a745', color: '#fff', border: 'none', borderRadius: 6 }}>Добавить продукт</button>
          </form>
          
          <ul>
            {products.map(p => (
              <li key={p.id}>{p.name} ({p.category}) — <b>{p.unit.name}</b></li>
            ))}
          </ul>
        </div>

        {/* Блок причин */}
        <div style={{ flex: 1, background: '#fff', padding: 20, borderRadius: 12 }}>
          <h2>Причины списаний</h2>
          <form onSubmit={handleAddReason} style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
            <input placeholder="Название причины" value={reasonName} onChange={e => setReasonName(e.target.value)} required style={{ padding: 10 }} />
            <input placeholder="Описание" value={reasonDesc} onChange={e => setReasonDesc(e.target.value)} style={{ padding: 10 }} />
            <button type="submit" style={{ padding: 10, background: '#28a745', color: '#fff', border: 'none', borderRadius: 6 }}>Добавить причину</button>
          </form>

          <ul>
            {reasons.map(r => (
              <li key={r.id}>{r.name}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}