"use client";
import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { receivingApi, aiApi } from "@/lib/api";
import {
  PackageSearch, History, Star, Bot,
  Search, Send, CheckCircle, AlertTriangle,
  XCircle, Package, Truck, Calendar,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

type TabId = "incoming" | "history" | "supplier" | "ai";

interface ReceivingLot {
  lot_id: string;
  lot_number: string;
  supplier_name: string;
  material_name: string;
  quantity: number;
  unit: string;
  received_at: string;
  status: "PENDING" | "ACCEPTED" | "REJECTED" | "QUARANTINE";
  inspector?: string;
}

interface HistoryEvent {
  event_id: string;
  event_type: string;
  description: string;
  created_at: string;
  actor?: string;
}

interface SupplierScore {
  supplier_id: string;
  supplier_name: string;
  quality_score: number;
  delivery_rate: number;
  defect_rate: number;
  total_lots: number;
  grade: "A" | "B" | "C" | "D";
}

interface ChatMessage {
  role: "user" | "ai";
  text: string;
  sources?: { source: string; similarity: number }[];
}

// ─── Config ───────────────────────────────────────────────────────────────────

const lotStatusCfg: Record<
  string,
  { label: string; cls: string; icon: React.ReactNode }
> = {
  PENDING:    { label: "검사 대기", cls: "bg-gray-100 text-gray-600",    icon: <Package size={11} /> },
  ACCEPTED:   { label: "입고 승인", cls: "bg-green-100 text-green-700",  icon: <CheckCircle size={11} /> },
  REJECTED:   { label: "반품 처리", cls: "bg-red-100 text-red-700",      icon: <XCircle size={11} /> },
  QUARANTINE: { label: "격리 보관", cls: "bg-amber-100 text-amber-700",  icon: <AlertTriangle size={11} /> },
};

const gradeCfg: Record<string, { cls: string; bar: string }> = {
  A: { cls: "bg-green-100 text-green-700",  bar: "bg-green-500" },
  B: { cls: "bg-blue-100 text-blue-700",    bar: "bg-blue-500"  },
  C: { cls: "bg-amber-100 text-amber-700",  bar: "bg-amber-400" },
  D: { cls: "bg-red-100 text-red-700",      bar: "bg-red-500"   },
};

// ─── Mock data (shown when API is unavailable) ────────────────────────────────

const MOCK_LOTS: ReceivingLot[] = [
  { lot_id: "1", lot_number: "RC-2026-0601", supplier_name: "한국철강(주)", material_name: "SPCC 냉연강판 1.2T", quantity: 5000, unit: "kg", received_at: "2026-06-01T09:00:00", status: "ACCEPTED",   inspector: "김검사" },
  { lot_id: "2", lot_number: "RC-2026-0602", supplier_name: "동양스틸",      material_name: "SS400 열연강판 2.3T", quantity: 3200, unit: "kg", received_at: "2026-06-02T10:30:00", status: "QUARANTINE", inspector: "이검사" },
  { lot_id: "3", lot_number: "RC-2026-0603", supplier_name: "포스코특수강",  material_name: "STS304 스테인리스 1.5T", quantity: 1800, unit: "kg", received_at: "2026-06-02T14:00:00", status: "PENDING",   inspector: undefined },
  { lot_id: "4", lot_number: "RC-2026-0604", supplier_name: "한국철강(주)", material_name: "SPHC 열연코일 2.0T",  quantity: 6500, unit: "kg", received_at: "2026-06-03T08:00:00", status: "ACCEPTED",   inspector: "김검사" },
  { lot_id: "5", lot_number: "RC-2026-0605", supplier_name: "세진철강",      material_name: "아연도금강판 1.0T",   quantity: 2400, unit: "kg", received_at: "2026-06-03T11:00:00", status: "REJECTED",  inspector: "박검사" },
];

const MOCK_HISTORY: HistoryEvent[] = [
  { event_id: "h1", event_type: "RECEIVED",   description: "원자재 입고 등록",             created_at: "2026-06-01T09:00:00", actor: "시스템" },
  { event_id: "h2", event_type: "INSPECTION",  description: "수입검사 개시 (QS-INC-001)",  created_at: "2026-06-01T10:30:00", actor: "김검사" },
  { event_id: "h3", event_type: "ACCEPTED",    description: "검사 합격 — 창고 이동 지시",  created_at: "2026-06-01T11:00:00", actor: "김검사" },
  { event_id: "h4", event_type: "STORED",      description: "A-03 창고 위치에 보관 완료",  created_at: "2026-06-01T11:45:00", actor: "박창고" },
];

const MOCK_SUPPLIERS: SupplierScore[] = [
  { supplier_id: "s1", supplier_name: "한국철강(주)",  quality_score: 96, delivery_rate: 98, defect_rate: 0.8, total_lots: 42, grade: "A" },
  { supplier_id: "s2", supplier_name: "동양스틸",      quality_score: 88, delivery_rate: 92, defect_rate: 2.1, total_lots: 28, grade: "B" },
  { supplier_id: "s3", supplier_name: "포스코특수강",  quality_score: 94, delivery_rate: 96, defect_rate: 1.2, total_lots: 35, grade: "A" },
  { supplier_id: "s4", supplier_name: "세진철강",      quality_score: 71, delivery_rate: 78, defect_rate: 5.4, total_lots: 14, grade: "C" },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function TabButton({
  active,
  onClick,
  icon,
  children,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
        active
          ? "border-blue-600 text-blue-600"
          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
      }`}
    >
      {icon}
      {children}
    </button>
  );
}

// ─── Tab: 입고관리 ────────────────────────────────────────────────────────────

function IncomingTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["receiving-lots"],
    queryFn: () => receivingApi.list({ limit: 20 }),
  });

  const lots: ReceivingLot[] = data?.data?.data ?? MOCK_LOTS;

  const statusCounts = lots.reduce(
    (acc, l) => { acc[l.status] = (acc[l.status] ?? 0) + 1; return acc; },
    {} as Record<string, number>
  );

  return (
    <div className="space-y-5">
      {/* Summary strip */}
      {/*
        ┌──────────┬──────────┬──────────┬──────────┐
        │입고 승인 │검사 대기 │격리 보관 │반품 처리 │
        │    3     │    1     │    1     │    1     │
        └──────────┴──────────┴──────────┴──────────┘
      */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { key: "ACCEPTED",   label: "입고 승인", color: "text-green-700", bg: "bg-green-50 border-green-100" },
          { key: "PENDING",    label: "검사 대기", color: "text-gray-700",  bg: "bg-gray-50 border-gray-100"  },
          { key: "QUARANTINE", label: "격리 보관", color: "text-amber-700", bg: "bg-amber-50 border-amber-100"},
          { key: "REJECTED",   label: "반품 처리", color: "text-red-700",   bg: "bg-red-50 border-red-100"    },
        ].map((s) => (
          <div key={s.key} className={`rounded-xl border p-4 text-center ${s.bg}`}>
            <p className={`text-2xl font-bold ${s.color}`}>{statusCounts[s.key] ?? 0}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* LOT table */}
      {/*
        ┌─────────┬────────────┬────────────┬───────┬──────┬──────────┬──────────┐
        │LOT 번호 │공급처      │품목        │수량   │검사자│입고일    │상태      │
        ├─────────┼────────────┼────────────┼───────┼──────┼──────────┼──────────┤
        │RC-0601  │한국철강    │SPCC 1.2T   │5,000kg│김검사│06-01     │입고승인  │
        │...      │...         │...         │...    │...   │...       │...       │
        └─────────┴────────────┴────────────┴───────┴──────┴──────────┴──────────┘
      */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-50 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">입고 LOT 목록</h3>
          <span className="text-xs text-gray-400">{lots.length}건</span>
        </div>
        {isLoading ? (
          <div className="flex items-center justify-center h-32 text-sm text-gray-400">
            로딩 중...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">LOT 번호</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">공급처</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">품목</th>
                  <th className="text-right text-xs font-medium text-gray-500 px-3 py-3">수량</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">검사자</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">입고일</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">상태</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {lots.map((lot) => {
                  const cfg = lotStatusCfg[lot.status] ?? lotStatusCfg.PENDING;
                  return (
                    <tr key={lot.lot_id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3 font-mono text-xs text-blue-600 font-medium">
                        {lot.lot_number}
                      </td>
                      <td className="px-3 py-3 text-gray-700 text-xs">{lot.supplier_name}</td>
                      <td className="px-3 py-3 text-gray-700 text-xs max-w-[180px] truncate">
                        {lot.material_name}
                      </td>
                      <td className="px-3 py-3 text-right text-gray-700 text-xs tabular-nums">
                        {lot.quantity.toLocaleString()} {lot.unit}
                      </td>
                      <td className="px-3 py-3 text-gray-500 text-xs">
                        {lot.inspector ?? <span className="text-gray-300">미배정</span>}
                      </td>
                      <td className="px-3 py-3 text-gray-500 text-xs flex items-center gap-1">
                        <Calendar size={11} />
                        {new Date(lot.received_at).toLocaleDateString("ko-KR", {
                          month: "2-digit", day: "2-digit",
                        })}
                      </td>
                      <td className="px-5 py-3">
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${cfg.cls}`}>
                          {cfg.icon}
                          {cfg.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Tab: 원자재이력 ─────────────────────────────────────────────────────────

function HistoryTab() {
  const [lotId, setLotId] = useState("");
  const [searchedId, setSearchedId] = useState("");

  const { data, isFetching } = useQuery({
    queryKey: ["lot-history", searchedId],
    queryFn: () => receivingApi.history(searchedId),
    enabled: !!searchedId,
  });

  const events: HistoryEvent[] = data?.data?.data ?? (searchedId ? MOCK_HISTORY : []);

  const eventIconMap: Record<string, React.ReactNode> = {
    RECEIVED:   <Truck size={13} className="text-blue-500" />,
    INSPECTION: <Search size={13} className="text-violet-500" />,
    ACCEPTED:   <CheckCircle size={13} className="text-green-500" />,
    REJECTED:   <XCircle size={13} className="text-red-500" />,
    STORED:     <Package size={13} className="text-gray-400" />,
  };

  return (
    <div className="space-y-5 max-w-2xl">
      {/* Search box */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">LOT ID로 이력 조회</h3>
        <div className="flex gap-2">
          <input
            value={lotId}
            onChange={(e) => setLotId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && setSearchedId(lotId.trim())}
            placeholder="LOT 번호 입력 (예: RC-2026-0601)"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={() => setSearchedId(lotId.trim())}
            disabled={!lotId.trim() || isFetching}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Search size={14} />
            조회
          </button>
        </div>
        {searchedId && (
          <p className="text-xs text-gray-400 mt-2">
            조회 중: <span className="font-mono text-blue-600">{searchedId}</span>
          </p>
        )}
      </div>

      {/* Timeline */}
      {/*
        ┌───────────────────────────────────────┐
        │ 이력 타임라인                          │
        │  ●─── 입고 등록       09:00  시스템   │
        │  ●─── 수입검사 개시   10:30  김검사   │
        │  ●─── 검사 합격       11:00  김검사   │
        │  ●─── 창고 보관 완료  11:45  박창고   │
        └───────────────────────────────────────┘
      */}
      {searchedId && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <History size={15} className="text-gray-400" />
            이력 타임라인
          </h3>
          {isFetching ? (
            <p className="text-sm text-gray-400 animate-pulse">조회 중...</p>
          ) : events.length === 0 ? (
            <p className="text-sm text-gray-400">이력 없음</p>
          ) : (
            <ol className="relative border-l border-gray-200 ml-2 space-y-0">
              {events.map((ev, idx) => (
                <li key={ev.event_id} className={`pl-6 ${idx !== events.length - 1 ? "pb-5" : "pb-0"}`}>
                  <span className="absolute -left-[7px] flex items-center justify-center w-3.5 h-3.5 rounded-full bg-white border-2 border-blue-400 ring-4 ring-white">
                    {eventIconMap[ev.event_type] ?? <span className="w-1 h-1 rounded-full bg-gray-400" />}
                  </span>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{ev.description}</p>
                      {ev.actor && (
                        <p className="text-xs text-gray-400 mt-0.5">처리: {ev.actor}</p>
                      )}
                    </div>
                    <time className="text-xs text-gray-400 whitespace-nowrap mt-0.5">
                      {new Date(ev.created_at).toLocaleTimeString("ko-KR", {
                        hour: "2-digit", minute: "2-digit",
                      })}
                    </time>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Tab: 공급처품질 ─────────────────────────────────────────────────────────

function SupplierQualityTab() {
  const { data } = useQuery({
    queryKey: ["supplier-quality"],
    queryFn: () => receivingApi.supplierQuality(),
  });

  const suppliers: SupplierScore[] = data?.data?.data ?? MOCK_SUPPLIERS;

  return (
    <div className="space-y-5">
      {/* Supplier score cards */}
      {/*
        ┌──────────────────┬──────────────────┐
        │한국철강(주)  [A] │동양스틸      [B] │
        │품질점수: 96     │품질점수: 88     │
        │납기준수: 98%    │납기준수: 92%    │
        │불량률:  0.8%    │불량률:  2.1%    │
        │입고실적: 42건   │입고실적: 28건   │
        │████████████████ │████████████░░░░ │
        └──────────────────┴──────────────────┘
      */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-2">
        {suppliers.map((s) => {
          const gcfg = gradeCfg[s.grade] ?? gradeCfg.B;
          return (
            <div key={s.supplier_id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="font-semibold text-gray-900">{s.supplier_name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">입고 실적 {s.total_lots}건</p>
                </div>
                <span className={`text-sm font-bold px-3 py-1 rounded-lg ${gcfg.cls}`}>
                  {s.grade}등급
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                {[
                  { label: "품질점수", value: s.quality_score, unit: "점" },
                  { label: "납기준수", value: s.delivery_rate, unit: "%" },
                  { label: "불량률",   value: s.defect_rate,   unit: "%" },
                ].map((m) => (
                  <div key={m.label} className="bg-gray-50 rounded-lg p-2.5 text-center">
                    <p className="text-lg font-bold text-gray-900 tabular-nums">{m.value}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{m.unit}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{m.label}</p>
                  </div>
                ))}
              </div>

              {/* Quality score bar */}
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>종합 품질점수</span>
                  <span>{s.quality_score}/100</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${gcfg.bar} transition-all duration-700`}
                    style={{ width: `${s.quality_score}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Grading legend */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <h4 className="text-xs font-semibold text-gray-700 mb-3">등급 기준</h4>
        <div className="flex flex-wrap gap-4">
          {[
            { grade: "A", desc: "90점 이상 · 우수 공급처",    cls: gradeCfg.A.cls },
            { grade: "B", desc: "80~89점 · 일반 공급처",     cls: gradeCfg.B.cls },
            { grade: "C", desc: "70~79점 · 주의 요망",       cls: gradeCfg.C.cls },
            { grade: "D", desc: "70점 미만 · 계약 검토 필요", cls: gradeCfg.D.cls },
          ].map((g) => (
            <div key={g.grade} className="flex items-center gap-2">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${g.cls}`}>{g.grade}</span>
              <span className="text-xs text-gray-500">{g.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Tab: AI Agent ────────────────────────────────────────────────────────────

const QUICK_PROMPTS = [
  "이번 주 입고된 LOT 현황을 요약해줘",
  "격리 보관 중인 자재 조치 방법 알려줘",
  "공급처 품질 점수가 낮은 이유를 분석해줘",
  "수입검사 불합격 이력이 있는 공급처는?",
];

function AiAgentTab() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "ai",
      text: "안녕하세요! 입고·재고 관련 AI 에이전트입니다.\n원자재 입고 현황, LOT 이력, 공급처 품질 분석 등을 질의하세요.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text?: string) => {
    const query = (text ?? input).trim();
    if (!query || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: query }]);
    setLoading(true);
    try {
      const res = await aiApi.query(query, "PRODUCTION");
      const d = res.data.data;
      setMessages((m) => [...m, {
        role: "ai",
        text: d.response,
        sources: d.retrieved_sources,
      }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "ai", text: "오류가 발생했습니다. 잠시 후 다시 시도해주세요." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-14rem)]">
      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2 mb-4">
        {QUICK_PROMPTS.map((p) => (
          <button
            key={p}
            onClick={() => send(p)}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded-full border border-gray-200 text-gray-600 bg-white hover:border-blue-400 hover:text-blue-600 transition-colors disabled:opacity-50"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chat window */}
      {/*
        ┌──────────────────────────────────────────────────────┐
        │  [AI] 안녕하세요! ...                                 │
        │                              [USER] 이번 주 입고 현황 │
        │  [AI] 이번 주 입고된 LOT는 총 5건...                  │
        └──────────────────────────────────────────────────────┘
        │ [입력창                                  ] [전송 ▶]   │
        └──────────────────────────────────────────────────────┘
      */}
      <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "ai" && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                <Bot size={15} className="text-white" />
              </div>
            )}
            <div
              className={`max-w-lg rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-blue-600 text-white rounded-br-sm"
                  : "bg-gray-100 text-gray-900 rounded-bl-sm"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.text}</p>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200 space-y-0.5">
                  {m.sources.map((s, j) => (
                    <p key={j} className="text-xs text-gray-500">
                      참조: {s.source} ({(s.similarity * 100).toFixed(0)}%)
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
              <Bot size={15} className="text-white" />
            </div>
            <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-gray-500">
              <span className="animate-pulse">분석 중...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="flex gap-2 mt-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="입고 LOT 현황, 공급처 품질, 자재 이력을 질의하세요"
          className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <button
          onClick={() => send()}
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white rounded-xl px-4 py-2.5 hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: "incoming", label: "입고관리",    icon: <PackageSearch size={14} /> },
  { id: "history",  label: "원자재이력",  icon: <History size={14} /> },
  { id: "supplier", label: "공급처품질",  icon: <Star size={14} /> },
  { id: "ai",       label: "AI Agent",   icon: <Bot size={14} /> },
];

export default function ReceivingPage() {
  const [activeTab, setActiveTab] = useState<TabId>("incoming");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">입고 · 재고 관리</h2>
          <p className="text-sm text-gray-500 mt-0.5">원자재 입고 LOT 관리 · 공급처 품질 이력 · AI 분석</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500 bg-white border border-gray-100 rounded-lg px-3 py-2 shadow-sm">
          <Truck size={13} />
          <span>입고 모니터링 활성</span>
        </div>
      </div>

      {/* Tab bar */}
      {/*
        ┌──────────────────────────────────────────────────────┐
        │ [입고관리] | [원자재이력] | [공급처품질] | [AI Agent]│
        │ ─────────  |             |              |            │
        └──────────────────────────────────────────────────────┘
      */}
      <div className="border-b border-gray-200">
        <div className="flex gap-0">
          {TABS.map((t) => (
            <TabButton
              key={t.id}
              active={activeTab === t.id}
              onClick={() => setActiveTab(t.id)}
              icon={t.icon}
            >
              {t.label}
            </TabButton>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {activeTab === "incoming" && <IncomingTab />}
      {activeTab === "history"  && <HistoryTab />}
      {activeTab === "supplier" && <SupplierQualityTab />}
      {activeTab === "ai"       && <AiAgentTab />}
    </div>
  );
}
