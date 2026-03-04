import { Link } from 'react-router-dom'
import DataUpload from '../components/DataUpload'

function DataEntry() {
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
              <Link to="/data-entry" className="text-sm text-[var(--accent-forest)]">每日数据录入</Link>
              <Link to="/sales-data" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">全年销量数据</Link>
              <Link to="/competitor-database" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">竞品数据库</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-auto">
        <div className="w-full h-full px-16 py-8">
          <DataUpload />
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

export default DataEntry
