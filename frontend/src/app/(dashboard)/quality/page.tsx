"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { qualityApi } from "@/lib/api";
import { useState } from "react";
import { CheckSquare, AlertTriangle, XCircle, PauseCircle } from "lucide-react";

interface Inspection {
  inspection_id: string;
  production_lot_id: string;
  qs_id: string;
  inspection_type: string;
  inspector_id: string;
  result: string;
  remarks?: string;
  inspected_at: string;
}

interface Defect {
  defect_id: string;
  defect_type: string;
  defect_location?: string;
  severity: string;
  corrective_action?: string;
  recorded_at: string;
}

const resultConfig: Record<string, { label: string; cls: string; icon: React.ReactNode }> = {
  PASS: { label: "합격", cls: "bg-green-100 text-green-700", icon: <CheckSquare size={12} /> },
  FAIL: { label: "불합격", cls: "bg-red-100 text-red-700",   icon: <XCircle size={12} /> },
  HOLD: { label: "보류",  cls: "bg-yellow-100 text-yellow-700", icon: <PauseCircle size={12} /> },
};

const severityConfig: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-700",
  MAJOR:    "bg-orange-100 text-orange-700",
  MINOR:    "bg-yellow-100 text-yellow-700",
};

const typeLabel: Record<string, string> = {
  INCOMING:   "수입검사",
  IN_PROCESS: "공정검사",
  FINAL:      "최종검사",
};

export default function QualityPage() {
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<string>("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    production_lot_id: "",
    qs_id: "",
    inspection_type: "FINAL",
    result: "PASS",
    remarks: "",
  });

  const { data: defectsRes } = useQuery({
    queryKey: ["defects", selectedId],
    queryFn: () => qualityApi.listDefects(selectedId),
    enabled: !!selectedId,
  });

  const createMut = useMutation({
    mutationFn: (data: unknown) => qualityApi.createInspection(data),
    onSuccess: () => {
      setShowForm(false);
      setForm({ production_lot_id: "", qs_id: "", inspection_type: "FINAL", result: "PASS", remarks: "" });
    },
  });

  const defects: Defect[] = defectsRes?.data?.data ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">품질 검사</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + 검사 등록
        </button>
      </div>

      {/* Inspection form */}
      {showForm && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">검사 결과 등록</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">생산 LOT ID</label>
              <input
                value={form.production_lot_id}
                onChange={(e) => setForm((f) => ({ ...f, production_lot_id: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="UUID"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">품질 기준 ID</label>
              <input
                value={form.qs_id}
                onChange={(e) => setForm((f) => ({ ...f, qs_id: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="UUID"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">검사 유형</label>
              <select
                value={form.inspection_type}
                onChange={(e) => setForm((f) => ({ ...f, inspection_type: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="INCOMING">수입검사</option>
                <option value="IN_PROCESS">공정검사</option>
                <option value="FINAL">최종검사</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">결과</label>
              <select
                value={form.result}
                onChange={(e) => setForm((f) => ({ ...f, result: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="PASS">합격</option>
                <option value="FAIL">불합격</option>
                <option value="HOLD">보류</option>
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">비고</label>
              <input
                value={form.remarks}
                onChange={(e) => setForm((f) => ({ ...f, remarks: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="검사 비고사항"
              />
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => createMut.mutate(form)}
              disabled={!form.production_lot_id || !form.qs_id || createMut.isPending}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {createMut.isPending ? "등록 중..." : "등록"}
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
          </div>
        </div>
      )}

      {/* Inspection ID lookup */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">검사 ID로 불량 조회</h3>
        <div className="flex gap-2">
          <input
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="검사 ID (UUID) 입력"
          />
        </div>

        {selectedId && (
          <div className="mt-4">
            <h4 className="text-xs font-medium text-gray-500 mb-3 flex items-center gap-1">
              <AlertTriangle size={12} /> 불량 기록
            </h4>
            {defects.length === 0 ? (
              <p className="text-sm text-gray-400">불량 기록 없음</p>
            ) : (
              <div className="space-y-2">
                {defects.map((d) => (
                  <div key={d.defect_id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${severityConfig[d.severity] ?? ""}`}>
                      {d.severity}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{d.defect_type}</p>
                      {d.defect_location && (
                        <p className="text-xs text-gray-500">위치: {d.defect_location}</p>
                      )}
                      {d.corrective_action && (
                        <p className="text-xs text-gray-500">조치: {d.corrective_action}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Info box */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
        <p className="text-sm text-blue-700 font-medium mb-1">품질 기준 (시드 데이터)</p>
        <div className="text-xs text-blue-600 space-y-1">
          <p>• QS-FORMING-001 — 두께 ±0.2mm, 길이 ±1.0mm, 각도 ±0.5°</p>
          <p>• QS-WELDING-001 — 비드폭 5~9mm, 기공 불허, 언더컷 최대 0.5mm</p>
          <p>• QS-FINAL-001 — 표면결함 0개, 치수 ±1.5mm, 도막 부착강도 ≥3.0MPa</p>
        </div>
      </div>
    </div>
  );
}
