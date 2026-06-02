"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { shippingApi } from "@/lib/api";
import { useState } from "react";
import { Truck, AlertTriangle, Package, FileText } from "lucide-react";

interface ShippingOrder {
  shipping_order_id: string;
  shipping_order_no: string;
  order_id: string;
  customer_id: string;
  planned_ship_date?: string;
  shipping_status: string;
  delivery_risk_flag: boolean;
  created_at: string;
}

interface Claim {
  claim_id: string;
  claim_no: string;
  customer_id: string;
  claim_type: string;
  claim_severity: string;
  status: string;
  description: string;
  claim_date: string;
}

const statusConfig: Record<string, { label: string; cls: string }> = {
  PENDING:  { label: "대기",    cls: "bg-gray-100 text-gray-600" },
  READY:    { label: "출하준비", cls: "bg-blue-100 text-blue-700" },
  SHIPPED:  { label: "출하완료", cls: "bg-green-100 text-green-700" },
  CANCELED: { label: "취소",    cls: "bg-red-100 text-red-700" },
};

const severityConfig: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-700",
  MAJOR:    "bg-orange-100 text-orange-700",
  MINOR:    "bg-yellow-100 text-yellow-700",
};

const claimStatusConfig: Record<string, string> = {
  OPEN:          "bg-red-100 text-red-700",
  INVESTIGATING: "bg-yellow-100 text-yellow-700",
  RESOLVED:      "bg-green-100 text-green-700",
  CLOSED:        "bg-gray-100 text-gray-600",
};

export default function ShippingPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<"orders" | "claims">("orders");

  const { data: ordersRes, isLoading } = useQuery({
    queryKey: ["shipping-orders"],
    queryFn: () => shippingApi.list(),
    refetchInterval: 30_000,
  });

  const { data: riskRes } = useQuery({
    queryKey: ["shipping-risk"],
    queryFn: () => shippingApi.deliveryRisk(),
  });

  const { data: claimsRes, isLoading: claimsLoading } = useQuery({
    queryKey: ["claims"],
    queryFn: () => shippingApi.listClaims(),
    enabled: tab === "claims",
  });

  const shipMut = useMutation({
    mutationFn: (id: string) => shippingApi.ship(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["shipping-orders"] }),
  });

  const orders: ShippingOrder[] = ordersRes?.data?.data?.items ?? ordersRes?.data?.data ?? [];
  const riskOrders: ShippingOrder[] = riskRes?.data?.data ?? [];
  const claims: Claim[] = claimsRes?.data?.data?.items ?? claimsRes?.data?.data ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">출하 관리</h2>
        <div className="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => setTab("orders")}
            className={`px-4 py-2 text-sm transition-colors ${
              tab === "orders" ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            출하 지시
          </button>
          <button
            onClick={() => setTab("claims")}
            className={`px-4 py-2 text-sm transition-colors ${
              tab === "claims" ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            클레임
          </button>
        </div>
      </div>

      {tab === "orders" && (
        <>
          {/* Risk banner */}
          {riskOrders.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
              <AlertTriangle size={18} className="text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-700">납기 위험 출하건 {riskOrders.length}건</p>
                <p className="text-xs text-red-600 mt-0.5">
                  {riskOrders.map((o) => o.shipping_order_no).join(", ")}
                </p>
              </div>
            </div>
          )}

          {/* Shipping orders table */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
              <Truck size={16} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-700">출하 지시 목록</span>
            </div>

            {isLoading ? (
              <div className="p-8 text-center text-gray-400 text-sm">로딩 중...</div>
            ) : orders.length === 0 ? (
              <div className="p-8 text-center text-gray-400 text-sm">
                출하 지시 없음 (DB 연결 확인 필요)
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    {["출하번호", "계획 출하일", "납기위험", "상태", "액션"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {orders.map((so) => {
                    const cfg = statusConfig[so.shipping_status] ?? statusConfig.PENDING;
                    return (
                      <tr key={so.shipping_order_id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">
                          {so.shipping_order_no}
                        </td>
                        <td className="px-4 py-3 text-gray-500">
                          {so.planned_ship_date ?? "—"}
                        </td>
                        <td className="px-4 py-3">
                          {so.delivery_risk_flag ? (
                            <span className="flex items-center gap-1 text-xs text-red-600">
                              <AlertTriangle size={12} /> 위험
                            </span>
                          ) : (
                            <span className="text-xs text-gray-400">정상</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.cls}`}>
                            {cfg.label}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {so.shipping_status === "READY" && (
                            <button
                              disabled={shipMut.isPending}
                              onClick={() => shipMut.mutate(so.shipping_order_id)}
                              className="text-xs px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                            >
                              출하 확정
                            </button>
                          )}
                          {so.shipping_status === "SHIPPED" && (
                            <span className="text-xs text-green-600 font-medium">출하됨</span>
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

      {tab === "claims" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
            <FileText size={16} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-700">클레임 목록</span>
          </div>

          {claimsLoading ? (
            <div className="p-8 text-center text-gray-400 text-sm">로딩 중...</div>
          ) : claims.length === 0 ? (
            <div className="p-8 text-center text-gray-400 text-sm">클레임 없음</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {["클레임번호", "유형", "심각도", "클레임일", "상태"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {claims.map((c) => (
                  <tr key={c.claim_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">{c.claim_no}</td>
                    <td className="px-4 py-3 text-gray-700">{c.claim_type}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${severityConfig[c.claim_severity] ?? ""}`}>
                        {c.claim_severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">{c.claim_date}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${claimStatusConfig[c.status] ?? ""}`}>
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
