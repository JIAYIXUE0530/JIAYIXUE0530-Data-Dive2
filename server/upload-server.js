import express from 'express'
import multer from 'multer'
import path from 'path'
import fs from 'fs'
import XLSX from 'xlsx'
import { fileURLToPath } from 'url'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const PORT = 3001

// 数据目录 - 必须在其他配置之前定义
const DATA_DIR = path.join(__dirname, '..', 'uploads')
const ARCHIVE_DIR = path.join(__dirname, '..', 'archive')

// 确保目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true })
}
if (!fs.existsSync(ARCHIVE_DIR)) {
  fs.mkdirSync(ARCHIVE_DIR, { recursive: true })
}

// 配置存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, DATA_DIR)
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now()
    cb(null, `upload_${timestamp}${path.extname(file.originalname)}`)
  }
})

const upload = multer({ 
  storage,
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase()
    if (ext === '.xlsx' || ext === '.xls') {
      cb(null, true)
    } else {
      cb(new Error('只支持 Excel 文件'))
    }
  }
})

// CORS 配置
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.header('Access-Control-Allow-Headers', 'Content-Type')
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200)
  }
  next()
})

// 解析 JSON 请求体
app.use(express.json())

// 获取最新数据文件
function getLatestFile() {
  const files = fs.readdirSync(DATA_DIR)
    .filter(f => f.endsWith('.xlsx') || f.endsWith('.xls'))
    .map(f => ({
      name: f,
      path: path.join(DATA_DIR, f),
      time: fs.statSync(path.join(DATA_DIR, f)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time)
  
  return files.length > 0 ? files[0] : null
}

// 处理 NaN、Infinity 等特殊值
function sanitizeData(data) {
  return data.map(row => {
    const sanitizedRow = {}
    for (const [key, value] of Object.entries(row)) {
      if (typeof value === 'number') {
        if (Number.isNaN(value) || !Number.isFinite(value)) {
          sanitizedRow[key] = null
        } else {
          sanitizedRow[key] = value
        }
      } else {
        sanitizedRow[key] = value
      }
    }
    return sanitizedRow
  })
}

// 上传接口
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: '没有收到文件' })
    }

    const filePath = req.file.path
    const workbook = XLSX.readFile(filePath)
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const data = XLSX.utils.sheet_to_json(worksheet)

    if (data.length === 0) {
      return res.status(400).json({ error: '文件中没有数据' })
    }

    // 归档旧文件
    const latestFile = getLatestFile()
    if (latestFile && latestFile.path !== filePath) {
      const archivePath = path.join(ARCHIVE_DIR, `${Date.now()}_${latestFile.name}`)
      fs.renameSync(latestFile.path, archivePath)
    }

    // 重命名上传的文件
    const newPath = path.join(DATA_DIR, `竞品销量数据_${Date.now()}.xlsx`)
    fs.renameSync(filePath, newPath)

    res.json({ 
      success: true,
      records: data.length,
      message: `成功上传 ${data.length} 条记录`
    })

  } catch (err) {
    console.error('Upload error:', err)
    res.status(500).json({ error: err.message || '处理文件时出错' })
  }
})

