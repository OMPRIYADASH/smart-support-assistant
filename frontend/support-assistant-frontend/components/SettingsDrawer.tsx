"use client";

import { X, Type, PanelLeft, Info } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function SettingsDrawer({
  open,
  onClose,
}: Props) {
  const {
    theme,
    setTheme,
    fontSize,
    setFontSize,
    chatWidth,
    setChatWidth,
  } = useTheme();

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-[380px] bg-white dark:bg-slate-900 shadow-2xl z-50 overflow-y-auto">

        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-slate-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Settings
          </h2>

          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition"
          >
            <X size={22} />
          </button>
        </div>

        <div className="p-6 space-y-8">

          {/* Appearance */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              🌙 Appearance
            </h3>

            <div className="flex items-center justify-between border border-gray-200 dark:border-slate-700 rounded-xl p-4">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Dark Mode
                </p>

                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Switch between light and dark mode
                </p>
              </div>

              <button
                onClick={() =>
                  setTheme(theme === "dark" ? "light" : "dark")
                }
                className={`relative w-12 h-7 rounded-full transition-all duration-300 ${
                  theme === "dark"
                    ? "bg-blue-600"
                    : "bg-gray-300"
                }`}
              >
                <span
                  className={`absolute top-1 left-1 h-5 w-5 rounded-full bg-white transition-transform duration-300 ${
                    theme === "dark"
                      ? "translate-x-5"
                      : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Font Size */}
          <div>
            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-4">
              <Type size={18} />
              Font Size
            </h3>

            <select
              value={fontSize}
              onChange={(e) =>
                setFontSize(e.target.value as "small" | "medium" | "large")
              }
              className="w-full rounded-xl border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 p-3 text-gray-900 dark:text-white"
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div> 

          {/* Chat Width */}
          <div>
            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-4">
              <PanelLeft size={18} />
              Chat Width
            </h3>

            <select
              value={chatWidth}
              onChange={(e) =>
                setChatWidth(e.target.value as "compact" | "comfortable" | "wide")
              }
              className="w-full rounded-xl border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 p-3 text-gray-900 dark:text-white"
            >
              <option value="compact">Compact</option>
              <option value="comfortable">Comfortable</option>
              <option value="wide">Wide</option>
            </select>
          </div>

          {/* About */}
          <div className="border-t border-gray-200 dark:border-slate-700 pt-6">

            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white mb-3">
              <Info size={18} />
              About
            </h3>

            <p className="text-sm text-gray-600 dark:text-gray-400 leading-6">
              Smart Support Assistant helps you upload documents,
              search information using AI, and chat with your
              knowledge base quickly and efficiently.
            </p>

          </div>

        </div>
      </div>
    </>
  );
}