"use client";

import { useLayoutEffect, useRef } from "react";
import { Message } from "@/types";
import { useTheme } from "@/context/ThemeContext";

interface MessageListProps {
  messages: Message[];
  loading: boolean;
  onSuggestionClick?: (text: string) => void;
}

export default function MessageList({
  messages,
  loading,
  onSuggestionClick,
}: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { theme } = useTheme();

  const isDark =
    theme === "dark"
      ? true
      : theme === "light"
      ? false
      : typeof window !== "undefined" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches;

  useLayoutEffect(() => {
    if (!containerRef.current) return;

    containerRef.current.scrollTo({
      top: containerRef.current.scrollHeight,
      behavior: "smooth",
    });

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  return (
    <div
      ref={containerRef}
      className={`h-full overflow-y-auto px-6 py-6 ${
        isDark ? "bg-slate-950" : "bg-slate-50"
    }`}
  >
    {messages.length === 0 && !loading && (
        <div
          className={`flex items-center justify-center h-full ${
            isDark ? "text-slate-400" : "text-slate-500"
          }`}
        >
          <div className="text-center">
            <div className="text-5xl mb-3">🤖</div>

            <p className="text-lg font-medium">
              Start chatting with Smart Support Assistant
            </p>

            <p className="text-sm mt-2">
              Upload a PDF or TXT file, or simply ask a question.
            </p>
          </div>
        </div>
      )}

      <div className="space-y-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-end gap-3 ${
              msg.role === "user"
                ? "justify-end"
                : "justify-start"
            }`}
          >
            {msg.role === "assistant" && (
              <div className="w-10 h-10 rounded-full bg-cyan-500 flex items-center justify-center text-white text-lg shadow-lg flex-shrink-0">
                🤖
              </div>
            )}

            <div
              className={`max-w-md lg:max-w-2xl px-5 py-3 rounded-3xl shadow-lg transition-all duration-300 hover:scale-[1.02] whitespace-pre-wrap break-words ${
                msg.role === "user"
                  ? "bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-br-md"
                  : isDark
                  ? "bg-slate-800 text-gray-100 rounded-bl-md border border-slate-700"
                  : "bg-white text-slate-900 rounded-bl-md border border-gray-300"
              }`}
            >
              <p className="text-[15px] leading-7">
                {msg.content}
              </p>

              {msg.suggestions &&
                msg.suggestions.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {msg.suggestions.map(
                      (suggestion, i) => (
                        <button
                          key={i}
                          onClick={() =>
                            onSuggestionClick?.(
                              suggestion
                            )
                          }
                          className={`rounded-full px-3 py-2 text-sm transition ${
                            isDark
                              ? "bg-slate-700 hover:bg-slate-600"
                              : "bg-gray-100 hover:bg-gray-200"
                          }`}
                        >
                          {suggestion}
                        </button>
                      )
                    )}
                  </div>
                )}
            </div>

            {msg.role === "user" && (
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white text-lg shadow-lg flex-shrink-0">
                👤
              </div>
            )}
          </div>
        ))}
        
        <div ref={bottomRef} />
      </div>
    </div>
  );
}