"use client"

import { useEffect, useState, useMemo } from "react"
import { getProjects, createProject, getSheets, getPendingWorkflows, advanceWorkflow, getComponents, createSheet } from "@/lib/api"
import { cn, scoreColor } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { StageBadge } from "@/components/shared/status-badge"
import { ScoreRing } from "@/components/shared/score-ring"
import {
  Plus, MapPin, Zap, Loader2, FileCheck, Lock, Clock, Activity,
  CheckCircle2, XCircle, ChevronRight, MessageSquare
} from "lucide-react"

interface Project { id: string; name: string; client_name: string; project_type: string; kwh: number; kw: number; location: string; status: string; progress: number }
interface Sheet { id: string; sheet_number: string; project_id: string; project_name: string; component_id: string; component_model_name: string; workflow_stage: string; compliance_score: number; revision: string; pass: number; fail: number; waived: number }
interface Workflow { id: string; sheet_number: string; project_name: string; workflow_stage: string; compliance_score: number; component_model_name: string; waiting_hours: number; revision: string; pass: number; fail: number; waived: number }
interface Component { id: string; oem_name: string; model_name: string; component_type_name: string; compliance_score: number }

/* ── Add Sheet Dialog ── */
function AddSheetDialog({ projectId, onCreated }: { projectId: string; onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [components, setComponents] = useState<Component[]>([])
  const [selectedComp, setSelectedComp] = useState("")
  const [creating, setCreating] = useState(false)
  const [loadingComps, setLoadingComps] = useState(false)

  useEffect(() => {
    if (open && components.length === 0) {
      setLoadingComps(true)
      getComponents().then(d => { setComponents(d.items || []); setLoadingComps(false) }).catch(() => setLoadingComps(false))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  const handleCreate = async () => {
    if (!selectedComp) return
    setCreating(true)
    try {
      await createSheet(projectId, selectedComp)
      onCreated()
      setOpen(false)
      setSelectedComp("")
    } catch (e) { console.error(e) }
    finally { setCreating(false) }
  }

  // Group components by OEM
  const grouped = useMemo(() => {
    const map = new Map<string, Component[]>()
    components.forEach(c => {
      if (!map.has(c.oem_name)) map.set(c.oem_name, [])
      map.get(c.oem_name)!.push(c)
    })
    return map
  }, [components])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="w-full text-xs h-8 gap-1.5">
          <Plus className="h-3 w-3" /> Add Compliance Sheet
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md max-h-[70vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-sm">Add Compliance Sheet</DialogTitle>
        </DialogHeader>
        <div className="space-y-3 pt-2">
          <p className="text-xs text-slate-500">Select an OEM component model to evaluate for this project:</p>

          {loadingComps ? (
            <div className="flex items-center justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-slate-400" /></div>
          ) : (
            <div className="space-y-3 max-h-[350px] overflow-y-auto scrollbar-thin">
              {Array.from(grouped.entries()).map(([oem, models]) => (
                <div key={oem}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">{oem}</div>
                  <div className="space-y-1">
                    {models.map(c => (
                      <button key={c.id} onClick={() => setSelectedComp(c.id)}
                        className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg border text-left transition-all text-xs",
                          selectedComp === c.id
                            ? "border-brand bg-brand-50/50 ring-1 ring-brand/20"
                            : "border-slate-100 hover:border-slate-300 hover:bg-slate-50")}>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-slate-700">{c.model_name}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5">{c.component_type_name}</div>
                        </div>
                        <span className={cn("text-xs font-bold", scoreColor(c.compliance_score))}>{c.compliance_score}%</span>
                        {selectedComp === c.id && <CheckCircle2 className="w-4 h-4 text-brand flex-shrink-0" />}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button variant="outline" className="flex-1" onClick={() => setOpen(false)}>Cancel</Button>
            <Button className="flex-1" disabled={!selectedComp || creating} onClick={handleCreate}>
              {creating ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Plus className="h-4 w-4 mr-1" />}
              Create Sheet
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

const STAGES = ["draft", "engineering_review", "technical_lead", "management", "customer_submission", "customer_signoff", "locked"]
const STAGE_LABELS: Record<string, string> = { draft: "Draft", engineering_review: "Eng. Review", technical_lead: "Tech Lead", management: "Management", customer_submission: "Cust. Submit", customer_signoff: "Cust. Signoff", locked: "Locked" }
const TYPE_CONFIG: Record<string, { label: string; color: string }> = {
  utility: { label: "Utility", color: "bg-orange-100 text-orange-700" },
  hybrid: { label: "Hybrid", color: "bg-purple-100 text-purple-700" },
  btm: { label: "BTM", color: "bg-emerald-100 text-emerald-700" },
  ci: { label: "C&I", color: "bg-blue-100 text-blue-700" },
}

export default function ProjectsWorkflowPage() {
  const [tab, setTab] = useState<"projects" | "workflow">("projects")
  const [projects, setProjects] = useState<Project[]>([])
  const [sheets, setSheets] = useState<Sheet[]>([])
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [selectedWF, setSelectedWF] = useState<Workflow | null>(null)
  const [comment, setComment] = useState("")
  const [actionDone, setActionDone] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: "", client_name: "", project_type: "utility", kwh: "", kw: "", location: "" })

  useEffect(() => {
    Promise.all([getProjects(), getSheets(), getPendingWorkflows()]).then(([p, s, w]) => {
      setProjects(p.items || [])
      setSheets(s.items || [])
      setWorkflows(w.items || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const proj = selectedProject ? projects.find(p => p.id === selectedProject) : null
  const projSheets = proj ? sheets.filter(s => s.project_id === proj.id) : []

  const handleCreate = async () => {
    if (!form.name || !form.client_name) return
    await createProject({ name: form.name, client_name: form.client_name, project_type: form.project_type, kwh: Number(form.kwh) || 0, kw: Number(form.kw) || 0, location: form.location })
    const p = await getProjects(); setProjects(p.items || [])
    setShowCreate(false); setForm({ name: "", client_name: "", project_type: "utility", kwh: "", kw: "", location: "" })
  }

  const handleAdvance = async (action: string) => {
    if (!selectedWF) return
    const res = await advanceWorkflow(selectedWF.id, { action, comment })
    setActionDone(`${action === "approve" ? "Approved" : "Rejected"} — moved to ${STAGE_LABELS[res.current_stage] || res.current_stage}`)
    setComment("")
    const w = await getPendingWorkflows(); setWorkflows(w.items || [])
    setTimeout(() => setActionDone(null), 3000)
  }

  const currentStageIdx = selectedWF ? STAGES.indexOf(selectedWF.workflow_stage) : 0

  if (loading) return <div className="flex items-center justify-center h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>

  return (
    <div className="space-y-6">
      {/* Header + Tabs */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Projects & Workflow</h1>
          <p className="text-sm text-slate-500 mt-1">Manage projects and track approval pipeline</p>
        </div>
        <div className="flex items-center gap-2">
          {tab === "projects" && (
            <Dialog open={showCreate} onOpenChange={setShowCreate}>
              <DialogTrigger asChild><Button><Plus className="mr-2 h-4 w-4" /> New Project</Button></DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>New Project</DialogTitle></DialogHeader>
                <div className="space-y-3 pt-2">
                  <Input placeholder="Project Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
                  <Input placeholder="Client Name" value={form.client_name} onChange={e => setForm({...form, client_name: e.target.value})} />
                  <select value={form.project_type} onChange={e => setForm({...form, project_type: e.target.value})}
                    className="w-full h-9 px-3 text-sm border rounded-xl bg-slate-50 focus:border-brand focus:outline-none">
                    <option value="utility">Utility</option><option value="hybrid">Hybrid</option><option value="btm">BTM</option><option value="ci">C&I</option>
                  </select>
                  <div className="grid grid-cols-2 gap-3">
                    <Input placeholder="Capacity (kWh)" type="number" value={form.kwh} onChange={e => setForm({...form, kwh: e.target.value})} />
                    <Input placeholder="Power (kW)" type="number" value={form.kw} onChange={e => setForm({...form, kw: e.target.value})} />
                  </div>
                  <Input placeholder="Location" value={form.location} onChange={e => setForm({...form, location: e.target.value})} />
                  <div className="flex gap-3 pt-2">
                    <Button variant="outline" className="flex-1" onClick={() => setShowCreate(false)}>Cancel</Button>
                    <Button className="flex-1" disabled={!form.name || !form.client_name} onClick={handleCreate}>Create</Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-1 border-b">
        {[
          { key: "projects", label: "Projects", count: projects.length, icon: FileCheck },
          { key: "workflow", label: "Approval Workflow", count: workflows.length, icon: Activity },
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key as any)}
            className={cn("relative flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors",
              tab === t.key ? "text-slate-900" : "text-slate-400 hover:text-slate-600")}>
            <t.icon className="w-4 h-4" />
            {t.label}
            <span className={cn("text-[10px] tabular-nums", tab === t.key ? "text-slate-500" : "text-slate-300")}>{t.count}</span>
            {tab === t.key && <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand rounded-full" />}
          </button>
        ))}
      </div>

      {/* ════════ PROJECTS TAB ════════ */}
      {tab === "projects" && (
        <div className="space-y-4">
          {/* KPI Row */}
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: "Total", value: projects.length, icon: FileCheck, color: "text-slate-700" },
              { label: "Active", value: projects.filter(p => p.status === "active").length, icon: Activity, color: "text-blue-600" },
              { label: "Locked Sheets", value: sheets.filter(s => s.workflow_stage === "locked").length, icon: Lock, color: "text-emerald-600" },
              { label: "In Review", value: sheets.filter(s => !["draft", "locked"].includes(s.workflow_stage)).length, icon: Clock, color: "text-amber-600" },
            ].map(k => (
              <Card key={k.label} className="kpi-card">
                <CardContent className="pt-4 pb-3">
                  <div className="flex items-center gap-3">
                    <k.icon className={cn("w-5 h-5", k.color)} />
                    <div><div className="text-2xl font-bold text-slate-900">{k.value}</div><div className="text-[10px] text-slate-400">{k.label}</div></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Project Grid + Detail */}
          <div className={cn("grid gap-4", selectedProject ? "grid-cols-[1fr_300px]" : "grid-cols-1")}>
            <div className="grid gap-3 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 auto-rows-max">
              {projects.map(p => {
                const type = TYPE_CONFIG[p.project_type] || TYPE_CONFIG.utility
                const sheetCount = sheets.filter(s => s.project_id === p.id).length
                return (
                  <Card key={p.id} className={cn("card-interactive cursor-pointer", selectedProject === p.id && "ring-2 ring-brand/30 border-brand/30")}
                    onClick={() => setSelectedProject(selectedProject === p.id ? null : p.id)}>
                    <CardContent className="pt-4 pb-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-bold text-slate-800 truncate">{p.name}</div>
                          <div className="text-xs text-slate-400 mt-0.5">{p.client_name}</div>
                        </div>
                        <span className={cn("text-[9px] font-bold px-1.5 py-0.5 rounded", type.color)}>{type.label}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 mb-3">
                        {p.kwh ? `${(p.kwh / 1000).toFixed(0)} MWh / ${(p.kw / 1000).toFixed(0)} MW` : ""} · {p.location || "—"}
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Progress value={p.progress} className="h-1.5 flex-1" indicatorClassName={p.progress >= 80 ? "bg-emerald-500" : p.progress >= 50 ? "bg-brand" : "bg-amber-500"} />
                        <span className="text-xs font-bold text-slate-700 tabular-nums">{p.progress}%</span>
                      </div>
                      <div className="text-[10px] text-slate-400">{sheetCount} sheet{sheetCount !== 1 ? "s" : ""}</div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {/* Detail Sidebar */}
            {proj && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{proj.name}</CardTitle>
                    <button onClick={() => setSelectedProject(null)} className="text-slate-400 hover:text-slate-600"><XCircle className="w-4 h-4" /></button>
                  </div>
                  <CardDescription>{proj.client_name}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Add Sheet Button */}
                  <AddSheetDialog
                    projectId={proj.id}
                    onCreated={async () => {
                      const [s, w] = await Promise.all([getSheets(), getPendingWorkflows()])
                      setSheets(s.items || [])
                      setWorkflows(w.items || [])
                    }}
                  />

                  {/* Sheet List */}
                  {projSheets.length === 0 ? (
                    <p className="text-xs text-slate-400 py-4 text-center">No sheets yet — add one above</p>
                  ) : projSheets.map(sh => (
                    <div key={sh.id} className="p-3 rounded-lg bg-slate-50 border space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-brand">{sh.sheet_number}</span>
                        <span className={cn("text-xs font-bold tabular-nums", scoreColor(sh.compliance_score))}>{sh.compliance_score}%</span>
                      </div>
                      <div className="text-[10px] text-slate-400">{sh.component_model_name}</div>
                      <div className="flex items-center justify-between">
                        <StageBadge stage={sh.workflow_stage} />
                        <div className="flex gap-1 text-[9px]">
                          <span className="text-emerald-600 font-semibold">{sh.pass}P</span>
                          {sh.fail > 0 && <span className="text-red-500 font-semibold">{sh.fail}F</span>}
                          {sh.waived > 0 && <span className="text-amber-500 font-semibold">{sh.waived}W</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* ════════ WORKFLOW TAB ════════ */}
      {tab === "workflow" && (
        <div className="grid grid-cols-[1fr_340px] gap-6">
          {/* Left: Pipeline Visual + Table */}
          <div className="space-y-4">
            {/* Stage Pipeline */}
            {selectedWF && (
              <Card>
                <CardContent className="pt-4 pb-3">
                  <div className="flex items-center gap-1">
                    {STAGES.map((stage, i) => {
                      const isComplete = i < currentStageIdx
                      const isCurrent = i === currentStageIdx
                      return (
                        <div key={stage} className="flex items-center gap-1 flex-1">
                          <div className={cn("w-8 h-8 rounded-full border-2 flex items-center justify-center text-[9px] font-bold transition-all",
                            isComplete ? "bg-emerald-500 border-emerald-500 text-white" :
                            isCurrent ? "bg-brand border-brand text-white scale-110 shadow-sm" :
                            "bg-slate-50 border-slate-200 text-slate-300")}>
                            {isComplete ? <CheckCircle2 className="w-4 h-4" /> : (i + 1)}
                          </div>
                          {i < STAGES.length - 1 && <div className={cn("h-0.5 flex-1 rounded", isComplete ? "bg-emerald-400" : "bg-slate-200")} />}
                        </div>
                      )
                    })}
                  </div>
                  <div className="flex justify-between mt-1.5">
                    {STAGES.map(s => <span key={s} className="text-[8px] text-slate-400 text-center flex-1">{STAGE_LABELS[s]?.split(" ")[0]}</span>)}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Pending Table */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Pending Approvals</CardTitle>
                <CardDescription>{workflows.length} items awaiting action</CardDescription>
              </CardHeader>
              <CardContent>
                <table className="w-full text-sm table-fixed">
                  <thead>
                    <tr className="border-b text-[10px] uppercase tracking-wider text-slate-400">
                      <th className="py-2 px-3 text-left w-[12%]">Sheet</th>
                      <th className="py-2 px-3 text-left w-[25%]">Project</th>
                      <th className="py-2 px-3 text-left w-[25%]">Model</th>
                      <th className="py-2 px-3 text-left w-[18%]">Stage</th>
                      <th className="py-2 px-3 text-right w-[10%]">Score</th>
                      <th className="py-2 px-3 text-right w-[10%]">Wait</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workflows.map(wf => (
                      <tr key={wf.id} onClick={() => setSelectedWF(wf)}
                        className={cn("border-b border-slate-50 cursor-pointer transition-colors",
                          selectedWF?.id === wf.id ? "bg-brand-50/50" : "table-row-hover")}>
                        <td className="py-2.5 px-3 font-semibold text-brand">{wf.sheet_number}</td>
                        <td className="py-2.5 px-3 text-slate-700 truncate">{wf.project_name}</td>
                        <td className="py-2.5 px-3 text-slate-500 truncate">{wf.component_model_name}</td>
                        <td className="py-2.5 px-3"><StageBadge stage={wf.workflow_stage} /></td>
                        <td className={cn("py-2.5 px-3 text-right font-bold tabular-nums", scoreColor(wf.compliance_score))}>{wf.compliance_score}%</td>
                        <td className="py-2.5 px-3 text-right">
                          <span className={cn("text-xs font-semibold", wf.waiting_hours > 48 ? "text-red-500" : wf.waiting_hours > 24 ? "text-amber-500" : "text-emerald-500")}>
                            {wf.waiting_hours < 24 ? `${wf.waiting_hours}h` : `${Math.floor(wf.waiting_hours / 24)}d`}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </div>

          {/* Right: Action Panel */}
          <div className="space-y-4">
            {selectedWF ? (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Review: {selectedWF.sheet_number}</CardTitle>
                  <CardDescription>{selectedWF.project_name}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-2.5 rounded-lg bg-slate-50 text-center">
                      <div className={cn("text-lg font-bold", scoreColor(selectedWF.compliance_score))}>{selectedWF.compliance_score}%</div>
                      <div className="text-[10px] text-slate-400">Score</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-50 text-center">
                      <StageBadge stage={selectedWF.workflow_stage} />
                      <div className="text-[10px] text-slate-400 mt-1">Current</div>
                    </div>
                  </div>

                  <div className="text-xs text-slate-500 space-y-1">
                    <div>Model: <span className="font-medium text-slate-700">{selectedWF.component_model_name}</span></div>
                    <div>Revision: <span className="font-medium text-slate-700">{selectedWF.revision}</span></div>
                    <div className="flex gap-2">
                      <span className="text-emerald-600 font-semibold">{selectedWF.pass}P</span>
                      <span className="text-red-500 font-semibold">{selectedWF.fail}F</span>
                      <span className="text-amber-500 font-semibold">{selectedWF.waived}W</span>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-slate-500 mb-1.5 block">Comment</label>
                    <textarea value={comment} onChange={e => setComment(e.target.value)} placeholder="Add review notes..."
                      className="w-full h-20 px-3 py-2 text-sm border rounded-xl bg-slate-50 focus:border-brand focus:outline-none resize-none" />
                  </div>

                  {actionDone && (
                    <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 font-medium flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" /> {actionDone}
                    </div>
                  )}

                  <div className="flex gap-3">
                    <Button variant="success" className="flex-1" onClick={() => handleAdvance("approve")}>
                      <CheckCircle2 className="w-4 h-4 mr-1" /> Approve
                    </Button>
                    <Button variant="destructive" className="flex-1" onClick={() => handleAdvance("reject")}>
                      <XCircle className="w-4 h-4 mr-1" /> Reject
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="py-16 text-center">
                  <Activity className="h-10 w-10 mx-auto text-slate-200 mb-3" />
                  <p className="text-sm text-slate-400">Select a workflow item to review</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
