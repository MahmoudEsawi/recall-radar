import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, ChevronDown } from 'lucide-react';
import {
  ResponsiveContainer, ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine
} from 'recharts';

const CASE_STUDIES = [
  { id: 'ford_explorer_2016_suspension', label: '2016 Ford Explorer — Suspension' },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2.5 shadow-lg min-w-[160px]">
      <div className="text-[11px] font-medium text-zinc-400 mb-1.5 pb-1.5 border-b border-zinc-800">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center justify-between gap-4 py-0.5">
          <span className="text-[11px] text-zinc-400">{p.name}</span>
          <span className="text-[12px] font-medium text-zinc-200 tabular-nums">{p.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function TimeMachineView({ simulationData }) {
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [caseOpen, setCaseOpen] = useState(false);
  const intervalRef = useRef(null);

  const timeline = simulationData?.monthly_timeline || [];
  const maxStep = Math.max(0, timeline.length - 1);
  const current = timeline[step] || {};

  // Playback
  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setStep(prev => {
          if (prev >= maxStep) { setPlaying(false); return prev; }
          return prev + 1;
        });
      }, 800);
    }
    return () => clearInterval(intervalRef.current);
  }, [playing, maxStep]);

  // Prepare chart data with risk percentage
  const chartData = timeline.slice(0, step + 1).map(d => ({
    ...d,
    risk_pct: Math.round(d.risk_score * 100),
  }));

  const riskScore = current.risk_score || 0;
  const riskPct = Math.round(riskScore * 100);

  // Threshold indicators
  const isWarning = riskScore >= 0.5;
  const isCritical = riskScore >= 0.75;

  return (
    <div className="space-y-4">
      {/* Control Bar */}
      <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            {/* Case study selector */}
            <div className="relative">
              <button
                onClick={() => setCaseOpen(!caseOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-800 border border-zinc-700 text-[12px] font-medium text-zinc-200 hover:border-zinc-600 transition-colors"
              >
                {simulationData.year} {simulationData.make} {simulationData.model}
                <ChevronDown className="w-3 h-3 text-zinc-500" />
              </button>
            </div>

            <div className="h-4 w-px bg-zinc-800" />

            {/* Playback controls */}
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setPlaying(!playing)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium transition-colors ${
                  playing
                    ? 'bg-zinc-700 text-zinc-200'
                    : 'bg-blue-600 text-white hover:bg-blue-500'
                }`}
              >
                {playing ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                {playing ? 'Pause' : 'Play'}
              </button>
              <button
                onClick={() => { setPlaying(false); setStep(0); }}
                className="p-1.5 rounded-md bg-zinc-800 border border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600 transition-colors"
                title="Reset"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Step indicator */}
          <div className="flex items-center gap-4 text-[11px]">
            <div className="text-zinc-500">
              Step <span className="text-zinc-300 font-medium tabular-nums">{step + 1}</span> of {timeline.length}
            </div>
            <div className="text-zinc-500">
              Month: <span className="text-zinc-200 font-medium">{current.month || '—'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content: Chart + Right Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Chart Panel */}
        <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-[13px] font-semibold text-zinc-200">Complaint Volume & Risk Score</h3>
              <p className="text-[11px] text-zinc-500 mt-0.5">Monthly progression leading to official recall</p>
            </div>
            <div className="flex items-center gap-4 text-[10px] text-zinc-500">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-[3px] rounded bg-red-400/70" /> Complaints
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-[3px] rounded bg-blue-400" /> Risk Score
              </span>
            </div>
          </div>

          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <defs>
                  <linearGradient id="complaintsFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.15} />
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
                {/* Warning threshold */}
                <ReferenceLine
                  yAxisId="right"
                  y={75}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  strokeOpacity={0.4}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#3f3f46', strokeDasharray: '3 3' }} />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="complaints"
                  name="Complaints"
                  stroke="#ef4444"
                  strokeWidth={1.5}
                  fill="url(#complaintsFill)"
                  strokeOpacity={0.7}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="risk_pct"
                  name="Risk %"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#3b82f6', stroke: '#09090b', strokeWidth: 2 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Scrubber */}
          <div className="mt-4 pt-3 border-t border-zinc-800/40">
            <input
              type="range"
              min={0}
              max={maxStep}
              value={step}
              onChange={e => { setPlaying(false); setStep(Number(e.target.value)); }}
              className="w-full"
            />
            <div className="flex justify-between text-[10px] text-zinc-600 mt-1 tabular-nums">
              <span>{timeline[0]?.month || ''}</span>
              <span>{timeline[maxStep]?.month || ''}</span>
            </div>
          </div>
        </div>

        {/* Right Stats Panel */}
        <div className="space-y-4">
          {/* Live Risk Gauge */}
          <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
            <div className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider mb-3">
              Current Risk Assessment
            </div>
            <div className="flex items-baseline gap-2 mb-3">
              <span className={`text-4xl font-bold tabular-nums ${
                isCritical ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-zinc-300'
              }`}>
                {riskPct}
              </span>
              <span className="text-sm text-zinc-500">/ 100</span>
            </div>
            {/* Progress bar */}
            <div className="w-full h-1.5 rounded-full bg-zinc-800 overflow-hidden mb-3">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isCritical ? 'bg-red-500' : isWarning ? 'bg-amber-500' : 'bg-blue-500'
                }`}
                style={{ width: `${riskPct}%` }}
              />
            </div>
            <div className={`text-[11px] font-medium px-2 py-1 rounded inline-block ${
              isCritical
                ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                : isWarning
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
            }`}>
              {isCritical ? 'CRITICAL — Recall Likely' : isWarning ? 'ELEVATED — Monitoring' : 'NORMAL'}
            </div>
          </div>

          {/* Stats */}
          <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4 space-y-3">
            <div className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider">Metrics</div>
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[12px] text-zinc-400">Complaints to date</span>
                <span className="text-[13px] font-medium text-zinc-200 tabular-nums">
                  {current.complaints || 0}
                </span>
              </div>
              <div className="border-b border-zinc-800/40" />
              <div className="flex items-center justify-between">
                <span className="text-[12px] text-zinc-400">Component</span>
                <span className="text-[12px] text-zinc-300">{simulationData.component}</span>
              </div>
              <div className="border-b border-zinc-800/40" />
              <div className="flex items-center justify-between">
                <span className="text-[12px] text-zinc-400">Early warning</span>
                <span className="text-[12px] font-medium text-emerald-400">
                  +{simulationData.lead_time_months || '—'} months
                </span>
              </div>
            </div>
          </div>

          {/* Official Recall */}
          <div className="bg-zinc-900 border border-zinc-800/60 rounded-lg p-4">
            <div className="text-[10px] font-medium text-zinc-500 uppercase tracking-wider mb-3">
              Official NHTSA Recall
            </div>
            <div className="text-[12px] text-zinc-300 font-medium">
              {simulationData.official_recall_date || 'Pending'}
            </div>
            {simulationData.top_risk_factors?.map((f, i) => (
              <div key={i} className="mt-2 text-[11px] text-zinc-500">
                • {f.factor}: <span className="text-zinc-400">{f.detail}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
