import { useEffect, useState } from 'react';
import { terminalApi } from '../api/terminal';

interface Product {
  id: number;
  name: string;
  unit: { name: string };
}

interface Reason {
  id: number;
  name: string;
}

export default function TerminalPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [reasons, setReasons] = useState<Reason[]>([]);
  
  // Состояние выбранного продукта для модалки
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState<string>('1');
  const [selectedReason, setSelectedReason] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    // Загружаем справочники при старте
    const fetchData = async () => {
      try {
        // Используем обычный fetch/axios для получения публичных данных
        const resP = await terminalApi.getProducts();//fetch('http://localhost:3020/api/products/');
        const resR = await terminalApi.getReasons();//fetch('http://localhost:3020/api/reasons/');
        // setProducts(await resP.json());
        // setReasons(await resR.json());
        setProducts(resP);
        setReasons(resR);
      } catch (error) {
        console.error("Ошибка загрузки справочников", error);
      }
    };
    fetchData();
  }, []);

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
    setQuantity('1'); // Сбрасываем количество
    setSelectedReason(null); // Сбрасываем причину
    setSuccessMsg('');
  };

  const handleSubmit = async () => {
    if (!selectedProduct || !selectedReason) return alert('Выберите причину!');
    
    setIsSubmitting(true);
    try {
      await terminalApi.createWaste({
        product_id: selectedProduct.id,
        reason_id: selectedReason,
        restaurant_id: 1, // В реальности терминал должен знать свой ID ресторана
        quantity: parseFloat(quantity),
      });
      
      setSuccessMsg(`Успешно списано: ${selectedProduct.name}`);
      setSelectedProduct(null); // Закрываем модалку
      
      // Очищаем сообщение через 3 секунды
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (error) {
      alert('Ошибка при списании');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: 'sans-serif', background: '#f5f5f5', minHeight: '100vh' }}>
      <h1 style={{ textAlign: 'center' }}>Терминал кухни</h1>
      
      {successMsg && (
        <div style={{ background: '#d4edda', color: '#155724', padding: 15, borderRadius: 8, marginBottom: 20, textAlign: 'center', fontSize: 20 }}>
          {successMsg}
        </div>
      )}

      {/* Сетка продуктов (плитки) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 15 }}>
        {products.map((product) => (
          <button
            key={product.id}
            onClick={() => handleProductClick(product)}
            style={{
              padding: 20, fontSize: 18, fontWeight: 'bold', borderRadius: 12, border: 'none',
              background: '#fff', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', cursor: 'pointer',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10
            }}
          >
            <span>{product.name}</span>
            <span style={{ fontSize: 14, color: '#666', fontWeight: 'normal' }}>({product.unit.name})</span>
          </button>
        ))}
      </div>

      {/* Модальное окно для ввода количества и причины */}
      {selectedProduct && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ background: '#fff', padding: 30, borderRadius: 12, width: 400 }}>
            <h2>Списание: {selectedProduct.name}</h2>
            
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Количество ({selectedProduct.unit.name}):</label>
              <input 
                type="number" 
                value={quantity} 
                onChange={(e) => setQuantity(e.target.value)} 
                style={{ width: '100%', padding: 10, fontSize: 18, borderRadius: 6, border: '1px solid #ccc' }}
              />
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 5 }}>Причина:</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {reasons.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => setSelectedReason(r.id)}
                    style={{
                      padding: 15, fontSize: 16, borderRadius: 8, cursor: 'pointer',
                      background: selectedReason === r.id ? '#007bff' : '#f0f0f0',
                      color: selectedReason === r.id ? '#fff' : '#000',
                      border: 'none'
                    }}
                  >
                    {r.name}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={() => setSelectedProduct(null)} style={{ flex: 1, padding: 15, borderRadius: 8, border: 'none', background: '#e0e0e0', fontSize: 16 }}>Отмена</button>
              <button onClick={handleSubmit} disabled={isSubmitting} style={{ flex: 2, padding: 15, borderRadius: 8, border: 'none', background: '#28a745', color: '#fff', fontSize: 16, cursor: 'pointer' }}>
                {isSubmitting ? 'Списание...' : 'Списать'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}