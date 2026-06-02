"use client";
import { useState } from "react";
import { ShieldCheck, BookOpen, Tag, Plus, Search } from "lucide-react";

interface QualityStandard {
  qs_code: string;
  product_type: string;
  process_type: string;
  criteria: string;
  tolerance: string;
  updated_at: string;
}

interface WorkStandard {
  ws_code: string;
  process_type: string;
  condition: string;
  value: string;
  unit: string;
  updated_at: string;
}

interface CodeItem {
  code: string;
  category: string;
  label: string;
  description: string;
}

const QUALITY_STANDARDS: QualityStandard[] = [
  { qs_code: "QS-FORMING-001", product_type: "강관",  process_type: "FORMING",  criteria: "두께 편차",   tolerance: "±0.2mm",  updated_at: "2026-05-01" },
  { qs_code: "QS-FORMING-002", product_type: "강관",  process_type: "FORMING",  criteria: "길이 편차",   tolerance: "±1.0mm",  updated_at: "2026-05-01" },
  { qs_code: "QS-FORMING-003", product_type: "강관",  process_type: "FORMING",  criteria: "각도 편차",   tolerance: "±0.5°",   updated_at: "2026-05-01" },
  { qs_code: "QS-WELDING-001", product_type: "강관",  process_type: "WELDING",  criteria: "비드폭",      tolerance: "5~9mm",   updated_at: "2026-05-10" },
  { qs_code: "QS-WELDING-002", product_type: "강관",  process_type: "WELDING",  criteria: "기공 발생",   tolerance: "불허",     updated_at: "2026-05-10" },
  { qs_code: "QS-WELDING-003", product_type: "강관",  process_type: "WELDING",  criteria: "언더컷",      tolerance: "최대 0.5mm", updated_at: "2026-05-10" },
  { qs_code: "QS-FINAL-001",   product_type: "완제품", process_type: "FINAL",    criteria: "표면결함",    tolerance: "0개",      updated_at: "2026-05-15" },
  { qs_code: "QS-FINAL-002",   product_type: "완제품", process_type: "FINAL",    criteria: "치수 편차",   tolerance: "±1.5mm",  updated_at: "2026-05-15" },
  { qs_code: "QS-FINAL-003",   product_type: "완제품", process_type: "FINAL",    criteria: "도막 부착강도", tolerance: "≥3.0MPa", updated_at: "2026-05-15" },
];

const WORK_STANDARDS: WorkStandard[] = [
  { ws_code: "WS-FORM-001", process_type: "FORMING",  condition: "프레스 압력",    value: "120",  unit: "ton",  updated_at: "2026-05-01" },
  { ws_code: "WS-FORM-002", process_type: "FORMING",  condition: "작업 속도",      value: "75",   unit: "rpm",  updated_at: "2026-05-01" },
  { ws_code: "WS-FORM-003", process_type: "FORMING",  condition: "소재 온도",      value: "25",   unit: "°C",   updated_at: "2026-05-01" },
  { ws_code: "WS-WELD-001", process_type: "WELDING",  condition: "용접 전류",      value: "180",  unit: "A",    updated_at: "2026-05-10" },
  { ws_code: "WS-WELD-002", process_type: "WELDING",  condition: "용접 속도",      value: "35",   unit: "cm/min", updated_at: "2026-05-10" },
  { ws_code: "WS-WELD-003", process_type: "WELDING",  condition: "예열 온도",      value: "150",  unit: "°C",   updated_at: "2026-05-10" },
  { ws_code: "WS-PAINT-001", process_type: "PAINTING", condition: "도료 점도",     value: "85",   unit: "KU",   updated_at: "2026-05-12" },
  { ws_code: "WS-PAINT-002", process_type: "PAINTING", condition: "건조 온도",     value: "80",   unit: "°C",   updated_at: "2026-05-12" },
];

