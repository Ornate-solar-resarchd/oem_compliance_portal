"use client"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { ScoreRing } from "@/components/shared/score-ring"
import {
  CheckCircle2, XCircle, AlertTriangle, FileText, ExternalLink, Download,
  ChevronDown, ChevronRight, Maximize2, Minimize2,
} from "lucide-react"
import { useState } from "react"

interface Param {
  name?: string
  parameter?: string
  code?: string
  value?: string
  required_value?: string
  unit?: string
  section?: string
  status?: string
  confidence?: number
}

interface SplitDocumentViewerProps {
  /** Google Drive file ID for PDF preview */
  gdriveFileId?: string
  /** Google Drive URL */
  gdriveUrl?: string
  /** Local file for preview (from upload) */
  localFile?: File | null
  /** Filename */
  fileName?: string
  /** Extracted parameters */
  parameters: Param[]
  /** Summary info */
  summary?: {
    oem_name?: string
    model_name?: string
    customer_name?: string
    project_name?: string
    category?: string
    compliance_score?: number
    pass?: number
    fail?: number
    waived?: number
    total?: number
  }
  /** "datasheet" or "rfq" */
  mode?: "datasheet" | "rfq"
}

const statusIcon = (s: string) => {
  if (s === "pass") return <CheckCircle2 className="h-3 w-3 text-emerald-500" />
  if (s === "fail") return <XCircle className="h-3 w-3 text-red-500" />
  if (s === "waived") return <AlertTriangle className="h-3 w-3 text-amber-500" />
  return null
}

