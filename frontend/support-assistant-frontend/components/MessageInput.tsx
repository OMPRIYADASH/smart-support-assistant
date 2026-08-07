"use client";

import { useRef, useState } from "react";
import { useTheme } from "@/context/ThemeContext";


  interface MessageInputProps {
    onSend: (message: string) => void;
    onUpload: (file: File) => void;
    onSummary: () => void;
    disabled: boolean;
  }

  export default function MessageInput({
    onSend,
    onUpload,
    onSummary,
    disabled,
  }: MessageInputProps) {

    const { theme } = useTheme();
    const isDark = theme === "dark";


    const [input, setInput] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
    // Reset so selecting the same file again re-fires onChange.
    e.target.value = "";
  };

  return (
    <div
  className={`p-4 border-t transition-colors duration-300 ${
    isDark
      ? "border-slate-700 bg-slate-900"
      : "border-gray-300 bg-white"
  }`}
>
      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileChange}
          disabled={disabled}
          className="hidden"
        />
        <button
           onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          title="Upload a document"
          aria-label="Upload a document"
          className={`px-3 py-2 border rounded-lg transition-colors ${
            isDark
            ? "border-slate-600 text-white hover:bg-slate-700"
            : "border-gray-300 text-slate-700 hover:bg-gray-100"
          }`}
        >
          📎
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={disabled}
          className={`flex-1 px-5 py-3 rounded-full border transition-all duration-300 disabled:opacity-50 ${
            isDark
            ? "bg-slate-800 border-slate-700 text-white placeholder:text-gray-400"
            : "bg-white border-gray-300 text-slate-900 placeholder:text-gray-500"
          }`}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-full text-white font-medium transition"
        >
          Send
        </button>
        <button
          onClick={onSummary}
          disabled={disabled}
          className="px-6 py-3 rounded-full bg-green-600 text-white hover:bg-green-700"
        >
          Summarize
        </button>
      </div>
    </div>
  );
}
