import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import Report from './pages/Report'
import DataEntry from './pages/DataEntry'
import SalesData from './pages/SalesData'
import CompetitorDatabase from './pages/CompetitorDatabase'
import Crawler from './pages/Crawler'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/report/:reportId" element={<Report />} />
        <Route path="/data-entry" element={<DataEntry />} />
        <Route path="/sales-data" element={<SalesData />} />
        <Route path="/competitor-database" element={<CompetitorDatabase />} />
        <Route path="/crawler" element={<Crawler />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App