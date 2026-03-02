import { useState, useEffect } from 'react'

function TestReport() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Starting fetch...')
        const url = 'http://localhost:5173/outputs/reports/report-2026-02-28-daily-dashboard.json'
        console.log('URL:', url)
        const response = await fetch(url)
        console.log('Response:', response)
        console.log('Status:', response.status)
        
        if (response.ok) {
          const json = await response.json()
          console.log('JSON:', json)
          setData(json)
        } else {
          setError(`HTTP ${response.status}: ${response.statusText}`)
        }
      } catch (err) {
        console.error('Error:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!data) return <div>No data</div>

  return (
    <div>
      <h1>{data.meta?.title}</h1>
      <p>{data.summary?.overall}</p>
      <p>Total: {data.summary?.total_conclusions}</p>
    </div>
  )
}

export default TestReport