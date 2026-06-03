"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Loader2, RefreshCw } from "lucide-react";
import { Message, MessageBubble, Source } from "./MessageBubble";

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am your Enterprise Knowledge Assistant. Ask me anything grounded in your uploaded documents.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

    const userMessageId = `user-${Date.now()}`;
    const assistantMessageId = `assistant-${Date.now()}`;
    const currentQuery = input.trim();

    setInput("");
    setError(null);
    setMessages((prev) => [
      ...prev,
      { id: userMessageId, role: "user", content: currentQuery },
    ]);
    setIsGenerating(true);

    // Add placeholder assistant message
    setMessages((prev) => [
      ...prev,
      { id: assistantMessageId, role: "assistant", content: "" },
    ]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: currentQuery, k: 5 }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Failed to generate answer.");
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No readable stream response found.");
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedText = "";
      let retrievedSources: Source[] = [];
      let streamError: string | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Split SSE blocks by blank lines. SSE may use either LF or CRLF.
        const blocks = buffer.split(/\r?\n\r?\n/);
        // Save the last partial block back to the buffer
        buffer = blocks.pop() || "";

        for (const block of blocks) {
          if (!block.trim()) continue;

          // Parse block lines
          const lines = block.split(/\r?\n/);
          let eventType = "";
          let dataStr = "";

          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventType = line.replace("event:", "").trim();
            } else if (line.startsWith("data:")) {
              dataStr = line.replace("data:", "").trim();
            }
          }

          if (dataStr) {
            try {
              const payload = JSON.parse(dataStr);
              if (eventType === "sources") {
                retrievedSources = payload.sources || [];
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, sources: retrievedSources }
                      : msg
                  )
                );
              } else if (eventType === "token") {
                accumulatedText += payload.token || "";
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: accumulatedText }
                      : msg
                  )
                );
              } else if (eventType === "error") {
                streamError = payload.error || "Streaming error occurred.";
              }
            } catch (err) {
              console.error("Error parsing stream chunk:", err);
            }
          }
        }
      }

      if (streamError) {
        throw new Error(streamError);
      }

      if (!accumulatedText.trim()) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  content:
                    "I could not generate an answer from the retrieved context. Please try a more specific question.",
                  sources: retrievedSources,
                }
              : msg
          )
        );
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.message || "An unexpected error occurred. Please try again.");
      // Update assistant message to show error or remove it
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, content: "Sorry, I encountered an error while retrieving the information." }
            : msg
        )
      );
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-220px)] flex-col rounded-2xl border border-slate-200/80 bg-white/70 shadow-xl backdrop-blur-lg">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 bg-white/95 px-6 py-4 rounded-t-2xl">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-sm font-semibold text-slate-700">Enterprise AI Assistant</span>
        </div>
        <button
          onClick={() => {
            setMessages([
              {
                id: "welcome",
                role: "assistant",
                content: "Hello! I am your Enterprise Knowledge Assistant. Ask me anything grounded in your uploaded documents.",
              },
            ]);
            setInput("");
            setError(null);
            setIsGenerating(false);
          }}
          className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-blue-600 transition"
          title="Reset conversation"
        >
          <RefreshCw size={12} />
          Reset
        </button>
      </div>

      {/* Messages Window */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isGenerating &&
          messages[messages.length - 1]?.content === "" && (
            <div className="flex w-full gap-3 justify-start animate-fade-in-up">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md">
                <Sparkles size={14} className="animate-spin" />
              </div>
              <div className="max-w-[85%] rounded-2xl px-5 py-3.5 bg-white border border-slate-200/80 text-slate-800 rounded-tl-none">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Loader2 size={14} className="animate-spin text-blue-500" />
                  Grounded retrieval in progress...
                </div>
              </div>
            </div>
          )}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input Bar */}
      <div className="border-t border-slate-100 bg-slate-50/50 p-4 rounded-b-2xl">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question (e.g. How do I apply for leave?)..."
            disabled={isGenerating}
            className="w-full rounded-xl border border-slate-200 bg-white pl-4 pr-12 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-slate-50 disabled:text-slate-400"
          />
          <button
            type="submit"
            disabled={isGenerating || !input.trim()}
            className="absolute right-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 p-1.5 text-white shadow-sm hover:from-blue-700 hover:to-indigo-700 focus:outline-none disabled:from-slate-300 disabled:to-slate-400 disabled:text-slate-100"
          >
            <Send size={16} />
          </button>
        </form>

        {error && (
          <p className="mt-2 text-xs text-red-600 bg-red-50 border border-red-100 rounded px-3 py-1.5 animate-shake">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
