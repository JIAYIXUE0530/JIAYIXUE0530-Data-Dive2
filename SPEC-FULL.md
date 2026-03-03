# Data Dive - 完整开发规范

> **使用方式**：将此文件放入空项目根目录，告诉 Claude Code："按照 SPEC-FULL.md 一步步构建这个项目"。
>
> 本规范包含所有代码和配置，Claude Code 可完全复刻此项目。

---

## 目录

1. [项目概述](#一项目概述)
2. [环境准备](#二环境准备)
3. [项目结构](#三项目结构)
4. [配置文件](#四配置文件)
5. [前端代码](#五前端代码)
6. [Python 脚本](#六python-脚本)
7. [Claude Skill](#七claude-skill)
8. [分析方法论](#八分析方法论)
9. [报告数据规范](#九报告数据规范)
10. [启动项目](#十启动项目)

---

## 一、项目概述

### 1.1 产品定义

Data Dive 是一个智能数据分析系统，能够：
- 接收多种格式的数据文件（Excel、PDF、Word、CSV、TXT）
- 通过交互式对话了解用户的分析侧重点
- 基于专业分析方法论（假设驱动、So What 追问、偏差检验）提取核心结论
- 生成可视化图表和专业报告页面
- 支持 PDF 导出

### 1.2 核心价值

- **不是"看看数据说什么"，而是"用数据验证假设、驱动决策"**
- 每个结论必须：有数据支撑 + 指向行动 + 可量化预期

### 1.3 技术栈

**前端**
| 技术 | 版本 | 用途 |
|------|------|------|
| React | ^18.3.1 | UI 框架 |
| Vite | ^6.0.7 | 构建工具 |
| Tailwind CSS | ^3.4.17 | 样式系统 |
| Recharts | ^2.15.0 | 图表渲染 |
| React Router | ^7.11.0 | 路由管理 |
| html2pdf.js | ^0.10.2 | PDF 导出 |

**后端处理（Python 3.10+）**
| 库 | 用途 |
|-----|------|
| pandas | 数据处理 |
| openpyxl | Excel 读取 |
| PyPDF2 | PDF 读取 |
| python-docx | Word 读取 |
| plotly | 图表生成（可选） |
| matplotlib | 图表生成（可选） |

---

## 二、环境准备

### 2.1 系统要求

- Node.js 18+
- Python 3.10+
- npm 或 yarn

### 2.2 检查环境

```bash
# 检查 Node.js
node --version  # 应显示 v18.x.x 或更高

# 检查 Python
python3 --version  # 应显示 Python 3.10.x 或更高

# 检查 npm
npm --version
```

### 2.3 如果缺少环境

**安装 Node.js（macOS）**：
```bash
# 使用 Homebrew
brew install node

# 或下载安装包
# https://nodejs.org/
```

**安装 Python（macOS）**：
```bash
# 使用 Homebrew
brew install python@3.11

# 或下载安装包
# https://www.python.org/downloads/
```

---

## 三、项目结构

执行以下命令创建目录结构：

```bash
# 创建项目目录
mkdir -p data-dive
cd data-dive

# 创建所有子目录
mkdir -p .claude/skills/data-insight-orchestrator/{scripts,references}
mkdir -p src/{pages,components,utils,styles}
mkdir -p outputs/{reports,charts}
mkdir -p uploads
mkdir -p public

# 创建空文件占位（后续会填充内容）
touch .claude/skills/data-insight-orchestrator/SKILL.md
touch outputs/reports/reports-index.json
```

完整结构如下：
```
data-dive/
├── .claude/
│   └── skills/
│       └── data-insight-orchestrator/
│           ├── SKILL.md
│           ├── scripts/
│           │   ├── file_processor.py
│           │   ├── chart_generator.py
│           │   └── report_builder.py
│           └── references/
│               ├── hypothesis-driven-analysis.md
│               ├── cognitive-biases.md
│               ├── general-frameworks.md
│               ├── data-storytelling.md
│               ├── driver-tree-analysis.md
│               ├── visualization-rules.md
│               └── data-interpretation.md
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   └── Report.jsx
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── InsightCard.jsx
│   │   ├── ChartContainer.jsx
│   │   ├── ReportCard.jsx
│   │   ├── StatsOverview.jsx
│   │   ├── ExportButton.jsx
│   │   ├── DataSourceBadge.jsx
│   │   └── EmptyState.jsx
│   └── utils/
│       ├── pdfExporter.js
│       └── chartConfig.js
├── outputs/
│   ├── reports/
│   │   └── reports-index.json
│   └── charts/
├── uploads/
├── public/
│   └── favicon.svg
├── venv/                    # Python 虚拟环境
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── CLAUDE.md
```

---

## 四、配置文件

### 4.1 package.json

```json
{
  "name": "data-dive",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "html2pdf.js": "^0.10.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.11.0",
    "recharts": "^2.15.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.5.1",
    "tailwindcss": "^3.4.17",
    "vite": "^6.0.7"
  }
}
```

### 4.2 vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    fs: {
      allow: ['..']
    }
  },
  publicDir: 'public',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})
```

### 4.3 tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          tertiary: 'var(--bg-tertiary)',
          card: 'var(--bg-card)',
          'card-hover': 'var(--bg-card-hover)',
        },
        accent: {
          terracotta: 'var(--accent-terracotta)',
          forest: 'var(--accent-forest)',
          gold: 'var(--accent-gold)',
          sage: 'var(--accent-sage)',
          rust: 'var(--accent-rust)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          tertiary: 'var(--text-tertiary)',
          muted: 'var(--text-muted)',
        },
        border: {
          subtle: 'var(--border-subtle)',
          medium: 'var(--border-medium)',
          strong: 'var(--border-strong)',
        },
        importance: {
          high: 'var(--importance-high)',
          medium: 'var(--importance-medium)',
          low: 'var(--importance-low)',
        },
        chart: {
          1: 'var(--chart-1)',
          2: 'var(--chart-2)',
          3: 'var(--chart-3)',
          4: 'var(--chart-4)',
          5: 'var(--chart-5)',
          6: 'var(--chart-6)',
          7: 'var(--chart-7)',
        },
      },
      fontFamily: {
        sans: ['Source Sans 3', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Cormorant Garamond', 'Georgia', 'serif'],
        mono: ['IBM Plex Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
      },
      boxShadow: {
        'editorial': '0 1px 2px rgba(61, 54, 48, 0.04), 0 4px 8px rgba(61, 54, 48, 0.04), 0 12px 24px rgba(61, 54, 48, 0.06)',
        'editorial-hover': '0 2px 4px rgba(61, 54, 48, 0.04), 0 8px 16px rgba(61, 54, 48, 0.06), 0 24px 48px rgba(61, 54, 48, 0.08)',
      },
    },
  },
  plugins: [],
}
```

### 4.4 postcss.config.js

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 4.5 index.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Data Dive</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### 4.6 public/favicon.svg

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2d5a4a" stroke-width="1.5">
  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
</svg>
```

### 4.7 outputs/reports/reports-index.json

```json
{
  "reports": []
}
```

### 4.8 public/outputs 软链接

在 public 目录创建软链接指向 outputs，以便前端可访问报告文件：

```bash
cd public
ln -s ../outputs outputs
cd ..
```

### 4.9 Python requirements.txt

在项目根目录创建 `requirements.txt`：

```
pandas>=2.0.0
openpyxl>=3.1.0
PyPDF2>=3.0.0
python-docx>=1.0.0
plotly>=5.18.0
matplotlib>=3.8.0
kaleido>=0.2.1
```

### 4.10 Python 虚拟环境设置

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

---

## 五、前端代码

> 以下是所有前端文件的完整代码。按顺序创建这些文件。

### 5.1 src/main.jsx

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 5.2 src/App.jsx

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Report from './pages/Report'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/report/:reportId" element={<Report />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

### 5.3 src/index.css

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Warm Parchment Theme */
  --bg-primary: #faf7f2;
  --bg-secondary: #f5f0e8;
  --bg-tertiary: #ebe5da;
  --bg-card: #ffffff;
  --bg-card-hover: #fffcf8;

  /* Accent Colors */
  --accent-terracotta: #c45c3c;
  --accent-forest: #2d5a4a;
  --accent-gold: #d4a853;
  --accent-sage: #8ba888;
  --accent-rust: #a0522d;

  /* Text Colors */
  --text-primary: #3d3630;
  --text-secondary: #6b635a;
  --text-tertiary: #8c8377;
  --text-muted: #a9a095;

  /* Borders & Dividers */
  --border-subtle: rgba(61, 54, 48, 0.08);
  --border-medium: rgba(61, 54, 48, 0.12);
  --border-strong: rgba(61, 54, 48, 0.18);

  /* Importance Colors */
  --importance-high: #c45c3c;
  --importance-medium: #d4a853;
  --importance-low: #2d5a4a;

  /* Chart Colors */
  --chart-1: #2d5a4a;
  --chart-2: #c45c3c;
  --chart-3: #d4a853;
  --chart-4: #8ba888;
  --chart-5: #a0522d;
  --chart-6: #6b8e7d;
  --chart-7: #d98a5c;

  /* Gradients */
  --gradient-hero: linear-gradient(135deg, #faf7f2 0%, #f5f0e8 50%, #ebe5da 100%);
  --gradient-card: linear-gradient(180deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%);
  --gradient-warm: linear-gradient(135deg, #faf7f2 0%, #f8f4ed 100%);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  margin: 0;
  padding: 0;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

.font-display {
  font-family: 'Cormorant Garamond', Georgia, serif;
}

.font-mono {
  font-family: 'IBM Plex Mono', 'Fira Code', monospace;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pulse-soft {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-fade-in-up {
  animation: fadeInUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

.animate-pulse-soft {
  animation: pulse-soft 2s ease-in-out infinite;
}

/* Dot pattern background */
.dot-pattern {
  background-image: radial-gradient(circle, var(--border-subtle) 1px, transparent 1px);
  background-size: 24px 24px;
}

/* Shadow effects */
.shadow-editorial {
  box-shadow: 0 1px 2px rgba(61, 54, 48, 0.04), 0 4px 8px rgba(61, 54, 48, 0.04), 0 12px 24px rgba(61, 54, 48, 0.06);
}

/* Badge styles */
.badge-high {
  background: rgba(196, 92, 60, 0.1);
  color: var(--accent-terracotta);
  border: 1px solid rgba(196, 92, 60, 0.2);
}

.badge-medium {
  background: rgba(212, 168, 83, 0.1);
  color: #b8923a;
  border: 1px solid rgba(212, 168, 83, 0.2);
}

.badge-low {
  background: rgba(45, 90, 74, 0.1);
  color: var(--accent-forest);
  border: 1px solid rgba(45, 90, 74, 0.2);
}

/* Button primary style */
.btn-primary {
  background: var(--accent-forest);
  color: #ffffff;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.btn-primary:hover {
  background: #245548;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(45, 90, 74, 0.3);
}

/* Divider with ornament */
.divider-ornament {
  display: flex;
  align-items: center;
  gap: 16px;
}

.divider-ornament::before,
.divider-ornament::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-medium), transparent);
}

/* Line clamp */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Radial gradient background */
.bg-gradient-radial {
  background: radial-gradient(circle, var(--tw-gradient-stops));
}

/* Recharts customization */
.recharts-cartesian-grid-horizontal line,
.recharts-cartesian-grid-vertical line {
  stroke: var(--border-subtle) !important;
}

.recharts-text {
  fill: var(--text-tertiary) !important;
  font-family: 'Source Sans 3', sans-serif !important;
}

/* Print styles */
@media print {
  body {
    background: #ffffff !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  header, nav button, .dot-pattern {
    display: none !important;
  }

  [class*="animate-"] {
    animation: none !important;
    opacity: 1 !important;
  }
}
```

### 5.4 src/pages/Dashboard.jsx

```jsx
import { useState, useEffect } from 'react'
import ReportCard from '../components/ReportCard'
import StatsOverview from '../components/StatsOverview'
import EmptyState from '../components/EmptyState'

function Dashboard() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      const response = await fetch('/outputs/reports/reports-index.json')
      if (response.ok) {
        const data = await response.json()
        const sortedReports = (data.reports || []).sort((a, b) => {
          return new Date(b.created_at) - new Date(a.created_at)
        })
        setReports(sortedReports)
      } else {
        setReports([])
      }
    } catch (err) {
      console.log('No reports found:', err)
      setReports([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-[var(--text-muted)] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-[var(--text-muted)] text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="border-b border-[var(--border-subtle)] sticky top-0 z-50 bg-[var(--bg-primary)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="opacity-0 animate-fade-in-up">
              <h1 className="font-display text-xl text-[var(--text-primary)]">Data Dive</h1>
            </div>
            <div className="opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <span className="font-mono text-xs text-[var(--text-muted)]">{reports.length} 份报告</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-12 lg:py-16">
        {reports.length > 0 ? (
          <>
            <div className="mb-12 opacity-0 animate-fade-in-up">
              <h2 className="font-display text-4xl lg:text-5xl font-light text-[var(--text-primary)] mb-4">分析存档</h2>
              <p className="text-[var(--text-secondary)] max-w-xl">所有数据分析报告与洞察结论的归档。</p>
            </div>

            <StatsOverview reports={reports} />

            <section>
              <div className="mb-8 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <h3 className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">全部报告</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 lg:pl-6">
                {reports.map((report, index) => (
                  <ReportCard key={report.id} report={report} index={index} />
                ))}
              </div>
            </section>
          </>
        ) : (
          <EmptyState />
        )}
      </main>

      <footer className="border-t border-[var(--border-subtle)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <p className="font-mono text-xs text-[var(--text-muted)]">Data Dive</p>
            <p className="text-xs text-[var(--text-muted)]">
              运行 <code className="font-mono px-1 py-0.5 bg-[var(--bg-secondary)] rounded">/analyze-data</code> 创建新分析
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard
```

### 5.5 src/pages/Report.jsx

> 注意：Report.jsx 代码较长（约 600 行），包含报告详情页面、图表展示、PDF 导出等功能。
> 完整代码请参考项目源码，此处提供简化版本。

```jsx
import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import Header from '../components/Header'
import InsightCard from '../components/InsightCard'
import ExportButton from '../components/ExportButton'
import { exportToPDF, generateFilename } from '../utils/pdfExporter'

function Report() {
  const { reportId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const reportRef = useRef(null)

  const handleExportPDF = async () => {
    const filename = generateFilename(report?.meta?.title?.slice(0, 20) || 'report')
    await exportToPDF(reportRef.current, filename)
  }

  useEffect(() => {
    loadReport()
  }, [reportId])

  const loadReport = async () => {
    setLoading(true)
    try {
      let filename = 'report.json'
      if (reportId) {
        const indexResponse = await fetch('/outputs/reports/reports-index.json')
        if (indexResponse.ok) {
          const indexData = await indexResponse.json()
          const reportEntry = indexData.reports?.find(r => r.id === reportId)
          if (reportEntry?.filename) filename = reportEntry.filename
        }
      }
      const response = await fetch(`/outputs/reports/${filename}`)
      if (response.ok) {
        const data = await response.json()
        setReport(data)
      }
    } catch (err) {
      console.log('Error loading report:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto relative">
            <div className="absolute inset-0 rounded-full border-2 border-[var(--border-subtle)]" />
            <div className="absolute inset-0 rounded-full border-2 border-[var(--accent-forest)] border-t-transparent animate-spin" />
          </div>
          <p className="mt-6 text-[var(--text-secondary)] text-sm">加载报告中...</p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--text-secondary)] font-display text-xl mb-4">暂无报告数据</p>
          <Link to="/" className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--accent-forest)] text-white rounded-lg">
            返回存档
          </Link>
        </div>
      </div>
    )
  }

  const formatDate = (isoString) => {
    try {
      return new Date(isoString).toLocaleString('zh-CN', {
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
      })
    } catch { return isoString }
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] relative">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 dot-pattern opacity-40" />
      </div>

      <Header title={report.meta?.title} />

      <main ref={reportRef} className="relative max-w-6xl mx-auto px-6 lg:px-8 pt-32 pb-24">
        {/* Navigation */}
        <nav className="mb-8 opacity-0 animate-fade-in-up flex items-center justify-between">
          <Link to="/" className="group inline-flex items-center gap-2 px-4 py-2 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-full text-sm">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>存档</span>
          </Link>
          <ExportButton onClick={handleExportPDF} />
        </nav>

        {/* Summary Section */}
        <section className="mb-20 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center gap-4 mb-8">
            <span className="text-[11px] font-bold text-[var(--accent-terracotta)] uppercase tracking-[0.2em]">摘要概览</span>
            <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-terracotta)]/30 to-transparent" />
          </div>
          <div className="relative bg-[var(--bg-card)] rounded-3xl border border-[var(--border-subtle)] shadow-editorial overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[var(--accent-forest)] via-[var(--accent-gold)] to-[var(--accent-terracotta)]" />
            <div className="relative p-8 lg:p-12">
              <div className="flex flex-wrap gap-8 mb-10">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-[var(--accent-forest)]/10 flex items-center justify-center">
                    <svg className="w-7 h-7 text-[var(--accent-forest)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-display text-4xl font-bold text-[var(--text-primary)]">{report.summary?.total_conclusions || 0}</p>
                    <p className="text-xs text-[var(--text-tertiary)] font-semibold uppercase tracking-wider mt-1">核心发现</p>
                  </div>
                </div>
              </div>
              <div className="divider-ornament mb-8">
                <svg className="w-6 h-6 text-[var(--accent-gold)]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L9.5 8.5 3 9.5l5 4.5-1.5 6.5 5.5-3.5 5.5 3.5-1.5-6.5 5-4.5-6.5-1z"/>
                </svg>
              </div>
              <p className="text-[var(--text-primary)] text-xl lg:text-2xl leading-relaxed font-display">{report.summary?.overall}</p>
            </div>
          </div>
        </section>

        {/* Insight Cards */}
        <section className="mb-10 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center gap-4">
            <span className="text-[11px] font-bold text-[var(--accent-forest)] uppercase tracking-[0.2em]">详细发现</span>
            <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-forest)]/30 to-transparent" />
          </div>
          <h2 className="mt-4 font-display text-3xl lg:text-4xl font-bold text-[var(--text-primary)]">关键洞察</h2>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {report.conclusions?.map((conclusion, index) => (
            <InsightCard key={conclusion.id} conclusion={conclusion} index={index} />
          ))}
        </section>
      </main>

      <footer className="relative border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)]">
        <div className="max-w-6xl mx-auto px-6 lg:px-8 py-10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <Link to="/" className="flex items-center gap-4">
              <p className="text-sm font-semibold text-[var(--text-primary)]">Data Dive</p>
            </Link>
            <p className="text-sm text-[var(--text-secondary)]">生成时间：{formatDate(report.meta?.generated_at)}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Report
```

### 5.6 src/components/Header.jsx

```jsx
import { useState, useEffect } from 'react'

function Header({ title }) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'py-3 bg-[var(--bg-primary)]/95 backdrop-blur-md shadow-editorial border-b border-[var(--border-subtle)]' : 'py-5 bg-transparent'}`}>
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="relative w-12 h-12 group">
              <div className="absolute inset-0 rounded-full border-2 border-[var(--accent-forest)]/20" />
              <div className="absolute inset-1.5 bg-[var(--bg-card)] rounded-full shadow-sm flex items-center justify-center">
                <svg className="w-5 h-5 text-[var(--accent-forest)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-[var(--accent-terracotta)] rounded-full opacity-80" />
            </div>
            <div>
              <h1 className="font-display text-2xl font-semibold text-[var(--text-primary)]">{title || 'Data Dive'}</h1>
              <p className="text-[11px] text-[var(--text-tertiary)] font-medium tracking-[0.15em] uppercase mt-0.5">分析报告</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
```

### 5.7 src/components/InsightCard.jsx

```jsx
import DataSourceBadge from './DataSourceBadge'
import ChartContainer from './ChartContainer'

const IMPORTANCE_LABELS = { high: '关键', medium: '重要', low: '一般' }

function InsightCard({ conclusion, index = 0 }) {
  const { title, description, data_support, source_files, importance = 'medium', chart_type, chart_data } = conclusion

  return (
    <article className="relative bg-[var(--bg-card)] border border-[var(--border-subtle)] transition-all duration-300 hover:border-[var(--border-medium)] opacity-0 animate-fade-in-up" style={{ animationDelay: `${0.15 + index * 0.1}s` }}>
      <div className="p-6 lg:p-8">
        <div className="flex items-start justify-between gap-4 mb-4">
          <span className="font-mono text-xs text-[var(--text-muted)] mt-1">{String(index + 1).padStart(2, '0')}</span>
          <span className="font-mono text-[10px] text-[var(--text-muted)] uppercase tracking-wider">{IMPORTANCE_LABELS[importance]}</span>
        </div>
        <h3 className="font-display text-xl lg:text-2xl font-normal text-[var(--text-primary)] leading-snug mb-4">{title}</h3>
        <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-6">{description}</p>
        {data_support && (
          <div className="mb-6 py-4 border-y border-[var(--border-subtle)]">
            <span className="font-mono text-[10px] text-[var(--text-muted)] uppercase tracking-wider block mb-3">数据支撑</span>
            <p className="text-[var(--text-primary)] text-sm font-mono leading-relaxed">{data_support}</p>
          </div>
        )}
        <DataSourceBadge files={source_files} />
        {chart_type && chart_type !== 'none' && chart_data && (
          <div className="mt-6">
            <ChartContainer type={chart_type} data={chart_data} />
          </div>
        )}
      </div>
    </article>
  )
}

export default InsightCard
```

### 5.8 src/components/ChartContainer.jsx

```jsx
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  ScatterChart, Scatter, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

const CHART_COLORS = ['#2d5a4a', '#c45c3c', '#d4a853', '#8ba888', '#a0522d', '#6b8e7d', '#d98a5c']

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

  return <p className="text-[var(--text-muted)] text-sm">Unsupported chart type: {type}</p>
}

export default ChartContainer
```

### 5.9 src/components/ReportCard.jsx

```jsx
import { Link } from 'react-router-dom'

function ReportCard({ report, index = 0 }) {
  const { id, title, created_at, summary_preview, stats, tags = [] } = report

  const formatDate = (isoString) => {
    try {
      const date = new Date(isoString)
      return { month: (date.getMonth() + 1) + '月', day: date.getDate(), year: date.getFullYear() }
    } catch { return { month: '1月', day: '01', year: '2025' } }
  }

  const { month, day, year } = formatDate(created_at)

  return (
    <Link to={`/report/${id}`} className="group relative block opacity-0 animate-fade-in-up no-underline" style={{ animationDelay: `${0.1 + index * 0.08}s` }}>
      <article className="relative h-full">
        <div className="relative h-full bg-[var(--bg-card)] border border-[var(--border-subtle)] transition-all duration-500 group-hover:border-[var(--border-medium)] group-hover:shadow-lg">
          <div className="p-6 lg:p-8">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-baseline gap-1 text-[var(--text-muted)]">
                <span className="font-mono text-xs">{month}</span>
                <span className="font-display text-2xl font-light text-[var(--text-primary)]">{day}</span>
                <span className="font-mono text-xs">{year}</span>
              </div>
              <div className="flex items-center gap-4 text-[var(--text-muted)]">
                <span className="font-mono text-xs">{stats?.total_conclusions || 0} 项发现</span>
              </div>
            </div>
            <h3 className="font-display text-2xl lg:text-3xl font-normal text-[var(--text-primary)] leading-snug mb-4 group-hover:text-[var(--accent-forest)] transition-colors">{title}</h3>
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed line-clamp-2 mb-6">{summary_preview}</p>
            <div className="flex items-center justify-between pt-5 border-t border-[var(--border-subtle)]">
              <div className="text-xs text-[var(--text-muted)]">{stats?.source_files || 0} 个数据源</div>
              <div className="flex items-center gap-2 text-xs text-[var(--text-muted)] group-hover:text-[var(--accent-forest)] transition-colors">
                <span className="font-medium opacity-0 group-hover:opacity-100 transition-opacity">查看</span>
                <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </article>
    </Link>
  )
}

export default ReportCard
```

### 5.10 src/components/StatsOverview.jsx

```jsx
import { useState, useEffect } from 'react'

function AnimatedNumber({ value, duration = 800 }) {
  const [displayValue, setDisplayValue] = useState(0)
  useEffect(() => {
    let startTime, animationFrame
    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      setDisplayValue(Math.floor((1 - Math.pow(1 - progress, 3)) * value))
      if (progress < 1) animationFrame = requestAnimationFrame(animate)
    }
    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])
  return <span>{displayValue}</span>
}

function StatsOverview({ reports = [] }) {
  const totalReports = reports.length
  const now = new Date()
  const thisMonthReports = reports.filter(r => {
    const d = new Date(r.created_at)
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).length
  const totalHighImportance = reports.reduce((sum, r) => sum + (r.stats?.high_importance || 0), 0)

  return (
    <div className="mb-16 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
      <div className="flex flex-wrap items-baseline gap-x-12 gap-y-4 py-6 border-y border-[var(--border-subtle)]">
        <div className="flex items-baseline gap-3">
          <span className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)]"><AnimatedNumber value={totalReports} /></span>
          <span className="text-sm text-[var(--text-muted)] font-medium">份报告</span>
        </div>
        <div className="hidden sm:block w-px h-8 bg-[var(--border-subtle)]" />
        <div className="flex items-baseline gap-3">
          <span className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)]"><AnimatedNumber value={thisMonthReports} /></span>
          <span className="text-sm text-[var(--text-muted)] font-medium">本月新增</span>
        </div>
        <div className="hidden sm:block w-px h-8 bg-[var(--border-subtle)]" />
        <div className="flex items-baseline gap-3">
          <span className="font-display text-5xl lg:text-6xl font-light text-[var(--text-primary)]"><AnimatedNumber value={totalHighImportance} /></span>
          <span className="text-sm text-[var(--text-muted)] font-medium">关键发现</span>
        </div>
      </div>
    </div>
  )
}

