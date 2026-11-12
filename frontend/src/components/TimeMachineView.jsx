import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, ChevronDown, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import {
  ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine
} from 'recharts';

const CASE_STUDIES = [
  { id: 'ford_explorer_2016_suspension', label: '2016 Ford Explorer (Suspension)', tag: '+8 Mo Early' },
  { id: 'chevrolet_bolt_2020_electrical', label: '2020 Chevrolet Bolt EV (Battery Fire)', tag: '+4 Mo Early' },
  { id: 'honda_civic_2017_airbags', label: '2017 Honda Civic (Airbags)', tag: '+6 Mo Early' },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2.5 shadow-lg min-w-[160px]">
      <div className="text-[11px] font-medium text-zinc-400 mb-1.5 pb-1.5 border-b border-zinc-800">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center justify-between gap-4 py-0.5">
          <span className="text-[11px] text-zinc-400">{p.name}</span>
          <span className="text-[12px] font-medium text-zinc-200 tabular-nums">
            {p.name.includes('%') ? `${p.value}%` : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function TimeMachineView({ simulationData, onSelectCaseStudy }) {
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const intervalRef = useRef(null);

  const timeline = simulationData?.monthly_timeline || [];
  const maxStep = Math.max(0, timeline.length - 1);
  const current = timeline[step] || {};

  // Reset step whenever simulationData changes
  useEffect(() => {
    setStep(Math.min(6, maxStep));
    setPlaying(false);
  }, [simulationData?.entity_id]);

  // Playback
  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setStep(prev => {
          if (prev >= maxStep) { setPlaying(false); return prev; }
          return prev + 1;
        });
      }, 750);
    }
    return () => clearInterval(intervalRef.current);
  }, [playing, maxStep]);

  const chartData = timeline.slice(0, step + 1).map(d => ({
    ...d,
    risk_pct: Math.round(d.risk_score * 100),
  }));

  const riskScore = current.risk_score || 0;
  const riskPct = Math.round(riskScore * 100);

  const isWarning = riskScore >= 0.60;
  const isCritical = riskScore >= 0.75;

  return (
    <div className="space-y-4">
      {/* Control Bar & Case Study Switcher */}
      <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Case Studies Segmented Selector */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mr-1">Case Study:</span>
            {CASE_STUDIES.map(c => (
              <button
                key={c.id}
                onClick={() => onSelectCaseStudy && onSelectCaseStudy(c.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                  simulationData?.entity_id === c.id
                    ? 'bg-zinc-800 text-white border-zinc-600 shadow-sm'
                    : 'bg-zinc-950 text-zinc-400 border-zinc-800 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >
                <span>{c.label}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${
                  simulationData?.entity_id === c.id ? 'bg-blue-500/20 text-blue-400' : 'bg-zinc-800 text-zinc-500'
                }`}>
                  {c.tag}
                </span>
              </button>
            ))}
          </div>

          {/* Playback Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 bg-zinc-950 p-1 rounded-lg border border-zinc-800">
              <button
                onClick={() => setPlaying(!playing)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                  playing
                    ? 'bg-amber-600 text-white'
                    : 'bg-blue-600 text-white hover:bg-blue-500'
                }`}
              >
                {playing ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                {playing ? 'Pause' : 'Play Simulation'}
              </button>
              
              <button
                onClick={() => { setPlaying(false); setStep(0); }}
                className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition"
                title="Reset to Month 1"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="text-xs text-zinc-400 font-mono bg-zinc-950 px-3 py-1.5 rounded-lg border border-zinc-800">
              Month: <span className="font-bold text-zinc-100">{current.month || '—'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Simulation Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Dual Axis Chart Panel */}
        <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800/60 rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-zinc-200">
                {simulationData?.year} {simulationData?.make} {simulationData?.model} — Defect Signal Evolution
              </h3>
              <p className="text-xs text-zinc-500 mt-0.5">
                Monthly consumer complaint spikes vs RecallRadar predictive risk score
              </p>
            </div>
            
            <div className="flex items-center gap-3 text-xs text-zinc-400">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-2 rounded bg-red-500/70" /> Complaints
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 rounded bg-blue-400" /> Risk Score
              </span>
            </div>
          </div>

          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
                <defs>
                  <linearGradient id="complaintFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis
                  dataKey="month"
                  tick={{ fill: '#71717a', fontSize: 10 }}
                  axisLine={{ stroke: '#27272a' }}
                  tickLine={false}
                />
                <YAxis
                  yAxisId="left"
                  tick={{ fill: '#71717a', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  domain={[0, 100]}
                  tick={{ fill: '#71717a', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={v => `${v}%`}
                />
                <ReferenceLine
                  yAxisId="right"
                  y={75}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  strokeOpacity={0.7}
                  label={{ value: 'Alert Threshold (75%)', fill: '#f59e0b', fontSize: 10, position: 'top' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="complaints"
                  name="Monthly Complaints"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fill="url(#complaintFill)"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="risk_pct"
                  name="Risk Score %"
                  stroke="#3b82f6"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 5, fill: '#3b82f6', stroke: '#09090b', strokeWidth: 2 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Timeline Slider */}
          <div className="mt-5 pt-3 border-t border-zinc-800">
            <div className="flex justify-between text-xs text-zinc-500 mb-2">
              <span>Start: {timeline[0]?.month}</span>
              <span className="font-semibold text-zinc-200">Replay Position: {current.month}</span>
              <span>Recall: {timeline[maxStep]?.month}</span>
            </div>
            <input
              type="range"
              min={0}
              max={maxStep}
              value={step}
              onChange={e => { setPlaying(false); setStep(Number(e.target.value)); }}
              className="w-full"
            />
          </div>
        </div>

        {/* Live Diagnostics & Victory Banner */}
        <div className="space-y-4">
          {/* Gauge Box */}
          <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-5">
            <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-2">
              Instantaneous Risk Assessment
            </div>
            
            <div className="flex items-baseline gap-2 mb-3">
              <span className={`text-4xl font-extrabold tabular-nums ${
                isCritical ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-zinc-300'
              }`}>
                {riskPct}%
              </span>
              <span className="text-xs text-zinc-500">recall probability</span>
            </div>

            <div className="w-full h-2 rounded-full bg-zinc-800 overflow-hidden mb-3">
              <div
                className={`h-full transition-all duration-300 ${
                  isCritical ? 'bg-red-500' : isWarning ? 'bg-amber-500' : 'bg-blue-500'
                }`}
                style={{ width: `${riskPct}%` }}
              />
            </div>

            <div className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center gap-2 ${
              isCritical
                ? 'bg-red-500/10 text-red-300 border-red-500/30'
                : isWarning
                ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                : 'bg-zinc-950 text-zinc-400 border-zinc-800'
            }`}>
              {isCritical ? (
                <>
                  <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
                  <span>EARLY WARNING: High Recall Probability</span>
                </>
              ) : isWarning ? (
                <>
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>ELEVATED RISK: Surge in Progress</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4 text-blue-400 shrink-0" />
                  <span>BASELINE: Normal Complaint Volume</span>
                </>
              )}
            </div>
          </div>

          {/* Lead Time Victory Banner */}
          <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-500/30">
            <div className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              Lead Time Advantage
            </div>
            <div className="text-xl font-bold text-white mt-1">
              +{simulationData?.lead_time_months} Months Ahead
            </div>
            <div className="text-[11px] text-zinc-400 mt-1">
              Recall Announced: <span className="text-zinc-200">{simulationData?.official_recall_date}</span>
            </div>
            <div className="text-[11px] font-mono text-emerald-300 mt-0.5">
              NHTSA Campaign #{simulationData?.campaign_id}
            </div>
          </div>

          {/* Key Drivers */}
          <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
            <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-2">
              Top Failure Factors
            </div>
            {simulationData?.top_risk_factors?.map((f, i) => (
              <div key={i} className="py-1 border-b border-zinc-800/40 last:border-0">
                <span className="font-semibold text-zinc-200">{f.factor}:</span>{' '}
                <span className="text-zinc-400">{f.detail}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
