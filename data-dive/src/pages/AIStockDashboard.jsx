import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function AIStockDashboard() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalReports: 0,
    avgConfidence: 0,
    bullishCount: 0,
    bearishCount: 0
  })

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      console.log('开始加载报告索引...')
      const response = await fetch('/outputs/ai-stock-reports/reports-index.json')
      console.log('响应状态:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('加载的数据:', data)
        const sortedReports = (data.reports || []).sort((a, b) => {
          return new Date(b.created_at) - new Date(a.created_at)
        })
        console.log('排序后的报告:', sortedReports)
        setReports(sortedReports)
        
        const totalBullish = sortedReports.reduce((sum, r) => sum + (r.bullish_count || 0), 0)
        const totalBearish = sortedReports.reduce((sum, r) => sum + (r.bearish_count || 0), 0)
        console.log('统计数据:', { totalBullish, totalBearish, totalReports: sortedReports.length })
        
        setStats({
          totalReports: sortedReports.length,
          avgConfidence: 7.4,
          bullishCount: totalBullish,
          bearishCount: totalBearish
        })
      } else {
        console.error('加载失败:', response.statusText)
      }
    } catch (err) {
      console.error('加载报告出错:', err)
    } finally {
      setLoading(false)
    }
  }

  const getMarketConditionColor = (condition) => {
    switch (condition) {
      case 'bullish': return 'text-green-500'
      case 'bearish': return 'text-red-500'
      case 'cautiously_bullish': return 'text-yellow-500'
      case 'cautiously_bearish': return 'text-orange-500'
      default: return 'text-gray-500'
    }
  }

  const getMarketConditionText = (condition) => {
    switch (condition) {
      case 'bullish': return '看涨'
      case 'bearish': return '看跌'
      case 'cautiously_bullish': return '谨慎看涨'
      case 'cautiously_bearish': return '谨慎看跌'
      case 'neutral': return '中性'
      default: return condition
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-[var(--text-muted)] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-[var(--text-muted)] text-sm">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <header className="border-b border-[var(--border-subtle)] sticky top-0 z-50 bg-[var(--bg-primary)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/" className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
                ← Data Dive
              </Link>
              <span className="text-[var(--border-subtle)]">|</span>
              <h1 className="font-display text-xl text-[var(--text-primary)]">🤖 AI选股看板</h1>
            </div>
            <div className="font-mono text-xs text-[var(--text-muted)]">
              {stats.totalReports} 份报告
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-12 lg:py-16">
        <div className="mb-12">
          <h2 className="font-display text-4xl lg:text-5xl font-light text-[var(--text-primary)] mb-4">
            AI选股日报
          </h2>
          <p className="text-[var(--text-secondary)] max-w-xl">
            每日AI驱动的行业/ETF投资建议，记录判断逻辑，追踪历史表现
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">总报告数</div>
            <div className="text-3xl font-light text-[var(--text-primary)]">{stats.totalReports}</div>
          </div>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">平均置信度</div>
            <div className="text-3xl font-light text-[var(--text-primary)]">{stats.avgConfidence.toFixed(1)}</div>
          </div>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">看涨推荐</div>
            <div className="text-3xl font-light text-green-500">{stats.bullishCount}</div>
          </div>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">看跌推荐</div>
            <div className="text-3xl font-light text-red-500">{stats.bearishCount}</div>
          </div>
        </div>

        {reports.length > 0 ? (
          <section>
            <div className="mb-8">
              <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">历史报告</h3>
            </div>
            <div className="space-y-4">
              {reports.map((report, index) => (
                <Link
                  key={report.id}
                  to={`/ai-stock-report/${report.id}`}
                  className="block bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)] hover:border-[var(--accent)] transition-all duration-200 group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-display text-lg text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">
                          {report.title}
                        </h4>
                        <span className={`font-mono text-xs ${getMarketConditionColor(report.market_condition)}`}>
                          {getMarketConditionText(report.market_condition)}
                        </span>
                      </div>
                      <div className="flex items-center gap-6 text-sm text-[var(--text-muted)]">
                        <span className="font-mono">{new Date(report.created_at).toLocaleDateString('zh-CN')}</span>
                        <span>VIX: {report.vix}</span>
                        <span>{report.total_recommendations} 个推荐</span>
                        <span className="text-green-500">{report.high_confidence_count} 个高置信度</span>
                      </div>
                    </div>
                    <div className="text-[var(--text-muted)] group-hover:text-[var(--accent)] transition-colors">
                      →
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl text-[var(--text-primary)] mb-2">暂无报告</h3>
            <p className="text-[var(--text-muted)]">
              运行 AI 选股 skill 生成第一份报告
            </p>
          </div>
        )}
      </main>

      <footer className="border-t border-[var(--border-subtle)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <p className="font-mono text-xs text-[var(--text-muted)]">AI Stock Picker Dashboard</p>
            <p className="text-xs text-[var(--text-muted)]">
              ⚠️ 仅供研究和教育用途，不构成投资建议
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default AIStockDashboard
