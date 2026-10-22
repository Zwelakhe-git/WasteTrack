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
        <h3 style={{ margin: 0, color: '#666', fontSize: '14px' }}>Общий объём списаний</h3>
        <p style={{ margin: '10px 0 0', fontSize: '32px', fontWeight: 'bold', color: '#d9534f' }}>
          {data.total_quantity}
        </p>
      </div>
    </div>
  );
}