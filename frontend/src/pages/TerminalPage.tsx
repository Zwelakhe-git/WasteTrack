import { useEffect, useState } from 'react';
import { terminalApi } from '../api/terminal';
import { apiClient } from '../api/client'; // Для удаления и получения продуктов, если нужно

interface Product {
  id: number;
  name: string;
  unit: { name: string };
}

interface Reason {
  id: number;
  name: string;
}

interface GridData {
  [key: string]: number; // ключ "product_id-hour", значение quantity
}

export default function TerminalPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [reasons, setReasons] = useState<Reason[]>([]);
  const [gridData, setGridData] = useState<GridData>({});
  
  // Выбранный продукт и час для модалки
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedHour, setSelectedHour] = useState<number | null>(null);
  
  const [quantity, setQuantity] = useState<string>('');
  const [selectedReason, setSelectedReason] = useState<number | ''>('');
  const [successMsg, setSuccessMsg] = useState('');

  // Генерируем часы работы (например, с 10:00 до 23:00)
  const START_HOUR = 10;
  const END_HOUR = 23;
  const hours = Array.from({ length: END_HOUR - START_HOUR + 1 }, (_, i) => START_HOUR + i);

  const loadData = async () => {
    try {
      const [resP, resR] = await Promise.all([
        fetch('http://localhost:3020/api/products/'),
        fetch('http://localhost:3020/api/reasons/')
      ]);
      setProducts(await resP.json());
      setReasons(await resR.json());

      // Получаем данные для сетки на сегодня
      const today = new Date().toISOString().split('T')[0];
      const resGrid = await fetch(`http://localhost:3020/api/waste/grid?restaurant_id=1&date=${today}`);
      const gridRows = await resGrid.json();
      
      // Преобразуем массив в словарь для быстрого доступа
      const newGrid: GridData = {};
      gridRows.forEach((row: any) => {
        newGrid[`${row.product_id}-${row.hour}`] = row.total_quantity;
      });
      setGridData(newGrid);
    } catch (error) {
      console.error("Ошибка загрузки", error);
    }
  };

  useEffect(() => {
    loadData();
    // Обновляем сетку каждую минуту, чтобы видеть актуальные данные
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleCellClick = (product: Product, hour: number) => {
    setSelectedProduct(product);
    setSelectedHour(hour);
    
    const existingQty = gridData[`${product.id}-${hour}`];
    setQuantity(existingQty ? existingQty.toString() : '1');
    setSelectedReason('');
    setSuccessMsg('');
  };

  const handleSubmit = async () => {
    if (!selectedProduct || selectedHour === null || !selectedReason) return alert('Выберите причину!');
    
    const qty = parseFloat(quantity);
    if (isNaN(qty) || qty < 0) return alert('Некорректное количество');

    try {
      // Если менеджер ввел 0 — удаляем запись (упрощенная логика)
      // В реальности тут нужен ID записи, но для прототипа сойдет
      if (qty === 0) {
        // Для простоты в этой версии мы не удаляем, а просто не даем отправить 0
        alert('Для отмены списания обратитесь к администратору (в разработке)');
        return;
      }
      const date = new Date();
      // Отправляем списание
      await terminalApi.createWaste({
        product_id: selectedProduct.id,
        reason_id: Number(selectedReason),
        restaurant_id: 1,
        quantity: qty,
        created_at: date.toLocaleString('sv-SE'),
      });
      
      setSuccessMsg(`Списано: ${selectedProduct.name}`);
      setSelectedProduct(null); // Закрываем модалку
      loadData(); // Обновляем таблицу
    } catch (error) {
      alert('Ошибка при списании');
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif', background: '#f5f5f5', minHeight: '100vh', overflowX: 'auto' }}>
      <h1 style={{ textAlign: 'center' }}>Терминал кухни (Журнал смены)</h1>
      
      {successMsg && (
        <div style={{ background: '#d4edda', color: '#155724', padding: 15, borderRadius: 8, marginBottom: 20, textAlign: 'center', fontSize: 20 }}>
          {successMsg}
        </div>
      )}

      {/* Таблица */}
      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ccc', padding: 10, textAlign: 'left', background: '#e0e0e0', minWidth: 200 }}>Название продукта</th>
            {hours.map(h => (
              <th key={h} style={{ border: '1px solid #ccc', padding: 10, background: '#e0e0e0', minWidth: 60 }}>
                {h}:00
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id}>
              <td 
                style={{ border: '1px solid #ccc', padding: 10, fontWeight: 'bold', cursor: 'pointer', background: '#f9f9f9' }}
                onClick={() => {
                  // Клик по названию продукта открывает модалку на текущий час
                  const currentHour = new Date().getHours();
                  handleCellClick(product, currentHour);
                }}
                title="Нажмите, чтобы списать на текущий час"
              >
                {product.name} <span style={{ fontWeight: 'normal', fontSize: 12, color: '#666' }}>({product.unit.name})</span>
              </td>
              
              {hours.map(hour => {
                const val = gridData[`${product.id}-${hour}`];
                return (
                  <td 
                    key={hour} 
                    style={{ 
                      border: '1px solid #ccc', 
                      padding: 10, 
                      textAlign: 'center', 
                      cursor: 'pointer',
                      background: val ? '#fff3cd' : 'transparent',
                      fontWeight: val ? 'bold' : 'normal',
                      color: val ? '#856404' : '#333'
                    }}
                    onClick={() => handleCellClick(product, hour)}
                  >
                    {val ? val : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Модалка */}
      {selectedProduct && selectedHour !== null && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ background: '#fff', padding: 30, borderRadius: 12, width: 400 }}>
            <h2>Списание: {selectedProduct.name}</h2>
            <p style={{ color: '#666' }}>Время: {selectedHour}:00 - {selectedHour}:59</p>
            
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Количество ({selectedProduct.unit.name}):</label>
              <input 
                type="number" 
                value={quantity} 
                onChange={(e) => setQuantity(e.target.value)} 
                style={{ width: '100%', padding: 10, fontSize: 18, borderRadius: 6, border: '1px solid #ccc' }}
                placeholder="0"
              />
              <small style={{ color: '#999' }}>Введите 0, чтобы отменить списание</small>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Причина:</label>
              <select 
                value={selectedReason} 
                onChange={(e) => setSelectedReason(Number(e.target.value))}
                style={{ width: '100%', padding: 12, fontSize: 16, borderRadius: 6, border: '1px solid #ccc' }}
              >
                <option value="">-- Выберите причину --</option>
                {reasons.map(r => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={() => setSelectedProduct(null)} style={{ flex: 1, padding: 15, borderRadius: 8, border: 'none', background: '#e0e0e0', fontSize: 16 }}>Отмена</button>
              <button onClick={handleSubmit} style={{ flex: 2, padding: 15, borderRadius: 8, border: 'none', background: '#28a745', color: '#fff', fontSize: 16, cursor: 'pointer' }}>
                {parseFloat(quantity) === 0 ? 'Отменить запись' : 'Списать'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
