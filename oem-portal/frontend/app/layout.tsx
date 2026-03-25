import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "UnityESS - Technical Compliance Portal",
  description: "BESS component technical approval lifecycle management",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