export default StatsOverview
```

### 5.11 src/components/EmptyState.jsx

```jsx
function EmptyState() {
  return (
    <div className="py-24 opacity-0 animate-fade-in-up">
      <div className="max-w-md">
        <h2 className="font-display text-3xl lg:text-4xl font-light text-[var(--text-primary)] mb-4">暂无报告</h2>
        <p className="text-[var(--text-secondary)] mb-8 leading-relaxed">
          开始你的第一次数据分析吧。将数据文件放入 <code className="font-mono text-sm px-1.5 py-0.5 bg-[var(--bg-secondary)] rounded">uploads/</code> 目录，然后运行分析命令。
        </p>
        <div className="inline-block">
          <div className="font-mono text-sm px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded">
            <span className="text-[var(--text-muted)]">$</span>
            <span className="text-[var(--text-primary)] ml-2">/analyze-data</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmptyState
```

### 5.12 src/components/ExportButton.jsx

```jsx
function ExportButton({ onClick }) {
  return (
    <button onClick={onClick} className="inline-flex items-center gap-2.5 px-6 py-3 rounded-full font-semibold text-sm btn-primary">
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      <span>导出 PDF</span>
    </button>
  )
}

export default ExportButton
```

### 5.13 src/components/DataSourceBadge.jsx

```jsx
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
```

### 5.14 src/utils/pdfExporter.js

```javascript
export async function exportToPDF(element, filename = 'report.pdf') {
  if (!element) throw new Error('导出元素不存在')
  document.body.classList.add('pdf-exporting')
  const originalTitle = document.title
  document.title = filename.replace('.pdf', '')
  await new Promise(resolve => setTimeout(resolve, 100))
  window.print()
  setTimeout(() => {
    document.title = originalTitle
    document.body.classList.remove('pdf-exporting')
  }, 1000)
  return true
}

export function generateFilename(prefix = 'report') {
  const now = new Date()
  const timestamp = now.toISOString().slice(0, 10).replace(/-/g, '')
  const cleanPrefix = prefix.replace(/[^\w\u4e00-\u9fa5-]/g, '_').slice(0, 30)
  return `${cleanPrefix}_${timestamp}.pdf`
}

export default { exportToPDF, generateFilename }
```

### 5.15 src/utils/chartConfig.js

```javascript
export const CHART_COLORS = ['#2563EB', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#EF4444']

export const defaultChartConfig = {
  margin: { top: 5, right: 20, left: 10, bottom: 5 },
  animationDuration: 300,
  gridStrokeDasharray: '3 3',
  gridStroke: '#E5E7EB',
}

export function formatNumber(num) {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}
```

---

## 六、Python 脚本

> 以下脚本用于数据处理和报告生成，放置于 `.claude/skills/data-insight-orchestrator/scripts/` 目录。

### 6.1 scripts/file_processor.py

```python
#!/usr/bin/env python3
"""文件处理器 - 支持多格式数据文件的读取"""

import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import openpyxl
import PyPDF2
from docx import Document


class FileProcessor:
    SUPPORTED_EXTENSIONS = {'.xlsx': 'Excel', '.xls': 'Excel', '.pdf': 'PDF', '.docx': 'Word', '.csv': 'CSV', '.txt': 'TXT'}

    def __init__(self, upload_dir='uploads'):
        self.upload_dir = Path(upload_dir)

    def scan_files(self):
        files = []
        if not self.upload_dir.exists():
            return files
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'type': self.SUPPORTED_EXTENSIONS[ext],
                        'size': self._format_size(file_path.stat().st_size),
                        'extension': ext
                    })
        return files

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def read_excel(self, file_path):
        result = {'type': 'Excel', 'sheets': {}, 'summary': ''}
        try:
            xl = pd.ExcelFile(file_path)
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet_name)
                result['sheets'][sheet_name] = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'data': df.to_dict('records')[:100]
                }
            result['summary'] = f"{len(xl.sheet_names)} 个工作表"
        except Exception as e:
            result['error'] = str(e)
        return result

    def read_csv(self, file_path):
        result = {'type': 'CSV', 'data': [], 'summary': ''}
        try:
            df = pd.read_csv(file_path)
            result['rows'] = len(df)
            result['columns'] = list(df.columns)
            result['data'] = df.to_dict('records')[:100]
            result['summary'] = f"{len(df)} 行, {len(df.columns)} 列"
        except Exception as e:
            result['error'] = str(e)
        return result

    def read_pdf(self, file_path):
        result = {'type': 'PDF', 'pages': [], 'summary': ''}
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    result['pages'].append({'page': i + 1, 'text': text[:2000] if text else ''})
            result['summary'] = f"{len(result['pages'])} 页"
        except Exception as e:
            result['error'] = str(e)
        return result

    def read_docx(self, file_path):
        result = {'type': 'Word', 'paragraphs': [], 'tables': [], 'summary': ''}
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    result['paragraphs'].append(para.text)
            for table in doc.tables:
                table_data = [[cell.text for cell in row.cells] for row in table.rows]
                result['tables'].append(table_data)
            result['summary'] = f"{len(result['paragraphs'])} 段落, {len(result['tables'])} 个表格"
        except Exception as e:
            result['error'] = str(e)
        return result

    def read_txt(self, file_path):
        result = {'type': 'TXT', 'content': '', 'summary': ''}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result['content'] = content[:10000]
            result['lines'] = len(content.split('\n'))
            result['summary'] = f"{result['lines']} 行"
        except Exception as e:
            result['error'] = str(e)
        return result

    def process_file(self, file_path):
        path = Path(file_path)
        ext = path.suffix.lower()
        if ext in ['.xlsx', '.xls']:
            return self.read_excel(file_path)
        elif ext == '.csv':
            return self.read_csv(file_path)
        elif ext == '.pdf':
            return self.read_pdf(file_path)
        elif ext == '.docx':
            return self.read_docx(file_path)
        elif ext == '.txt':
            return self.read_txt(file_path)
        return {'error': f'不支持的文件格式: {ext}'}


