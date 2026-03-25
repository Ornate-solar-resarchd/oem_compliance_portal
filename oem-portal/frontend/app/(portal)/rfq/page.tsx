"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { getRFQs, uploadRFQ, createRFQ } from "@/lib/api"
import { DriveFetcherModal } from "@/components/shared/drive-fetcher-modal"
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
    setExtractionProgress(0)
    setExtractionPhase("")
    setExtractedData(null)
    setExtractionError("")
    setUploading(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.type === "application/pdf" || f.name.match(/\.(pdf|xlsx?|csv)$/i))) {
      setFile(f)
    }
  }

  const handleUpload = async () => {
    if (!file || !customerName.trim() || !projectName.trim()) return

    try {
      setUploading(true)
      setExtractionError("")
      setExtractedData(null)

      // Phase 1: Upload
      setExtractionPhase("Uploading document...")
      setExtractionProgress(10)
      await new Promise(r => setTimeout(r, 400))

      // Phase 2: Parsing
      setExtractionPhase("Parsing document structure...")
      setExtractionProgress(25)
      await new Promise(r => setTimeout(r, 600))

      // Phase 3: AI extraction
      setExtractionPhase("AI extracting technical requirements...")
      setExtractionProgress(45)
      await new Promise(r => setTimeout(r, 800))

      // Actually upload to backend
      const result = await uploadRFQ(file, customerName, projectName)

      // Phase 4: Validating
      setExtractionPhase("Validating extracted parameters...")
      setExtractionProgress(75)
      await new Promise(r => setTimeout(r, 500))

      // Phase 5: Cross-referencing
      setExtractionPhase("Cross-referencing with compliance standards...")
      setExtractionProgress(90)
      await new Promise(r => setTimeout(r, 400))

      // Done
      setExtractionPhase("Extraction complete!")
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
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-brand" />
                Upload RFQ Document
              </DialogTitle>
              <DialogDescription>
                Upload a PDF or Excel file — AI will extract technical requirements automatically
              </DialogDescription>
            </DialogHeader>

            {/* Extraction Result */}
            {extractedData ? (
              <div className="space-y-4 pt-2">
                <div className="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <CheckCircle2 className="h-6 w-6 text-emerald-500 flex-shrink-0" />
                  <div>
                    <div className="text-sm font-semibold text-emerald-700">
                      {extractedData.requirements_extracted} requirements extracted
                    </div>
                    <div className="text-xs text-emerald-600 mt-0.5">
                      from {extractedData.file_name}
                    </div>
                  </div>
                </div>

                {/* Show extracted requirements */}
                <div className="border rounded-lg overflow-hidden">
                  <div className="bg-slate-50 px-4 py-2.5 border-b">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Extracted Requirements
                    </span>
                  </div>
                  <div className="divide-y max-h-[300px] overflow-y-auto scrollbar-thin">
                    {(extractedData.requirements || []).map((req: Requirement, i: number) => (
                      <div key={i} className="px-4 py-2.5 flex items-center justify-between hover:bg-slate-50 transition-colors">
                        <div>
                          <div className="text-sm font-medium text-slate-700">{req.parameter}</div>
                          <div className="text-xs text-slate-400 font-mono">{req.code}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-slate-900">
                            {req.required_value} {req.unit && <span className="text-slate-400 font-normal">{req.unit}</span>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <Button variant="outline" className="flex-1" onClick={handleDone}>
                    Close
                  </Button>
                  <Button className="flex-1" onClick={() => { handleDone(); router.push(`/rfq/${extractedData.rfq_id}`) }}>
                    View Comparison
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

                {/* File Upload Zone */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">RFQ Document</label>
                  <div
                    onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                    onClick={() => !uploading && fileInputRef.current?.click()}
                    className={cn(
                      "relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all",
                      dragOver ? "border-brand bg-brand/5" : file ? "border-emerald-300 bg-emerald-50" : "border-slate-200 hover:border-slate-300 bg-slate-50",
                      uploading && "pointer-events-none opacity-60"
                    )}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.xls,.xlsx,.csv"
                      className="hidden"
                      onChange={e => setFile(e.target.files?.[0] || null)}
                      disabled={uploading}
                    />

                    {file ? (
                      <div className="flex items-center justify-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                          <File className="h-5 w-5 text-emerald-600" />
                        </div>
                        <div className="text-left">
                          <div className="text-sm font-semibold text-emerald-700">{file.name}</div>
                          <div className="text-xs text-emerald-500">{(file.size / 1024).toFixed(1)} KB</div>
                        </div>
                        {!uploading && (
                          <button
                            onClick={e => { e.stopPropagation(); setFile(null) }}
                            className="ml-2 p-1 rounded-full hover:bg-emerald-200 transition-colors"
                          >
                            <X className="h-4 w-4 text-emerald-600" />
                          </button>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mx-auto">
                          <FileUp className="h-6 w-6 text-slate-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-slate-600">
                            Drop your RFQ document here or <span className="text-brand font-semibold">browse</span>
                          </div>
                          <div className="text-xs text-slate-400 mt-1">
                            Supports PDF, Excel (.xls, .xlsx), CSV — Max 50MB
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
                    disabled={!file || !customerName.trim() || !projectName.trim() || uploading}
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
