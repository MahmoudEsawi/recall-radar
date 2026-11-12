import React from 'react';
import { ShieldAlert, PlayCircle, BarChart3 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-red-600/20 p-2 rounded-lg border border-red-500/30">
            <ShieldAlert className="w-6 h-6 text-red-500" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              RecallRadar
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Samsung AI Capstone
              </span>
            </h1>
            <p className="text-xs text-slate-400">Automotive Defect Early Warning & Prediction System</p>
          </div>
        </div>

        <nav className="flex items-center space-x-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('alerts')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === 'alerts'
                ? 'bg-slate-800 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Active Alerts</span>
          </button>

          <button
            onClick={() => setActiveTab('timemachine')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === 'timemachine'
                ? 'bg-red-950/80 text-red-300 border border-red-800/40 shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <PlayCircle className="w-4 h-4 text-red-400" />
            <span>Time Machine Demo</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
