function DataSourceBadge({ files }) {
  if (!files || files.length === 0) return null

  const getColor = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    if (['xlsx', 'xls'].includes(ext)) return 'text-[var(--accent-forest)] bg-[var(--accent-forest)]/8 border-[var(--accent-forest)]/15'
    if (ext === 'pdf') return 'text-[var(--accent-terracotta)] bg-[var(--accent-terracotta)]/8 border-[var(--accent-terracotta)]/15'
    if (ext === 'csv') return 'text-[var(--accent-gold)] bg-[var(--accent-gold)]/8 border-[var(--accent-gold)]/15'
    return 'text-[var(--text-tertiary)] bg-[var(--bg-tertiary)] border-[var(--border-subtle)]'
  }

  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider self-center mr-1">Sources:</span>
      {files.map((file, index) => (
        <span key={index} className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${getColor(file)}`}>
          {file}
        </span>
      ))}
    </div>
  )
}

export default DataSourceBadge