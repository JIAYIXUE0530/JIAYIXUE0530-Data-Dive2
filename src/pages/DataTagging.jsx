import { useState } from 'react'
import { Link } from 'react-router-dom'

function DataTagging() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [tagging, setTagging] = useState(false)
  const [result, setResult] = useState(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setResult(null)
    }
  }

  const handleTagging = async () => {
    if (!selectedFile) return

    setTagging(true)
    setResult(null)

    setTimeout(() => {
      setResult({
        success: false,
        message: '数据打标功能正在开发中，敬请期待'
      })
      setTagging(false)
    }, 1000)
  }

  const taggingRules = [
    { category: '学段分类', description: '根据商品名称自动识别学段（小学/初中/高中/低幼）' },
    { category: '学科分类', description: '根据商品名称自动识别学科（语文/数学/英语等）' },
    { category: '链路分类', description: '根据价格区间自动识别链路（低价/中价/正价）' },
    { category: '品牌分类', description: '根据店铺名称自动识别竞品品牌' }
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
              <Link to="/crawler" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">数据爬取</Link>
              <Link to="/data-entry" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
              <Link to="/data-tagging" className="text-sm text-[var(--accent-forest)]">数据打标</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-auto">
        <div className="w-full h-full px-16 py-8">
          <div className="mb-8">
            <h2 className="font-display text-3xl lg:text-4xl font-light text-[var(--text-primary)] mb-2">数据打标</h2>
            <p className="text-[var(--text-secondary)]">使用 AI 对商品数据进行分类打标</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-6">上传数据文件</h3>
                
                <div className="mb-6">
                  <label className="block text-sm text-[var(--text-secondary)] mb-2">选择 Excel 文件</label>
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileChange}
                    className="w-full px-4 py-2.5 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-forest)]"
                  />
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={handleTagging}
                    disabled={tagging || !selectedFile}
                    className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      tagging || !selectedFile
                        ? 'bg-[var(--text-muted)] text-white cursor-not-allowed'
                        : 'bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90 active:scale-[0.98]'
                    }`}
                  >
                    {tagging ? '打标中...' : '开始打标'}
                  </button>
                </div>

                {result && (
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-600">{result.message}</p>
                  </div>
                )}

                <div className="mt-6 p-4 bg-[var(--bg-secondary)] rounded-lg border border-[var(--border-subtle)]">
                  <p className="text-sm text-[var(--text-muted)]">
                    此功能正在开发中，将支持使用 DeepSeek API 对商品数据进行智能分类打标。
                  </p>
                </div>
              </div>
            </div>

            <div>
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">打标规则</h3>
                <p className="text-sm text-[var(--text-secondary)] mb-4">自动识别以下分类：</p>
                
                <div className="space-y-4">
                  {taggingRules.map((rule, index) => (
                    <div key={index} className="pb-4 border-b border-[var(--border-subtle)] last:border-0 last:pb-0">
                      <h4 className="text-sm font-medium text-[var(--text-primary)] mb-1">{rule.category}</h4>
                      <p className="text-xs text-[var(--text-muted)]">{rule.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6">
                <h3 className="font-display text-lg text-[var(--text-primary)] mb-4">AI 模型</h3>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-[#a88fbf] to-[#c9b8d9] rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--text-primary)]">DeepSeek</p>
                    <p className="text-xs text-[var(--text-muted)]">智能文本分析</p>
                  </div>
                </div>
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

export default DataTagging
