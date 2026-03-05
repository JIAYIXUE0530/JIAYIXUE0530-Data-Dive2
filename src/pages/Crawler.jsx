import { useState } from 'react'
import { Link } from 'react-router-dom'

function Crawler() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [cookie, setCookie] = useState('')
  const [crawling, setCrawling] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [logs, setLogs] = useState([])

  const addLog = (message) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`])
  }

  const handleCrawl = async () => {
    if (!startDate) {
      setError('请输入开始日期')
      return
    }

    if (!cookie.trim()) {
      setError('请输入蝉妈妈Cookie')
      return
    }

    setCrawling(true)
    setError('')
    setResult(null)
    setLogs([])
    addLog('开始爬取数据...')

    try {
      const response = await fetch('http://localhost:3001/api/crawler/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate || startDate,
          cookie: cookie.trim()
        })
      })

      const data = await response.json()

      if (data.success) {
        addLog(`爬取完成: ${data.message}`)
        addLog(`数据文件: ${data.filepath}`)
        setResult(data)
      } else {
        addLog(`爬取失败: ${data.message}`)
        setError(data.message)
      }
    } catch (err) {
      addLog(`请求失败: ${err.message}`)
      setError('爬取请求失败，请检查后端服务是否运行')
    } finally {
      setCrawling(false)
    }
  }

  const handleAutoCrawl = async () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    const dateStr = yesterday.toISOString().split('T')[0]
    
    setStartDate(dateStr)
    setEndDate(dateStr)
    
    if (!cookie.trim()) {
      setError('请先输入蝉妈妈Cookie')
      return
    }
    
    setTimeout(() => {
      handleCrawl()
    }, 100)
  }

  const competitors = [
    { brand: '作业帮', count: 5 },
    { brand: '猿辅导', count: 5 },
    { brand: '高途', count: 4 },
    { brand: '希望学', count: 3 },
    { brand: '豆神', count: 3 },
    { brand: '叫叫', count: 2 },
    { brand: '有道', count: 3 },
    { brand: '新东方', count: 3 },
    { brand: '斑马', count: 3 }
  ]

  return (
    <div className="h-screen bg-[var(--bg-primary)] flex flex-col">
      <header className="border-b border-[var(--border-subtle)] bg-[var(--bg-primary)] flex-shrink-0">
        <div className="w-full px-16">
          <div className="flex items-center justify-between h-16">
            <Link to="/">
              <h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1>
            </Link>
            <nav className="flex items-center gap-8">
              <Link to="/reports" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">日报</Link>
              <Link to="/crawler" className="text-sm text-[var(--accent-forest)]">数据爬取</Link>
              <Link to="/data-tagging" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">数据打标</Link>
              <Link to="/data-entry" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-auto">
        <div className="w-full h-full px-16 py-8">
          <div className="mb-8">
            <h2 className="font-display text-3xl lg:text-4xl font-light text-[var(--text-primary)] mb-2">数据爬取</h2>
            <p className="text-[var(--text-secondary)]">从蝉妈妈平台自动爬取竞品销量数据</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6 mb-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">Cookie 配置</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">
                  请先登录蝉妈妈网站，从浏览器开发者工具中复制Cookie
                </p>
                <textarea
                  value={cookie}
                  onChange={(e) => setCookie(e.target.value)}
                  placeholder="粘贴蝉妈妈Cookie..."
                  rows={3}
                  className="w-full px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent-forest)] font-mono"
                />
                <div className="mt-3 p-3 bg-[var(--bg-secondary)] rounded-lg text-xs text-[var(--text-muted)]">
                  <p className="font-medium mb-1">获取Cookie方法：</p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>打开浏览器访问 https://www.chanmama.com 并登录</li>
                    <li>按F12打开开发者工具</li>
                    <li>切换到Network标签，刷新页面</li>
                    <li>找到任意请求，在请求头中找到Cookie字段</li>
                    <li>复制完整Cookie内容粘贴到上方输入框</li>
                  </ol>
                </div>
              </div>

              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-6">爬取配置</h3>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="block text-sm text-[var(--text-secondary)] mb-2">开始日期</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full px-4 py-2.5 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[var(--text-secondary)] mb-2">结束日期</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      placeholder="默认与开始日期相同"
                      className="w-full px-4 py-2.5 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                    />
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={handleCrawl}
                    disabled={crawling}
                    className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      crawling
                        ? 'bg-[var(--text-muted)] text-white cursor-not-allowed'
                        : 'bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 active:scale-[0.98]'
                    }`}
                  >
                    {crawling ? '爬取中...' : '开始爬取'}
                  </button>
                  <button
                    onClick={handleAutoCrawl}
                    disabled={crawling}
                    className="px-6 py-2.5 rounded-lg text-sm font-medium border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-forest)] transition-all disabled:opacity-50"
                  >
                    爬取昨日数据
                  </button>
                </div>

                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                    {error}
                  </div>
                )}

                {result && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-600 font-medium">{result.message}</p>
                    <p className="text-xs text-green-500 mt-1">文件路径: {result.filepath}</p>
                  </div>
                )}
              </div>

              {logs.length > 0 && (
                <div className="mt-6 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                  <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">爬取日志</h3>
                  <div className="bg-[var(--bg-secondary)] rounded-lg p-4 max-h-64 overflow-auto">
                    {logs.map((log, index) => (
                      <p key={index} className="text-sm text-[var(--text-secondary)] font-mono">{log}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div>
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">爬取范围</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">以下竞品店铺将被爬取：</p>
                
                <div className="space-y-3">
                  {competitors.map((item) => (
                    <div key={item.brand} className="flex justify-between items-center py-2 border-b border-[var(--border-subtle)] last:border-0">
                      <span className="text-sm text-[var(--text-primary)]">{item.brand}</span>
                      <span className="text-xs text-[var(--text-muted)]">{item.count} 个店铺</span>
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border-subtle)]">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-[var(--text-primary)] font-medium">总计</span>
                    <span className="text-sm text-[var(--accent-forest)]">{competitors.reduce((sum, item) => sum + item.count, 0)} 个店铺</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">定时任务</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">设置每日自动爬取</p>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[var(--text-primary)]">自动爬取</span>
                  <button className="relative w-12 h-6 bg-[var(--bg-secondary)] rounded-full transition-colors">
                    <span className="absolute left-1 top-1 w-4 h-4 bg-[var(--text-muted)] rounded-full transition-transform" />
                  </button>
                </div>
                
                <p className="text-xs text-[var(--text-muted)] mt-3">
                  功能开发中，暂未开放
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-[var(--border-subtle)] flex-shrink-0">
        <div className="w-full px-16 py-4">
          <div className="flex justify-between items-center">
            <p className="font-mono text-xs text-[var(--text-muted)]">Data Dive</p>
            <p className="text-xs text-[var(--text-muted)]">竞品销量数据分析平台</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Crawler
