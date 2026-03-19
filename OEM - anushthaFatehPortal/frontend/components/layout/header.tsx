"use client"

import { useAuth } from "@/lib/auth"
import { useRouter } from "next/navigation"
import { Bell, LogOut, Search, Sparkles } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useState } from "react"

const ROLE_CONFIG: Record<string, { bg: string; text: string; dot: string }> = {
  admin:      { bg: "bg-purple-100", text: "text-purple-700", dot: "bg-purple-400" },
  engineer:   { bg: "bg-blue-100",   text: "text-blue-700",   dot: "bg-blue-400" },
  reviewer:   { bg: "bg-amber-100",  text: "text-amber-700",  dot: "bg-amber-400" },
  commercial: { bg: "bg-emerald-100",text: "text-emerald-700",dot: "bg-emerald-400" },
  customer:   { bg: "bg-slate-100",  text: "text-slate-700",  dot: "bg-slate-400" },
}

export function Header() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [searchFocused, setSearchFocused] = useState(false)
  const role = ROLE_CONFIG[user?.role || "admin"] || ROLE_CONFIG.admin

  const handleLogout = () => { logout(); router.push("/login") }

  return (
    <header className="h-[60px] border-b bg-white/80 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-30 animate-fade-in-down">
      {/* Left: Search */}
      <div className="flex items-center gap-4 flex-1">
        <div className={`relative transition-all duration-300 ${searchFocused ? "w-80" : "w-64"}`}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 transition-colors" />
          <input
            type="text"
            placeholder="Search models, OEMs, projects..."
            className="w-full h-9 pl-10 pr-4 text-sm bg-slate-50 border border-transparent rounded-xl
                       placeholder:text-slate-400 text-slate-700
                       focus:bg-white focus:border-brand/30 focus:ring-2 focus:ring-brand/10
                       focus:outline-none transition-all duration-300"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
            /
          </kbd>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" className="gap-1.5 text-xs text-slate-500 hover:text-brand">
          <Sparkles className="w-3.5 h-3.5" />
          AI Assist
        </Button>

        <div className="w-px h-6 bg-slate-200 mx-1" />

        <Button variant="ghost" size="icon" className="relative group">
          <Bell className="w-4 h-4 text-slate-500 group-hover:text-slate-700 transition-colors" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand rounded-full dot-pulse" />
        </Button>

        {user && (
          <>
            <div className="w-px h-6 bg-slate-200 mx-1" />
            <div className="flex items-center gap-3 group cursor-pointer" onClick={() => router.push("/settings")}>
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-navy to-navy-light flex items-center justify-center
                                ring-2 ring-white shadow-sm group-hover:shadow-md transition-shadow">
                  <span className="text-white text-xs font-bold">
                    {user.name?.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()}
                  </span>
                </div>
                <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 ${role.dot} rounded-full border-2 border-white`} />
              </div>
              <div className="hidden lg:block">
                <div className="text-xs font-semibold text-slate-800 leading-tight group-hover:text-brand transition-colors">
                  {user.name}
                </div>
                <div className={`text-[10px] font-bold ${role.text} ${role.bg} rounded-md px-1.5 py-0.5 inline-block mt-0.5`}>
                  {user.role?.charAt(0).toUpperCase() + user.role?.slice(1)}
                </div>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={handleLogout} className="ml-1 hover:bg-red-50 hover:text-red-500 transition-all">
              <LogOut className="w-4 h-4" />
            </Button>
          </>
        )}
      </div>
    </header>
  )
}
