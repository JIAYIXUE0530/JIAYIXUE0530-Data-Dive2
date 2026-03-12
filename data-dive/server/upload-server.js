import express from 'express'
import multer from 'multer'
import path from 'path'
import fs from 'fs'
import XLSX from 'xlsx'
import { fileURLToPath } from 'url'
import { exec, spawn } from 'child_process'
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

// Job 存储（内存中）
const crawlerJobs = new Map()

// 获取最新打标结果文件
function getTaggedFile() {
  const files = fs.readdirSync(DATA_DIR)
    .filter(f => f.includes('_匹配打标结果') && (f.endsWith('.xlsx') || f.endsWith('.xls')))
    .map(f => ({
      name: f,
      path: path.join(DATA_DIR, f),
      time: fs.statSync(path.join(DATA_DIR, f)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time)
  return files.length > 0 ? files[0] : null
}

const CHANGELOG_DIR = path.join(__dirname, '..', 'changelog')
if (!fs.existsSync(CHANGELOG_DIR)) fs.mkdirSync(CHANGELOG_DIR, { recursive: true })

function readChangelog() {
  const p = path.join(CHANGELOG_DIR, 'history.json')
  if (!fs.existsSync(p)) return []
  return JSON.parse(fs.readFileSync(p, 'utf-8'))
}

function writeChangelog(data) {
  fs.writeFileSync(path.join(CHANGELOG_DIR, 'history.json'), JSON.stringify(data, null, 2))
}

app.post('/api/crawler/start', (req, res) => {
  const { start_date, end_date, cookie } = req.body
  if (!start_date) return res.status(400).json({ error: '请提供开始日期' })
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(start_date)) return res.status(400).json({ error: '日期格式错误' })

  const jobId = Date.now().toString()
  crawlerJobs.set(jobId, { params: { start_date, end_date, cookie }, status: 'pending' })
  res.json({ success: true, jobId })
})

app.get('/api/crawler/stream/:jobId', async (req, res) => {
  const job = crawlerJobs.get(req.params.jobId)
  if (!job) return res.status(404).end()

  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  res.flushHeaders()

  const send = (data) => res.write(`data: ${JSON.stringify(data)}\n\n`)

  const { start_date, end_date, cookie } = job.params
  if (cookie) {
    fs.writeFileSync(path.join(__dirname, '..', 'cookie.txt'), cookie, 'utf-8')
  }

  // Stage 1: 爬虫
  send({ type: 'stage', stage: 'crawling', message: '▶ 开始爬取数据...' })

  const crawlerScript = path.join(__dirname, '..', 'scripts', 'crawler.py')
  const crawlerArgs = [crawlerScript, start_date]
  if (end_date && end_date !== start_date) crawlerArgs.push(end_date)

  // 记录爬取前的文件时间戳，用于之后判断是否产生了新文件
  const beforeCrawlTime = Date.now()

  let crawlerFilepath = null  // 从爬虫输出的 JSON 中解析
  let crawlerResult = null    // 爬虫最终 JSON 结果

  await new Promise((resolve) => {
    const proc = spawn('python3', crawlerArgs, { cwd: path.join(__dirname, '..') })
    proc.stdout.on('data', d => {
      d.toString().split('\n').filter(l => l.trim()).forEach(l => {
        // 尝试解析 JSON 结果行（爬虫最后输出 filepath / success / message）
        if (l.trim().startsWith('{')) {
          try {
            const parsed = JSON.parse(l)
            if ('success' in parsed) {
              crawlerResult = parsed
              if (parsed.filepath) crawlerFilepath = parsed.filepath
              // 把爬虫结果摘要打印到日志
              if (!parsed.success) {
                send({ type: 'log', message: `❌ 爬虫报告: ${parsed.message || '未知错误'}` })
              } else {
                send({ type: 'log', message: `✓ 爬虫完成: ${parsed.message || ''} (${parsed.count || 0} 条)` })
              }
            }
          } catch {}
          return // 不把原始 JSON 发到日志
        }
        send({ type: 'log', message: l })
      })
    })
    proc.stderr.on('data', d => d.toString().split('\n').filter(l => l.trim()).forEach(l => send({ type: 'log', message: l })))
    proc.on('close', resolve)
  })

  // 如果爬虫明确报告失败，直接返回具体错误
  if (crawlerResult && !crawlerResult.success) {
    send({ type: 'error', message: crawlerResult.message || '爬取失败，请检查Cookie是否有效' })
    return res.end()
  }

  // 尝试从 JSON 输出或新文件中找到爬取结果
  let crawledFile = null
  if (crawlerFilepath && fs.existsSync(crawlerFilepath)) {
    const name = path.basename(crawlerFilepath)
    crawledFile = { name, path: crawlerFilepath }
    send({ type: 'log', message: `✓ 爬虫输出文件: ${name}` })
  } else {
    // 降级：找比爬取前更新的、非打标结果的 xlsx
    const newFile = fs.readdirSync(DATA_DIR)
      .filter(f => (f.endsWith('.xlsx') || f.endsWith('.xls')) && !f.includes('_匹配打标结果') && !f.includes('_打标结果') && !f.includes('_智能打标结果'))
      .map(f => ({ name: f, path: path.join(DATA_DIR, f), time: fs.statSync(path.join(DATA_DIR, f)).mtime.getTime() }))
      .filter(f => f.time > beforeCrawlTime)
      .sort((a, b) => b.time - a.time)[0]
    crawledFile = newFile || null
  }

  if (!crawledFile) {
    send({ type: 'error', message: '爬取完成但未生成数据文件，请检查Cookie是否有效或当日是否有数据' })
    return res.end()
  }

  send({ type: 'stage', stage: 'tagging', message: '▶ 开始数据打标...' })

  const taggerScript = path.join(__dirname, '..', 'scripts', 'tag_with_database_v34.py')
  let taggedFilePath = null

  await new Promise((resolve) => {
    const proc = spawn('python3', [taggerScript, crawledFile.path], { cwd: path.join(__dirname, '..') })
    proc.stdout.on('data', d => {
      d.toString().split('\n').filter(l => l.trim()).forEach(l => {
        send({ type: 'log', message: l })
        if (l.includes('结果已保存到:')) taggedFilePath = l.split('结果已保存到:')[1].trim()
      })
    })
    proc.stderr.on('data', d => d.toString().split('\n').filter(l => l.trim()).forEach(l => send({ type: 'log', message: l })))
    proc.on('close', resolve)
  })

  if (!taggedFilePath) {
    const base = crawledFile.path.replace(/\.xlsx$/, '')
    taggedFilePath = `${base}_匹配打标结果.xlsx`
  }

  job.taggedFilePath = taggedFilePath
  job.status = 'done'

  send({ type: 'done', filepath: taggedFilePath })
  res.end()
})

// 列出所有历史打标结果文件
app.get('/api/review/history', (req, res) => {
  try {
    const files = fs.readdirSync(DATA_DIR)
      .filter(f => f.includes('_匹配打标结果') && (f.endsWith('.xlsx') || f.endsWith('.xls')))
      .map(f => {
        const stat = fs.statSync(path.join(DATA_DIR, f))
        return { name: f, path: path.join(DATA_DIR, f), mtime: stat.mtime.getTime() }
      })
      .sort((a, b) => b.mtime - a.mtime)
    res.json({ files: files.map(f => ({ name: f.name, mtime: f.mtime })) })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

app.get('/api/review/data', (req, res) => {
  try {
    // 支持通过 ?file=xxx 指定历史文件
    const specificFile = req.query.file
    let file
    if (specificFile) {
      const filePath = path.join(DATA_DIR, specificFile)
      if (!fs.existsSync(filePath)) return res.status(404).json({ error: '指定文件不存在' })
      file = { name: specificFile, path: filePath }
    } else {
      file = getTaggedFile()
    }
    if (!file) return res.status(404).json({ error: '没有找到打标结果文件，请先爬取数据' })

    const workbook = XLSX.readFile(file.path)
    const worksheet = workbook.Sheets[workbook.SheetNames[0]]
    const data = sanitizeData(XLSX.utils.sheet_to_json(worksheet))
    res.json({ data, filename: file.name, total: data.length })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

app.post('/api/review/save', async (req, res) => {
  try {
    const { data } = req.body
    if (!data || !Array.isArray(data)) return res.status(400).json({ error: '无效数据' })

    // 读取当前数据库用于changelog对比
    const prevFile = getLatestFile()
    let prevData = []
    if (prevFile && !prevFile.name.includes('_匹配打标结果')) {
      const wb = XLSX.readFile(prevFile.path)
      prevData = sanitizeData(XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]))
    }

    // 保存新数据为主数据库文件
    const ts = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15)
    const newFilename = `竞品销量数据_${ts}.xlsx`
    const newFilePath = path.join(DATA_DIR, newFilename)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), 'Sheet1')
    XLSX.writeFile(wb, newFilePath)

    // 归档旧文件
    if (prevFile && !prevFile.name.includes('_匹配打标结果')) {
      const archivePath = path.join(ARCHIVE_DIR, `${Date.now()}_${prevFile.name}`)
      fs.renameSync(prevFile.path, archivePath)
    }

    // 计算变更
    const prevIds = new Set(prevData.map(r => r['商品ID']).filter(Boolean))
    const newIds = new Set(data.map(r => r['商品ID']).filter(Boolean))
    const added = data.filter(r => r['商品ID'] && !prevIds.has(r['商品ID'])).length
    const removed = prevData.filter(r => r['商品ID'] && !newIds.has(r['商品ID'])).length

    // 写入changelog
    const changelog = readChangelog()
    changelog.unshift({
      id: Date.now(),
      timestamp: new Date().toISOString(),
      filename: newFilename,
      prevFilename: (prevFile && !prevFile.name.includes('_匹配打标结果')) ? prevFile.name : null,
      added,
      removed,
      total: data.length
    })
    writeChangelog(changelog)

    // 更新打标系统：写入 manual_tags.xlsx
    const tagCols = ['低/中/正价', '产品形态一', '产品形态二', '产品形态三', '产品形态四', '学段', '学科', '链路类型']
    const taggedRows = data
      .filter(row => tagCols.some(col => row[col] && row[col] !== ''))
      .map(row => {
        const r = { 商品ID: row['商品ID'] || '', 竞品: row['竞品'] || '', 商品名称: row['商品名称'] || '' }
        tagCols.forEach(col => r[col] = row[col] || '')
        return r
      })

    const taggedDir = path.join(__dirname, '..', '打了标的数据')
    if (!fs.existsSync(taggedDir)) fs.mkdirSync(taggedDir, { recursive: true })
    const manualTagsPath = path.join(taggedDir, 'manual_tags.xlsx')

    // 合并已有manual_tags
    let existingManual = []
    if (fs.existsSync(manualTagsPath)) {
      const mwb = XLSX.readFile(manualTagsPath)
      existingManual = XLSX.utils.sheet_to_json(mwb.Sheets[mwb.SheetNames[0]])
    }
    const existingIds = new Set(existingManual.map(r => r['商品ID']))
    const merged = [
      ...existingManual.map(r => {
        const updated = taggedRows.find(t => t['商品ID'] === r['商品ID'])
        return updated || r
      }),
      ...taggedRows.filter(r => !existingIds.has(r['商品ID']))
    ]
    const mwb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(mwb, XLSX.utils.json_to_sheet(merged), 'Sheet1')
    XLSX.writeFile(mwb, manualTagsPath)

    res.json({ success: true, message: `成功保存 ${data.length} 条记录`, added, removed, total: data.length })
  } catch (err) {
    console.error('Save error:', err)
    res.status(500).json({ error: err.message })
  }
})

app.get('/api/database/changelog', (req, res) => {
  try {
    res.json({ changelog: readChangelog() })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

app.post('/api/database/rollback/:id', (req, res) => {
  try {
    const targetId = parseInt(req.params.id)
    const changelog = readChangelog()
    const entryIdx = changelog.findIndex(e => e.id === targetId)
    if (entryIdx < 0) return res.status(404).json({ error: '找不到该版本' })
    const entry = changelog[entryIdx]

    if (!entry.prevFilename) return res.status(400).json({ error: '该版本没有可回撤的历史' })

    // 在archive中找到上一版本文件
    const archiveFiles = fs.readdirSync(ARCHIVE_DIR)
    const targetArchive = archiveFiles.find(f => f.includes(entry.prevFilename))
    if (!targetArchive) return res.status(404).json({ error: '找不到备份文件' })

    // 归档当前文件
    const currentFile = getLatestFile()
    if (currentFile) {
      fs.renameSync(currentFile.path, path.join(ARCHIVE_DIR, `${Date.now()}_rollback_${currentFile.name}`))
    }

    // 恢复
    fs.copyFileSync(path.join(ARCHIVE_DIR, targetArchive), path.join(DATA_DIR, entry.prevFilename))

    // 更新changelog
    changelog.splice(0, entryIdx + 1)
    changelog.unshift({
      id: Date.now(),
      timestamp: new Date().toISOString(),
      filename: entry.prevFilename,
      prevFilename: null,
      added: 0,
      removed: 0,
      total: 0,
      isRollback: true,
      rollbackTo: entry.timestamp
    })
    writeChangelog(changelog)

    res.json({ success: true, message: `已回撤到 ${entry.timestamp} 的版本` })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

app.listen(PORT, () => {
  console.log(`Data upload server running on port ${PORT}`)
})
