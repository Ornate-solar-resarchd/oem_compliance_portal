"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getDashboardSummary } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Building2, Layers, CheckCircle2, BarChart3,
  Zap, Box, Cpu, Wifi, FileText, ArrowRight,
  AlertTriangle, Loader2, TrendingUp, Database,
} from "lucide-react"

/* ── Types ── */
interface Summary {
  totals: { oems: number; models: number; avg_completeness: number; approved_oems: number }
  category_breakdown: { category: string; count: number }[]
  oem_summary: { id: string; name: string; model_count: number; avg_completeness: number; categories: string[]; is_approved: boolean }[]
  data_coverage: { id: string; oem_name: string; model_name: string; category: string; completeness: number; parameters_count: number; has_datasheet: boolean }[]
  recent_imports: { id: string; oem_name: string; model_name: string; category: string; source: string; datasheet: string; completeness: number }[]
}

/* ── Helpers ── */
const CATEGORY_ICONS: Record<string, any> = {
  "Cell": Zap,
  "PCS": Cpu,
  "EMS": Wifi,
  "DC Block": Box,
}

const CATEGORY_COLORS: Record<string, string> = {
  "Cell": "from-blue-500 to-blue-600",
  "PCS": "from-violet-500 to-violet-600",
  "EMS": "from-emerald-500 to-emerald-600",
  "DC Block": "from-amber-500 to-amber-600",
}

const CATEGORY_BG: Record<string, string> = {
  "Cell": "bg-blue-50",
  "PCS": "bg-violet-50",
  "EMS": "bg-emerald-50",
  "DC Block": "bg-amber-50",
}

const CATEGORY_TEXT: Record<string, string> = {
  "Cell": "text-blue-600",
  "PCS": "text-violet-600",
  "EMS": "text-emerald-600",
  "DC Block": "text-amber-600",
}

function scoreColor(s: number) {
  if (s >= 80) return "text-emerald-600"
  if (s >= 60) return "text-amber-500"
  return "text-red-500"
}

function scoreBar(s: number) {
  if (s >= 80) return "bg-emerald-500"
  if (s >= 60) return "bg-amber-400"
  return "bg-red-400"
}

