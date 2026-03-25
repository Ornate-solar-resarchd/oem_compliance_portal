"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { getComponents, getComponentParams, generateTechnicalSignal } from "@/lib/api"
import { cn, formatNumber, scoreColor } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { ScoreRing } from "@/components/shared/score-ring"
import { StatusBadge } from "@/components/shared/status-badge"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import {
  ArrowLeft, Download, Loader2, CheckCircle2, XCircle, AlertTriangle,
  Search, LayoutGrid, List, Building2, ExternalLink, Filter, ChevronDown, ChevronRight, X, FileBarChart
} from "lucide-react"

/* ── Types ── */
interface Component {
  id: string; oem_id: string; oem_name: string; model_name: string; sku: string
  component_type_name: string; fill_rate: number; compliance_score: number
  is_active: boolean; pass: number; fail: number; waived: number
}
interface Param {
  code: string; name: string; value: string; unit: string; section: string; status: string; confidence: number
}

/* ── OEM Info ── */
const OEM_INFO: Record<string, { color: string; website: string; logo: string }> = {
  "CATL":    { color: "from-blue-500 to-blue-600", website: "https://catl.com", logo: "C" },
  "Lishen":  { color: "from-emerald-500 to-emerald-600", website: "https://lishen.com.cn", logo: "L" },
  "BYD":     { color: "from-red-500 to-red-600", website: "https://byd.com", logo: "B" },
  "HiTHIUM": { color: "from-purple-500 to-purple-600", website: "https://hithium.com", logo: "H" },
  "SVOLT":   { color: "from-amber-500 to-amber-600", website: "https://www.svolt.cn/en", logo: "S" },
}

const statusIcon = (s: string) => {
  if (s === "pass") return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
  if (s === "fail") return <XCircle className="h-3.5 w-3.5 text-red-500" />
  if (s === "waived") return <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
  return null
}

