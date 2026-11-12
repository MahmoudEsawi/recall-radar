import React from 'react';
import { TrendingUp, TrendingDown, Minus, ArrowUpRight } from 'lucide-react';

function MetricCard({ label, value, unit, change, changeLabel, status, icon: Icon }) {
  const statusColors = {
    danger: 'text-red-400',
    warning: 'text-amber-400',
    success: 'text-emerald-400',
    neutral: 'text-zinc-400',
  };
  const changeColors = {
    up: 'text-red-400 bg-red-500/10',
    down: 'text-emerald-400 bg-emerald-500/10',
    flat: 'text-zinc-400 bg-zinc-800',
  };
  const changeDirection = change > 0 ? 'up' : change < 0 ? 'down' : 'flat';
  const ChangeIcon = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Minus;

  return (
    <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider">{label}</span>
        {Icon && <Icon className={`w-4 h-4 ${statusColors[status] || 'text-zinc-500'}`} />}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-semibold text-zinc-100 tabular-nums">{value}</span>
        {unit && <span className="text-xs text-zinc-500">{unit}</span>}
      </div>
      {(change !== undefined || changeLabel) && (
        <div className="flex items-center gap-1.5 mt-2">
          <span className={`inline-flex items-center gap-0.5 text-[11px] font-medium px-1.5 py-0.5 rounded ${changeColors[changeDirection]}`}>
            <ChangeIcon className="w-3 h-3" />
            {Math.abs(change)}%
          </span>
          {changeLabel && <span className="text-[11px] text-zinc-500">{changeLabel}</span>}
        </div>
      )}
    </div>
  );
}

export default function OverviewKPIs({ alerts }) {
  const critical = alerts.filter(a => a.risk_category === 'CRITICAL').length;
  const high = alerts.filter(a => a.risk_category === 'HIGH').length;
  const avgScore = alerts.length
    ? (alerts.reduce((s, a) => s + a.risk_score, 0) / alerts.length * 100).toFixed(0)
    : 0;

  return (
    <div className="grid grid-cols-4 gap-3">
      <MetricCard
        label="Critical Alerts"
        value={critical}
        status="danger"
        change={12}
        changeLabel="vs last month"
        icon={TrendingUp}
      />
      <MetricCard
        label="High Risk"
        value={high}
        status="warning"
        change={-5}
        changeLabel="vs last month"
        icon={TrendingDown}
      />
      <MetricCard
        label="Avg Risk Score"
        value={avgScore}
        unit="%"
        status={avgScore > 70 ? 'danger' : 'warning'}
        change={8}
        changeLabel="vs last month"
        icon={ArrowUpRight}
      />
      <MetricCard
        label="Avg Lead Time"
        value="6.5"
        unit="mo"
        status="success"
        change={0}
        changeLabel="stable"
        icon={Minus}
      />
    </div>
  );
}

