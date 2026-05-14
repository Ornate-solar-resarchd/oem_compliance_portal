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
  Plus, Sparkles,
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

  /* Dedupe models (by id) and rows (by code) — backend occasionally returns dupes */
  const dedupedModels = useMemo(() => {
    if (!matrix) return [] as MatrixModel[]
    const seen = new Set<string>()
    return matrix.models.filter(m => {
      if (seen.has(m.id)) return false
      seen.add(m.id); return true
    })
  }, [matrix])

  /* Merge rows sharing the same code — keeps the shortest/cleanest parameter
     name and combines `values` so each model contributes once. */
  const dedupedRows = useMemo(() => {
    if (!matrix) return [] as MatrixRow[]
    const byKey = new Map<string, MatrixRow>()
    for (const r of matrix.rows) {
      const key = r.code || `${r.section}::${r.parameter}`
      const existing = byKey.get(key)
      if (!existing) {
        byKey.set(key, { ...r, values: { ...r.values } })
        continue
      }
      // merge values; prefer non-empty
      for (const [mid, v] of Object.entries(r.values)) {
        if (!existing.values[mid] || !existing.values[mid].display) existing.values[mid] = v
      }
      // prefer shorter, less-parenthesised name
      const cleaner = (s: string) => !s.includes("(") && s.length < (existing.parameter || "").length
      if (r.parameter && cleaner(r.parameter)) existing.parameter = r.parameter
    }
    return Array.from(byKey.values())
  }, [matrix])

  /* CarDekho-style: show-only-differences toggle + section accordions */
  const [showOnlyDiff, setShowOnlyDiff] = useState(false)
  const [openSections, setOpenSections] = useState<Set<string>>(new Set())

  function rowHasDifference(row: MatrixRow): boolean {
    const values = dedupedModels.map(m => row.values[m.id]?.display ?? "")
    const first = values[0]
    return values.some(v => v !== first)
  }

  /* ── Best-value highlighting (green) ──
     higher: cycle life, energy density
     lower: AC impedance, internal resistance
     wider: charge / discharge / storage temperature ranges */
  type BestDir = "higher" | "lower" | "wider"
  function bestDirection(code: string): BestDir | null {
    if (/CYCLE_LIFE|ENERGY_DENSITY/.test(code)) return "higher"
    if (/AC_IMPEDANCE/.test(code)) return "lower"
    if (/_TEMP$|CHG_TEMP|DIS_TEMP|STORAGE_TEMP|CHARGE_TEMP|DISCHARGE_TEMP/.test(code)) {
      // Skip the individual MIN/MAX rows — we want wider only when both ends are in one cell
      if (/_MIN$|_MAX$/.test(code)) return null
      return "wider"
    }
    return null
  }

  function parseNum(s: string): number | null {
    if (!s) return null
    const m = String(s).replace(/,/g, "").match(/-?\d+\.?\d*/)
    return m ? parseFloat(m[0]) : null
  }
  function parseRangeWidth(s: string): number | null {
    if (!s) return null
    const nums = String(s).match(/-?\d+\.?\d*/g)
    if (!nums || nums.length < 2) return null
    return Math.abs(parseFloat(nums[1]) - parseFloat(nums[0]))
  }

  function bestModelIds(row: MatrixRow): Set<string> {
    const dir = bestDirection(row.code)
    if (!dir) return new Set()
    const scored: [string, number][] = []
    for (const m of dedupedModels) {
      const display = row.values[m.id]?.display
      if (!display) continue
      const n = dir === "wider" ? parseRangeWidth(String(display)) : parseNum(String(display))
      if (n == null || isNaN(n)) continue
      scored.push([m.id, n])
    }
    if (scored.length < 2) return new Set()
    const nums = scored.map(s => s[1])
    const target = dir === "lower" ? Math.min(...nums) : Math.max(...nums)
    // Avoid highlighting all when every model ties
    if (nums.every(n => n === target)) return new Set()
    return new Set(scored.filter(s => s[1] === target).map(s => s[0]))
  }

  /* Matrix grouping */
  const groupedRows = useMemo(() => {
    if (!matrix) return new Map<string, MatrixRow[]>()
    const map = new Map<string, MatrixRow[]>()
    for (const row of dedupedRows) {
      if (sectionFilter !== "All" && row.section !== sectionFilter) continue
      if (showOnlyDiff && !rowHasDifference(row)) continue
      const section = row.section || "General"
      if (!map.has(section)) map.set(section, [])
      map.get(section)!.push(row)
    }
    return map
  }, [matrix, dedupedRows, sectionFilter, showOnlyDiff, dedupedModels])

  /* When a new matrix arrives, open all sections by default */
  useEffect(() => {
    if (!matrix) return
    const sections = new Set<string>(matrix.rows.map(r => r.section || "General"))
    setOpenSections(sections)
  }, [matrix])

  function toggleSection(s: string) {
    setOpenSections(prev => {
      const next = new Set(prev)
      if (next.has(s)) next.delete(s); else next.add(s)
      return next
    })
  }

  function removeModel(id: string) {
    setSelectedIds(prev => {
      const next = new Set(prev); next.delete(id); return next
    })
    if (matrix) {
      const remaining = matrix.models.filter(m => m.id !== id)
      if (remaining.length < 2) { setMatrix(null); return }
      setMatrix({
        ...matrix,
        models: remaining,
        rows: matrix.rows.map(r => {
          const v = { ...r.values }; delete v[id]; return { ...r, values: v }
        }),
      })
    }
  }

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

  /* ── Highlighted key specs (CarDekho-style hero metrics) ── */
  const KEY_SPECS: { codes: string[]; label: string; unit: string; icon: string }[] = [
    { codes: ["CELL_CAPACITY_AH", "CELL_NOM_CAPACITY", "CELL_NOMINAL_CAPACITY"],     label: "Nominal Capacity", unit: "Ah",     icon: "⚡" },
    { codes: ["CELL_ENERGY_WH", "CELL_NOM_ENERGY", "CELL_NOMINAL_ENERGY"],           label: "Nominal Energy",   unit: "Wh",     icon: "🔌" },
    { codes: ["CELL_ENERGY_DENSITY", "CELL_ENERGY_DENSITY_WH_KG"],                   label: "Energy Density",   unit: "Wh/kg",  icon: "🔋" },
    { codes: ["CELL_CYCLE_LIFE"],                                                    label: "Cycle Life",       unit: "cycles", icon: "♻️" },
  ]
  /* Flat list of all key codes — used to detect "is highlighted" inside the table */
  const KEY_CODES = new Set(KEY_SPECS.flatMap(s => s.codes))

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto">
      {/* ── Header ── */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Model Comparison</h1>
          <p className="text-sm text-slate-500 mt-1">Side-by-side specifications across BESS cells and manufacturers</p>
        </div>
        {selectedType && (
          <Badge variant="default" className="text-xs px-3 py-1.5">
            <Columns3 className="h-3 w-3 mr-1.5" /> {selectedType}
          </Badge>
        )}
      </div>

      {/* ── Top Selector Strip ── */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="pb-3 border-b border-slate-100">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <CardTitle className="text-base font-semibold text-slate-800 flex items-center gap-2">
                <GitCompareArrows className="h-4 w-4 text-brand" />
                Select Models to Compare
              </CardTitle>
              <CardDescription className="text-xs text-slate-500 mt-0.5">
                {selectedIds.size === 0 ? "Pick 2 or more models below" :
                  selectedIds.size === 1 ? "1 selected · pick at least 1 more" :
                  `${selectedIds.size} selected · ready to compare`}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {selectedIds.size > 0 && (
                <Button size="sm" variant="ghost" className="text-xs h-8" onClick={() => setSelectedIds(new Set())}>
                  <X className="h-3.5 w-3.5 mr-1" /> Clear
                </Button>
              )}
              <Button size="sm" className="h-8 px-4" disabled={selectedIds.size < 2 || comparing} onClick={handleCompare}>
                {comparing ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" /> : <GitCompareArrows className="h-3.5 w-3.5 mr-1.5" />}
                Compare {selectedIds.size > 0 ? `(${selectedIds.size})` : ""}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-4 space-y-3">
          {/* Component types + search on a single row */}
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1.5 flex-wrap">
              {componentTypes.map(type => (
                <button key={type}
                  onClick={() => { setSelectedType(type); setSelectedIds(new Set()); setMatrix(null); setSelectedOEMs(new Set()) }}
                  className={cn("text-xs font-medium px-3 py-1.5 rounded-md border transition-all",
                    selectedType === type ? "bg-brand text-white border-brand" : "bg-white text-slate-600 border-slate-200 hover:border-brand/40")}>
                  {type}
                </button>
              ))}
            </div>
            <div className="relative flex-1 min-w-[220px] max-w-[320px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
              <Input placeholder="Search models or OEMs..." value={search} onChange={e => setSearch(e.target.value)}
                className="pl-9 h-9 text-sm" />
            </div>
          </div>

          {/* Horizontal OEM strip */}
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin -mx-1 px-1">
            {Array.from(modelsByOEM.entries()).map(([oem, models]) => {
              const info = OEM_INFO[oem] || { color: "from-slate-500 to-slate-600", website: "#", country: "—", logo: oem[0] }
              const allSelected = models.every(m => selectedIds.has(m.id))
              const someSelected = models.some(m => selectedIds.has(m.id))
              return (
                <div key={oem} className={cn(
                  "flex-shrink-0 w-[240px] border rounded-xl overflow-hidden bg-white transition-all",
                  someSelected ? "border-brand shadow-sm ring-1 ring-brand/20" : "border-slate-200 hover:border-slate-300"
                )}>
                  <div className="flex items-center gap-2.5 px-3 py-2.5 bg-gradient-to-r from-slate-50/80 to-white border-b border-slate-100">
                    <div className={cn("w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center text-white text-sm font-bold shadow-sm flex-shrink-0", info.color)}>
                      {info.logo}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-bold text-slate-800 truncate">{oem}</div>
                      <div className="text-[10px] text-slate-400">{models.length} model{models.length !== 1 ? "s" : ""}</div>
                    </div>
                    <button onClick={() => selectAllFromOEM(oem)}
                      className={cn("text-[10px] font-semibold px-2 py-1 rounded-md transition-colors flex-shrink-0",
                        allSelected ? "bg-brand text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200")}>
                      {allSelected ? "Clear" : "All"}
                    </button>
                  </div>
                  <div className="max-h-[220px] overflow-y-auto">
                    {models.map(model => {
                      const isSelected = selectedIds.has(model.id)
                      return (
                        <button key={model.id} onClick={() => toggleModel(model.id)}
                          className={cn("w-full flex items-center gap-2.5 px-3 py-2 text-left transition-all border-b border-slate-50 last:border-0",
                            isSelected ? "bg-brand/5 border-l-2 border-l-brand" : "hover:bg-slate-50")}>
                          <div className={cn("w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0",
                            isSelected ? "bg-brand border-brand text-white" : "border-slate-300")}>
                            {isSelected && <Check className="h-2.5 w-2.5" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-semibold text-slate-800 truncate">{model.model_name}</div>
                            <div className="text-[10px] text-slate-400 truncate">{model.sku}</div>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })}
            {modelsByOEM.size === 0 && (
              <div className="flex-1 text-center text-xs text-slate-400 py-8">No models match your filters.</div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* ── Results ── */}
      <div className="space-y-6">
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
              {/* ── CarDekho-style Comparison Table ── */}
              <Card className="overflow-hidden">
                <CardHeader className="pb-3 flex flex-row items-start justify-between gap-4 flex-wrap">
                  <div>
                    <CardTitle className="text-base font-semibold flex items-center gap-2">
                      <GitCompareArrows className="h-4 w-4 text-brand" />
                      Specification Comparison
                    </CardTitle>
                    <CardDescription className="text-xs text-slate-500">
                      {matrix.total_parameters} parameters · {dedupedModels.length} models
                      {sectionFilter !== "All" && ` · Filtered: ${sectionFilter}`}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {allSections.length > 2 && allSections.map(s => (
                      <button key={s} onClick={() => setSectionFilter(s)}
                        className={cn("text-xs font-medium px-2.5 py-1 rounded-md border transition-all",
                          sectionFilter === s ? "bg-brand text-white border-brand" : "bg-white text-slate-600 border-slate-200 hover:border-brand/30")}>
                        {s}
                      </button>
                    ))}
                    <button onClick={() => setShowOnlyDiff(v => !v)}
                      className={cn("text-xs font-medium px-2.5 py-1 rounded-md border transition-all flex items-center gap-1.5",
                        showOnlyDiff ? "bg-amber-500 text-white border-amber-500" : "bg-white text-slate-600 border-slate-200 hover:border-amber-400")}>
                      <Sparkles className="h-3 w-3" />
                      {showOnlyDiff ? "Showing differences" : "Show only differences"}
                    </button>
                  </div>
                </CardHeader>

                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                      {/* Sticky model header — like CarDekho's car cards row */}
                      <thead className="sticky top-0 z-20 bg-white">
                        <tr className="border-b-2 border-slate-200">
                          <th className="text-left py-3 px-4 bg-white min-w-[200px] sticky left-0 z-20 border-r border-slate-200">
                            <div className="text-[10px] uppercase tracking-[0.08em] text-slate-400 font-semibold">Specification</div>
                          </th>
                          {dedupedModels.map(model => {
                            const info = OEM_INFO[model.oem_name] || { color: "from-slate-500 to-slate-600", logo: model.oem_name[0] }
                            return (
                              <th key={model.id} className="py-3 px-2 min-w-[160px] align-top bg-white border-l border-slate-100">
                                <div className="relative flex flex-col items-center gap-1.5">
                                  <button onClick={() => removeModel(model.id)}
                                    className="absolute -top-0.5 right-0 w-5 h-5 rounded-full bg-slate-100 hover:bg-red-100 hover:text-red-600 text-slate-400 flex items-center justify-center transition-colors"
                                    title="Remove from comparison">
                                    <X className="h-3 w-3" />
                                  </button>
                                  <div className={cn("w-11 h-11 rounded-xl bg-gradient-to-br flex items-center justify-center text-white text-base font-bold shadow-sm", info.color)}>
                                    {info.logo}
                                  </div>
                                  <div className="text-center">
                                    <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">{model.oem_name}</div>
                                    <div className="text-xs font-semibold text-slate-800 leading-tight mt-0.5">{model.model_name}</div>
                                  </div>
                                </div>
                              </th>
                            )
                          })}
                        </tr>
                      </thead>

                      <tbody>
                        {Array.from(groupedRows.entries()).map(([section, rows]) => {
                          const isOpen = openSections.has(section)
                          return (
                            <>
                              <tr key={`s-${section}`}>
                                <td colSpan={dedupedModels.length + 1} className="p-0 bg-slate-50 border-y border-slate-200">
                                  <button onClick={() => toggleSection(section)}
                                    className="sticky left-0 flex items-center gap-2 py-2.5 px-4 text-left transition-colors hover:bg-slate-100">
                                    {isOpen ? <ChevronDown className="h-3 w-3 text-slate-400" /> : <ChevronRight className="h-3 w-3 text-slate-400" />}
                                    <span className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-600">{section}</span>
                                    <span className="text-[10px] text-slate-400 font-normal ml-0.5">· {rows.length}</span>
                                  </button>
                                </td>
                              </tr>
                              {isOpen && rows.map((row, idx) => {
                                const bestIds = bestModelIds(row)
                                const zebra = idx % 2 === 1
                                return (
                                  <tr key={row.code} className={cn("group transition-colors hover:!bg-blue-50/30", zebra && "bg-slate-50/40")}>
                                    <td className={cn(
                                      "py-2.5 px-4 sticky left-0 z-10 border-r border-slate-100 group-hover:bg-blue-50/30",
                                      zebra ? "bg-slate-50" : "bg-white"
                                    )}>
                                      <div className="text-[13px] text-slate-700 leading-snug">
                                        {row.parameter}
                                        {row.unit && <span className="text-[11px] text-slate-400 ml-1">· {row.unit}</span>}
                                      </div>
                                    </td>
                                    {dedupedModels.map(model => {
                                      const val = row.values[model.id]
                                      const display = val ? val.display : null
                                      const isBest = bestIds.has(model.id)
                                      return (
                                        <td key={model.id} className={cn(
                                          "py-2.5 px-3 text-center border-l border-slate-100 tabular-nums relative text-[13px]",
                                          isBest ? "bg-emerald-50 text-emerald-700 font-semibold" : "text-slate-700"
                                        )}>
                                          {isBest && <span className="absolute top-1 right-1.5 text-[8px] font-bold text-emerald-500">★</span>}
                                          {display ?? <span className="text-slate-300">—</span>}
                                        </td>
                                      )
                                    })}
                                  </tr>
                                )
                              })}
                            </>
                          )
                        })}
                        {groupedRows.size === 0 && (
                          <tr>
                            <td colSpan={dedupedModels.length + 1} className="py-10 text-center text-slate-400 text-sm">
                              {showOnlyDiff ? "All values match across the selected models." : "No parameters to display."}
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
    </div>
  )
}
