import React from 'react';

export default function RecentActivity({ alerts }) {
  // Generate realistic activity feed from alert data
  const activities = alerts.flatMap(a => [
    {
      type: 'alert',
      msg: `${a.make} ${a.model} (${a.year}) — ${a.component}`,
      detail: `Risk score reached ${(a.risk_score * 100).toFixed(0)}%`,
      time: a.as_of_date,
      severity: a.risk_category,
    },
    ...(a.official_recall?.recalled ? [{
      type: 'recall',
      msg: `Official recall issued: ${a.official_recall.campaign_id}`,
      detail: a.official_recall.defect_summary?.slice(0, 80),
      time: a.official_recall.recall_date,
      severity: 'RECALL',
    }] : []),
  ]).slice(0, 8);

  const dotColor = {
    CRITICAL: 'bg-red-500',
    HIGH: 'bg-amber-500',
    MODERATE: 'bg-blue-500',
    RECALL: 'bg-emerald-500',
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
      <div className="mb-4">
        <h3 className="text-[13px] font-semibold text-zinc-200">Recent Activity</h3>
        <p className="text-[11px] text-zinc-500 mt-0.5">Latest system events and detections</p>
      </div>
      <div className="space-y-0">
        {activities.map((item, i) => (
          <div key={i} className="flex items-start gap-3 py-2.5 border-b border-zinc-800/30 last:border-0">
            {/* Timeline dot */}
            <div className="flex flex-col items-center pt-1.5">
              <div className={`w-2 h-2 rounded-full ${dotColor[item.severity] || 'bg-zinc-600'}`} />
              {i < activities.length - 1 && <div className="w-px flex-1 bg-zinc-800/60 mt-1" />}
            </div>
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="text-[12px] font-medium text-zinc-300">{item.msg}</div>
              {item.detail && (
                <div className="text-[11px] text-zinc-500 mt-0.5 truncate">{item.detail}</div>
              )}
              <div className="text-[10px] text-zinc-600 mt-1">{item.time}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

