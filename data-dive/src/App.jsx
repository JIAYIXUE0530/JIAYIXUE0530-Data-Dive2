import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Report from './pages/Report'
import AIStockDashboard from './pages/AIStockDashboard'
import AIStockReport from './pages/AIStockReport'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/report/:reportId" element={<Report />} />
        <Route path="/ai-stock" element={<AIStockDashboard />} />
        <Route path="/ai-stock-report/:reportId" element={<AIStockReport />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App