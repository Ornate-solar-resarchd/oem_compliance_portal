"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { getRFQ, matchRFQ } from "@/lib/api";
import { cn, scoreColor, scoreBg } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScoreRing } from "@/components/shared/score-ring";
import { StatusBadge } from "@/components/shared/status-badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  ArrowLeft,
  FileCheck,
  GitCompare,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";

interface Requirement {
  parameter: string;
  code: string;
  required_value: string;
  unit: string;
}

interface MatchDetail {
  parameter: string;
  required: string;
  oem_value: string;
  match: boolean;
}

interface MatchResult {
  component_id: string;
  model_name: string;
  oem_name: string;
  match_percentage: number;
  passed: number;
  total: number;
  details: MatchDetail[];
}

interface RFQData {
  id: string;
  customer_name: string;
  project_name: string;
  status: string;
  created_at: string;
  requirements: Requirement[];
}

interface MatchData {
  rfq_id: string;
  customer: string;
  matches: MatchResult[];
}

export default function RFQComparisonPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [rfq, setRfq] = useState<RFQData | null>(null);
  const [matchData, setMatchData] = useState<MatchData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [rfqRes, matchRes] = await Promise.all([
          getRFQ(id),
          matchRFQ(id),
        ]);
        setRfq(rfqRes);
        setMatchData(matchRes);
      } catch (err) {
        console.error("Failed to fetch RFQ data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  const sortedMatches = matchData?.matches
    ? [...matchData.matches].sort(
        (a, b) => b.match_percentage - a.match_percentage
      )
    : [];

  const chartData = sortedMatches.map((m) => ({
    name: m.model_name.length > 15
      ? m.model_name.slice(0, 15) + "..."
      : m.model_name,
    fullName: m.model_name,
    match: m.match_percentage,
  }));

  const getBarColor = (value: number) => {
    if (value >= 90) return "#22c55e";
    if (value >= 70) return "#eab308";
    if (value >= 50) return "#f97316";
    return "#ef4444";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!rfq) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        RFQ not found.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/rfq")}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {rfq.customer_name} &mdash; {rfq.project_name}
            </h1>
            <p className="text-muted-foreground text-sm mt-0.5">
              RFQ Comparison &middot; {rfq.requirements?.length || 0} parameters
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => router.push(`/rfq/${id}/compliance`)}
          >
            <FileCheck className="mr-2 h-4 w-4" />
            Generate Compliance Sheet
          </Button>
          <Button onClick={() => router.push(`/rfq/${id}/diversify`)}>
            <GitCompare className="mr-2 h-4 w-4" />
            Generate Diversify Sheet
          </Button>
        </div>
      </div>

      {/* Match Chart */}
      {chartData.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">
              Match Percentage by Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 40, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 11 }}
                    angle={-30}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(value: number) => [`${value}%`, "Match"]}
                    labelFormatter={(label: string, payload: any[]) =>
                      payload?.[0]?.payload?.fullName || label
                    }
                  />
                  <Bar dataKey="match" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={getBarColor(entry.match)}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content - Two Panels */}
      <div className="grid gap-6 lg:grid-cols-[1fr_1.5fr]">
        {/* Left Panel: Requirements Table */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">RFQ Requirements</CardTitle>
            <CardDescription>
              Technical parameters specified by {rfq.customer_name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="py-2 px-3 text-left font-medium">
                      Parameter
                    </th>
                    <th className="py-2 px-3 text-left font-medium">
                      Required
                    </th>
                    <th className="py-2 px-3 text-left font-medium">Unit</th>
                  </tr>
                </thead>
                <tbody>
                  {rfq.requirements?.map((req, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td className="py-2 px-3 font-medium">
                        {req.parameter}
                      </td>
                      <td className="py-2 px-3 font-mono text-xs">
                        {req.required_value}
                      </td>
                      <td className="py-2 px-3 text-muted-foreground">
                        {req.unit}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Right Panel: Match Results */}
        <div className="space-y-4">
          <h2 className="text-base font-semibold">
            Match Results ({sortedMatches.length} models)
          </h2>
          {sortedMatches.map((match) => {
            const isExpanded = expandedCard === match.component_id;
            return (
              <Card key={match.component_id} className="overflow-hidden">
                <div
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/30 transition-colors"
                  onClick={() =>
                    setExpandedCard(isExpanded ? null : match.component_id)
                  }
                >
                  <div className="flex items-center gap-4">
                    <ScoreRing score={match.match_percentage} size={48} />
                    <div>
                      <p className="font-semibold">{match.model_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {match.oem_name}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="flex items-center gap-2">
                        <Progress
                          value={match.match_percentage}
                          className="w-24 h-2"
                        />
                        <span
                          className={cn(
                            "text-sm font-semibold",
                            scoreColor(match.match_percentage)
                          )}
                        >
                          {match.match_percentage}%
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {match.passed}/{match.total} passed
                      </p>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                </div>

                {isExpanded && (
                  <div className="border-t px-4 pb-4">
                    <table className="w-full text-sm mt-3">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="py-2 px-3 text-left font-medium">
                            Parameter
                          </th>
                          <th className="py-2 px-3 text-left font-medium">
                            Required
                          </th>
                          <th className="py-2 px-3 text-left font-medium">
                            OEM Value
                          </th>
                          <th className="py-2 px-3 text-center font-medium">
                            Match
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {match.details.map((detail, i) => (
                          <tr
                            key={i}
                            className={cn(
                              "border-b last:border-0",
                              detail.match ? "bg-green-50/50 dark:bg-green-950/20" : "bg-red-50/50 dark:bg-red-950/20"
                            )}
                          >
                            <td className="py-2 px-3 font-medium">
                              {detail.parameter}
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">
                              {detail.required}
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">
                              {detail.oem_value}
                            </td>
                            <td className="py-2 px-3 text-center">
                              {detail.match ? (
                                <CheckCircle2 className="h-4 w-4 text-green-600 inline" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-500 inline" />
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            );
          })}

          {sortedMatches.length === 0 && (
            <Card className="py-12">
              <CardContent className="text-center text-muted-foreground">
                No matching models found for this RFQ.
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
