import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'

const TAG_COLS = ['低/中/正价', '产品形态一', '产品形态二', '产品形态三', '产品形态四', '学段', '学科', '链路类型']
const PRICE_OPTIONS = ['', '低价', '中价', '正价']
const GRADE_OPTIONS = ['', '低幼', '幼小', '小学', '初中', '高中', '大学']
const SUBJECT_OPTIONS = ['', '语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '编程', '多科', '其它']
const ROUTE_OPTIONS = ['', 'leads', '正价', '低价', '中价']

const EDITABLE_COL_CONFIG = {
  '低/中/正价': { type: 'select', options: PRICE_OPTIONS },
  '产品形态一': { type: 'text' },
  '产品形态二': { type: 'text' },
  '产品形态三': { type: 'text' },
  '产品形态四': { type: 'text' },
  '学段': { type: 'select', options: GRADE_OPTIONS },
  '学科': { type: 'select', options: SUBJECT_OPTIONS },
  '链路类型': { type: 'select', options: ROUTE_OPTIONS },
}

const FIXED_COLS = ['竞品', '商品名称', '价格', '销量', '起始时间']
const ALL_REVIEW_COLS = [...FIXED_COLS, ...TAG_COLS]

function isRowTagged(row) {
  return TAG_COLS.some(col => row[col] && String(row[col]).trim() !== '')
}

function Crawler() {
  // ── Config state
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [cookie, setCookie] = useState('')

  // ── History state
  const [historyFiles, setHistoryFiles] = useState([])
  const [showHistory, setShowHistory] = useState(false)

  // ── Phase: 'config' | 'running' | 'review' | 'saved'
  const [phase, setPhase] = useState('config')
  const [runStage, setRunStage] = useState('') // 'crawling' | 'tagging'
  const [logs, setLogs] = useState([])
  const logsEndRef = useRef(null)
  const eventSourceRef = useRef(null)

  // ── Review state
  const [reviewData, setReviewData] = useState([])
  const [edits, setEdits] = useState({}) // rowIndex -> { col: value }
  const [editingCell, setEditingCell] = useState(null) // { row, col }
  const [reviewPage, setReviewPage] = useState(1)
  const [showUntaggedOnly, setShowUntaggedOnly] = useState(false)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveResult, setSaveResult] = useState(null)
  const [error, setError] = useState('')

  const REVIEW_PAGE_SIZE = 50

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close()
    }
  }, [])

  // 加载历史打标文件列表
  useEffect(() => {
    fetch('http://localhost:3001/api/review/history')
      .then(r => r.json())
      .then(d => setHistoryFiles(d.files || []))
      .catch(() => {})
  }, [])

  // 从历史文件恢复审核
  const loadHistoryFile = async (filename) => {
    setReviewLoading(true)
    setError('')
    try {
      const res = await fetch(`http://localhost:3001/api/review/data?file=${encodeURIComponent(filename)}`)
      if (!res.ok) throw new Error((await res.json()).error)
      const { data } = await res.json()
      setReviewData(data)
      setEdits({})
      setReviewPage(1)
      setShowUntaggedOnly(false)
      setPhase('review')
    } catch (err) {
      setError(err.message)
    } finally {
      setReviewLoading(false)
    }
  }

  const addLog = (msg) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`])

  // ── Start crawl
  const handleStart = async () => {
    if (!startDate) return setError('请输入开始日期')
    if (!cookie.trim()) return setError('请输入蝉妈妈Cookie')
    setError('')
    setLogs([])
    setSaveResult(null)
    setPhase('running')
    setRunStage('crawling')

    try {
      const res = await fetch('http://localhost:3001/api/crawler/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_date: startDate, end_date: endDate || startDate, cookie: cookie.trim() })
      })
      const { jobId, error: err } = await res.json()
      if (err) { setError(err); setPhase('config'); return }

      // Connect to SSE stream
      const es = new EventSource(`http://localhost:3001/api/crawler/stream/${jobId}`)
      eventSourceRef.current = es

      es.onmessage = (e) => {
        const event = JSON.parse(e.data)
        if (event.type === 'stage') {
          setRunStage(event.stage)
          addLog(event.message)
        } else if (event.type === 'log') {
          addLog(event.message)
        } else if (event.type === 'done') {
          addLog('✅ 爬取和打标完成，正在加载审核数据...')
          es.close()
          loadReviewData()
        } else if (event.type === 'error') {
          addLog(`❌ ${event.message}`)
          setError(event.message)
          setPhase('config')
          es.close()
        }
      }

      es.onerror = () => {
        addLog('连接中断')
        es.close()
      }
    } catch (err) {
      setError(err.message)
      setPhase('config')
    }
  }

  const handleAutoCrawl = () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    const dateStr = yesterday.toISOString().split('T')[0]
    setStartDate(dateStr)
    setEndDate(dateStr)
    if (!cookie.trim()) { setError('请先输入蝉妈妈Cookie'); return }
    setTimeout(handleStart, 150)
  }

  // ── Load review data
  const loadReviewData = async () => {
    setReviewLoading(true)
    try {
      const res = await fetch('http://localhost:3001/api/review/data')
      if (!res.ok) throw new Error((await res.json()).error)
      const { data } = await res.json()
      setReviewData(data)
      setEdits({})
      setReviewPage(1)
      setPhase('review')
    } catch (err) {
      addLog(`❌ 加载审核数据失败: ${err.message}`)
      setError(err.message)
    } finally {
      setReviewLoading(false)
    }
  }

  // ── Get effective row value (with edits applied)
  const getRowValue = (rowIdx, col) => {
    if (edits[rowIdx] && edits[rowIdx][col] !== undefined) return edits[rowIdx][col]
    return reviewData[rowIdx]?.[col] ?? ''
  }

  const setEdit = (rowIdx, col, value) => {
    setEdits(prev => ({
      ...prev,
      [rowIdx]: { ...(prev[rowIdx] || {}), [col]: value }
    }))
  }

  // ── Apply edits to data array for save
  const getMergedData = () => {
    return reviewData.map((row, idx) => {
      if (!edits[idx]) return row
      return { ...row, ...edits[idx] }
    })
  }

  // ── Review filtering
  const filteredIndices = reviewData
    .map((row, idx) => ({ row, idx }))
    .filter(({ row, idx }) => {
      if (!showUntaggedOnly) return true
      const effectiveRow = edits[idx] ? { ...row, ...edits[idx] } : row
      return !isRowTagged(effectiveRow)
    })

  const totalReviewPages = Math.ceil(filteredIndices.length / REVIEW_PAGE_SIZE)
  const pagedIndices = filteredIndices.slice((reviewPage - 1) * REVIEW_PAGE_SIZE, reviewPage * REVIEW_PAGE_SIZE)
  const taggedCount = reviewData.filter((row, idx) => isRowTagged(edits[idx] ? { ...row, ...edits[idx] } : row)).length

  // ── Save
  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      const merged = getMergedData()
      const res = await fetch('http://localhost:3001/api/review/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: merged })
      })
      const result = await res.json()
      if (!result.success) throw new Error(result.error)
      setSaveResult(result)
      setPhase('saved')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const competitors = [
    { brand: '作业帮', count: 5 }, { brand: '猿辅导', count: 5 },
    { brand: '高途', count: 4 }, { brand: '希望学', count: 3 },
    { brand: '豆神', count: 3 }, { brand: '叫叫', count: 2 },
    { brand: '有道', count: 3 }, { brand: '新东方', count: 3 }, { brand: '斑马', count: 3 }
  ]

  // ── Render
  return (
    <div className="h-screen bg-[var(--bg-primary)] flex flex-col">
      {/* Header */}
      <header className="border-b border-[var(--border-subtle)] bg-[var(--bg-primary)] flex-shrink-0">
        <div className="w-full px-16">
          <div className="flex items-center justify-between h-16">
            <Link to="/"><h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1></Link>
            <nav className="flex items-center gap-8">
              <Link to="/reports" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">日报</Link>
              <Link to="/crawler" className="text-sm text-[var(--accent-forest)]">数据爬取</Link>
              <Link to="/data-entry" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-auto">
        <div className="w-full h-full px-16 py-8">

          {/* Phase indicator */}
          {phase !== 'config' && (
            <div className="flex items-center gap-3 mb-8">
              {[
                { key: 'running', label: '爬取 & 打标' },
                { key: 'review', label: '人工审核' },
                { key: 'saved', label: '已入库' }
              ].map((step, i) => {
                const phases = ['running', 'review', 'saved']
                const currentIdx = phases.indexOf(phase)
                const stepIdx = phases.indexOf(step.key)
                const isDone = stepIdx < currentIdx
                const isActive = step.key === phase
                return (
                  <div key={step.key} className="flex items-center gap-3">
                    {i > 0 && <div className={`w-12 h-px ${isDone || isActive ? 'bg-[var(--accent-forest)]' : 'bg-[var(--border-subtle)]'}`} />}
                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                      isActive ? 'bg-[var(--accent-forest)] text-white' :
                      isDone ? 'bg-[var(--accent-forest)]/20 text-[var(--accent-forest)]' :
                      'bg-[var(--bg-secondary)] text-[var(--text-muted)]'
                    }`}>
                      {isDone && <span>✓</span>}
                      {step.label}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* ── CONFIG PHASE ── */}
          {phase === 'config' && (
            <div>
              <div className="mb-8">
                <h2 className="font-display text-3xl lg:text-4xl font-light text-[var(--text-primary)] mb-2">数据爬取</h2>
                <p className="text-[var(--text-secondary)]">从蝉妈妈平台自动爬取竞品销量数据，自动打标后进行人工审核</p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                    <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">Cookie 配置</h3>
                    <textarea value={cookie} onChange={e => setCookie(e.target.value)}
                      placeholder="粘贴蝉妈妈Cookie..." rows={3}
                      className="w-full px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent-forest)] font-mono" />
                    <div className="mt-3 p-3 bg-[var(--bg-secondary)] rounded-lg text-xs text-[var(--text-muted)]">
                      <p className="font-medium mb-1">获取Cookie方法：</p>
                      <ol className="list-decimal list-inside space-y-1">
                        <li>打开浏览器访问蝉妈妈并登录</li>
                        <li>按F12 → Network → 刷新页面</li>
                        <li>找到任意请求，复制请求头中的Cookie字段</li>
                      </ol>
                    </div>
                  </div>
                  <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                    <h3 className="font-display text-lg text-[var(--text-primary)] mb-6">爬取配置</h3>
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div>
                        <label className="block text-sm text-[var(--text-secondary)] mb-2">开始日期</label>
                        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
                          className="w-full px-4 py-2.5 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]" />
                      </div>
                      <div>
                        <label className="block text-sm text-[var(--text-secondary)] mb-2">结束日期</label>
                        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)}
                          className="w-full px-4 py-2.5 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]" />
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <button onClick={handleStart}
                        className="px-6 py-2.5 rounded-lg text-sm font-medium bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 active:scale-[0.98] transition-all">
                        开始爬取 & 打标
                      </button>
                      <button onClick={handleAutoCrawl}
                        className="px-6 py-2.5 rounded-lg text-sm font-medium border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[var(--accent-forest)] transition-all">
                        爬取昨日数据
                      </button>
                    </div>
                    {error && <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{error}</div>}
                  </div>

                  {/* 历史爬取记录 */}
                  {historyFiles.length > 0 && (
                    <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl overflow-hidden">
                      <button
                        onClick={() => setShowHistory(v => !v)}
                        className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-[var(--bg-secondary)]/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-medium text-[var(--text-primary)]">历史爬取记录</span>
                          <span className="text-xs px-2 py-0.5 bg-[var(--bg-secondary)] text-[var(--text-muted)] rounded-full">{historyFiles.length} 个文件</span>
                        </div>
                        <span className={`text-[var(--text-muted)] transition-transform ${showHistory ? 'rotate-180' : ''}`}>▾</span>
                      </button>
                      {showHistory && (
                        <div className="border-t border-[var(--border-subtle)]">
                          <p className="px-6 py-3 text-xs text-[var(--text-muted)]">选择一个历史打标文件，直接进入人工审核</p>
                          <div className="divide-y divide-[var(--border-subtle)]">
                            {historyFiles.map(f => (
                              <div key={f.name} className="flex items-center justify-between px-6 py-3 hover:bg-[var(--bg-secondary)]/30 transition-colors">
                                <div>
                                  <p className="text-sm text-[var(--text-primary)] font-mono">{f.name}</p>
                                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                                    {new Date(f.mtime).toLocaleString('zh-CN')}
                                  </p>
                                </div>
                                <button
                                  onClick={() => loadHistoryFile(f.name)}
                                  disabled={reviewLoading}
                                  className="px-4 py-1.5 text-xs rounded-lg bg-[var(--accent-forest)]/10 text-[var(--accent-forest)] hover:bg-[var(--accent-forest)]/20 transition-colors disabled:opacity-50"
                                >
                                  {reviewLoading ? '加载中...' : '进入审核'}
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div>
                  <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                    <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">爬取范围</h3>
                    <div className="space-y-3">
                      {competitors.map(item => (
                        <div key={item.brand} className="flex justify-between items-center py-2 border-b border-[var(--border-subtle)] last:border-0">
                          <span className="text-sm text-[var(--text-primary)]">{item.brand}</span>
                          <span className="text-xs text-[var(--text-muted)]">{item.count} 个店铺</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4 pt-4 border-t border-[var(--border-subtle)] flex justify-between">
                      <span className="text-sm font-medium text-[var(--text-primary)]">总计</span>
                      <span className="text-sm text-[var(--accent-forest)]">{competitors.reduce((s, i) => s + i.count, 0)} 个店铺</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ── RUNNING PHASE ── */}
          {phase === 'running' && (
            <div>
              <div className="mb-6">
                <h2 className="font-display text-3xl font-light text-[var(--text-primary)] mb-2">
                  {runStage === 'crawling' ? '正在爬取数据...' : runStage === 'tagging' ? '正在打标...' : '处理中...'}
                </h2>
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full animate-pulse ${runStage === 'crawling' ? 'bg-blue-500' : 'bg-[var(--accent-forest)]'}`} />
                  <span className="text-sm text-[var(--text-secondary)]">
                    {runStage === 'crawling' ? '爬取中，请勿关闭页面...' : '打标匹配中...'}
                  </span>
                </div>
              </div>
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl overflow-hidden">
                <div className="flex items-center gap-3 px-6 py-4 border-b border-[var(--border-subtle)] bg-[var(--bg-secondary)]">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-400" />
                    <div className="w-3 h-3 rounded-full bg-yellow-400" />
                    <div className="w-3 h-3 rounded-full bg-green-400" />
                  </div>
                  <span className="text-xs text-[var(--text-muted)] font-mono">实时日志</span>
                </div>
                <div className="h-[60vh] overflow-auto p-6 font-mono text-xs space-y-1">
                  {logs.map((log, i) => (
                    <p key={i} className={`${log.includes('✅') ? 'text-green-500' : log.includes('❌') ? 'text-red-500' : log.includes('▶') ? 'text-[var(--accent-forest)] font-semibold' : 'text-[var(--text-secondary)]'}`}>
                      {log}
                    </p>
                  ))}
                  {reviewLoading && <p className="text-[var(--accent-forest)] animate-pulse">正在加载审核数据...</p>}
                  <div ref={logsEndRef} />
                </div>
              </div>
            </div>
          )}

          {/* ── REVIEW PHASE ── */}
          {phase === 'review' && (
            <div>
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="font-display text-3xl font-light text-[var(--text-primary)] mb-1">人工审核</h2>
                  <p className="text-[var(--text-secondary)] text-sm">
                    共 {reviewData.length} 条数据 · 已匹配 <span className="text-[var(--accent-forest)] font-medium">{taggedCount}</span> 条 · 未匹配 <span className="text-orange-500 font-medium">{reviewData.length - taggedCount}</span> 条
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 text-sm text-[var(--text-secondary)] cursor-pointer">
                    <input type="checkbox" checked={showUntaggedOnly} onChange={e => { setShowUntaggedOnly(e.target.checked); setReviewPage(1) }}
                      className="rounded" />
                    仅显示未匹配
                  </label>
                  <button onClick={handleSave} disabled={saving}
                    className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${saving ? 'bg-[var(--text-muted)] text-white cursor-not-allowed' : 'bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 active:scale-[0.98]'}`}>
                    {saving ? '保存中...' : '✓ 确认保存入库'}
                  </button>
                </div>
              </div>

              {error && <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{error}</div>}

              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <div className="max-h-[65vh] overflow-y-auto">
                    <table className="w-full text-xs border-collapse" style={{ minWidth: '1400px' }}>
                      <thead className="sticky top-0 z-10">
                        <tr className="bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]">
                          <th className="py-3 px-3 text-left text-[var(--text-muted)] font-medium whitespace-nowrap border-r border-[var(--border-subtle)] w-8">#</th>
                          {FIXED_COLS.map(col => (
                            <th key={col} className="py-3 px-3 text-left text-[var(--text-primary)] font-semibold whitespace-nowrap border-r border-[var(--border-subtle)]">{col}</th>
                          ))}
                          <th colSpan={TAG_COLS.length} className="py-2 px-3 text-center text-[var(--accent-forest)] font-semibold border-r border-[var(--border-subtle)] bg-[var(--accent-forest)]/5">
                            打标字段（可编辑）
                          </th>
                        </tr>
                        <tr className="bg-[var(--bg-secondary)] border-b-2 border-[var(--border-subtle)]">
                          <th className="border-r border-[var(--border-subtle)]" />
                          {FIXED_COLS.map(col => <th key={col} className="border-r border-[var(--border-subtle)]" />)}
                          {TAG_COLS.map(col => (
                            <th key={col} className="py-2 px-3 text-left text-xs text-[var(--accent-forest)]/80 font-medium whitespace-nowrap border-r border-[var(--border-subtle)] last:border-r-0 bg-[var(--accent-forest)]/5">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {pagedIndices.map(({ row, idx }) => {
                          const tagged = isRowTagged(edits[idx] ? { ...row, ...edits[idx] } : row)
                          return (
                            <tr key={idx} className={`border-b border-[var(--border-subtle)] transition-colors ${tagged ? 'hover:bg-green-50/30' : 'bg-orange-50/20 hover:bg-orange-50/40'}`}>
                              <td className="py-2 px-3 text-[var(--text-muted)] border-r border-[var(--border-subtle)] text-center">{idx + 1}</td>
                              {FIXED_COLS.map(col => (
                                <td key={col} className="py-2 px-3 text-[var(--text-secondary)] border-r border-[var(--border-subtle)] max-w-[200px] truncate" title={String(row[col] ?? '')}>
                                  {col === '价格' || col === '销量' ? (row[col] != null ? Number(row[col]).toLocaleString() : '-') : (row[col] ?? '-')}
                                </td>
                              ))}
                              {TAG_COLS.map(col => {
                                const val = getRowValue(idx, col)
                                const isEditing = editingCell?.row === idx && editingCell?.col === col
                                const config = EDITABLE_COL_CONFIG[col]
                                return (
                                  <td key={col} className={`py-1 px-2 border-r border-[var(--border-subtle)] last:border-r-0 bg-[var(--accent-forest)]/[0.02] cursor-pointer min-w-[90px]`}
                                    onClick={() => setEditingCell({ row: idx, col })}>
                                    {isEditing ? (
                                      config.type === 'select' ? (
                                        <select autoFocus value={val} onBlur={() => setEditingCell(null)}
                                          onChange={e => { setEdit(idx, col, e.target.value); setEditingCell(null) }}
                                          className="w-full px-1 py-0.5 text-xs bg-white border border-[var(--accent-forest)] rounded focus:outline-none">
                                          {config.options.map(o => <option key={o} value={o}>{o || '—'}</option>)}
                                        </select>
                                      ) : (
                                        <input autoFocus type="text" value={val}
                                          onChange={e => setEdit(idx, col, e.target.value)}
                                          onBlur={() => setEditingCell(null)}
                                          onKeyDown={e => { if (e.key === 'Enter' || e.key === 'Escape') setEditingCell(null) }}
                                          className="w-full px-1 py-0.5 text-xs bg-white border border-[var(--accent-forest)] rounded focus:outline-none" />
                                      )
                                    ) : (
                                      <span className={`block px-1 py-0.5 rounded text-xs ${val ? 'text-[var(--text-primary)]' : 'text-[var(--text-muted)] italic'}`}>
                                        {val || '点击编辑'}
                                      </span>
                                    )}
                                  </td>
                                )
                              })}
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
                {/* Pagination */}
                <div className="px-4 py-3 border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)]/30 flex justify-between items-center">
                  <span className="text-sm text-[var(--text-muted)]">
                    显示 {filteredIndices.length} 条，第 {reviewPage}/{totalReviewPages || 1} 页
                  </span>
                  <div className="flex gap-2">
                    <button onClick={() => setReviewPage(p => Math.max(1, p - 1))} disabled={reviewPage === 1}
                      className="px-3 py-1 text-xs rounded border border-[var(--border-subtle)] text-[var(--text-secondary)] disabled:opacity-40 hover:border-[var(--accent-forest)] transition-colors">上一页</button>
                    <button onClick={() => setReviewPage(p => Math.min(totalReviewPages, p + 1))} disabled={reviewPage >= totalReviewPages}
                      className="px-3 py-1 text-xs rounded border border-[var(--border-subtle)] text-[var(--text-secondary)] disabled:opacity-40 hover:border-[var(--accent-forest)] transition-colors">下一页</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ── SAVED PHASE ── */}
          {phase === 'saved' && saveResult && (
            <div className="max-w-lg">
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-8 text-center">
                <div className="text-5xl mb-4">✅</div>
                <h2 className="font-display text-2xl font-light text-[var(--text-primary)] mb-2">数据已入库</h2>
                <p className="text-[var(--text-secondary)] mb-6">{saveResult.message}</p>
                <div className="grid grid-cols-3 gap-4 mb-8">
                  <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
                    <div className="text-2xl font-light text-[var(--text-primary)]">{saveResult.total}</div>
                    <div className="text-xs text-[var(--text-muted)] mt-1">总记录</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="text-2xl font-light text-green-600">+{saveResult.added}</div>
                    <div className="text-xs text-[var(--text-muted)] mt-1">新增</div>
                  </div>
                  <div className="bg-red-50 rounded-lg p-4">
                    <div className="text-2xl font-light text-red-500">-{saveResult.removed}</div>
                    <div className="text-xs text-[var(--text-muted)] mt-1">减少</div>
                  </div>
                </div>
                <div className="flex gap-3 justify-center">
                  <button onClick={() => { setPhase('config'); setSaveResult(null); setLogs([]) }}
                    className="px-6 py-2.5 rounded-lg text-sm font-medium border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[var(--accent-forest)] transition-all">
                    再次爬取
                  </button>
                  <Link to="/competitor-database"
                    className="px-6 py-2.5 rounded-lg text-sm font-medium bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 transition-all">
                    查看竞品数据库 →
                  </Link>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>

      <footer className="border-t border-[var(--border-subtle)] flex-shrink-0">
        <div className="w-full px-16 py-4 flex justify-between items-center">
          <p className="font-mono text-xs text-[var(--text-muted)]">Data Dive</p>
          <p className="text-xs text-[var(--text-muted)]">竞品销量数据分析平台</p>
        </div>
      </footer>
    </div>
  )
}

export default Crawler
