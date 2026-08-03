import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FilePlus, TestTube2 } from 'lucide-react';

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-slate-800/50 bg-slate-900/40 backdrop-blur-md hidden md:flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-slate-800/50">
        <div className="flex items-center gap-2 text-indigo-400">
          <TestTube2 className="h-6 w-6" />
          <span className="font-bold text-lg text-slate-100">Agentic QA</span>
        </div>
      </div>
      
      <div className="flex-1 py-6 px-4 space-y-1">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              isActive 
                ? 'bg-indigo-500/10 text-indigo-400' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <LayoutDashboard className="h-5 w-5" />
          <span className="font-medium">Dashboard</span>
        </NavLink>
        
        <NavLink
          to="/plans/new"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              isActive 
                ? 'bg-indigo-500/10 text-indigo-400' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`
          }
        >
          <FilePlus className="h-5 w-5" />
          <span className="font-medium">Create Plan</span>
        </NavLink>
      </div>

      <div className="p-4 border-t border-slate-800/50 text-xs text-slate-500 text-center">
        Agentic QA Planner &copy; {new Date().getFullYear()}
      </div>
    </aside>
  );
};
