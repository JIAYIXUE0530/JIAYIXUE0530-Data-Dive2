import { useState, useRef } from 'react'

function DataUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = (selectedFile) => {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      '.xlsx',
      '.xls'
    ]
    
    if (selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls')) {
      setFile(selectedFile)
      setMessage(null)
    } else {
      setMessage({ type: 'error', text: '请上传 Excel 文件 (.xlsx 或 .xls)' })
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setMessage(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (response.ok) {
        setMessage({ type: 'success', text: `数据上传成功！共处理 ${result.records} 条记录` })
        setFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        onUploadSuccess?.()
      } else {
        setMessage({ type: 'error', text: result.error || '上传失败，请重试' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: '网络错误，请检查服务器连接' })
    } finally {
      setUploading(false)
    }
  }

  return (
    <section className="mb-10">
      <div className="flex items-center gap-4 mb-6">
        <span className="text-[11px] font-bold text-[var(--accent-terracotta)] uppercase tracking-[0.2em]">数据管理</span>
        <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-terracotta)]/30 to-transparent" />
      </div>
      <h2 className="font-display text-2xl lg:text-3xl font-bold text-[var(--text-primary)] mb-6">每日数据录入</h2>

      <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] shadow-editorial overflow-hidden">
        <div className="p-6">
          {/* 上传区域 */}
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
              dragActive
                ? 'border-[var(--accent-forest)] bg-[var(--accent-forest)]/5'
                : 'border-[var(--border-medium)] hover:border-[var(--accent-forest)]/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              className="hidden"
              id="file-upload"
            />
            
            <div className="mb-4">
              <svg className="w-12 h-12 mx-auto text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            
            {file ? (
              <div className="mb-4">
                <p className="text-[var(--text-primary)] font-medium">{file.name}</p>
                <p className="text-sm text-[var(--text-tertiary)]">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : (
              <div className="mb-4">
                <p className="text-[var(--text-primary)] font-medium">拖拽文件到此处，或</p>
                <label
                  htmlFor="file-upload"
                  className="text-[var(--accent-forest)] hover:underline cursor-pointer"
                >
                  点击选择文件
                </label>
              </div>
            )}
            
            <p className="text-sm text-[var(--text-muted)]">支持 .xlsx, .xls 格式的 Excel 文件</p>
          </div>

          {/* 消息提示 */}
          {message && (
            <div className={`mt-4 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-800'
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <div className="flex items-center gap-2">
                {message.type === 'success' ? (
                  <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                <span>{message.text}</span>
              </div>
            </div>
          )}

          {/* 上传按钮 */}
          <div className="mt-6 flex justify-end gap-3">
            {file && (
              <button
                onClick={() => {
                  setFile(null)
                  if (fileInputRef.current) {
                    fileInputRef.current.value = ''
                  }
                }}
                className="px-4 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              >
                取消
              </button>
            )}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
                !file || uploading
                  ? 'bg-[var(--bg-tertiary)] text-[var(--text-muted)] cursor-not-allowed'
                  : 'bg-[var(--accent-forest)] text-white hover:bg-[var(--accent-forest)]/90'
              }`}
            >
              {uploading ? (
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  上传中...
                </span>
              ) : (
                '上传数据'
              )}
            </button>
          </div>
        </div>

        {/* 数据说明 */}
        <div className="border-t border-[var(--border-subtle)] p-6 bg-[var(--bg-secondary)]/30">
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">数据格式说明</h3>
          <ul className="text-sm text-[var(--text-secondary)] space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-forest)]">•</span>
              <span>支持标准格式的竞品销量数据 Excel 文件</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-forest)]">•</span>
              <span>必需字段：销售日期、链路、学段、竞品、商品、销量</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-forest)]">•</span>
              <span>可选字段：学科、价格等</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-forest)]">•</span>
              <span>上传后将自动合并到历史数据库，并重新生成报告</span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  )
}

export default DataUpload
