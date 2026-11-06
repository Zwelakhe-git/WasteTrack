export const formatRub = (value: number | string) =>
  Number(value).toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 2 });

export default function AnalyticsCards({ data }: { data: any }) {
  if (!data) return null;

  const cardStyle = {
    padding: '20px',
    background: '#fff',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
    flex: 1,
    textAlign: 'center' as const
  };

  return (
    <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
      <div style={cardStyle}>
        <h3 style={{ margin: 0, color: '#666', fontSize: '14px' }}>Всего записей о списании</h3>
        <p style={{ margin: '10px 0 0', fontSize: '32px', fontWeight: 'bold', color: '#333' }}>
          {data.total_records}
        </p>
      </div>
      <div style={cardStyle}>
        <h3 style={{ margin: 0, color: '#666', fontSize: '14px' }}>Сумма потерь (по себестоимости)</h3>
        <p style={{ margin: '10px 0 0', fontSize: '32px', fontWeight: 'bold', color: '#d9534f' }}>
          {formatRub(data.total_cost)}
        </p>
      </div>
    </div>
  );
}
