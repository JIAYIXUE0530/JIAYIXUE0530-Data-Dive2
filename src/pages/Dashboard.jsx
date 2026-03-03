import { useState, useEffect } from 'react'
import ReportCard from '../components/ReportCard'
import StatsOverview from '../components/StatsOverview'
import EmptyState from '../components/EmptyState'

function Dashboard() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      const response = await fetch('/outputs/reports/reports-index.json')
      if (response.ok) {
        const data = await response.json()
        const sortedReports = (data.reports || []).sort((a, b) => {
          return new Date(b.created_at) - new Date(a.created_at)
        })
        setReports(sortedReports)
      } else {
        setReports([])
      }
    } catch (err) {
      console.log('No reports found:', err)
      setReports([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-[var(--text-muted)] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-[var(--text-muted)] text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col">
      {/* Header */}
      <header className="border-b border-[var(--border-subtle)] sticky top-0 z-50 bg-[var(--bg-primary)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="opacity-0 animate-fade-in-up">
              <h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1>
            </div>
            <div className="flex items-center gap-6">
              <div className="opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                <span className="font-mono text-xs text-[var(--text-muted)]">{reports.length} 份报告</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto px-6 lg:px-8 py-12 lg:py-16">
        {reports.length > 0 ? (
          <>
            <div className="mb-12 opacity-0 animate-fade-in-up">
              <h2 className="font-display text-4xl lg:text-5xl font-light text-[var(--text-primary)] mb-4">分析存档</h2>
              <p className="text-[var(--text-secondary)] max-w-xl">所有数据分析报告与洞察结论的归档。</p>
            </div>

            <StatsOverview reports={reports} />

            <section>
              <div className="mb-8 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">全部报告</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 lg:pl-6">
                {reports.map((report, index) => (
                  <ReportCard key={report.id} report={report} index={index} />
                ))}
              </div>
            </section>
          </>
        ) : (
          <EmptyState />
        )}
      </main>

      <footer className="border-t border-[var(--border-subtle)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <p className="font-mono text-xs text-[var(--text-muted)]">Data Dive</p>
            <p className="text-xs text-[var(--text-muted)]">
              运行 <code className="font-mono px-1 py-0.5 bg-[var(--bg-secondary)] rounded">/analyze-data</code> 创建新分析
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard