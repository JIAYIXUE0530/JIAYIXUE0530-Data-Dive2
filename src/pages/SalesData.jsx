import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import ChartContainer from '../components/ChartContainer'

function SalesData() {
  const [loading, setLoading] = useState(true)
  const [salesData, setSalesData] = useState(null)
  const [selectedChannel, setSelectedChannel] = useState('低价')
  const [selectedSegment, setSelectedSegment] = useState('小学')

  useEffect(() => {
    loadSalesData()
  }, [])

  const loadSalesData = async () => {
    try {
      const response = await fetch('/outputs/reports/report-2025-12-31.json')
      if (response.ok) {
        const data = await response.json()
        setSalesData(data)
      }
    } catch (err) {
      console.log('Failed to load sales data:', err)
    } finally {
      setLoading(false)
    }
  }

  const channels = ['低价', '中价', '正价']
  const segments = ['小学', '初中', '高中']

  return (
    <div className="h-screen bg-[var(--bg-primary)] flex flex-col">
      <header className="border-b border-[var(--border-subtle)] bg-[var(--bg-primary)] flex-shrink-0">
        <div className="w-full px-16">
          <div className="flex items-center justify-between h-16">
            <Link to="/">
              <h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1>
            </Link>
            <nav className="flex items-center gap-8">
              <Link to="/reports" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">日报</Link>
              <Link to="/data-entry" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--accent-forest)]">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-auto">
        <div className="w-full h-full px-16 py-8">
          <div className="mb-8">
            <h2 className="font-display text-3xl lg:text-4xl font-light text-[var(--text-primary)] mb-2">全年销量数据</h2>
            <p className="text-[var(--text-secondary)]">查看全年销量趋势分析，按链路和学段筛选数据。</p>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <div className="w-6 h-6 border-2 border-[var(--text-muted)] border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="mt-4 text-[var(--text-muted)] text-sm">加载中...</p>
            </div>
          ) : salesData ? (
            <>
              <div className="flex flex-wrap gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-[var(--text-secondary)]">链路:</label>
                  <select
                    value={selectedChannel}
                    onChange={(e) => setSelectedChannel(e.target.value)}
                    className="px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                  >
                    {channels.map(ch => (
                      <option key={ch} value={ch}>{ch}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-[var(--text-secondary)]">学段:</label>
                  <select
                    value={selectedSegment}
                    onChange={(e) => setSelectedSegment(e.target.value)}
                    className="px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                  >
                    {segments.map(seg => (
                      <option key={seg} value={seg}>{seg}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6 text-center">
                  <p className="text-sm text-[var(--text-secondary)] mb-2">累计销量</p>
                  <p className="text-3xl font-display text-[var(--text-primary)]">
                    {salesData.kpi?.total_sales?.toLocaleString() || '-'}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">
                    环比 {salesData.kpi?.mom_change >= 0 ? '+' : ''}{salesData.kpi?.mom_change}%
                  </p>
                </div>
                <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6 text-center">
                  <p className="text-sm text-[var(--text-secondary)] mb-2">TOP品牌</p>
                  <p className="text-xl font-display text-[var(--text-primary)]">
                    {salesData.kpi?.top_brands?.[0] || '-'}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">
                    {salesData.kpi?.top_brands?.slice(0, 3).join(' > ')}
                  </p>
                </div>
                <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6 text-center">
                  <p className="text-sm text-[var(--text-secondary)] mb-2">7日日均销量</p>
                  <p className="text-3xl font-display text-[var(--text-primary)]">
                    {salesData.daily_summary?.大盘?.avg_7d?.toLocaleString() || '-'}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">
                    TOP学段: {salesData.daily_summary?.大盘?.top_segment || '-'}
                  </p>
                </div>
              </div>

              {salesData.conclusions?.[0]?.chart_data && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                  <h3 className="font-display text-lg text-[var(--text-primary)] mb-6">品牌月度销量趋势</h3>
                  <ChartContainer
                    type="filterable_line"
                    data={{
                      ...salesData.conclusions[0].chart_data,
                      default_channel: selectedChannel,
                      default_segment: selectedSegment
                    }}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-16">
              <p className="text-[var(--text-muted)]">暂无数据，请先上传数据文件</p>
              <Link to="/data-entry" className="mt-4 inline-block text-[var(--accent-forest)] hover:underline">
                前往上传数据
              </Link>
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

export default SalesData
