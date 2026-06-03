import React from "react";

export function LoadingSpinner() {
  return (
    <div className="flex items-center space-x-2 py-1">
      <div className="relative flex h-4 w-4">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75"></span>
        <span className="relative inline-flex h-4 w-4 rounded-full bg-blue-500"></span>
      </div>
      <div className="flex space-x-1">
        <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]"></div>
        <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]"></div>
        <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"></div>
      </div>
    </div>
  );
}