/* ── Page ── */
export default function DashboardPage() {
  const router = useRouter()
  const [data, setData] = useState<Summary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboardSummary()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-slate-300" />
      </div>
    )
  }

  if (!data) return null

  const { totals, category_breakdown, oem_summary, data_coverage, recent_imports } = data

  const quickLinks = [
    { label: "OEM Library", desc: "Browse all models & specs", icon: Building2, href: "/oems", color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Compare Models", desc: "Side-by-side spec comparison", icon: BarChart3, href: "/compare", color: "text-violet-600", bg: "bg-violet-50" },
    { label: "RFQ Matching", desc: "Match RFQ to best OEM", icon: FileText, href: "/rfq", color: "text-emerald-600", bg: "bg-emerald-50" },
    { label: "Projects", desc: "Track compliance projects", icon: Layers, href: "/projects", color: "text-amber-600", bg: "bg-amber-50" },
  ]

  // Models needing attention (completeness < 70%)
  const needsAttention = data_coverage.filter(c => c.completeness < 70)

  return (
    <div className="space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">BESS OEM data overview</p>
      </div>

      {/* ── Top KPIs ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total OEMs", value: totals.oems, icon: Building2, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Total Models", value: totals.models, icon: Database, color: "text-violet-600", bg: "bg-violet-50" },
          { label: "Avg Data Completeness", value: `${totals.avg_completeness}%`, icon: TrendingUp, color: "text-emerald-600", bg: "bg-emerald-50" },
          { label: "Categories Covered", value: category_breakdown.filter(c => c.count > 0).length, icon: Layers, color: "text-amber-600", bg: "bg-amber-50" },
        ].map(kpi => (
          <Card key={kpi.label}>
            <CardContent className="pt-5 pb-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-slate-500">{kpi.label}</p>
                  <p className="text-3xl font-bold text-slate-900 mt-1">{kpi.value}</p>
                </div>
                <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center", kpi.bg)}>
                  <kpi.icon className={cn("h-6 w-6", kpi.color)} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ── Category Breakdown + Quick Links ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Category Breakdown */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Models by Category</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {category_breakdown.map(cat => {
              const Icon = CATEGORY_ICONS[cat.category] || Box
              const pct = totals.models > 0 ? Math.round((cat.count / totals.models) * 100) : 0
              return (
                <div key={cat.category} className="flex items-center gap-3">
                  <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0", CATEGORY_BG[cat.category])}>
                    <Icon className={cn("h-4 w-4", CATEGORY_TEXT[cat.category])} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-slate-700">{cat.category}</span>
                      <span className="text-sm font-bold text-slate-800">{cat.count} models</span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full bg-gradient-to-r", CATEGORY_COLORS[cat.category])}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-slate-400 w-8 text-right">{pct}%</span>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Quick Links */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Quick Access</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            {quickLinks.map(link => (
              <button
                key={link.href}
                onClick={() => router.push(link.href)}
                className="flex items-start gap-3 p-3 rounded-xl border border-slate-100 hover:border-slate-200 hover:shadow-sm transition-all text-left group"
              >
                <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5", link.bg)}>
                  <link.icon className={cn("h-4 w-4", link.color)} />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800 group-hover:text-slate-900">{link.label}</p>
                  <p className="text-xs text-slate-400 mt-0.5 leading-tight">{link.desc}</p>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* ── OEM Summary ── */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">OEM Summary</CardTitle>
            <button onClick={() => router.push("/oems")} className="text-xs text-blue-600 font-semibold hover:underline flex items-center gap-1">
              View All <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-[10px] uppercase tracking-wider text-slate-400">
                  <th className="text-left py-2 pr-4 font-semibold">OEM</th>
                  <th className="text-center py-2 px-3 font-semibold">Models</th>
                  <th className="text-left py-2 px-3 font-semibold w-[35%]">Data Completeness</th>
                  <th className="text-left py-2 px-3 font-semibold">Categories</th>
                </tr>
              </thead>
              <tbody>
                {oem_summary.map(oem => (
                  <tr
                    key={oem.id}
                    className="border-b border-slate-50 hover:bg-slate-50/60 cursor-pointer transition-colors"
                    onClick={() => router.push("/oems")}
                  >
                    <td className="py-2.5 pr-4">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">
                          {oem.name.charAt(0)}
                        </div>
                        <span className="font-semibold text-slate-800">{oem.name}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="font-bold text-slate-700">{oem.model_count}</span>
                    </td>
                    <td className="py-2.5 px-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div className={cn("h-full rounded-full", scoreBar(oem.avg_completeness))}
                            style={{ width: `${oem.avg_completeness}%` }} />
                        </div>
                        <span className={cn("text-xs font-bold tabular-nums w-9 text-right", scoreColor(oem.avg_completeness))}>
                          {oem.avg_completeness}%
                        </span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3">
                      <div className="flex flex-wrap gap-1">
                        {oem.categories.map(cat => (
                          <span key={cat} className={cn("text-[10px] px-1.5 py-0.5 rounded font-medium", CATEGORY_BG[cat], CATEGORY_TEXT[cat])}>
                            {cat}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* ── Recent Imports + Needs Attention ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Recent Imports */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Recent Imports</CardTitle>
          </CardHeader>
          <CardContent>
            {recent_imports.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">No recent imports</p>
            ) : (
              <div className="space-y-2">
                {recent_imports.map(imp => {
                  const Icon = CATEGORY_ICONS[imp.category] || FileText
                  return (
                    <div key={imp.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors">
                      <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0", CATEGORY_BG[imp.category])}>
                        <Icon className={cn("h-3.5 w-3.5", CATEGORY_TEXT[imp.category])} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-800 truncate">{imp.model_name}</p>
                        <p className="text-xs text-slate-400">{imp.oem_name} · {imp.category}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <span className={cn("text-sm font-bold", scoreColor(imp.completeness))}>
                          {imp.completeness}%
                        </span>
                        <p className="text-[10px] text-slate-300 capitalize">{imp.source}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Needs Attention */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              <CardTitle className="text-base">Needs Attention</CardTitle>
              <span className="text-xs text-slate-400">— completeness below 70%</span>
            </div>
          </CardHeader>
          <CardContent>
            {needsAttention.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 gap-2">
                <CheckCircle2 className="h-8 w-8 text-emerald-400" />
                <p className="text-sm text-slate-400">All models look good!</p>
              </div>
            ) : (
              <div className="space-y-2">
                {needsAttention.slice(0, 8).map(c => (
                  <div key={c.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => router.push("/oems")}>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-slate-800 truncate">{c.model_name}</p>
                      <p className="text-xs text-slate-400">{c.oem_name} · {c.category} · {c.parameters_count} params</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0 w-28">
                      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className={cn("h-full rounded-full", scoreBar(c.completeness))}
                          style={{ width: `${c.completeness}%` }} />
                      </div>
                      <span className={cn("text-xs font-bold w-9 text-right", scoreColor(c.completeness))}>
                        {c.completeness}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

    </div>
  )
}
