"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workOrderApi, productionApi, equipmentApi } from "@/lib/api";
import { useState } from "react";
import {
  ClipboardList, Play, CheckCircle, Clock,
  BarChart2, Activity, History, Cpu, Search,
} from "lucide-react";

interface WorkOrder {
  work_order_id: string;
  work_order_no: string;
  order_id: string;
  bom_id: string;
  status: string;
  planned_qty: number;
  planned_start_date?: string;
  planned_end_date?: string;
  created_at: string;
}

const statusConfig: Record<string, { label: string; cls: string; icon: React.ReactNode }> = {
  PLANNED:     { label: "계획",   cls: "bg-gray-100 text-gray-600",   icon: <Clock size={12} /> },
  IN_PROGRESS: { label: "생산중", cls: "bg-blue-100 text-blue-700",   icon: <Play size={12} /> },
  COMPLETED:   { label: "완료",   cls: "bg-green-100 text-green-700", icon: <CheckCircle size={12} /> },
};

const nextStatus: Record<string, string> = {
  PLANNED: "IN_PROGRESS",
  IN_PROGRESS: "COMPLETED",
};

// Mock data for tabs without live endpoints
const MOCK_PROCESS_OUTPUT = [
  { process: "성형 (Forming)",   today: 1240, target: 1500, unit: "EA" },
  { process: "용접 (Welding)",   today: 980,  target: 1200, unit: "EA" },
  { process: "도장 (Painting)",  today: 860,  target: 1000, unit: "EA" },
  { process: "포장 (Packing)",   today: 820,  target: 1000, unit: "EA" },
];

const MOCK_SENSOR: Record<string, { value: number; unit: string; min: number; max: number; warn: number }> = {
  "속도 (Speed)":   { value: 72,  unit: "rpm",  min: 0,  max: 100, warn: 90 },
  "압력 (Pressure)":{ value: 8.4, unit: "bar",  min: 0,  max: 12,  warn: 10 },
  "온도 (Temp)":    { value: 187, unit: "°C",   min: 150, max: 220, warn: 210 },
};

const MOCK_HISTORY = [
  { date: "2026-06-02", process: "성형", lot: "LOT-2026-0602-01", qty: 1240, operator: "김철수", result: "정상" },
  { date: "2026-06-02", process: "용접", lot: "LOT-2026-0602-01", qty: 980,  operator: "이영희", result: "정상" },
  { date: "2026-06-01", process: "성형", lot: "LOT-2026-0601-02", qty: 1300, operator: "박민준", result: "정상" },
  { date: "2026-06-01", process: "도장", lot: "LOT-2026-0601-02", qty: 1280, operator: "최수진", result: "경고" },
  { date: "2026-05-31", process: "포장", lot: "LOT-2026-0531-01", qty: 950,  operator: "정다은", result: "정상" },
];

// Equipment sensor dummy data for 공정 데이터 tab
const EQUIPMENT_SENSORS = [
  {
    eq_id: "EQ-FORMING-01",
    name: "성형기 1호",
    sensors: [
      { label: "압력", value: 6.2, unit: "MPa", min: 5, max: 8, status: "정상" },
      { label: "속도", value: 3.1, unit: "m/min", min: 2, max: 4, status: "정상" },
    ],
    overall: "정상",
  },
  {
    eq_id: "EQ-WELDING-01",
    name: "용접기 1호",
    sensors: [
      { label: "전류", value: 175, unit: "A", min: 150, max: 200, status: "정상" },
      { label: "전압", value: 24, unit: "V", min: 22, max: 26, status: "정상" },
    ],
    overall: "정상",
  },
  {
    eq_id: "EQ-CUTTING-01",
    name: "절단기 1호",
    sensors: [
      { label: "속도", value: 0.7, unit: "m/min", min: 0.5, max: 1.0, status: "주의" },
    ],
    overall: "주의",
  },
];

const overallCls: Record<string, string> = {
  정상: "bg-green-100 text-green-700 border-gray-100",
  주의: "bg-yellow-100 text-yellow-700 border-yellow-200",
  이상: "bg-red-100 text-red-700 border-red-200",
};

