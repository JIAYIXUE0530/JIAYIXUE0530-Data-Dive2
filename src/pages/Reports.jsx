import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import ReportCard from '../components/ReportCard'
import StatsOverview from '../components/StatsOverview'

function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [generateDate, setGenerateDate] = useState('')
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState('')
  const [generateSuccess, setGenerateSuccess] = useState('')

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

  const handleGenerateReport = async () => {
    if (!generateDate) {
      setGenerateError('请输入日期')
      return
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(generateDate)) {
      setGenerateError('日期格式错误，请使用 YYYY-MM-DD 格式')
      return
    }

    setGenerating(true)
    setGenerateError('')
    setGenerateSuccess('')

    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ date: generateDate })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setGenerateSuccess(data.message)
        await loadReports()
        setGenerateDate('')
      } else {
        setGenerateError(data.error || '生成报告失败')
      }
    } catch (err) {
      setGenerateError('网络错误，请稍后重试')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-[var(--text-muted)] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-[var(--text-muted)] text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-[var(--bg-primary)] flex flex-col">
      <header className="border-b border-[var(--border-subtle)] flex-shrink-0 bg-[var(--bg-primary)]">
        <div className="w-full px-16">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="opacity-0 animate-fade-in-up">
              <h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1>
            </Link>
            <nav className="flex items-center gap-6">
              <Link to="/reports" className="text-sm text-[var(--accent-forest)]">日报</Link>
              <Link to="/crawler" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">数据爬取</Link>
              <Link to="/data-entry" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-auto">
        <div className="w-full px-16 py-8">
        {reports.length > 0 ? (
          <>
            <div className="mb-12 opacity-0 animate-fade-in-up">
              <h2 className="font-display text-4xl lg:text-5xl font-light text-[var(--text-primary)] mb-4">日报存档</h2>
              <p className="text-[var(--text-secondary)] max-w-xl">所有竞品日报的归档，点击查看详细分析。</p>
            </div>

            <StatsOverview reports={reports} />

            <section className="mb-12 opacity-0 animate-fade-in-up">
              <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-6 border border-[var(--border-subtle)]">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">生成竞品日报</h3>
                <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                  <div className="flex-1 w-full sm:w-auto">
                    <input
                      type="text"
                      value={generateDate}
                      onChange={(e) => setGenerateDate(e.target.value)}
                      placeholder="输入日期 (YYYY-MM-DD)"
                      className="w-full sm:w-64 px-4 py-2.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent-forest)] transition-colors"
                    />
                  </div>
                  <button
                    onClick={handleGenerateReport}
                    disabled={generating}
                    className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      generating
                        ? 'bg-[var(--text-muted)] text-white cursor-not-allowed'
                        : 'bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 active:scale-[0.98]'
                    }`}
                  >
                    {generating ? (
                      <span className="flex items-center gap-2">
                        <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        生成中...
                      </span>
                    ) : (
                      '生成竞品日报'
                    )}
                  </button>
                </div>
                {generateError && (
                  <p className="mt-3 text-sm text-red-500">{generateError}</p>
                )}
                {generateSuccess && (
                  <p className="mt-3 text-sm text-[var(--accent-forest)]">{generateSuccess}</p>
                )}
              </div>
            </section>

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
          <div className="text-center py-16">
            <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-6 border border-[var(--border-subtle)] max-w-md mx-auto mb-8">
              <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">生成竞品日报</h3>
              <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                <div className="flex-1 w-full sm:w-auto">
                  <input
                    type="text"
                    value={generateDate}
                    onChange={(e) => setGenerateDate(e.target.value)}
                    placeholder="输入日期 (YYYY-MM-DD)"
                    className="w-full sm:w-64 px-4 py-2.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent-forest)] transition-colors"
                  />
                </div>
                <button
                  onClick={handleGenerateReport}
                  disabled={generating}
                  className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    generating
                      ? 'bg-[var(--text-muted)] text-white cursor-not-allowed'
                      : 'bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 active:scale-[0.98]'
                  }`}
                >
                  {generating ? (
                    <span className="flex items-center gap-2">
                      <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      生成中...
                    </span>
                  ) : (
                    '生成竞品日报'
                  )}
                </button>
              </div>
              {generateError && (
                <p className="mt-3 text-sm text-red-500">{generateError}</p>
              )}
              {generateSuccess && (
                <p className="mt-3 text-sm text-[var(--accent-forest)]">{generateSuccess}</p>
              )}
            </div>
            <p className="text-[var(--text-muted)]">暂无报告，请先生成日报</p>
          </div>
        )}
        </div>
      </main>

      <footer className="border-t border-[var(--border-subtle)] flex-shrink-0">
        <div className="w-full px-16 py-4">
          <div className="flex justify-between items-center">
            <p className="font-mono text-xs text-[var(--text-muted)]">Data Dive</p>
            <p className="text-xs text-[var(--text-muted)]">竞品销量数据分析平台</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Reports
