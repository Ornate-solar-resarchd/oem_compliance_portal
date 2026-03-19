"use client"

import { useEffect, useState, useMemo } from "react"
import { getProjects, createProject, getSheets } from "@/lib/api"
import { cn, formatNumber, scoreColor, scoreBg } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/components/ui/dialog"
import { StageBadge } from "@/components/shared/status-badge"
import {
  FolderKanban,
  Plus,
  MapPin,
  Zap,
  X,
  Loader2,
  FileCheck,
  Lock,
  Clock,
  Activity,
} from "lucide-react"

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface Project {
  id: string
  name: string
  client_name: string
  project_type: string
  kwh: number
  kw: number
  location: string
  status: string
  progress: number
}

interface Sheet {
  id: string
  sheet_number: string
  project_id: string
  project_name: string
  component_id: string
  component_model_name: string
  workflow_stage: string
  compliance_score: number
  revision: number
  pass: number
  fail: number
  waived: number
}

const TYPE_COLORS: Record<string, string> = {
  utility: "bg-orange-100 text-orange-700 border-orange-200",
  hybrid: "bg-purple-100 text-purple-700 border-purple-200",
  btm: "bg-emerald-100 text-emerald-700 border-emerald-200",
  ci: "bg-blue-100 text-blue-700 border-blue-200",
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [sheets, setSheets] = useState<Sheet[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)

  /* New Project Dialog */
  const [dialogOpen, setDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    client_name: "",
    project_type: "utility",
    kwh: "",
    kw: "",
    location: "",
  })

  /* Fetch */
  useEffect(() => {
    async function load() {
      try {
        const [projRes, sheetsRes] = await Promise.all([getProjects(), getSheets()])
        setProjects(projRes.items ?? [])
        setSheets(sheetsRes.items ?? [])
      } catch (e) {
        console.error("Failed to load projects", e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  /* Derived KPIs */
  const totalProjects = projects.length
  const activeProjects = projects.filter((p) => p.status === "active").length
  const lockedSheets = sheets.filter((s) => s.workflow_stage === "locked").length
  const pendingSheets = sheets.filter((s) => s.workflow_stage !== "locked" && s.workflow_stage !== "draft").length

  /* Project sheets */
  const projectSheets = useMemo(() => {
    if (!selectedProject) return []
    return sheets.filter((s) => s.project_id === selectedProject.id)
  }, [selectedProject, sheets])

  /* Create Project */
  async function handleCreate() {
    if (!formData.name.trim()) return
    setSubmitting(true)
    try {
      await createProject({
        name: formData.name,
        client_name: formData.client_name,
        project_type: formData.project_type,
        kwh: Number(formData.kwh) || 0,
        kw: Number(formData.kw) || 0,
        location: formData.location,
      })
      const res = await getProjects()
      setProjects(res.items ?? [])
      setDialogOpen(false)
      setFormData({ name: "", client_name: "", project_type: "utility", kwh: "", kw: "", location: "" })
    } catch (e) {
      console.error("Failed to create project", e)
    } finally {
      setSubmitting(false)
    }
  }

  /* Sheet count per project */
  function sheetCount(projectId: string) {
    return sheets.filter((s) => s.project_id === projectId).length
  }

  /* Loading */
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
          <p className="text-sm text-muted-foreground">Loading projects...</p>
        </div>
      </div>
    )
  }

  const kpiCards = [
    { title: "Total Projects", value: totalProjects, icon: FolderKanban, color: "text-blue-600", bg: "bg-blue-50" },
    { title: "Active", value: activeProjects, icon: Activity, color: "text-emerald-600", bg: "bg-emerald-50" },
    { title: "Locked Sheets", value: lockedSheets, icon: Lock, color: "text-purple-600", bg: "bg-purple-50" },
    { title: "Pending Sheets", value: pendingSheets, icon: Clock, color: "text-amber-600", bg: "bg-amber-50" },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
          <p className="text-sm text-slate-500 mt-1">Manage BESS project compliance tracking</p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
              <DialogDescription>Add a new BESS project for technical compliance evaluation.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Project Name *</label>
                <Input
                  placeholder="e.g., Solar Valley 200MW BESS"
                  value={formData.name}
                  onChange={(e) => setFormData((f) => ({ ...f, name: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Client Name</label>
                <Input
                  placeholder="e.g., Acme Energy Corp"
                  value={formData.client_name}
                  onChange={(e) => setFormData((f) => ({ ...f, client_name: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Project Type</label>
                <select
                  value={formData.project_type}
                  onChange={(e) => setFormData((f) => ({ ...f, project_type: e.target.value }))}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="utility">Utility Scale</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="btm">Behind-the-Meter</option>
                  <option value="ci">C&I</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Capacity (kWh)</label>
                  <Input
                    placeholder="e.g., 500000"
                    type="number"
                    value={formData.kwh}
                    onChange={(e) => setFormData((f) => ({ ...f, kwh: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Power (kW)</label>
                  <Input
                    placeholder="e.g., 125000"
                    type="number"
                    value={formData.kw}
                    onChange={(e) => setFormData((f) => ({ ...f, kw: e.target.value }))}
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Location</label>
                <Input
                  placeholder="e.g., Texas, USA"
                  value={formData.location}
                  onChange={(e) => setFormData((f) => ({ ...f, location: e.target.value }))}
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreate} disabled={submitting || !formData.name.trim()}>
                  {submitting ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpi) => (
          <Card key={kpi.title} className="border-0 shadow-sm">
            <CardContent className="pt-5 pb-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{kpi.title}</p>
                  <p className="text-3xl font-bold mt-1 text-slate-900">{formatNumber(kpi.value)}</p>
                </div>
                <div className={cn("flex items-center justify-center w-12 h-12 rounded-xl", kpi.bg)}>
                  <kpi.icon className={cn("h-6 w-6", kpi.color)} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main content: grid + sidebar */}
      <div className="flex gap-6">
        {/* Project cards grid */}
        <div className={cn("flex-1 transition-all", selectedProject ? "max-w-[calc(100%-380px)]" : "")}>
          {projects.length === 0 ? (
            <div className="text-center py-20">
              <FolderKanban className="h-12 w-12 mx-auto text-muted-foreground/40 mb-4" />
              <p className="text-muted-foreground">No projects yet. Create your first project.</p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {projects.map((proj) => (
                <Card
                  key={proj.id}
                  className={cn(
                    "group cursor-pointer hover:shadow-lg transition-all duration-200 hover:border-primary/30",
                    selectedProject?.id === proj.id && "ring-2 ring-primary/50 border-primary/30"
                  )}
                  onClick={() => setSelectedProject(selectedProject?.id === proj.id ? null : proj)}
                >
                  <CardContent className="pt-6">
                    {/* Name + type badge */}
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <h3 className="font-semibold text-base truncate group-hover:text-primary transition-colors">
                        {proj.name}
                      </h3>
                      <Badge
                        variant="outline"
                        className={cn("text-[10px] uppercase shrink-0", TYPE_COLORS[proj.project_type] || "bg-slate-100 text-slate-600")}
                      >
                        {proj.project_type}
                      </Badge>
                    </div>

                    {/* Client */}
                    <p className="text-sm text-muted-foreground mb-2">{proj.client_name || "No client"}</p>

                    {/* Capacity + Location */}
                    <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
                      <span className="flex items-center gap-1">
                        <Zap className="h-3 w-3" />
                        {formatNumber(proj.kwh)} kWh / {formatNumber(proj.kw)} kW
                      </span>
                      {proj.location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {proj.location}
                        </span>
                      )}
                    </div>

                    {/* Progress */}
                    <div className="mb-2">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs text-muted-foreground">Progress</span>
                        <span className="text-xs font-semibold text-slate-700">{proj.progress}%</span>
                      </div>
                      <Progress value={proj.progress} className="h-2" />
                    </div>

                    {/* Sheet count */}
                    <div className="pt-3 border-t mt-3 flex items-center justify-between">
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <FileCheck className="h-3 w-3" />
                        {sheetCount(proj.id)} sheets
                      </span>
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-[10px]",
                          proj.status === "active"
                            ? "bg-emerald-50 text-emerald-600 border-emerald-200"
                            : "bg-slate-50 text-slate-600 border-slate-200"
                        )}
                      >
                        {proj.status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Right sidebar: project sheets */}
        {selectedProject && (
          <div className="w-[360px] shrink-0">
            <Card className="sticky top-6 border-0 shadow-md">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{selectedProject.name}</CardTitle>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setSelectedProject(null)}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <CardDescription>Compliance sheets for this project</CardDescription>
              </CardHeader>
              <CardContent>
                {projectSheets.length === 0 ? (
                  <div className="text-center py-8 text-sm text-muted-foreground">
                    No sheets assigned to this project.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {projectSheets.map((sheet) => (
                      <div
                        key={sheet.id}
                        className="p-3 rounded-lg border bg-slate-50/50 hover:bg-slate-100/80 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-slate-900">{sheet.sheet_number}</span>
                          <span className={cn("text-sm font-bold", scoreColor(sheet.compliance_score))}>
                            {sheet.compliance_score}%
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground truncate mb-2">{sheet.component_model_name}</p>
                        <div className="flex items-center gap-2 flex-wrap">
                          <StageBadge stage={sheet.workflow_stage} />
                          <Badge variant="outline" className="text-[10px] bg-emerald-50 text-emerald-600 border-emerald-200">
                            {sheet.pass} pass
                          </Badge>
                          <Badge variant="outline" className="text-[10px] bg-red-50 text-red-600 border-red-200">
                            {sheet.fail} fail
                          </Badge>
                          <Badge variant="outline" className="text-[10px] bg-amber-50 text-amber-600 border-amber-200">
                            {sheet.waived} waived
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
