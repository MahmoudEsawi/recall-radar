import React from 'react';
import {
  AlertTriangle, BarChart3, Clock, Search, Bell, ChevronDown
} from 'lucide-react';

export default function Sidebar({ activeView, setActiveView }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'alerts', label: 'Active Alerts', icon: TriangleAlert },
    { id: 'timemachine', label: 'Time Machine', icon: Clock },
  ];

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-[220px] bg-zinc-950 border-r border-zinc-800/60 flex flex-col z-40">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-zinc-800/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-sm font-semibold text-zinc-100 tracking-tight">RecallRadar</div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-widest">Early Warning</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="px-2 pb-2 text-[10px] font-medium text-zinc-500 uppercase tracking-wider">
          Monitor
        </div>
        {navItems.map(({ id, label, icon: Icon }) => {
          const isActive = activeView === id;
          return (
            <button
              key={id}
              onClick={() => setActiveView(id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors ${
                isActive
                  ? 'bg-zinc-800/80 text-zinc-100'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40'
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
              {id === 'alerts' && (
                <span className="ml-auto text-[10px] bg-red-500/15 text-red-400 px-1.5 py-0.5 rounded font-semibold">
                  4
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-zinc-800/60">
        <div className="text-[10px] text-zinc-600">
          Data source: NHTSA ODI
        </div>
        <div className="text-[10px] text-zinc-600">
          Last sync: 12 Nov 2026
        </div>
      </div>
    </aside>
  );
}
