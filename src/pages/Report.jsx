import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import Header from '../components/Header'
import ExportButton from '../components/ExportButton'
import ChartContainer from '../components/ChartContainer'
import SPUReportTabs from '../components/SPUReportTabs'
import DataUpload from '../components/DataUpload'
import CompetitorDatabase from '../components/CompetitorDatabase'
import { exportToPDF, generateFilename } from '../utils/pdfExporter'

function Report() {
  const { reportId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('daily')
  const reportRef = useRef(null)

  const handleExportPDF = async () => {
    const filename = generateFilename(report?.meta?.title?.slice(0, 20) || 'report')
    await exportToPDF(reportRef.current, filename)
  }

  useEffect(() => {
    loadReport()
  }, [reportId])

  const loadReport = async () => {
    setLoading(true)
    try {
      let filename = 'report.json'
      if (reportId) {
        const indexResponse = await fetch('/outputs/reports/reports-index.json')
        if (indexResponse.ok) {
          const indexData = await indexResponse.json()
          const reportEntry = indexData.reports?.find(r => r.id === reportId)
          if (reportEntry?.filename) filename = reportEntry.filename
        }
      }
      const response = await fetch(`/outputs/reports/${filename}`)
      if (response.ok) {
        const data = await response.json()
        setReport(data)
      }
    } catch (err) {
      console.log('Error loading report:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[var(--accent-forest)]/20 border-t-[var(--accent-forest)] rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[var(--text-secondary)]">加载中...</p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <p className="text-[var(--text-muted)]">报告未找到</p>
      </div>
    )
  }

  const formatDate = (isoString) => {
    try {
      return new Date(isoString).toLocaleString('zh-CN', {
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
      })
    } catch { return isoString }
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] relative flex flex-col">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 dot-pattern opacity-40" />
      </div>

      <Header title={report.meta?.title} activeTab={activeTab} onTabChange={setActiveTab} />

      <main ref={reportRef} className="relative w-full px-16 pt-24 pb-20 flex-1">
        <nav className="mb-6 opacity-0 animate-fade-in-up flex items-center justify-between">
          <Link to="/" className="group inline-flex items-center gap-2 px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-full text-sm">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>存档</span>
          </Link>
          {activeTab !== 'upload' && <ExportButton onClick={handleExportPDF} />}
        </nav>

        {/* 日报 Tab - 只显示SPU日报 */}
        {activeTab === 'daily' && (
          <>
            {/* SPU日报 - 标签页形式 */}
            {report.conclusions?.filter(c => c.chart_type === 'complex_table').length > 0 && (
              <SPUReportTabs 
                reports={report.conclusions?.filter(c => c.chart_type === 'complex_table') || []}
                dailySummary={report.daily_summary}
              />
            )}
          </>
        )}

        {/* 全年销量数据 Tab - 显示整体洞察+详细洞察 */}
        {activeTab === 'yearly' && (
          <>
            {/* 整体洞察 */}
            {report.overall_insights && report.overall_insights.length > 0 && (
              <section className="mb-10 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
                <div className="flex items-center gap-4 mb-6">
                  <span className="text-[11px] font-bold text-[var(--accent-gold)] uppercase tracking-[0.2em]">整体洞察</span>
                  <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-gold)]/30 to-transparent" />
                </div>
                <h2 className="font-display text-2xl lg:text-3xl font-bold text-[var(--text-primary)] mb-6">全年销量分析</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {report.overall_insights.map((insight, idx) => (
                    <div key={idx} className={`p-4 rounded-xl border ${
                      insight.priority === 'high' 
                        ? 'bg-[var(--accent-terracotta)]/5 border-[var(--accent-terracotta)]/20' 
                        : insight.priority === 'medium'
                        ? 'bg-[var(--accent-gold)]/5 border-[var(--accent-gold)]/20'
                        : 'bg-[var(--bg-card)] border-[var(--border-subtle)]'
                    }`}>
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">{insight.icon}</span>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-[var(--text-tertiary)]">{insight.type}</span>
                            {insight.priority === 'high' && (
                              <span className="text-xs px-1.5 py-0.5 bg-[var(--accent-terracotta)]/10 text-[var(--accent-terracotta)] rounded">重要</span>
                            )}
                          </div>
                          <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-1">{insight.title}</h4>
                          <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{insight.content}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section className="mb-4 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center gap-4">
                <span className="text-[11px] font-bold text-[var(--accent-forest)] uppercase tracking-[0.2em]">详细洞察</span>
                <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-forest)]/30 to-transparent" />
              </div>
              <h2 className="mt-3 font-display text-2xl lg:text-3xl font-bold text-[var(--text-primary)]">销量趋势数据</h2>
            </section>

            {/* 趋势图表 - 可筛选 */}
            {report.conclusions?.filter(c => c.chart_type === 'filterable_line').map((conclusion, index) => (
              <section key={conclusion.id} className="mb-10">
                <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] shadow-editorial overflow-hidden">
                  <div className="p-4">
                    <ChartContainer type={conclusion.chart_type} data={conclusion.chart_data} />
                  </div>
                </div>
              </section>
            ))}
          </>
        )}

        {/* 竞品数据库 Tab */}
        {activeTab === 'database' && (
          <CompetitorDatabase />
        )}

        {/* 每日数据录入 Tab */}
        {activeTab === 'upload' && (
          <DataUpload onUploadSuccess={loadReport} />
        )}
      </main>

      <footer className="relative mt-auto border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)]">
        <div className="w-full px-16 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <Link to="/" className="flex items-center gap-3">
              <p className="text-sm font-semibold text-[var(--text-primary)]">Data Dive</p>
            </Link>
            <p className="text-sm text-[var(--text-secondary)]">生成时间：{formatDate(report.meta?.generated_at)}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Report
