"use client"

import { useState, useEffect, useMemo } from "react"
import { useParams, useRouter } from "next/navigation"
import { getRFQ } from "@/lib/api"
import { SplitDocumentViewer } from "@/components/shared/split-document-viewer"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  ArrowLeft, Loader2, FileText, MapPin, Zap, Calendar, Building2,
  Download, ClipboardList, CheckCircle2, ChevronDown, ChevronRight
} from "lucide-react"

interface Requirement {
  parameter: string
  code: string
  required_value: string
  unit: string
  section?: string
}

interface RFQ {
  id: string
  customer_name: string
  project_name: string
  status: string
  created_at: string
  requirements: Requirement[]
  source_file?: string
  file_size?: number
  extraction_method?: string
  text_length?: number
  gdrive_url?: string
  gdrive_file_id?: string
  project_meta?: {
    rfq_ref?: string
    capacity?: string
    solar_pv?: string
    location?: string
    scope?: string
    design_life?: string
    issuer?: string
  }
}

export default function RFQDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  const [rfq, setRfq] = useState<RFQ | null>(null)
  const [loading, setLoading] = useState(true)
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set())

  const toggleSection = (key: string) => {
    setCollapsedSections(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  const collapseAll = (keys: string[]) => {
    setCollapsedSections(prev => {
      const allCollapsed = keys.every(k => prev.has(k))
      const next = new Set(prev)
      if (allCollapsed) keys.forEach(k => next.delete(k))
      else keys.forEach(k => next.add(k))
      return next
    })
  }

  useEffect(() => {
    getRFQ(id).then(d => { setRfq(d); setLoading(false) }).catch(() => setLoading(false))
  }, [id])

  // Group requirements by section
  const groupedReqs = useMemo(() => {
    if (!rfq) return new Map<string, Requirement[]>()
    const map = new Map<string, Requirement[]>()
    for (const r of (rfq.requirements || [])) {
      const section = r.section || "General"
      if (!map.has(section)) map.set(section, [])
      map.get(section)!.push(r)
    }
    return map
  }, [rfq])

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-slate-400" /></div>
  if (!rfq) return <div className="text-center py-20 text-slate-400">RFQ not found</div>

  const meta = rfq.project_meta

  return (
    <div className="space-y-6 animate-fade-in-up" style={{ animationFillMode: "both" }}>
      {/* Back */}
      <Button variant="ghost" onClick={() => router.push("/rfq")}>
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to RFQ Manager
      </Button>

      {/* Header Card */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="pass" className="text-[10px] uppercase tracking-wider">
                {rfq.status}
              </Badge>
              {rfq.extraction_method && (
                <Badge variant="brand" className="text-[10px] uppercase tracking-wider">
                  {rfq.extraction_method === "document_parsing" ? "AI Extracted" : rfq.extraction_method}
                </Badge>
              )}
            </div>
            <h1 className="text-2xl font-bold">{rfq.project_name}</h1>
            <div className="text-slate-300 mt-1">{rfq.customer_name}</div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-brand">{(rfq.requirements || []).length}</div>
            <div className="text-xs text-slate-400 mt-1">Requirements Extracted</div>
          </div>
        </div>

        {/* Meta Info */}
        {meta && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5 pt-5 border-t border-white/10">
            {meta.capacity && (
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                <div><div className="text-[10px] text-slate-400">Capacity</div><div className="text-sm font-semibold">{meta.capacity}</div></div>
              </div>
            )}
            {meta.location && (
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-400" />
                <div><div className="text-[10px] text-slate-400">Location</div><div className="text-sm font-semibold">{meta.location}</div></div>
              </div>
            )}
            {meta.rfq_ref && (
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <div><div className="text-[10px] text-slate-400">RFQ Ref</div><div className="text-sm font-semibold">{meta.rfq_ref}</div></div>
              </div>
            )}
            {meta.design_life && (
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-400" />
                <div><div className="text-[10px] text-slate-400">Design Life</div><div className="text-sm font-semibold">{meta.design_life}</div></div>
              </div>
            )}
            {meta.solar_pv && (
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <div><div className="text-[10px] text-slate-400">Solar PV</div><div className="text-sm font-semibold">{meta.solar_pv}</div></div>
              </div>
            )}
            {meta.scope && (
              <div className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-slate-400" />
                <div><div className="text-[10px] text-slate-400">Scope</div><div className="text-sm font-semibold">{meta.scope}</div></div>
              </div>
            )}
          </div>
        )}

        {/* Source file info */}
        {rfq.source_file && (
          <div className="flex items-center gap-2 mt-4 pt-4 border-t border-white/10 text-xs text-slate-400">
            <FileText className="w-3.5 h-3.5" />
            <span>Source: {rfq.source_file}</span>
            {rfq.text_length && <span>· {rfq.text_length.toLocaleString()} chars parsed</span>}
          </div>
        )}
      </div>

      {/* Split View: PDF + Extracted Requirements */}
      {(rfq.gdrive_url || rfq.gdrive_file_id || rfq.source_file) && (
        <SplitDocumentViewer
          gdriveUrl={rfq.gdrive_url}
          gdriveFileId={rfq.gdrive_file_id}
          fileName={rfq.source_file}
          parameters={(rfq.requirements || []).map(r => ({
            name: r.parameter,
            code: r.code,
            required_value: r.required_value,
            unit: r.unit,
            section: r.section,
          }))}
          mode="rfq"
          summary={{
            customer_name: rfq.customer_name,
            project_name: rfq.project_name,
            total: (rfq.requirements || []).length,
          }}
        />
      )}

      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <FileText className="w-5 h-5 text-brand" />
          Extracted Requirements ({(rfq.requirements || []).length})
        </h2>
        <div className="flex items-center gap-2">
          <Badge variant="brand" className="text-xs">{Array.from(groupedReqs.keys()).length} sections</Badge>
          <button
            onClick={() => collapseAll(Array.from(groupedReqs.keys()))}
            className="text-xs text-brand font-medium hover:underline"
          >
            {Array.from(groupedReqs.keys()).every(k => collapsedSections.has(k)) ? "Expand All" : "Collapse All"}
          </button>
        </div>
      </div>


      {/* Requirements Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Array.from(groupedReqs.entries()).map(([section, reqs]) => (
          <Card key={section} className="card-interactive">
            <CardContent className="pt-4 pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{section}</div>
                  <div className="text-2xl font-bold text-slate-800 mt-1">{reqs.length}</div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center">
                  <ClipboardList className="w-5 h-5 text-brand" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Requirements by Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-xs text-slate-500">
            {groupedReqs.size} sections · {rfq.requirements?.length || 0} total
          </div>
          <button
            onClick={() => collapseAll(Array.from(groupedReqs.keys()).map(s => `req-${s}`))}
            className="text-xs text-brand font-medium hover:underline"
          >
            {Array.from(groupedReqs.keys()).every(s => collapsedSections.has(`req-${s}`)) ? "Expand All" : "Collapse All"}
          </button>
        </div>
        {Array.from(groupedReqs.entries()).map(([section, reqs]) => {
          const key = `req-${section}`
          const isCollapsed = collapsedSections.has(key)
          return (
            <Card key={section} className="overflow-hidden">
              <button
                onClick={() => toggleSection(key)}
                className="w-full text-left px-5 py-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-brand/10 flex items-center justify-center shrink-0">
                    {isCollapsed
                      ? <ChevronRight className="w-4 h-4 text-brand" />
                      : <ChevronDown className="w-4 h-4 text-brand" />
                    }
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{section}</div>
                    <div className="text-xs text-slate-500">{reqs.length} requirements</div>
                  </div>
                </div>
                <Badge variant="outline" className="tabular-nums shrink-0">
                  {reqs.length}
                </Badge>
              </button>

              {!isCollapsed && (
                <CardContent className="pt-0 pb-4 border-t">
                  <div className="rounded-lg border overflow-hidden mt-4">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-slate-50 border-b text-[10px] uppercase tracking-wider text-slate-500">
                          <th className="py-2.5 px-4 text-left font-semibold">Parameter</th>
                          <th className="py-2.5 px-4 text-left font-semibold">Code</th>
                          <th className="py-2.5 px-4 text-left font-semibold">Required Value</th>
                          <th className="py-2.5 px-4 text-left font-semibold">Unit</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reqs.map((r, i) => (
                          <tr key={r.code + i} className={cn("border-b last:border-0 table-row-hover", i % 2 ? "bg-slate-50/50" : "")}>
                            <td className="py-2.5 px-4 font-medium text-slate-700">{r.parameter}</td>
                            <td className="py-2.5 px-4 font-mono text-xs text-slate-400">{r.code}</td>
                            <td className="py-2.5 px-4">
                              <span className={cn("font-semibold",
                                r.required_value.startsWith(">=") ? "text-emerald-600" :
                                r.required_value.startsWith("<=") ? "text-blue-600" :
                                r.required_value === "Yes" || r.required_value === "Required" || r.required_value === "Mandatory" ? "text-brand" :
                                "text-slate-800"
                              )}>
                                {r.required_value}
                              </span>
                            </td>
                            <td className="py-2.5 px-4 text-slate-400 text-xs">{r.unit}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              )}
            </Card>
          )
        })}
      </div>

      {/* Download / Actions */}
      <div className="flex gap-3">
        <Button variant="outline" className="flex-1" onClick={() => window.print()}>
          <Download className="mr-2 h-4 w-4" /> Download / Print
        </Button>
      </div>

    </div>
  )
}
