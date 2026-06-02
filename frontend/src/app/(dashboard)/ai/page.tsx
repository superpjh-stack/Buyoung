"use client";
import { useState } from "react";
import { aiApi } from "@/lib/api";
import { Send, Bot } from "lucide-react";

interface Message {
  role: "user" | "ai";
  text: string;
  sources?: { source: string; similarity: number }[];
}

const AGENTS = [
  { value: "INTEGRATED", label: "통합" },
  { value: "ORDER",      label: "수주·견적" },
  { value: "PRODUCTION", label: "생산·품질" },
  { value: "EQUIPMENT",  label: "설비·이상" },
];

export default function AiAgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", text: "안녕하세요! 부영기업 MES AI입니다. 공정 데이터에 대해 질의하세요." },
  ]);
  const [input, setInput] = useState("");
  const [agentType, setAgentType] = useState("INTEGRATED");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text: userMsg }]);
    setLoading(true);
    try {
      const res = await aiApi.query(userMsg, agentType);
      const d = res.data.data;
      setMessages((m) => [...m, {
        role: "ai",
        text: d.response,
        sources: d.retrieved_sources,
      }]);
    } catch {
      setMessages((m) => [...m, { role: "ai", text: "오류가 발생했습니다. 다시 시도해주세요." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] space-y-4">
      <div className="flex items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-900">AI Agent</h2>
        <div className="flex gap-2">
          {AGENTS.map((a) => (
            <button
              key={a.value}
              onClick={() => setAgentType(a.value)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                agentType === a.value
                  ? "bg-blue-600 text-white border-blue-600"
                  : "border-gray-300 text-gray-600 hover:border-blue-400"
              }`}
            >
              {a.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chat window */}
      <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            {m.role === "ai" && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                <Bot size={16} className="text-white" />
              </div>
            )}
            <div className={`max-w-lg rounded-2xl px-4 py-2.5 text-sm ${
              m.role === "user"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-900"
            }`}>
              <p className="whitespace-pre-wrap">{m.text}</p>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 space-y-0.5">
                  {m.sources.map((s, j) => (
                    <p key={j} className="text-xs text-gray-500">
                      📄 {s.source} ({(s.similarity * 100).toFixed(0)}%)
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-gray-100 rounded-2xl px-4 py-2.5 text-sm text-gray-500 animate-pulse">
              분석 중...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="예: 오늘 생산 현황 알려줘 / 불량률이 높은 공정은?"
          className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-blue-600 text-white rounded-xl px-4 py-2.5 hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
