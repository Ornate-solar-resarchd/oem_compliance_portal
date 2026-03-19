import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(n: number): string {
  return n.toLocaleString("en-IN")
}

export function scoreColor(score: number): string {
  if (score >= 90) return "text-emerald-500"
  if (score >= 75) return "text-brand"
  return "text-red-500"
}

export function scoreBg(score: number): string {
  if (score >= 90) return "bg-emerald-500"
  if (score >= 75) return "bg-brand"
  return "bg-red-500"
}
