import { useState, useEffect } from 'react'

function AnimatedNumber({ value, duration = 800 }) {
  const [displayValue, setDisplayValue] = useState(0)
  useEffect(() => {
    let startTime, animationFrame
    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      setDisplayValue(Math.floor((1 - Math.pow(1 - progress, 3)) * value))
      if (progress < 1) animationFrame = requestAnimationFrame(animate)
    }
    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])
  return <span>{displayValue}</span>
}

function StatsOverview({ reports = [] }) {
  const totalReports = reports.length
  const now = new Date()
  const thisMonthReports = reports.filter(r => {
    const d = new Date(r.created_at)
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).length
  const totalHighImportance = reports.reduce((sum, r) => sum + (r.stats?.high_importance || 0), 0)

  return (
    <div className="mb-16 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
      <div className="flex flex-wrap items-baseline gap-x-12 gap-y-4 py-6 border-y border-[var(--border-subtle)]">
        <div className="flex items-baseline gap-3">
          <span className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)]"><AnimatedNumber value={totalReports} /></span>
          <span className="text-sm text-[var(--text-muted)] font-medium">份报告</span>
        </div>
        <div className="hidden sm:block w-px h-8 bg-[var(--border-subtle)]" />
        <div className="flex items-baseline gap-3">
          <span className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)]"><AnimatedNumber value={thisMonthReports} /></span>
          <span className="text-sm text-[var(--text-muted)] font-medium">本月新增</span>
        </div>
        <div className="hidden sm:block w-px h-8 bg-[var(--border-subtle)]" />
        <div className="flex items-baseline gap-3">
          <span className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)]"><AnimatedNumber value={totalHighImportance} /></span>
          <span className="text-sm text-[var(--text-muted)] font-medium">关键发现</span>
        </div>
      </div>
    </div>
  )
}

export default StatsOverview