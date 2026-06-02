"use client";
import { useState } from "react";
import { Database, BarChart2, Download, Brain, Search, FileDown } from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const TABS = [
  { key: "query",    label: "데이터조회",    icon: Search },
  { key: "viz",      label: "시각화",        icon: BarChart2 },
  { key: "download", label: "다운로드",      icon: Download },
  { key: "ai",       label: "AI학습데이터",  icon: Brain },
] as const;

type Tab = typeof TABS[number]["key"];

// Mock lot data
const MOCK_LOT = {
  lot_id: "LOT-2026-0602-01",
  work_order_no: "WO-2026-060200001",
  product: "강관 Ø60 t=3.2",
  planned_qty: 1500,
  actual_qty: 1240,
  status: "IN_PROGRESS",
  start_date: "2026-06-02 08:00",
  processes: [
    { process: "FORMING",  start: "08:00", end: "11:30", operator: "김철수", result: "정상", qty: 1240 },
    { process: "WELDING",  start: "11:45", end: "15:00", operator: "이영희", result: "정상", qty: 1190 },
    { process: "PAINTING", start: "15:15", end: "17:30", operator: "박민준", result: "진행중", qty: null },
  ],
  inspections: [
    { type: "IN_PROCESS", result: "PASS", inspector: "최수진", time: "12:00" },
    { type: "IN_PROCESS", result: "PASS", inspector: "최수진", time: "14:30" },
  ],
};

// Mock chart data — monthly production trend
const CHART_DATA = [
  { month: "1월",  forming: 28000, welding: 24000, painting: 21000, packing: 20500 },
  { month: "2월",  forming: 30000, welding: 26500, painting: 23000, packing: 22000 },
  { month: "3월",  forming: 27000, welding: 23000, painting: 20500, packing: 19800 },
  { month: "4월",  forming: 32000, welding: 28000, painting: 25000, packing: 24500 },
  { month: "5월",  forming: 35000, welding: 31000, painting: 28000, packing: 27200 },
  { month: "6월",  forming: 22000, welding: 19000, painting: 14000, packing: 13000 },
];

const AREA_COLORS = ["#3b82f6", "#f97316", "#8b5cf6", "#10b981"];
const AREA_KEYS  = ["forming", "welding", "painting", "packing"];
const AREA_LABELS = ["성형", "용접", "도장", "포장"];

const AI_DATASETS = [
  { name: "공정 센서 데이터셋",      records: "124,500",  period: "2025-01 ~ 2026-05", size: "48.2 MB", status: "완료" },
  { name: "품질 검사 이력",          records: "18,320",   period: "2025-01 ~ 2026-05", size: "8.7 MB",  status: "완료" },
  { name: "불량 패턴 라벨 데이터",   records: "3,420",    period: "2025-06 ~ 2026-05", size: "2.1 MB",  status: "완료" },
  { name: "CAD 도면 해석 데이터셋",  records: "890",      period: "2025-01 ~ 2026-05", size: "1.2 GB",  status: "준비중" },
  { name: "수율 예측 학습 데이터",   records: "56,700",   period: "2025-01 ~ 2026-05", size: "22.4 MB", status: "완료" },
];

const resultCls: Record<string, string> = {
  PASS: "bg-green-100 text-green-700",
  FAIL: "bg-red-100 text-red-700",
  HOLD: "bg-yellow-100 text-yellow-700",
};

