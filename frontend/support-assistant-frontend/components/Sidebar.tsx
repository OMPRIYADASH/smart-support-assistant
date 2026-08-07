"use client";

import { useEffect, useRef } from "react";
import { useTheme } from "@/context/ThemeContext";
import { Settings, User } from "lucide-react";

interface SidebarProps {
  documents: string[];
  selected: string;
  onSelect: (doc: string) => void;

  chats: { id: string; title: string }[];
  selectedChat?: string;
  onSelectChat: (id: string) => void;

 sidebarView:
  | "main"
  | "documents"
  | "chats"
  | "settings"
  | "profile";

setSidebarView: (
  view:
    | "main"
    | "documents"
    | "chats"
    | "settings"
    | "profile"
) => void;
}

export default function Sidebar({
  documents,
  selected,
  onSelect,
  chats,
  selectedChat,
  onSelectChat,
  sidebarView,
  setSidebarView,
}: SidebarProps) {
  const { theme } = useTheme();

  const scrollRef = useRef<HTMLDivElement>(null);

  const handleBack = () => {
    setSidebarView("main");
  };

  const isDark =
    theme === "dark"
      ? true
      : theme === "light"
      ? false
      : typeof window !== "undefined" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop =
        scrollRef.current.scrollHeight;
    }
  }, [documents, chats]);

  /* ===========================
        SETTINGS PAGE
  ============================ */

  if (sidebarView === "settings") {
    return (
      <div
      key="settings"
      className={`w-72 h-screen flex flex-col overflow-hidden ${
          isDark
            ? "bg-slate-900 text-white"
            : "bg-white text-slate-900"
        }`}
      >
        <button
          onClick={handleBack}
          className={`flex items-center gap-2 px-6 py-5 border-b ${
            isDark
              ? "border-slate-800 hover:bg-slate-800"
              : "border-gray-200 hover:bg-gray-100"
          }`}
        >
          ← Back
        </button>

        <div className="px-6 py-6">
          <h2 className="text-2xl font-bold">
            ⚙ Settings
          </h2>
        </div>

        <div className="px-6 space-y-4">
          <button className="w-full rounded-xl p-3 text-left hover:bg-slate-800">
            🌙 Theme
          </button>

          <button className="w-full rounded-xl p-3 text-left hover:bg-slate-800">
            🔤 Font Size
          </button>

          <button className="w-full rounded-xl p-3 text-left hover:bg-slate-800">
            📏 Chat Width
          </button>
        </div>
      </div>
    );
  }

  if (sidebarView === "documents") {
  return (
    <div
      className={`w-72 h-screen flex flex-col ${
        isDark
          ? "bg-slate-900 text-white"
          : "bg-white text-slate-900"
      }`}
    >
      <button
        onClick={() => setSidebarView("main")}
        className="p-4 text-left border-b"
      >
        ← Back
      </button>

      <div className="flex-1 overflow-y-auto p-4">
        {documents.length === 0 ? (
          <p
            className={`text-sm ${
              isDark ? "text-slate-400" : "text-slate-500"
            }`}
          >
            No document uploaded
          </p>
        ) : (
          documents.map((doc) => (
            <button
              key={doc}
              onClick={() => {
                onSelect(doc);
                handleBack();
              }}
              className={`w-full rounded-xl p-3 mb-2 text-left transition ${
                selected === doc
                  ? "bg-indigo-600 text-white"
                  : isDark
                  ? "bg-slate-800 hover:bg-slate-700"
                  : "bg-gray-100 hover:bg-gray-200"
              }`}
            >
              📄 {doc}
            </button>
          ))
        )}
      </div>
    </div>
  );
}
  


