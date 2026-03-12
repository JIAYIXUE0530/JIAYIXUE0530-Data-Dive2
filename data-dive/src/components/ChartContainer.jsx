import { useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  ScatterChart, Scatter, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

const CHART_COLORS = ['#1e3a8a', '#1e40af', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe']

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[var(--bg-card)] border border-[var(--border-medium)] rounded-xl px-4 py-3 shadow-editorial">
        <p className="text-[var(--text-primary)] font-display font-semibold text-sm mb-2">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-xs">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-[var(--text-secondary)]">{entry.name}:</span>
            <span className="text-[var(--text-primary)] font-mono font-semibold">
              {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
            </span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

function ChartContainer({ type, data }) {
  if (!data) return null

  const axisStyle = { tick: { fontSize: 11, fill: '#8c8377' }, stroke: 'rgba(61, 54, 48, 0.08)' }
  const gridStyle = { strokeDasharray: '4 4', stroke: 'rgba(61, 54, 48, 0.08)' }

  // Bar Chart
  if (type === 'bar') {
    let chartData = [], seriesKeys = []
    const xKey = data.xKey || 'name'
    if (data.data && Array.isArray(data.data)) {
      chartData = data.data
      seriesKeys = [data.yKey || 'value']
    } else if (data.x_labels && data.series) {
      chartData = data.x_labels.map((label, i) => {
        const point = { name: label }
        Object.entries(data.series).forEach(([key, values]) => { point[key] = values[i] })
        return point
      })
      seriesKeys = Object.keys(data.series)
    }
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-4 -mx-2" style={{ minHeight: '300px' }}>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid {...gridStyle} vertical={false} />
              <XAxis dataKey={xKey} {...axisStyle} axisLine={false} tickLine={false} />
              <YAxis {...axisStyle} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              {seriesKeys.length > 1 && <Legend />}
              {seriesKeys.map((key, i) => (
                <Bar key={key} dataKey={key} fill={CHART_COLORS[i % CHART_COLORS.length]} radius={[6, 6, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  // Line Chart
  if (type === 'line') {
    let chartData = [], seriesKeys = []
    if (data.x_labels && data.series) {
      chartData = data.x_labels.map((label, i) => {
        const point = { name: label }
        Object.entries(data.series).forEach(([key, values]) => { point[key] = values[i] })
        return point
      })
      seriesKeys = Object.keys(data.series)
    }
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-4 -mx-2" style={{ minHeight: '300px' }}>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid {...gridStyle} vertical={false} />
              <XAxis dataKey="name" {...axisStyle} axisLine={false} tickLine={false} />
              <YAxis {...axisStyle} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {seriesKeys.map((key, i) => (
                <Line key={key} type="monotone" dataKey={key} stroke={CHART_COLORS[i % CHART_COLORS.length]} strokeWidth={2.5} dot={{ r: 4 }} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  // Filterable Line Chart (可筛选的趋势图表)
  if (type === 'filterable_line') {
    const [selectedChannel, setSelectedChannel] = useState(data.default_channel || '低价')
    const [selectedSegment, setSelectedSegment] = useState(data.default_segment || '小学')
    const [selectedDateRange, setSelectedDateRange] = useState('全部')
    
    // 获取当前选中组合的数据
    const key = `${selectedChannel}_${selectedSegment}`
    const currentData = data.combinations?.[key] || {}
    
    // 根据日期范围筛选数据
    const filterByDateRange = (xLabels, seriesData) => {
      if (!xLabels || !seriesData || selectedDateRange === '全部') {
        return { filteredLabels: xLabels, filteredSeries: seriesData }
      }
      
      const totalMonths = xLabels.length
      let monthsToShow = totalMonths
      
      switch (selectedDateRange) {
        case '最近3个月':
          monthsToShow = Math.min(3, totalMonths)
          break
        case '最近6个月':
          monthsToShow = Math.min(6, totalMonths)
          break
        case '最近12个月':
          monthsToShow = Math.min(12, totalMonths)
          break
        default:
          monthsToShow = totalMonths
      }
      
      const startIndex = Math.max(0, totalMonths - monthsToShow)
      const filteredLabels = xLabels.slice(startIndex)
      const filteredSeries = {}
      
      Object.entries(seriesData).forEach(([k, values]) => {
        filteredSeries[k] = values.slice(startIndex)
      })
      
      return { filteredLabels, filteredSeries }
    }
    
    const { filteredLabels, filteredSeries } = filterByDateRange(currentData.x_labels, currentData.series)
    
    let chartData = [], seriesKeys = []
    if (filteredLabels && filteredSeries) {
      chartData = filteredLabels.map((label, i) => {
        const point = { name: label }
        Object.entries(filteredSeries).forEach(([k, values]) => { point[k] = values[i] })
        return point
      })
      seriesKeys = Object.keys(filteredSeries)
    }
    
    const dateRangeOptions = ['全部', '最近3个月', '最近6个月', '最近12个月']
    
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        {/* 筛选器 */}
        <div className="flex flex-wrap gap-4 mb-4">
          <div className="flex items-center gap-2">
            <label className="text-sm text-[var(--text-secondary)]">链路:</label>
            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
            >
              {data.filters?.链路?.map(option => (
                <option key={option} value={option}>{option}</option>
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
              {data.filters?.学段?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm text-[var(--text-secondary)]">日期:</label>
            <select
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value)}
              className="px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
            >
              {dateRangeOptions.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>
        
        {/* 图表 */}
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-4 -mx-2" style={{ minHeight: '300px' }}>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
                <CartesianGrid {...gridStyle} vertical={false} />
                <XAxis dataKey="name" {...axisStyle} axisLine={false} tickLine={false} />
                <YAxis {...axisStyle} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                {seriesKeys.map((key, i) => (
                  <Line key={key} type="monotone" dataKey={key} stroke={CHART_COLORS[i % CHART_COLORS.length]} strokeWidth={2.5} dot={{ r: 4 }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[280px] text-[var(--text-muted)]">
              该组合暂无数据
            </div>
          )}
        </div>
      </div>
    )
  }

  // Pie Chart
  if (type === 'pie') {
    let chartData = []
    if (data.labels && data.values) {
      chartData = data.labels.map((label, i) => ({ name: label, value: data.values[i] }))
    } else if (data.data) {
      chartData = data.data.map(item => ({ name: item[data.nameKey || 'name'], value: item[data.valueKey || 'value'] }))
    }
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-4 -mx-2" style={{ minHeight: '300px' }}>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={chartData} cx="50%" cy="50%" innerRadius={60} outerRadius={95} paddingAngle={3} dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="#ffffff" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  // Scatter Chart
  if (type === 'scatter') {
    const chartData = data.x?.map((x, i) => ({ x, y: data.y[i], name: data.labels?.[i] || `Point ${i + 1}` })) || []
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-4 -mx-2" style={{ minHeight: '300px' }}>
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid {...gridStyle} />
              <XAxis type="number" dataKey="x" name={data.x_title || 'X'} {...axisStyle} axisLine={false} />
              <YAxis type="number" dataKey="y" name={data.y_title || 'Y'} {...axisStyle} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Scatter name="Data Points" data={chartData} fill={CHART_COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  // Table Chart
  if (type === 'table') {
    const { columns = [], data: tableData = [], filters = {} } = data
    const [activeFilters, setActiveFilters] = useState({})
    const [currentPage, setCurrentPage] = useState(1)
    const pageSize = 20
    
    // Filter data based on active filters
    const filteredData = tableData.filter(row => {
      return Object.entries(activeFilters).every(([key, value]) => {
        if (!value || value === '全部') return true
        return row[key] === value
      })
    })
    
    // Pagination
    const totalPages = Math.ceil(filteredData.length / pageSize)
    const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)
    
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        {/* Filters */}
        {Object.keys(filters).length > 0 && (
          <div className="flex flex-wrap gap-4 mb-6">
            {Object.entries(filters).map(([filterKey, options]) => (
              <div key={filterKey} className="flex items-center gap-2">
                <label className="text-sm text-[var(--text-secondary)]">{filterKey}:</label>
                <select
                  value={activeFilters[filterKey] || '全部'}
                  onChange={(e) => {
                    setActiveFilters(prev => ({
                      ...prev,
                      [filterKey]: e.target.value
                    }))
                    setCurrentPage(1)
                  }}
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
        )}
        
        {/* Table */}
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-4 -mx-2 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border-subtle)]">
                {columns.map((column, index) => (
                  <th key={index} className="text-left py-3 px-4 font-semibold text-[var(--text-primary)] whitespace-nowrap">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-tertiary)]/30 transition-colors">
                  {columns.map((column, colIndex) => (
                    <td key={colIndex} className="py-3 px-4 text-[var(--text-secondary)] whitespace-nowrap">
                      {row[column] !== null && row[column] !== undefined ? row[column].toLocaleString?.() || row[column] : '-'}
                    </td>
                  ))}
                </tr>
              ))}
              {paginatedData.length === 0 && (
                <tr>
                  <td colSpan={columns.length} className="py-8 text-center text-[var(--text-muted)]">
                    没有匹配的数据
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 px-2">
            <p className="text-sm text-[var(--text-muted)]">
              显示 {(currentPage - 1) * pageSize + 1}-{Math.min(currentPage * pageSize, filteredData.length)} 条，共 {filteredData.length} 条
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border border-[var(--border-subtle)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--bg-tertiary)]"
              >
                上一页
              </button>
              <span className="px-3 py-1 text-sm text-[var(--text-secondary)]">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border border-[var(--border-subtle)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--bg-tertiary)]"
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Complex Table Chart (with grouped headers)
  if (type === 'complex_table') {
    const { columns = [], header_groups = [], data: tableData = [], filters = {} } = data
    const [activeFilters, setActiveFilters] = useState({})
    
    // Filter data based on active filters
    const filteredData = tableData.filter(row => {
      return Object.entries(activeFilters).every(([key, value]) => {
        if (!value || value === '全部') return true
        return row[key] === value
      })
    })
    
    // 计算总计行
    const calculateTotals = () => {
      if (filteredData.length === 0) return null
      
      const totals = {}
      
      // 数值列（需要求和）
      const numericColumns = ['昨日销量', '3日日均', '7日日均', '30日日均', 
                              'T周', 'T-1周', 'T-2周', 'T-3周', 'T-4周',
                              '当月', 'T-1月', 'T-2月', 'T-3月']
      
      // 占比列（总计为100%）
      const ratioColumns = ['昨日销量占比', '3日日均占比', '7日日均占比', '30日日均占比']
      
      // 文本列（显示"-"或"总计"）
      const textColumns = ['学段', '学科', '竞品', '商品名称', '价格']
      
      columns.forEach(col => {
        if (textColumns.includes(col)) {
          if (col === columns[0]) {
            totals[col] = '总计'
          } else {
            totals[col] = '-'
          }
        } else if (ratioColumns.includes(col)) {
          totals[col] = '100%'
        } else if (numericColumns.includes(col)) {
          const sum = filteredData.reduce((acc, row) => {
            const val = row[col]
            if (typeof val === 'number') return acc + val
            return acc
          }, 0)
          totals[col] = Math.round(sum)  // 整数
        } else {
          totals[col] = '-'
        }
      })
      
      return totals
    }
    
    const totalsRow = calculateTotals()
    
    return (
      <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
        {/* Filters */}
        {Object.keys(filters).length > 0 && (
          <div className="flex flex-wrap gap-4 mb-4">
            {Object.entries(filters).map(([filterKey, options]) => {
              // 自定义排序顺序
              const getSortedOptions = (key, opts) => {
                if (key === '学段') {
                  const order = ['小学', '初中', '高中', '低幼']
                  return order.filter(o => opts.includes(o))
                }
                if (key === '竞品') {
                  const order = ['作业帮', '猿辅导', '高途', '希望学', '豆神', '叫叫']
                  const ordered = order.filter(o => opts.includes(o))
                  const others = opts.filter(o => !order.includes(o) && o !== 'IP').sort()
                  const ip = opts.includes('IP') ? ['IP'] : []
                  return [...ordered, ...others, ...ip]
                }
                return opts
              }
              const sortedOptions = getSortedOptions(filterKey, options)
              
              return (
              <div key={filterKey} className="flex items-center gap-2">
                <label className="text-sm text-[var(--text-secondary)]">{filterKey}:</label>
                <select
                  value={activeFilters[filterKey] || '全部'}
                  onChange={(e) => {
                    setActiveFilters(prev => ({
                      ...prev,
                      [filterKey]: e.target.value
                    }))
                  }}
                  className="px-3 py-1.5 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                >
                  <option value="全部">全部</option>
                  {sortedOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            )})}
          </div>
        )}
        
        {/* 表格容器 - 固定高度，内容滚动 */}
        <div className="bg-[var(--bg-secondary)]/50 rounded-xl -mx-2 overflow-hidden">
          <div className="overflow-x-auto">
            <div className="max-h-[800px] overflow-y-auto">
              <table className="w-full text-sm border-collapse min-w-[1200px]">
                <thead className="sticky top-0 z-10">
                  {/* Header Groups (第一行) - 明亮深蓝 */}
                  {header_groups && header_groups.length > 0 && (
                    <tr className="border-b border-[var(--border-subtle)] bg-[#7ba3c9]">
                      {header_groups.map((group, index) => (
                        <th 
                          key={index} 
                          colSpan={group.colspan} 
                          className="text-center py-3 px-3 font-semibold text-white whitespace-nowrap border-r border-white/20 last:border-r-0"
                        >
                          {group.title}
                        </th>
                      ))}
                    </tr>
                  )}
                  {/* Column Headers (第二行) - 明亮中蓝 */}
                  <tr className="border-b border-[var(--border-subtle)] bg-[#9ec5e8]">
                    {columns.map((column, index) => (
                      <th key={index} className="text-left py-2 px-3 font-semibold text-white whitespace-nowrap border-r border-white/20 last:border-r-0">
                        {column}
                      </th>
                    ))}
                  </tr>
                  {/* 总计行 (第三行) - 明亮浅蓝，放入thead以冻结 */}
                  {totalsRow && (
                    <tr className="border-b-2 border-[#c8dff2] bg-[#d6e9f7]/90 font-semibold">
                      {columns.map((column, colIndex) => (
                        <th key={colIndex} className="py-2 px-3 text-[#4a7a9e] whitespace-nowrap border-r border-[var(--border-subtle)] last:border-r-0 font-semibold text-left">
                          {totalsRow[column] !== null && totalsRow[column] !== undefined ? 
                            (typeof totalsRow[column] === 'number' ? totalsRow[column].toLocaleString() : totalsRow[column]) 
                            : '-'}
                        </th>
                      ))}
                    </tr>
                  )}
                </thead>
                <tbody>
                  {/* 数据行 */}
                  {filteredData.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-tertiary)]/30 transition-colors">
                      {columns.map((column, colIndex) => (
                        <td key={colIndex} className="py-2 px-3 text-[var(--text-secondary)] whitespace-nowrap border-r border-[var(--border-subtle)] last:border-r-0">
                          {row[column] !== null && row[column] !== undefined ? 
                            (typeof row[column] === 'number' ? Math.round(row[column]).toLocaleString() : row[column]) 
                            : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                  {filteredData.length === 0 && (
                    <tr>
                      <td colSpan={columns.length} className="py-8 text-center text-[var(--text-muted)]">
                        没有匹配的数据
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          {/* 数据统计 */}
          <div className="px-4 py-2 border-t border-[var(--border-subtle)] text-sm text-[var(--text-muted)]">
            共 {filteredData.length} 条数据
          </div>
        </div>
      </div>
    )
  }

  return <p className="text-[var(--text-muted)] text-sm">Unsupported chart type: {type}</p>
}

export default ChartContainer