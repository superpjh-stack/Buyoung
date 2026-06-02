"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { equipmentApi } from "@/lib/api";
import { Wrench } from "lucide-react";

interface Equipment {
  equipment_id: string;
  equipment_code: string;
  equipment_name: string;
  process_type: string;
  status: string;
}

const statusConfig: Record<string, { label: string; cls: string }> = {
  IDLE:        { label: "대기",   cls: "bg-gray-100 text-gray-600" },
  RUNNING:     { label: "가동",   cls: "bg-green-100 text-green-700" },
  MAINTENANCE: { label: "점검",   cls: "bg-yellow-100 text-yellow-700" },
  ERROR:       { label: "오류",   cls: "bg-red-100 text-red-700" },
};

const nextStatus: Record<string, string> = {
  IDLE: "RUNNING", RUNNING: "IDLE", MAINTENANCE: "IDLE", ERROR: "MAINTENANCE",
};

export default function EquipmentPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["equipment"],
    queryFn: () => equipmentApi.list(),
    refetchInterval: 10_000,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      equipmentApi.updateStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["equipment"] }),
  });

  const items: Equipment[] = data?.data?.data ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">설비 모니터링</h2>

      {isLoading ? (
        <div className="text-gray-400 text-sm">로딩 중...</div>
      ) : items.length === 0 ? (
        <div className="bg-white rounded-xl p-8 text-center text-gray-400 border border-gray-100">
          설비 데이터 없음 (DB 연결 필요)
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {items.map((eq) => {
            const cfg = statusConfig[eq.status] ?? statusConfig.IDLE;
            return (
              <div key={eq.equipment_id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{eq.equipment_name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{eq.equipment_code} · {eq.process_type}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${cfg.cls}`}>
                    {cfg.label}
                  </span>
                </div>
                <div className="mt-4 flex gap-2">
                  {Object.entries(statusConfig).map(([s, c]) => (
                    <button
                      key={s}
                      disabled={eq.status === s || mutation.isPending}
                      onClick={() => mutation.mutate({ id: eq.equipment_id, status: s })}
                      className={`text-xs px-2 py-1 rounded border transition-colors ${
                        eq.status === s
                          ? `${c.cls} border-transparent font-medium`
                          : "border-gray-200 text-gray-500 hover:border-gray-400"
                      }`}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
