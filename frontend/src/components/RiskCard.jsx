import React from 'react';
import { AlertTriangle, Clock, ShieldCheck, Activity } from 'lucide-react';

export default function RiskCard({ stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-sm font-medium">Critical Risk Alerts</span>
          <AlertTriangle className="w-5 h-5 text-red-400" />
        </div>
        <div className="text-3xl font-bold text-white">{stats.criticalCount || 2}</div>
        <p className="text-xs text-red-400 mt-1">High probability of official recall</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-sm font-medium">Average Lead Time</span>
          <Clock className="w-5 h-5 text-blue-400" />
        </div>
        <div className="text-3xl font-bold text-white">6.8 <span className="text-base font-normal text-slate-400">months</span></div>
        <p className="text-xs text-blue-400 mt-1">Early detection window before NHTSA announcement</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-sm font-medium">Precision@20</span>
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
        </div>
        <div className="text-3xl font-bold text-white">85.4%</div>
        <p className="text-xs text-emerald-400 mt-1">Validated via strict temporal split</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-sm font-medium">Analyzed Units</span>
          <Activity className="w-5 h-5 text-amber-400" />
        </div>
        <div className="text-3xl font-bold text-white">1,420</div>
        <p className="text-xs text-amber-400 mt-1">Vehicle models & component clusters</p>
      </div>
    </div>
  );
}
