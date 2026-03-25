import { Badge } from "@/components/ui/badge"

const statusMap: Record<string, { label: string; variant: "pass" | "fail" | "waived" | "pending" }> = {
  pass: { label: "Pass", variant: "pass" },
  fail: { label: "Fail", variant: "fail" },
  waived: { label: "Waived", variant: "waived" },
  pending: { label: "Pending", variant: "pending" },
}

export function StatusBadge({ status }: { status: string }) {
  const s = statusMap[status] || statusMap.pending
  return <Badge variant={s.variant}>{s.label}</Badge>
}

const stageMap: Record<string, { label: string; variant: "default" | "blue" | "brand" | "purple" | "review" | "approved" | "fail" }> = {
  draft: { label: "Draft", variant: "default" },
  engineering_review: { label: "Eng. Review", variant: "blue" },
  technical_lead: { label: "Tech Lead", variant: "brand" },
  management: { label: "Management", variant: "purple" },
  customer_submission: { label: "Cust. Submission", variant: "review" },
  customer_signoff: { label: "Cust. Signoff", variant: "approved" },
  locked: { label: "Locked", variant: "fail" },
}

export function StageBadge({ stage }: { stage: string }) {
  const s = stageMap[stage] || stageMap.draft
  return <Badge variant={s.variant as any}>{s.label}</Badge>
}
