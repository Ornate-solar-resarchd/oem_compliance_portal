"use client"

import { useEffect, useState } from "react"
import { getDashboardStats, getDashboardCharts, getOEMs, getPendingWorkflows, getProjects } from "@/lib/api"
import { cn, formatNumber, scoreColor, scoreBg } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScoreRing } from "@/components/shared/score-ring"
import { StageBadge } from "@/components/shared/status-badge"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts"
import { Activity, FileCheck, Clock, TrendingUp, Loader2 } from "lucide-react"

interface Stats {
  active_projects: number
  sheets_in_review: number
  pending_approvals: number
  avg_compliance_score: number
}

interface OEM {
  id: string
  name: string
  country_of_origin: string
  is_approved: boolean
  score: number
  model_count: number
  avg_compliance_score: number
}

interface Workflow {
  id: string
  sheet_number: string
  project_name: string
  workflow_stage: string
  compliance_score: number
  component_model_name: string
  waiting_hours: number
}

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

interface ChartData {
  oem_name: string
  model_scores: { model: string; score: number }[]
  electrical_params: { name: string; value: number; unit: string }[]
  compliance_breakdown: { pass: number; fail: number; waived: number }
}

const PIE_COLORS = ["#10b981", "#ef4444", "#f59e0b"]

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [oems, setOems] = useState<OEM[]>([])
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [chartData, setChartData] = useState<ChartData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, oemsRes, wfRes, projRes] = await Promise.all([
          getDashboardStats(),
          getOEMs(),
          getPendingWorkflows(),
          getProjects(),
        ])
        setStats(statsRes)
        setOems(oemsRes.items || [])
        setWorkflows(wfRes.items || [])
        setProjects(projRes.items || [])

        // Fetch chart data for first OEM
        if (oemsRes.items?.length > 0) {
          const charts = await getDashboardCharts(oemsRes.items[0].id)
          setChartData(charts)
        }
      } catch (err) {
        console.error("Dashboard load error:", err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    )
  }

  const kpiCards = [
    {
      title: "Active Projects",
      value: stats?.active_projects ?? 0,
      icon: Activity,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      title: "Sheets In Review",
      value: stats?.sheets_in_review ?? 0,
      icon: FileCheck,
      color: "text-amber-600",
      bg: "bg-amber-50",
    },
    {
      title: "Pending Approvals",
      value: stats?.pending_approvals ?? 0,
      icon: Clock,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      title: "Avg Compliance",
      value: stats?.avg_compliance_score ?? 0,
      icon: TrendingUp,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      isScore: true,
    },
  ]

  // Top 5 OEMs by compliance score for bar chart
  const top5OEMs = [...oems]
    .sort((a, b) => (b.avg_compliance_score || 0) - (a.avg_compliance_score || 0))
    .slice(0, 5)
    .map((o) => ({ name: o.name, score: o.avg_compliance_score || 0 }))

  // Compliance breakdown pie data
  const pieData = chartData
    ? [
        { name: "Pass", value: chartData.compliance_breakdown.pass },
        { name: "Fail", value: chartData.compliance_breakdown.fail },
        { name: "Waived", value: chartData.compliance_breakdown.waived },
      ]
    : []

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Overview of technical compliance activities</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpi) => (
          <Card key={kpi.title} className="border-0 shadow-sm">
            <CardContent className="pt-5 pb-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{kpi.title}</p>
                  <p className={cn("text-3xl font-bold mt-1", kpi.isScore ? scoreColor(kpi.value) : "text-slate-900")}>
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

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* OEM Performance Bar Chart */}
        <Card className="lg:col-span-2 border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">OEM Performance</CardTitle>
            <CardDescription>Top 5 OEMs by average compliance score</CardDescription>
          </CardHeader>
          <CardContent>
            {top5OEMs.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={top5OEMs} layout="vertical" margin={{ left: 20, right: 20, top: 5, bottom: 5 }}>
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={100} />
                  <Tooltip
                    formatter={(value: number) => [`${value}%`, "Compliance Score"]}
                    contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "13px" }}
                  />
                  <Bar dataKey="score" fill="#F26B4E" radius={[0, 6, 6, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[260px] text-slate-400 text-sm">
                No OEM data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Compliance Breakdown Pie */}
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Compliance Breakdown</CardTitle>
            <CardDescription>{chartData?.oem_name || "Overall"}</CardDescription>
          </CardHeader>
          <CardContent>
            {pieData.length > 0 ? (
              <div className="flex flex-col items-center">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                      paddingAngle={3}
                    >
                      {pieData.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "13px" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex items-center gap-4 mt-2">
                  {pieData.map((entry, idx) => (
                    <div key={entry.name} className="flex items-center gap-1.5 text-xs text-slate-600">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[idx] }} />
                      {entry.name} ({entry.value})
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-[200px] text-slate-400 text-sm">
                No chart data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Approval Pipeline */}
        <Card className="lg:col-span-2 border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Approval Pipeline</CardTitle>
            <CardDescription>Pending workflow items requiring attention</CardDescription>
          </CardHeader>
          <CardContent>
            {workflows.length > 0 ? (
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
                    {workflows.slice(0, 8).map((wf) => (
                      <tr key={wf.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                        <td className="py-2.5 px-3 font-medium text-slate-900">{wf.sheet_number}</td>
                        <td className="py-2.5 px-3 text-slate-600">{wf.project_name}</td>
                        <td className="py-2.5 px-3 text-slate-600 truncate max-w-[150px]">{wf.component_model_name}</td>
                        <td className="py-2.5 px-3">
                          <StageBadge stage={wf.workflow_stage} />
                        </td>
                        <td className={cn("py-2.5 px-3 text-right font-semibold", scoreColor(wf.compliance_score))}>
                          {wf.compliance_score}%
                        </td>
                        <td className="py-2.5 px-3 text-right text-slate-500">
                          {wf.waiting_hours < 24
                            ? `${wf.waiting_hours}h`
                            : `${Math.floor(wf.waiting_hours / 24)}d ${wf.waiting_hours % 24}h`}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-slate-400 text-sm">
                No pending workflows
              </div>
            )}
          </CardContent>
        </Card>

        {/* Project Progress */}
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Project Progress</CardTitle>
            <CardDescription>Active project completion status</CardDescription>
          </CardHeader>
          <CardContent>
            {projects.length > 0 ? (
              <div className="space-y-4">
                {projects.slice(0, 6).map((proj) => (
                  <div key={proj.id}>
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="min-w-0 pr-3">
                        <p className="text-sm font-medium text-slate-900 truncate">{proj.name}</p>
                        <p className="text-xs text-slate-500">{proj.client_name}</p>
                      </div>
                      <span className="text-sm font-semibold text-slate-700 whitespace-nowrap">
                        {proj.progress}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all duration-500",
                          proj.progress >= 80
                            ? "bg-emerald-500"
                            : proj.progress >= 50
                            ? "bg-[#F26B4E]"
                            : "bg-amber-500"
                        )}
                        style={{ width: `${proj.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-slate-400 text-sm">
                No active projects
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
