import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

function AIStockReport() {
  const { reportId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReport()
  }, [reportId])

  const loadReport = async () => {
    try {
      const response = await fetch(`/outputs/ai-stock-reports/${reportId}.json`)
      if (response.ok) {
        const data = await response.json()
        setReport(data)
      }
    } catch (err) {
      console.error('Failed to load report:', err)
    } finally {
      setLoading(false)
    }
  }

  const getMarketConditionColor = (condition) => {
    switch (condition) {
      case 'bullish': return 'bg-green-500'
      case 'bearish': return 'bg-red-500'
      case 'cautiously_bullish': return 'bg-yellow-500'
      case 'cautiously_bearish': return 'bg-orange-500'
      default: return 'bg-gray-500'
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

  if (!report) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl text-[var(--text-primary)] mb-4">报告未找到</h2>
          <Link to="/ai-stock" className="text-[var(--accent)] hover:underline">
            ← 返回看板
          </Link>
        </div>
      </div>
    )
  }

  const confidenceData = report.conclusions.map(c => ({
    name: c.metadata?.etf || c.title.substring(0, 10),
    confidence: c.metadata?.confidence || 0,
    direction: c.metadata?.direction
  }))

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <header className="border-b border-[var(--border-subtle)] sticky top-0 z-50 bg-[var(--bg-primary)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/ai-stock" className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
              ← 返回看板
            </Link>
            <div className="font-mono text-xs text-[var(--text-muted)]">
              {new Date(report.meta.generated_at).toLocaleDateString('zh-CN')}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-12 lg:py-16">
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <h1 className="font-display text-4xl lg:text-5xl font-light text-[var(--text-primary)]">
              {report.meta.title}
            </h1>
            <span className={`px-3 py-1 rounded-full text-white text-sm font-mono ${getMarketConditionColor(report.summary.market_condition)}`}>
              {getMarketConditionText(report.summary.market_condition)}
            </span>
          </div>
          <p className="text-[var(--text-secondary)] max-w-2xl">
            {report.summary.overall}
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">VIX 恐慌指数</div>
            <div className="text-3xl font-light text-[var(--text-primary)]">{report.summary.vix}</div>
          </div>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">平均置信度</div>
            <div className="text-3xl font-light text-[var(--text-primary)]">{report.summary.avg_confidence.toFixed(1)}</div>
          </div>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">看涨推荐</div>
            <div className="text-3xl font-light text-green-500">{report.summary.bullish_count}</div>
          </div>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <div className="text-[var(--text-muted)] text-xs font-mono uppercase mb-2">看跌推荐</div>
            <div className="text-3xl font-light text-red-500">{report.summary.bearish_count}</div>
          </div>
        </div>

        <div className="mb-12">
          <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider mb-6">置信度分布</h3>
          <div className="bg-[var(--bg-secondary)] rounded-lg p-6 border border-[var(--border-subtle)]">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={confidenceData} layout="vertical">
                <XAxis type="number" domain={[0, 10]} />
                <YAxis type="category" dataKey="name" width={80} />
                <Tooltip 
                  formatter={(value, name, props) => [
                    `${value}/10`,
                    '置信度'
                  ]}
                />
                <Bar dataKey="confidence" radius={[0, 4, 4, 0]}>
                  {confidenceData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.direction === 'bullish' ? '#22c55e' : '#ef4444'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="mb-12">
          <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider mb-6">投资建议</h3>
          <div className="space-y-4">
            {report.conclusions.map((conclusion) => (
              <div 
                key={conclusion.id}
                className={`bg-[var(--bg-secondary)] rounded-lg p-6 border-l-4 ${
                  conclusion.metadata?.direction === 'bullish' 
                    ? 'border-l-green-500' 
                    : 'border-l-red-500'
                } border border-[var(--border-subtle)]`}
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-display text-lg text-[var(--text-primary)]">
                    {conclusion.title}
                  </h4>
                  <span className={`font-mono text-sm px-2 py-1 rounded ${
                    conclusion.importance === 'high' 
                      ? 'bg-yellow-500/20 text-yellow-500' 
                      : 'bg-[var(--bg-primary)] text-[var(--text-muted)]'
                  }`}>
                    {conclusion.importance === 'high' ? '高置信度' : '中等置信度'}
                  </span>
                </div>
                <div className="text-[var(--text-secondary)] whitespace-pre-line mb-3">
                  {conclusion.description}
                </div>
                <div className="text-sm text-[var(--text-muted)]">
                  {conclusion.data_support}
                </div>
              </div>
            ))}
          </div>
        </div>

        {report.key_risks && report.key_risks.length > 0 && (
          <div className="mb-12">
            <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider mb-6">⚠️ 关键风险</h3>
            <div className="bg-orange-500/10 rounded-lg p-6 border border-orange-500/20">
              <ul className="space-y-2">
                {report.key_risks.map((risk, index) => (
                  <li key={index} className="flex items-start gap-2 text-[var(--text-primary)]">
                    <span className="text-orange-500 mt-1">•</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {report.strategy_suggestions && report.strategy_suggestions.length > 0 && (
          <div className="mb-12">
            <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider mb-6">💡 策略建议</h3>
            <div className="bg-blue-500/10 rounded-lg p-6 border border-blue-500/20">
              <ul className="space-y-2">
                {report.strategy_suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2 text-[var(--text-primary)]">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {report.next_focus && report.next_focus.length > 0 && (
          <div className="mb-12">
            <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider mb-6">🔍 下周关注</h3>
            <div className="bg-purple-500/10 rounded-lg p-6 border border-purple-500/20">
              <ul className="space-y-2">
                {report.next_focus.map((focus, index) => (
                  <li key={index} className="flex items-start gap-2 text-[var(--text-primary)]">
                    <span className="text-purple-500 mt-1">•</span>
                    <span>{focus}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-[var(--border-subtle)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <p className="font-mono text-xs text-[var(--text-muted)]">
              生成时间: {new Date(report.meta.generated_at).toLocaleString('zh-CN')}
            </p>
            <p className="text-xs text-[var(--text-muted)]">
              ⚠️ 仅供研究和教育用途，不构成投资建议
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default AIStockReport
