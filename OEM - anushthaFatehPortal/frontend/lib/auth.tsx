"use client"

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react"
import { login as apiLogin } from "./api"

interface User {
  id: string
  email: string
  name: string
  role: string
  organisation: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem("tcp_token")
    if (stored) {
      try {
        const payload = JSON.parse(atob(stored.split(".")[1]))
        if (payload.exp && payload.exp * 1000 < Date.now()) {
          clearSession()
        } else {
          setToken(stored)
          setUser({
            id: payload.sub,
            email: payload.email,
            name: payload.name,
            role: payload.role,
            organisation: payload.org,
          })
        }
      } catch {
        clearSession()
      }
    }
    setLoading(false)
  }, [])

  const clearSession = useCallback(() => {
    localStorage.removeItem("tcp_token")
    setToken(null)
    setUser(null)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const data = await apiLogin(email, password)
    localStorage.setItem("tcp_token", data.token)
    setToken(data.token)
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(() => {
    clearSession()
  }, [clearSession])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be inside AuthProvider")
  return ctx
}

export const INTERNAL_ROLES = ["admin", "engineer", "reviewer", "commercial"]
