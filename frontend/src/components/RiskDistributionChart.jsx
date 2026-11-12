import React from 'react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 shadow-lg">
      <div className="text-[11px] text-zinc-400 mb-1">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="text-[12px] font-medium text-zinc-200">
          {p.name}: <span className="tabular-nums">{p.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function RiskDistributionChart({ alerts }) {
  // Build distribution data
  const distribution = [
    { range: '90-100', count: alerts.filter(a => a.risk_score >= 0.9).length, color: '#ef4444' },
    { range: '80-89', count: alerts.filter(a => a.risk_score >= 0.8 && a.risk_score < 0.9).length, color: '#f97316' },
    { range: '70-79', count: alerts.filter(a => a.risk_score >= 0.7 && a.risk_score < 0.8).length, color: '#f59e0b' },
    { range: '60-69', count: alerts.filter(a => a.risk_score >= 0.6 && a.risk_score < 0.7).length, color: '#eab308' },
    { range: '40-59', count: alerts.filter(a => a.risk_score >= 0.4 && a.risk_score < 0.6).length, color: '#3b82f6' },
    { range: '0-39', count: alerts.filter(a => a.risk_score < 0.4).length, color: '#6b7280' },
  ];

  return (
    <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
      <div className="mb-4">
        <h3 className="text-[13px] font-semibold text-zinc-200">Risk Score Distribution</h3>
        <p className="text-[11px] text-zinc-500 mt-0.5">Fleet-wide defect severity breakdown</p>
      </div>
      <div className="h-[180px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={distribution} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
            <XAxis
              dataKey="range"
              tick={{ fill: '#71717a', fontSize: 10 }}
              axisLine={{ stroke: '#27272a' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: '#71717a', fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="count" name="Vehicles" radius={[3, 3, 0, 0]} maxBarSize={32}>
              {distribution.map((entry, i) => (
                <Cell key={i} fill={entry.color} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

