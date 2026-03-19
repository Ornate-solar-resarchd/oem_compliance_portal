"use client";

import { useEffect, useState, useMemo } from "react";
import {
  getComponents,
  getComponentParams,
  getOEMs,
} from "@/lib/api";
import { cn, formatNumber, scoreColor, scoreBg } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScoreRing } from "@/components/shared/score-ring";
import { StatusBadge } from "@/components/shared/status-badge";
import {
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  Zap,
  Battery,
  Thermometer,
  Shield,
  Activity,
  Box,
  X,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from "recharts";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

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
}

interface Param {
  code: string;
  name: string;
  value: string;
  unit: string;
  section: string;
  status: string;
  confidence: number;
}

interface OEMItem {
  id: string;
  name: string;
}

/* ------------------------------------------------------------------ */
/*  Section icon helper                                                */
/* ------------------------------------------------------------------ */

const sectionIcon: Record<string, React.ReactNode> = {
  Electrical: <Zap className="h-4 w-4 text-yellow-500" />,
  Physical: <Box className="h-4 w-4 text-blue-500" />,
  Thermal: <Thermometer className="h-4 w-4 text-orange-500" />,
  Safety: <Shield className="h-4 w-4 text-red-500" />,
  Performance: <Activity className="h-4 w-4 text-emerald-500" />,
};

