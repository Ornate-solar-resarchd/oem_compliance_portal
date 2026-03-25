"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { AuthProvider, useAuth } from "@/lib/auth"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"

function PortalGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) router.replace("/login")
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4 bg-surface">
        <div className="relative">
          <div className="w-12 h-12 rounded-2xl bg-brand-gradient flex items-center justify-center animate-bounce-subtle shadow-glow">
            <span className="text-white font-black text-lg">U</span>
          </div>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="text-sm font-semibold text-slate-700">Loading Portal</div>
          <div className="flex gap-1 mt-2">
            <div className="w-1.5 h-1.5 rounded-full bg-brand animate-bounce" style={{ animationDelay: "0ms" }} />
            <div className="w-1.5 h-1.5 rounded-full bg-brand animate-bounce" style={{ animationDelay: "150ms" }} />
            <div className="w-1.5 h-1.5 rounded-full bg-brand animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-surface bg-mesh-gradient">
      <Sidebar />
      <div className="ml-[230px]">
        <Header />
        <main className="p-6 animate-fade-in-up" style={{ animationFillMode: "both" }}>
          {children}
        </main>
      </div>
    </div>
  )
}

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <PortalGuard>{children}</PortalGuard>
    </AuthProvider>
  )
}
