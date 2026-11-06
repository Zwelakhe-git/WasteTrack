import { useEffect, useState } from 'react';
import { terminalApi } from '../api/terminal';
import { RESTAURANT_ID } from '../config';

interface Product {
  id: number;
  name: string;
  unit: { name: string };
}

interface Reason {
  id: number;
  name: string;
}

interface GridRecord {
  id: number,
  product_id?: number,
  reason_id: number,
  reason_name?: string,
  hour?: number,
  quantity: number,
}

// Новая структура для хранения деталей в ячейке
interface CellDetails {
  total: number;
  records: GridRecord[];
  groupedReasons: {
    [reason_id: string]: number 
  }
}

export default function TerminalPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [reasons, setReasons] = useState<Reason[]>([]);
  
  // Словарь: ключ "product_id-hour", значение - детали
  const [gridData, setGridData] = useState<Record<string, CellDetails>>({});
  
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedHour, setSelectedHour] = useState<number | null>(null);
  const [cellRecords, setCellRecords] = useState<GridRecord[]>([]); // Записи в текущей ячейке
  
  const [quantity, setQuantity] = useState<string>('');
  const [selectedReason, setSelectedReason] = useState<number | ''>('');
  
  const START_HOUR = 10;
  const END_HOUR = 23;
  const hours = Array.from({ length: END_HOUR - START_HOUR + 1 }, (_, i) => START_HOUR + i);

  const loadData = async () => {
    try {
      // Берем локальную дату клиента (YYYY-MM-DD)
      const today = new Date().toLocaleDateString('sv-SE');
      const [productsData, reasonsData, records] = await Promise.all([
        terminalApi.getProducts(),
        terminalApi.getReasons(),
        terminalApi.getGrid(RESTAURANT_ID, today)
      ]);
      setProducts(productsData);
      setReasons(reasonsData);
      
      // Группируем данные на клиенте
      const newGrid: Record<string, CellDetails> = {};
      records.forEach((r: GridRecord) => {
        const key = `${r.product_id}-${r.hour}`;
        if (!newGrid[key]) {
          newGrid[key] = { total: 0, records: [], groupedReasons: {} };
        }
        if(!newGrid[key].groupedReasons[`${r.reason_id}`]){
          newGrid[key].groupedReasons[`${r.reason_id}`] = 0;
        }
        newGrid[key].total += r.quantity;
        newGrid[key].records.push(r);
        newGrid[key].groupedReasons[`${r.reason_id}`] += r.quantity;
      });
      
      setGridData(newGrid);
    } catch (error) {
      console.error("Ошибка загрузки", error);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleCellClick = (product: Product, hour: number) => {
    setSelectedProduct(product);
    setSelectedHour(hour);
    
    const details = gridData[`${product.id}-${hour}`];
    // Количество подставляется после выбора причины (см. handleSelectedReasonChange)
    setQuantity('1');
    setCellRecords(details ? details.records : []);
    setSelectedReason('');
  };

  const handleSubmit = async () => {
    if (!selectedProduct || selectedHour === null || !selectedReason) return alert('Выберите причину!');
    
    const qty = parseFloat(quantity);
    if (isNaN(qty)) return alert('Некорректное количество');

    try {
      if (qty < 0) return alert('Количество не может быть отрицательным');

      if (qty === 0) {
        // Отменяем списание только по выбранной причине
        const target: GridRecord | undefined = cellRecords.find(r => r.reason_id === Number(selectedReason));
        if (!target) return alert('По этой причине за этот час списаний нет');

        const reasonName = reasons.find(r => r.id === Number(selectedReason))?.name ?? '';
        const confirmDelete = window.confirm(`Отменить списание по причине «${reasonName}» за ${selectedHour}:00?`);
        if (!confirmDelete) return;

        await terminalApi.deleteWaste(target.id);

        setSelectedProduct(null);
        loadData();
        return;
      }

      
      // Нельзя списывать в час, который ещё не наступил
      if (selectedHour > new Date().getHours()) {
        return alert('Этот час ещё не наступил');
      }

      // Формируем дату с нужным часом (локальное время)
      const now = new Date();
      now.setHours(selectedHour, 0, 0, 0); // Ставим выбранный час

      await terminalApi.createWaste({
        product_id: selectedProduct.id,
        reason_id: Number(selectedReason),
        restaurant_id: RESTAURANT_ID,
        quantity: qty,
        created_at: now.toLocaleString('sv-SE') // Передаем локальное время на сервер
      });
      
      setSelectedProduct(null);
      loadData();
    } catch (error) {
      console.error(error);
      alert('Ошибка при списании');
    }
  };
  const handleSelectedReasonChange = (reasonId: number) => {
    setSelectedReason(reasonId);
    if (!selectedProduct || selectedHour === null) return;
    // Если по этой причине в этом часе уже есть списание — показываем его количество,
    // иначе начинаем с 1 (в пустой ячейке gridData[...] нет, поэтому через ?.)
    const existing = gridData[`${selectedProduct.id}-${selectedHour}`]?.groupedReasons[`${reasonId}`];
    setQuantity(existing && existing > 0 ? existing.toString() : '1');
  }

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif', background: '#f5f5f5', minHeight: '100vh', overflowX: 'auto' }}>
      <h1 style={{ textAlign: 'center' }}>Терминал кухни</h1>

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
                onClick={() => handleCellClick(product, new Date().getHours())}
              >
                {product.name} <span style={{ fontWeight: 'normal', fontSize: 12, color: '#666' }}>({product.unit.name})</span>
              </td>
              
              {hours.map(hour => {
                const details = gridData[`${product.id}-${hour}`];
                return (
                  <td 
                    key={hour} 
                    style={{ 
                      border: '1px solid #ccc', 
                      padding: 10, 
                      textAlign: 'center', 
                      cursor: 'pointer',
                      background: details ? '#fff3cd' : 'transparent',
                      fontWeight: details ? 'bold' : 'normal',
                      color: details ? '#856404' : '#333'
                    }}
                    onClick={() => handleCellClick(product, hour)}
                  >
                    {details ? details.total : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Модальное окно */}
      {selectedProduct && selectedHour !== null && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ background: '#fff', padding: 30, borderRadius: 12, width: 450 }}>
            <h2>Списание: {selectedProduct.name}</h2>
            <p style={{ color: '#666' }}>Время: {selectedHour}:00 - {selectedHour}:59</p>

            {/* Детализация по причинам (если есть записи) */}
            {cellRecords.length > 0 && (
              <div style={{ background: '#f8f9fa', padding: 10, borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
                <strong>Детализация за этот час:</strong>
                <ul style={{ margin: '5px 0 0 0', paddingLeft: 20 }}>
                  {Object.entries(gridData[`${selectedProduct.id}-${selectedHour}`].groupedReasons).map(r => (
                    <li key={r[0]}>{reasons.find(reason => reason.id === Number(r[0]))?.name}: <b>{r[1]}</b></li>
                  ))}
                </ul>
              </div>
            )}
            
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Количество ({selectedProduct.unit.name}), 0 — отменить:</label>
              <input 
                type="number" 
                value={quantity} 
                onChange={(e) => setQuantity(e.target.value)} 
                style={{ width: '100%', padding: 10, fontSize: 18, borderRadius: 6, border: '1px solid #ccc' }}
              />
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Причина:</label>
              <select 
                value={selectedReason} 
                onChange={(e) => handleSelectedReasonChange(Number(e.target.value))}
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
                Добавить запись
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}