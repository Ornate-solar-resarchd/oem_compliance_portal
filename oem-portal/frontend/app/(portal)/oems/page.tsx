"use client";

import { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  getOEMs,
  createOEM,
  getComponents,
  getComponentParams,
  uploadDatasheet,
  getDashboardCharts,
} from "@/lib/api";
import { DriveFetcherModal } from "@/components/shared/drive-fetcher-modal";
import { SplitDocumentViewer } from "@/components/shared/split-document-viewer";
import { cn, scoreColor } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { ScoreRing } from "@/components/shared/score-ring";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Cell as RCell,
  CartesianGrid,
} from "recharts";
import {
  Search,
  Plus,
  Globe,
  Mail,
  Building2,
  CheckCircle2,
  XCircle,
  X,
  Upload,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Loader2,
  AlertTriangle,
  FileText,
  Download,
  Zap,
  Thermometer,
  Shield,
  Activity,
  Box,
  FileUp,
  Eye,
  HardDrive,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface OEM {
  id: string;
  name: string;
  country_of_origin: string;
  is_approved: boolean;
  score: number;
  model_count: number;
  avg_compliance_score: number;
  website: string;
  contact_email: string;
}

interface Component {
  id: string;
  oem_id: string;
  oem_name: string;
  model_name: string;
  sku: string;
  component_type_name: string;
  fill_rate: number;
  compliance_score: number;
  is_active: boolean;
  pass: number;
  fail: number;
  waived: number;
  datasheet: string;
  gdrive_url?: string;
  gdrive_file_id?: string;
}

interface Param {
  code: string;
  name: string;
  value: string;
  unit: string;
  section: string;
  verified?: boolean;
}

/* ------------------------------------------------------------------ */
/*  OEM Config                                                         */
/* ------------------------------------------------------------------ */

const OEM_INFO: Record<string, { color: string; website: string; logo: string }> = {
  CATL:    { color: "from-blue-500 to-blue-600",     website: "https://catl.com",        logo: "C" },
  Lishen:  { color: "from-emerald-500 to-emerald-600", website: "https://lishen.com.cn", logo: "L" },
  BYD:     { color: "from-red-500 to-red-600",       website: "https://byd.com",          logo: "B" },
  HiTHIUM: { color: "from-purple-500 to-purple-600", website: "https://hithium.com",      logo: "H" },
  SVOLT:   { color: "from-amber-500 to-amber-600",   website: "https://www.svolt.cn/en",  logo: "S" },
};

const CATEGORIES = ["Cell", "DC Block", "PCS", "EMS"] as const;

const SECTION_ICON: Record<string, React.ComponentType<{ className?: string }>> = {
  Electrical: Zap,
  Physical: Box,
  Thermal: Thermometer,
  Safety: Shield,
  Performance: Activity,
};

const SECTION_COLOR: Record<string, string> = {
  Electrical: "text-amber-500",
  Physical: "text-blue-500",
  Thermal: "text-orange-500",
  Safety: "text-red-500",
  Performance: "text-emerald-500",
};

const BAR_COLORS = [
  "#3b82f6", "#6366f1", "#8b5cf6", "#a78bfa",
  "#c4b5fd", "#818cf8", "#6d28d9", "#4f46e5",
];

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function groupParams(params: Param[]) {
  const map: Record<string, Param[]> = {};
  params.forEach((p) => {
    const s = p.section || "General";
    if (!map[s]) map[s] = [];
    map[s].push(p);
  });
  return map;
}

function radarData(params: Param[]) {
  const sections = ["Electrical", "Physical", "Thermal", "Safety", "Performance"];
  return sections.map((s) => {
    const sp = params.filter((p) => (p.section || "").includes(s));
    const total = sp.length;
    const pass = sp.filter((p) => p.verified !== false).length;
    return { section: s, score: total > 0 ? Math.round((pass / total) * 100) : 0 };
  });
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function OEMsPage() {
  const router = useRouter();

  /* ── Data ── */
  const [oems, setOems] = useState<OEM[]>([]);
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);

  /* ── Filters ── */
  const [search, setSearch] = useState("");
  const [selectedOEM, setSelectedOEM] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  /* ── Model expand ── */
  const [expandedModel, setExpandedModel] = useState<string | null>(null);
  const [modelParams, setModelParams] = useState<Record<string, Param[]>>({});
  const [loadingParams, setLoadingParams] = useState<Record<string, boolean>>({});

  /* ── Add OEM Dialog ── */
  const [addOEMOpen, setAddOEMOpen] = useState(false);
  const [oemForm, setOemForm] = useState({
    name: "",
    country_of_origin: "",
    website: "",
    contact_email: "",
  });
  const [submittingOEM, setSubmittingOEM] = useState(false);

  /* ── Upload Dialog ── */
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploadOEM, setUploadOEM] = useState("");
  const [uploadNewOEM, setUploadNewOEM] = useState("");
  const [uploadModel, setUploadModel] = useState("");
  const [uploadCategory, setUploadCategory] = useState<string>("Cell");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropRef = useRef<HTMLDivElement>(null);

  /* ── Drive Fetcher ── */
  const [driveModalOpen, setDriveModalOpen] = useState(false);

  /* ── Fetch Data ── */
  useEffect(() => {
    async function load() {
      try {
        const [oemRes, compRes] = await Promise.all([getOEMs(), getComponents()]);
        setOems(oemRes.items ?? []);
        setComponents(compRes.items ?? []);
      } catch (e) {
        console.error("Failed to load data", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* ── Derived ── */
  const filteredComponents = useMemo(() => {
    let list = components.filter((c) => c.is_active);
    if (selectedOEM) list = list.filter((c) => c.oem_name === selectedOEM);
    if (selectedCategory !== "All")
      list = list.filter((c) => c.component_type_name === selectedCategory);
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (c) =>
          c.model_name.toLowerCase().includes(q) ||
          c.oem_name.toLowerCase().includes(q) ||
          c.sku.toLowerCase().includes(q)
      );
    }
    return list;
  }, [components, selectedOEM, selectedCategory, search]);

  const groupedByOEM = useMemo(() => {
    const map = new Map<string, Component[]>();
    for (const c of filteredComponents) {
      if (!map.has(c.oem_name)) map.set(c.oem_name, []);
      map.get(c.oem_name)!.push(c);
    }
    return map;
  }, [filteredComponents]);

  /* ── Handlers ── */

  async function handleAddOEM() {
    if (!oemForm.name.trim()) return;
    setSubmittingOEM(true);
    try {
      await createOEM(oemForm);
      const res = await getOEMs();
      setOems(res.items ?? []);
      setAddOEMOpen(false);
      setOemForm({ name: "", country_of_origin: "", website: "", contact_email: "" });
    } catch (e) {
      console.error("Failed to create OEM", e);
    } finally {
      setSubmittingOEM(false);
    }
  }

  async function toggleModelExpand(id: string) {
    if (expandedModel === id) {
      setExpandedModel(null);
      return;
    }
    setExpandedModel(id);
    if (modelParams[id]) return;
    setLoadingParams((p) => ({ ...p, [id]: true }));
    try {
      const d = await getComponentParams(id);
      setModelParams((p) => ({ ...p, [id]: d.items || [] }));
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingParams((p) => ({ ...p, [id]: false }));
    }
  }

  async function handleUpload() {
    if (!uploadFile) return;
    const oemName = uploadOEM === "__new__" ? uploadNewOEM : uploadOEM;
    if (!oemName.trim() || !uploadModel.trim()) return;
    setUploading(true);
    setUploadProgress(0);

    // Simulate progress ticks
    const interval = setInterval(() => {
      setUploadProgress((p) => Math.min(p + Math.random() * 15, 90));
    }, 400);

    try {
      const result = await uploadDatasheet(uploadFile, oemName, uploadModel, uploadCategory);
      clearInterval(interval);
      setUploadProgress(100);
      setUploadResult(result);
      // Refresh data
      const [oemRes, compRes] = await Promise.all([getOEMs(), getComponents()]);
      setOems(oemRes.items ?? []);
      setComponents(compRes.items ?? []);
    } catch (e) {
      console.error("Upload failed", e);
      clearInterval(interval);
    } finally {
      setUploading(false);
    }
  }

  function resetUploadDialog() {
    setUploadOEM("");
    setUploadNewOEM("");
    setUploadModel("");
    setUploadCategory("Cell");
    setUploadFile(null);
    setUploadProgress(0);
    setUploadResult(null);
    setUploading(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer.files;
    if (files.length > 0) setUploadFile(files[0]);
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
  }

  /* ── Loading ── */
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <p className="text-muted-foreground text-sm">Loading OEM library...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ================================================================ */}
      {/*  1. TOP BAR                                                      */}
      {/* ================================================================ */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex-1 min-w-0">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">OEM Library</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Manage manufacturers, models, and technical specifications
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search OEMs, models, SKU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 w-64"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          {/* Add OEM Dialog */}
          <Dialog open={addOEMOpen} onOpenChange={setAddOEMOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Add OEM
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add New OEM</DialogTitle>
                <DialogDescription>
                  Register a new Original Equipment Manufacturer in the system.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 pt-2">
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Company Name *</label>
                  <Input
                    placeholder="e.g., CATL, BYD, Samsung SDI"
                    value={oemForm.name}
                    onChange={(e) => setOemForm((f) => ({ ...f, name: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Country of Origin</label>
                  <Input
                    placeholder="e.g., China, South Korea"
                    value={oemForm.country_of_origin}
                    onChange={(e) => setOemForm((f) => ({ ...f, country_of_origin: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Website</label>
                  <Input
                    placeholder="https://..."
                    value={oemForm.website}
                    onChange={(e) => setOemForm((f) => ({ ...f, website: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Contact Email</label>
                  <Input
                    placeholder="contact@oem.com"
                    type="email"
                    value={oemForm.contact_email}
                    onChange={(e) => setOemForm((f) => ({ ...f, contact_email: e.target.value }))}
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button variant="outline" onClick={() => setAddOEMOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddOEM} disabled={submittingOEM || !oemForm.name.trim()}>
                    {submittingOEM ? "Creating..." : "Create OEM"}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          {/* Drive Fetcher Modal */}
          <DriveFetcherModal
            open={driveModalOpen}
            onClose={() => setDriveModalOpen(false)}
            mode="datasheet"
            defaultOemName={selectedOEM || ""}
            defaultCategory={selectedCategory !== "All" ? selectedCategory : "Cell"}
            onExtracted={async () => {
              setDriveModalOpen(false);
              // Refresh data
              const [oemRes, compRes] = await Promise.all([getOEMs(), getComponents()]);
              setOems(oemRes.items ?? []);
              setComponents(compRes.items ?? []);
            }}
          />

          {/* Upload Datasheet Dialog */}
          <Dialog
            open={uploadOpen}
            onOpenChange={(open) => {
              setUploadOpen(open);
              if (!open) resetUploadDialog();
            }}
          >
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload Datasheet
              </Button>
            </DialogTrigger>
            <DialogContent className={cn("max-h-[90vh] overflow-y-auto", uploadResult ? "sm:max-w-5xl" : "sm:max-w-lg")}>
              <DialogHeader>
                <DialogTitle>Upload Datasheet</DialogTitle>
                <DialogDescription>
                  Upload a PDF, Excel, or CSV file to extract technical parameters automatically.
                </DialogDescription>
              </DialogHeader>

              {!uploadResult ? (
                <div className="space-y-4 pt-2">
                  {/* OEM Selector */}
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">OEM Name *</label>
                    <select
                      value={uploadOEM}
                      onChange={(e) => setUploadOEM(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="">Select OEM...</option>
                      {oems.map((o) => (
                        <option key={o.id} value={o.name}>
                          {o.name}
                        </option>
                      ))}
                      <option value="__new__">+ New OEM</option>
                    </select>
                  </div>

                  {uploadOEM === "__new__" && (
                    <div>
                      <label className="text-sm font-medium mb-1.5 block">New OEM Name *</label>
                      <Input
                        placeholder="Enter new OEM name"
                        value={uploadNewOEM}
                        onChange={(e) => setUploadNewOEM(e.target.value)}
                      />
                    </div>
                  )}

                  {/* Model Name */}
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Model Name *</label>
                    <Input
                      placeholder="e.g., EnerOne Plus 5MWh"
                      value={uploadModel}
                      onChange={(e) => setUploadModel(e.target.value)}
                    />
                  </div>

                  {/* Category */}
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Category *</label>
                    <div className="flex gap-2">
                      {CATEGORIES.map((cat) => (
                        <button
                          key={cat}
                          onClick={() => setUploadCategory(cat)}
                          className={cn(
                            "px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all",
                            uploadCategory === cat
                              ? "bg-slate-900 text-white border-slate-900"
                              : "bg-white text-slate-600 border-slate-200 hover:border-slate-400"
                          )}
                        >
                          {cat}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* File Drop Zone */}
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Datasheet File *</label>
                    <div
                      ref={dropRef}
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      onClick={() => fileInputRef.current?.click()}
                      className={cn(
                        "border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all",
                        uploadFile
                          ? "border-emerald-300 bg-emerald-50/50"
                          : "border-slate-200 bg-slate-50/50 hover:border-slate-400 hover:bg-slate-50"
                      )}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.xlsx,.xls,.csv"
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files?.[0]) setUploadFile(e.target.files[0]);
                        }}
                      />
                      {uploadFile ? (
                        <div className="flex items-center justify-center gap-3">
                          <FileText className="h-8 w-8 text-emerald-500" />
                          <div className="text-left">
                            <p className="text-sm font-medium text-slate-700">{uploadFile.name}</p>
                            <p className="text-xs text-slate-400">
                              {(uploadFile.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setUploadFile(null);
                            }}
                            className="ml-2 text-slate-400 hover:text-red-500"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <>
                          <FileUp className="h-10 w-10 mx-auto text-slate-300 mb-2" />
                          <p className="text-sm text-slate-500">
                            Drag & drop your datasheet here, or click to browse
                          </p>
                          <p className="text-xs text-slate-400 mt-1">
                            PDF, Excel (.xlsx/.xls), CSV
                          </p>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Upload Progress */}
                  {uploading && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span className="flex items-center gap-2">
                          <Loader2 className="h-3 w-3 animate-spin" /> Extracting parameters...
                        </span>
                        <span className="tabular-nums">{Math.round(uploadProgress)}%</span>
                      </div>
                      <Progress value={uploadProgress} />
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex justify-end gap-2 pt-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setUploadOpen(false);
                        resetUploadDialog();
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleUpload}
                      disabled={
                        uploading ||
                        !uploadFile ||
                        !uploadModel.trim() ||
                        (!uploadOEM || (uploadOEM === "__new__" && !uploadNewOEM.trim()))
                      }
                    >
                      {uploading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" /> Extracting...
                        </>
                      ) : (
                        <>
                          <Upload className="h-4 w-4 mr-2" /> Upload & Extract
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              ) : (
                /* Upload Result — Split View */
                <div className="space-y-3 pt-2">
                  <SplitDocumentViewer
                    localFile={uploadFile}
                    gdriveFileId={uploadResult.gdrive_file_id}
                    gdriveUrl={uploadResult.gdrive_url}
                    fileName={uploadResult.file_name}
                    parameters={uploadResult.parameters || []}
                    mode="datasheet"
                    summary={{
                      oem_name: uploadResult.oem_name,
                      model_name: uploadResult.model_name,
                      category: uploadResult.category,
                      compliance_score: uploadResult.compliance_score,
                      pass: uploadResult.pass,
                      fail: uploadResult.fail,
                      total: uploadResult.parameters_extracted,
                    }}
                  />
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => { setUploadOpen(false); resetUploadDialog(); }}>
                      Close
                    </Button>
                    {uploadResult.component_id && (
                      <Button onClick={() => { setUploadOpen(false); resetUploadDialog(); toggleModelExpand(uploadResult.component_id); }}>
                        <Eye className="h-4 w-4 mr-2" /> View Details
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* ================================================================ */}
      {/*  2. OEM CARDS ROW                                                */}
      {/* ================================================================ */}
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
        {/* "All OEMs" card */}
        <button
          onClick={() => setSelectedOEM(null)}
          className={cn(
            "flex-shrink-0 rounded-xl border px-4 py-3 transition-all duration-200 min-w-[140px]",
            selectedOEM === null
              ? "bg-slate-900 text-white border-slate-900 shadow-lg"
              : "bg-white text-slate-600 border-slate-200 hover:border-slate-400 hover:shadow-md"
          )}
        >
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            <div className="text-left">
              <p className="text-xs font-bold">All OEMs</p>
              <p className={cn("text-[10px]", selectedOEM === null ? "text-slate-300" : "text-slate-400")}>
                {oems.length} manufacturers
              </p>
            </div>
          </div>
        </button>

        {oems.map((oem, idx) => {
          const info = OEM_INFO[oem.name] || {
            color: "from-slate-500 to-slate-600",
            website: "#",
            logo: oem.name[0],
          };
          const isSelected = selectedOEM === oem.name;
          return (
            <button
              key={oem.id}
              onClick={() => setSelectedOEM(isSelected ? null : oem.name)}
              className={cn(
                "flex-shrink-0 rounded-xl border px-4 py-3 transition-all duration-200 min-w-[200px]",
                "animate-fade-in",
                isSelected
                  ? "border-slate-900 shadow-lg ring-2 ring-slate-900/10 bg-white"
                  : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-md"
              )}
              style={{ animationDelay: `${idx * 60}ms`, animationFillMode: "both" }}
            >
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white text-lg font-bold shadow-md transition-transform",
                    info.color,
                    isSelected && "scale-110"
                  )}
                >
                  {info.logo}
                </div>
                <div className="text-left flex-1 min-w-0">
                  <p className="text-sm font-bold text-slate-800 truncate">{oem.name}</p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <Globe className="h-3 w-3 text-slate-400" />
                    <span className="text-[10px] text-slate-400 truncate">
                      {oem.country_of_origin || "--"}
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <ScoreRing score={oem.avg_compliance_score} size={40} strokeWidth={3} />
                </div>
              </div>
              <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="text-slate-500">
                    {oem.model_count} model{oem.model_count !== 1 ? "s" : ""}
                  </span>
                  {oem.is_approved ? (
                    <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-200 text-[9px] px-1.5 py-0.5">
                      <CheckCircle2 className="h-2.5 w-2.5 mr-0.5" />
                      Approved
                    </Badge>
                  ) : (
                    <Badge variant="pending" className="text-[9px] px-1.5 py-0.5">
                      Pending
                    </Badge>
                  )}
                </div>
                {oem.website && (
                  <a
                    href={oem.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-slate-300 hover:text-blue-500 transition-colors"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* ================================================================ */}
      {/*  3. CATEGORY TABS                                                */}
      {/* ================================================================ */}
      <div className="flex items-center gap-1 border-b border-slate-200 pb-0">
        {["All", ...CATEGORIES].map((cat) => {
          const count =
            cat === "All"
              ? filteredComponents.length
              : components.filter(
                  (c) =>
                    c.is_active &&
                    c.component_type_name === cat &&
                    (!selectedOEM || c.oem_name === selectedOEM)
                ).length;
          const isActive = selectedCategory === cat;
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                "relative px-4 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "text-slate-900"
                  : "text-slate-400 hover:text-slate-600"
              )}
            >
              {cat}
              <span
                className={cn(
                  "ml-1.5 text-[10px] tabular-nums",
                  isActive ? "text-slate-500" : "text-slate-300"
                )}
              >
                {count}
              </span>
              {isActive && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-slate-900 rounded-full" />
              )}
            </button>
          );
        })}

        {/* Per-category upload button */}
        <div className="ml-auto flex items-center gap-3 pr-1">
          <span className="text-xs text-slate-400">
            {filteredComponents.length} model{filteredComponents.length !== 1 ? "s" : ""}
          </span>
          <Button size="sm" variant="outline" className="text-xs h-7 gap-1.5"
            onClick={() => setDriveModalOpen(true)}>
            <HardDrive className="h-3 w-3" /> Fetch from Drive
          </Button>
          {selectedCategory !== "All" && (
            <Button size="sm" variant="outline" className="text-xs h-7 gap-1.5"
              onClick={() => { setUploadCategory(selectedCategory); setUploadOpen(true); }}>
              <Upload className="h-3 w-3" /> Upload {selectedCategory} Datasheet
            </Button>
          )}
        </div>
      </div>

      {/* ================================================================ */}
      {/*  4. MODELS SECTION                                               */}
      {/* ================================================================ */}
      {filteredComponents.length === 0 ? (
        <div className="text-center py-20">
          <Box className="h-12 w-12 mx-auto text-slate-200 mb-4" />
          <h3 className="text-lg font-semibold text-slate-600">No models found</h3>
          <p className="text-sm text-slate-400 mt-1">Try adjusting your filters or upload a new datasheet</p>
        </div>
      ) : (
        <div className="space-y-8">
          {Array.from(groupedByOEM.entries()).map(([oem, models]) => {
            const info = OEM_INFO[oem] || {
              color: "from-slate-500 to-slate-600",
              website: "#",
              logo: oem[0],
            };
            const avgScore = Math.round(
              models.reduce((s, m) => s + m.compliance_score, 0) / models.length
            );

            return (
              <div key={oem} className="animate-fade-in" style={{ animationFillMode: "both" }}>
                {/* OEM Group Header */}
                <div className="flex items-center gap-4 mb-4">
                  <div
                    className={cn(
                      "w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white text-lg font-bold shadow-md",
                      info.color
                    )}
                  >
                    {info.logo}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-800">{oem}</h2>
                      <Badge variant="default" className="text-[10px]">
                        {models.length} model{models.length !== 1 ? "s" : ""}
                      </Badge>
                      <span className={cn("text-sm font-bold", scoreColor(avgScore))}>
                        {avgScore}% avg
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline" className="text-xs h-7 gap-1.5"
                      onClick={() => { setUploadOEM(oem); setUploadOpen(true); }}>
                      <Upload className="h-3 w-3" /> Upload Datasheet
                    </Button>
                    <a href={info.website} target="_blank" rel="noopener noreferrer"
                      className="text-slate-300 hover:text-blue-500 transition-colors flex items-center gap-1 text-xs">
                      <ExternalLink className="w-3.5 h-3.5" /> Website
                    </a>
                  </div>
                </div>

                {/* Model Cards */}
                <div className="space-y-3 ml-14">
                  {models.map((comp, mIdx) => {
                    const isExpanded = expandedModel === comp.id;
                    const isLoadingP = !!loadingParams[comp.id];
                    const params = modelParams[comp.id] || [];
                    const grouped = groupParams(params);

                    return (
                      <div
                        key={comp.id}
                        className={cn(
                          "border rounded-xl bg-white overflow-hidden transition-all duration-200",
                          isExpanded ? "shadow-lg ring-1 ring-slate-200" : "hover:shadow-md"
                        )}
                        style={{
                          animationDelay: `${mIdx * 40}ms`,
                          animationFillMode: "both",
                        }}
                      >
                        {/* Model Header -- always visible */}
                        <div
                          className="flex items-center gap-4 p-4 cursor-pointer group"
                          onClick={() => toggleModelExpand(comp.id)}
                        >
                          <ScoreRing score={comp.compliance_score} size={52} strokeWidth={4} />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
                              {comp.model_name}
                            </div>
                            <div className="text-xs text-slate-400 mt-0.5">
                              {comp.sku} &middot;{" "}
                              <Badge variant="default" className="text-[9px] px-1.5 py-0">
                                {comp.component_type_name}
                              </Badge>
                            </div>
                          </div>

                          {/* Pass / Fail / Waived */}
                          <div className="flex items-center gap-2.5 text-[10px]">
                            <span className="flex items-center gap-1 text-emerald-600 font-semibold">
                              <CheckCircle2 className="h-3 w-3" />
                              {comp.pass}P
                            </span>
                            {comp.fail > 0 && (
                              <span className="flex items-center gap-1 text-red-500 font-semibold">
                                <XCircle className="h-3 w-3" />
                                {comp.fail}F
                              </span>
                            )}
                            {comp.waived > 0 && (
                              <span className="flex items-center gap-1 text-amber-500 font-semibold">
                                <AlertTriangle className="h-3 w-3" />
                                {comp.waived}W
                              </span>
                            )}
                          </div>

                          {/* Fill Rate */}
                          <div className="flex items-center gap-1.5 text-xs text-slate-400">
                            Fill <Progress value={comp.fill_rate} className="h-1.5 w-12" />{" "}
                            <span className="tabular-nums w-8 text-right">{comp.fill_rate}%</span>
                          </div>

                          {/* Datasheet indicator */}
                          {comp.datasheet && (
                            <div className="flex items-center gap-1 text-[10px] text-slate-300">
                              <FileText className="h-3 w-3" />
                              <span className="max-w-[80px] truncate">{comp.datasheet}</span>
                            </div>
                          )}

                          {/* Expand icon */}
                          {isLoadingP ? (
                            <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                          ) : isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-slate-400" />
                          )}
                        </div>

                        {/* ── Expanded Detail ── */}
                        {isExpanded && params.length > 0 && (
                          <div
                            className="border-t animate-fade-in"
                            style={{ animationFillMode: "both" }}
                          >
                            {/* Document Info Bar */}
                            <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b">
                              <div className="flex items-center gap-3">
                                <div className="w-9 h-9 rounded-lg bg-brand-50 flex items-center justify-center">
                                  <FileText className="h-5 w-5 text-brand" />
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-slate-700">{comp.datasheet || "No datasheet"}</div>
                                  <div className="text-[10px] text-slate-400">
                                    {params.length} parameters extracted · {comp.component_type_name}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button size="sm" variant="outline" className="text-xs h-7 gap-1.5"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    if (comp.gdrive_url) window.open(comp.gdrive_url, "_blank")
                                    else if (comp.gdrive_file_id) window.open(`https://drive.google.com/file/d/${comp.gdrive_file_id}/view`, "_blank")
                                    else alert("No document link available. Upload via 'Fetch from Drive' to enable viewing.")
                                  }}>
                                  <Eye className="h-3 w-3" /> View
                                </Button>
                                <Button size="sm" variant="outline" className="text-xs h-7 gap-1.5"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    if (comp.gdrive_url) window.open(comp.gdrive_url, "_blank")
                                    else if (comp.gdrive_file_id) window.open(`https://drive.google.com/uc?export=download&id=${comp.gdrive_file_id}`, "_blank")
                                    else alert("No document link available. Upload via 'Fetch from Drive' to enable downloading.")
                                  }}>
                                  <Download className="h-3 w-3" /> Download
                                </Button>
                                <Button size="sm" variant="ghost" className="text-xs h-7 gap-1.5 text-brand"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setUploadOEM(comp.oem_name);
                                    setUploadCategory(comp.component_type_name);
                                    setUploadModel("");
                                    setUploadOpen(true);
                                  }}>
                                  <Upload className="h-3 w-3" /> Re-upload
                                </Button>
                              </div>
                            </div>

                            {/* Embedded Datasheet Viewer */}
                            {(comp.gdrive_file_id || comp.gdrive_url) && (
                              <div className="border-t bg-slate-50/50">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    const el = document.getElementById(`pdf-viewer-${comp.id}`);
                                    if (el) el.classList.toggle("hidden");
                                  }}
                                  className="w-full flex items-center justify-between px-4 py-2.5 text-xs font-semibold text-slate-500 hover:text-brand transition-colors"
                                >
                                  <span className="flex items-center gap-1.5">
                                    <FileText className="h-3.5 w-3.5" />
                                    View Datasheet: {comp.datasheet}
                                  </span>
                                  <ChevronDown className="h-3.5 w-3.5" />
                                </button>
                                <div id={`pdf-viewer-${comp.id}`} className="hidden px-4 pb-4">
                                  <div className="rounded-lg border overflow-hidden bg-white" style={{ height: "500px" }}>
                                    <iframe
                                      src={comp.gdrive_file_id
                                        ? `https://drive.google.com/file/d/${comp.gdrive_file_id}/preview`
                                        : comp.gdrive_url?.replace("/view", "/preview")}
                                      width="100%"
                                      height="100%"
                                      style={{ border: "none" }}
                                      allow="autoplay"
                                      title={`Datasheet: ${comp.datasheet}`}
                                    />
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Split Document View — Compare with PDF */}
                            {(comp.gdrive_file_id || comp.gdrive_url) && (
                              <div className="p-4 border-b">
                                <SplitDocumentViewer
                                  gdriveFileId={comp.gdrive_file_id}
                                  gdriveUrl={comp.gdrive_url}
                                  fileName={comp.datasheet}
                                  parameters={params}
                                  mode="datasheet"
                                  summary={{
                                    oem_name: comp.oem_name,
                                    model_name: comp.model_name,
                                    category: comp.component_type_name,
                                    compliance_score: comp.compliance_score,
                                    pass: comp.pass,
                                    fail: comp.fail,
                                    total: params.length,
                                  }}
                                />
                              </div>
                            )}

                            {/* Charts Row */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-slate-50/50">
                              {/* Electrical Bar Chart */}
                              <div>
                                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                                  Electrical Parameters
                                </div>
                                <ResponsiveContainer width="100%" height={200}>
                                  <BarChart
                                    data={params
                                      .filter(
                                        (p) =>
                                          (p.section || "").includes("Electrical") &&
                                          !isNaN(parseFloat(p.value))
                                      )
                                      .map((p) => ({
                                        name:
                                          p.name.length > 14
                                            ? p.name.slice(0, 14) + "\u2026"
                                            : p.name,
                                        value: parseFloat(p.value),
                                        unit: p.unit,
                                        fullName: p.name,
                                      }))}
                                    margin={{ top: 5, right: 10, bottom: 30, left: 0 }}
                                  >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                    <XAxis
                                      dataKey="name"
                                      tick={{ fontSize: 9 }}
                                      angle={-25}
                                      textAnchor="end"
                                      height={50}
                                    />
                                    <YAxis tick={{ fontSize: 10 }} />
                                    <Tooltip
                                      contentStyle={{
                                        borderRadius: 8,
                                        border: "1px solid #e2e8f0",
                                        fontSize: 11,
                                      }}
                                      formatter={(v: number, _n: string, p: any) => [
                                        `${v} ${p.payload.unit}`,
                                        p.payload.fullName,
                                      ]}
                                    />
                                    <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={22}>
                                      {params
                                        .filter(
                                          (p) =>
                                            (p.section || "").includes("Electrical") &&
                                            !isNaN(parseFloat(p.value))
                                        )
                                        .map((_, i) => (
                                          <RCell
                                            key={i}
                                            fill={BAR_COLORS[i % BAR_COLORS.length]}
                                          />
                                        ))}
                                    </Bar>
                                  </BarChart>
                                </ResponsiveContainer>
                              </div>

                              {/* Radar Chart */}
                              <div>
                                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                                  Section Pass Rates
                                </div>
                                <ResponsiveContainer width="100%" height={200}>
                                  <RadarChart data={radarData(params)}>
                                    <PolarGrid stroke="#e2e8f0" />
                                    <PolarAngleAxis dataKey="section" tick={{ fontSize: 10 }} />
                                    <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 9 }} />
                                    <Radar
                                      dataKey="score"
                                      stroke="#3b82f6"
                                      fill="#3b82f6"
                                      fillOpacity={0.15}
                                      strokeWidth={2}
                                    />
                                  </RadarChart>
                                </ResponsiveContainer>
                              </div>
                            </div>

                            {/* Download Datasheet */}
                            {comp.datasheet && (
                              <div className="px-4 pb-2">
                                <Button variant="outline" size="sm" className="text-xs"
                                  onClick={() => comp.gdrive_url ? window.open(comp.gdrive_url, "_blank") : null}>
                                  <Download className="h-3.5 w-3.5 mr-1.5" />
                                  {comp.gdrive_url ? `View on Drive (${comp.datasheet})` : `Datasheet: ${comp.datasheet}`}
                                </Button>
                              </div>
                            )}

                            {/* Parameter Tables by Section */}
                            <div className="p-4 space-y-4">
                              {Object.entries(grouped).map(([section, sectionParams]) => {
                                const Icon = SECTION_ICON[section] || Box;
                                const color = SECTION_COLOR[section] || "text-slate-500";
                                return (
                                  <div key={section}>
                                    <div className="flex items-center gap-2 mb-2">
                                      <Icon className={cn("w-3.5 h-3.5", color)} />
                                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                                        {section}
                                      </span>
                                      <span className="text-[10px] text-slate-300">
                                        {sectionParams.length} params
                                      </span>
                                    </div>
                                    <div className="rounded-lg border overflow-hidden">
                                      <table className="w-full text-xs table-fixed">
                                        <thead>
                                          <tr className="bg-slate-50 border-b text-[10px] uppercase tracking-wider text-slate-400">
                                            <th className="py-2 px-4 text-left font-semibold w-[40%]">
                                              Parameter
                                            </th>
                                            <th className="py-2 px-4 text-right font-semibold w-[25%]">
                                              Value
                                            </th>
                                            <th className="py-2 px-4 text-center font-semibold w-[35%]">
                                              Verified
                                            </th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {sectionParams.map((p, i) => (
                                            <tr
                                              key={p.code}
                                              className={cn(
                                                "border-b last:border-0",
                                                i % 2 ? "bg-slate-50/50" : ""
                                              )}
                                            >
                                              <td className="py-2 px-4 font-medium text-slate-700">
                                                {p.name}
                                                <span className="text-slate-300 font-mono text-[9px] block mt-0.5">
                                                  {p.code}
                                                </span>
                                              </td>
                                              <td className="py-2 px-4 text-right font-semibold text-slate-800 tabular-nums">
                                                {p.value}{" "}
                                                <span className="text-slate-400 font-normal">
                                                  {p.unit}
                                                </span>
                                              </td>
                                              <td className="py-2 px-4 text-center">
                                                {p.verified === false
                                                  ? <span className="text-[10px] text-amber-500 font-medium">Unverified</span>
                                                  : <span className="text-[10px] text-emerald-500 font-medium">Verified</span>
                                                }
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Loading state for params */}
                        {isExpanded && isLoadingP && (
                          <div className="border-t p-8 flex items-center justify-center">
                            <Loader2 className="h-6 w-6 animate-spin text-slate-400 mr-2" />
                            <span className="text-sm text-slate-400">
                              Loading parameters...
                            </span>
                          </div>
                        )}

                        {/* Empty params state */}
                        {isExpanded && !isLoadingP && params.length === 0 && (
                          <div className="border-t p-8 text-center">
                            <FileText className="h-8 w-8 mx-auto text-slate-200 mb-2" />
                            <p className="text-sm text-slate-400">
                              No parameters extracted yet. Upload a datasheet to populate.
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
