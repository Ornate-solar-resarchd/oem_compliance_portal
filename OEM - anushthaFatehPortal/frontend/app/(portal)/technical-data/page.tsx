"use client"

import { useEffect, useState, useMemo } from "react"
import { getComponents, getComponentParams } from "@/lib/api"
import { cn, scoreColor } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { ScoreRing } from "@/components/shared/score-ring"
import { StatusBadge } from "@/components/shared/status-badge"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Cell,
} from "recharts"
import {
  Search, Zap, Thermometer, Shield, Activity, Box, ChevronDown, ChevronRight,
  LayoutGrid, List, ExternalLink, Building2, X, Loader2, CheckCircle2, XCircle, AlertTriangle
} from "lucide-react"

/* ── Types ── */
interface Component {
  id: string; oem_id: string; oem_name: string; model_name: string; sku: string
  component_type_name: string; fill_rate: number; compliance_score: number
  is_active: boolean; pass: number; fail: number; waived: number; datasheet: string
}
interface Param { code: string; name: string; value: string; unit: string; section: string; status: string; confidence: number }

/* ── OEM Config ── */
const OEM_INFO: Record<string, { color: string; website: string; logo: string; tagline: string }> = {
  "CATL":    { color: "from-blue-500 to-blue-600",     website: "https://catl.com",        logo: "C", tagline: "World's largest battery manufacturer" },
  "Lishen":  { color: "from-emerald-500 to-emerald-600", website: "https://lishen.com.cn", logo: "L", tagline: "Tianjin Lishen Battery" },
  "BYD":     { color: "from-red-500 to-red-600",       website: "https://byd.com",          logo: "B", tagline: "Build Your Dreams — Blade Battery" },
  "HiTHIUM": { color: "from-purple-500 to-purple-600", website: "https://hithium.com",      logo: "H", tagline: "High-Tech Energy Storage" },
  "SVOLT":   { color: "from-amber-500 to-amber-600",   website: "https://www.svolt.cn/en",  logo: "S", tagline: "Short Blade LFP Technology" },
}

const SECTION_ICON: Record<string, any> = {
  Electrical: Zap, Physical: Box, Thermal: Thermometer, Safety: Shield, Performance: Activity,
}

const SECTION_COLOR: Record<string, string> = {
  Electrical: "text-amber-500", Physical: "text-blue-500", Thermal: "text-orange-500", Safety: "text-red-500", Performance: "text-emerald-500",
}

