"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Package, FileText, Truck,
  Cpu, Bot, BarChart2, BookOpen, Database, Settings, LogOut,
} from "lucide-react";
import { useAuth } from "@/lib/auth";

const nav = [
  { href: "/",          label: "AI 대시보드",       icon: LayoutDashboard },
  { href: "/receiving", label: "입고재고관리",       icon: Package },
  { href: "/orders",    label: "수주견적AI관리",     icon: FileText },
  { href: "/shipping",  label: "출하물류관리",       icon: Truck },
  { href: "/production",label: "공정관리",           icon: Cpu },
  { href: "/ai",        label: "AI Agent 통합",     icon: Bot },
  { href: "/kpi",       label: "KPI관리",            icon: BarChart2 },
  { href: "/standards", label: "기준정보관리",       icon: BookOpen },
  { href: "/data",      label: "데이터관리",         icon: Database },
  { href: "/admin",     label: "시스템관리",         icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="flex flex-col w-56 min-h-screen bg-gray-900 text-white">
      <div className="px-5 py-4 border-b border-gray-700">
        <p className="text-xs text-gray-400">부영기업</p>
        <h1 className="text-lg font-bold tracking-tight">AI MES</h1>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                active
                  ? "bg-blue-600 text-white"
                  : "text-gray-300 hover:bg-gray-800"
              }`}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-4 py-3 border-t border-gray-700 text-sm">
        {user && (
          <div className="mb-2 text-gray-400 truncate">
            <span className="text-white font-medium">{user.username}</span>
            <span className="ml-1 text-xs">({user.role})</span>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <LogOut size={14} /> 로그아웃
        </button>
      </div>
    </aside>
  );
}