const CODES: CodeItem[] = [
  { code: "PROC-001", category: "공정유형",   label: "FORMING",   description: "성형 공정" },
  { code: "PROC-002", category: "공정유형",   label: "WELDING",   description: "용접 공정" },
  { code: "PROC-003", category: "공정유형",   label: "PAINTING",  description: "도장 공정" },
  { code: "PROC-004", category: "공정유형",   label: "PACKING",   description: "포장 공정" },
  { code: "PROC-005", category: "공정유형",   label: "FINAL",     description: "최종검사 공정" },
  { code: "PROD-001", category: "제품유형",   label: "강관",      description: "일반 강관 제품" },
  { code: "PROD-002", category: "제품유형",   label: "완제품",    description: "포장 완료 제품" },
  { code: "ROLE-001", category: "역할코드",   label: "ADMIN",     description: "시스템 관리자" },
  { code: "ROLE-002", category: "역할코드",   label: "MANAGER",   description: "생산 관리자" },
  { code: "ROLE-003", category: "역할코드",   label: "OPERATOR",  description: "생산 작업자" },
  { code: "ROLE-004", category: "역할코드",   label: "INSPECTOR", description: "품질 검사자" },
];

const processTypeCls: Record<string, string> = {
  FORMING:  "bg-blue-100 text-blue-700",
  WELDING:  "bg-orange-100 text-orange-700",
  PAINTING: "bg-purple-100 text-purple-700",
  PACKING:  "bg-teal-100 text-teal-700",
  FINAL:    "bg-green-100 text-green-700",
};

const TABS = [
  { key: "quality",  label: "품질기준",  icon: ShieldCheck },
  { key: "work",     label: "작업표준",  icon: BookOpen },
  { key: "codes",    label: "코드관리",  icon: Tag },
] as const;

type Tab = typeof TABS[number]["key"];

export default function StandardsPage() {
  const [tab, setTab] = useState<Tab>("quality");
  const [search, setSearch] = useState("");

  const filteredQS = QUALITY_STANDARDS.filter(
    (r) =>
      r.qs_code.toLowerCase().includes(search.toLowerCase()) ||
      r.process_type.toLowerCase().includes(search.toLowerCase()) ||
      r.criteria.toLowerCase().includes(search.toLowerCase())
  );

  const filteredWS = WORK_STANDARDS.filter(
    (r) =>
      r.ws_code.toLowerCase().includes(search.toLowerCase()) ||
      r.process_type.toLowerCase().includes(search.toLowerCase()) ||
      r.condition.toLowerCase().includes(search.toLowerCase())
  );

  const filteredCodes = CODES.filter(
    (r) =>
      r.code.toLowerCase().includes(search.toLowerCase()) ||
      r.label.toLowerCase().includes(search.toLowerCase()) ||
      r.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">기준정보관리</h2>
        <button className="flex items-center gap-2 text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <Plus size={14} /> 새 기준 등록
        </button>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => { setTab(key); setSearch(""); }}
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

      {/* Search */}
      <div className="relative w-72">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="검색..."
          className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* === 품질기준 === */}
      {tab === "quality" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
            <ShieldCheck size={16} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-700">품질기준 목록</span>
            <span className="ml-auto text-xs text-gray-400">{filteredQS.length}건</span>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["QS 코드", "제품유형", "공정유형", "검사 기준", "허용 공차", "최종 수정"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredQS.map((row) => (
                <tr key={row.qs_code} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">{row.qs_code}</td>
                  <td className="px-4 py-3 text-gray-700">{row.product_type}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${processTypeCls[row.process_type] ?? "bg-gray-100 text-gray-600"}`}>
                      {row.process_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{row.criteria}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-900">{row.tolerance}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{row.updated_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* === 작업표준 === */}
      {tab === "work" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
            <BookOpen size={16} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-700">공정별 작업표준</span>
            <span className="ml-auto text-xs text-gray-400">{filteredWS.length}건</span>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["WS 코드", "공정유형", "표준 조건", "기준값", "단위", "최종 수정"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredWS.map((row) => (
                <tr key={row.ws_code} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">{row.ws_code}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${processTypeCls[row.process_type] ?? "bg-gray-100 text-gray-600"}`}>
                      {row.process_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{row.condition}</td>
                  <td className="px-4 py-3 font-mono text-sm font-medium text-gray-900">{row.value}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{row.unit}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{row.updated_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* === 코드관리 === */}
      {tab === "codes" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
            <Tag size={16} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-700">코드 목록</span>
            <span className="ml-auto text-xs text-gray-400">{filteredCodes.length}건</span>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                {["코드", "분류", "코드명", "설명"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filteredCodes.map((row) => (
                <tr key={row.code} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">{row.code}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                      {row.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">{row.label}</td>
                  <td className="px-4 py-3 text-gray-500">{row.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
