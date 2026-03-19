"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard, Database, Building2, FileText,
  GitCompare, ClipboardCheck, Settings,
  Activity, FileBarChart, Zap, ChevronRight
} from "lucide-react"
import { cn } from "@/lib/utils"

const NAV_SECTIONS = [
  {
    label: "Main",
    items: [
      { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
      { href: "/technical-data", icon: Database, label: "Technical Data" },
      { href: "/oems", icon: Building2, label: "OEM Library" },
    ],
  },
  {
    label: "Compliance",
    items: [
      { href: "/rfq", icon: FileText, label: "RFQ Manager", badge: "AI" },
      { href: "/projects", icon: ClipboardCheck, label: "Projects" },
      { href: "/workflow", icon: Activity, label: "Workflow" },
    ],
  },
  {
    label: "Tools",
    items: [
      { href: "/tech-signal", icon: FileBarChart, label: "Tech Signal" },
      { href: "/compare", icon: GitCompare, label: "Comparison" },
    ],
  },
  {
    label: "System",
    items: [
      { href: "/settings", icon: Settings, label: "Settings" },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-[230px] bg-navy-gradient flex flex-col shadow-xl">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
        <div className="relative">
          <div className="w-9 h-9 rounded-xl bg-brand-gradient flex items-center justify-center shadow-glow">
            <Zap className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 rounded-full border-2 border-navy" />
        </div>
        <div>
          <div className="text-sm font-bold text-white leading-tight tracking-tight">UnityESS</div>
          <div className="text-[10px] text-slate-400 font-medium tracking-wide">Technical Compliance</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin px-3 py-5 space-y-6">
        {NAV_SECTIONS.map((section, sIdx) => (
          <div key={section.label} className="animate-slide-in-left" style={{ animationDelay: `${sIdx * 80}ms`, animationFillMode: 'both' }}>
            <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500 px-3 mb-2">
              {section.label}
            </div>
            <div className="space-y-1">
              {section.items.map((item) => {
                const active = pathname === item.href || pathname.startsWith(item.href + "/")
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-200 relative",
                      active
                        ? "bg-white/10 text-white font-semibold shadow-inner-glow"
                        : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                    )}
                  >
                    {active && (
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-brand animate-scale-in" />
                    )}
                    <item.icon className={cn(
                      "w-[18px] h-[18px] transition-all duration-200 flex-shrink-0",
                      active ? "text-brand" : "text-slate-500 group-hover:text-slate-300"
                    )} />
                    <span className="flex-1">{item.label}</span>
                    {"badge" in item && item.badge && (
                      <span className="text-[9px] font-bold bg-brand-gradient text-white px-1.5 py-0.5 rounded-md uppercase tracking-wider">
                        {item.badge}
                      </span>
                    )}
                    {active && <ChevronRight className="w-3.5 h-3.5 text-slate-500" />}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/10 px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] text-slate-500">System Online</span>
        </div>
        <div className="text-[10px] text-slate-600 mt-1.5">Ornate Agencies Pvt. Ltd. · v2.2.0</div>
      </div>
    </aside>
  )
}
