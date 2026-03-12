import { useState, useEffect } from 'react'

function Header({ title, activeTab, onTabChange }) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const tabs = [
    { id: 'daily', label: '日报' },
    { id: 'upload', label: '每日数据录入' },
    { id: 'yearly', label: '全年销量数据' },
    { id: 'database', label: '竞品数据库' }
  ]

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'py-3 bg-[var(--bg-primary)]/95 backdrop-blur-md shadow-editorial border-b border-[var(--border-subtle)]' : 'py-5 bg-transparent'}`}>
      <div className="w-full px-16">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="relative w-10 h-10 group">
              <div className="absolute inset-0 rounded-full border-2 border-[var(--accent-forest)]/20" />
              <div className="absolute inset-1.5 bg-[var(--bg-card)] rounded-full shadow-sm flex items-center justify-center">
                <svg className="w-4 h-4 text-[var(--accent-forest)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <h1 className="font-display text-xl font-semibold text-[var(--text-primary)]">{title || 'Data Dive'}</h1>
          </div>
          
          <div className="flex items-center gap-1 bg-[var(--bg-secondary)] rounded-lg p-1 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => onTabChange?.(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                  activeTab === tab.id
                    ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
