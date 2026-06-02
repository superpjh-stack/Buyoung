"use client";
import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { orderApi, cadApi, quoteApi } from "@/lib/api";
import Link from "next/link";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Order {
  order_id: string;
  order_no: string;
  status: string;
  product_type: string;
  quantity: number;
  requested_delivery_date?: string;
}

interface Quote {
  quote_id: string;
  quote_no: string;
  total_amount: number;
  confidence_score: number;
  status: string;
}

interface BomItem {
  bom_id: string;
  material_name: string;
  quantity: number;
  unit: string;
}

interface CadDrawing {
  drawing_id: string;
  drawing_no: string;
  parse_status: string;
}

// ─── Config ──────────────────────────────────────────────────────────────────

const statusLabel: Record<string, { label: string; cls: string }> = {
  RECEIVED:    { label: "수주",   cls: "bg-blue-100 text-blue-700" },
  QUOTING:     { label: "견적중", cls: "bg-yellow-100 text-yellow-700" },
  CONFIRMED:   { label: "확정",   cls: "bg-green-100 text-green-700" },
  IN_PROGRESS: { label: "생산중", cls: "bg-purple-100 text-purple-700" },
  SHIPPED:     { label: "출하",   cls: "bg-gray-100 text-gray-600" },
};

const TABS = ["수주 목록", "CAD 도면 분석", "견적 관리", "BOM"] as const;
type Tab = typeof TABS[number];

// ─── Sub-tabs ─────────────────────────────────────────────────────────────────

