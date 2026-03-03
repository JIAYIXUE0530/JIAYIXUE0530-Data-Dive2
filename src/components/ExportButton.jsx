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