import React from 'react';
import { X, ShieldAlert, AlertTriangle, CheckCircle, ArrowRight, Printer, FileText, Wrench } from 'lucide-react';

export default function InvestigationDrawer({ alert, isOpen, onClose, onOpenTimeMachine }) {
  if (!isOpen || !alert) return null;

  const isCritical = alert.risk_category === 'CRITICAL';
  const isHigh = alert.risk_category === 'HIGH';

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end transition-opacity">
      <div 
        className="w-full max-w-xl bg-zinc-950 border-l border-zinc-800 h-full flex flex-col shadow-2xl overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-zinc-800 flex items-start justify-between bg-zinc-900/50 sticky top-0 z-10 backdrop-blur">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                isCritical 
                  ? 'bg-red-500/10 text-red-400 border-red-500/20' 
                  : isHigh 
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
                  : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
              }`}>
                {alert.risk_category} RISK ({(alert.risk_score * 100).toFixed(0)}%)
              </span>
              <span className="text-zinc-500 text-xs font-mono">{alert.entity_id}</span>
            </div>
            <h2 className="text-xl font-bold text-zinc-100">
              {alert.year} {alert.make} {alert.model}
            </h2>
            <div className="flex items-center gap-1.5 text-xs text-zinc-400 mt-1">
              <Wrench className="w-3.5 h-3.5 text-blue-400" />
              Component: <span className="text-zinc-200 font-medium">{alert.component}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-zinc-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 flex-1">
          {/* Executive Diagnostic Box */}
          <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Predictive Diagnostics Summary
            </h3>
            <p className="text-xs text-zinc-300 leading-relaxed">
              System flags high probability of impending safety recall within 12 months. Early defect signal detected 
              via consumer filing acceleration and text keyword clustering against historical recall patterns.
            </p>
            <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-zinc-800/60">
              <div>
                <span className="text-[11px] text-zinc-500">Total Filings Analyzed</span>
                <div className="text-sm font-semibold text-zinc-200 tabular-nums">{alert.complaint_count} complaints</div>
              </div>
              <div>
                <span className="text-[11px] text-zinc-500">Lead Time Advantage</span>
                <div className="text-sm font-semibold text-emerald-400">
                  {alert.lead_time_months ? `+${alert.lead_time_months} Months Ahead` : 'Monitoring'}
                </div>
              </div>
            </div>
          </div>

          {/* Key Risk Drivers */}
          <div>
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-3">
              Key Contributing Risk Factors
            </h3>
            <div className="space-y-2">
              {alert.top_risk_factors?.map((factor, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/60 flex items-start justify-between gap-3">
                  <div>
                    <div className="text-xs font-semibold text-zinc-200">{factor.factor}</div>
                    <div className="text-[11px] text-zinc-400 mt-0.5">{factor.detail}</div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase shrink-0 ${
                    factor.impact === 'Critical' 
                      ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {factor.impact}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Genuine Complaint Narratives */}
          <div>
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-3 flex items-center justify-between">
              <span>Authentic Driver Complaint Samples (NHTSA)</span>
              <FileText className="w-3.5 h-3.5 text-zinc-500" />
            </h3>
            <div className="space-y-2.5">
              {alert.sample_complaints?.map((narrative, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-zinc-900/40 border border-zinc-800/40 text-xs text-zinc-300 italic leading-relaxed">
                  "{narrative}"
                </div>
              ))}
            </div>
          </div>

          {/* Official Recall Status */}
          {alert.official_recall && alert.official_recall.recalled && (
            <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-500/30">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold mb-1">
                <CheckCircle className="w-4 h-4" />
                Confirmed Official NHTSA Recall
              </div>
              <div className="text-xs font-mono text-zinc-300 mt-1">
                Campaign ID: <span className="text-white font-bold">{alert.official_recall.campaign_id}</span>
              </div>
              <div className="text-xs text-zinc-400 mt-1">
                Announced Date: <span className="text-zinc-200">{alert.official_recall.recall_date}</span>
              </div>
              <p className="text-xs text-zinc-300 mt-2 bg-zinc-950/40 p-2.5 rounded border border-emerald-500/20">
                {alert.official_recall.defect_summary}
              </p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-5 border-t border-zinc-800 bg-zinc-900/80 sticky bottom-0 flex items-center justify-between gap-3">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium border border-zinc-700 transition"
          >
            <Printer className="w-3.5 h-3.5" />
            Print Brief
          </button>
          
          <button
            onClick={() => {
              onClose();
              onOpenTimeMachine(alert.entity_id);
            }}
            className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition"
          >
            Launch in Time Machine
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
