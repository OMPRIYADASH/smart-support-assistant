import { useTheme } from "@/context/ThemeContext";

interface ChatItem {
  id: string;
  title: string;
}

interface Props {
  chats: ChatItem[];
  selectedId?: string;
  onSelect: (id: string) => void;
}

export default function ChatHistory({
  chats,
  selectedId,
  onSelect,
}: Props) {

const { theme } = useTheme();
const isDark = theme === "dark";

  return (
    <div
  className={`w-64 border-r flex flex-col transition-colors duration-300 ${
    isDark
      ? "bg-slate-900 border-slate-800"
      : "bg-white border-gray-300"
  }`}
>

      <div
  className={`p-4 border-b ${
    isDark ? "border-slate-800" : "border-gray-300"
  }`}
>
  <h2
    className={`text-lg font-semibold ${
      isDark ? "text-white" : "text-slate-900"
    }`}
  >
    💬 Chats
  </h2>
</div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelect(chat.id)}
            className={`w-full text-left p-3 rounded-xl transition ${
              selectedId === chat.id
                ? "bg-cyan-600 text-white"
                : isDark
                  ? "bg-slate-800 hover:bg-slate-700 text-gray-300"
                  : "bg-gray-100 hover:bg-gray-200 text-slate-900"
            }`}
          >
            <div className="text-sm font-medium truncate">
              {chat.title}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}