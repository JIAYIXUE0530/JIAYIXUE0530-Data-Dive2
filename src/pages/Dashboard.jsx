import { Link } from 'react-router-dom'

function Dashboard() {
  const navItems = [
    {
      title: '日报',
      description: '竞品日报存档，查看历史分析报告，生成新的日报',
      path: '/reports',
      gradient: 'from-[#7ba3c9] to-[#9ec5e8]'
    },
    {
      title: '数据爬取',
      description: '从蝉妈妈平台自动爬取竞品销量数据',
      path: '/crawler',
      gradient: 'from-[#6b9b8f] to-[#8fc5b5]'
    },
    {
      title: '数据打标',
      description: '使用 AI 对商品数据进行智能分类打标',
      path: '/data-tagging',
      gradient: 'from-[#a88fbf] to-[#c9b8d9]'
    },
    {
      title: '每日数据录入',
      description: '录入每日销量数据，更新数据库',
      path: '/data-entry',
      gradient: 'from-[#8fa8bf] to-[#b8c9d9]'
    },
    {
      title: '全年销量数据',
      description: '查看全年销量趋势分析，数据可视化',
      path: '/sales-data',
      gradient: 'from-[#7ba3c9] to-[#9ec5e8]'
    },
    {
      title: '竞品数据库',
      description: '竞品信息数据库查询与管理',
      path: '/competitor-database',
      gradient: 'from-[#8fa8bf] to-[#b8c9d9]'
    }
  ]

  return (
    <div className="h-screen bg-[var(--bg-primary)] flex flex-col">
      <header className="border-b border-[var(--border-subtle)] bg-[var(--bg-primary)] flex-shrink-0">
        <div className="w-full px-16">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1>
            </div>
            <nav className="flex items-center gap-8">
              <Link to="/reports" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">日报</Link>
              <Link to="/crawler" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">数据爬取</Link>
              <Link to="/data-entry" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center overflow-auto">
        <div className="w-full max-w-6xl mx-auto px-6 lg:px-8 py-12 lg:py-16">
          <div className="text-center mb-16">
            <h2 className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)] mb-6">
              数据分析平台
            </h2>
            <p className="text-[var(--text-secondary)] text-lg max-w-2xl mx-auto">
              竞品销量数据分析与洞察，助力业务决策
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {navItems.map((item, index) => (
              <Link
                key={item.path}
                to={item.path}
                className="group"
              >
                <div className="h-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-[var(--accent-forest)]/10 hover:border-[var(--accent-forest)]/30 hover:-translate-y-1">
                  <div className="flex flex-col h-full">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
                      <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        {index === 0 && (
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                        )}
                        {index === 1 && (
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
                        )}
                        {index === 2 && (
                          <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                        )}
                        {index === 3 && (
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                        )}
                        {index === 4 && (
                          <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 1.875-1.875 3.75-3.75 3.75s-3.75-1.875-3.75-3.75 1.875-3.75 3.75-3.75 3.75 1.875 3.75 3.75zM4.5 19.5c0-1.875 1.875-3.75 3.75-3.75S12 17.625 12 19.5m-7.5 0v-3.375c0-.621.504-1.125 1.125-1.125h9.75c.621 0 1.125.504 1.125 1.125v3.375m-7.5 0v-6.75c0-.621.504-1.125 1.125-1.125h9.75c.621 0 1.125.504 1.125 1.125v6.75m-7.5 0h7.5" />
                        )}
                      </svg>
                    </div>
                    
                    <h3 className="font-display text-lg text-[var(--text-primary)] mb-2 group-hover:text-[var(--accent-forest)] transition-colors">
                      {item.title}
                    </h3>
                    
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1">
                      {item.description}
                    </p>
                    
                    <div className="mt-4 flex items-center text-[var(--accent-forest)] opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="text-sm font-medium">进入</span>
                      <svg className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
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

export default Dashboard
