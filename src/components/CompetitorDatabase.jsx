import { useState, useEffect, useCallback } from 'react'

function CompetitorDatabase() {
  const [data, setData] = useState([])
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
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const pageSize = 100

  // 加载筛选选项
  useEffect(() => {
    const loadOptions = async () => {
      try {
        const response = await fetch('/api/database/options')
        if (response.ok) {
          const result = await response.json()
          setFilterOptions(result.options || {})
          setTotal(result.total || 0)
        }
      } catch (err) {
        console.error('加载选项失败:', err)
      }
    }
    loadOptions()
  }, [])

  // 加载数据
  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      
      const response = await fetch(`/api/database?${params}`)
      if (response.ok) {
        const result = await response.json()
        setData(result.data || [])
        setTotal(result.total || 0)
        setTotalPages(result.totalPages || 0)
      }
    } catch (err) {
      console.error('加载数据失败:', err)
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => {
    loadData()
  }, [loadData])

  // 筛选数据（前端筛选）
  const filteredData = data.filter(row => {
    return Object.entries(filters).every(([key, value]) => {
      if (!value || value === '全部') return true
      return row[key] === value
    })
  })

  // 列定义
  const columns = [
    '销售日期', '链路', '学段', '学科', '竞品', '商品', '价格', '销量'
  ]

  // 格式化日期
  const formatDate = (value) => {
    if (!value) return '-'
    if (typeof value === 'number') {
      // Excel 日期序列号转换
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
        {/* 筛选器 */}
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
            
            {/* 刷新按钮 */}
            <button
              onClick={loadData}
              disabled={loading}
              className="ml-auto px-4 py-1.5 text-sm bg-[var(--accent-forest)] text-white rounded-lg hover:bg-[var(--accent-forest)]/90 disabled:opacity-50"
            >
              {loading ? '加载中...' : '刷新'}
            </button>
          </div>
        </div>

        {/* 表格 */}
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
                ) : filteredData.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} className="py-8 text-center text-[var(--text-muted)]">
                      没有匹配的数据
                    </td>
                  </tr>
                ) : (
                  filteredData.map((row, rowIndex) => (
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

        {/* 分页 */}
        <div className="px-4 py-3 border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)]/30 flex justify-between items-center">
          <span className="text-sm text-[var(--text-muted)]">
            共 {total.toLocaleString()} 条记录，当前第 {page}/{totalPages} 页
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
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages || loading}
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
