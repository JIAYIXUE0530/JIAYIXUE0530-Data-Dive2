import express from 'express'
import multer from 'multer'
import path from 'path'
import fs from 'fs'
import XLSX from 'xlsx'
import { fileURLToPath } from 'url'

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

app.listen(PORT, () => {
  console.log(`Data upload server running on port ${PORT}`)
})
