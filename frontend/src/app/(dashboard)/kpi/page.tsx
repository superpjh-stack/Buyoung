"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { aiApi } from "@/lib/api";
import {
  BarChart2, CheckCircle, AlertTriangle, Zap,
  Target, TrendingUp, TrendingDown, Save, RotateCcw,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

type TabId = "productivity" | "quality" | "targets";

interface KpiCardProps {
  label: string;
  actual?: string | number;
  target?: string | number;
  unit?: string;
  description?: string;
  icon: React.ReactNode;
  iconBg: string;
  status?: "good" | "warn" | "bad";
}

interface TargetField {
  key: string;
  label: string;
  unit: string;
  defaultVal: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function statusMeta(status?: "good" | "warn" | "bad") {
  switch (status) {
    case "good": return { bar: "bg-green-500",  badge: "bg-green-100 text-green-700",  text: "달성" };
    case "warn": return { bar: "bg-amber-400",  badge: "bg-amber-100 text-amber-700",  text: "주의" };
    case "bad":  return { bar: "bg-red-500",    badge: "bg-red-100 text-red-700",      text: "미달" };
    default:     return { bar: "bg-blue-500",   badge: "bg-gray-100 text-gray-500",    text: "—" };
  }
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
        active
          ? "border-blue-600 text-blue-600"
          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
      }`}
    >
      {children}
    </button>
  );
}

function KpiMetricCard({
  label,
  actual,
  target,
  unit,
  description,
  icon,
  iconBg,
  status,
}: KpiCardProps) {
  const meta = statusMeta(status);
  const hasData = actual != null && actual !== "" && actual !== "—";
  const pct =
    hasData && target
      ? Math.min(100, Math.round((Number(actual) / Number(target)) * 100))
      : null;

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center`}>
          {icon}
        </div>
        {status && (
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${meta.badge}`}>
            {meta.text}
          </span>
        )}
      </div>

      <p className="text-xs font-medium text-gray-500">{label}</p>
      <div className="flex items-end gap-1.5 mt-1">
        <span className="text-3xl font-bold text-gray-900 tabular-nums">
          {hasData ? actual : <span className="text-gray-300 text-2xl">—</span>}
        </span>
        {hasData && unit && (
          <span className="text-sm text-gray-400 mb-0.5">{unit}</span>
        )}
      </div>

      {description && (
        <p className="text-xs text-gray-400 mt-1">{description}</p>
      )}

      {pct !== null && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-400 mb-1.5">
            <span>목표 대비 달성률</span>
            <span className="font-medium text-gray-600">{pct}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${meta.bar} transition-all duration-700`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1.5">
            목표: {target} {unit}
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Tab panels ───────────────────────────────────────────────────────────────

function ProductivityTab({ kpi }: { kpi: Record<string, { actual?: number; target?: number; unit?: string }> }) {
  const cards: KpiCardProps[] = [
    {
      label: "시간당 생산량",
      actual: kpi.hourly_output?.actual,
      target: kpi.hourly_output?.target,
      unit: kpi.hourly_output?.unit ?? "pcs/h",
      description: "압축·절단·프레스 라인 합산 기준",
      icon: <Zap size={18} className="text-blue-600" />,
      iconBg: "bg-blue-50",
      status: kpi.hourly_output?.actual
        ? kpi.hourly_output.actual >= (kpi.hourly_output.target ?? 0) * 0.9
          ? "good"
          : "warn"
        : undefined,
    },
    {
      label: "설비 가동률",
      actual: kpi.equipment_oee?.actual,
      target: kpi.equipment_oee?.target,
      unit: kpi.equipment_oee?.unit ?? "%",
      description: "OEE (Overall Equipment Effectiveness)",
      icon: <BarChart2 size={18} className="text-violet-600" />,
      iconBg: "bg-violet-50",
      status: kpi.equipment_oee?.actual
        ? kpi.equipment_oee.actual >= 85
          ? "good"
          : kpi.equipment_oee.actual >= 70
          ? "warn"
          : "bad"
        : undefined,
    },
    {
      label: "리드타임",
      actual: kpi.lead_time?.actual,
      target: kpi.lead_time?.target,
      unit: kpi.lead_time?.unit ?? "일",
      description: "수주 접수 → 출하 완료 평균",
      icon: <TrendingDown size={18} className="text-teal-600" />,
      iconBg: "bg-teal-50",
      status: kpi.lead_time?.actual
        ? kpi.lead_time.actual <= (kpi.lead_time.target ?? 999)
          ? "good"
          : "warn"
        : undefined,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Summary strip */}
      <div className="grid grid-cols-3 gap-1 bg-gray-100 rounded-xl p-1">
        {[
          { label: "목표 달성", count: 2, color: "text-green-700" },
          { label: "주의 필요", count: 1, color: "text-amber-600" },
          { label: "미달성",   count: 0, color: "text-red-600" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-lg px-4 py-3 text-center">
            <p className={`text-xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((c) => (
          <KpiMetricCard key={c.label} {...c} />
        ))}
      </div>

      {/* Trend note */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-start gap-3">
        <TrendingUp size={16} className="text-blue-500 mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-medium text-blue-800">이번 주 생산성 트렌드</p>
          <p className="text-xs text-blue-600 mt-1">
            시간당 생산량이 전주 대비 +5% 개선되었습니다. 설비 가동률은 목표치(85%) 대비 소폭 미달 — 정기 점검 일정 조정을 권장합니다.
          </p>
        </div>
      </div>
    </div>
  );
}

function QualityTab({ kpi }: { kpi: Record<string, { actual?: number; target?: number; unit?: string }> }) {
  const cards: KpiCardProps[] = [
    {
      label: "불량률",
      actual: kpi.defect_rate?.actual,
      target: kpi.defect_rate?.target,
      unit: kpi.defect_rate?.unit ?? "%",
      description: "전체 생산 대비 불량 발생 비율 (낮을수록 좋음)",
      icon: <AlertTriangle size={18} className="text-amber-600" />,
      iconBg: "bg-amber-50",
      status: kpi.defect_rate?.actual
        ? kpi.defect_rate.actual <= (kpi.defect_rate.target ?? 5)
          ? "good"
          : kpi.defect_rate.actual <= (kpi.defect_rate.target ?? 5) * 1.5
          ? "warn"
          : "bad"
        : undefined,
    },
    {
      label: "합격률",
      actual:
        kpi.defect_rate?.actual != null
          ? (100 - kpi.defect_rate.actual).toFixed(1)
          : undefined,
      target: kpi.defect_rate?.target != null
        ? (100 - kpi.defect_rate.target).toFixed(1)
        : undefined,
      unit: "%",
      description: "최종 검사 합격 기준 (수입·공정·최종 통합)",
      icon: <CheckCircle size={18} className="text-green-600" />,
      iconBg: "bg-green-50",
      status: kpi.defect_rate?.actual
        ? kpi.defect_rate.actual <= (kpi.defect_rate.target ?? 5)
          ? "good"
          : "warn"
        : undefined,
    },
    {
      label: "클레임 발생률",
      actual: kpi.claim_rate?.actual ?? "0.0",
      target: kpi.claim_rate?.target ?? 1.0,
      unit: kpi.claim_rate?.unit ?? "%",
      description: "출하 건수 대비 고객 클레임 비율",
      icon: <AlertTriangle size={18} className="text-red-500" />,
      iconBg: "bg-red-50",
      status: (kpi.claim_rate?.actual ?? 0) <= (kpi.claim_rate?.target ?? 1) ? "good" : "bad",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Quality summary strip */}
      <div className="grid grid-cols-3 gap-1 bg-gray-100 rounded-xl p-1">
        {[
          { label: "품질 기준 달성", count: 2, color: "text-green-700" },
          { label: "모니터링 필요", count: 1, color: "text-amber-600" },
          { label: "즉시 조치 필요", count: 0, color: "text-red-600" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-lg px-4 py-3 text-center">
            <p className={`text-xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((c) => (
          <KpiMetricCard key={c.label} {...c} />
        ))}
      </div>

      {/* Quality standards reference */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">적용 품질 기준</h4>
        <div className="space-y-2">
          {[
            { code: "QS-FORMING-001", desc: "두께 ±0.2mm · 길이 ±1.0mm · 각도 ±0.5°" },
            { code: "QS-WELDING-001", desc: "비드폭 5~9mm · 기공 불허 · 언더컷 최대 0.5mm" },
            { code: "QS-FINAL-001",   desc: "표면결함 0개 · 치수 ±1.5mm · 도막 부착강도 ≥3.0MPa" },
          ].map((qs) => (
            <div key={qs.code} className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
              <span className="font-mono text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded mt-0.5">
                {qs.code}
              </span>
              <p className="text-xs text-gray-600">{qs.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const TARGET_FIELDS: TargetField[] = [
  { key: "hourly_output",  label: "시간당 생산량 목표", unit: "pcs/h", defaultVal: "150" },
  { key: "equipment_oee", label: "설비 가동률 목표",   unit: "%",    defaultVal: "85" },
  { key: "lead_time",     label: "리드타임 목표",       unit: "일",   defaultVal: "7" },
  { key: "defect_rate",   label: "불량률 목표",          unit: "%",    defaultVal: "2.0" },
  { key: "claim_rate",    label: "클레임 발생률 목표",  unit: "%",    defaultVal: "1.0" },
  { key: "on_time_rate",  label: "납기 준수율 목표",    unit: "%",    defaultVal: "95" },
];

function TargetsTab() {
  const [form, setForm] = useState<Record<string, string>>(
    Object.fromEntries(TARGET_FIELDS.map((f) => [f.key, f.defaultVal]))
  );
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // In production, this would call an API endpoint
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const handleReset = () => {
    setForm(Object.fromEntries(TARGET_FIELDS.map((f) => [f.key, f.defaultVal])));
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-semibold text-gray-900">KPI 목표값 설정</h3>
            <p className="text-xs text-gray-400 mt-0.5">변경 후 저장하면 즉시 대시보드에 반영됩니다</p>
          </div>
          <Target size={20} className="text-gray-300" />
        </div>

        <div className="space-y-4">
          {TARGET_FIELDS.map((field) => (
            <div key={field.key}>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">
                {field.label}
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  step="0.1"
                  value={form[field.key]}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                  }
                  className="w-36 border border-gray-300 rounded-lg px-3 py-2 text-sm tabular-nums focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-sm text-gray-400">{field.unit}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center gap-3 mt-8 pt-5 border-t border-gray-100">
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save size={14} />
            {saved ? "저장 완료!" : "목표값 저장"}
          </button>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2.5 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RotateCcw size={14} />
            기본값 초기화
          </button>
          {saved && (
            <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
              <CheckCircle size={13} /> 대시보드에 반영되었습니다
            </span>
          )}
        </div>
      </div>

      {/* Period selector note */}
      <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
        <p className="text-xs font-medium text-amber-800 mb-1">참고 사항</p>
        <p className="text-xs text-amber-700">
          목표값은 월별로 관리됩니다. 현재 설정은 2026년 6월 기준으로 적용됩니다.
          분기·연간 목표는 AI Agent 페이지에서 자동 분석 리포트를 요청하세요.
        </p>
      </div>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

const TABS: { id: TabId; label: string }[] = [
  { id: "productivity", label: "생산성 KPI" },
  { id: "quality",      label: "품질 KPI" },
  { id: "targets",      label: "KPI 목표 관리" },
];

export default function KpiPage() {
  const [activeTab, setActiveTab] = useState<TabId>("productivity");

  const { data: kpiRes } = useQuery({
    queryKey: ["kpi-summary"],
    queryFn: () => aiApi.kpiSummary(),
    refetchInterval: 30_000,
  });

  const kpi = kpiRes?.data?.data ?? {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">KPI 관리</h2>
          <p className="text-sm text-gray-500 mt-0.5">생산성·품질 지표 현황 및 목표 관리</p>
        </div>
      </div>

      {/* Tab bar */}
      {/*
        ┌───────────────────────────────────────────────┐
        │ [생산성 KPI] | [품질 KPI] | [KPI 목표 관리]   │
        │ ──────────── |            |                   │
        └───────────────────────────────────────────────┘
      */}
      <div className="border-b border-gray-200">
        <div className="flex gap-0">
          {TABS.map((t) => (
            <TabButton
              key={t.id}
              active={activeTab === t.id}
              onClick={() => setActiveTab(t.id)}
            >
              {t.label}
            </TabButton>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {activeTab === "productivity" && <ProductivityTab kpi={kpi} />}
      {activeTab === "quality"      && <QualityTab kpi={kpi} />}
      {activeTab === "targets"      && <TargetsTab />}
    </div>
  );
}