const SECTIONS = ["Electrical", "Physical", "Thermal", "Safety", "Performance"];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function TechnicalDataPage() {
  /* ---- data ---- */
  const [components, setComponents] = useState<Component[]>([]);
  const [oems, setOems] = useState<OEMItem[]>([]);
  const [loading, setLoading] = useState(true);

  /* expanded cards: id → params */
  const [expanded, setExpanded] = useState<Record<string, Param[]>>({});
  const [loadingParams, setLoadingParams] = useState<Record<string, boolean>>({});

  /* ---- filters ---- */
  const [search, setSearch] = useState("");
  const [oemFilter, setOemFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [scoreMin, setScoreMin] = useState(0);
  const [scoreMax, setScoreMax] = useState(100);

  /* ---- fetch ---- */
  useEffect(() => {
    async function load() {
      try {
        const [compRes, oemRes] = await Promise.all([
          getComponents(),
          getOEMs(),
        ]);
        setComponents(compRes.items ?? []);
        setOems(oemRes.items ?? []);
      } catch (e) {
        console.error("Failed to load technical data", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* ---- derived ---- */
  const componentTypes = useMemo(
    () => [...new Set(components.map((c) => c.component_type_name))].sort(),
    [components]
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return components.filter((c) => {
      if (q && !`${c.model_name} ${c.oem_name} ${c.sku}`.toLowerCase().includes(q))
        return false;
      if (oemFilter !== "all" && c.oem_id !== oemFilter) return false;
      if (typeFilter !== "all" && c.component_type_name !== typeFilter) return false;
      if (c.compliance_score < scoreMin || c.compliance_score > scoreMax) return false;
      return true;
    });
  }, [components, search, oemFilter, typeFilter, scoreMin, scoreMax]);

  /* ---- expand / collapse ---- */
  async function toggleExpand(id: string) {
    if (expanded[id]) {
      const next = { ...expanded };
      delete next[id];
      setExpanded(next);
      return;
    }
    setLoadingParams((p) => ({ ...p, [id]: true }));
    try {
      const res = await getComponentParams(id);
      setExpanded((prev) => ({ ...prev, [id]: res.items ?? [] }));
    } catch (e) {
      console.error("Failed to load params", e);
    } finally {
      setLoadingParams((p) => ({ ...p, [id]: false }));
    }
  }

  /* ---- helpers for expanded view ---- */
  function keySpec(params: Param[], code: string) {
    const p = params.find((x) => x.code === code);
    return p ? `${p.value} ${p.unit}` : "—";
  }

  function groupedBySection(params: Param[]) {
    const groups: Record<string, Param[]> = {};
    SECTIONS.forEach((s) => (groups[s] = []));
    params.forEach((p) => {
      const sec = SECTIONS.includes(p.section) ? p.section : "Performance";
      groups[sec].push(p);
    });
    return groups;
  }

  function sectionPassRates(params: Param[]) {
    return SECTIONS.map((sec) => {
      const items = params.filter((p) => p.section === sec || (!SECTIONS.includes(p.section) && sec === "Performance"));
      const passed = items.filter((p) => p.status === "pass").length;
      const total = items.length || 1;
      return { section: sec, rate: Math.round((passed / total) * 100) };
    });
  }

  /* ---- render ---- */
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <p className="text-muted-foreground text-sm">Loading technical data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ---- Header ---- */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Technical Data</h1>
        <p className="text-muted-foreground mt-1">
          BESS component specifications, compliance scores & parameter analysis
        </p>
      </div>

      {/* ---- Filter Bar ---- */}
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
                  placeholder="Model, OEM, or SKU..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            {/* OEM dropdown */}
            <div className="min-w-[180px]">
              <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                OEM
              </label>
              <select
                value={oemFilter}
                onChange={(e) => setOemFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="all">All OEMs</option>
                {oems.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Type dropdown */}
            <div className="min-w-[180px]">
              <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                Component Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="all">All Types</option>
                {componentTypes.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            {/* Score range */}
            <div className="flex gap-2 items-end">
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                  Score Min
                </label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={scoreMin}
                  onChange={(e) => setScoreMin(Number(e.target.value))}
                  className="w-20"
                />
              </div>
              <span className="pb-2 text-muted-foreground">–</span>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                  Score Max
                </label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  value={scoreMax}
                  onChange={(e) => setScoreMax(Number(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Reset */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSearch("");
                setOemFilter("all");
                setTypeFilter("all");
                setScoreMin(0);
                setScoreMax(100);
              }}
              className="text-muted-foreground"
            >
              <X className="h-4 w-4 mr-1" />
              Reset
            </Button>
          </div>

          <p className="text-xs text-muted-foreground mt-3">
            Showing {filtered.length} of {components.length} components
          </p>
        </CardContent>
      </Card>

      {/* ---- Component Grid ---- */}
      {filtered.length === 0 ? (
        <div className="text-center py-20">
          <Battery className="h-12 w-12 mx-auto text-muted-foreground/40 mb-4" />
          <p className="text-muted-foreground">No components match your filters.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((comp) => {
            const isExpanded = !!expanded[comp.id];
            const params = expanded[comp.id] ?? [];
            const isLoading = loadingParams[comp.id];

            return (
              <div
                key={comp.id}
                className={cn(
                  "col-span-1 transition-all duration-300",
                  isExpanded && "md:col-span-2 xl:col-span-3"
                )}
              >
                <Card
                  className={cn(
                    "overflow-hidden transition-shadow hover:shadow-lg cursor-pointer border",
                    isExpanded && "ring-2 ring-primary/20"
                  )}
                >
                  {/* ---- Collapsed Card Header ---- */}
                  <div
                    className="p-5 flex items-start gap-4"
                    onClick={() => toggleExpand(comp.id)}
                  >
                    {/* Score ring */}
                    <div className="shrink-0">
                      <ScoreRing score={comp.compliance_score} size={64} />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-semibold text-base truncate">
                          {comp.model_name}
                        </h3>
                        <Badge variant="outline" className="text-[10px] shrink-0">
                          {comp.component_type_name}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mt-0.5">
                        {comp.oem_name}
                      </p>
                      <p className="text-xs text-muted-foreground font-mono mt-0.5">
                        SKU: {comp.sku}
                      </p>

                      {/* Key specs (from expanded params if available) */}
                      {isExpanded && params.length > 0 && (
                        <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                          <span>Capacity: {keySpec(params, "capacity")}</span>
                          <span>Voltage: {keySpec(params, "voltage")}</span>
                          <span>Cycle Life: {keySpec(params, "cycle_life")}</span>
                        </div>
                      )}

                      {/* Pass / Fail / Waived */}
                      <div className="flex items-center gap-2 mt-3">
                        <Badge
                          variant="secondary"
                          className="bg-emerald-500/10 text-emerald-600 text-[10px]"
                        >
                          {comp.pass} Pass
                        </Badge>
                        <Badge
                          variant="secondary"
                          className="bg-red-500/10 text-red-600 text-[10px]"
                        >
                          {comp.fail} Fail
                        </Badge>
                        <Badge
                          variant="secondary"
                          className="bg-amber-500/10 text-amber-600 text-[10px]"
                        >
                          {comp.waived} Waived
                        </Badge>
                        <div className="ml-auto text-xs text-muted-foreground">
                          Fill: {formatNumber(comp.fill_rate * 100)}%
                        </div>
                      </div>
                    </div>

                    {/* Expand chevron */}
                    <div className="shrink-0 pt-1">
                      {isLoading ? (
                        <div className="h-5 w-5 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                      ) : isExpanded ? (
                        <ChevronUp className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                  </div>

                  {/* ---- Expanded Detail ---- */}
                  {isExpanded && params.length > 0 && (
                    <div className="border-t bg-muted/30">
                      <div className="p-5 space-y-6">
                        {/* Charts Row */}
                        <div className="grid md:grid-cols-2 gap-6">
                          {/* Electrical Params Bar Chart */}
                          <Card>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <Zap className="h-4 w-4 text-yellow-500" />
                                Electrical Parameters
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <ResponsiveContainer width="100%" height={220}>
                                <BarChart
                                  data={params
                                    .filter((p) => p.section === "Electrical")
                                    .slice(0, 8)
                                    .map((p) => ({
                                      name: p.name.length > 14 ? p.name.slice(0, 12) + "..." : p.name,
                                      value: parseFloat(p.value) || 0,
                                      unit: p.unit,
                                    }))}
                                  margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
                                >
                                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                                  <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={50} />
                                  <YAxis tick={{ fontSize: 10 }} />
                                  <Tooltip
                                    contentStyle={{ fontSize: 12, borderRadius: 8 }}
                                    formatter={(val: number, _name: string, props: any) => [
                                      `${val} ${props.payload.unit}`,
                                      "Value",
                                    ]}
                                  />
                                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                </BarChart>
                              </ResponsiveContainer>
                            </CardContent>
                          </Card>

                          {/* Radar Chart - Section Pass Rates */}
                          <Card>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-sm flex items-center gap-2">
                                <Activity className="h-4 w-4 text-emerald-500" />
                                Section Pass Rates
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <ResponsiveContainer width="100%" height={220}>
                                <RadarChart
                                  data={sectionPassRates(params)}
                                  cx="50%"
                                  cy="50%"
                                  outerRadius="70%"
                                >
                                  <PolarGrid strokeDasharray="3 3" />
                                  <PolarAngleAxis dataKey="section" tick={{ fontSize: 11 }} />
                                  <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9 }} />
                                  <Radar
                                    name="Pass Rate %"
                                    dataKey="rate"
                                    stroke="#10b981"
                                    fill="#10b981"
                                    fillOpacity={0.25}
                                    strokeWidth={2}
                                  />
                                  <Legend wrapperStyle={{ fontSize: 11 }} />
                                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                                </RadarChart>
                              </ResponsiveContainer>
                            </CardContent>
                          </Card>
                        </div>

                        {/* Parameter Table grouped by section */}
                        <div className="space-y-4">
                          {SECTIONS.map((section) => {
                            const grouped = groupedBySection(params);
                            const items = grouped[section];
                            if (!items || items.length === 0) return null;

                            return (
                              <div key={section}>
                                <div className="flex items-center gap-2 mb-2">
                                  {sectionIcon[section]}
                                  <h4 className="text-sm font-semibold">{section}</h4>
                                  <Badge variant="outline" className="text-[10px] ml-1">
                                    {items.length} params
                                  </Badge>
                                </div>

                                <div className="rounded-lg border overflow-hidden">
                                  <table className="w-full text-sm">
                                    <thead>
                                      <tr className="bg-muted/50 text-left">
                                        <th className="px-4 py-2 font-medium text-xs text-muted-foreground">
                                          Parameter
                                        </th>
                                        <th className="px-4 py-2 font-medium text-xs text-muted-foreground">
                                          Value
                                        </th>
                                        <th className="px-4 py-2 font-medium text-xs text-muted-foreground w-[140px]">
                                          Confidence
                                        </th>
                                        <th className="px-4 py-2 font-medium text-xs text-muted-foreground w-[90px]">
                                          Status
                                        </th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y">
                                      {items.map((p) => (
                                        <tr
                                          key={p.code}
                                          className="hover:bg-muted/30 transition-colors"
                                        >
                                          <td className="px-4 py-2.5 font-medium">
                                            {p.name}
                                          </td>
                                          <td className="px-4 py-2.5 font-mono text-xs">
                                            {p.value}{" "}
                                            <span className="text-muted-foreground">
                                              {p.unit}
                                            </span>
                                          </td>
                                          <td className="px-4 py-2.5">
                                            <div className="flex items-center gap-2">
                                              <Progress
                                                value={p.confidence * 100}
                                                className="h-1.5 flex-1"
                                              />
                                              <span className="text-[10px] text-muted-foreground w-8 text-right">
                                                {Math.round(p.confidence * 100)}%
                                              </span>
                                            </div>
                                          </td>
                                          <td className="px-4 py-2.5">
                                            <StatusBadge status={p.status} />
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
                    </div>
                  )}
                </Card>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
