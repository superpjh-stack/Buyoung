"use client";
import { useState } from "react";
import { Users, ScrollText, Bell, Settings, Search, Plus, Shield } from "lucide-react";

const TABS = [
  { key: "users",   label: "사용자관리", icon: Users },
  { key: "logs",    label: "시스템로그", icon: ScrollText },
  { key: "alerts",  label: "알림설정",   icon: Bell },
  { key: "system",  label: "시스템설정", icon: Settings },
] as const;

type Tab = typeof TABS[number]["key"];

interface User {
  user_id: string;
  username: string;
  name: string;
  role: "ADMIN" | "MANAGER" | "OPERATOR" | "INSPECTOR";
  department: string;
  email: string;
  status: "active" | "inactive";
  last_login: string;
}

const USERS: User[] = [
  { user_id: "u001", username: "admin",      name: "관리자",   role: "ADMIN",     department: "IT팀",      email: "admin@buyoung.co.kr",    status: "active",   last_login: "2026-06-03 08:12" },
  { user_id: "u002", username: "manager01",  name: "박정훈",   role: "MANAGER",   department: "생산관리팀", email: "pjh@buyoung.co.kr",       status: "active",   last_login: "2026-06-03 08:45" },
  { user_id: "u003", username: "operator01", name: "김철수",   role: "OPERATOR",  department: "성형팀",    email: "kcs@buyoung.co.kr",       status: "active",   last_login: "2026-06-03 07:55" },
  { user_id: "u004", username: "operator02", name: "이영희",   role: "OPERATOR",  department: "용접팀",    email: "lyh@buyoung.co.kr",       status: "active",   last_login: "2026-06-02 18:30" },
  { user_id: "u005", username: "inspector01",name: "최수진",   role: "INSPECTOR", department: "품질팀",    email: "csj@buyoung.co.kr",       status: "active",   last_login: "2026-06-03 09:00" },
  { user_id: "u006", username: "operator03", name: "박민준",   role: "OPERATOR",  department: "도장팀",    email: "pmj@buyoung.co.kr",       status: "inactive", last_login: "2026-05-28 17:10" },
];

const LOGS = [
  { time: "2026-06-03 09:12:34", level: "INFO",  user: "admin",       action: "시스템 설정 변경",              ip: "192.168.1.10" },
  { time: "2026-06-03 09:05:21", level: "INFO",  user: "manager01",   action: "작업지시 WO-2026-060200001 생성", ip: "192.168.1.15" },
  { time: "2026-06-03 08:55:10", level: "WARN",  user: "operator01",  action: "설비 센서 임계값 초과 감지",    ip: "192.168.1.22" },
  { time: "2026-06-03 08:45:00", level: "INFO",  user: "inspector01", action: "품질 검사 결과 등록 (PASS)",    ip: "192.168.1.30" },
  { time: "2026-06-03 08:32:11", level: "ERROR", user: "operator02",  action: "API 요청 실패 (500)",           ip: "192.168.1.18" },
  { time: "2026-06-03 08:21:45", level: "INFO",  user: "manager01",   action: "수주 SO-2026-0603 등록",        ip: "192.168.1.15" },
  { time: "2026-06-03 08:10:02", level: "INFO",  user: "admin",       action: "사용자 operator03 비활성화",    ip: "192.168.1.10" },
  { time: "2026-06-02 18:30:55", level: "INFO",  user: "operator03",  action: "로그아웃",                      ip: "192.168.1.20" },
];

const ROLE_CONFIG: Record<User["role"], { label: string; cls: string }> = {
  ADMIN:     { label: "ADMIN",     cls: "bg-red-100 text-red-700" },
  MANAGER:   { label: "MANAGER",   cls: "bg-blue-100 text-blue-700" },
  OPERATOR:  { label: "OPERATOR",  cls: "bg-green-100 text-green-700" },
  INSPECTOR: { label: "INSPECTOR", cls: "bg-purple-100 text-purple-700" },
};

const LOG_LEVEL_CLS: Record<string, string> = {
  INFO:  "bg-gray-100 text-gray-600",
  WARN:  "bg-yellow-100 text-yellow-700",
  ERROR: "bg-red-100 text-red-700",
};

interface AlertSetting {
  id: string;
  name: string;
  description: string;
  channel: string;
  enabled: boolean;
}

const ALERT_SETTINGS_INIT: AlertSetting[] = [
  { id: "a1", name: "설비 오류 알림",        description: "설비 상태가 ERROR로 변경 시",     channel: "이메일 + SMS", enabled: true },
  { id: "a2", name: "센서 임계값 초과",      description: "온도/압력/속도 경고 범위 초과 시", channel: "이메일",       enabled: true },
  { id: "a3", name: "작업지시 완료",         description: "작업지시 상태가 COMPLETED 전환 시", channel: "이메일",       enabled: false },
  { id: "a4", name: "품질 검사 불합격",      description: "검사 결과 FAIL 등록 시",           channel: "이메일 + SMS", enabled: true },
  { id: "a5", name: "납기 지연 위험",        description: "AI 납기 위험도 HIGH 감지 시",       channel: "이메일",       enabled: true },
  { id: "a6", name: "일일 생산 리포트",      description: "매일 오후 6시 자동 발송",           channel: "이메일",       enabled: true },
];

