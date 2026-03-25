"use client"

import { useEffect, useState } from "react"
import { getPendingWorkflows, advanceWorkflow } from "@/lib/api"
import { cn, scoreColor } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { StageBadge } from "@/components/shared/status-badge"
import {
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  ChevronRight,
  MessageSquare,
  AlertCircle,
} from "lucide-react"

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface WorkflowItem {
  id: string
  sheet_number: string
  project_name: string
  workflow_stage: string
  compliance_score: number
  component_model_name: string
  waiting_hours: number
  revision: number
  pass: number
  fail: number
  waived: number
}

const PIPELINE_STAGES = [
  { key: "draft", label: "Draft" },
  { key: "engineering_review", label: "Eng Review" },
  { key: "tech_lead", label: "Tech Lead" },
  { key: "management", label: "Management" },
  { key: "customer_submission", label: "Cust Submission" },
  { key: "customer_signoff", label: "Cust Signoff" },
  { key: "locked", label: "Locked" },
]

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function WorkflowPage() {
  const [items, setItems] = useState<WorkflowItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<WorkflowItem | null>(null)
  const [comment, setComment] = useState("")
  const [acting, setActing] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null)

  /* Fetch */
  useEffect(() => {
    loadWorkflows()
  }, [])

  async function loadWorkflows() {
    try {
      const res = await getPendingWorkflows()
      setItems(res.items ?? [])
    } catch (e) {
      console.error("Failed to load workflows", e)
    } finally {
      setLoading(false)
    }
  }

  /* Action handler */
  async function handleAction(action: "approve" | "reject") {
    if (!selected) return
    setActing(true)
    try {
      const result = await advanceWorkflow(selected.id, { action, comment })
      setToast({
        message: `Sheet ${selected.sheet_number} ${action === "approve" ? "approved" : "rejected"}: ${result.previous_stage} → ${result.current_stage}`,
        type: "success",
      })
      setComment("")
      setSelected(null)
      await loadWorkflows()
    } catch (e) {
      console.error("Workflow action failed", e)
      setToast({ message: "Action failed. Please try again.", type: "error" })
    } finally {
      setActing(false)
      setTimeout(() => setToast(null), 4000)
    }
  }

  /* Waiting hours color */
  function waitingColor(hours: number) {
    if (hours < 24) return "text-emerald-600"
    if (hours < 48) return "text-amber-600"
    return "text-red-600"
  }

  function waitingBg(hours: number) {
    if (hours < 24) return "bg-emerald-50"
    if (hours < 48) return "bg-amber-50"
    return "bg-red-50"
  }

  function formatWaiting(hours: number) {
    if (hours < 24) return `${hours}h`
    return `${Math.floor(hours / 24)}d ${hours % 24}h`
  }

  /* Current stage index for pipeline */
  function stageIndex(stage: string) {
    return PIPELINE_STAGES.findIndex((s) => s.key === stage)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
          <p className="text-sm text-muted-foreground">Loading approval queue...</p>
        </div>
      </div>
    )
  }

  const activeStageIdx = selected ? stageIndex(selected.workflow_stage) : -1

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div
          className={cn(
            "fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2 animate-in slide-in-from-top-2",
            toast.type === "success" ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
          )}
        >
          {toast.type === "success" ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Approval Workflow</h1>
        <p className="text-sm text-slate-500 mt-1">Review and advance compliance sheet approvals</p>
      </div>

      {/* Pipeline visualization */}
      <Card className="border-0 shadow-sm">
        <CardContent className="pt-6 pb-6">
          <div className="flex items-center justify-between px-4">
            {PIPELINE_STAGES.map((stage, idx) => {
              const isActive = idx === activeStageIdx
              const isPast = activeStageIdx >= 0 && idx < activeStageIdx
              const isFuture = activeStageIdx >= 0 && idx > activeStageIdx

              return (
                <div key={stage.key} className="flex items-center flex-1 last:flex-none">
                  {/* Stage dot + label */}
                  <div className="flex flex-col items-center">
                    <div
                      className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all",
                        isActive
                          ? "bg-primary text-white border-primary scale-110 shadow-lg shadow-primary/25"
                          : isPast
                          ? "bg-emerald-500 text-white border-emerald-500"
                          : "bg-white text-slate-400 border-slate-200"
                      )}
                    >
                      {isPast ? (
                        <CheckCircle2 className="h-5 w-5" />
                      ) : (
                        idx + 1
                      )}
                    </div>
                    <span
                      className={cn(
                        "text-[10px] mt-2 text-center leading-tight font-medium max-w-[80px]",
                        isActive ? "text-primary" : isPast ? "text-emerald-600" : "text-slate-400"
                      )}
                    >
                      {stage.label}
                    </span>
                  </div>

                  {/* Connector line */}
                  {idx < PIPELINE_STAGES.length - 1 && (
                    <div className="flex-1 mx-2 mt-[-20px]">
                      <div
                        className={cn(
                          "h-0.5 w-full rounded-full",
                          isPast ? "bg-emerald-400" : "bg-slate-200"
                        )}
                      />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
          {!selected && (
            <p className="text-center text-xs text-muted-foreground mt-4">
              Select a sheet from the queue below to see its pipeline position
            </p>
          )}
        </CardContent>
      </Card>

      {/* Main content: queue table + action panel */}
      <div className="flex gap-6">
        {/* Pending queue */}
        <div className={cn("flex-1 transition-all", selected ? "max-w-[calc(100%-380px)]" : "")}>
          <Card className="border-0 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Pending Queue</CardTitle>
              <CardDescription>{items.length} items awaiting review</CardDescription>
            </CardHeader>
            <CardContent>
              {items.length === 0 ? (
                <div className="text-center py-12 text-sm text-muted-foreground">
                  <CheckCircle2 className="h-10 w-10 mx-auto text-emerald-400 mb-3" />
                  All caught up! No pending approvals.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Sheet</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Project</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Model</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Stage</th>
                        <th className="text-right py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Score</th>
                        <th className="text-right py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Waiting</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((wf) => (
                        <tr
                          key={wf.id}
                          className={cn(
                            "border-b border-slate-50 cursor-pointer transition-colors",
                            selected?.id === wf.id
                              ? "bg-primary/5 hover:bg-primary/10"
                              : "hover:bg-slate-50/50"
                          )}
                          onClick={() => {
                            setSelected(selected?.id === wf.id ? null : wf)
                            setComment("")
                          }}
                        >
                          <td className="py-2.5 px-3 font-medium text-slate-900">{wf.sheet_number}</td>
                          <td className="py-2.5 px-3 text-slate-600">{wf.project_name}</td>
                          <td className="py-2.5 px-3 text-slate-600 truncate max-w-[150px]">{wf.component_model_name}</td>
                          <td className="py-2.5 px-3">
                            <StageBadge stage={wf.workflow_stage} />
                          </td>
                          <td className={cn("py-2.5 px-3 text-right font-semibold", scoreColor(wf.compliance_score))}>
                            {wf.compliance_score}%
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            <span
                              className={cn(
                                "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
                                waitingBg(wf.waiting_hours),
                                waitingColor(wf.waiting_hours)
                              )}
                            >
                              <Clock className="h-3 w-3" />
                              {formatWaiting(wf.waiting_hours)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Action panel */}
        {selected && (
          <div className="w-[360px] shrink-0">
            <Card className="sticky top-6 border-0 shadow-md">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Review Action</CardTitle>
                <CardDescription>Approve or reject this compliance sheet</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Sheet details */}
                <div className="space-y-3 p-3 rounded-lg bg-slate-50 border">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Sheet Number</span>
                    <span className="text-sm font-semibold">{selected.sheet_number}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Model</span>
                    <span className="text-sm font-medium truncate ml-4 text-right">{selected.component_model_name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Stage</span>
                    <StageBadge stage={selected.workflow_stage} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Score</span>
                    <span className={cn("text-sm font-bold", scoreColor(selected.compliance_score))}>
                      {selected.compliance_score}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Revision</span>
                    <span className="text-sm font-medium">R{selected.revision}</span>
                  </div>
                  <div className="flex items-center gap-2 pt-1">
                    <Badge variant="outline" className="text-[10px] bg-emerald-50 text-emerald-600 border-emerald-200">
                      {selected.pass} pass
                    </Badge>
                    <Badge variant="outline" className="text-[10px] bg-red-50 text-red-600 border-red-200">
                      {selected.fail} fail
                    </Badge>
                    <Badge variant="outline" className="text-[10px] bg-amber-50 text-amber-600 border-amber-200">
                      {selected.waived} waived
                    </Badge>
                  </div>
                </div>

                {/* Comment */}
                <div>
                  <label className="text-sm font-medium mb-1.5 flex items-center gap-1.5">
                    <MessageSquare className="h-3.5 w-3.5 text-muted-foreground" />
                    Comment
                  </label>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Add review notes or feedback..."
                    rows={3}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
                  />
                </div>

                {/* Action buttons */}
                <div className="flex gap-3">
                  <Button
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                    onClick={() => handleAction("approve")}
                    disabled={acting}
                  >
                    {acting ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                    )}
                    Approve
                  </Button>
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={() => handleAction("reject")}
                    disabled={acting}
                  >
                    {acting ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <XCircle className="h-4 w-4 mr-2" />
                    )}
                    Reject
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