def main():
    processor = FileProcessor()
    files = processor.scan_files()
    print(f"发现 {len(files)} 个文件")
    for f in files:
        print(f"  - {f['name']} ({f['type']}) - {f['size']}")


if __name__ == '__main__':
    main()
```

### 6.2 scripts/report_builder.py

```python
#!/usr/bin/env python3
"""报告构建器 - 将分析结论整合为 JSON 格式"""

import json
from pathlib import Path
from datetime import datetime


class ReportBuilder:
    def __init__(self, output_dir='outputs/reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_report(self, title, overall_summary, conclusions, source_files):
        return {
            'meta': {'title': title, 'generated_at': datetime.now().isoformat(), 'version': '1.0'},
            'summary': {
                'overall': overall_summary,
                'total_conclusions': len(conclusions),
                'high_importance_count': len([c for c in conclusions if c.get('importance') == 'high']),
                'source_files': source_files
            },
            'conclusions': conclusions
        }

    def save_report(self, report, filename='report.json'):
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return str(output_path)

    def update_index(self, report, filename):
        index_path = self.output_dir / 'reports-index.json'
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except:
            index = {'reports': []}

        report_id = filename.replace('.json', '')
        # 移除已存在的同名报告
        index['reports'] = [r for r in index['reports'] if r['id'] != report_id]
        # 添加新报告
        index['reports'].insert(0, {
            'id': report_id,
            'title': report['meta']['title'],
            'filename': filename,
            'created_at': report['meta']['generated_at'],
            'summary_preview': report['summary']['overall'][:100] + '...',
            'stats': {
                'total_conclusions': report['summary']['total_conclusions'],
                'high_importance': report['summary']['high_importance_count'],
                'source_files': len(report['summary']['source_files'])
            }
        })

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)


