"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { matchRFQ } from "@/lib/api";
import { cn, scoreColor } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScoreRing } from "@/components/shared/score-ring";
import { ArrowLeft, Printer, Download, Loader2 } from "lucide-react";

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

interface MatchData {
  rfq_id: string;
  customer: string;
  matches: MatchResult[];
}

export default function DiversifySheetPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [matchData, setMatchData] = useState<MatchData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await matchRFQ(id);
        setMatchData(res);
      } catch (err) {
        console.error("Failed to fetch match data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!matchData || matchData.matches.length === 0) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        No match data available for this RFQ.
      </div>
    );
  }

  // Take top 3 matching models
  const top3 = [...matchData.matches]
    .sort((a, b) => b.match_percentage - a.match_percentage)
    .slice(0, 3);

  // Collect all unique parameter names from the first model's details
  const allParameters = top3[0]?.details.map((d) => d.parameter) || [];

  // Build a lookup: model_name -> parameter -> detail
  const modelDetails: Record<string, Record<string, MatchDetail>> = {};
  top3.forEach((model) => {
    modelDetails[model.component_id] = {};
    model.details.forEach((d) => {
      modelDetails[model.component_id][d.parameter] = d;
    });
  });

  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="space-y-6">
      {/* Navigation */}
      <div className="flex items-center justify-between print:hidden">
        <Button variant="ghost" onClick={() => router.push(`/rfq/${id}`)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to RFQ
        </Button>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.print()}>
            <Printer className="mr-2 h-4 w-4" />
            Print
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Diversify Document */}
      <div className="max-w-5xl mx-auto bg-white dark:bg-card rounded-lg border shadow-sm print:shadow-none print:border-0">
        {/* Document Header */}
        <div className="border-b px-8 py-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                Diversify Analysis
              </h1>
              <p className="text-muted-foreground mt-1">
                Side-by-Side Model Comparison for {matchData.customer}
              </p>
            </div>
            <div className="text-right text-sm text-muted-foreground">
              <p>Date: {today}</p>
              <p>RFQ ID: {matchData.rfq_id}</p>
            </div>
          </div>
        </div>

        {/* Model Summary Cards */}
        <div className="px-8 py-6 border-b">
          <div className={cn("grid gap-4", `grid-cols-${Math.min(top3.length, 3)}`)}>
            {top3.map((model, idx) => (
              <Card key={model.component_id} className="text-center py-4">
                <CardContent className="p-0 space-y-2">
                  <div className="flex justify-center">
                    <ScoreRing score={model.match_percentage} size={56} />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{model.model_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {model.oem_name}
                    </p>
                  </div>
                  <Badge
                    variant="outline"
                    className={cn(
                      idx === 0
                        ? "bg-green-50 text-green-700 border-green-200 dark:bg-green-950/30 dark:text-green-400"
                        : ""
                    )}
                  >
                    {idx === 0 ? "Best Match" : `Option ${idx + 1}`}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Side-by-Side Comparison Table */}
        <div className="px-8 py-6">
          <h2 className="text-base font-semibold mb-4">
            Parameter Comparison
          </h2>
          <div className="rounded-md border overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted/50 border-b">
                  <th className="py-2.5 px-4 text-left font-medium min-w-[200px]">
                    Parameter
                  </th>
                  <th className="py-2.5 px-4 text-left font-medium min-w-[100px]">
                    Required
                  </th>
                  {top3.map((model) => (
                    <th
                      key={model.component_id}
                      className="py-2.5 px-4 text-left font-medium min-w-[140px]"
                    >
                      <div>{model.model_name}</div>
                      <div className="text-xs font-normal text-muted-foreground">
                        {model.oem_name}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {allParameters.map((param, i) => {
                  const requiredValue =
                    modelDetails[top3[0].component_id]?.[param]?.required || "-";

                  return (
                    <tr
                      key={i}
                      className={cn(
                        "border-b last:border-0",
                        i % 2 === 0
                          ? "bg-white dark:bg-card"
                          : "bg-muted/20"
                      )}
                    >
                      <td className="py-2.5 px-4 font-medium">{param}</td>
                      <td className="py-2.5 px-4 font-mono text-xs">
                        {requiredValue}
                      </td>
                      {top3.map((model) => {
                        const detail =
                          modelDetails[model.component_id]?.[param];
                        if (!detail) {
                          return (
                            <td
                              key={model.component_id}
                              className="py-2.5 px-4 text-muted-foreground"
                            >
                              N/A
                            </td>
                          );
                        }
                        return (
                          <td
                            key={model.component_id}
                            className={cn(
                              "py-2.5 px-4 font-mono text-xs",
                              detail.match
                                ? "bg-green-50 dark:bg-green-950/20"
                                : "bg-red-50 dark:bg-red-950/20"
                            )}
                          >
                            <div className="flex items-center gap-2">
                              <span>{detail.oem_value}</span>
                              {detail.match ? (
                                <Badge
                                  variant="outline"
                                  className="bg-green-100 text-green-700 border-green-200 text-[10px] px-1.5 py-0 dark:bg-green-950/40 dark:text-green-400"
                                >
                                  Pass
                                </Badge>
                              ) : (
                                <Badge
                                  variant="outline"
                                  className="bg-red-100 text-red-700 border-red-200 text-[10px] px-1.5 py-0 dark:bg-red-950/40 dark:text-red-400"
                                >
                                  Fail
                                </Badge>
                              )}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}

                {/* Summary Row */}
                <tr className="bg-muted/50 border-t-2 font-semibold">
                  <td className="py-3 px-4">Match Percentage</td>
                  <td className="py-3 px-4">-</td>
                  {top3.map((model) => (
                    <td
                      key={model.component_id}
                      className="py-3 px-4"
                    >
                      <span className={cn(scoreColor(model.match_percentage))}>
                        {model.match_percentage}%
                      </span>
                      <span className="text-xs font-normal text-muted-foreground ml-2">
                        ({model.passed}/{model.total})
                      </span>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t px-8 py-4 text-xs text-muted-foreground text-center">
          Generated by BESS Technical Compliance Portal &middot; {today}
        </div>
      </div>
    </div>
  );
}