/* ── Page ── */
export default function TechnicalDataPage() {
  const [components, setComponents] = useState<Component[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<"card" | "list">("card")
  const [search, setSearch] = useState("")
  const [selectedOEM, setSelectedOEM] = useState("")
  const [selectedType, setSelectedType] = useState("")
  const [expandedOEMs, setExpandedOEMs] = useState<Set<string>>(new Set())

  // Detail expand
  const [expanded, setExpanded] = useState<Record<string, Param[]>>({})
  const [loadingParams, setLoadingParams] = useState<Record<string, boolean>>({})

  useEffect(() => {
    getComponents().then(d => {
      const items = d.items || []
      setComponents(items)
      setExpandedOEMs(new Set(items.map((c: Component) => c.oem_name)))
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  /* Derived */
  const oemList = useMemo(() => (Array.from(new Set(components.map(c => c.oem_name).filter(Boolean))) as string[]).sort(), [components])
  const typeList = useMemo(() => (Array.from(new Set(components.map(c => c.component_type_name).filter(Boolean))) as string[]).sort(), [components])

  const filtered = useMemo(() => {
    let list = components.filter(c => c.is_active)
    if (selectedOEM) list = list.filter(c => c.oem_name === selectedOEM)
    if (selectedType) list = list.filter(c => c.component_type_name === selectedType)
    if (search) {
      const q = search.toLowerCase()
      list = list.filter(c => c.model_name.toLowerCase().includes(q) || c.oem_name.toLowerCase().includes(q) || c.sku.toLowerCase().includes(q))
    }
    return list
  }, [components, selectedOEM, selectedType, search])

  const groupedByOEM = useMemo(() => {
    const map = new Map<string, Component[]>()
    for (const c of filtered) {
      if (!map.has(c.oem_name)) map.set(c.oem_name, [])
      map.get(c.oem_name)!.push(c)
    }
    return map
  }, [filtered])

  async function toggleExpand(id: string) {
    if (expanded[id]) {
      const next = { ...expanded }; delete next[id]; setExpanded(next); return
    }
    setLoadingParams(p => ({ ...p, [id]: true }))
    try {
      const d = await getComponentParams(id)
      setExpanded(p => ({ ...p, [id]: d.items || [] }))
    } catch (e) { console.error(e) }
    finally { setLoadingParams(p => ({ ...p, [id]: false })) }
  }

  function toggleOEMExpand(oem: string) {
    setExpandedOEMs(prev => { const n = new Set(prev); if (n.has(oem)) n.delete(oem); else n.add(oem); return n })
  }

  /* Group params by section */
  function groupParams(params: Param[]) {
    const map: Record<string, Param[]> = {}
    params.forEach(p => { const s = p.section || "General"; if (!map[s]) map[s] = []; map[s].push(p) })
    return map
  }

  /* Radar data from params */
  function radarData(params: Param[]) {
    const sections = ["Electrical", "Physical", "Thermal", "Safety", "Performance"]
    return sections.map(s => {
      const sp = params.filter(p => (p.section || "").includes(s))
      const total = sp.length
      const pass = sp.filter(p => p.status === "pass").length
      return { section: s, score: total > 0 ? Math.round((pass / total) * 100) : 0 }
    })
  }

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Technical Data</h1>
          <p className="text-sm text-slate-500 mt-1">All OEM models with specs, charts — grouped by manufacturer</p>
        </div>
        <div className="flex items-center gap-2 border rounded-lg p-0.5 bg-slate-50">
          <button onClick={() => setViewMode("card")} className={cn("p-2 rounded-md transition-all", viewMode === "card" ? "bg-white shadow-sm text-brand" : "text-slate-400 hover:text-slate-600")}>
            <LayoutGrid className="w-4 h-4" />
          </button>
          <button onClick={() => setViewMode("list")} className={cn("p-2 rounded-md transition-all", viewMode === "list" ? "bg-white shadow-sm text-brand" : "text-slate-400 hover:text-slate-600")}>
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input placeholder="Search models, OEMs, SKU..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
        </div>
        <select value={selectedOEM} onChange={e => setSelectedOEM(e.target.value)}
          className="h-9 px-3 pr-8 text-sm border rounded-xl bg-white text-slate-700 focus:border-brand focus:ring-2 focus:ring-brand/20 focus:outline-none cursor-pointer">
          <option value="">All Manufacturers</option>
          {oemList.map(oem => <option key={oem} value={oem}>{oem}</option>)}
        </select>
        <select value={selectedType} onChange={e => setSelectedType(e.target.value)}
          className="h-9 px-3 pr-8 text-sm border rounded-xl bg-white text-slate-700 focus:border-brand focus:ring-2 focus:ring-brand/20 focus:outline-none cursor-pointer">
          <option value="">All Types</option>
          {typeList.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {(selectedOEM || selectedType || search) && (
          <button onClick={() => { setSelectedOEM(""); setSelectedType(""); setSearch("") }}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-brand transition-colors"><X className="w-3 h-3" /> Clear</button>
        )}
        <div className="ml-auto text-xs text-slate-400">{filtered.length} models across {groupedByOEM.size} OEMs</div>
      </div>

      {/* OEM Quick Filter Chips */}
      <div className="flex items-center gap-2 flex-wrap">
        <Building2 className="w-3.5 h-3.5 text-slate-400" />
        {oemList.map(oem => {
          const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", logo: oem[0] }
          const active = selectedOEM === oem
          return (
            <button key={oem} onClick={() => setSelectedOEM(active ? "" : oem)}
              className={cn("flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all",
                active ? "bg-brand text-white border-brand shadow-glow" : "bg-white text-slate-600 border-slate-200 hover:border-brand/30")}>
              <div className={cn("w-4 h-4 rounded bg-gradient-to-br flex items-center justify-center text-white text-[8px] font-bold", active ? "opacity-80" : info.color)}>
                {info.logo}
              </div>
              {oem}
              {active && <X className="w-3 h-3 ml-0.5" />}
            </button>
          )
        })}
      </div>

      {/* Content */}
      {filtered.length === 0 ? (
        <Card><CardContent className="py-16 text-center">
          <Box className="h-12 w-12 mx-auto text-slate-200 mb-4" />
          <h3 className="text-lg font-semibold text-slate-600">No models found</h3>
          <p className="text-sm text-slate-400 mt-1">Try adjusting your filters</p>
        </CardContent></Card>
      ) : viewMode === "card" ? (
        /* ════════ CARD VIEW ════════ */
        <div className="space-y-8 stagger-children">
          {Array.from(groupedByOEM.entries()).map(([oem, models]) => {
            const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", website: "#", logo: oem[0], tagline: "" }
            const isExpOEM = expandedOEMs.has(oem)
            const avgScore = Math.round(models.reduce((s, m) => s + m.compliance_score, 0) / models.length)
            return (
              <div key={oem}>
                {/* OEM Section Header */}
                <div className="flex items-center gap-4 mb-4 cursor-pointer group" onClick={() => toggleOEMExpand(oem)}>
                  {isExpOEM ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                  <div className={cn("w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white text-lg font-bold shadow-md", info.color)}>
                    {info.logo}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-800 group-hover:text-brand transition-colors">{oem}</h2>
                      <Badge variant="default" className="text-[10px]">{models.length} model{models.length !== 1 ? "s" : ""}</Badge>
                      <span className={cn("text-sm font-bold", scoreColor(avgScore))}>{avgScore}% avg</span>
                    </div>
                    {info.tagline && <p className="text-xs text-slate-400 mt-0.5">{info.tagline}</p>}
                  </div>
                  <a href={info.website} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
                    className="text-slate-300 hover:text-brand transition-colors flex items-center gap-1 text-xs">
                    <ExternalLink className="w-3.5 h-3.5" /> Website
                  </a>
                </div>

                {/* Models Grid */}
                {isExpOEM && (
                  <div className="space-y-3 ml-[56px]">
                    {models.map(comp => {
                      const isExpanded = !!expanded[comp.id]
                      const isLoadingP = !!loadingParams[comp.id]
                      const params = expanded[comp.id] || []
                      const grouped = groupParams(params)
                      return (
                        <div key={comp.id} className="border rounded-xl bg-white overflow-hidden transition-all hover:shadow-md">
                          {/* Card Header — always visible */}
                          <div className="flex items-center gap-4 p-4 cursor-pointer" onClick={() => toggleExpand(comp.id)}>
                            <ScoreRing score={comp.compliance_score} size={52} strokeWidth={4} />
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-bold text-slate-800">{comp.model_name}</div>
                              <div className="text-xs text-slate-400 mt-0.5">{comp.sku} · {comp.component_type_name}</div>
                            </div>
                            <div className="flex items-center gap-2 text-[10px]">
                              <span className="flex items-center gap-1 text-emerald-600 font-semibold"><CheckCircle2 className="h-3 w-3" />{comp.pass}P</span>
                              {comp.fail > 0 && <span className="flex items-center gap-1 text-red-500 font-semibold"><XCircle className="h-3 w-3" />{comp.fail}F</span>}
                              {comp.waived > 0 && <span className="flex items-center gap-1 text-amber-500 font-semibold"><AlertTriangle className="h-3 w-3" />{comp.waived}W</span>}
                            </div>
                            <div className="flex items-center gap-1.5 text-xs text-slate-400">
                              Fill <Progress value={comp.fill_rate} className="h-1.5 w-10" /> {comp.fill_rate}%
                            </div>
                            {isLoadingP ? <Loader2 className="w-4 h-4 animate-spin text-brand" /> :
                              isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                          </div>

                          {/* Expanded Detail */}
                          {isExpanded && params.length > 0 && (
                            <div className="border-t animate-fade-in" style={{ animationFillMode: "both" }}>
                              {/* Charts Row */}
                              <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50/50">
                                {/* Electrical Bar Chart */}
                                <div>
                                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Electrical Parameters</div>
                                  <ResponsiveContainer width="100%" height={180}>
                                    <BarChart data={params.filter(p => (p.section || "").includes("Electrical") && !isNaN(parseFloat(p.value))).map(p => ({
                                      name: p.name.length > 14 ? p.name.slice(0, 14) + "…" : p.name, value: parseFloat(p.value), unit: p.unit, fullName: p.name
                                    }))} margin={{ top: 5, right: 10, bottom: 30, left: 0 }}>
                                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                      <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-25} textAnchor="end" height={50} />
                                      <YAxis tick={{ fontSize: 10 }} />
                                      <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 11 }}
                                        formatter={(v: number, n: string, p: any) => [`${v} ${p.payload.unit}`, p.payload.fullName]} />
                                      <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={20}>
                                        {params.filter(p => (p.section || "").includes("Electrical") && !isNaN(parseFloat(p.value))).map((_, i) =>
                                          <Cell key={i} fill={["#3b82f6", "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8", "#6d28d9", "#4f46e5"][i % 8]} />)}
                                      </Bar>
                                    </BarChart>
                                  </ResponsiveContainer>
                                </div>
                                {/* Radar Chart */}
                                <div>
                                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Section Pass Rates</div>
                                  <ResponsiveContainer width="100%" height={180}>
                                    <RadarChart data={radarData(params)}>
                                      <PolarGrid stroke="#e2e8f0" />
                                      <PolarAngleAxis dataKey="section" tick={{ fontSize: 10 }} />
                                      <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 9 }} />
                                      <Radar dataKey="score" stroke="#F26B4E" fill="#F26B4E" fillOpacity={0.15} strokeWidth={2} />
                                    </RadarChart>
                                  </ResponsiveContainer>
                                </div>
                              </div>

                              {/* Parameter Tables by Section */}
                              <div className="p-4 space-y-4">
                                {Object.entries(grouped).map(([section, sectionParams]) => {
                                  const Icon = SECTION_ICON[section] || Box
                                  const color = SECTION_COLOR[section] || "text-slate-500"
                                  return (
                                    <div key={section}>
                                      <div className="flex items-center gap-2 mb-2">
                                        <Icon className={cn("w-3.5 h-3.5", color)} />
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{section}</span>
                                        <span className="text-[10px] text-slate-300">{sectionParams.length} params</span>
                                      </div>
                                      <div className="rounded-lg border overflow-hidden">
                                        <table className="w-full text-xs table-fixed">
                                          <thead><tr className="bg-slate-50 border-b text-[10px] uppercase tracking-wider text-slate-400">
                                            <th className="py-2 px-4 text-left font-semibold w-[40%]">Parameter</th>
                                            <th className="py-2 px-4 text-right font-semibold w-[25%]">Value</th>
                                            <th className="py-2 px-4 text-center font-semibold w-[15%]">Status</th>
                                            <th className="py-2 px-4 text-right font-semibold w-[20%]">Confidence</th>
                                          </tr></thead>
                                          <tbody>
                                            {sectionParams.map((p, i) => (
                                              <tr key={p.code} className={cn("border-b last:border-0", i % 2 ? "bg-slate-50/50" : "")}>
                                                <td className="py-2 px-4 font-medium text-slate-700">{p.name} <span className="text-slate-300 font-mono text-[9px] block mt-0.5">{p.code}</span></td>
                                                <td className="py-2 px-4 text-right font-semibold text-slate-800 tabular-nums">{p.value} <span className="text-slate-400 font-normal">{p.unit}</span></td>
                                                <td className="py-2 px-4 text-center"><StatusBadge status={p.status} /></td>
                                                <td className="py-2 px-4 text-right"><div className="flex items-center justify-end gap-2"><Progress value={p.confidence * 100} className="h-1.5 w-16" /><span className="text-slate-500 text-[10px] tabular-nums w-8">{Math.round(p.confidence * 100)}%</span></div></td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      </div>
                                    </div>
                                  )
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      ) : (
        /* ════════ LIST VIEW ════════ */
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b text-[10px] uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 text-left font-semibold">OEM</th>
                  <th className="py-3 px-4 text-left font-semibold">Model</th>
                  <th className="py-3 px-4 text-left font-semibold">SKU</th>
                  <th className="py-3 px-4 text-left font-semibold">Type</th>
                  <th className="py-3 px-4 text-center font-semibold">Score</th>
                  <th className="py-3 px-4 text-center font-semibold">Fill</th>
                  <th className="py-3 px-4 text-center font-semibold">Pass</th>
                  <th className="py-3 px-4 text-center font-semibold">Fail</th>
                  <th className="py-3 px-4 text-center font-semibold">Waived</th>
                  <th className="py-3 px-4 text-center font-semibold">Datasheet</th>
                </tr>
              </thead>
              <tbody>
                {Array.from(groupedByOEM.entries()).map(([oem, models]) => {
                  const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", logo: oem[0], website: "#" }
                  return (
                    <>
                      {/* OEM Group Header */}
                      <tr key={`oem-${oem}`} className="bg-slate-50/80">
                        <td colSpan={10} className="py-2 px-4">
                          <div className="flex items-center gap-2">
                            <div className={cn("w-6 h-6 rounded-md bg-gradient-to-br flex items-center justify-center text-white text-[10px] font-bold", info.color)}>{info.logo}</div>
                            <span className="text-xs font-bold text-slate-700">{oem}</span>
                            <Badge variant="default" className="text-[9px]">{models.length}</Badge>
                            <a href={info.website} target="_blank" rel="noopener noreferrer" className="ml-auto text-slate-300 hover:text-brand transition-colors">
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        </td>
                      </tr>
                      {/* Model Rows */}
                      {models.map(comp => (
                        <tr key={comp.id} onClick={() => toggleExpand(comp.id)} className="border-b border-slate-50 table-row-hover cursor-pointer group">
                          <td className="py-2.5 px-4 pl-12 text-xs text-slate-500">{comp.oem_name}</td>
                          <td className="py-2.5 px-4"><span className="text-xs font-bold text-slate-800 group-hover:text-brand transition-colors">{comp.model_name}</span></td>
                          <td className="py-2.5 px-4 text-xs text-slate-400 font-mono">{comp.sku}</td>
                          <td className="py-2.5 px-4"><Badge variant="default" className="text-[10px]">{comp.component_type_name}</Badge></td>
                          <td className="py-2.5 px-4 text-center"><span className={cn("text-xs font-bold", scoreColor(comp.compliance_score))}>{comp.compliance_score}%</span></td>
                          <td className="py-2.5 px-4 text-center text-xs text-slate-500">{comp.fill_rate}%</td>
                          <td className="py-2.5 px-4 text-center text-xs text-emerald-600 font-semibold">{comp.pass}</td>
                          <td className="py-2.5 px-4 text-center text-xs text-red-500 font-semibold">{comp.fail}</td>
                          <td className="py-2.5 px-4 text-center text-xs text-amber-500 font-semibold">{comp.waived}</td>
                          <td className="py-2.5 px-4 text-center text-[10px] text-slate-400">{comp.datasheet?.split("-")[0]}</td>
                        </tr>
                      ))}
                    </>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