const TABS = [
  { key: "orders",      label: "작업지시",     icon: ClipboardList },
  { key: "output",      label: "공정실적",     icon: BarChart2 },
  { key: "monitoring",  label: "데이터모니터링", icon: Activity },
  { key: "history",     label: "공정이력",     icon: History },
  { key: "sensor",      label: "공정 데이터",   icon: Cpu },
  { key: "forming",     label: "성형 이력",     icon: Search },
] as const;

type Tab = typeof TABS[number]["key"];

export default function ProductionPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("orders");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [formingLotId, setFormingLotId] = useState("");
  const [formingLotInput, setFormingLotInput] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["work-orders", statusFilter],
    queryFn: () => workOrderApi.list(statusFilter ? { status: statusFilter } : undefined),
    refetchInterval: 15_000,
  });

  const { data: formingRes, isLoading: formingLoading } = useQuery({
    queryKey: ["forming-history", formingLotId],
    queryFn: () => productionApi.listForming(formingLotId),
    enabled: !!formingLotId,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      workOrderApi.updateStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["work-orders"] }),
  });

  const orders: WorkOrder[] = data?.data?.data ?? [];

  const counts = {
    PLANNED:     orders.filter((o) => o.status === "PLANNED").length,
    IN_PROGRESS: orders.filter((o) => o.status === "IN_PROGRESS").length,
    COMPLETED:   orders.filter((o) => o.status === "COMPLETED").length,
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">공정관리</h2>
        <span className="text-sm text-gray-400">15초마다 갱신</span>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* === 작업지시 탭 === */}
      {tab === "orders" && (
        <>
          <div className="grid grid-cols-3 gap-4">
            {(["PLANNED", "IN_PROGRESS", "COMPLETED"] as const).map((s) => {
              const cfg = statusConfig[s];
              return (
                <button
                  key={s}
                  onClick={() => setStatusFilter(statusFilter === s ? "" : s)}
                  className={`bg-white rounded-xl border p-4 text-left transition-all ${
                    statusFilter === s ? "border-blue-500 ring-1 ring-blue-500" : "border-gray-100"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${cfg.cls}`}>
                      {cfg.icon} {cfg.label}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{counts[s]}</p>
                  <p className="text-xs text-gray-400 mt-0.5">작업지시</p>
                </button>
              );
            })}
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
              <ClipboardList size={16} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                작업지시 목록 {statusFilter && `— ${statusConfig[statusFilter]?.label}`}
              </span>
            </div>
            {isLoading ? (
              <div className="p-8 text-center text-gray-400 text-sm">로딩 중...</div>
            ) : orders.length === 0 ? (
              <div className="p-8 text-center text-gray-400 text-sm">
                작업지시 없음 (DB 연결 확인 필요)
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    {["작업지시번호", "계획 수량", "시작일", "완료 예정일", "상태", "액션"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {orders.map((wo) => {
                    const cfg = statusConfig[wo.status] ?? statusConfig.PLANNED;
                    const next = nextStatus[wo.status];
                    return (
                      <tr key={wo.work_order_id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">{wo.work_order_no}</td>
                        <td className="px-4 py-3 text-gray-700">{wo.planned_qty?.toLocaleString()} EA</td>
                        <td className="px-4 py-3 text-gray-500">{wo.planned_start_date ?? "—"}</td>
                        <td className="px-4 py-3 text-gray-500">{wo.planned_end_date ?? "—"}</td>
                        <td className="px-4 py-3">
                          <span className={`flex items-center gap-1 w-fit text-xs px-2 py-0.5 rounded-full ${cfg.cls}`}>
                            {cfg.icon} {cfg.label}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {next && (
                            <button
                              disabled={mutation.isPending}
                              onClick={() => mutation.mutate({ id: wo.work_order_id, status: next })}
                              className="text-xs px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                            >
                              {next === "IN_PROGRESS" ? "생산 시작" : "완료 처리"}
                            </button>
                          )}
                          {wo.status === "COMPLETED" && (
                            <span className="text-xs text-green-600 font-medium">완료됨</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {/* === 공정실적 탭 === */}
      {tab === "output" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
            {MOCK_PROCESS_OUTPUT.map((p) => {
              const pct = Math.round((p.today / p.target) * 100);
              const color = pct >= 90 ? "bg-green-500" : pct >= 70 ? "bg-blue-500" : "bg-yellow-500";
              return (
                <div key={p.process} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                  <p className="text-xs text-gray-500 font-medium mb-1">{p.process}</p>
                  <p className="text-2xl font-bold text-gray-900">{p.today.toLocaleString()}</p>
                  <p className="text-xs text-gray-400 mb-3">목표: {p.target.toLocaleString()} {p.unit}</p>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${color}`}
                      style={{ width: `${Math.min(pct, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-right mt-1 text-gray-500">{pct}%</p>
                </div>
              );
            })}
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100">
              <span className="text-sm font-medium text-gray-700">공정별 실적 상세</span>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {["공정", "당일 생산량", "목표 수량", "달성률", "상태"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {MOCK_PROCESS_OUTPUT.map((p) => {
                  const pct = Math.round((p.today / p.target) * 100);
                  const statusCls = pct >= 90 ? "bg-green-100 text-green-700" : pct >= 70 ? "bg-blue-100 text-blue-700" : "bg-yellow-100 text-yellow-700";
                  const statusLabel = pct >= 90 ? "정상" : pct >= 70 ? "주의" : "미달";
                  return (
                    <tr key={p.process} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-medium text-gray-900">{p.process}</td>
                      <td className="px-4 py-3 text-gray-700">{p.today.toLocaleString()} {p.unit}</td>
                      <td className="px-4 py-3 text-gray-500">{p.target.toLocaleString()} {p.unit}</td>
                      <td className="px-4 py-3 font-medium text-gray-900">{pct}%</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${statusCls}`}>{statusLabel}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === 데이터모니터링 탭 === */}
      {tab === "monitoring" && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(MOCK_SENSOR).map(([name, s]) => {
              const pct = ((s.value - s.min) / (s.max - s.min)) * 100;
              const isWarn = s.value >= s.warn;
              return (
                <div
                  key={name}
                  className={`bg-white rounded-xl border shadow-sm p-5 ${isWarn ? "border-yellow-300" : "border-gray-100"}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-xs font-medium text-gray-500">{name}</p>
                    {isWarn && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">경고</span>
                    )}
                  </div>
                  <p className={`text-3xl font-bold ${isWarn ? "text-yellow-600" : "text-gray-900"}`}>
                    {s.value}
                    <span className="text-base font-normal text-gray-400 ml-1">{s.unit}</span>
                  </p>
                  <div className="mt-4 w-full bg-gray-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${isWarn ? "bg-yellow-400" : "bg-blue-500"}`}
                      style={{ width: `${Math.min(pct, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-1">
                    <span className="text-xs text-gray-400">{s.min}{s.unit}</span>
                    <span className="text-xs text-gray-400">{s.max}{s.unit}</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-sm font-medium text-blue-700 mb-1">실시간 센서 데이터</p>
            <p className="text-xs text-blue-600">
              설비 API 연결 시 <span className="font-mono">/v1/equipment/:id/sensor-data</span> 를 통해 실시간 갱신됩니다.
              현재는 시뮬레이션 값을 표시합니다.
            </p>
          </div>
        </div>
      )}

      {/* === 공정이력 탭 === */}
      {tab === "history" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
            <History size={16} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-700">공정이력</span>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["날짜", "공정", "LOT ID", "생산량", "작업자", "결과"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {MOCK_HISTORY.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-500">{row.date}</td>
                  <td className="px-4 py-3 text-gray-700">{row.process}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-900">{row.lot}</td>
                  <td className="px-4 py-3 text-gray-700">{row.qty.toLocaleString()} EA</td>
                  <td className="px-4 py-3 text-gray-700">{row.operator}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      row.result === "정상" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                    }`}>
                      {row.result}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* === 공정 데이터 탭 === */}
      {tab === "sensor" && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            {EQUIPMENT_SENSORS.map((eq) => {
              const badgeCls = overallCls[eq.overall] ?? overallCls["정상"];
              const borderCls = eq.overall === "주의" ? "border-yellow-200" : eq.overall === "이상" ? "border-red-200" : "border-gray-100";
              return (
                <div key={eq.eq_id} className={`bg-white rounded-xl border shadow-sm p-5 ${borderCls}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-xs font-mono text-gray-400">{eq.eq_id}</p>
                      <p className="text-sm font-semibold text-gray-900">{eq.name}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${badgeCls.split(" ").slice(0, 2).join(" ")}`}>
                      {eq.overall}
                    </span>
                  </div>
                  <div className="space-y-3">
                    {eq.sensors.map((s) => {
                      const pct = ((s.value - s.min) / (s.max - s.min)) * 100;
                      const barCls = s.status === "이상" ? "bg-red-500" : s.status === "주의" ? "bg-yellow-400" : "bg-blue-500";
                      return (
                        <div key={s.label}>
                          <div className="flex justify-between items-baseline mb-1">
                            <span className="text-xs text-gray-500">{s.label}</span>
                            <span className="text-sm font-bold text-gray-900">
                              {s.value}
                              <span className="text-xs font-normal text-gray-400 ml-1">{s.unit}</span>
                            </span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-1.5">
                            <div
                              className={`h-1.5 rounded-full ${barCls}`}
                              style={{ width: `${Math.min(Math.max(pct, 0), 100)}%` }}
                            />
                          </div>
                          <div className="flex justify-between mt-0.5">
                            <span className="text-xs text-gray-300">{s.min}{s.unit}</span>
                            <span className="text-xs text-gray-300">{s.max}{s.unit}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-xs text-blue-600">
              실시간 센서 API 연결 시 <span className="font-mono">/v1/equipment/:id/sensor-data</span> 를 통해 자동 갱신됩니다. 현재는 더미 값을 표시합니다.
            </p>
          </div>
        </div>
      )}

      {/* === 성형 이력 탭 === */}
      {tab === "forming" && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">LOT ID로 성형 공정 이력 조회</h3>
            <div className="flex gap-2">
              <input
                value={formingLotInput}
                onChange={(e) => setFormingLotInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && setFormingLotId(formingLotInput.trim())}
                placeholder="LOT ID 입력 (예: uuid)"
                className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => setFormingLotId(formingLotInput.trim())}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                조회
              </button>
              {formingLotId && (
                <button
                  onClick={() => { setFormingLotId(""); setFormingLotInput(""); }}
                  className="px-4 py-2 border border-gray-200 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
                >
                  초기화
                </button>
              )}
            </div>
          </div>

          {formingLotId && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
                <Cpu size={16} className="text-gray-400" />
                <span className="text-sm font-medium text-gray-700">성형 공정 이력</span>
                <span className="ml-auto text-xs font-mono text-gray-400">{formingLotId}</span>
              </div>
              {formingLoading ? (
                <div className="p-8 text-center text-gray-400 text-sm">조회 중...</div>
              ) : (() => {
                  const rows: Array<{
                    forming_id?: string;
                    recorded_at?: string;
                    defect_flag?: boolean;
                    defect_count?: number;
                  }> = formingRes?.data?.data ?? [];
                  return rows.length === 0 ? (
                    <div className="p-8 text-center text-gray-400 text-sm">
                      성형 이력 없음 (LOT ID 확인 또는 DB 연결 필요)
                    </div>
                  ) : (
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 border-b border-gray-100">
                        <tr>
                          {["기록 시각", "불량 여부", "불량 수량"].map((h) => (
                            <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50">
                        {rows.map((row, i) => (
                          <tr key={row.forming_id ?? i} className="hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3 font-mono text-xs text-gray-500">{row.recorded_at ?? "—"}</td>
                            <td className="px-4 py-3">
                              <span className={`text-xs px-2 py-0.5 rounded-full ${
                                row.defect_flag ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
                              }`}>
                                {row.defect_flag ? "불량" : "정상"}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-gray-700">{row.defect_count ?? 0}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  );
                })()
              }
            </div>
          )}
        </div>
      )}
    </div>
  );
}
