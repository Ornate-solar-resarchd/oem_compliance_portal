"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth"
import { cn } from "@/lib/utils"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import {
  User,
  Bell,
  Users,
  Server,
  Mail,
  Shield,
  Building2,
  Database,
  HardDrive,
  Wifi,
  Activity,
} from "lucide-react"

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

type TabKey = "profile" | "notifications" | "team" | "system"

interface TeamMember {
  name: string
  email: string
  role: string
  status: "active" | "inactive"
}

interface ServiceStatus {
  name: string
  status: "healthy" | "degraded" | "down"
  icon: typeof Database
  latency?: string
}

/* ------------------------------------------------------------------ */
/*  Demo Data                                                          */
/* ------------------------------------------------------------------ */

const TEAM_MEMBERS: TeamMember[] = [
  { name: "Anushthan Fateh", email: "anushthan@ornate.energy", role: "Admin", status: "active" },
  { name: "Priyank Rajput", email: "priyank@ornate.energy", role: "Tech Lead", status: "active" },
  { name: "Rahul Sharma", email: "rahul@ornate.energy", role: "Engineer", status: "active" },
  { name: "Neha Gupta", email: "neha@ornate.energy", role: "Engineer", status: "active" },
  { name: "Vikram Singh", email: "vikram@ornate.energy", role: "Manager", status: "active" },
  { name: "Aisha Patel", email: "aisha@ornate.energy", role: "Analyst", status: "inactive" },
  { name: "Karan Mehta", email: "karan@ornate.energy", role: "Engineer", status: "active" },
]

const SERVICES: ServiceStatus[] = [
  { name: "Database (PostgreSQL)", status: "healthy", icon: Database, latency: "2ms" },
  { name: "Redis Cache", status: "healthy", icon: Server, latency: "0.5ms" },
  { name: "MinIO Storage", status: "healthy", icon: HardDrive, latency: "8ms" },
  { name: "API Gateway", status: "healthy", icon: Wifi, latency: "12ms" },
]

