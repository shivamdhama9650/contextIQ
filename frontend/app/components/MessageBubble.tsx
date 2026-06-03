import React from "react";
import Link from "next/link";
import { Sparkles, FileText, User, ArrowLeft } from "lucide-react";

export interface Source {
  document_id: string;
  page_number?: number;
  text: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full gap-3 ${
        isUser ? "justify-end" : "justify-start"
      } animate-fade-in-up`}
    >
      {/* Icon/Avatar for Bot */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md">
          <Sparkles size={14} className="animate-pulse" />
        </div>
      )}

      {/* Bubble Container */}
      <div
        className={`max-w-[85%] rounded-2xl px-5 py-3.5 shadow-sm transition-all duration-300 hover:shadow-md ${
          isUser
            ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-none"
            : "bg-white border border-slate-200/80 text-slate-800 rounded-tl-none backdrop-blur-md"
        }`}
      >
        {/* Content */}
        <p className="whitespace-pre-wrap text-sm leading-relaxed select-text">
          {message.content}
        </p>

        {/* Sources/Citations Section */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-4 border-t border-slate-100 pt-3">
            <p className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <FileText size={12} className="text-blue-500" />
              Sources
            </p>
            <div className="mt-2 flex flex-col gap-2">
              {message.sources.map((src, index) => (
                <Link
                  href={`/source/${src.document_id}`}
                  key={index}
                  className="block rounded-lg border border-slate-100 bg-slate-50/50 p-2.5 text-xs text-slate-600 transition hover:bg-slate-50 hover:border-slate-200"
                >
                  <div className="flex items-center justify-between font-medium text-slate-700">
                    <span className="truncate max-w-[200px]">Doc: {src.document_id}</span>
                    {src.page_number !== undefined && src.page_number !== null && (
                      <span className="shrink-0 rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-semibold text-blue-600">
                        Page {src.page_number}
                      </span>
                    )}
                  </div>
                  <p className="mt-1 line-clamp-2 italic text-slate-500 font-normal">
                    &ldquo;{src.text}&rdquo;
                  </p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Icon/Avatar for User */}
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600 shadow-inner">
          <User size={14} />
        </div>
      )}
    </div>
  );
}