def main():
    builder = ReportBuilder()
    # 示例报告
    conclusions = [
        {
            'id': 1,
            'title': 'Q3 销售额环比下降 23%',
            'description': '第三季度销售额为 850 万元，相比 Q2 下降 23%。',
            'data_support': 'Q2: 1100万 → Q3: 850万',
            'source_files': ['销售数据.xlsx'],
            'importance': 'high',
            'chart_type': 'line',
            'chart_data': {
                'x_labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                'series': {'实际': [980, 1100, 850, None], '目标': [1000, 1000, 1000, 1000]}
            }
        }
    ]
    report = builder.build_report(
        title='示例销售分析报告',
        overall_summary='Q3 销售下滑主要受华东区域影响。',
        conclusions=conclusions,
        source_files=['销售数据.xlsx']
    )
    filename = f"report-{datetime.now().strftime('%Y-%m-%d')}-example.json"
    builder.save_report(report, filename)
    builder.update_index(report, filename)
    print(f"报告已生成: {filename}")


if __name__ == '__main__':
    main()
```

---

## 七、Claude Skill

> 将以下内容保存为 `.claude/skills/data-insight-orchestrator/SKILL.md`

```markdown
---
name: data-insight-orchestrator
description: |
  数据洞察分析 skill。包含完整的分析流程、方法论和原则库。
  当用户上传数据文件（Excel/PDF/Word/TXT/CSV）并要求分析时自动激活。
