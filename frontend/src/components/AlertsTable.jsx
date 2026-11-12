import React, { useState } from 'react';
import { AlertCircle, ChevronRight, CheckCircle2, Flame, Wrench } from 'lucide-react';

export default function AlertsTable({ alerts, onSelectEntity }) {
  const [filter, setFilter] = useState('ALL');

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'ALL') return true;
    return a.risk_category === filter;
  });

  const getBadgeClass = (category) => {
    switch (category) {
      case 'CRITICAL':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'HIGH':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      case 'MODERATE':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
      <div className="p-5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Active Early Defect Alerts</h2>
          <p className="text-sm text-slate-400">Models predicted to encounter official safety recalls within 12 months</p>
        </div>

        <div className="flex space-x-2">
          {['ALL', 'CRITICAL', 'HIGH', 'MODERATE'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                filter === cat
                  ? 'bg-slate-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950/60 text-slate-400 font-medium border-b border-slate-800">
            <tr>
              <th className="py-3 px-5">Vehicle Entity</th>
              <th className="py-3 px-5">Component</th>
              <th className="py-3 px-5">Risk Score</th>
              <th className="py-3 px-5">Top Key Risk Factor</th>
              <th className="py-3 px-5">Lead Time Window</th>
              <th className="py-3 px-5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200">
            {filteredAlerts.map((alert) => (
              <tr key={alert.entity_id} className="hover:bg-slate-800/40 transition">
                <td className="py-4 px-5">
                  <div className="font-semibold text-white">
                    {alert.year} {alert.make} {alert.model}
                  </div>
                  <div className="text-xs text-slate-500 font-mono">{alert.entity_id}</div>
                </td>
                <td className="py-4 px-5">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-xs font-medium text-slate-300">
                    <Wrench className="w-3.5 h-3.5 text-blue-400" />
                    {alert.component}
                  </span>
                </td>
                <td className="py-4 px-5">
                  <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${getBadgeClass(alert.risk_category)}`}>
                      {(alert.risk_score * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs text-slate-400">{alert.risk_category}</span>
                  </div>
                </td>
                <td className="py-4 px-5 max-w-xs">
                  <div className="text-xs text-slate-300 font-medium">
                    {alert.top_risk_factors[0]?.factor}
                  </div>
                  <div className="text-xs text-slate-500 truncate">
                    {alert.top_risk_factors[0]?.detail}
                  </div>
                </td>
                <td className="py-4 px-5">
                  {alert.lead_time_months ? (
                    <span className="text-emerald-400 font-medium text-xs flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      +{alert.lead_time_months} Months Ahead
                    </span>
                  ) : (
                    <span className="text-slate-500 text-xs">Monitoring</span>
                  )}
                </td>
                <td className="py-4 px-5 text-right">
                  <button
                    onClick={() => onSelectEntity(alert.entity_id)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium border border-blue-500/20 transition"
                  >
                    Investigate
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
