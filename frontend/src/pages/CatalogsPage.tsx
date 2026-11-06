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
  const [prodCost, setProdCost] = useState('');

  // Редактирование себестоимости в списке: id продукта -> введённое значение
  const [costDrafts, setCostDrafts] = useState<Record<number, string>>({});

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
      await apiClient.post('/products/', {
        name: prodName,
        category: prodCategory,
        unit_id: Number(prodUnitId),
        cost: prodCost === '' ? 0 : Number(prodCost)
      });
      setProdName(''); setProdCategory(''); setProdUnitId(''); setProdCost('');
      loadData();
      alert('Продукт добавлен');
    } catch (err) { alert('Ошибка добавления продукта'); }
  };

  const handleSaveCost = async (productId: number) => {
    const value = costDrafts[productId];
    if (value === undefined || value === '' || Number(value) < 0) return alert('Введите себестоимость (0 или больше)');
    try {
      await apiClient.patch(`/products/${productId}`, { cost: Number(value) });
      setCostDrafts(d => { const next = { ...d }; delete next[productId]; return next; });
      loadData();
    } catch (err) { alert('Ошибка сохранения себестоимости'); }
  };

  const handleToggleStatus = async (product: any) => {
    const status = product.status === 'active' ? 'frozen' : 'active';
    try {
      await apiClient.patch(`/products/${product.id}`, { status });
      loadData();
    } catch (err) { alert('Ошибка изменения статуса'); }
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
            <input
              type="number" min="0" step="0.01"
              placeholder="Себестоимость за единицу, ₽"
              value={prodCost} onChange={e => setProdCost(e.target.value)}
              style={{ padding: 10 }}
            />
            <button type="submit" style={{ padding: 10, background: '#28a745', color: '#fff', border: 'none', borderRadius: 6 }}>Добавить продукт</button>
          </form>
          
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid #ddd' }}>
                <th style={{ padding: 6 }}>Продукт</th>
                <th style={{ padding: 6 }}>Ед.</th>
                <th style={{ padding: 6 }}>Себестоимость, ₽ за ед.</th>
                <th style={{ padding: 6 }}>Статус</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => {
                const draft = costDrafts[p.id];
                return (
                  <tr key={p.id} style={{ borderBottom: '1px solid #f0f0f0', opacity: p.status === 'active' ? 1 : 0.5 }}>
                    <td style={{ padding: 6 }}>{p.name} <span style={{ color: '#888', fontSize: 12 }}>({p.category})</span></td>
                    <td style={{ padding: 6 }}><b>{p.unit.name}</b></td>
                    <td style={{ padding: 6, whiteSpace: 'nowrap' }}>
                      <input
                        type="number" min="0" step="0.01"
                        value={draft ?? String(p.cost)}
                        onChange={e => setCostDrafts(d => ({ ...d, [p.id]: e.target.value }))}
                        style={{ width: 90, padding: 6 }}
                      />
                      {draft !== undefined && (
                        <button onClick={() => handleSaveCost(p.id)} style={{ marginLeft: 6, padding: '6px 10px', background: '#007bff', color: '#fff', border: 'none', borderRadius: 4 }}>
                          Сохранить
                        </button>
                      )}
                    </td>
                    <td style={{ padding: 6 }}>
                      <button onClick={() => handleToggleStatus(p)} style={{ padding: '6px 10px', border: '1px solid #ccc', borderRadius: 4, background: '#fff' }}>
                        {p.status === 'active' ? 'Заморозить' : 'Активировать'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
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