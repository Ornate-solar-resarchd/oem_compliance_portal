"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { getOEMs, createOEM } from "@/lib/api";
import { cn, formatNumber, scoreColor, scoreBg } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
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
import { ScoreRing } from "@/components/shared/score-ring";
import {
  Search,
  Plus,
  Globe,
  Mail,
  Building2,
  CheckCircle2,
  XCircle,
  Filter,
  X,
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

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function OEMsPage() {
  const router = useRouter();
  const [oems, setOems] = useState<OEM[]>([]);
  const [loading, setLoading] = useState(true);

  /* Filters */
  const [search, setSearch] = useState("");
  const [countryFilter, setCountryFilter] = useState("all");
  const [approvalFilter, setApprovalFilter] = useState<"all" | "approved" | "pending">("all");

  /* Add OEM Dialog */
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    country_of_origin: "",
    website: "",
    contact_email: "",
  });
  const [submitting, setSubmitting] = useState(false);

  /* Fetch */
  useEffect(() => {
    async function load() {
      try {
        const res = await getOEMs();
        setOems(res.items ?? []);
      } catch (e) {
        console.error("Failed to load OEMs", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* Derived */
  const countries = useMemo(
    () => [...new Set(oems.map((o) => o.country_of_origin).filter(Boolean))].sort(),
    [oems]
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return oems.filter((o) => {
      if (q && !`${o.name} ${o.country_of_origin}`.toLowerCase().includes(q)) return false;
      if (countryFilter !== "all" && o.country_of_origin !== countryFilter) return false;
      if (approvalFilter === "approved" && !o.is_approved) return false;
      if (approvalFilter === "pending" && o.is_approved) return false;
      return true;
    });
  }, [oems, search, countryFilter, approvalFilter]);

  /* Add OEM */
  async function handleAddOEM() {
    if (!formData.name.trim()) return;
    setSubmitting(true);
    try {
      await createOEM(formData);
      const res = await getOEMs();
      setOems(res.items ?? []);
      setDialogOpen(false);
      setFormData({ name: "", country_of_origin: "", website: "", contact_email: "" });
    } catch (e) {
      console.error("Failed to create OEM", e);
    } finally {
      setSubmitting(false);
    }
  }

  /* Loading */
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">OEM Library</h1>
          <p className="text-muted-foreground mt-1">
            Manage and review Original Equipment Manufacturers
          </p>
        </div>

        {/* Add OEM Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
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
                  value={formData.name}
                  onChange={(e) => setFormData((f) => ({ ...f, name: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Country of Origin</label>
                <Input
                  placeholder="e.g., China, South Korea"
                  value={formData.country_of_origin}
                  onChange={(e) => setFormData((f) => ({ ...f, country_of_origin: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Website</label>
                <Input
                  placeholder="https://..."
                  value={formData.website}
                  onChange={(e) => setFormData((f) => ({ ...f, website: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Contact Email</label>
                <Input
                  placeholder="contact@oem.com"
                  type="email"
                  value={formData.contact_email}
                  onChange={(e) => setFormData((f) => ({ ...f, contact_email: e.target.value }))}
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddOEM} disabled={submitting || !formData.name.trim()}>
                  {submitting ? "Creating..." : "Create OEM"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filter Bar */}
      <Card className="border-dashed">
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-end gap-4">
            {/* Search */}
            <div className="flex-1 min-w-[220px]">
              <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search OEM name or country..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            {/* Country */}
            <div className="min-w-[180px]">
              <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                Country
              </label>
              <select
                value={countryFilter}
                onChange={(e) => setCountryFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="all">All Countries</option>
                {countries.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            {/* Approval Status */}
            <div className="min-w-[160px]">
              <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                Approval Status
              </label>
              <select
                value={approvalFilter}
                onChange={(e) => setApprovalFilter(e.target.value as any)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="all">All</option>
                <option value="approved">Approved</option>
                <option value="pending">Pending</option>
              </select>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSearch("");
                setCountryFilter("all");
                setApprovalFilter("all");
              }}
              className="text-muted-foreground"
            >
              <X className="h-4 w-4 mr-1" />
              Reset
            </Button>
          </div>

          <p className="text-xs text-muted-foreground mt-3">
            Showing {filtered.length} of {oems.length} OEMs
          </p>
        </CardContent>
      </Card>

      {/* OEM Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20">
          <Building2 className="h-12 w-12 mx-auto text-muted-foreground/40 mb-4" />
          <p className="text-muted-foreground">No OEMs match your filters.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((oem) => (
            <Card
              key={oem.id}
              className="group cursor-pointer hover:shadow-lg transition-all duration-200 hover:border-primary/30"
              onClick={() => router.push(`/oems/${oem.id}`)}
            >
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <ScoreRing score={oem.avg_compliance_score} size={56} />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-base truncate group-hover:text-primary transition-colors">
                      {oem.name}
                    </h3>
                    <div className="flex items-center gap-1.5 mt-1">
                      <Globe className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">
                        {oem.country_of_origin || "—"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-2 flex-wrap">
                  {/* Approval badge */}
                  {oem.is_approved ? (
                    <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-200 text-[10px]">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Approved
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="text-amber-600 border-amber-200 text-[10px]">
                      <XCircle className="h-3 w-3 mr-1" />
                      Pending
                    </Badge>
                  )}

                  {/* Country badge */}
                  {oem.country_of_origin && (
                    <Badge variant="secondary" className="text-[10px]">
                      {oem.country_of_origin}
                    </Badge>
                  )}
                </div>

                {/* Stats */}
                <div className="mt-4 pt-3 border-t grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider">
                      Models
                    </p>
                    <p className="text-lg font-bold">{oem.model_count}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider">
                      Avg Score
                    </p>
                    <p className={cn("text-lg font-bold", scoreColor(oem.avg_compliance_score))}>
                      {formatNumber(oem.avg_compliance_score)}%
                    </p>
                  </div>
                </div>

                {/* Contact info */}
                {oem.contact_email && (
                  <div className="mt-3 pt-3 border-t flex items-center gap-1.5 text-xs text-muted-foreground truncate">
                    <Mail className="h-3 w-3 shrink-0" />
                    <span className="truncate">{oem.contact_email}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