const TABS: { key: TabKey; label: string; icon: typeof User }[] = [
  { key: "profile", label: "Profile", icon: User },
  { key: "notifications", label: "Notifications", icon: Bell },
  { key: "team", label: "Team", icon: Users },
  { key: "system", label: "System Health", icon: Server },
]

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function SettingsPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<TabKey>("profile")

  /* Notification toggles (visual only) */
  const [emailAlerts, setEmailAlerts] = useState(true)
  const [inAppNotifs, setInAppNotifs] = useState(true)
  const [dailyDigest, setDailyDigest] = useState(false)

  /* Avatar initials */
  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n: string) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U"

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your account and system configuration</p>
      </div>

      <div className="flex gap-6">
        {/* Tab navigation */}
        <div className="w-[220px] shrink-0">
          <Card className="border-0 shadow-sm">
            <CardContent className="p-2">
              <nav className="space-y-1">
                {TABS.map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-left",
                      activeTab === tab.key
                        ? "bg-primary/10 text-primary"
                        : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                    )}
                  >
                    <tab.icon className="h-4 w-4" />
                    {tab.label}
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Tab content */}
        <div className="flex-1 min-w-0">
          {/* Profile Tab */}
          {activeTab === "profile" && (
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="text-base">Profile Information</CardTitle>
                <CardDescription>Your account details and personal information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Avatar */}
                <div className="flex items-center gap-5">
                  <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-2xl font-bold text-primary">{initials}</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {user?.name || "Current User"}
                    </h3>
                    <p className="text-sm text-muted-foreground">{user?.email || "user@ornate.energy"}</p>
                  </div>
                </div>

                {/* Fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div>
                    <label className="text-sm font-medium mb-1.5 block flex items-center gap-1.5">
                      <User className="h-3.5 w-3.5 text-muted-foreground" />
                      Full Name
                    </label>
                    <Input defaultValue={user?.name || "Current User"} readOnly className="bg-slate-50" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block flex items-center gap-1.5">
                      <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                      Email
                    </label>
                    <Input defaultValue={user?.email || "user@ornate.energy"} readOnly className="bg-slate-50" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block flex items-center gap-1.5">
                      <Shield className="h-3.5 w-3.5 text-muted-foreground" />
                      Role
                    </label>
                    <Input defaultValue={user?.role || "Engineer"} readOnly className="bg-slate-50" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block flex items-center gap-1.5">
                      <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                      Organization
                    </label>
                    <Input defaultValue={user?.org || "Ornate Energy"} readOnly className="bg-slate-50" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Notifications Tab */}
          {activeTab === "notifications" && (
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="text-base">Notification Preferences</CardTitle>
                <CardDescription>Control how you receive alerts and updates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Toggle: Email Alerts */}
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                      <Mail className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">Email Alerts</p>
                      <p className="text-xs text-muted-foreground">
                        Receive workflow updates and approvals via email
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setEmailAlerts(!emailAlerts)}
                    className={cn(
                      "relative w-11 h-6 rounded-full transition-colors",
                      emailAlerts ? "bg-primary" : "bg-slate-200"
                    )}
                  >
                    <span
                      className={cn(
                        "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform",
                        emailAlerts && "translate-x-5"
                      )}
                    />
                  </button>
                </div>

                {/* Toggle: In-App Notifications */}
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
                      <Bell className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">In-App Notifications</p>
                      <p className="text-xs text-muted-foreground">
                        Show notifications within the portal interface
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setInAppNotifs(!inAppNotifs)}
                    className={cn(
                      "relative w-11 h-6 rounded-full transition-colors",
                      inAppNotifs ? "bg-primary" : "bg-slate-200"
                    )}
                  >
                    <span
                      className={cn(
                        "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform",
                        inAppNotifs && "translate-x-5"
                      )}
                    />
                  </button>
                </div>

                {/* Toggle: Daily Digest */}
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                      <Activity className="h-5 w-5 text-amber-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">Daily Digest</p>
                      <p className="text-xs text-muted-foreground">
                        Get a daily summary of compliance activity
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setDailyDigest(!dailyDigest)}
                    className={cn(
                      "relative w-11 h-6 rounded-full transition-colors",
                      dailyDigest ? "bg-primary" : "bg-slate-200"
                    )}
                  >
                    <span
                      className={cn(
                        "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform",
                        dailyDigest && "translate-x-5"
                      )}
                    />
                  </button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Team Tab */}
          {activeTab === "team" && (
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="text-base">Team Members</CardTitle>
                <CardDescription>{TEAM_MEMBERS.length} members in your organization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Member</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Role</th>
                        <th className="text-left py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {TEAM_MEMBERS.map((member) => {
                        const memberInitials = member.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")
                          .toUpperCase()

                        return (
                          <tr
                            key={member.email}
                            className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors"
                          >
                            <td className="py-3 px-3">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                  <span className="text-xs font-bold text-primary">{memberInitials}</span>
                                </div>
                                <span className="font-medium text-slate-900">{member.name}</span>
                              </div>
                            </td>
                            <td className="py-3 px-3 text-slate-600">{member.email}</td>
                            <td className="py-3 px-3">
                              <Badge variant="outline" className="text-[10px]">
                                {member.role}
                              </Badge>
                            </td>
                            <td className="py-3 px-3">
                              <div className="flex items-center gap-1.5">
                                <span
                                  className={cn(
                                    "w-2 h-2 rounded-full",
                                    member.status === "active" ? "bg-emerald-500" : "bg-slate-300"
                                  )}
                                />
                                <span
                                  className={cn(
                                    "text-xs capitalize",
                                    member.status === "active" ? "text-emerald-600" : "text-slate-400"
                                  )}
                                >
                                  {member.status}
                                </span>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* System Health Tab */}
          {activeTab === "system" && (
            <div className="space-y-6">
              {/* Service status cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {SERVICES.map((service) => (
                  <Card key={service.name} className="border-0 shadow-sm">
                    <CardContent className="pt-5 pb-5">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center">
                          <service.icon className="h-6 w-6 text-slate-500" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="text-sm font-semibold text-slate-900">{service.name}</h3>
                            <div className="flex items-center gap-1.5">
                              <span
                                className={cn(
                                  "w-2.5 h-2.5 rounded-full",
                                  service.status === "healthy"
                                    ? "bg-emerald-500"
                                    : service.status === "degraded"
                                    ? "bg-amber-500"
                                    : "bg-red-500"
                                )}
                              />
                              <span
                                className={cn(
                                  "text-xs font-medium capitalize",
                                  service.status === "healthy"
                                    ? "text-emerald-600"
                                    : service.status === "degraded"
                                    ? "text-amber-600"
                                    : "text-red-600"
                                )}
                              >
                                {service.status}
                              </span>
                            </div>
                          </div>
                          {service.latency && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Latency: {service.latency}
                            </p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Storage usage */}
              <Card className="border-0 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Storage Usage</CardTitle>
                  <CardDescription>MinIO object storage utilization</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-slate-700">Documents & Datasheets</span>
                        <span className="text-sm font-semibold text-slate-900">24.3 GB / 100 GB</span>
                      </div>
                      <Progress value={24.3} className="h-3" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-slate-700">Report Exports</span>
                        <span className="text-sm font-semibold text-slate-900">8.7 GB / 50 GB</span>
                      </div>
                      <Progress value={17.4} className="h-3" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-slate-700">Database Backups</span>
                        <span className="text-sm font-semibold text-slate-900">12.1 GB / 50 GB</span>
                      </div>
                      <Progress value={24.2} className="h-3" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
