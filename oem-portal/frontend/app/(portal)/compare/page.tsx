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
        const types = Array.from(new Set(items.map((c: Component) => c.component_type_name).filter(Boolean))) as string[]
        if (types.length > 0) setSelectedType(types[0])
        // Expand all OEMs by default
        const oems = Array.from(new Set(items.map((c: Component) => c.oem_name).filter(Boolean))) as string[]
        setExpandedOEMs(new Set(oems))
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  /* Derived data */
  const componentTypes = useMemo(() =>
    (Array.from(new Set(components.map(c => c.component_type_name).filter(Boolean))) as string[]).sort(), [components])

  const oemList = useMemo(() => {
    const oems = Array.from(new Set(components.filter(c => c.component_type_name === selectedType).map(c => c.oem_name).filter(Boolean))) as string[]
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

  // No score/benchmark coloring — plain cells per user request
  function cellColor(_row: MatrixRow, _modelId: string) { return "" }

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
        <p className="text-sm text-slate-500 mt-1">Side-by-side specification comparison across BESS models and manufacturers</p>
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

          {/* Models grouped by OEM — horizontal strip */}
          <Card>
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold text-slate-700">Select Models</CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  {selectedIds.size > 0 ? `${selectedIds.size} selected · scroll horizontally to see all OEMs` : "Click any model to add it to the comparison"}
                </CardDescription>
              </div>
              {selectedIds.size > 0 && (
                <Button size="sm" variant="outline" onClick={() => setSelectedIds(new Set())} className="text-xs">
                  <X className="h-3 w-3 mr-1" /> Clear all
                </Button>
              )}
            </CardHeader>
            <CardContent>
              <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
                {Array.from(modelsByOEM.entries()).map(([oem, models]) => {
                  const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", website: "#", country: "—", logo: oem[0] }
                  const allSelected = models.every(m => selectedIds.has(m.id))
                  return (
                    <div key={oem} className="flex-shrink-0 w-[210px] border border-slate-200 rounded-xl overflow-hidden bg-white">
                      <div className="flex items-center gap-2 px-3 py-2.5 bg-slate-50 border-b border-slate-100">
                        <div className={cn("w-6 h-6 rounded bg-gradient-to-br flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0", info.color)}>
                          {info.logo}
                        </div>
                        <span className="text-xs font-semibold text-slate-800 flex-1 truncate">{oem}</span>
                        <button onClick={() => selectAllFromOEM(oem)}
                          className={cn("text-[10px] font-medium px-1.5 py-0.5 rounded transition-colors flex-shrink-0",
                            allSelected ? "bg-brand/10 text-brand" : "text-slate-500 hover:bg-slate-200")}>
                          {allSelected ? "Clear" : "All"}
                        </button>
                      </div>
                      <div className="max-h-[260px] overflow-y-auto">
                        {models.map(model => {
                          const isSelected = selectedIds.has(model.id)
                          return (
                            <button key={model.id} onClick={() => toggleModel(model.id)}
                              className={cn("w-full flex items-center gap-2 px-3 py-2 text-left transition-all border-b border-slate-50 last:border-0",
                                isSelected ? "bg-brand-50/40" : "hover:bg-slate-50")}>
                              <div className={cn("w-3.5 h-3.5 rounded border-2 flex items-center justify-center flex-shrink-0",
                                isSelected ? "bg-brand border-brand text-white" : "border-slate-300")}>
                                {isSelected && <Check className="h-2 w-2" />}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="text-xs font-medium text-slate-800 truncate">{model.model_name}</div>
                                <div className="text-[10px] text-slate-400 truncate">{model.sku}</div>
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
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
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                {matrix.models.map((m) => {
                  const info = OEM_INFO[m.oem_name] || { color: "from-slate-500 to-slate-600", website: "#", logo: m.oem_name[0] }
                  return (
                    <Card key={m.id} className="card-interactive">
                      <CardContent className="py-4">
                        <div className="flex items-center gap-3">
                          <div className={cn("w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center text-white text-base font-bold shadow-sm flex-shrink-0", info.color)}>
                            {info.logo}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-slate-800 truncate">{m.model_name}</div>
                            <div className="text-xs text-slate-500">{m.oem_name}</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>

              {/* Model summary cards kept, score chart removed */}
              <Card className="hidden">
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

              {/* Comparison Matrix — Original vertical layout (params as rows, models as columns) */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-semibold">Specification Comparison</CardTitle>
                  <CardDescription className="text-xs text-slate-500">
                    {matrix.total_parameters} parameters · {matrix.models.length} models
                    {sectionFilter !== "All" && ` · Filtered: ${sectionFilter}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto rounded-xl border border-slate-200">
                    <table className="w-full text-sm border-collapse">
                      <thead className="sticky top-0 z-10">
                        <tr className="bg-slate-50 border-b border-slate-200">
                          <th className="text-left py-4 px-4 text-xs font-semibold text-slate-600 uppercase tracking-wide min-w-[220px]">
                            Parameter
                          </th>
                          {matrix.models.map(model => {
                            const info = OEM_INFO[model.oem_name] || { color: "from-slate-500 to-slate-600", logo: model.oem_name[0] }
                            return (
                              <th key={model.id} className="text-center py-4 px-4 min-w-[150px]">
                                <div className="flex items-center justify-center gap-2">
                                  <div className={cn("w-6 h-6 rounded bg-gradient-to-br flex items-center justify-center text-white text-xs font-bold", info.color)}>
                                    {info.logo}
                                  </div>
                                  <div className="text-left">
                                    <div className="text-xs font-semibold text-slate-800">{model.oem_name}</div>
                                    <div className="text-[11px] text-slate-500 font-normal">{model.model_name.split("-").slice(-2).join("-")}</div>
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
                                className="py-3 px-4 text-xs font-semibold uppercase tracking-wide text-slate-700 bg-slate-100/70 border-t border-b border-slate-200">
                                {section}
                              </td>
                            </tr>
                            {rows.map(row => (
                              <tr key={row.code} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                                <td className="py-3 px-4 text-slate-700">
                                  <div className="text-sm font-medium">{row.parameter}</div>
                                  {row.unit && <span className="text-xs text-slate-400">{row.unit}</span>}
                                </td>
                                {matrix.models.map(model => {
                                  const val = row.values[model.id]
                                  return (
                                    <td key={model.id} className="py-3 px-4 text-center text-sm text-slate-800">
                                      {val ? val.display : <span className="text-slate-300">—</span>}
                                    </td>
                                  )
                                })}
                              </tr>
                            ))}
                          </>
                        ))}
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
