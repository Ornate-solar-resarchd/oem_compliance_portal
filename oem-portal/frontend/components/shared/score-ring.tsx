"use client"

import { useEffect, useState } from "react"

interface ScoreRingProps {
  score: number
  size?: number
  strokeWidth?: number
  className?: string
  animated?: boolean
}

export function ScoreRing({ score, size = 64, strokeWidth = 5, className, animated = true }: ScoreRingProps) {
  const [currentScore, setCurrentScore] = useState(animated ? 0 : score)
  const r = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * r
  const offset = circumference - (currentScore / 100) * circumference
  const color = currentScore >= 90 ? "#10b981" : currentScore >= 75 ? "#F26B4E" : "#ef4444"
  const bgColor = currentScore >= 90 ? "#ecfdf5" : currentScore >= 75 ? "#fef3f0" : "#fef2f2"

  useEffect(() => {
    if (!animated) { setCurrentScore(score); return }
    let start = 0
    const duration = 800
    const startTime = performance.now()
    const animate = (now: number) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3) // ease-out cubic
      setCurrentScore(Math.round(score * eased))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [score, animated])

  return (
    <div className={`relative inline-flex items-center justify-center ${className || ""}`} style={{ width: size, height: size }}>
      {/* Background glow */}
      <div
        className="absolute inset-1 rounded-full opacity-30 blur-sm transition-colors duration-500"
        style={{ backgroundColor: bgColor }}
      />
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#f1f5f9" strokeWidth={strokeWidth} />
        {/* Progress arc */}
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out"
          style={{ filter: `drop-shadow(0 0 4px ${color}40)` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-bold text-slate-900 leading-none tabular-nums" style={{ fontSize: size * 0.28 }}>
          {Math.round(currentScore)}
        </span>
        <span className="text-slate-400 font-medium" style={{ fontSize: Math.max(8, size * 0.13) }}>Score</span>
      </div>
    </div>
  )
}
