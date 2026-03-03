function EmptyState() {
  return (
    <div className="py-24 opacity-0 animate-fade-in-up">
      <div className="max-w-md">
        <h2 className="font-display text-3xl lg:text-4xl font-light text-[var(--text-primary)] mb-4">暂无报告</h2>
        <p className="text-[var(--text-secondary)] mb-8 leading-relaxed">
          开始你的第一次数据分析吧。将数据文件放入 <code className="font-mono text-sm px-1.5 py-0.5 bg-[var(--bg-secondary)] rounded">uploads/</code> 目录，然后运行分析命令。
        </p>
        <div className="inline-block">
          <div className="font-mono text-sm px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded">
            <span className="text-[var(--text-muted)]">$</span>
            <span className="text-[var(--text-primary)] ml-2">/analyze-data</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmptyState