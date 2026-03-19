"use client"

import { useEffect, useState, useMemo } from "react"
import { getComponents, getComparisonMatrix } from "@/lib/api"
import { cn, scoreColor } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScoreRing } from "@/components/shared/score-ring"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts"
import {
  Loader2, GitCompareArrows, Check, Columns3, BarChart3,
  Building2, ExternalLink, Search, Filter, X, ChevronDown, ChevronRight,
} from "lucide-react"

/* ── Types ── */
interface Component {
  id: string; oem_id: string; oem_name: string; model_name: string; sku: string
  component_type_name: string; fill_rate: number; compliance_score: number
  is_active: boolean; pass: number; fail: number; waived: number
}
interface MatrixModel { id: string; model_name: string; oem_name: string; score: number }
interface MatrixRow {
  code: string; parameter: string; unit: string; section: string
  values: Record<string, { value: string | number; status: string; display: string }>
  benchmark?: { min: number; max: number; avg: number }
}
interface MatrixData { models: MatrixModel[]; rows: MatrixRow[]; total_parameters: number }

/* ── OEM Reference Data ── */
const OEM_INFO: Record<string, { color: string; website: string; country: string; logo: string }> = {
  "CATL":    { color: "from-blue-500 to-blue-600",    website: "https://catl.com",         country: "China", logo: "C" },
  "Lishen":  { color: "from-emerald-500 to-emerald-600", website: "https://lishen.com.cn", country: "China", logo: "L" },
  "BYD":     { color: "from-red-500 to-red-600",      website: "https://byd.com",           country: "China", logo: "B" },
  "HiTHIUM": { color: "from-purple-500 to-purple-600", website: "https://hithium.com",     country: "China", logo: "H" },
  "SVOLT":   { color: "from-amber-500 to-amber-600",  website: "https://www.svolt.cn/en",   country: "China", logo: "S" },
}

const BAR_COLORS = ["#3b82f6", "#f59e0b", "#10b981", "#8b5cf6", "#ef4444", "#06b6d4", "#ec4899", "#f97316"]