if (sidebarView === "chats") {
  return (
    <div
      className={`w-72 h-screen flex flex-col ${
        isDark
          ? "bg-slate-900 text-white"
          : "bg-white text-slate-900"
      }`}
    >
      <button
        onClick={handleBack}
        className="p-4 text-left border-b"
      >
        ← Back
      </button>

      <div className="flex-1 overflow-y-auto p-4">
        {chats.length === 0 ? (
          <p
            className={`text-sm ${
              isDark ? "text-slate-400" : "text-slate-500"
            }`}
          >
            No chats yet
          </p>
        ) : (
          chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => {
                onSelectChat(chat.id);
                handleBack();
              }}
              className={`w-full rounded-xl p-3 mb-2 text-left transition ${
                selectedChat === chat.id
                  ? "bg-cyan-600 text-white"
                  : isDark
                  ? "hover:bg-slate-800"
                  : "hover:bg-gray-100"
              }`}
            >
              {chat.title}
            </button>
          ))
        )}
      </div>
    </div>
  );
}
    /* ===========================
        PROFILE PAGE
  ============================ */

  if (sidebarView === "profile") {
    return (
      <div
        key="profile"
        className={`w-72 h-screen flex flex-col ${
          isDark
            ? "bg-slate-900 text-white"
            : "bg-white text-slate-900"
        }`}
      >
        {/* Back */}
        <button
          onClick={handleBack}
          className={`flex items-center gap-2 px-6 py-5 border-b ${
            isDark
              ? "border-slate-800 hover:bg-slate-800"
              : "border-gray-200 hover:bg-gray-100"
          }`}
        >
          ← Back
        </button>

        {/* Profile */}
        <div className="px-6 py-8 flex flex-col items-center">
          <div className="w-20 h-20 rounded-full bg-indigo-600 flex items-center justify-center text-3xl font-bold">
            G
          </div>

          <h2 className="mt-4 text-xl font-bold">
            Guest User
          </h2>

          <p className="text-sm opacity-70">
            Smart Support Assistant
          </p>
        </div>

        <div className="px-4 space-y-2">
          <button
            className={`w-full rounded-xl p-3 text-left ${
              isDark
                ? "hover:bg-slate-800"
                : "hover:bg-gray-100"
            }`}
          >
            📤 Export Chat
          </button>

          <button
            className={`w-full rounded-xl p-3 text-left ${
              isDark
                ? "hover:bg-slate-800"
                : "hover:bg-gray-100"
            }`}
          >
            🗑 Clear Chat
          </button>

          <button
            className={`w-full rounded-xl p-3 text-left ${
              isDark
                ? "hover:bg-slate-800"
                : "hover:bg-gray-100"
            }`}
          >
            ℹ About
          </button>
        </div>
      </div>
    );
  }
    /* ===========================
        MAIN SIDEBAR
  ============================ */

  return (
    <div
      key="main"
      className={`w-72 h-screen flex flex-col border-r transition-all duration-300 ${
        isDark
          ? "bg-slate-900 border-slate-800 text-white"
          : "bg-white border-gray-300 text-slate-900"
      }`}
    >
      <div className="flex-1 overflow-y-auto p-4 space-y-3">

  <button
  onClick={() => setSidebarView("documents")}
  className={`w-full text-left rounded-xl px-4 py-3 transition ${
    isDark ? "hover:bg-slate-800" : "hover:bg-gray-100"
  }`}
>
  Documents
</button>

<button
  onClick={() => setSidebarView("chats")}
  className={`w-full text-left rounded-xl px-4 py-3 transition ${
    isDark ? "hover:bg-slate-800" : "hover:bg-gray-100"
  }`}
>
  Chats
</button>

</div>

      {/* ===========================
            FIXED BOTTOM
      ============================ */}

      <div
        className={`border-t p-4 ${
          isDark
            ? "border-slate-800"
            : "border-gray-300"
        }`}
      >
        <button
          onClick={() =>
            setSidebarView("settings")
          }
          className={`w-full flex items-center gap-3 rounded-xl px-4 py-3 transition ${
            isDark
              ? "hover:bg-slate-800"
              : "hover:bg-gray-100"
          }`}
        >
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <button
          onClick={() =>
            setSidebarView("profile")
          }
          className={`mt-2 w-full flex items-center gap-3 rounded-xl px-4 py-3 transition ${
            isDark
              ? "hover:bg-slate-800"
              : "hover:bg-gray-100"
          }`}
        >
          <User size={18} />
          <span>Profile</span>
        </button>
      </div>
          </div>
  );
}