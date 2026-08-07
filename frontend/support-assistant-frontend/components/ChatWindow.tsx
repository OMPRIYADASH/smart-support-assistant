"use client";

import { useEffect, useState } from "react";
import { Message, ChatResponse, UploadResponse } from "@/types";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import Sidebar from "./Sidebar";
import { Menu } from "lucide-react";
//import SettingsDrawer from "./SettingsDrawer";
//import ProfileMenu from "./ProfileMenu";
import { useTheme } from "@/context/ThemeContext";
 


const API_BASE_URL = "http://localhost:8000";

type SidebarView = "main" | "documents" | "chats" | "settings" | "profile";

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [uploadedDocument, setUploadedDocument] = useState("");
  const [documents, setDocuments] = useState<string[]>([]); 
  const [chats, setChats] = useState<{ id: string; title: string }[]>([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [sidebarView, setSidebarView] = useState<SidebarView>("main");
  const [uploading, setUploading] = useState(false);


  const { theme } = useTheme();
  console.log("Current theme =", theme);
  const isDark =
  theme === "dark"
    ? true
    : theme === "light"
    ? false
    : typeof window !== "undefined" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
  
  

  const handleSidebarViewChange = (view: SidebarView) => {
    setSidebarView(view);
  };

  const handleSelectDocument = (doc: string) => {
    setUploadedDocument(doc);
    setSidebarView("main");
  };

  const handleSelectChat = (id: string) => {
    loadConversation(id);
    setSidebarView("main");
  };

  const loadChats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`);

    console.log(response.status);

    if (!response.ok) {
      throw new Error("Failed to load conversations");
    }

    const data = await response.json();

    console.log(data);

    setChats(data);
  } catch (err) {
    console.error(err);
  }
};

  const loadConversation = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/${id}`);

      if (!response.ok) return;

      const data = await response.json();

      setConversationId(id);
      setMessages(data);
      } catch (err) {
      console.error(err);
    }
  };

  const loadDocuments = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents`);

    console.log(response.status);

    if (!response.ok)
      throw new Error("Failed to load documents");

    const docs = await response.json();

    console.log(docs);

    setDocuments(docs.map((d: { filename: string }) => d.filename));

    if(docs.length>0){
      setUploadedDocument(docs[0].filename);
    }

  } catch(err){
    console.error(err);
  }
};
  
  const send = async (text: string) => {
    try {
      setError(null);
      // Add user message to the UI immediately
      setMessages((m) => [...m, { role: "user", content: text }]);
      setLoading(true);


      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          conversation_id: conversationId,
        }),
      });


      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Update conversation ID if it's a new one
      if (!conversationId) {
      setConversationId(data.conversation_id);
      }

      await loadChats();

      // Add an empty assistant message first
      // Add an empty assistant message
setMessages((m) => [
  ...m,
  {
    role: "assistant",
    content: "",
  },
]);

// Animate the assistant reply
let currentText = "";

for (let i = 0; i < data.reply.length; i++) {
  currentText += data.reply[i];

  setMessages((prev) => {
    const updated = [...prev];
    updated[updated.length - 1] = {
      role: "assistant",
      content: currentText,
    };
    return updated;
  });

  await new Promise((resolve) => setTimeout(resolve, 12));
}
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);
      console.error("Chat error:", err);

      // Remove the user message if there was an error
      setMessages((m) => m.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const upload = async (file: File) => {
  try {
  setError(null);
  setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed (status ${response.status})`);
    }

    const data: UploadResponse = await response.json();
    console.log("Upload Response:", data);

    setUploadedDocument(data.filename);

    // Reload all documents from the backend
    await loadDocuments();

    setMessages((m) => [
  ...m,
  {
    role: "user",
    content: `📎 Uploaded: ${data.filename}`,
  },
  {
    role: "assistant",
    content: data.summary,
    suggestions: data.suggestions,
  },
]);
  } catch (err) {
    const errorMessage =
      err instanceof Error ? err.message : "Failed to upload file";
    setError(errorMessage);
    console.error("Upload error:", err);
  } finally {
    setUploading(false);
  }
};
  
  const summarizeDocument = async () => {
    try {
      setError(null);
      setLoading(true);

      const response = await fetch(`${API_BASE_URL}/features/summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document: uploadedDocument }),
      });

      if (!response.ok) {
        throw new Error("Failed to summarize document");
      }

      const data = await response.json();

      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
          `📄 Summary

            ${data.summary}

          🔹KEY POINTS
            • ${data.key_points.join("\n• ")}`,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Summary failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadInitialData = () => {
      void loadDocuments();
      void loadChats();
    };

    const timeoutId = window.setTimeout(loadInitialData, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  return (
  <div
  className={`flex h-screen overflow-hidden transition-colors duration-300 ${
    isDark
      ? "bg-slate-950 text-white"
      : "bg-gray-100 text-slate-900"
  }`}
>

  {showSidebar && (
  <Sidebar
  key={sidebarView}
  documents={documents}
  selected={uploadedDocument}
  onSelect={handleSelectDocument}
  chats={chats}
  selectedChat={conversationId}
  onSelectChat={handleSelectChat}
  sidebarView={sidebarView}
  setSidebarView={handleSidebarViewChange}
/>
)}

    {/* Chat Area */}
<div
  className={`flex-1 flex flex-col min-h-0 overflow-hidden transition-colors duration-300 ${
    isDark ? "bg-slate-950" : "bg-white"
  }`}
>

    <div className="shadow-xl px-6 py-4 flex items-center justify-between bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500">

  {/* Left */}
  <div className="flex items-center">
    <button
      onClick={() => setShowSidebar(!showSidebar)}
      className="p-2 rounded-lg hover:bg-white/10 transition"
    >
      <Menu size={24} className="text-white" />
    </button>
  </div>

    {/* Center */}
    <div className="text-center">
    <h1 className="text-2xl font-bold text-white">
      Smart Support Assistant
    </h1>

    {uploadedDocument && (
      <p className="text-sm text-cyan-100">
        📄 {uploadedDocument}
      </p>
    )}
    </div>

    <div className="w-20" />

  </div>

  <div className="flex-1 min-h-0">
  <MessageList
    messages={messages}
    loading={loading}
    onSuggestionClick={send}
  />
</div>

      {/* Input */}
      <MessageInput
        onSend={send}
        onUpload={upload}
        onSummary={summarizeDocument}
        disabled={loading || uploading}
      />
    </div>

    </div>

);

}