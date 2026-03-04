import { useState, useEffect, useCallback } from 'react'

function CompetitorDatabase() {
  const [allData, setAllData] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    链路: '全部',
    学段: '全部',
    竞品: '全部',
    学科: '全部'
  })
  const [filterOptions, setFilterOptions] = useState({
    链路: [],
    学段: [],
    竞品: [],
    学科: []
  })
  const [page, setPage] = useState(1)
  const pageSize = 100

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const response = await fetch('/data/database.json')
        if (response.ok) {
          const data = await response.json()
          setAllData(data)
          
          const options = {
            链路: [...new Set(data.map(row => row['链路']).filter(Boolean))].sort(),
            学段: [...new Set(data.map(row => row['学段']).filter(Boolean))].sort(),
            竞品: [...new Set(data.map(row => row['竞品']).filter(Boolean))].sort(),
            学科: [...new Set(data.map(row => row['学科']).filter(Boolean))].sort()
          }
          setFilterOptions(options)
        }
      } catch (err) {
        console.error('加载数据失败:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const filteredData = allData.filter(row => {
    return Object.entries(filters).every(([key, value]) => {
      if (!value || value === '全部') return true
      return row[key] === value
    })
  })

  const total = filteredData.length
  const totalPages = Math.ceil(total / pageSize)
  const startIndex = (page - 1) * pageSize
  const paginatedData = filteredData.slice(startIndex, startIndex + pageSize)

  useEffect(() => {
    setPage(1)
  }, [filters])

  const columns = [
    '销售日期', '链路', '学段', '学科', '竞品', '商品', '价格', '销量'
  ]

  const formatDate = (value) => {
    if (!value) return '-'
    if (typeof value === 'number') {
      const date = new Date((value - 25569) * 86400 * 1000)
      return date.toLocaleDateString('zh-CN')
    }
    try {
      return new Date(value).toLocaleDateString('zh-CN')
    } catch {
      return value
    }
  }

  return (
    <section className="mb-10">
      <div className="flex items-center gap-4 mb-6">
        <span className="text-[11px] font-bold text-[var(--accent-terracotta)] uppercase tracking-[0.2em]">数据库</span>
        <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-terracotta)]/30 to-transparent" />
      </div>
      <h2 className="font-display text-2xl lg:text-3xl font-bold text-[var(--text-primary)] mb-6">竞品数据库</h2>

      <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] shadow-editorial overflow-hidden">
        <div className="p-4 border-b border-[var(--border-subtle)] bg-[var(--bg-secondary)]/30">
          <div className="flex flex-wrap gap-4 items-center">
            {Object.entries(filterOptions).map(([key, options]) => (
              <div key={key} className="flex items-center gap-2">
                <label className="text-sm text-[var(--text-secondary)]">{key}:</label>
                <select
                  value={filters[key] || '全部'}
                  onChange={(e) => setFilters(prev => ({ ...prev, [key]: e.target.value }))}
                  className="px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                >
                  <option value="全部">全部</option>
                  {options.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <div className="max-h-[500px] overflow-y-auto">
            <table className="w-full text-sm border-collapse min-w-[1000px]">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-[var(--border-subtle)] bg-[var(--bg-card)]">
                  {columns.map((column, index) => (
                    <th key={index} className="text-left py-3 px-4 font-semibold text-[var(--text-primary)] whitespace-nowrap border-r border-[var(--border-subtle)] last:border-r-0 bg-[var(--bg-card)]">
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={columns.length} className="py-8 text-center text-[var(--text-muted)]">
                      加载中...
                    </td>
                  </tr>
                ) : paginatedData.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} className="py-8 text-center text-[var(--text-muted)]">
                      没有匹配的数据
                    </td>
                  </tr>
                ) : (
                  paginatedData.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-tertiary)]/30 transition-colors">
                      {columns.map((column, colIndex) => (
                        <td key={colIndex} className="py-2 px-4 text-[var(--text-secondary)] whitespace-nowrap border-r border-[var(--border-subtle)] last:border-r-0">
                          {column === '销售日期' 
                            ? formatDate(row[column])
                            : row[column] !== null && row[column] !== undefined
                              ? (typeof row[column] === 'number' ? row[column].toLocaleString() : row[column])
                              : '-'}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="px-4 py-3 border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)]/30 flex justify-between items-center">
          <span className="text-sm text-[var(--text-muted)]">
            共 {total.toLocaleString()} 条记录，当前第 {page}/{totalPages || 1} 页
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1 || loading}
              className="px-3 py-1 text-sm border border-[var(--border-subtle)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--bg-tertiary)]"
            >
              上一页
            </button>
            <span className="px-3 py-1 text-sm text-[var(--text-secondary)]">
              {page} / {totalPages || 1}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages || loading || totalPages === 0}
              className="px-3 py-1 text-sm border border-[var(--border-subtle)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--bg-tertiary)]"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

export default CompetitorDatabase
