"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { AuthProvider, useAuth } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Eye, EyeOff, Zap, LogIn, Loader2 } from "lucide-react"


function LoginForm() {
  const { login } = useAuth()
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPw, setShowPw] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const user = await login(email.trim(), password)
      router.replace("/oems")
    } catch (err: any) {
      setError(err.message || "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-navy-gradient flex items-center justify-center p-6 relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand/5 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl animate-float" style={{ animationDelay: "3s" }} />
      <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl animate-float" style={{ animationDelay: "1.5s" }} />

      <div className="relative z-10 w-full max-w-[440px] space-y-5 animate-fade-in-up">
        {/* Card */}
        <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          {/* Header */}
          <div className="px-8 pt-8 pb-6 text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-gradient shadow-glow mb-5 animate-bounce-subtle">
              <Zap className="w-7 h-7 text-white" strokeWidth={2.5} />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Technical <span className="gradient-text">Compliance</span> Portal
            </h1>
            <p className="text-sm text-slate-400 mt-2">
              UnityESS · Secure internal access
            </p>
          </div>

          {/* Form */}
          <div className="px-8 pb-8">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Email</label>
                <Input
                  type="email"
                  placeholder="you@ornatesolar.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 focus:border-brand/50 focus:bg-white/10 focus:ring-brand/20 h-11"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Password</label>
                <div className="relative">
                  <Input
                    type={showPw ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                    className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 focus:border-brand/50 focus:bg-white/10 focus:ring-brand/20 h-11 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPw(p => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-sm text-red-400 animate-scale-in">
                  {error}
                </div>
              )}

              <Button type="submit" disabled={loading} className="w-full h-11 text-sm mt-2">
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Signing in...</>
                ) : (
                  <><LogIn className="w-4 h-4" /> Sign In</>
                )}
              </Button>
            </form>
          </div>
        </div>

        <p className="text-center text-[11px] text-slate-600">
          Ornate Agencies Pvt. Ltd. · Internal use only
        </p>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  )
}