export default function DataPage() {
  const [tab, setTab] = useState<Tab>("query");
  const [lotId, setLotId] = useState("");
  const [searched, setSearched] = useState(false);
  const [period, setPeriod] = useState<"1M" | "3M" | "6M">("6M");
  const [dlFrom, setDlFrom] = useState("2026-05-01");
  const [dlTo, setDlTo] = useState("2026-06-03");
  const [dlType, setDlType] = useState("전체");
  const [downloading, setDownloading] = useState(false);

  const handleSearch = () => {
    if (lotId.trim()) setSearched(true);
  };

  const handleDownload = () => {
    setDownloading(true);
    setTimeout(() => setDownloading(false), 1500);
  };

  const chartData =
    period === "1M" ? CHART_DATA.slice(-1) :
    period === "3M" ? CHART_DATA.slice(-3) :
    CHART_DATA;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">데이터관리</h2>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => { setTab(key); setSearched(false); }}
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

      {/* === 데이터조회 === */}
      {tab === "query" && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">LOT ID 기반 통합 조회</h3>
            <div className="flex gap-2">
              <input
                value={lotId}
                onChange={(e) => setLotId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="LOT ID 입력 (예: LOT-2026-0602-01)"
                className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                조회
              </button>
              {searched && (
                <button
                  onClick={() => { setSearched(false); setLotId(""); }}
                  className="px-4 py-2 border border-gray-200 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
                >
                  초기화
                </button>
              )}
            </div>
          </div>

          {searched && (
            <>
              {/* LOT 기본 정보 */}
              <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">LOT 기본정보</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {[
                    ["LOT ID", MOCK_LOT.lot_id],
                    ["작업지시번호", MOCK_LOT.work_order_no],
                    ["제품명", MOCK_LOT.product],
                    ["계획 수량", `${MOCK_LOT.planned_qty.toLocaleString()} EA`],
                    ["실적 수량", `${MOCK_LOT.actual_qty.toLocaleString()} EA`],
                    ["시작일시", MOCK_LOT.start_date],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <p className="text-xs text-gray-400 mb-0.5">{label}</p>
                      <p className="text-sm font-medium text-gray-900 font-mono">{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 공정 이력 */}
              <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="px-5 py-3 border-b border-gray-100">
                  <span className="text-sm font-medium text-gray-700">공정 이력</span>
                </div>
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-100">
                    <tr>
                      {["공정", "시작", "종료", "작업자", "수량", "결과"].map((h) => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {MOCK_LOT.processes.map((p, i) => (
                      <tr key={i} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3">
                          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{p.process}</span>
                        </td>
                        <td className="px-4 py-3 text-gray-500">{p.start}</td>
                        <td className="px-4 py-3 text-gray-500">{p.end}</td>
                        <td className="px-4 py-3 text-gray-700">{p.operator}</td>
                        <td className="px-4 py-3 text-gray-700">{p.qty != null ? `${p.qty.toLocaleString()} EA` : "—"}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${p.result === "정상" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}`}>
                            {p.result}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 품질 검사 */}
              <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="px-5 py-3 border-b border-gray-100">
                  <span className="text-sm font-medium text-gray-700">품질 검사 이력</span>
                </div>
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-100">
                    <tr>
                      {["검사유형", "결과", "검사자", "시각"].map((h) => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {MOCK_LOT.inspections.map((ins, i) => (
                      <tr key={i} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-gray-700">{ins.type}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${resultCls[ins.result] ?? ""}`}>{ins.result}</span>
                        </td>
                        <td className="px-4 py-3 text-gray-700">{ins.inspector}</td>
                        <td className="px-4 py-3 text-gray-400">{ins.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {/* === 시각화 === */}
      {tab === "viz" && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-sm font-semibold text-gray-900">공정별 생산량 추이</h3>
              <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
                {(["1M", "3M", "6M"] as const).map((p) => (
                  <button
                    key={p}
                    onClick={() => setPeriod(p)}
                    className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                      period === p ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 12 }}
                  formatter={(value, name) => [
                    `${Number(value).toLocaleString()} EA`,
                    AREA_LABELS[AREA_KEYS.indexOf(name as typeof AREA_KEYS[number])] ?? String(name),
                  ]}
                />
                <Legend
                  formatter={(value) => AREA_LABELS[AREA_KEYS.indexOf(value as typeof AREA_KEYS[number])] ?? value}
                  iconType="circle"
                  iconSize={8}
                />
                {AREA_KEYS.map((key, i) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={AREA_COLORS[i]}
                    fill={AREA_COLORS[i]}
                    fillOpacity={0.08}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* === 다운로드 === */}
      {tab === "download" && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">데이터 다운로드</h3>
            <div className="grid grid-cols-2 gap-4 mb-5">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">시작일</label>
                <input
                  type="date"
                  value={dlFrom}
                  onChange={(e) => setDlFrom(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">종료일</label>
                <input
                  type="date"
                  value={dlTo}
                  onChange={(e) => setDlTo(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-600 mb-1">데이터 유형</label>
                <select
                  value={dlType}
                  onChange={(e) => setDlType(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>전체</option>
                  <option>공정 실적</option>
                  <option>품질 검사</option>
                  <option>설비 센서</option>
                  <option>작업지시</option>
                </select>
              </div>
            </div>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-60 transition-colors"
            >
              <FileDown size={15} />
              {downloading ? "다운로드 준비 중..." : "CSV 다운로드"}
            </button>
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-sm font-medium text-blue-700 mb-1">다운로드 형식</p>
            <p className="text-xs text-blue-600">
              선택한 기간의 데이터를 UTF-8 BOM CSV 형식으로 내보냅니다.
              대용량 데이터(1만건 이상)는 백그라운드 작업 후 이메일로 전송됩니다.
            </p>
          </div>
        </div>
      )}

      {/* === AI학습데이터 === */}
      {tab === "ai" && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
              <Brain size={16} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-700">AI 학습 데이터셋</span>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {["데이터셋명", "레코드 수", "기간", "크기", "상태", "액션"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {AI_DATASETS.map((ds) => (
                  <tr key={ds.name} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-gray-900">{ds.name}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{ds.records}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{ds.period}</td>
                    <td className="px-4 py-3 text-gray-500">{ds.size}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        ds.status === "완료" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                      }`}>
                        {ds.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {ds.status === "완료" && (
                        <button className="text-xs px-3 py-1 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors">
                          다운로드
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-sm font-medium text-blue-700 mb-1">AI 학습 파이프라인</p>
            <p className="text-xs text-blue-600">
              수집된 센서 데이터 및 품질 이력은 RAG AI Agent 및 공정 이상 감지 모델 학습에 활용됩니다.
              데이터 품질 검증 후 자동으로 학습 파이프라인에 공급됩니다.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
