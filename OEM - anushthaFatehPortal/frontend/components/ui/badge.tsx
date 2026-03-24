import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-lg px-2.5 py-1 text-[11px] font-semibold transition-all duration-200 leading-none",
  {
    variants: {
      variant: {
        default: "bg-slate-100 text-slate-600",
        pass: "bg-emerald-50 text-emerald-600 ring-1 ring-emerald-100",
        fail: "bg-red-50 text-red-600 ring-1 ring-red-100",
        waived: "bg-slate-50 text-slate-500 ring-1 ring-slate-100",
        pending: "bg-amber-50 text-amber-600 ring-1 ring-amber-100",
        brand: "bg-brand-50 text-brand-600 ring-1 ring-brand-100",
        blue: "bg-blue-50 text-blue-600 ring-1 ring-blue-100",
        purple: "bg-purple-50 text-purple-600 ring-1 ring-purple-100",
        approved: "bg-emerald-50 text-emerald-600 ring-1 ring-emerald-100",
        review: "bg-amber-50 text-amber-600 ring-1 ring-amber-100",
        active: "bg-brand-50 text-brand-600 ring-1 ring-brand-200 animate-pulse-glow",
        outline: "bg-transparent border border-slate-200 text-slate-600",
        secondary: "bg-slate-50 text-slate-500",
      },
    },
    defaultVariants: { variant: "default" },
  }
)

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
