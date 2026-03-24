"use client"

import { useState, useCallback } from "react"
import { searchDrive, fetchAndExtract, uploadRFQ } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from "@/components/ui/dialog"
import {
  Search, Loader2, FileText, Download, CloudDownload, CheckCircle2,
  AlertTriangle, HardDrive, Filter, X, ExternalLink,
} from "lucide-react"

/* ── Types ── */
interface DriveFile {
  name: string
  url: string
  downloadUrl: string
  type: string
  mimeType: string
  size: string
  lastUpdated: string
  id: string
  iconUrl: string
}

interface DriveFetcherModalProps {
  open: boolean
  onClose: () => void
  /** "datasheet" for OEM Library, "rfq" for RFQ Manager */
  mode: "datasheet" | "rfq"
  /** For datasheet mode: pre-fill OEM name */
  defaultOemName?: string
  /** For datasheet mode: pre-fill category */
  defaultCategory?: string
  /** Callback when extraction is complete */
  onExtracted?: (result: any) => void
  /** For RFQ mode: customer name */
  customerName?: string
  /** For RFQ mode: project name */
  projectName?: string
}

const FILE_TYPES = [
  { value: "", label: "All" },
  { value: "pdf", label: "PDF" },
  { value: "xlsx", label: "Excel" },
  { value: "doc", label: "Docs" },
  { value: "sheet", label: "Sheets" },
  { value: "csv", label: "CSV" },
]

const CATEGORIES = ["Cell", "DC Block", "PCS", "EMS"]

