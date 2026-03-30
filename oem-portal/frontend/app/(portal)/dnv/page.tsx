"use client"

import { useState, useEffect, useMemo, useRef } from "react"
import { getDNVReports, getDNVPrimer, uploadDNVReport } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import {
  Shield, Search, Upload, Loader2, CheckCircle2, XCircle, ChevronDown, ChevronRight,
  Thermometer, Battery, Zap, Building2, Award, FileUp, X, ExternalLink,
} from "lucide-react"

interface DNVReport {
  id: string; name: string; fullName: string; type: string; model: string
  capacity_kwh: number | null; power_kw: number | null; summary: string
  cell: any; perf: any; pcs: any; thermal: any; safety: any; bms: any; phys: any; company: any; dnv: any
  source_file?: string
}

const DNV_COLORS: Record<string, string> = {
  "4": "bg-emerald-500", "3": "bg-amber-500", "2": "bg-orange-500", "1": "bg-red-500",
}

function DnvBadge({ label, value }: { label: string; value: string | null }) {
  if (!value) return <div className="text-center"><div className="text-[9px] text-slate-400 uppercase">{label}</div><div className="text-[10px] text-slate-300">N/A</div></div>
  const score = value.charAt(0)
  const color = DNV_COLORS[score] || "bg-slate-400"
  return (
    <div className="text-center">
      <div className="text-[9px] text-slate-400 uppercase mb-1">{label}</div>
      <div className={cn("inline-block w-6 h-6 rounded-full text-white text-xs font-bold flex items-center justify-center", color)}>{score}</div>
    </div>
  )
}