// 获取数据文件列表
app.get('/api/files', (req, res) => {
  try {
    const dataFiles = fs.readdirSync(DATA_DIR)
      .filter(f => f.endsWith('.xlsx') || f.endsWith('.xls'))
      .map(f => ({
        name: f,
        path: path.join(DATA_DIR, f),
        time: fs.statSync(path.join(DATA_DIR, f)).mtime.getTime()
      }))
      .sort((a, b) => b.time - a.time)

    res.json({ files: dataFiles })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

// 获取数据库全部数据（支持分页）
app.get('/api/database', (req, res) => {
  try {
    const latestFile = getLatestFile()
    
    if (!latestFile) {
      return res.json({ data: [], total: 0, file: null })
    }

    const page = parseInt(req.query.page) || 1
    const pageSize = parseInt(req.query.pageSize) || 100
    
    const workbook = XLSX.readFile(latestFile.path)
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const rawData = XLSX.utils.sheet_to_json(worksheet)
    
    // 处理 NaN、Infinity 等特殊值
    const data = sanitizeData(rawData)
    
    // 分页
    const total = data.length
    const totalPages = Math.ceil(total / pageSize)
    const startIndex = (page - 1) * pageSize
    const endIndex = Math.min(startIndex + pageSize, total)
    const paginatedData = data.slice(startIndex, endIndex)

    res.json({ 
      data: paginatedData,
      total: total,
      page: page,
      pageSize: pageSize,
      totalPages: totalPages,
      file: latestFile.name
    })
  } catch (err) {
    console.error('Database error:', err)
    res.status(500).json({ error: err.message })
  }
})

// 获取筛选选项（不返回全部数据，只返回选项）
app.get('/api/database/options', (req, res) => {
  try {
    const latestFile = getLatestFile()
    
    if (!latestFile) {
      return res.json({ options: {} })
    }

    const workbook = XLSX.readFile(latestFile.path)
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const rawData = XLSX.utils.sheet_to_json(worksheet)
    
    // 提取筛选选项
    const options = {
      链路: [...new Set(rawData.map(d => d.链路).filter(Boolean))].sort(),
      学段: [...new Set(rawData.map(d => d.学段).filter(Boolean))].sort(),
      竞品: [...new Set(rawData.map(d => d.竞品).filter(Boolean))].sort(),
      学科: [...new Set(rawData.map(d => d.学科).filter(Boolean))].sort()
    }

    res.json({ 
      options: options,
      total: rawData.length,
      file: latestFile.name
    })
  } catch (err) {
    console.error('Database options error:', err)
    res.status(500).json({ error: err.message })
  }
})

// 生成竞品日报
app.post('/api/generate-report', async (req, res) => {
  try {
    const { date } = req.body
    
    if (!date) {
      return res.status(400).json({ error: '请提供日期参数' })
    }
    
    // 验证日期格式
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(date)) {
      return res.status(400).json({ error: '日期格式错误，请使用 YYYY-MM-DD 格式' })
    }
    
    // 检查数据文件是否存在
    const latestFile = getLatestFile()
    if (!latestFile) {
      return res.status(400).json({ error: '没有找到数据文件，请先上传数据' })
    }
    
    console.log(`开始生成报告: ${date}`)
    
    // 执行Python脚本生成报告
    const scriptPath = path.join(__dirname, '..', 'scripts', 'generate_daily_report.py')
    const { stdout, stderr } = await execAsync(`python3 "${scriptPath}" ${date}`, {
      cwd: path.join(__dirname, '..'),
      timeout: 120000 // 2分钟超时
    })
    
    if (stderr && !stderr.includes('报告生成完成')) {
      console.error('Script stderr:', stderr)
    }
    
    console.log('Script output:', stdout)
    
    // 复制报告到public目录
    const reportPath = path.join(__dirname, '..', 'outputs', 'reports', `report-${date}.json`)
    const publicReportPath = path.join(__dirname, '..', 'public', 'outputs', 'reports', `report-${date}.json`)
    
    if (fs.existsSync(reportPath)) {
      // 确保目标目录存在
      const publicReportsDir = path.dirname(publicReportPath)
      if (!fs.existsSync(publicReportsDir)) {
        fs.mkdirSync(publicReportsDir, { recursive: true })
      }
      fs.copyFileSync(reportPath, publicReportPath)
      
      // 更新索引文件
      await updateReportsIndex(date)
      
      res.json({ 
        success: true,
        message: `成功生成 ${date} 竞品日报`,
        reportId: `report-${date}`
      })
    } else {
      res.status(500).json({ error: '报告生成失败，请检查日志' })
    }
    
  } catch (err) {
    console.error('Generate report error:', err)
    res.status(500).json({ error: err.message || '生成报告时出错' })
  }
})

// 更新报告索引
async function updateReportsIndex(newDate) {
  const indexPath = path.join(__dirname, '..', 'public', 'outputs', 'reports', 'reports-index.json')
  const outputIndexPath = path.join(__dirname, '..', 'outputs', 'reports', 'reports-index.json')
  
  let indexData = { reports: [] }
  
  // 读取现有索引
  if (fs.existsSync(indexPath)) {
    const content = fs.readFileSync(indexPath, 'utf-8')
    indexData = JSON.parse(content)
  }
  
  // 检查是否已存在该日期的报告
  const existingIndex = indexData.reports.findIndex(r => r.id === `report-${newDate}`)
  
  const newReport = {
    id: `report-${newDate}`,
    title: `${newDate}竞品日报`,
    filename: `report-${newDate}.json`,
    created_at: `${newDate}T23:59:59.000000`,
    summary_preview: `截止${newDate}的竞品销量分析报告...`,
    stats: {
      total_conclusions: 4,
      high_importance: 4,
      source_files: 1
    }
  }
  
  if (existingIndex >= 0) {
    indexData.reports[existingIndex] = newReport
  } else {
    // 按日期排序插入
    indexData.reports.push(newReport)
    indexData.reports.sort((a, b) => {
      const dateA = a.id.replace('report-', '').replace('report-daily-sales', '2025-12-31')
      const dateB = b.id.replace('report-', '').replace('report-daily-sales', '2025-12-31')
      return dateA.localeCompare(dateB)
    })
  }
  
  // 保存索引
  fs.writeFileSync(indexPath, JSON.stringify(indexData, null, 2))
  fs.writeFileSync(outputIndexPath, JSON.stringify(indexData, null, 2))
}

app.post('/api/crawler/run', async (req, res) => {
  try {
    const { start_date, end_date, cookie } = req.body
    
    if (!start_date) {
      return res.status(400).json({ success: false, message: '请提供开始日期' })
    }
    
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(start_date)) {
      return res.status(400).json({ success: false, message: '日期格式错误，请使用 YYYY-MM-DD 格式' })
    }
    
    console.log(`开始爬取数据: ${start_date} ~ ${end_date || start_date}`)
    
    const scriptPath = path.join(__dirname, '..', 'scripts', 'crawler.py')
    
    let command
    if (cookie) {
      const cookieFile = path.join(__dirname, '..', 'cookie.txt')
      fs.writeFileSync(cookieFile, cookie, 'utf-8')
      command = end_date 
        ? `python3 "${scriptPath}" ${start_date} ${end_date}`
        : `python3 "${scriptPath}" ${start_date}`
    } else {
      command = end_date 
        ? `python3 "${scriptPath}" ${start_date} ${end_date}`
        : `python3 "${scriptPath}" ${start_date}`
    }
    
    const { stdout, stderr } = await execAsync(command, {
      cwd: path.join(__dirname, '..'),
      timeout: 600000
    })
    
    console.log('Crawler output:', stdout)
    if (stderr) {
      console.error('Crawler stderr:', stderr)
    }
    
    try {
      const lastLine = stdout.trim().split('\n').pop()
      const result = JSON.parse(lastLine)
      res.json(result)
    } catch (parseErr) {
      res.json({
        success: true,
        message: '爬取完成',
        filepath: '',
        count: 0,
        date: start_date
      })
    }
    
  } catch (err) {
    console.error('Crawler error:', err)
    res.status(500).json({ success: false, message: err.message || '爬取失败' })
  }
})

app.listen(PORT, () => {
  console.log(`Data upload server running on port ${PORT}`)
})