/* ── Page ── */
export default function ComparePage() {
  const [components, setComponents] = useState<Component[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState("")
  const [selectedOEMs, setSelectedOEMs] = useState<Set<string>>(new Set())
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [matrix, setMatrix] = useState<MatrixData | null>(null)
  const [comparing, setComparing] = useState(false)
  const [search, setSearch] = useState("")
  const [sectionFilter, setSectionFilter] = useState("All")
  const [expandedOEMs, setExpandedOEMs] = useState<Set<string>>(new Set())

  useEffect(() => {
    async function load() {
      try {
        const res = await getComponents()
        const items = res.items ?? []
        setComponents(items)
        const types = [...new Set(items.map((c: Component) => c.component_type_name).filter(Boolean))]
        if (types.length > 0) setSelectedType(types[0])
        // Expand all OEMs by default
        const oems = [...new Set(items.map((c: Component) => c.oem_name).filter(Boolean))]
        setExpandedOEMs(new Set(oems))
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  /* Derived data */
  const componentTypes = useMemo(() =>
    [...new Set(components.map(c => c.component_type_name).filter(Boolean))].sort(), [components])

  const oemList = useMemo(() => {
    const oems = [...new Set(components.filter(c => c.component_type_name === selectedType).map(c => c.oem_name).filter(Boolean))]
    return oems.sort()
  }, [components, selectedType])

  const filteredModels = useMemo(() => {
    let models = components.filter(c => c.component_type_name === selectedType && c.is_active)
    if (selectedOEMs.size > 0) models = models.filter(c => selectedOEMs.has(c.oem_name))
    if (search) {
      const q = search.toLowerCase()
      models = models.filter(c => c.model_name.toLowerCase().includes(q) || c.oem_name.toLowerCase().includes(q) || c.sku.toLowerCase().includes(q))
    }
    return models
  }, [components, selectedType, selectedOEMs, search])

  /* Group models by OEM */
  const modelsByOEM = useMemo(() => {
    const map = new Map<string, Component[]>()
    for (const m of filteredModels) {
      if (!map.has(m.oem_name)) map.set(m.oem_name, [])
      map.get(m.oem_name)!.push(m)
    }
    return map
  }, [filteredModels])

  function toggleOEM(oem: string) {
    setSelectedOEMs(prev => {
      const next = new Set(prev)
      if (next.has(oem)) next.delete(oem); else next.add(oem)
      return next
    })
  }

  function toggleExpandOEM(oem: string) {
    setExpandedOEMs(prev => {
      const next = new Set(prev)
      if (next.has(oem)) next.delete(oem); else next.add(oem)
      return next
    })
  }

  function toggleModel(id: string) {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  function selectAllFromOEM(oem: string) {
    const models = modelsByOEM.get(oem) || []
    setSelectedIds(prev => {
      const next = new Set(prev)
      const allSelected = models.every(m => next.has(m.id))
      if (allSelected) { models.forEach(m => next.delete(m.id)) }
      else { models.forEach(m => next.add(m.id)) }
      return next
    })
  }

  async function handleCompare() {
    if (selectedIds.size < 2) return
    setComparing(true)
    try {
      const result = await getComparisonMatrix(Array.from(selectedIds))
      setMatrix(result)
    } catch (e) { console.error(e) }
    finally { setComparing(false) }
  }

  /* Matrix grouping */
  const groupedRows = useMemo(() => {
    if (!matrix) return new Map<string, MatrixRow[]>()
    const map = new Map<string, MatrixRow[]>()
    for (const row of matrix.rows) {
      if (sectionFilter !== "All" && row.section !== sectionFilter) continue
      const section = row.section || "General"
      if (!map.has(section)) map.set(section, [])
      map.get(section)!.push(row)
    }
    return map
  }, [matrix, sectionFilter])

  const allSections = useMemo(() => {
    if (!matrix) return []
    return ["All", ...new Set(matrix.rows.map(r => r.section).filter(Boolean))]
  }, [matrix])

  function cellColor(row: MatrixRow, modelId: string) {
    const val = row.values[modelId]
    if (!val) return ""
    if (val.status === "pass") return "bg-emerald-50 text-emerald-700"
    if (val.status === "fail") return "bg-red-50 text-red-700"
    if (row.benchmark && typeof val.value === "number") {
      if (val.value >= row.benchmark.max) return "bg-emerald-50 text-emerald-700 font-bold"
      if (val.value <= row.benchmark.min) return "bg-red-50 text-red-700"
    }
    return ""
  }

  const scoreChartData = useMemo(() => {
    if (!matrix) return []
    return matrix.models.map((m, idx) => ({
      name: m.oem_name + "\n" + m.model_name.split("-").slice(-1)[0],
      fullName: m.model_name,
      oem: m.oem_name,
      score: m.score,
      fill: BAR_COLORS[idx % BAR_COLORS.length],
    }))
  }, [matrix])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Model Comparison</h1>
        <p className="text-sm text-slate-500 mt-1">Compare BESS components side-by-side — filter by manufacturer, type, and product</p>
      </div>

      <div className="flex gap-6">
        {/* ── Left Panel: Filters ── */}
        <div className="w-[340px] shrink-0 space-y-4">

          {/* Component Type */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <Columns3 className="h-3.5 w-3.5" /> Component Type
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {componentTypes.map(type => (
                  <Button key={type} variant={selectedType === type ? "default" : "outline"} size="sm" className="text-xs"
                    onClick={() => { setSelectedType(type); setSelectedIds(new Set()); setMatrix(null); setSelectedOEMs(new Set()) }}>
                    {type}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input placeholder="Search models, OEMs..." value={search} onChange={e => setSearch(e.target.value)}
              className="pl-10" />
          </div>

          {/* OEM Manufacturer Filter */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <Building2 className="h-3.5 w-3.5" /> Filter by Manufacturer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {oemList.map(oem => {
                const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", website: "#", country: "—", logo: oem[0] }
                const isFiltered = selectedOEMs.size === 0 || selectedOEMs.has(oem)
                return (
                  <button key={oem} onClick={() => toggleOEM(oem)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2 rounded-lg border transition-all text-left text-sm",
                      isFiltered && selectedOEMs.size > 0 ? "border-brand/30 bg-brand-50/50" : "border-transparent hover:bg-slate-50"
                    )}>
                    <div className={cn("w-7 h-7 rounded-lg bg-gradient-to-br flex items-center justify-center text-white text-xs font-bold flex-shrink-0", info.color)}>
                      {info.logo}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-slate-800 text-xs">{oem}</div>
                      <div className="text-[10px] text-slate-400">{info.country}</div>
                    </div>
                    {selectedOEMs.has(oem) && <Check className="w-4 h-4 text-brand flex-shrink-0" />}
                  </button>
                )
              })}
              {selectedOEMs.size > 0 && (
                <button onClick={() => setSelectedOEMs(new Set())}
                  className="w-full text-xs text-slate-400 hover:text-brand py-1.5 flex items-center justify-center gap-1 transition-colors">
                  <X className="w-3 h-3" /> Clear filter
                </button>
              )}
            </CardContent>
          </Card>

          {/* Models grouped by OEM */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase tracking-wider text-slate-500">
                Select Models to Compare
              </CardTitle>
              <CardDescription className="text-[11px]">{selectedIds.size} selected — need 2+ to compare</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin">
              {Array.from(modelsByOEM.entries()).map(([oem, models]) => {
                const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", website: "#", country: "—", logo: oem[0] }
                const isExpanded = expandedOEMs.has(oem)
                const allSelected = models.every(m => selectedIds.has(m.id))
                const someSelected = models.some(m => selectedIds.has(m.id))
                return (
                  <div key={oem} className="border border-slate-100 rounded-xl overflow-hidden">
                    {/* OEM Header */}
                    <div className="flex items-center gap-2 px-3 py-2.5 bg-slate-50/80 cursor-pointer hover:bg-slate-100/80 transition-colors"
                      onClick={() => toggleExpandOEM(oem)}>
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-slate-400" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-400" />}
                      <div className={cn("w-6 h-6 rounded-md bg-gradient-to-br flex items-center justify-center text-white text-[10px] font-bold", info.color)}>
                        {info.logo}
                      </div>
                      <span className="text-xs font-bold text-slate-700 flex-1">{oem}</span>
                      <button onClick={e => { e.stopPropagation(); selectAllFromOEM(oem) }}
                        className={cn("text-[10px] font-semibold px-2 py-0.5 rounded-md transition-colors",
                          allSelected ? "bg-brand/10 text-brand" : "bg-slate-100 text-slate-400 hover:text-slate-600")}>
                        {allSelected ? "Deselect" : "Select All"}
                      </button>
                      <a href={info.website} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
                        className="text-slate-300 hover:text-brand transition-colors">
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    {/* Models */}
                    {isExpanded && (
                      <div className="divide-y divide-slate-50">
                        {models.map(model => {
                          const isSelected = selectedIds.has(model.id)
                          return (
                            <button key={model.id} onClick={() => toggleModel(model.id)}
                              className={cn("w-full flex items-center gap-3 px-3 py-2.5 text-left transition-all",
                                isSelected ? "bg-brand-50/50" : "hover:bg-slate-50")}>
                              <div className={cn("w-4 h-4 rounded border flex items-center justify-center flex-shrink-0",
                                isSelected ? "bg-brand border-brand text-white" : "border-slate-300")}>
                                {isSelected && <Check className="h-2.5 w-2.5" />}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="text-xs font-semibold text-slate-700 truncate">{model.model_name}</div>
                                <div className="text-[10px] text-slate-400">{model.sku} · {model.component_type_name}</div>
                              </div>
                              <div className="text-right flex-shrink-0">
                                <div className={cn("text-xs font-bold", scoreColor(model.compliance_score))}>{model.compliance_score}%</div>
                                <div className="flex gap-1 mt-0.5">
                                  <span className="text-[9px] text-emerald-500 font-semibold">{model.pass}P</span>
                                  {model.fail > 0 && <span className="text-[9px] text-red-500 font-semibold">{model.fail}F</span>}
                                </div>
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}
            </CardContent>
          </Card>

          {/* Compare Button */}
          <Button className="w-full" size="lg" disabled={selectedIds.size < 2 || comparing} onClick={handleCompare}>
            {comparing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <GitCompareArrows className="h-4 w-4 mr-2" />}
            Compare {selectedIds.size} Models
          </Button>
        </div>

        {/* ── Right Panel: Results ── */}
        <div className="flex-1 space-y-6 min-w-0">
          {!matrix ? (
            <Card>
              <CardContent className="py-20">
                <div className="text-center">
                  <GitCompareArrows className="h-12 w-12 mx-auto text-slate-200 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-600">Select Models to Compare</h3>
                  <p className="text-sm text-slate-400 mt-1 max-w-sm mx-auto">
                    Choose 2+ models from the left panel and click Compare to see the full parameter matrix
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Model Summary Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                {matrix.models.map((m, idx) => {
                  const info = OEM_INFO[m.oem_name] || { color: "from-slate-500 to-slate-600", website: "#", logo: m.oem_name[0] }
                  return (
                    <Card key={m.id} className="card-interactive">
                      <CardContent className="pt-4 pb-3">
                        <div className="flex items-center gap-3">
                          <div className={cn("w-9 h-9 rounded-lg bg-gradient-to-br flex items-center justify-center text-white text-sm font-bold shadow-sm", info.color)}>
                            {info.logo}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-bold text-slate-800 truncate">{m.model_name}</div>
                            <div className="text-[10px] text-slate-400">{m.oem_name}</div>
                          </div>
                          <ScoreRing score={m.score} size={44} strokeWidth={4} />
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>

              {/* Score Chart */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-slate-400" /> Compliance Score Comparison
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={scoreChartData} margin={{ top: 10, right: 20, bottom: 5, left: 20 }}>
                      <XAxis dataKey="oem" tick={{ fontSize: 11 }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                      <Tooltip content={({ active, payload }) => {
                        if (!active || !payload?.[0]) return null
                        const d = payload[0].payload
                        return (
                          <div className="bg-white border rounded-lg shadow-lg p-3 text-xs">
                            <div className="font-bold text-slate-800">{d.fullName}</div>
                            <div className="text-slate-500">{d.oem}</div>
                            <div className={cn("text-lg font-bold mt-1", scoreColor(d.score))}>{d.score}%</div>
                          </div>
                        )
                      }} />
                      <Bar dataKey="score" radius={[6, 6, 0, 0]} barSize={40}>
                        {scoreChartData.map((entry, idx) => <Cell key={idx} fill={entry.fill} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Section Filter */}
              {allSections.length > 2 && (
                <div className="flex items-center gap-2 flex-wrap">
                  <Filter className="w-3.5 h-3.5 text-slate-400" />
                  {allSections.map(s => (
                    <button key={s} onClick={() => setSectionFilter(s)}
                      className={cn("text-xs font-medium px-3 py-1.5 rounded-lg border transition-all",
                        sectionFilter === s ? "bg-brand text-white border-brand" : "bg-white text-slate-600 border-slate-200 hover:border-brand/30")}>
                      {s}
                    </button>
                  ))}
                </div>
              )}

              {/* Comparison Matrix */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Parameter Matrix</CardTitle>
                  <CardDescription className="text-xs">
                    {matrix.total_parameters} parameters · {matrix.models.length} models
                    {sectionFilter !== "All" && ` · Filtered: ${sectionFilter}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto rounded-lg border">
                    <table className="w-full text-sm border-collapse">
                      <thead className="sticky top-0 z-10">
                        <tr className="bg-slate-50 border-b-2 border-slate-200">
                          <th className="text-left py-3 px-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider min-w-[200px]">
                            Parameter
                          </th>
                          {matrix.models.map(model => {
                            const info = OEM_INFO[model.oem_name] || { color: "from-slate-500 to-slate-600", logo: model.oem_name[0] }
                            return (
                              <th key={model.id} className="text-center py-3 px-3 min-w-[130px]">
                                <div className="flex items-center justify-center gap-1.5">
                                  <div className={cn("w-5 h-5 rounded bg-gradient-to-br flex items-center justify-center text-white text-[9px] font-bold", info.color)}>
                                    {info.logo}
                                  </div>
                                  <div>
                                    <div className="text-[10px] font-bold text-slate-800">{model.oem_name}</div>
                                    <div className="text-[9px] text-slate-400 font-normal">{model.model_name.split("-").slice(-2).join("-")}</div>
                                  </div>
                                </div>
                              </th>
                            )
                          })}
                        </tr>
                      </thead>
                      <tbody>
                        {Array.from(groupedRows.entries()).map(([section, rows]) => (
                          <>
                            <tr key={`s-${section}`}>
                              <td colSpan={matrix.models.length + 1}
                                className="py-2 px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 bg-slate-50/80 border-y border-slate-100">
                                {section}
                              </td>
                            </tr>
                            {rows.map(row => (
                              <tr key={row.code} className="border-b border-slate-50 table-row-hover">
                                <td className="py-2 px-3 text-slate-700">
                                  <div className="text-xs font-medium">{row.parameter}</div>
                                  {row.unit && <span className="text-[9px] text-slate-400">({row.unit})</span>}
                                </td>
                                {matrix.models.map(model => {
                                  const val = row.values[model.id]
                                  return (
                                    <td key={model.id} className={cn("py-2 px-3 text-center text-xs font-medium transition-colors", cellColor(row, model.id))}>
                                      {val ? val.display : "—"}
                                    </td>
                                  )
                                })}
                              </tr>
                            ))}
                          </>
                        ))}
                        {/* Score row */}
                        <tr className="border-t-2 border-slate-200 bg-slate-50">
                          <td className="py-3 px-3 text-xs font-bold text-slate-900">Compliance Score</td>
                          {matrix.models.map(model => (
                            <td key={model.id} className="py-3 px-3 text-center">
                              <span className={cn("text-base font-bold", scoreColor(model.score))}>{model.score}%</span>
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