export default function DNVPage() {
  const [reports, setReports] = useState<DNVReport[]>([])
  const [stats, setStats] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [typeFilter, setTypeFilter] = useState("")
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [uploadName, setUploadName] = useState("")
  const [uploadModel, setUploadModel] = useState("")
  const [uploadType, setUploadType] = useState("system")
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  // Tab & Primer state
  const [activeTab, setActiveTab] = useState<"reports" | "knowledge">("reports")
  const [primer, setPrimer] = useState<any[]>([])
  const [primerCats, setPrimerCats] = useState<string[]>([])
  const [primerFilter, setPrimerFilter] = useState("all")

  useEffect(() => {
    Promise.all([getDNVReports(), getDNVPrimer()]).then(([reportsData, primerData]) => {
      setReports(reportsData.items || [])
      setStats(reportsData.stats || {})
      setPrimer(primerData.items || [])
      setPrimerCats(primerData.categories || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    let list = reports
    if (typeFilter) list = list.filter(r => r.type === typeFilter)
    if (search) {
      const q = search.toLowerCase()
      list = list.filter(r => r.name.toLowerCase().includes(q) || r.fullName.toLowerCase().includes(q) || r.model.toLowerCase().includes(q))
    }
    return list
  }, [reports, typeFilter, search])

  const filteredPrimer = useMemo(() => {
    if (primerFilter === "all") return primer
    return primer.filter(p => p.cat === primerFilter)
  }, [primer, primerFilter])

  const handleUpload = async () => {
    if (!uploadFile || !uploadName) return
    setUploading(true)
    try {
      await uploadDNVReport(uploadFile, uploadName, uploadModel, uploadType)
      const d = await getDNVReports()
      setReports(d.items || [])
      setStats(d.stats || {})
      setUploadOpen(false)
      setUploadFile(null); setUploadName(""); setUploadModel("")
    } catch (e) { console.error(e) }
    finally { setUploading(false) }
  }

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Shield className="h-6 w-6 text-blue-600" /> DNV Intelligence
          </h1>
          <p className="text-sm text-slate-500 mt-1">BESS evaluation reports from DNV assessments — technical benchmarks and safety ratings</p>
        </div>
        <Button onClick={() => setUploadOpen(true)}>
          <Upload className="h-4 w-4 mr-2" /> Upload DNV Report
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="kpi-card"><CardContent className="pt-5 pb-5">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-500">Total Reports</p><p className="text-3xl font-bold text-slate-900 mt-1">{stats.total || 0}</p></div>
            <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center"><Shield className="h-6 w-6 text-blue-600" /></div>
          </div>
        </CardContent></Card>
        <Card className="kpi-card"><CardContent className="pt-5 pb-5">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-500">System Reports</p><p className="text-3xl font-bold text-slate-900 mt-1">{stats.systems || 0}</p></div>
            <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center"><Battery className="h-6 w-6 text-purple-600" /></div>
          </div>
        </CardContent></Card>
        <Card className="kpi-card"><CardContent className="pt-5 pb-5">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-slate-500">Cell Reports</p><p className="text-3xl font-bold text-slate-900 mt-1">{stats.cells || 0}</p></div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center"><Zap className="h-6 w-6 text-emerald-600" /></div>
          </div>
        </CardContent></Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl w-fit">
        <button onClick={() => setActiveTab("reports")}
          className={cn("px-4 py-2 rounded-lg text-sm font-semibold transition-all",
            activeTab === "reports" ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700")}>
          Supplier Reports ({reports.length})
        </button>
        <button onClick={() => setActiveTab("knowledge")}
          className={cn("px-4 py-2 rounded-lg text-sm font-semibold transition-all",
            activeTab === "knowledge" ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700")}>
          Knowledge Base ({primer.length})
        </button>
      </div>

      {activeTab === "knowledge" ? (
        /* ═══════════ KNOWLEDGE BASE ═══════════ */
        <div className="space-y-4">
          {/* Category filter */}
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => setPrimerFilter("all")}
              className={cn("text-xs font-medium px-3 py-1.5 rounded-lg border transition-all",
                primerFilter === "all" ? "bg-brand text-white border-brand" : "bg-white text-slate-500 border-slate-200 hover:border-brand/30")}>
              All ({primer.length})
            </button>
            {primerCats.map(cat => (
              <button key={cat} onClick={() => setPrimerFilter(cat)}
                className={cn("text-xs font-medium px-3 py-1.5 rounded-lg border transition-all",
                  primerFilter === cat ? "bg-brand text-white border-brand" : "bg-white text-slate-500 border-slate-200 hover:border-brand/30")}>
                {cat}
              </button>
            ))}
          </div>

          {/* Primer Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredPrimer.map((p, i) => (
              <Card key={i} className="card-interactive">
                <CardContent className="pt-5 pb-4">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-brand mb-2">{p.cat}</div>
                  <div className="text-2xl mb-3">{p.icon}</div>
                  <h3 className="text-base font-bold text-slate-800 mb-0.5">{p.term}</h3>
                  <p className="text-xs text-slate-400 mb-3">{p.sub}</p>
                  <p className="text-sm text-slate-600 leading-relaxed mb-3">{p.def}</p>
                  <div className="border-l-2 border-brand pl-3">
                    <p className="text-xs text-slate-500 leading-relaxed italic">{p.why}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ) : (
      /* ═══════════ REPORTS TAB ═══════════ */
      <div className="space-y-4">

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input placeholder="Search suppliers..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
        </div>
        <div className="flex gap-2">
          {["", "system", "cell"].map(t => (
            <Button key={t} size="sm" variant={typeFilter === t ? "default" : "outline"} className="text-xs"
              onClick={() => setTypeFilter(t)}>
              {t === "" ? "All" : t === "system" ? "Systems" : "Cells"}
            </Button>
          ))}
        </div>
        <div className="ml-auto text-xs text-slate-400">{filtered.length} reports</div>
      </div>

      {/* Report Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map(r => {
          const isExpanded = expandedId === r.id
          return (
            <Card key={r.id} className="card-interactive cursor-pointer overflow-hidden"
              onClick={() => setExpandedId(isExpanded ? null : r.id)}>
              <CardContent className="pt-5 pb-4">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-bold text-slate-800">{r.name}</h3>
                      <Badge variant={r.type === "system" ? "blue" : "default"} className="text-[9px]">
                        {r.type === "system" ? "SYSTEM" : "CELL"}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400">{r.model}</p>
                  </div>
                  {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="text-center p-2 bg-slate-50 rounded-lg">
                    <div className="text-lg font-bold text-slate-800">{r.perf?.rte ? `${r.perf.rte}%` : "—"}</div>
                    <div className="text-[9px] text-slate-400 uppercase">RTE</div>
                  </div>
                  <div className="text-center p-2 bg-slate-50 rounded-lg">
                    <div className="text-lg font-bold text-slate-800">{r.perf?.cycle_life ? r.perf.cycle_life.toLocaleString() : "—"}</div>
                    <div className="text-[9px] text-slate-400 uppercase">Cycle Life</div>
                  </div>
                  <div className="text-center p-2 bg-slate-50 rounded-lg">
                    <div className="text-lg font-bold text-slate-800">{r.capacity_kwh ? `${r.capacity_kwh.toLocaleString()}` : "—"}</div>
                    <div className="text-[9px] text-slate-400 uppercase">kWh</div>
                  </div>
                </div>

                {/* DNV Ratings */}
                {r.dnv && Object.values(r.dnv).some(v => v) && (
                  <div className="flex items-center gap-4 p-2 bg-blue-50 rounded-lg mb-3">
                    <Shield className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    <div className="flex gap-3 flex-1">
                      <DnvBadge label="Company" value={r.dnv.company} />
                      <DnvBadge label="Battery" value={r.dnv.battery} />
                      <DnvBadge label="Safety" value={r.dnv.safety} />
                      <DnvBadge label="Quality" value={r.dnv.quality} />
                      <DnvBadge label="Service" value={r.dnv.service} />
                    </div>
                  </div>
                )}

                {/* Summary */}
                <p className="text-xs text-slate-500 leading-relaxed">{r.summary}</p>

                {/* Certifications */}
                {r.safety?.certs && r.safety.certs.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {r.safety.certs.slice(0, 5).map((c: string) => (
                      <span key={c} className="text-[9px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-500 border border-slate-200">{c}</span>
                    ))}
                    {r.safety.certs.length > 5 && <span className="text-[9px] text-slate-400">+{r.safety.certs.length - 5}</span>}
                  </div>
                )}

                {/* Expanded Detail */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t space-y-3 animate-fade-in" onClick={e => e.stopPropagation()}>
                    {/* Cell Specs */}
                    {r.cell && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Cell Specifications</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div><span className="text-slate-400">Chemistry:</span> <strong>{r.cell.chemistry}</strong></div>
                          <div><span className="text-slate-400">Format:</span> <strong>{r.cell.format}</strong></div>
                          <div><span className="text-slate-400">Voltage:</span> <strong>{r.cell.voltage_v}V</strong></div>
                          <div><span className="text-slate-400">Capacity:</span> <strong>{r.cell.capacity_ah}Ah</strong></div>
                          {r.cell.config && <div><span className="text-slate-400">Config:</span> <strong>{r.cell.config}</strong></div>}
                          {r.cell.total_cells && <div><span className="text-slate-400">Cells:</span> <strong>{r.cell.total_cells.toLocaleString()}</strong></div>}
                        </div>
                      </div>
                    )}

                    {/* Performance */}
                    {r.perf && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Performance</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          {r.perf.rte && <div><span className="text-slate-400">RTE:</span> <strong>{r.perf.rte}%</strong></div>}
                          {r.perf.cycle_life && <div><span className="text-slate-400">Cycles:</span> <strong>{r.perf.cycle_life.toLocaleString()}</strong></div>}
                          {r.perf.calendar_life && <div><span className="text-slate-400">Calendar:</span> <strong>{r.perf.calendar_life} years</strong></div>}
                          {r.perf.dod && <div><span className="text-slate-400">DoD:</span> <strong>{r.perf.dod}%</strong></div>}
                          {r.perf.deg_per_year && <div><span className="text-slate-400">Degradation:</span> <strong>{r.perf.deg_per_year}%/yr</strong></div>}
                        </div>
                      </div>
                    )}

                    {/* Thermal */}
                    {r.thermal && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Thermal</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div><span className="text-slate-400">Cooling:</span> <strong>{r.thermal.cooling || "—"}</strong></div>
                          {r.thermal.cooling_kw && <div><span className="text-slate-400">Cooling:</span> <strong>{r.thermal.cooling_kw} kW</strong></div>}
                          <div><span className="text-slate-400">Charge:</span> <strong>{r.thermal.t_chg_min ?? "—"}°C to {r.thermal.t_chg_max ?? "—"}°C</strong></div>
                          <div><span className="text-slate-400">Discharge:</span> <strong>{r.thermal.t_dis_min ?? "—"}°C to {r.thermal.t_dis_max ?? "—"}°C</strong></div>
                          {r.thermal.alt_m && <div><span className="text-slate-400">Altitude:</span> <strong>{r.thermal.alt_m.toLocaleString()}m</strong></div>}
                        </div>
                      </div>
                    )}

                    {/* PCS */}
                    {r.pcs && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">PCS</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          {r.pcs.eff_peak && <div><span className="text-slate-400">Peak Eff:</span> <strong>{r.pcs.eff_peak}%</strong></div>}
                          {r.pcs.dc_v_nom && <div><span className="text-slate-400">DC Nom:</span> <strong>{r.pcs.dc_v_nom}V</strong></div>}
                          {r.pcs.dc_v_range && <div><span className="text-slate-400">DC Range:</span> <strong>{r.pcs.dc_v_range}</strong></div>}
                          {r.pcs.freq && <div><span className="text-slate-400">Freq:</span> <strong>{r.pcs.freq}</strong></div>}
                        </div>
                      </div>
                    )}

                    {/* Company */}
                    {r.company && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Company</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          {r.company.loc && <div><span className="text-slate-400">Location:</span> <strong>{r.company.loc}</strong></div>}
                          {r.company.deployments && <div><span className="text-slate-400">Deployments:</span> <strong>{r.company.deployments}</strong></div>}
                          {r.company.deployed_gwh && <div><span className="text-slate-400">Deployed:</span> <strong>{r.company.deployed_gwh} GWh</strong></div>}
                          {r.company.warranty && <div><span className="text-slate-400">Warranty:</span> <strong>{r.company.warranty} years</strong></div>}
                        </div>
                      </div>
                    )}

                    {/* Physical */}
                    {r.phys && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Physical</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          {r.phys.container && <div><span className="text-slate-400">Container:</span> <strong>{r.phys.container}</strong></div>}
                          {r.phys.dims && <div><span className="text-slate-400">Dims:</span> <strong>{r.phys.dims}</strong></div>}
                          {r.phys.wt_t && <div><span className="text-slate-400">Weight:</span> <strong>{r.phys.wt_t}t</strong></div>}
                        </div>
                      </div>
                    )}

                    {/* Safety */}
                    {r.safety && (
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Safety</div>
                        <div className="text-xs space-y-1">
                          {r.safety.ip && <div><span className="text-slate-400">IP Rating:</span> <strong>{r.safety.ip}</strong></div>}
                          {r.safety.fire && <div><span className="text-slate-400">Fire:</span> <strong>{r.safety.fire}</strong></div>}
                          {r.safety.tr && <div><span className="text-slate-400">Thermal Runaway:</span> <strong>{r.safety.tr}</strong></div>}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filtered.length === 0 && (
        <Card><CardContent className="py-16 text-center">
          <Shield className="h-12 w-12 mx-auto text-slate-200 mb-4" />
          <h3 className="text-lg font-semibold text-slate-600">No DNV reports found</h3>
          <p className="text-sm text-slate-400 mt-1">Upload a DNV report to get started</p>
        </CardContent></Card>
      )}

      </div>
      )}

      {/* Upload Dialog */}
      <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Shield className="h-5 w-5 text-blue-600" /> Upload DNV Report</DialogTitle>
            <DialogDescription>Upload a DNV BESS evaluation report PDF for AI extraction</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase">Supplier Name *</label>
              <Input placeholder="e.g. Gotion, SVOLT, CLOU..." value={uploadName} onChange={e => setUploadName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase">Model</label>
              <Input placeholder="e.g. GRID 5015" value={uploadModel} onChange={e => setUploadModel(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-500 uppercase">Report Type</label>
              <div className="flex gap-2">
                <Button size="sm" variant={uploadType === "system" ? "default" : "outline"} onClick={() => setUploadType("system")}>System</Button>
                <Button size="sm" variant={uploadType === "cell" ? "default" : "outline"} onClick={() => setUploadType("cell")}>Cell</Button>
              </div>
            </div>
            <div
              className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center cursor-pointer hover:border-brand/30 transition-colors"
              onClick={() => fileRef.current?.click()}
            >
              <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={e => setUploadFile(e.target.files?.[0] || null)} />
              {uploadFile ? (
                <div className="flex items-center justify-center gap-2">
                  <FileUp className="h-5 w-5 text-brand" />
                  <span className="text-sm font-medium text-slate-700">{uploadFile.name}</span>
                  <button onClick={e => { e.stopPropagation(); setUploadFile(null) }}><X className="h-4 w-4 text-slate-400" /></button>
                </div>
              ) : (
                <>
                  <Upload className="h-8 w-8 mx-auto text-slate-300 mb-2" />
                  <p className="text-sm text-slate-500">Click to select DNV report PDF</p>
                </>
              )}
            </div>
            <Button className="w-full" disabled={!uploadFile || !uploadName || uploading} onClick={handleUpload}>
              {uploading ? <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Extracting...</> : <><Shield className="h-4 w-4 mr-2" /> Import Report</>}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