function OrdersTab() {
  const { data, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => orderApi.list(),
  });
  const orders: Order[] = data?.data?.data?.items ?? data?.data?.data ?? [];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {isLoading ? (
        <div className="p-8 text-center text-gray-400">로딩 중...</div>
      ) : orders.length === 0 ? (
        <div className="p-8 text-center text-gray-400">수주 데이터 없음 (DB 연결 필요)</div>
      ) : (
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              {["수주번호", "제품 유형", "수량", "납기일", "상태"].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {orders.map((o) => {
              const st = statusLabel[o.status] ?? { label: o.status, cls: "bg-gray-100 text-gray-600" };
              return (
                <tr key={o.order_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-blue-600">
                    <Link href={`/orders/${o.order_id}`}>{o.order_no}</Link>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{o.product_type}</td>
                  <td className="px-4 py-3 text-gray-700">{o.quantity?.toLocaleString()} EA</td>
                  <td className="px-4 py-3 text-gray-500">{o.requested_delivery_date ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${st.cls}`}>{st.label}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}

function CadTab() {
  const [orderId, setOrderId] = useState("");
  const [drawingNo, setDrawingNo] = useState("");
  const [uploaded, setUploaded] = useState<CadDrawing | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const uploadMut = useMutation({
    mutationFn: (formData: FormData) => cadApi.upload(formData),
    onSuccess: (res) => {
      setUploaded(res.data?.data ?? res.data ?? null);
    },
  });

  const { data: statusRes } = useQuery({
    queryKey: ["cad-status", uploaded?.drawing_id],
    queryFn: () => cadApi.parseStatus(uploaded!.drawing_id),
    enabled: !!uploaded?.drawing_id && uploaded?.parse_status === "PENDING",
    refetchInterval: 3000,
  });

  const parseStatus = statusRes?.data?.data?.parse_status ?? uploaded?.parse_status;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file || !orderId || !drawingNo) return;
    const fd = new FormData();
    fd.append("order_id", orderId);
    fd.append("drawing_no", drawingNo);
    fd.append("file", file);
    uploadMut.mutate(fd);
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h4 className="text-sm font-semibold text-gray-800 mb-4">CAD 도면 업로드</h4>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">수주 ID</label>
              <input
                type="text"
                value={orderId}
                onChange={(e) => setOrderId(e.target.value)}
                placeholder="order_id 입력"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">도면 번호</label>
              <input
                type="text"
                value={drawingNo}
                onChange={(e) => setDrawingNo(e.target.value)}
                placeholder="drawing_no 입력"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">파일 선택</label>
            <input
              ref={fileRef}
              type="file"
              accept=".dwg,.dxf,.pdf,.png,.jpg"
              className="block w-full text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          <button
            type="submit"
            disabled={uploadMut.isPending}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {uploadMut.isPending ? "업로드 중..." : "업로드"}
          </button>
        </form>
      </div>

      {uploaded && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h4 className="text-sm font-semibold text-gray-800 mb-3">업로드 결과</h4>
          <div className="space-y-2 text-sm">
            <div className="flex gap-2">
              <span className="text-gray-500 w-24">도면 번호</span>
              <span className="font-medium text-gray-800">{uploaded.drawing_no}</span>
            </div>
            <div className="flex gap-2 items-center">
              <span className="text-gray-500 w-24">파싱 상태</span>
              {parseStatus === "PENDING" ? (
                <span className="inline-flex items-center gap-1.5 text-amber-600 text-xs font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                  파싱 중... (자동 갱신)
                </span>
              ) : parseStatus === "COMPLETED" ? (
                <span className="text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded-full">완료</span>
              ) : parseStatus === "FAILED" ? (
                <span className="text-xs font-medium text-red-700 bg-red-100 px-2 py-0.5 rounded-full">실패</span>
              ) : (
                <span className="text-xs text-gray-500">{parseStatus ?? "—"}</span>
              )}
            </div>
          </div>
        </div>
      )}

      {uploadMut.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
          업로드 실패. 서버 연결을 확인하세요.
        </div>
      )}
    </div>
  );
}

function QuoteTab() {
  const [orderId, setOrderId] = useState("");
  const [queriedId, setQueriedId] = useState("");
  const queryClient = useQueryClient();

  const { data: quoteRes, isLoading } = useQuery({
    queryKey: ["quotes", queriedId],
    queryFn: () => orderApi.quotes(queriedId),
    enabled: !!queriedId,
  });

  const quotes: Quote[] = quoteRes?.data?.data ?? [];

  const approveMut = useMutation({
    mutationFn: (id: string) => quoteApi.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["quotes", queriedId] }),
  });
  const rejectMut = useMutation({
    mutationFn: (id: string) => quoteApi.reject(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["quotes", queriedId] }),
  });

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h4 className="text-sm font-semibold text-gray-800 mb-3">견적 조회</h4>
        <div className="flex gap-2">
          <input
            type="text"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            placeholder="수주 ID 입력"
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            onClick={() => setQueriedId(orderId)}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            조회
          </button>
        </div>
      </div>

      {isLoading && <div className="text-center text-sm text-gray-400 py-4">조회 중...</div>}

      {quotes.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {quotes.map((q) => {
            const pct = Math.round(q.confidence_score * 100);
            return (
              <div key={q.quote_id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-xs text-gray-500">견적번호</p>
                    <p className="font-semibold text-gray-900 text-sm mt-0.5">{q.quote_no}</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    q.status === "APPROVED" ? "bg-green-100 text-green-700" :
                    q.status === "REJECTED" ? "bg-red-100 text-red-700" :
                    "bg-gray-100 text-gray-600"
                  }`}>{q.status}</span>
                </div>
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">금액</span>
                    <span className="font-semibold text-gray-800">
                      {q.total_amount?.toLocaleString()}원
                    </span>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>AI 신뢰도</span>
                      <span className="font-medium text-gray-700">{pct}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          pct >= 80 ? "bg-green-500" : pct >= 60 ? "bg-amber-400" : "bg-red-400"
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                </div>
                {q.status === "PENDING" && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => approveMut.mutate(q.quote_id)}
                      disabled={approveMut.isPending}
                      className="flex-1 py-1.5 text-xs font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                    >
                      승인
                    </button>
                    <button
                      onClick={() => rejectMut.mutate(q.quote_id)}
                      disabled={rejectMut.isPending}
                      className="flex-1 py-1.5 text-xs font-medium bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition-colors"
                    >
                      거절
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {queriedId && !isLoading && quotes.length === 0 && (
        <div className="text-center text-sm text-gray-400 py-6 bg-white rounded-xl border border-gray-100">
          해당 수주의 견적이 없습니다.
        </div>
      )}
    </div>
  );
}

function BomTab() {
  const [orderId, setOrderId] = useState("");
  const [queriedId, setQueriedId] = useState("");
  const queryClient = useQueryClient();

  const { data: bomRes, isLoading } = useQuery({
    queryKey: ["bom", queriedId],
    queryFn: () => orderApi.bom(queriedId),
    enabled: !!queriedId,
    retry: false,
  });

  const bomItems: BomItem[] = bomRes?.data?.data ?? [];
  const hasBom = bomRes?.data && !bomRes?.data?.error && bomItems.length > 0;

  const generateMut = useMutation({
    mutationFn: () => orderApi.generateBom(queriedId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bom", queriedId] }),
  });

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h4 className="text-sm font-semibold text-gray-800 mb-3">BOM 조회</h4>
        <div className="flex gap-2">
          <input
            type="text"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            placeholder="수주 ID 입력"
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            onClick={() => setQueriedId(orderId)}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            조회
          </button>
        </div>
      </div>

      {isLoading && <div className="text-center text-sm text-gray-400 py-4">조회 중...</div>}

      {queriedId && !isLoading && !hasBom && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
          <p className="text-sm text-gray-500 mb-4">BOM 데이터가 없습니다.</p>
          <button
            onClick={() => generateMut.mutate()}
            disabled={generateMut.isPending}
            className="px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {generateMut.isPending ? "생성 중..." : "BOM 자동 생성"}
          </button>
          {generateMut.isError && (
            <p className="mt-3 text-xs text-red-500">생성 실패. 서버를 확인하세요.</p>
          )}
        </div>
      )}

      {hasBom && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["자재명", "수량", "단위"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {bomItems.map((b) => (
                <tr key={b.bom_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-800 font-medium">{b.material_name}</td>
                  <td className="px-4 py-3 text-gray-700 tabular-nums">{b.quantity?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-gray-500">{b.unit}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function OrdersPage() {
  const [activeTab, setActiveTab] = useState<Tab>("수주 목록");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">수주견적AI관리</h2>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeTab === tab
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "수주 목록" && <OrdersTab />}
      {activeTab === "CAD 도면 분석" && <CadTab />}
      {activeTab === "견적 관리" && <QuoteTab />}
      {activeTab === "BOM" && <BomTab />}
    </div>
  );
}
