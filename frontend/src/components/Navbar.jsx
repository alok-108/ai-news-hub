import React from "react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-surface-900/70 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        {/* Logo / Title */}
        <a href="/" className="flex items-center gap-2.5 group" id="nav-logo">
          <span className="text-2xl group-hover:scale-110 transition-transform duration-200">
            📰
          </span>
          <div className="flex flex-col leading-tight">
            <span className="text-lg font-bold tracking-tight text-gradient">
              AI News Hub
            </span>
            <span className="text-[10px] font-medium text-white/30 tracking-widest uppercase">
              बहुभाषी समाचार
            </span>
          </div>
        </a>

        {/* Right side — ad placeholder + live dot */}
        <div className="flex items-center gap-4">
          {/* Live indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-xs font-medium text-emerald-400">Live</span>
          </div>

          {/* Ad slot placeholder (hidden until configured) */}
          {/* <div id="ad-slot-nav" className="w-[320px] h-[50px] bg-white/5 rounded-lg hidden lg:block" /> */}
        </div>
      </div>
    </header>
  );
}
