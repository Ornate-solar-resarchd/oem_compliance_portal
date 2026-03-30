"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { getRFQs, uploadRFQ, uploadRFQMulti, createRFQ } from "@/lib/api"
import { DriveFetcherModal } from "@/components/shared/drive-fetcher-modal"
import { SplitDocumentViewer } from "@/components/shared/split-document-viewer"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "@/components/ui/dialog"
import { Progress } from "@/components/ui/progress"
import {
  Upload, FileText, Calendar, ClipboardList, Loader2, CheckCircle2,
  FileUp, File, X, AlertCircle, Sparkles, ArrowRight, HardDrive
} from "lucide-react"

interface Requirement {
  parameter: string
  code: string
  required_value: string
  unit: string
}

interface RFQ {
  id: string
  customer_name: string
  project_name: string
  status: string
  created_at: string
  requirements: Requirement[]
  source_file?: string
}

export default function RFQManagerPage() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [rfqs, setRfqs] = useState<RFQ[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [driveModalOpen, setDriveModalOpen] = useState(false)

  // Upload form state
  const [customerName, setCustomerName] = useState("")
  const [projectName, setProjectName] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [dragOver, setDragOver] = useState(false)

  // Extraction state
  const [uploading, setUploading] = useState(false)
  const [extractionProgress, setExtractionProgress] = useState(0)
  const [extractionPhase, setExtractionPhase] = useState("")
  const [extractedData, setExtractedData] = useState<any>(null)
  const [extractionError, setExtractionError] = useState("")

  const fetchRFQs = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getRFQs()
      setRfqs(data.items || [])
    } catch (err) {
      console.error("Failed to fetch RFQs:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchRFQs() }, [fetchRFQs])

  const resetForm = () => {
    setCustomerName("")
    setProjectName("")
    setFile(null)
    setFiles([])
    setExtractionProgress(0)
    setExtractionPhase("")
    setExtractedData(null)
    setExtractionError("")
    setUploading(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      f => f.type === "application/pdf" || f.name.match(/\.(pdf|xlsx?|csv)$/i)
    )
    if (droppedFiles.length > 0) {
      setFiles(prev => [...prev, ...droppedFiles])
      setFile(droppedFiles[0]) // keep first file for backward compat
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []).filter(
      f => f.type === "application/pdf" || f.name.match(/\.(pdf|xlsx?|csv)$/i)
    )
    if (selected.length > 0) {
      setFiles(prev => [...prev, ...selected])
      if (!file) setFile(selected[0])
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => {
      const next = prev.filter((_, i) => i !== index)
      if (next.length === 0) setFile(null)
      else setFile(next[0])
      return next
    })
  }

  const handleUpload = async () => {
    const uploadFiles = files.length > 0 ? files : file ? [file] : []
    if (uploadFiles.length === 0 || !customerName.trim() || !projectName.trim()) return

    try {
      setUploading(true)
      setExtractionError("")
      setExtractedData(null)

      // Phase 1: Upload
      setExtractionPhase(`Uploading ${uploadFiles.length} compliance sheet(s)...`)
      setExtractionProgress(15)
      await new Promise(r => setTimeout(r, 400))

      // Phase 2: Parsing
      setExtractionPhase("Parsing all documents...")
      setExtractionProgress(30)
      await new Promise(r => setTimeout(r, 500))

      // Phase 3: Send ALL files in ONE request
      setExtractionPhase(`Extracting from ${uploadFiles.length} file(s) — matching 344 compliance parameters...`)
      setExtractionProgress(50)

      let result: any
      if (uploadFiles.length > 1) {
        // Multi-file: one API call, one RFQ
        result = await uploadRFQMulti(uploadFiles, customerName, projectName)
      } else {
        // Single file
        result = await uploadRFQ(uploadFiles[0], customerName, projectName)
      }

      // Phase 4: Done
      setExtractionPhase("Cross-referencing with compliance standards...")
      setExtractionProgress(85)
      await new Promise(r => setTimeout(r, 400))

      setExtractionPhase(`Done! ${result.requirements_extracted} parameters from ${uploadFiles.length} file(s)`)
      setExtractionProgress(100)
      setExtractedData(result)

    } catch (err: any) {
      setExtractionError(err.message || "Upload failed")
      setExtractionProgress(0)
      setExtractionPhase("")
    } finally {
      setUploading(false)
    }
  }

  const handleDone = () => {
    setDialogOpen(false)
    resetForm()
    fetchRFQs()
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric", month: "short", day: "numeric",
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">RFQ Manager</h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload RFQ documents and AI will extract compliance requirements automatically
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setDriveModalOpen(true)}>
            <HardDrive className="mr-2 h-4 w-4" />
            Fetch from Drive
          </Button>
          <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm() }}>
          <DialogTrigger asChild>
            <Button>
              <Upload className="mr-2 h-4 w-4" />
              Upload RFQ
            </Button>
          </DialogTrigger>
          <DialogContent className={cn("max-h-[90vh] overflow-y-auto", extractedData ? "max-w-5xl" : "max-w-2xl")}>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-brand" />
                Upload RFQ Document
              </DialogTitle>
              <DialogDescription>
                Upload a PDF or Excel file — AI will extract technical requirements automatically
              </DialogDescription>
            </DialogHeader>

            {/* Extraction Result — Split View */}
            {extractedData ? (
              <div className="space-y-3 pt-2">
                <SplitDocumentViewer
                  localFile={file}
                  fileName={extractedData.file_name}
                  parameters={extractedData.requirements || []}
                  mode="rfq"
                  summary={{
                    customer_name: extractedData.customer_name,
                    project_name: extractedData.project_name,
                    total: extractedData.requirements_extracted,
                  }}
                />
                <div className="flex gap-3 pt-1">
                  <Button variant="outline" className="flex-1" onClick={handleDone}>
                    Close
                  </Button>
                  <Button className="flex-1" onClick={() => { handleDone(); router.push(`/rfq/${extractedData.rfq_id}`) }}>
                    View Details
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-5 pt-2">
                {/* Customer Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Customer Name</label>
                    <Input
                      placeholder="e.g., NTPC, BSPGCL, Eagle Infra"
                      value={customerName}
                      onChange={e => setCustomerName(e.target.value)}
                      disabled={uploading}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Project Name</label>
                    <Input
                      placeholder="e.g., Bihar BESS 400MWh"
                      value={projectName}
                      onChange={e => setProjectName(e.target.value)}
                      disabled={uploading}
                    />
                  </div>
                </div>

                {/* File Upload Zone — Multiple Files */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">
                    Compliance Sheets <span className="text-slate-400 font-normal">(upload multiple: Battery, PCS, EMS, HVAC, etc.)</span>
                  </label>
                  <div
                    onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                    onClick={() => !uploading && fileInputRef.current?.click()}
                    className={cn(
                      "relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all",
                      dragOver ? "border-brand bg-brand/5" : files.length > 0 ? "border-emerald-300 bg-emerald-50/50" : "border-slate-200 hover:border-slate-300 bg-slate-50",
                      uploading && "pointer-events-none opacity-60"
                    )}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.xls,.xlsx,.csv"
                      multiple
                      className="hidden"
                      onChange={handleFileSelect}
                      disabled={uploading}
                    />

                    {files.length > 0 ? (
                      <div className="space-y-2">
                        {files.map((f, i) => (
                          <div key={f.name + i} className="flex items-center gap-3 bg-white rounded-lg p-2.5 border border-emerald-200">
                            <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0">
                              <File className="h-4 w-4 text-emerald-600" />
                            </div>
                            <div className="text-left flex-1 min-w-0">
                              <div className="text-xs font-semibold text-emerald-700 truncate">{f.name}</div>
                              <div className="text-[10px] text-emerald-500">{(f.size / 1024).toFixed(1)} KB</div>
                            </div>
                            {!uploading && (
                              <button
                                onClick={e => { e.stopPropagation(); removeFile(i) }}
                                className="p-1 rounded-full hover:bg-red-100 transition-colors shrink-0"
                              >
                                <X className="h-3.5 w-3.5 text-red-400" />
                              </button>
                            )}
                          </div>
                        ))}
                        {!uploading && (
                          <div className="text-xs text-emerald-600 font-medium pt-1">
                            + Drop or click to add more files
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mx-auto">
                          <FileUp className="h-6 w-6 text-slate-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-slate-600">
                            Drop compliance sheets here or <span className="text-brand font-semibold">browse</span>
                          </div>
                          <div className="text-xs text-slate-400 mt-1">
                            Upload multiple files: Battery, PCS, EMS, HVAC, Guarantees — PDF/Excel
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Extraction Progress */}
                {uploading && (
                  <div className="space-y-3 p-4 bg-slate-50 rounded-lg border">
                    <div className="flex items-center gap-2">
                      {extractionProgress < 100 ? (
                        <Loader2 className="h-4 w-4 animate-spin text-brand" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                      )}
                      <span className="text-sm font-medium text-slate-700">{extractionPhase}</span>
                    </div>
                    <Progress value={extractionProgress} className="h-2" />
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <Sparkles className="h-3 w-3" />
                      AI-powered extraction in progress...
                    </div>
                  </div>
                )}

                {/* Error */}
                {extractionError && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                    <span className="text-sm text-red-600">{extractionError}</span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-1">
                  <Button variant="outline" className="flex-1" onClick={() => setDialogOpen(false)} disabled={uploading}>
                    Cancel
                  </Button>
                  <Button
                    className="flex-1"
                    disabled={(files.length === 0 && !file) || !customerName.trim() || !projectName.trim() || uploading}
                    onClick={handleUpload}
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Extracting...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Upload & Extract
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Drive Fetcher Modal for RFQ */}
      <DriveFetcherModal
        open={driveModalOpen}
        onClose={() => setDriveModalOpen(false)}
        mode="rfq"
        customerName={customerName}
        projectName={projectName}
        onExtracted={async () => {
          setDriveModalOpen(false)
          const data = await getRFQs()
          setRfqs(data.items || [])
        }}
      />

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-brand/10 flex items-center justify-center">
                <FileText className="h-5 w-5 text-brand" />
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">{rfqs.length}</div>
                <div className="text-xs text-slate-500">Total RFQs</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">{rfqs.filter(r => r.status === "active").length}</div>
                <div className="text-xs text-slate-500">Active</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <ClipboardList className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">
                  {rfqs.reduce((sum, r) => sum + (r.requirements?.length || 0), 0)}
                </div>
                <div className="text-xs text-slate-500">Total Requirements</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* RFQ List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
        </div>
      ) : rfqs.length === 0 ? (
        <Card className="py-16">
          <CardContent className="flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
              <FileUp className="h-8 w-8 text-slate-300" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700">No RFQs yet</h3>
            <p className="text-sm text-slate-400 mt-1 max-w-sm">
              Upload your first RFQ document and AI will extract technical requirements for compliance matching.
            </p>
            <Button className="mt-6" onClick={() => setDialogOpen(true)}>
              <Upload className="mr-2 h-4 w-4" />
              Upload First RFQ
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {rfqs.map(rfq => (
            <Card
              key={rfq.id}
              className="cursor-pointer transition-all hover:shadow-md hover:border-brand/30 group"
              onClick={() => router.push(`/rfq/${rfq.id}`)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-base group-hover:text-brand transition-colors">
                      {rfq.customer_name}
                    </CardTitle>
                    <CardDescription>{rfq.project_name}</CardDescription>
                  </div>
                  <Badge variant={rfq.status === "active" ? "pass" : "default"}>
                    {rfq.status === "active" ? "Active" : rfq.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <ClipboardList className="h-3.5 w-3.5" />
                    <span className="font-medium text-slate-700">{rfq.requirements?.length || 0}</span>
                    <span>requirements</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{formatDate(rfq.created_at)}</span>
                  </div>
                </div>
                {rfq.source_file && (
                  <div className="flex items-center gap-1.5 mt-3 text-xs text-slate-400">
                    <File className="h-3 w-3" />
                    <span>{rfq.source_file}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
