"use client";
import Sidebar from "@/components/Sidebar";
import { useQuery } from "@tanstack/react-query";
import { aiApi, equipmentApi, workOrderApi, shippingApi } from "@/lib/api";
import {
  Activity, Package, Wrench, AlertTriangle,
  TrendingUp, TrendingDown, Minus, CheckCircle,
  Clock, Truck, AlertCircle,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Equipment {
  equipment_id: string;
  equipment_name: string;
  status: string;
  process_type: string;
}

interface WorkOrder {
  work_order_id: string;
  wo_number: string;
  product_name?: string;
  planned_qty: number;
  actual_qty?: number;
  status: string;
  start_date?: string;
}

interface ShippingOrder {
  shipping_order_id: string;
  delivery_risk_flag?: boolean;
  status: string;
}

// ─── Config maps ─────────────────────────────────────────────────────────────

const statusColor: Record<string, { bg: string; text: string; dot: string; label: string }> = {
  IDLE:        { bg: "bg-gray-100",   text: "text-gray-600",   dot: "bg-gray-400",   label: "대기" },
  RUNNING:     { bg: "bg-green-100",  text: "text-green-700",  dot: "bg-green-500",  label: "가동" },
  MAINTENANCE: { bg: "bg-amber-100",  text: "text-amber-700",  dot: "bg-amber-500",  label: "점검" },
  ERROR:       { bg: "bg-red-100",    text: "text-red-700",    dot: "bg-red-500",    label: "오류" },
};

const woStatusCfg: Record<string, { cls: string; label: string }> = {
  PLANNED:     { cls: "bg-gray-100 text-gray-600",    label: "계획" },
  IN_PROGRESS: { cls: "bg-blue-100 text-blue-700",    label: "진행" },
  COMPLETED:   { cls: "bg-green-100 text-green-700",  label: "완료" },
  ON_HOLD:     { cls: "bg-amber-100 text-amber-700",  label: "보류" },
};

// ─── Dummy process data ───────────────────────────────────────────────────────

const PROCESS_DATA = [
  { key: "FORMING",  label: "FORMING",  color: "blue",  working: 120, done: 980,  defect: 12 },
  { key: "WELDING",  label: "WELDING",  color: "violet",working: 85,  done: 740,  defect: 8  },
  { key: "CUTTING",  label: "CUTTING",  color: "amber", working: 200, done: 1560, defect: 21 },
  { key: "PACKING",  label: "PACKING",  color: "green", working: 60,  done: 880,  defect: 3  },
];

const processColor: Record<string, { bar: string; bg: string; text: string }> = {
  blue:   { bar: "bg-blue-500",   bg: "bg-blue-50",   text: "text-blue-700"   },
  violet: { bar: "bg-violet-500", bg: "bg-violet-50", text: "text-violet-700" },
  amber:  { bar: "bg-amber-500",  bg: "bg-amber-50",  text: "text-amber-700"  },
  green:  { bar: "bg-green-500",  bg: "bg-green-50",  text: "text-green-700"  },
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function Trend({ pct }: { pct?: number }) {
  if (pct == null) return <span className="text-gray-300">—</span>;
  if (pct > 0)
    return (
      <span className="inline-flex items-center gap-0.5 text-green-600 text-xs font-medium">
        <TrendingUp size={12} /> +{pct}%
      </span>
    );
  if (pct < 0)
    return (
      <span className="inline-flex items-center gap-0.5 text-red-500 text-xs font-medium">
        <TrendingDown size={12} /> {pct}%
      </span>
    );
  return (
    <span className="inline-flex items-center gap-0.5 text-gray-400 text-xs">
      <Minus size={12} /> 0%
    </span>
  );
}

function KpiCard({
  label,
  actual,
  target,
  unit,
  icon,
  trend,
  accentClass,
}: {
  label: string;
  actual?: string | number;
  target?: string | number;
  unit?: string;
  icon: React.ReactNode;
  trend?: number;
  accentClass: string;
}) {
  const hasData = actual != null && actual !== "" && actual !== "—";
  const progress =
    hasData && target
      ? Math.min(100, Math.round((Number(actual) / Number(target)) * 100))
      : null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <div className={`w-9 h-9 rounded-lg ${accentClass} flex items-center justify-center`}>
          {icon}
        </div>
        <Trend pct={trend} />
      </div>
      <div>
        <p className="text-xs text-gray-500 font-medium">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-0.5 tabular-nums">
          {hasData ? actual : <span className="text-gray-300 text-xl">연결 대기</span>}
          {hasData && unit && (
            <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>
          )}
        </p>
      </div>
      {progress !== null && (
        <div>
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>목표 대비</span>
            <span>{progress}%</span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1">목표: {target} {unit}</p>
        </div>
      )}
    </div>
  );
}

function EquipmentCard({ eq }: { eq: Equipment }) {
  const cfg = statusColor[eq.status] ?? statusColor.IDLE;
  const isRunning = eq.status === "RUNNING";
  return (
    <div className="border border-gray-100 rounded-xl p-4 bg-white hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-full ${cfg.bg} ${cfg.text}`}>
          <span
            className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${isRunning ? "animate-pulse" : ""}`}
          />
          {cfg.label}
        </span>
      </div>
      <p className="text-sm font-semibold text-gray-800 leading-tight truncate">{eq.equipment_name}</p>
      <p className="text-xs text-gray-400 mt-0.5">{eq.process_type}</p>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const today = new Date().toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "short",
  });

  const { data: kpiRes } = useQuery({
    queryKey: ["kpi-summary"],
    queryFn: () => aiApi.kpiSummary(),
    refetchInterval: 30_000,
  });

  const { data: eqRes } = useQuery({
    queryKey: ["equipment-list"],
    queryFn: () => equipmentApi.list(),
    refetchInterval: 10_000,
  });

  const { data: woRes } = useQuery({
    queryKey: ["work-orders-dashboard"],
    queryFn: () => workOrderApi.list({ limit: 10 }),
    refetchInterval: 30_000,
  });

  const { data: shippingRes } = useQuery({
    queryKey: ["shipping-pending"],
    queryFn: () => shippingApi.list({ status: "PENDING" }),
    refetchInterval: 30_000,
  });

  const kpi = kpiRes?.data?.data ?? {};
  const equipment: Equipment[] = eqRes?.data?.data ?? [];
  const workOrders: WorkOrder[] = woRes?.data?.data ?? [];
  const shippingOrders: ShippingOrder[] = shippingRes?.data?.data?.items ?? shippingRes?.data?.data ?? [];
  const riskCount = shippingOrders.filter((s) => s.delivery_risk_flag).length;

  // Derive equipment summary counts
  const eqCounts = equipment.reduce(
    (acc, eq) => {
      acc[eq.status] = (acc[eq.status] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const cards = [
    {
      label: "시간당 생산량",
      actual: kpi.hourly_output?.actual,
      target: kpi.hourly_output?.target,
      unit: kpi.hourly_output?.unit ?? "pcs/h",
      icon: <Activity size={18} className="text-blue-600" />,
      accentClass: "bg-blue-50",
      trend: 5,
    },
    {
      label: "리드타임",
      actual: kpi.lead_time?.actual,
      target: kpi.lead_time?.target,
      unit: kpi.lead_time?.unit ?? "일",
      icon: <Clock size={18} className="text-violet-600" />,
      accentClass: "bg-violet-50",
      trend: -3,
    },
    {
      label: "불량률",
      actual: kpi.defect_rate?.actual,
      target: kpi.defect_rate?.target,
      unit: kpi.defect_rate?.unit ?? "%",
      icon: <AlertTriangle size={18} className="text-amber-600" />,
      accentClass: "bg-amber-50",
      trend: -1,
    },
    {
      label: "설비 OEE",
      actual: kpi.equipment_oee?.actual,
      target: kpi.equipment_oee?.target,
      unit: kpi.equipment_oee?.unit ?? "%",
      icon: <Wrench size={18} className="text-green-600" />,
      accentClass: "bg-green-50",
      trend: 2,
    },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 space-y-6">

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI 대시보드</h2>
            <p className="text-sm text-gray-500 mt-0.5">{today} · 30초마다 갱신</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500 bg-white border border-gray-100 rounded-lg px-3 py-2 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            라이브 연결
          </div>
        </div>

        {/* KPI Cards — 4-column */}
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
          {cards.map((c) => (
            <KpiCard key={c.label} {...c} />
          ))}
        </div>

        {/* 생산현황 분석 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">생산현황 분석</h3>
            <span className="text-xs text-gray-400">공정별 실시간 현황</span>
          </div>
          <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
            {PROCESS_DATA.map((proc) => {
              const clr = processColor[proc.color];
              const total = proc.working + proc.done + proc.defect;
              const donePct = Math.round((proc.done / total) * 100);
              return (
                <div key={proc.key} className={`rounded-xl p-4 ${clr.bg} border border-gray-100`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-xs font-bold tracking-wider ${clr.text}`}>{proc.label}</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500 text-xs">작업중</span>
                      <span className="font-semibold text-gray-800 tabular-nums">{proc.working.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 text-xs">완료</span>
                      <span className="font-semibold text-green-700 tabular-nums">{proc.done.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 text-xs">불량</span>
                      <span className="font-semibold text-red-600 tabular-nums">{proc.defect.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="h-1.5 bg-white/60 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${clr.bar} transition-all duration-500`}
                        style={{ width: `${donePct}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1 text-right">완료율 {donePct}%</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 출하현황 분석 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">출하현황 분석</h3>
            <span className="text-xs text-gray-400">PENDING 출하 기준</span>
          </div>

          {riskCount > 0 && (
            <div className="mb-4 flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
              <AlertCircle size={16} className="shrink-0" />
              <span>
                <span className="font-semibold">납기위험 {riskCount}건</span> — 즉시 확인이 필요한 출하 건이 있습니다.
              </span>
            </div>
          )}

          {shippingOrders.length === 0 ? (
            <div className="flex items-center justify-center h-20 text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-200">
              출하 데이터 없음 (DB 연결 필요)
            </div>
          ) : (
            <div className="overflow-x-auto -mx-5">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">출하 ID</th>
                    <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">상태</th>
                    <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">납기위험</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {shippingOrders.map((s) => (
                    <tr key={s.shipping_order_id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3 font-mono text-xs text-gray-700">{s.shipping_order_id}</td>
                      <td className="px-3 py-3">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{s.status}</span>
                      </td>
                      <td className="px-3 py-3">
                        {s.delivery_risk_flag ? (
                          <span className="inline-flex items-center gap-1 text-xs font-medium text-red-600">
                            <AlertCircle size={12} /> 위험
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">정상</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Equipment Status Grid */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">설비 현황</h3>
            <div className="flex items-center gap-3">
              {Object.entries(statusColor).map(([key, cfg]) => (
                <span key={key} className="flex items-center gap-1 text-xs text-gray-500">
                  <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                  {cfg.label} {eqCounts[key] ?? 0}
                </span>
              ))}
            </div>
          </div>
          {equipment.length === 0 ? (
            <div className="flex items-center justify-center h-24 text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-200">
              설비 데이터 없음 (DB 연결 필요)
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">
              {equipment.map((eq) => (
                <EquipmentCard key={eq.equipment_id} eq={eq} />
              ))}
            </div>
          )}
        </div>

        {/* Production Work Orders Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-gray-900">실시간 생산 현황</h3>
              <p className="text-xs text-gray-400 mt-0.5">작업지시 기준 · 최근 10건</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Package size={14} />
              <span>{workOrders.length}건</span>
            </div>
          </div>

          {workOrders.length === 0 ? (
            <div className="flex items-center justify-center h-24 text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-200">
              작업지시 없음 (DB 연결 필요)
            </div>
          ) : (
            <div className="overflow-x-auto -mx-5">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">WO 번호</th>
                    <th className="text-left text-xs font-medium text-gray-500 px-3 py-3">품목</th>
                    <th className="text-right text-xs font-medium text-gray-500 px-3 py-3">계획</th>
                    <th className="text-right text-xs font-medium text-gray-500 px-3 py-3">실적</th>
                    <th className="text-left text-xs font-medium text-gray-500 px-3 py-3 min-w-[120px]">진행률</th>
                    <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">상태</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {workOrders.map((wo) => {
                    const pct = wo.actual_qty
                      ? Math.min(100, Math.round((wo.actual_qty / wo.planned_qty) * 100))
                      : 0;
                    const cfg = woStatusCfg[wo.status] ?? woStatusCfg.PLANNED;
                    return (
                      <tr key={wo.work_order_id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-5 py-3 font-mono text-xs text-gray-700 font-medium">
                          {wo.wo_number}
                        </td>
                        <td className="px-3 py-3 text-gray-700 max-w-[160px] truncate">
                          {wo.product_name ?? "—"}
                        </td>
                        <td className="px-3 py-3 text-right text-gray-700 tabular-nums">
                          {wo.planned_qty.toLocaleString()}
                        </td>
                        <td className="px-3 py-3 text-right text-gray-700 tabular-nums">
                          {wo.actual_qty?.toLocaleString() ?? "—"}
                        </td>
                        <td className="px-3 py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full bg-blue-500 transition-all duration-500"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-400 tabular-nums w-8 text-right">{pct}%</span>
                          </div>
                        </td>
                        <td className="px-5 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.cls}`}>
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

        {/* Footer summary bar */}
        <div className="flex items-center gap-6 text-xs text-gray-400 pb-2">
          <span className="flex items-center gap-1"><CheckCircle size={12} className="text-green-500" /> 시스템 정상</span>
          <span className="flex items-center gap-1"><Truck size={12} /> 출하 연동 활성</span>
          <span className="flex items-center gap-1"><Activity size={12} /> AI KPI 분석 가동 중</span>
        </div>

      </main>
    </div>
  );
}
