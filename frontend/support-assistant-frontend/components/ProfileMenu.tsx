"use client";

import {
  User,
  Moon,
  Trash2,
  Download,
  Info,
  X,
} from "lucide-react";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function ProfileMenu({
  open,
  onClose,
}: Props) {
  if (!open) return null;

  return (
    <div className="absolute top-20 right-5 w-80 rounded-3xl bg-white shadow-2xl border border-gray-200 overflow-hidden z-50">

      {/* Header */}
      <div className="flex items-center gap-4 p-5 border-b">

        <div className="w-16 h-16 rounded-full bg-cyan-100 flex items-center justify-center">
          <User size={32} className="text-cyan-600" />
        </div>

        <div>
          <h2 className="font-bold text-xl text-gray-900">
            Guest User
          </h2>

          <p className="text-gray-500 text-sm">
            Smart Support Assistant
          </p>
        </div>

      </div>

      {/* Menu */}

      <button className="w-full flex items-center gap-4 px-6 py-4 hover:bg-gray-100 transition text-gray-800">
        <Moon size={22} />
        <span className="text-lg">Toggle Theme</span>
      </button>

      <button className="w-full flex items-center gap-4 px-6 py-4 hover:bg-gray-100 transition text-red-600">
        <Trash2 size={22} />
        <span className="text-lg">Clear Chat</span>
      </button>

      <button className="w-full flex items-center gap-4 px-6 py-4 hover:bg-gray-100 transition text-green-600">
        <Download size={22} />
        <span className="text-lg">Export Chat</span>
      </button>

      <button className="w-full flex items-center gap-4 px-6 py-4 hover:bg-gray-100 transition text-blue-600">
        <Info size={22} />
        <span className="text-lg">About</span>
      </button>

      <div className="border-t">

        <button
          onClick={onClose}
          className="w-full flex items-center gap-4 px-6 py-4 hover:bg-gray-100 transition text-gray-600"
        >
          <X size={22} />
          <span className="text-lg">Close</span>
        </button>

      </div>
    </div>
  );
}