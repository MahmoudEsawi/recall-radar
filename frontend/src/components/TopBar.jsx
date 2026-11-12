import React from 'react';
import { Search, Bell } from 'lucide-react';

export default function TopBar({ title, subtitle }) {
  return (
    <header className="h-14 border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-30">
      <div>
        <h1 className="text-sm font-semibold text-zinc-100">{title}</h1>
        {subtitle && <p className="text-[11px] text-zinc-500">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search vehicles..."
            className="w-48 h-8 pl-8 pr-3 rounded-md bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
          />
        </div>
        {/* Notifications */}
        <button className="relative w-8 h-8 rounded-md bg-zinc-900 border border-zinc-800 flex items-center justify-center hover:border-zinc-700 transition-colors">
          <Bell className="w-3.5 h-3.5 text-zinc-400" />
          <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500" />
        </button>
      </div>
    </header>
  );
}