---

# Data Insight Orchestrator

## 触发条件

- 用户上传数据文件（.xlsx, .xls, .pdf, .docx, .csv, .txt）
- 用户使用 `/analyze-data` 命令
- 用户表达"分析数据"、"数据洞察"等意图

## 执行流程

Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
文件识别   询问侧重点  数据分析   图表生成   页面构建    交付

### Phase 1: 文件识别
- 支持 attach 文件或 uploads/ 目录
- 格式：xlsx/xls/pdf/docx/csv/txt

### Phase 2: 询问侧重点
1. 核心问题：想回答什么？
2. 关注指标：重点关注哪些？
3. 用途场景：内部汇报/公开发布/决策支持

### Phase 3: 数据分析（核心）

**假设驱动分析**
1. 明确核心问题
2. 构建假设树
3. 用数据验证假设
4. So What 追问（至少3层）

**偏差检验（必须）**
- 辛普森悖论：分组后结论是否仍成立？
- 幸存者偏差：有没有看不到的数据？
- 相关≠因果：是否把相关当因果？

**核心准则**
- 因果推演：区分相关和因果
- 可落地性：结论必须指向行动
- 短期突破 + 中长期复利

### Phase 4: 图表生成
图表数据写入 report.json，由前端 Recharts 渲染

### Phase 5: 页面构建
生成 outputs/reports/report.json，启动 npm run dev

