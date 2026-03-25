"use client"

import { useState, useEffect, useMemo } from "react"
import { getPipeline, createDeal, advanceDeal } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import {
  Loader2, Plus, Phone, Mail, MapPin, Calendar, ArrowRight, ChevronRight,
  CheckCircle2, Clock, DollarSign, Zap, Building2, X, User, FileText, Trophy, AlertCircle
} from "lucide-react"

/* ── Types ── */
interface Activity { date: string; type: string; note: string }
interface Deal {
  id: string; title: string; customer: string; contact_person: string
  contact_email: string; contact_phone: string; stage: string
  capacity: string; location: string; project_type: string
  estimated_value: string; rfq_id: string | null; priority: string
  created_at: string; updated_at: string; notes: string
  activities: Activity[]; outcome?: string
}

const STAGE_CONFIG: Record<string, { icon: any; color: string; bg: string; border: string }> = {
  enquiry:  { icon: Phone,       color: "text-slate-600",   bg: "bg-slate-50",   border: "border-slate-200" },
  rfq:      { icon: FileText,    color: "text-blue-600",    bg: "bg-blue-50",    border: "border-blue-200" },
  meeting:  { icon: User,        color: "text-purple-600",  bg: "bg-purple-50",  border: "border-purple-200" },
  request:  { icon: Zap,         color: "text-amber-600",   bg: "bg-amber-50",   border: "border-amber-200" },
  proposal: { icon: DollarSign,  color: "text-brand",       bg: "bg-brand-50",   border: "border-brand-200" },
  final:    { icon: Trophy,      color: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-200" },
}

const PRIORITY_CONFIG: Record<string, { label: string; color: string }> = {
  high:   { label: "High",   color: "bg-red-100 text-red-700" },
  medium: { label: "Medium", color: "bg-amber-100 text-amber-700" },
  low:    { label: "Low",    color: "bg-slate-100 text-slate-600" },
}

const TYPE_CONFIG: Record<string, { label: string; color: string }> = {
  utility: { label: "Utility",  color: "bg-orange-100 text-orange-700" },
  hybrid:  { label: "Hybrid",   color: "bg-purple-100 text-purple-700" },
  btm:     { label: "BTM",      color: "bg-emerald-100 text-emerald-700" },
  ci:      { label: "C&I",      color: "bg-blue-100 text-blue-700" },
}

export default function PipelinePage() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [stages, setStages] = useState<string[]>([])
  const [stageLabels, setStageLabels] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ title: "", customer: "", contact_person: "", contact_email: "", contact_phone: "", capacity: "", location: "", project_type: "utility", estimated_value: "", notes: "", priority: "medium" })

  useEffect(() => {
    getPipeline().then(d => {
      setDeals(d.items || [])
      setStages(d.stages || [])
      setStageLabels(d.stage_labels || {})
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const dealsByStage = useMemo(() => {
    const map = new Map<string, Deal[]>()
    stages.forEach(s => map.set(s, []))
    deals.forEach(d => {
      if (map.has(d.stage)) map.get(d.stage)!.push(d)
    })
    return map
  }, [deals, stages])

  const handleCreate = async () => {
    if (!form.title || !form.customer) return
    try {
      await createDeal(form)
      const d = await getPipeline()
      setDeals(d.items || [])
      setShowCreate(false)
      setForm({ title: "", customer: "", contact_person: "", contact_email: "", contact_phone: "", capacity: "", location: "", project_type: "utility", estimated_value: "", notes: "", priority: "medium" })
    } catch (e) { console.error(e) }
  }

  const handleAdvance = async (dealId: string, nextStage: string, note: string) => {
    try {
      await advanceDeal(dealId, { stage: nextStage, note })
      const d = await getPipeline()
      setDeals(d.items || [])
      const updated = (d.items || []).find((x: Deal) => x.id === dealId)
      if (updated) setSelectedDeal(updated)
    } catch (e) { console.error(e) }
  }

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Deal Pipeline</h1>
          <p className="text-sm text-slate-500 mt-1">Track projects from first enquiry to final closure</p>
        </div>
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" /> New Lead</Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader><DialogTitle>Create New Lead</DialogTitle></DialogHeader>
            <div className="space-y-3 pt-2">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Deal Title *</label>
                  <Input placeholder="e.g. NTPC Bihar 500 MWh" value={form.title} onChange={e => setForm({...form, title: e.target.value})} /></div>
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Customer *</label>
                  <Input placeholder="e.g. NTPC REL" value={form.customer} onChange={e => setForm({...form, customer: e.target.value})} /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Contact Person</label>
                  <Input placeholder="Name" value={form.contact_person} onChange={e => setForm({...form, contact_person: e.target.value})} /></div>
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Contact Email</label>
                  <Input placeholder="email@example.com" value={form.contact_email} onChange={e => setForm({...form, contact_email: e.target.value})} /></div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Capacity</label>
                  <Input placeholder="15 MW / 45 MWh" value={form.capacity} onChange={e => setForm({...form, capacity: e.target.value})} /></div>
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Location</label>
                  <Input placeholder="City, State" value={form.location} onChange={e => setForm({...form, location: e.target.value})} /></div>
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Est. Value</label>
                  <Input placeholder="INR 85 Cr" value={form.estimated_value} onChange={e => setForm({...form, estimated_value: e.target.value})} /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Type</label>
                  <select value={form.project_type} onChange={e => setForm({...form, project_type: e.target.value})}
                    className="w-full h-9 px-3 text-sm border rounded-xl bg-slate-50 focus:border-brand focus:outline-none">
                    <option value="utility">Utility</option><option value="hybrid">Hybrid</option><option value="btm">BTM</option><option value="ci">C&I</option>
                  </select></div>
                <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Priority</label>
                  <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})}
                    className="w-full h-9 px-3 text-sm border rounded-xl bg-slate-50 focus:border-brand focus:outline-none">
                    <option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
                  </select></div>
              </div>
              <div className="space-y-1.5"><label className="text-xs font-medium text-slate-500">Notes</label>
                <textarea value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Additional notes..."
                  className="w-full h-20 px-3 py-2 text-sm border rounded-xl bg-slate-50 focus:border-brand focus:outline-none resize-none" /></div>
              <div className="flex gap-3 pt-2">
                <Button variant="outline" className="flex-1" onClick={() => setShowCreate(false)}>Cancel</Button>
                <Button className="flex-1" disabled={!form.title || !form.customer} onClick={handleCreate}>Create Lead</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stage Summary */}
      <div className="grid grid-cols-6 gap-3">
        {stages.map((stage, i) => {
          const cfg = STAGE_CONFIG[stage] || STAGE_CONFIG.enquiry
          const count = dealsByStage.get(stage)?.length || 0
          const Icon = cfg.icon
          return (
            <div key={stage} className={cn("rounded-xl border p-3 transition-all", cfg.bg, cfg.border)}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className={cn("w-4 h-4", cfg.color)} />
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{stageLabels[stage] || stage}</span>
              </div>
              <div className={cn("text-2xl font-bold", cfg.color)}>{count}</div>
            </div>
          )
        })}
      </div>

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin">
        {stages.map((stage, stageIdx) => {
          const cfg = STAGE_CONFIG[stage] || STAGE_CONFIG.enquiry
          const stageDeals = dealsByStage.get(stage) || []
          const Icon = cfg.icon
          const nextStage = stageIdx < stages.length - 1 ? stages[stageIdx + 1] : null
          return (
            <div key={stage} className="w-[280px] flex-shrink-0 flex flex-col">
              {/* Column Header */}
              <div className={cn("rounded-t-xl border-x border-t px-3 py-2.5 flex items-center gap-2", cfg.bg, cfg.border)}>
                <Icon className={cn("w-4 h-4", cfg.color)} />
                <span className="text-xs font-bold text-slate-700">{stageLabels[stage]}</span>
                <span className={cn("ml-auto text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center", cfg.color, cfg.bg)}>
                  {stageDeals.length}
                </span>
              </div>

              {/* Cards */}
              <div className={cn("flex-1 border-x border-b rounded-b-xl p-2 space-y-2 min-h-[200px]", cfg.border, "bg-white/50")}>
                {stageDeals.length === 0 ? (
                  <div className="text-center py-8 text-xs text-slate-300">No deals</div>
                ) : stageDeals.map(deal => {
                  const prio = PRIORITY_CONFIG[deal.priority] || PRIORITY_CONFIG.medium
                  const type = TYPE_CONFIG[deal.project_type] || TYPE_CONFIG.utility
                  return (
                    <div key={deal.id} onClick={() => setSelectedDeal(deal)}
                      className="bg-white rounded-lg border border-slate-100 p-3 cursor-pointer hover:shadow-md hover:border-brand/20 transition-all group">
                      {/* Priority + Type */}
                      <div className="flex items-center gap-1.5 mb-2">
                        <span className={cn("text-[9px] font-bold px-1.5 py-0.5 rounded", prio.color)}>{prio.label}</span>
                        <span className={cn("text-[9px] font-bold px-1.5 py-0.5 rounded", type.color)}>{type.label}</span>
                        {deal.outcome === "won" && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 ml-auto">WON</span>}
                      </div>
                      {/* Title */}
                      <h3 className="text-xs font-bold text-slate-800 leading-tight group-hover:text-brand transition-colors">{deal.title}</h3>
                      <div className="text-[10px] text-slate-400 mt-1">{deal.customer}</div>
                      {/* Info */}
                      <div className="mt-2.5 pt-2 border-t border-slate-50 space-y-1">
                        {deal.capacity && <div className="flex items-center gap-1.5 text-[10px] text-slate-500"><Zap className="w-3 h-3 text-amber-400" />{deal.capacity}</div>}
                        {deal.location && <div className="flex items-center gap-1.5 text-[10px] text-slate-500"><MapPin className="w-3 h-3 text-slate-300" />{deal.location}</div>}
                        {deal.estimated_value && <div className="flex items-center gap-1.5 text-[10px] text-slate-500"><DollarSign className="w-3 h-3 text-emerald-400" />{deal.estimated_value}</div>}
                      </div>
                      {/* Advance button */}
                      {nextStage && (
                        <button onClick={e => { e.stopPropagation(); handleAdvance(deal.id, nextStage, "") }}
                          className="mt-2 w-full flex items-center justify-center gap-1 text-[10px] font-semibold text-brand bg-brand-50 hover:bg-brand-100 rounded-md py-1.5 transition-colors">
                          Move to {stageLabels[nextStage]} <ChevronRight className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>

      {/* Deal Detail Modal */}
      {selectedDeal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setSelectedDeal(null)}>
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-2xl" onClick={e => e.stopPropagation()}>
            {/* Header */}
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between rounded-t-2xl z-10">
              <div>
                <h2 className="text-lg font-bold text-slate-900">{selectedDeal.title}</h2>
                <div className="text-sm text-slate-500 mt-0.5">{selectedDeal.customer}</div>
              </div>
              <button onClick={() => setSelectedDeal(null)} className="text-slate-400 hover:text-slate-600 transition-colors"><X className="w-5 h-5" /></button>
            </div>

            <div className="p-6 space-y-6">
              {/* Stage Progress */}
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Pipeline Progress</div>
                <div className="flex items-center gap-1">
                  {stages.map((stage, i) => {
                    const cfg = STAGE_CONFIG[stage] || STAGE_CONFIG.enquiry
                    const stageIdx = stages.indexOf(selectedDeal.stage)
                    const isComplete = i < stageIdx
                    const isCurrent = i === stageIdx
                    const Icon = cfg.icon
                    return (
                      <div key={stage} className="flex items-center gap-1 flex-1">
                        <div className={cn("flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all",
                          isComplete ? "bg-emerald-500 border-emerald-500 text-white" :
                          isCurrent ? cn(cfg.bg, cfg.border, cfg.color, "border-2 scale-110 shadow-sm") :
                          "bg-slate-50 border-slate-200 text-slate-300")}>
                          {isComplete ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-3.5 h-3.5" />}
                        </div>
                        {i < stages.length - 1 && <div className={cn("h-0.5 flex-1 rounded", isComplete ? "bg-emerald-400" : "bg-slate-200")} />}
                      </div>
                    )
                  })}
                </div>
                <div className="flex justify-between mt-1.5">
                  {stages.map(s => <span key={s} className="text-[9px] text-slate-400 text-center flex-1">{stageLabels[s]?.split(" ")[0]}</span>)}
                </div>
              </div>

              {/* Info Grid */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { icon: Zap, label: "Capacity", value: selectedDeal.capacity },
                  { icon: MapPin, label: "Location", value: selectedDeal.location },
                  { icon: DollarSign, label: "Est. Value", value: selectedDeal.estimated_value },
                  { icon: Building2, label: "Type", value: TYPE_CONFIG[selectedDeal.project_type]?.label || selectedDeal.project_type },
                  { icon: User, label: "Contact", value: selectedDeal.contact_person },
                  { icon: Mail, label: "Email", value: selectedDeal.contact_email },
                ].filter(x => x.value).map(item => (
                  <div key={item.label} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                    <item.icon className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    <div>
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider">{item.label}</div>
                      <div className="text-xs font-semibold text-slate-700">{item.value}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Notes */}
              {selectedDeal.notes && (
                <div className="p-3 rounded-lg bg-amber-50 border border-amber-200">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-amber-600 mb-1">Notes</div>
                  <div className="text-xs text-amber-800">{selectedDeal.notes}</div>
                </div>
              )}

              {/* Activity Timeline */}
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Activity Timeline</div>
                <div className="space-y-0">
                  {(selectedDeal.activities || []).map((act, i) => {
                    const cfg = STAGE_CONFIG[act.type] || STAGE_CONFIG.enquiry
                    const Icon = cfg.icon
                    const isLast = i === selectedDeal.activities.length - 1
                    return (
                      <div key={i} className="flex gap-3">
                        <div className="flex flex-col items-center">
                          <div className={cn("w-7 h-7 rounded-full border-2 flex items-center justify-center flex-shrink-0", cfg.bg, cfg.border)}>
                            <Icon className={cn("w-3 h-3", cfg.color)} />
                          </div>
                          {!isLast && <div className="w-0.5 flex-1 bg-slate-200 my-1" />}
                        </div>
                        <div className={cn("pb-4", isLast ? "" : "")}>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-700">{stageLabels[act.type] || act.type}</span>
                            <span className="text-[10px] text-slate-400">{act.date}</span>
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5">{act.note}</div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Advance Actions */}
              {(() => {
                const currentIdx = stages.indexOf(selectedDeal.stage)
                const nextStage = currentIdx < stages.length - 1 ? stages[currentIdx + 1] : null
                if (!nextStage || selectedDeal.outcome) return null
                return (
                  <Button className="w-full" onClick={() => handleAdvance(selectedDeal.id, nextStage, "")}>
                    Advance to {stageLabels[nextStage]} <ArrowRight className="ml-2 w-4 h-4" />
                  </Button>
                )
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
