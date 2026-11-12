import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, AlertTriangle, CheckCircle, Calendar, ShieldAlert } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function TimeMachineView({ simulationData }) {
  const [currentStep, setCurrentStep] = useState(7); // Start around alert trigger
  const [isPlaying, setIsPlaying] = useState(false);

  const timeline = simulationData?.monthly_timeline || [];
  const maxStep = Math.max(0, timeline.length - 1);
  const currentMonthData = timeline[currentStep] || {};

  useEffect(() => {
    let timer;
    if (isPlaying) {
      timer = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= maxStep) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 900);
    }
    return () => clearInterval(timer);
  }, [isPlaying, maxStep]);

  const visibleData = timeline.slice(0, currentStep + 1);
  const isAlertTriggered = currentMonthData.risk_score >= 0.75;
  const isRecallAnnounced = currentStep === maxStep;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-red-950/40 via-slate-900 to-slate-900 border border-red-500/20 rounded-xl p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/30 mb-2">
              <ShieldAlert className="w-3.5 h-3.5" />
              Interactive Simulation
            </div>
            <h2 className="text-2xl font-bold text-white">
              The "Time Machine" Historical Replay
            </h2>
            <p className="text-slate-400 text-sm mt-1">
              Case Study: <span className="text-white font-medium">{simulationData.year} {simulationData.make} {simulationData.model}</span> ({simulationData.component})
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-950 p-2 rounded-xl border border-slate-800">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-medium text-xs transition"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isPlaying ? 'Pause' : 'Play Timeline'}
            </button>
            <button
              onClick={() => { setIsPlaying(false); setCurrentStep(0); }}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition"
              title="Reset Timeline"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Simulation Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-white">Complaints & Risk Curve Over Time</h3>
              <p className="text-xs text-slate-400">Monthly consumer filings vs RecallRadar predictive risk score</p>
            </div>
            <div className="flex items-center gap-2 font-mono text-xs text-slate-300 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
              <Calendar className="w-3.5 h-3.5 text-blue-400" />
              As of: <span className="font-bold text-white">{currentMonthData.month}</span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={visibleData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#e2e8f0', fontWeight: 'bold' }}
                />
                <Area
                  type="monotone"
                  dataKey="complaints"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#riskGradient)"
                  name="Monthly Complaints"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Scrubber Slider */}
          <div className="mt-6 pt-4 border-t border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Sep 2018 (Baseline)</span>
              <span className="font-semibold text-white">{currentMonthData.month}</span>
              <span>Dec 2019 (Recall)</span>
            </div>
            <input
              type="range"
              min="0"
              max={maxStep}
              value={currentStep}
              onChange={(e) => {
                setIsPlaying(false);
                setCurrentStep(Number(e.target.value));
              }}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-500"
            />
          </div>
        </div>

        {/* Live Evaluation Box */}
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              Predictive Diagnostics
            </h4>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300 font-medium">Model Risk Score</span>
                  <span className="font-bold text-white">{(currentMonthData.risk_score * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      currentMonthData.risk_score >= 0.75
                        ? 'bg-red-500'
                        : currentMonthData.risk_score >= 0.45
                        ? 'bg-yellow-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${currentMonthData.risk_score * 100}%` }}
                  />
                </div>
              </div>

              <div className="p-3 rounded-lg border bg-slate-950/70 border-slate-800">
                <div className="text-xs text-slate-400">Total Filings to Date</div>
                <div className="text-2xl font-bold text-white mt-1">{currentMonthData.complaints} complaints</div>
              </div>

              {/* Status Alert Badge */}
              {isAlertTriggered ? (
                <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-red-300 text-xs flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold">EARLY RECALL WARNING ISSUED</div>
                    <div className="mt-0.5 text-red-400/90">
                      Surge detected! System identified dangerous defect pattern.
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/40 text-slate-400 text-xs flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-slate-500" />
                  Standard monitoring thresholds active.
                </div>
              )}

              {/* Lead Time Victory Banner */}
              <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10">
                <div className="text-xs text-emerald-400 font-medium">Official NHTSA Recall Date</div>
                <div className="text-sm font-bold text-white mt-0.5">Dec 10, 2019 (Campaign #19V437000)</div>
                <div className="mt-2 text-xs text-emerald-300 font-semibold flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  RecallRadar detected defect 8 months ahead!
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