const SYSTEM_SETTINGS = [
  { group: "API 설정",     key: "API 서버 URL",        value: "http://localhost:8000" },
  { group: "API 설정",     key: "요청 타임아웃",        value: "30초" },
  { group: "데이터",       key: "자동 갱신 주기",       value: "15초" },
  { group: "데이터",       key: "데이터 보관 기간",     value: "3년" },
  { group: "AI 설정",      key: "AI Agent 모델",        value: "GPT-4o / RAG" },
  { group: "AI 설정",      key: "CAD 분석 타임아웃",    value: "120초" },
  { group: "보안",         key: "세션 만료 시간",       value: "8시간" },
  { group: "보안",         key: "비밀번호 정책",        value: "8자 이상, 특수문자 포함" },
];

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>("users");
  const [search, setSearch] = useState("");
  const [alerts, setAlerts] = useState(ALERT_SETTINGS_INIT);
  const [logLevel, setLogLevel] = useState("전체");

  const filteredUsers = USERS.filter(
    (u) =>
      u.username.toLowerCase().includes(search.toLowerCase()) ||
      u.name.includes(search) ||
      u.department.includes(search) ||
      u.role.toLowerCase().includes(search.toLowerCase())
  );

  const filteredLogs = LOGS.filter(
    (l) => logLevel === "전체" || l.level === logLevel
  );

  const toggleAlert = (id: string) =>
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, enabled: !a.enabled } : a)));

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">사용자 / 시스템 관리</h2>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Shield size={12} />
          관리자 전용
        </div>
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

      {/* === 사용자관리 === */}
      {tab === "users" && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-xs">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="이름, 아이디, 부서 검색..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button className="flex items-center gap-2 text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Plus size={14} /> 사용자 추가
            </button>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100">
              <span className="text-sm font-medium text-gray-700">사용자 목록</span>
              <span className="ml-2 text-xs text-gray-400">{filteredUsers.length}명</span>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {["아이디", "이름", "역할", "부서", "이메일", "상태", "최근 로그인"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filteredUsers.map((u) => {
                  const roleCfg = ROLE_CONFIG[u.role];
                  return (
                    <tr key={u.user_id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs font-medium text-gray-900">{u.username}</td>
                      <td className="px-4 py-3 text-gray-900 font-medium">{u.name}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${roleCfg.cls}`}>
                          {roleCfg.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600">{u.department}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{u.email}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          u.status === "active"
                            ? "bg-green-100 text-green-700"
                            : "bg-gray-100 text-gray-500"
                        }`}>
                          {u.status === "active" ? "활성" : "비활성"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs">{u.last_login}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === 시스템로그 === */}
      {tab === "logs" && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-medium">레벨 필터:</span>
            {["전체", "INFO", "WARN", "ERROR"].map((lv) => (
              <button
                key={lv}
                onClick={() => setLogLevel(lv)}
                className={`text-xs px-3 py-1 rounded-lg border transition-colors ${
                  logLevel === lv
                    ? "bg-gray-900 text-white border-gray-900"
                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                }`}
              >
                {lv}
              </button>
            ))}
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100">
              <span className="text-sm font-medium text-gray-700">시스템 로그</span>
              <span className="ml-2 text-xs text-gray-400">{filteredLogs.length}건</span>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {["시각", "레벨", "사용자", "작업 내용", "IP"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filteredLogs.map((log, i) => (
                  <tr key={i} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">{log.time}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${LOG_LEVEL_CLS[log.level] ?? ""}`}>
                        {log.level}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{log.user}</td>
                    <td className="px-4 py-3 text-gray-700">{log.action}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">{log.ip}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* === 알림설정 === */}
      {tab === "alerts" && (
        <div className="space-y-3">
          {alerts.map((a) => (
            <div
              key={a.id}
              className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between"
            >
              <div>
                <p className="text-sm font-medium text-gray-900">{a.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">{a.description}</p>
                <p className="text-xs text-gray-500 mt-0.5">
                  채널: <span className="font-medium">{a.channel}</span>
                </p>
              </div>
              <button
                onClick={() => toggleAlert(a.id)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  a.enabled ? "bg-blue-600" : "bg-gray-200"
                }`}
                role="switch"
                aria-checked={a.enabled}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                    a.enabled ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* === 시스템설정 === */}
      {tab === "system" && (
        <div className="space-y-4">
          {Array.from(new Set(SYSTEM_SETTINGS.map((s) => s.group))).map((group) => (
            <div key={group} className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100 bg-gray-50">
                <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">{group}</span>
              </div>
              <div className="divide-y divide-gray-50">
                {SYSTEM_SETTINGS.filter((s) => s.group === group).map((s) => (
                  <div key={s.key} className="px-5 py-3 flex items-center justify-between">
                    <span className="text-sm text-gray-600">{s.key}</span>
                    <span className="text-sm font-medium text-gray-900 font-mono">{s.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-4">
            <p className="text-sm font-medium text-yellow-700 mb-1">주의</p>
            <p className="text-xs text-yellow-600">
              시스템 설정 변경은 전체 서비스에 영향을 미칩니다. 변경 전 반드시 관리자 확인이 필요합니다.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
