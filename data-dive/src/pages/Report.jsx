import { useState, useEffect, useRef } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ExportButton from '../components/ExportButton'
import SPUReportTabs from '../components/SPUReportTabs'
import { exportToPDF, generateFilename } from '../utils/pdfExporter'

function Report() {
  const { reportId } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
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
      <div className="h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[var(--accent-forest)]/20 border-t-[var(--accent-forest)] rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[var(--text-secondary)]">加载中...</p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="h-screen bg-[var(--bg-primary)] flex items-center justify-center">
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
    <div className="h-screen bg-[var(--bg-primary)] relative flex flex-col">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 dot-pattern opacity-40" />
      </div>

      <main ref={reportRef} className="relative w-full px-16 pt-8 pb-8 flex-1 overflow-auto">
        <nav className="mb-6 opacity-0 animate-fade-in-up flex items-center justify-between">
          <button 
            onClick={() => navigate(-1)} 
            className="group inline-flex items-center gap-2 px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-full text-sm hover:border-[var(--accent-forest)] transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>返回</span>
          </button>
          <ExportButton onClick={handleExportPDF} />
        </nav>

        <h1 className="font-display text-2xl lg:text-3xl font-bold text-[var(--text-primary)] mb-6 opacity-0 animate-fade-in-up">
          {report.meta?.title}
        </h1>

        {report.conclusions?.filter(c => c.chart_type === 'complex_table').length > 0 && (
          <SPUReportTabs 
            reports={report.conclusions?.filter(c => c.chart_type === 'complex_table') || []}
            dailySummary={report.daily_summary}
          />
        )}
      </main>

      <footer className="relative border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)] flex-shrink-0">
        <div className="w-full px-16 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="text-sm font-semibold text-[var(--text-primary)]">Data Dive</Link>
            <p className="text-sm text-[var(--text-secondary)]">生成时间：{formatDate(report.meta?.generated_at)}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Report
