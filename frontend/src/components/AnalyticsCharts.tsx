import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

export default function AnalyticsCharts({ data }: { data: any }) {
  if (!data) return null;

  // Данные для графика причин (разбивка)
  const reasonsData = data.top_reasons.map((r: any) => ({
    name: r.reason_name,
    value: Number(r.total_quantity),
    count: r.records_count
  }));

  // Данные для графика продуктов
  const productsData = data.top_products.map((p: any) => ({
    name: p.product_name,
    value: Number(p.total_quantity),
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
      
      {/* График по причинам */}
      <div style={{ flex: 1, minWidth: '400px', background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
        <h3 style={{ marginTop: 0 }}>Списания по причинам</h3>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={reasonsData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {reasonsData.map((_: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: any) => [`${value} ед.`, 'Объём']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* График по продуктам */}
      <div style={{ flex: 1, minWidth: '400px', background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
        <h3 style={{ marginTop: 0 }}>Топ продуктов по списанию</h3>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={productsData} layout="vertical" margin={{ left: 50 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value: any) => [`${value} ед.`, 'Объём']} />
              <Bar dataKey="value" fill="#8884d8" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}