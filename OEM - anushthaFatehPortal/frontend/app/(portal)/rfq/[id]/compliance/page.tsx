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

export default function ComplianceSheetPage() {
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

  // Pick the best matching model
  const bestMatch = [...matchData.matches].sort(
    (a, b) => b.match_percentage - a.match_percentage
  )[0];

  const failed = bestMatch.total - bestMatch.passed;
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

      {/* Compliance Document */}
      <div className="max-w-4xl mx-auto bg-white dark:bg-card rounded-lg border shadow-sm print:shadow-none print:border-0">
        {/* Document Header */}
        <div className="border-b px-8 py-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                Compliance Sheet
              </h1>
              <p className="text-muted-foreground mt-1">
                Technical Parameter Compliance Analysis
              </p>
            </div>
            <div className="text-right text-sm text-muted-foreground">
              <p>Date: {today}</p>
              <p>RFQ ID: {matchData.rfq_id}</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Customer:</span>{" "}
              <span className="font-medium">{matchData.customer}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Recommended Model:</span>{" "}
              <span className="font-medium">{bestMatch.model_name}</span>
            </div>
            <div>
              <span className="text-muted-foreground">OEM:</span>{" "}
              <span className="font-medium">{bestMatch.oem_name}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Compliance Score:</span>{" "}
              <span
                className={cn("font-semibold", scoreColor(bestMatch.match_percentage))}
              >
                {bestMatch.match_percentage}%
              </span>
            </div>
          </div>
        </div>

        {/* Score Summary */}
        <div className="px-8 py-6 border-b">
          <div className="flex items-center gap-8">
            <ScoreRing score={bestMatch.match_percentage} size={80} />
            <div className="grid grid-cols-3 gap-6 flex-1">
              <Card className="text-center py-4">
                <CardContent className="p-0">
                  <p className="text-3xl font-bold">{bestMatch.total}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Total Parameters
                  </p>
                </CardContent>
              </Card>
              <Card className="text-center py-4 border-green-200 bg-green-50/50 dark:bg-green-950/20">
                <CardContent className="p-0">
                  <p className="text-3xl font-bold text-green-600">
                    {bestMatch.passed}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Passed</p>
                </CardContent>
              </Card>
              <Card className="text-center py-4 border-red-200 bg-red-50/50 dark:bg-red-950/20">
                <CardContent className="p-0">
                  <p className="text-3xl font-bold text-red-500">{failed}</p>
                  <p className="text-xs text-muted-foreground mt-1">Failed</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Full Parameter Table */}
        <div className="px-8 py-6">
          <h2 className="text-base font-semibold mb-4">
            Parameter Compliance Detail
          </h2>
          <div className="rounded-md border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted/50 border-b">
                  <th className="py-2.5 px-4 text-left font-medium w-8">#</th>
                  <th className="py-2.5 px-4 text-left font-medium">
                    Parameter
                  </th>
                  <th className="py-2.5 px-4 text-left font-medium">
                    Required Value
                  </th>
                  <th className="py-2.5 px-4 text-left font-medium">
                    OEM Value
                  </th>
                  <th className="py-2.5 px-4 text-center font-medium">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {bestMatch.details.map((detail, i) => (
                  <tr
                    key={i}
                    className={cn(
                      "border-b last:border-0",
                      i % 2 === 0 ? "bg-white dark:bg-card" : "bg-muted/20"
                    )}
                  >
                    <td className="py-2.5 px-4 text-muted-foreground text-xs">
                      {i + 1}
                    </td>
                    <td className="py-2.5 px-4 font-medium">
                      {detail.parameter}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-xs">
                      {detail.required}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-xs">
                      {detail.oem_value}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      {detail.match ? (
                        <Badge
                          variant="outline"
                          className="bg-green-50 text-green-700 border-green-200 dark:bg-green-950/30 dark:text-green-400 dark:border-green-800"
                        >
                          Pass
                        </Badge>
                      ) : (
                        <Badge
                          variant="outline"
                          className="bg-red-50 text-red-700 border-red-200 dark:bg-red-950/30 dark:text-red-400 dark:border-red-800"
                        >
                          Fail
                        </Badge>
                      )}
                    </td>
                  </tr>
                ))}
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
