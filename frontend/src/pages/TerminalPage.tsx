import { useEffect, useState } from 'react';
import { terminalApi } from '../api/terminal';

interface Product { id: number; name: string; unit: { name: string }; }
interface Reason { id: number; name: string; }
interface CellRecord { id: number; reason_id: number; reason_name: string; quantity: number; }
interface CellDetails { total: number; records: CellRecord[]; groupedReasons: {
    [reason_id: string]: number 
  }; }

export default function TerminalPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [reasons, setReasons] = useState<Reason[]>([]);
  const [gridData, setGridData] = useState<Record<string, CellDetails>>({});
  
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedHour, setSelectedHour] = useState<number | null>(null);
  const [cellRecords, setCellRecords] = useState<CellRecord[]>([]);
  
  const [quantity, setQuantity] = useState<string>('');
  const [selectedReason, setSelectedReason] = useState<number | ''>('');
  
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

      const today = new Date().toLocaleDateString('sv-SE'); 
      const resGrid = await fetch(`http://localhost:3020/api/waste/grid?restaurant_id=1&date=${today}`);
      const records = await resGrid.json();
      
      const newGrid: Record<string, CellDetails> = {};
      records.forEach((r: any) => {
        const key = `${r.product_id}-${r.hour}`;
        if (!newGrid[key]) newGrid[key] = { total: 0, records: [], groupedReasons: {} };
        if(!newGrid[key].groupedReasons[`${r.reason_id}`]){
          newGrid[key].groupedReasons[`${r.reason_id}`] = r.quantity;
        }
        newGrid[key].total += r.quantity;
        newGrid[key].records.push(r);
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
    if (details) {
      setQuantity(details.total.toString());
      setCellRecords(details.records);
    } else {
      setQuantity('1');
      setCellRecords([]);
    }
    setSelectedReason('');
  };

  const handleSubmit = async () => {
    if (!selectedProduct || selectedHour === null) return;
    
    const qty = parseFloat(quantity);
    if (isNaN(qty) || qty < 0) return alert('Некорректное количество');

    try {
      // ЛОГИКА ОТМЕНЫ: Если ввели 0 и есть записи, удаляем их
      if (qty === 0) {
        if (cellRecords.length === 0) {
          setSelectedProduct(null);
          return; // Нечего удалять
        }
        
        const confirmDelete = window.confirm(`Вы уверены, что хотите отменить все списания (${cellRecords.length} шт.) за этот час?`);
        if (!confirmDelete) return;

        // Удаляем все записи в этой ячейке
        await Promise.all(cellRecords.map(r => terminalApi.deleteWaste(r.id)));
        setSelectedProduct(null);
        loadData();
        return;
      }

      // ЛОГИКА СОЗДАНИЯ: Если ввели больше 0
      if (!selectedReason) return alert('Выберите причину!');

      const now = new Date();
      now.setHours(selectedHour, 0, 0, 0);
      if(selectedHour > (new Date().getHours())){
        return;
      }

      await terminalApi.createWaste({
        product_id: selectedProduct.id,
        reason_id: Number(selectedReason),
        restaurant_id: 1,
        quantity: qty,
        created_at: now.toLocaleString('sv-SE')
      });
      
      setSelectedProduct(null);
      loadData();
    } catch (error) {
      alert('Ошибка при сохранении');
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif', background: '#f5f5f5', minHeight: '100vh', overflowX: 'auto' }}>
      <h1 style={{ textAlign: 'center' }}>Терминал кухни</h1>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ccc', padding: 10, textAlign: 'left', background: '#e0e0e0', minWidth: 200 }}>Название продукта</th>
            {hours.map(h => (
              <th key={h} style={{ border: '1px solid #ccc', padding: 10, background: '#e0e0e0', minWidth: 60 }}>{h}:00</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id}>
              <td style={{ border: '1px solid #ccc', padding: 10, fontWeight: 'bold', cursor: 'pointer', background: '#f9f9f9' }}
                  onClick={() => handleCellClick(product, new Date().getHours())}>
                {product.name} <span style={{ fontWeight: 'normal', fontSize: 12, color: '#666' }}>({product.unit.name})</span>
              </td>
              {hours.map(hour => {
                const details = gridData[`${product.id}-${hour}`];
                return (
                  <td key={hour} 
                      style={{ border: '1px solid #ccc', padding: 10, textAlign: 'center', cursor: 'pointer',
                               background: details ? '#fff3cd' : 'transparent', fontWeight: details ? 'bold' : 'normal',
                               color: details ? '#856404' : '#333' }}
                      onClick={() => handleCellClick(product, hour)}>
                    {details ? details.total : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {selectedProduct && selectedHour !== null && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ background: '#fff', padding: 30, borderRadius: 12, width: 450 }}>
            <h2>Списание: {selectedProduct.name}</h2>
            <p style={{ color: '#666' }}>Время: {selectedHour}:00 - {selectedHour}:59</p>

            {cellRecords.length > 0 && (
              <div style={{ background: '#f8f9fa', padding: 10, borderRadius: 8, marginBottom: 20, fontSize: 14 }}>
                <strong>Детализация за этот час:</strong>
                <ul style={{ margin: '5px 0 0 0', paddingLeft: 20 }}>
                  {cellRecords.map(r => (
                    <li key={r.id}>{r.reason_name}: <b>{r.quantity}</b></li>
                  ))}
                </ul>
              </div>
            )}
            
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Количество ({selectedProduct.unit.name}):</label>
              <input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value)} 
                     style={{ width: '100%', padding: 10, fontSize: 18, borderRadius: 6, border: '1px solid #ccc' }} />
              <small style={{ color: '#d9534f', display: 'block', marginTop: 5 }}>
                Введите 0, чтобы отменить все записи за этот час
              </small>
            </div>

            <div style={{ marginBottom: 20, opacity: parseFloat(quantity) === 0 ? 0.5 : 1 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Добавить причину:</label>
              <select value={selectedReason} onChange={(e) => setSelectedReason(Number(e.target.value))}
                      disabled={parseFloat(quantity) === 0}
                      style={{ width: '100%', padding: 12, fontSize: 16, borderRadius: 6, border: '1px solid #ccc' }}>
                <option value="">-- Выберите причину --</option>
                {reasons.map(r => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={() => setSelectedProduct(null)} style={{ flex: 1, padding: 15, borderRadius: 8, border: 'none', background: '#e0e0e0', fontSize: 16 }}>Отмена</button>
              <button onClick={handleSubmit} style={{ flex: 2, padding: 15, borderRadius: 8, border: 'none', background: parseFloat(quantity) === 0 ? '#dc3545' : '#28a745', color: '#fff', fontSize: 16, cursor: 'pointer' }}>
                {parseFloat(quantity) === 0 ? 'Отменить записи' : 'Добавить запись'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}