export function DriveFetcherModal({
  open, onClose, mode, defaultOemName = "", defaultCategory = "Cell",
  onExtracted, customerName = "", projectName = "",
}: DriveFetcherModalProps) {
  const [query, setQuery] = useState("")
  const [fileType, setFileType] = useState("")
  const [results, setResults] = useState<DriveFile[]>([])
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState("")

  // Extraction state
  const [extractingId, setExtractingId] = useState<string | null>(null)
  const [extractResult, setExtractResult] = useState<any>(null)

  // Form fields for datasheet mode
  const [oemName, setOemName] = useState(defaultOemName)
  const [modelName, setModelName] = useState("")
  const [category, setCategory] = useState(defaultCategory)

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return
    setSearching(true)
    setError("")
    setResults([])
    setExtractResult(null)
    try {
      const data = await searchDrive(query.trim(), fileType)
      if (data.success) {
        setResults(data.results || [])
      } else {
        setError(data.error || "Search failed")
      }
    } catch (e: any) {
      setError(e.message || "Search failed — check if GDRIVE_FETCHER_URL is configured")
    } finally {
      setSearching(false)
    }
  }, [query, fileType])

  const handleExtract = useCallback(async (file: DriveFile) => {
    setExtractingId(file.id)
    setExtractResult(null)
    setError("")
    try {
      if (mode === "datasheet") {
        const result = await fetchAndExtract({
          file_id: file.id,
          file_name: file.name,
          oem_name: oemName || "Unknown",
          model_name: modelName || file.name.replace(/\.[^.]+$/, ""),
          category,
        })
        setExtractResult(result)
        onExtracted?.(result)
      } else {
        // RFQ mode — download file content and upload as RFQ
        // For RFQ, we use the existing upload endpoint with the Drive file
        const result = await fetchAndExtract({
          file_id: file.id,
          file_name: file.name,
          oem_name: customerName || "Unknown",
          model_name: projectName || file.name.replace(/\.[^.]+$/, ""),
          category: "RFQ",
        })
        setExtractResult(result)
        onExtracted?.(result)
      }
    } catch (e: any) {
      setError(e.message || "Extraction failed")
    } finally {
      setExtractingId(null)
    }
  }, [mode, oemName, modelName, category, customerName, projectName, onExtracted])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base">
            <HardDrive className="w-5 h-5 text-brand" />
            {mode === "datasheet" ? "Fetch Datasheet from Company Drive" : "Fetch RFQ from Company Drive"}
          </DialogTitle>
          <DialogDescription>
            Search your company Google Drive and extract technical data automatically
          </DialogDescription>
        </DialogHeader>

        {/* Search Bar */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder={mode === "datasheet" ? "Search datasheets... (e.g. CATL 280Ah)" : "Search RFQ documents..."}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="pl-10"
              autoFocus
            />
          </div>
          <Button onClick={handleSearch} disabled={searching || !query.trim()}>
            {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          </Button>
        </div>

        {/* File Type Filter */}
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          {FILE_TYPES.map((ft) => (
            <button
              key={ft.value}
              onClick={() => setFileType(ft.value)}
              className={cn(
                "text-xs font-medium px-2.5 py-1 rounded-lg border transition-all",
                fileType === ft.value
                  ? "bg-brand text-white border-brand"
                  : "bg-white text-slate-500 border-slate-200 hover:border-brand/30"
              )}
            >
              {ft.label}
            </button>
          ))}
        </div>

        {/* Datasheet mode: OEM/Model/Category fields */}
        {mode === "datasheet" && (
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-[10px] font-semibold text-slate-500 uppercase mb-1 block">OEM Name</label>
              <Input
                placeholder="e.g. CATL"
                value={oemName}
                onChange={(e) => setOemName(e.target.value)}
                className="h-8 text-sm"
              />
            </div>
            <div>
              <label className="text-[10px] font-semibold text-slate-500 uppercase mb-1 block">Model Name</label>
              <Input
                placeholder="e.g. LFP-280AH"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="h-8 text-sm"
              />
            </div>
            <div>
              <label className="text-[10px] font-semibold text-slate-500 uppercase mb-1 block">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="h-8 w-full px-2 text-sm border rounded-lg bg-white focus:border-brand focus:ring-1 focus:ring-brand/20 focus:outline-none"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError("")} className="ml-auto"><X className="w-3.5 h-3.5" /></button>
          </div>
        )}

        {/* Success */}
        {extractResult && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            {extractResult.message}
          </div>
        )}

        {/* Results */}
        <div className="flex-1 overflow-y-auto space-y-2 min-h-0">
          {searching ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin mb-3" />
              <p className="text-sm">Searching your Google Drive...</p>
            </div>
          ) : results.length === 0 && query ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <FileText className="w-10 h-10 mb-3 text-slate-200" />
              <p className="text-sm font-medium text-slate-500">No files found</p>
              <p className="text-xs mt-1">Try a different search query</p>
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <HardDrive className="w-10 h-10 mb-3 text-slate-200" />
              <p className="text-sm font-medium text-slate-500">Search your company Drive</p>
              <p className="text-xs mt-1">Type a filename and press Enter or click Search</p>
            </div>
          ) : (
            <>
              <div className="text-xs text-slate-400 mb-2">{results.length} files found</div>
              {results.map((file) => (
                <div
                  key={file.id}
                  className={cn(
                    "flex items-center gap-3 p-3 rounded-lg border transition-all",
                    extractingId === file.id
                      ? "border-brand/30 bg-brand-50/50"
                      : "border-slate-200 hover:border-slate-300 hover:shadow-sm"
                  )}
                >
                  <span className="text-2xl flex-shrink-0">{file.iconUrl}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-slate-800 truncate">{file.name}</div>
                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                      <Badge variant="outline" className="text-[10px] px-1.5 py-0">{file.type}</Badge>
                      <span>{file.size}</span>
                      <span>{new Date(file.lastUpdated).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <a
                      href={file.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-slate-400 hover:text-brand transition-colors p-1.5"
                      title="Open in Drive"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                    <Button
                      size="sm"
                      variant={extractingId === file.id ? "default" : "outline"}
                      disabled={extractingId !== null}
                      onClick={() => handleExtract(file)}
                      className="text-xs gap-1.5"
                    >
                      {extractingId === file.id ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          Extracting...
                        </>
                      ) : (
                        <>
                          <CloudDownload className="w-3.5 h-3.5" />
                          Fetch & Extract
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
