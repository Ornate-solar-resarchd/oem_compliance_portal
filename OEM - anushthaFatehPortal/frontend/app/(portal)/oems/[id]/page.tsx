"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getOEM, getDashboardCharts } from "@/lib/api";
import { cn, formatNumber, scoreColor, scoreBg } from "@/lib/utils";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScoreRing } from "@/components/shared/score-ring";
import { StatusBadge } from "@/components/shared/status-badge";
import {
  ArrowLeft,
  Globe,
  Mail,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Zap,
  BarChart3,
  PieChartIcon,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface Model {
  id: string;
  oem_id: string;
  oem_name: string;
  model_name: string;
  sku: string;
  component_type_name: string;
  fill_rate: number;
  compliance_score: number;
}

interface OEMDetail {
  id: string;
  name: string;
  country_of_origin: string;
  is_approved: boolean;
  score: number;
  model_count: number;
  avg_compliance_score: number;
  website: string;
  contact_email: string;
  models: Model[];
}

interface ChartData {
  oem_name: string;
  model_scores: { model: string; score: number }[];
  electrical_params: { name: string; value: number; unit: string }[];
  compliance_breakdown: { pass: number; fail: number; waived: number };
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const PIE_COLORS = ["#10b981", "#ef4444", "#f59e0b"];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function OEMDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [oem, setOem] = useState<OEMDetail | null>(null);
  const [charts, setCharts] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    async function load() {
      try {
        const [oemRes, chartRes] = await Promise.all([
          getOEM(id),
          getDashboardCharts(id),
        ]);
        setOem(oemRes);
        setCharts(chartRes);
      } catch (e) {
        console.error("Failed to load OEM detail", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <p className="text-muted-foreground text-sm">Loading OEM details...</p>
        </div>
      </div>
    );
  }

  if (!oem) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">OEM not found.</p>
        <Button variant="outline" className="mt-4" onClick={() => router.push("/oems")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to OEMs
        </Button>
      </div>
    );
  }

  const breakdown = charts?.compliance_breakdown;
  const pieData = breakdown
    ? [
        { name: "Pass", value: breakdown.pass },
        { name: "Fail", value: breakdown.fail },
        { name: "Waived", value: breakdown.waived },
      ]
    : [];

  return (
    <div className="space-y-8">
      {/* Back link */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => router.push("/oems")}
        className="text-muted-foreground -ml-2"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to OEM Library
      </Button>

      {/* ---- Hero Section ---- */}
      <div className="rounded-xl border bg-gradient-to-br from-background to-muted/30 p-6 md:p-8">
        <div className="flex flex-col md:flex-row items-start gap-6">
          {/* Score ring */}
          <div className="shrink-0">
            <ScoreRing score={oem.avg_compliance_score} size={100} />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-3xl font-bold tracking-tight">{oem.name}</h1>
              {oem.is_approved ? (
                <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-200">
                  <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                  Approved
                </Badge>
              ) : (
                <Badge variant="outline" className="text-amber-600 border-amber-200">
                  <XCircle className="h-3.5 w-3.5 mr-1" />
                  Pending Approval
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground flex-wrap">
              {oem.country_of_origin && (
                <div className="flex items-center gap-1.5">
                  <Globe className="h-4 w-4" />
                  {oem.country_of_origin}
                </div>
              )}
              {oem.contact_email && (
                <div className="flex items-center gap-1.5">
                  <Mail className="h-4 w-4" />
                  {oem.contact_email}
                </div>
              )}
              {oem.website && (
                <a
                  href={oem.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 hover:text-primary transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  Website
                </a>
              )}
            </div>

            {/* Summary stats */}
            <div className="flex gap-6 mt-5">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Models</p>
                <p className="text-2xl font-bold">{oem.model_count}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">
                  Avg Compliance
                </p>
                <p className={cn("text-2xl font-bold", scoreColor(oem.avg_compliance_score))}>
                  {formatNumber(oem.avg_compliance_score)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">
                  OEM Score
                </p>
                <p className={cn("text-2xl font-bold", scoreColor(oem.score))}>
                  {formatNumber(oem.score)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ---- Model List ---- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Models</CardTitle>
          <CardDescription>
            All BESS component models from {oem.name}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {oem.models && oem.models.length > 0 ? (
            <div className="space-y-3">
              {oem.models.map((model) => (
                <div
                  key={model.id}
                  className="flex items-center gap-4 p-3 rounded-lg border hover:bg-muted/30 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium truncate">{model.model_name}</p>
                      <Badge variant="outline" className="text-[10px] shrink-0">
                        {model.component_type_name}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground font-mono mt-0.5">
                      SKU: {model.sku}
                    </p>
                  </div>

                  <div className="w-48 shrink-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-muted-foreground">Compliance</span>
                      <span
                        className={cn(
                          "text-xs font-semibold",
                          scoreColor(model.compliance_score)
                        )}
                      >
                        {formatNumber(model.compliance_score)}%
                      </span>
                    </div>
                    <Progress value={model.compliance_score} className="h-2" />
                  </div>

                  <div className="w-20 text-right shrink-0">
                    <p className="text-xs text-muted-foreground">Fill Rate</p>
                    <p className="text-sm font-medium">
                      {formatNumber(model.fill_rate * 100)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm py-8 text-center">
              No models registered yet.
            </p>
          )}
        </CardContent>
      </Card>

      {/* ---- Charts Section ---- */}
      {charts && (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {/* Model Scores Bar Chart */}
          <Card className="xl:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-blue-500" />
                Model Compliance Scores
              </CardTitle>
            </CardHeader>
            <CardContent>
              {charts.model_scores && charts.model_scores.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={charts.model_scores.map((m) => ({
                      name:
                        m.model.length > 16 ? m.model.slice(0, 14) + "..." : m.model,
                      score: m.score,
                    }))}
                    margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 10 }}
                      angle={-25}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8 }}
                      formatter={(val: number) => [`${val}%`, "Score"]}
                    />
                    <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                      {charts.model_scores.map((entry, index) => (
                        <Cell
                          key={index}
                          fill={
                            entry.score >= 80
                              ? "#10b981"
                              : entry.score >= 60
                              ? "#f59e0b"
                              : "#ef4444"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted-foreground text-sm py-12 text-center">
                  No model score data available.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Compliance Breakdown Pie Chart */}
          <Card className="xl:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <PieChartIcon className="h-4 w-4 text-emerald-500" />
                Compliance Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pieData.length > 0 && pieData.some((d) => d.value > 0) ? (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="45%"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={3}
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                      labelLine={{ strokeWidth: 1 }}
                    >
                      {pieData.map((_, index) => (
                        <Cell key={index} fill={PIE_COLORS[index]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8 }}
                      formatter={(val: number) => [val, "Count"]}
                    />
                    <Legend
                      wrapperStyle={{ fontSize: 12 }}
                      formatter={(value) => (
                        <span className="text-xs">{value}</span>
                      )}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted-foreground text-sm py-12 text-center">
                  No compliance data available.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Electrical Parameters Bar Chart */}
          <Card className="xl:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-500" />
                Electrical Parameters
              </CardTitle>
            </CardHeader>
            <CardContent>
              {charts.electrical_params && charts.electrical_params.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={charts.electrical_params.map((p) => ({
                      name:
                        p.name.length > 14 ? p.name.slice(0, 12) + "..." : p.name,
                      value: p.value,
                      unit: p.unit,
                    }))}
                    margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 10 }}
                      angle={-25}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8 }}
                      formatter={(val: number, _name: string, props: any) => [
                        `${val} ${props.payload.unit}`,
                        "Value",
                      ]}
                    />
                    <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted-foreground text-sm py-12 text-center">
                  No electrical parameter data available.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