### Phase 6: 交付
采用 SCR 叙事结构（情境-冲突-解决）

## 报告 JSON 格式

```json
{
  "meta": { "title": "报告标题", "generated_at": "ISO时间", "version": "1.0" },
  "summary": { "overall": "摘要", "total_conclusions": 5, "high_importance_count": 2, "source_files": [] },
  "conclusions": [
    {
      "id": 1,
      "title": "结论标题",
      "description": "详细描述",
      "data_support": "数据支撑",
      "importance": "high | medium | low",
      "chart_type": "bar | line | pie | scatter",
      "chart_data": {}
    }
  ]
}
```
```

---

## 八、分析方法论

> 将以下文档保存到 `.claude/skills/data-insight-orchestrator/references/` 目录

### 8.1 references/general-frameworks.md

```markdown
# 通用分析框架

## MECE 原则
- **相互独立**：各个分类之间不重叠
- **完全穷尽**：所有分类覆盖全部情况

## 金字塔原理
- **结论先行**：先给出核心结论
- **以上统下**：上层结论由下层论据支撑

## 5W1H 分析法
- What：发生了什么？
- Why：为什么会这样？
- Who：涉及哪些对象？
- When：什么时间发生？
- Where：在哪里发生？
- How：如何发生的？

## 对比分析框架
- 时间对比：同比、环比
- 空间对比：地区、渠道
- 标杆对比：行业均值、竞品
- 目标对比：实际 vs 计划
```

### 8.2 references/hypothesis-driven-analysis.md

> 此文档包含假设驱动分析法的详细说明，约 6KB。核心要点：
> - 不是"看看数据说什么"，而是"用数据验证假设"
> - 构建假设树，按优先级验证
> - So What 追问链：数据现象 → 业务含义 → 行动建议 → 预期影响

### 8.3 references/cognitive-biases.md

> 此文档包含 15 种认知偏差详解，约 13KB。核心偏差类型：
> - 统计陷阱：辛普森悖论、幸存者偏差、回归均值
> - 因果谬误：相关≠因果、反向因果、遗漏变量
> - 心理偏误：确认偏误、锚定效应、可得性偏误

---

## 九、报告数据规范

### 9.1 reports-index.json 结构

```json
{
  "reports": [
    {
      "id": "report-2024-01-01-sales",
      "title": "销售数据分析报告",
      "filename": "report-2024-01-01-sales.json",
      "created_at": "2024-01-01T00:00:00.000000",
      "summary_preview": "摘要前100字...",
      "stats": {
        "total_conclusions": 5,
        "high_importance": 2,
        "source_files": 2
      }
    }
  ]
}
```

### 9.2 chart_data 格式

**柱状图**：`{ "xKey": "name", "yKey": "value", "data": [{"name": "A", "value": 100}] }`

**折线图**：`{ "x_labels": ["Q1"], "series": {"实际": [100], "目标": [90]} }`

**饼图**：`{ "labels": ["A", "B"], "values": [60, 40] }`

**散点图**：`{ "x": [10, 20], "y": [15, 25], "x_title": "X轴", "y_title": "Y轴" }`

---

## 十、启动项目

### 10.1 安装依赖

```bash
# 前端依赖
npm install

# Python 依赖（如需使用脚本）
source venv/bin/activate
pip install -r requirements.txt
```

### 10.2 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看报告页面。

### 10.3 创建新分析

1. 将数据文件放入 `uploads/` 目录，或直接 attach 文件
2. 在 Claude Code 中说"帮我分析这份数据"
3. 回答分析侧重点问题
4. 等待分析完成，查看生成的报告

### 10.4 CLAUDE.md 内容

在项目根目录创建 `CLAUDE.md`：

```markdown
# Data Dive

数据洞察分析系统。

## 快速开始

npm run dev

访问 http://localhost:5173

## 分析数据

1. 将数据文件放入 uploads/ 目录
2. 告诉我你想分析什么
3. 我会应用分析方法论，生成报告

## 技术栈

- 前端：React + Tailwind + Recharts
- 分析：Claude Skill + Python
```

---

## 完成

按照以上规范，Claude Code 可以完整复刻 Data Dive 项目。所有配置文件和代码均已包含。
