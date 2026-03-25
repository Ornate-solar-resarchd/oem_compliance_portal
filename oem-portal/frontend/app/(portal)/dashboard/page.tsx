"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getDashboardStats, getPendingWorkflows, getProjects } from "@/lib/api"
import { cn, formatNumber, scoreColor } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { StageBadge } from "@/components/shared/status-badge"
import { Activity, FileCheck, Clock, TrendingUp, Loader2 } from "lucide-react"

interface Stats { active_projects: number; sheets_in_review: number; pending_approvals: number; avg_compliance_score: number }
interface Workflow { id: string; sheet_number: string; project_name: string; workflow_stage: string; compliance_score: number; component_model_name: string; waiting_hours: number }
interface Project { id: string; name: string; client_name: string; project_type: string; kwh: number; kw: number; location: string; status: string; progress: number }

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<Stats | null>(null)
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, wfRes, projRes] = await Promise.all([getDashboardStats(), getPendingWorkflows(), getProjects()])
        setStats(statsRes)
        setWorkflows(wfRes.items || [])
        setProjects(projRes.items || [])
      } catch (err) { console.error("Dashboard load error:", err) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  if (loading) return <div className="flex items-center justify-center h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>

  const kpiCards = [
    { title: "Active Projects", value: stats?.active_projects ?? 0, icon: Activity, color: "text-blue-600", bg: "bg-blue-50" },
    { title: "Sheets In Review", value: stats?.sheets_in_review ?? 0, icon: FileCheck, color: "text-amber-600", bg: "bg-amber-50" },
    { title: "Pending Approvals", value: stats?.pending_approvals ?? 0, icon: Clock, color: "text-purple-600", bg: "bg-purple-50" },
    { title: "Avg Score", value: stats?.avg_compliance_score ?? 0, icon: TrendingUp, color: "text-emerald-600", bg: "bg-emerald-50", isScore: true },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Overview of technical compliance activities</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
        {kpiCards.map((kpi) => (
          <Card key={kpi.title} className="kpi-card">
            <CardContent className="pt-5 pb-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{kpi.title}</p>
                  <p className={cn("text-3xl font-bold mt-1 number-animate", kpi.isScore ? scoreColor(kpi.value) : "text-slate-900")}>
                    {kpi.isScore ? `${kpi.value}%` : formatNumber(kpi.value)}
                  </p>
                </div>
                <div className={cn("flex items-center justify-center w-12 h-12 rounded-xl", kpi.bg)}>
                  <kpi.icon className={cn("h-6 w-6", kpi.color)} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Workflow Pipeline — TOP */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Approval Pipeline</CardTitle>
              <CardDescription>Pending workflow items requiring attention</CardDescription>
            </div>
            <button onClick={() => router.push("/projects")} className="text-xs text-brand font-semibold hover:underline">
              View All →
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {workflows.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm table-fixed">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-2.5 px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider w-[12%]">Sheet</th>
                    <th className="text-left py-2.5 px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider w-[25%]">Project</th>
                    <th className="text-left py-2.5 px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider w-[25%]">Model</th>
                    <th className="text-left py-2.5 px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider w-[18%]">Stage</th>
                    <th className="text-right py-2.5 px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider w-[10%]">Score</th>
                    <th className="text-right py-2.5 px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider w-[10%]">Waiting</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.slice(0, 8).map((wf) => (
                    <tr key={wf.id} className="border-b border-slate-50 table-row-hover cursor-pointer" onClick={() => router.push("/projects")}>
                      <td className="py-2.5 px-3 font-semibold text-brand">{wf.sheet_number}</td>
                      <td className="py-2.5 px-3 text-slate-700 truncate">{wf.project_name}</td>
                      <td className="py-2.5 px-3 text-slate-500 truncate">{wf.component_model_name}</td>
                      <td className="py-2.5 px-3"><StageBadge stage={wf.workflow_stage} /></td>
                      <td className={cn("py-2.5 px-3 text-right font-bold tabular-nums", scoreColor(wf.compliance_score))}>{wf.compliance_score}%</td>
                      <td className="py-2.5 px-3 text-right">
                        <span className={cn("text-xs font-semibold tabular-nums",
                          wf.waiting_hours > 48 ? "text-red-500" : wf.waiting_hours > 24 ? "text-amber-500" : "text-emerald-500"
                        )}>
                          {wf.waiting_hours < 24 ? `${wf.waiting_hours}h` : `${Math.floor(wf.waiting_hours / 24)}d`}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-slate-400 text-sm">No pending workflows</div>
          )}
        </CardContent>
      </Card>

      {/* Project Progress */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Project Progress</CardTitle>
              <CardDescription>Active project completion status</CardDescription>
            </div>
            <button onClick={() => router.push("/projects")} className="text-xs text-brand font-semibold hover:underline">
              View All →
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {projects.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {projects.slice(0, 6).map((proj) => (
                <div key={proj.id} className="flex items-center gap-4 p-3 rounded-lg border hover:shadow-sm transition-all cursor-pointer"
                  onClick={() => router.push("/projects")}>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-800 truncate">{proj.name}</p>
                    <p className="text-xs text-slate-400">{proj.client_name} · {proj.location}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="w-24">
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className={cn("h-full rounded-full transition-all duration-500",
                          proj.progress >= 80 ? "bg-emerald-500" : proj.progress >= 50 ? "bg-brand" : "bg-amber-500"
                        )} style={{ width: `${proj.progress}%` }} />
                      </div>
                    </div>
                    <span className="text-sm font-bold text-slate-700 tabular-nums w-10 text-right">{proj.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-slate-400 text-sm">No active projects</div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
