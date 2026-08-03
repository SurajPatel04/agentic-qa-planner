import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="h-16 border-b border-slate-800/50 bg-slate-900/40 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center">
        {/* Can put a breadcrumb or title here if needed */}
      </div>
      <div className="flex items-center gap-4">
        <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm border border-indigo-500/30">
          QA
        </div>
      </div>
    </header>
  );
};