/* ── Page ── */
export default function TechSignalPage() {
  const [components, setComponents] = useState<Component[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [viewMode, setViewMode] = useState<"card" | "list">("card")
  const [selectedOEM, setSelectedOEM] = useState("")
  const [selectedType, setSelectedType] = useState("")

  // Detail state
  const [selected, setSelected] = useState<Component | null>(null)
  const [params, setParams] = useState<Param[]>([])
  const [paramsLoading, setParamsLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    getComponents().then(d => { setComponents(d.items || []); setLoading(false) }).catch(() => setLoading(false))
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

  /* Group by OEM for display */
  const groupedByOEM = useMemo(() => {
    const map = new Map<string, Component[]>()
    for (const c of filtered) {
      if (!map.has(c.oem_name)) map.set(c.oem_name, [])
      map.get(c.oem_name)!.push(c)
    }
    return map
  }, [filtered])

  const handleSelect = async (comp: Component) => {
    setSelected(comp); setParamsLoading(true)
    try { const d = await getComponentParams(comp.id); setParams(d.items || []) }
    catch (e) { console.error(e) }
    finally { setParamsLoading(false) }
  }

  const handleGenerate = async () => {
    if (!selected) return
    setGenerating(true)
    try { await generateTechnicalSignal({ component_id: selected.id }) }
    catch (e) { console.error(e) }
    finally { setGenerating(false) }
  }

  /* Grouped params */
  const groupedParams = useMemo(() => {
    const map: Record<string, Param[]> = {}
    params.forEach(p => { const s = p.section || "General"; if (!map[s]) map[s] = []; map[s].push(p) })
    return map
  }, [params])

  const chartData = useMemo(() =>
    params.filter(p => (p.section || "").toLowerCase().includes("electrical") && !isNaN(parseFloat(p.value)))
      .map(p => ({ name: p.name.length > 18 ? p.name.slice(0, 18) + "…" : p.name, fullName: p.name, value: parseFloat(p.value), unit: p.unit })),
    [params])

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>

  /* ══════════════ DETAIL VIEW ══════════════ */
  if (selected) {
    const info = OEM_INFO[selected.oem_name] || { color: "from-slate-500 to-slate-600", website: "#", logo: selected.oem_name[0] }
    return (
      <div className="space-y-6 animate-fade-in-up" style={{ animationFillMode: "both" }}>
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={() => { setSelected(null); setParams([]) }}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back
          </Button>
          <Button onClick={handleGenerate} disabled={generating}>
            {generating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
            Generate PDF
          </Button>
        </div>

        {paramsLoading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>
        ) : (
          <div className="max-w-5xl mx-auto bg-white rounded-xl border shadow-sm overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 px-8 py-6 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={cn("w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center text-white text-lg font-bold shadow-lg", info.color)}>
                    {info.logo}
                  </div>
                  <div>
                    <h1 className="text-xl font-bold">{selected.model_name}</h1>
                    <div className="flex items-center gap-3 mt-1 text-sm text-slate-300">
                      <span>{selected.oem_name}</span>
                      <span className="text-slate-500">·</span>
                      <span>{selected.component_type_name}</span>
                      <span className="text-slate-500">·</span>
                      <span>{selected.sku}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400 uppercase tracking-wider">Technical Signal</div>
                  <div className="text-xs text-slate-500 mt-1">{new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</div>
                </div>
              </div>
            </div>

            {/* Score Summary */}
            <div className="px-8 py-6 border-b flex items-center gap-8">
              <ScoreRing score={selected.compliance_score} size={80} />
              <div className="grid grid-cols-4 gap-3 flex-1">
                {[
                  { label: "Total", value: selected.pass + selected.fail + selected.waived, color: "text-slate-800", bg: "" },
                  { label: "Pass", value: selected.pass, color: "text-emerald-600", bg: "bg-emerald-50 border-emerald-200" },
                  { label: "Fail", value: selected.fail, color: "text-red-500", bg: "bg-red-50 border-red-200" },
                  { label: "Waived", value: selected.waived, color: "text-amber-600", bg: "bg-amber-50 border-amber-200" },
                ].map(k => (
                  <div key={k.label} className={cn("text-center py-3 rounded-xl border", k.bg)}>
                    <div className={cn("text-2xl font-bold", k.color)}>{k.value}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5 uppercase tracking-wider">{k.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Chart */}
            {chartData.length > 0 && (
              <div className="px-8 py-6 border-b">
                <h2 className="text-sm font-semibold text-slate-700 mb-4">Electrical Parameters</h2>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 40, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={60} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v: number, n: string, p: any) => [`${v} ${p.payload.unit}`, p.payload.fullName]}
                      contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 12 }} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {chartData.map((_, i) => <Cell key={i} fill={["#3b82f6", "#6366f1", "#8b5cf6"][i % 3]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Parameters */}
            <div className="px-8 py-6">
              <h2 className="text-sm font-semibold text-slate-700 mb-4">Full Parameter Listing</h2>
              <div className="space-y-5">
                {Object.entries(groupedParams).map(([section, sectionParams]) => (
                  <div key={section}>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 pb-1 border-b">{section}</div>
                    <div className="rounded-lg border overflow-hidden">
                      <table className="w-full text-xs table-fixed">
                        <thead>
                          <tr className="bg-slate-50 border-b text-[10px] uppercase tracking-wider text-slate-500">
                            <th className="py-2.5 px-4 text-left font-semibold w-[35%]">Parameter</th>
                            <th className="py-2.5 px-4 text-right font-semibold w-[25%]">Value</th>
                            <th className="py-2.5 px-4 text-center font-semibold w-[15%]">Status</th>
                            <th className="py-2.5 px-4 text-right font-semibold w-[25%]">Confidence</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sectionParams.map((p, i) => (
                            <tr key={p.code} className={cn("border-b last:border-0 table-row-hover", i % 2 === 0 ? "" : "bg-slate-50/50")}>
                              <td className="py-2.5 px-4 font-medium text-slate-700">{p.name}<span className="text-slate-300 font-mono text-[9px] block mt-0.5">{p.code}</span></td>
                              <td className="py-2.5 px-4 text-right font-semibold text-slate-800 tabular-nums">{p.value} <span className="text-slate-400 font-normal">{p.unit}</span></td>
                              <td className="py-2.5 px-4 text-center"><div className="flex items-center justify-center gap-1">{statusIcon(p.status)}<span className="capitalize">{p.status}</span></div></td>
                              <td className="py-2.5 px-4 text-right"><div className="flex items-center justify-end gap-2"><Progress value={p.confidence * 100} className="h-1.5 w-16" /><span className="text-slate-500 tabular-nums w-8 text-[10px]">{Math.round(p.confidence * 100)}%</span></div></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t px-8 py-3 text-[10px] text-slate-400 text-center">
              UnityESS Technical Compliance Portal · Generated {new Date().toLocaleDateString()}
            </div>
          </div>
        )}
      </div>
    )
  }

  /* ══════════════ LIST / CARD VIEW ══════════════ */
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Tech Signal</h1>
          <p className="text-sm text-slate-500 mt-1">Component technical data sheets — filter by manufacturer and model</p>
        </div>
        <div className="flex items-center gap-2 border rounded-lg p-0.5 bg-slate-50">
          <button onClick={() => setViewMode("card")}
            className={cn("p-2 rounded-md transition-all", viewMode === "card" ? "bg-white shadow-sm text-brand" : "text-slate-400 hover:text-slate-600")}>
            <LayoutGrid className="w-4 h-4" />
          </button>
          <button onClick={() => setViewMode("list")}
            className={cn("p-2 rounded-md transition-all", viewMode === "list" ? "bg-white shadow-sm text-brand" : "text-slate-400 hover:text-slate-600")}>
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters Row */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input placeholder="Search models, OEMs, SKU..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
        </div>

        {/* OEM Filter */}
        <select value={selectedOEM} onChange={e => setSelectedOEM(e.target.value)}
          className="h-9 px-3 pr-8 text-sm border rounded-xl bg-white text-slate-700 focus:border-brand focus:ring-2 focus:ring-brand/20 focus:outline-none cursor-pointer">
          <option value="">All Manufacturers</option>
          {oemList.map(oem => <option key={oem} value={oem}>{oem}</option>)}
        </select>

        {/* Type Filter */}
        <select value={selectedType} onChange={e => setSelectedType(e.target.value)}
          className="h-9 px-3 pr-8 text-sm border rounded-xl bg-white text-slate-700 focus:border-brand focus:ring-2 focus:ring-brand/20 focus:outline-none cursor-pointer">
          <option value="">All Types</option>
          {typeList.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        {/* Active filter badges */}
        {(selectedOEM || selectedType) && (
          <button onClick={() => { setSelectedOEM(""); setSelectedType("") }}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-brand transition-colors">
            <X className="w-3 h-3" /> Clear filters
          </button>
        )}

        <div className="ml-auto text-xs text-slate-400">{filtered.length} models</div>
      </div>

      {/* Content */}
      {filtered.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <FileBarChart className="h-12 w-12 mx-auto text-slate-200 mb-4" />
            <h3 className="text-lg font-semibold text-slate-600">No models found</h3>
            <p className="text-sm text-slate-400 mt-1">Try adjusting your filters</p>
          </CardContent>
        </Card>
      ) : viewMode === "card" ? (
        /* ── Card View ── */
        <div className="space-y-6 stagger-children">
          {Array.from(groupedByOEM.entries()).map(([oem, models]) => {
            const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", website: "#", logo: oem[0] }
            return (
              <div key={oem}>
                {/* OEM Header */}
                <div className="flex items-center gap-3 mb-3">
                  <div className={cn("w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center text-white text-sm font-bold shadow-sm", info.color)}>
                    {info.logo}
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-slate-800">{oem}</h2>
                    <span className="text-[10px] text-slate-400">{models.length} model{models.length !== 1 ? "s" : ""}</span>
                  </div>
                  <a href={info.website} target="_blank" rel="noopener noreferrer"
                    className="ml-2 text-slate-300 hover:text-brand transition-colors">
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                {/* Model Cards */}
                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                  {models.map(comp => (
                    <Card key={comp.id} className="card-interactive cursor-pointer group" onClick={() => handleSelect(comp)}>
                      <CardContent className="pt-4 pb-3">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-bold text-slate-800 truncate group-hover:text-brand transition-colors">{comp.model_name}</div>
                            <div className="text-[11px] text-slate-400 mt-0.5">{comp.sku} · {comp.component_type_name}</div>
                          </div>
                          <ScoreRing score={comp.compliance_score} size={48} strokeWidth={4} />
                        </div>
                        <div className="flex items-center gap-2 text-[10px]">
                          <span className="flex items-center gap-1 text-emerald-600 font-semibold"><CheckCircle2 className="h-3 w-3" />{comp.pass}P</span>
                          {comp.fail > 0 && <span className="flex items-center gap-1 text-red-500 font-semibold"><XCircle className="h-3 w-3" />{comp.fail}F</span>}
                          {comp.waived > 0 && <span className="flex items-center gap-1 text-amber-500 font-semibold"><AlertTriangle className="h-3 w-3" />{comp.waived}W</span>}
                          <div className="ml-auto flex items-center gap-1.5">
                            <span className="text-slate-400">Fill</span>
                            <Progress value={comp.fill_rate} className="h-1.5 w-12" />
                            <span className="text-slate-500 font-medium">{comp.fill_rate}%</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        /* ── List View ── */
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
                </tr>
              </thead>
              <tbody>
                {Array.from(groupedByOEM.entries()).map(([oem, models]) => {
                  const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", logo: oem[0] }
                  return models.map((comp, i) => (
                    <tr key={comp.id} onClick={() => handleSelect(comp)}
                      className="border-b border-slate-50 table-row-hover cursor-pointer group">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          {i === 0 && (
                            <div className={cn("w-6 h-6 rounded-md bg-gradient-to-br flex items-center justify-center text-white text-[10px] font-bold", info.color)}>
                              {info.logo}
                            </div>
                          )}
                          {i > 0 && <div className="w-6" />}
                          <span className="text-xs font-semibold text-slate-700">{comp.oem_name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-xs font-semibold text-slate-800 group-hover:text-brand transition-colors">{comp.model_name}</span>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-400 font-mono">{comp.sku}</td>
                      <td className="py-3 px-4"><Badge variant="default" className="text-[10px]">{comp.component_type_name}</Badge></td>
                      <td className="py-3 px-4 text-center"><span className={cn("text-xs font-bold", scoreColor(comp.compliance_score))}>{comp.compliance_score}%</span></td>
                      <td className="py-3 px-4 text-center"><span className="text-xs text-slate-500">{comp.fill_rate}%</span></td>
                      <td className="py-3 px-4 text-center text-xs text-emerald-600 font-semibold">{comp.pass}</td>
                      <td className="py-3 px-4 text-center text-xs text-red-500 font-semibold">{comp.fail}</td>
                      <td className="py-3 px-4 text-center text-xs text-amber-500 font-semibold">{comp.waived}</td>
                    </tr>
                  ))
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
