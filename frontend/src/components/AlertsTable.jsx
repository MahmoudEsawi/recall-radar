import React, { useState } from 'react';
import { ArrowUpRight, ChevronDown, ExternalLink } from 'lucide-react';

const SEVERITY_CONFIG = {
  CRITICAL: { dot: 'bg-red-500', text: 'text-red-400', bg: 'bg-red-500/8', border: 'border-red-500/20' },
  HIGH:     { dot: 'bg-amber-500', text: 'text-amber-400', bg: 'bg-amber-500/8', border: 'border-amber-500/20' },
  MODERATE: { dot: 'bg-blue-500', text: 'text-blue-400', bg: 'bg-blue-500/8', border: 'border-blue-500/20' },
  LOW:      { dot: 'bg-zinc-500', text: 'text-zinc-400', bg: 'bg-zinc-500/8', border: 'border-zinc-500/20' },
};

export default function AlertsTable({ alerts, onInvestigate }) {
  const [filter, setFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('risk_score');

  const filtered = alerts
    .filter(a => filter === 'ALL' || a.risk_category === filter)
    .sort((a, b) => b[sortBy] - a[sortBy]);

  const filters = ['ALL', 'CRITICAL', 'HIGH', 'MODERATE'];

  return (
    <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg overflow-hidden">
      {/* Table Header */}
      <div className="px-4 py-3 border-b border-zinc-800/60 flex items-center justify-between">
        <div>
          <h3 className="text-[13px] font-semibold text-zinc-200">Active Defect Alerts</h3>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            Vehicles predicted to face recall within 12 months
          </p>
        </div>
        <div className="flex items-center gap-1 bg-zinc-950 rounded-md p-0.5 border border-zinc-800/60">
          {filters.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                filter === f
                  ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {f === 'ALL' ? 'All' : f.charAt(0) + f.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800/40">
              <th className="text-left px-4 py-2.5 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Vehicle</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Component</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Risk</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Complaints</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Primary Factor</th>
              <th className="text-left px-4 py-2.5 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Lead Time</th>
              <th className="text-right px-4 py-2.5"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/30">
            {filtered.map((alert) => {
              const sev = SEVERITY_CONFIG[alert.risk_category] || SEVERITY_CONFIG.LOW;
              return (
                <tr key={alert.entity_id} className="group hover:bg-zinc-800/20 transition-colors">
                  {/* Vehicle */}
                  <td className="px-4 py-3">
                    <div className="text-[13px] font-medium text-zinc-200">
                      {alert.year} {alert.make} {alert.model}
                    </div>
                  </td>
                  {/* Component */}
                  <td className="px-4 py-3">
                    <span className="text-[12px] text-zinc-400 bg-zinc-800/60 px-2 py-0.5 rounded">
                      {alert.component}
                    </span>
                  </td>
                  {/* Risk Score + Category */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            alert.risk_score >= 0.8 ? 'bg-red-500' :
                            alert.risk_score >= 0.6 ? 'bg-amber-500' : 'bg-blue-500'
                          }`}
                          style={{ width: `${alert.risk_score * 100}%` }}
                        />
                      </div>
                      <span className="text-[12px] font-medium text-zinc-300 tabular-nums">
                        {(alert.risk_score * 100).toFixed(0)}
                      </span>
                      <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded border ${sev.bg} ${sev.text} ${sev.border}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`} />
                        {alert.risk_category}
                      </span>
                    </div>
                  </td>
                  {/* Complaints */}
                  <td className="px-4 py-3">
                    <span className="text-[13px] text-zinc-300 tabular-nums">{alert.complaint_count}</span>
                  </td>
                  {/* Primary Factor */}
                  <td className="px-4 py-3 max-w-[200px]">
                    <div className="text-[12px] text-zinc-300">{alert.top_risk_factors[0]?.factor}</div>
                    <div className="text-[11px] text-zinc-500 truncate">{alert.top_risk_factors[0]?.detail}</div>
                  </td>
                  {/* Lead Time */}
                  <td className="px-4 py-3">
                    {alert.lead_time_months ? (
                      <span className="text-[12px] font-medium text-emerald-400 tabular-nums">
                        +{alert.lead_time_months} mo
                      </span>
                    ) : (
                      <span className="text-[11px] text-zinc-600">—</span>
                    )}
                  </td>
                  {/* Action */}
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => onInvestigate(alert.entity_id)}
                      className="opacity-0 group-hover:opacity-100 inline-flex items-center gap-1 px-2.5 py-1.5 rounded-md text-[11px] font-medium text-blue-400 bg-blue-500/10 border border-blue-500/20 hover:bg-blue-500/20 transition-all"
                    >
                      Investigate
                      <ArrowUpRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="px-4 py-2.5 border-t border-zinc-800/40 flex items-center justify-between">
        <span className="text-[11px] text-zinc-500">
          Showing {filtered.length} of {alerts.length} alerts
        </span>
        <span className="text-[10px] text-zinc-600">
          Sorted by risk score (desc)
        </span>
      </div>
    </div>
  );
}