export function SplitDocumentViewer({
  gdriveFileId, gdriveUrl, localFile, fileName, parameters, summary, mode = "datasheet",
}: SplitDocumentViewerProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["Electrical", "BESS System"]))
  const [fullscreen, setFullscreen] = useState(false)

  // Group params by section
  const grouped: Record<string, Param[]> = {}
  parameters.forEach(p => {
    const section = p.section || "General"
    if (!grouped[section]) grouped[section] = []
    grouped[section].push(p)
  })

  const toggleSection = (s: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(s)) next.delete(s); else next.add(s)
      return next
    })
  }

  // Build PDF preview URL
  let pdfSrc = ""
  if (localFile && localFile.type === "application/pdf") {
    pdfSrc = URL.createObjectURL(localFile)
  } else if (gdriveFileId) {
    pdfSrc = `https://drive.google.com/file/d/${gdriveFileId}/preview`
  } else if (gdriveUrl) {
    pdfSrc = gdriveUrl.replace("/view", "/preview")
  }

  const totalParams = parameters.length
  const passCount = summary?.pass ?? parameters.filter(p => p.status === "pass").length
  const failCount = summary?.fail ?? parameters.filter(p => p.status === "fail").length

  return (
    <div className={cn(
      "flex gap-0 border rounded-xl overflow-hidden bg-white",
      fullscreen ? "fixed inset-4 z-50 shadow-2xl" : "h-[520px]"
    )}>
      {/* Left: PDF Viewer */}
      <div className="w-1/2 border-r flex flex-col bg-slate-50">
        {/* PDF Header */}
        <div className="flex items-center justify-between px-3 py-2 border-b bg-white">
          <div className="flex items-center gap-2 min-w-0">
            <FileText className="h-3.5 w-3.5 text-brand flex-shrink-0" />
            <span className="text-xs font-semibold text-slate-700 truncate">{fileName || "Document"}</span>
          </div>
          <div className="flex items-center gap-1">
            {(gdriveUrl || gdriveFileId) && (
              <Button size="sm" variant="ghost" className="h-6 w-6 p-0"
                onClick={() => window.open(gdriveUrl || `https://drive.google.com/file/d/${gdriveFileId}/view`, "_blank")}>
                <ExternalLink className="h-3 w-3 text-slate-400" />
              </Button>
            )}
            <Button size="sm" variant="ghost" className="h-6 w-6 p-0"
              onClick={() => setFullscreen(f => !f)}>
              {fullscreen ? <Minimize2 className="h-3 w-3 text-slate-400" /> : <Maximize2 className="h-3 w-3 text-slate-400" />}
            </Button>
          </div>
        </div>

        {/* PDF Content */}
        {pdfSrc ? (
          <iframe
            src={pdfSrc}
            className="flex-1 w-full"
            style={{ border: "none" }}
            title="Document Preview"
          />
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-400">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto mb-3 text-slate-200" />
              <p className="text-sm font-medium">No preview available</p>
              <p className="text-xs mt-1">Upload a PDF to see preview</p>
            </div>
          </div>
        )}
      </div>

      {/* Right: Extracted Data */}
      <div className="w-1/2 flex flex-col">
        {/* Summary Header */}
        <div className="px-4 py-3 border-b bg-white">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="text-sm font-bold text-slate-800">
                {mode === "rfq" ? "Extracted Requirements" : "Extracted Specs"}
              </h3>
              <p className="text-[11px] text-slate-400">
                {totalParams} parameters from {fileName || "document"}
              </p>
            </div>
            {summary?.compliance_score !== undefined && (
              <ScoreRing score={summary.compliance_score} size={44} strokeWidth={4} />
            )}
          </div>

          {/* Quick stats */}
          <div className="flex items-center gap-3 text-[10px]">
            {summary?.oem_name && (
              <span className="text-slate-500">OEM: <strong className="text-slate-700">{summary.oem_name}</strong></span>
            )}
            {summary?.customer_name && (
              <span className="text-slate-500">Customer: <strong className="text-slate-700">{summary.customer_name}</strong></span>
            )}
            {summary?.category && (
              <Badge variant="default" className="text-[9px] px-1.5 py-0">{summary.category}</Badge>
            )}
            <span className="flex items-center gap-1 text-emerald-600 font-semibold">
              <CheckCircle2 className="h-2.5 w-2.5" />{passCount}
            </span>
            {failCount > 0 && (
              <span className="flex items-center gap-1 text-red-500 font-semibold">
                <XCircle className="h-2.5 w-2.5" />{failCount}
              </span>
            )}
          </div>
        </div>

        {/* Parameter Sections */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {Object.entries(grouped).map(([section, params]) => {
            const isExpanded = expandedSections.has(section)
            return (
              <div key={section} className="border-b border-slate-100 last:border-0">
                <button
                  onClick={() => toggleSection(section)}
                  className="w-full flex items-center justify-between px-4 py-2 text-left hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    {isExpanded
                      ? <ChevronDown className="h-3 w-3 text-slate-400" />
                      : <ChevronRight className="h-3 w-3 text-slate-400" />}
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{section}</span>
                    <span className="text-[10px] text-slate-300">{params.length}</span>
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-2">
                    <table className="w-full text-[11px]">
                      <tbody>
                        {params.map((p, i) => (
                          <tr key={p.code || i} className={cn(
                            "border-b border-slate-50 last:border-0",
                            i % 2 === 0 ? "" : "bg-slate-50/30"
                          )}>
                            <td className="py-1.5 pr-2 font-medium text-slate-700 w-[45%]">
                              {p.name || p.parameter}
                              {p.code && <span className="block text-[9px] text-slate-300 font-mono">{p.code}</span>}
                            </td>
                            <td className="py-1.5 px-2 text-right font-semibold text-slate-800 tabular-nums w-[30%]">
                              {p.value || p.required_value}
                              {p.unit && <span className="text-slate-400 font-normal ml-1">{p.unit}</span>}
                            </td>
                            <td className="py-1.5 pl-2 w-[12%]">
                              {p.status && (
                                <div className="flex items-center justify-center">
                                  {statusIcon(p.status)}
                                </div>
                              )}
                            </td>
                            <td className="py-1.5 pl-1 w-[13%]">
                              {p.confidence !== undefined && (
                                <div className="flex items-center gap-1">
                                  <Progress value={(p.confidence || 0) * 100} className="h-1 w-8" />
                                  <span className="text-[9px] text-slate-400">{Math.round((p.confidence || 0) * 100)}%</span>
                                </div>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )
          })}

          {parameters.length === 0 && (
            <div className="flex items-center justify-center h-full text-slate-400 text-sm">
              No parameters extracted yet
            </div>
          )}
        </div>
      </div>

      {/* Fullscreen overlay backdrop */}
      {fullscreen && (
        <div className="fixed inset-0 bg-black/50 -z-10" onClick={() => setFullscreen(false)} />
      )}
    </div>
  )
}
