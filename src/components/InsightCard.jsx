import DataSourceBadge from './DataSourceBadge'
import ChartContainer from './ChartContainer'

const IMPORTANCE_LABELS = { high: '关键', medium: '重要', low: '一般' }

function InsightCard({ conclusion, index = 0 }) {
  const { title, description, data_support, source_files, importance = 'medium', chart_type, chart_data } = conclusion

  return (
    <article className="relative bg-[var(--bg-card)] border border-[var(--border-subtle)] transition-all duration-300 hover:border-[var(--border-medium)] opacity-0 animate-fade-in-up" style={{ animationDelay: `${0.15 + index * 0.1}s` }}>
      <div className="p-6 lg:p-8">
        <div className="flex items-start justify-between gap-4 mb-4">
          <span className="font-mono text-xs text-[var(--text-muted)] mt-1">{String(index + 1).padStart(2, '0')}</span>
          <span className="font-mono text-[10px] text-[var(--text-muted)] uppercase tracking-wider">{IMPORTANCE_LABELS[importance]}</span>
        </div>
        <h3 className="font-display text-xl lg:text-2xl font-normal text-[var(--text-primary)] leading-snug mb-4">{title}</h3>
        <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-6">{description}</p>
        {data_support && (
          <div className="mb-6 py-4 border-y border-[var(--border-subtle)]">
            <span className="font-mono text-[10px] text-[var(--text-muted)] uppercase tracking-wider block mb-3">数据支撑</span>
            <p className="text-[var(--text-primary)] text-sm font-mono leading-relaxed">{data_support}</p>
          </div>
        )}
        <DataSourceBadge files={source_files} />
        {chart_type && chart_type !== 'none' && chart_data && (
          <div className="mt-6">
            <ChartContainer type={chart_type} data={chart_data} />
          </div>
        )}
      </div>
    </article>
  )
}

export default InsightCard