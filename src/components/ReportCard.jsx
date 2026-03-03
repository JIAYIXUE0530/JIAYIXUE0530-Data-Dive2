import { Link } from 'react-router-dom'

function ReportCard({ report, index = 0 }) {
  const { id, title, created_at, summary_preview, stats, tags = [] } = report

  const formatDate = (isoString) => {
    try {
      const date = new Date(isoString)
      return { month: (date.getMonth() + 1) + '月', day: date.getDate(), year: date.getFullYear() }
    } catch { return { month: '1月', day: '01', year: '2025' } }
  }

  const { month, day, year } = formatDate(created_at)

  return (
    <Link to={`/report/${id}`} className="group relative block opacity-0 animate-fade-in-up no-underline" style={{ animationDelay: `${0.1 + index * 0.08}s` }}>
      <article className="relative h-full">
        <div className="relative h-full bg-[var(--bg-card)] border border-[var(--border-subtle)] transition-all duration-500 group-hover:border-[var(--border-medium)] group-hover:shadow-lg">
          <div className="p-6 lg:p-8">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-baseline gap-1 text-[var(--text-muted)]">
                <span className="font-mono text-xs">{month}</span>
                <span className="font-display text-2xl font-light text-[var(--text-primary)]">{day}</span>
                <span className="font-mono text-xs">{year}</span>
              </div>
              <div className="flex items-center gap-4 text-[var(--text-muted)]">
                <span className="font-mono text-xs">{stats?.total_conclusions || 0} 项发现</span>
              </div>
            </div>
            <h3 className="font-display text-2xl lg:text-3xl font-normal text-[var(--text-primary)] leading-snug mb-4 group-hover:text-[var(--accent-forest)] transition-colors">{title}</h3>
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed line-clamp-2 mb-6">{summary_preview}</p>
            <div className="flex items-center justify-between pt-5 border-t border-[var(--border-subtle)]">
              <div className="text-xs text-[var(--text-muted)]">{stats?.source_files || 0} 个数据源</div>
              <div className="flex items-center gap-2 text-xs text-[var(--text-muted)] group-hover:text-[var(--accent-forest)] transition-colors">
                <span className="font-medium opacity-0 group-hover:opacity-100 transition-opacity">查看</span>
                <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </article>
    </Link>
  )
}

export default ReportCard