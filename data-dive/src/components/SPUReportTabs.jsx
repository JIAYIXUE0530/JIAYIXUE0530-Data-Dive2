import { useState } from 'react'
import ChartContainer from './ChartContainer'

function SPUReportTabs({ reports, dailySummary }) {
  const [activeTab, setActiveTab] = useState(0)
  const [showInsights, setShowInsights] = useState({})
  const currentReport = reports[activeTab]
  
  if (!reports || reports.length === 0) return null
  
  // 切换洞察显示
  const toggleInsights = (reportId) => {
    setShowInsights(prev => ({
      ...prev,
      [reportId]: !prev[reportId]
    }))
  }
  
  // 渲染总体结论
  const renderDailySummary = () => {
    if (!dailySummary) return null
    
    const channels = [
      { key: '中价', title: '近期抖音场中价重点关注', icon: '📈' },
      { key: '低价', title: '近期抖音场低价重点关注', icon: '📉' }
    ]
    
    // 大盘数据
    const marketData = dailySummary['大盘']
    
    return (
      <div className="mb-6 p-6 bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)]">
        <h3 className="font-display text-lg font-bold text-[var(--text-primary)] mb-4">📊 当日数据总体结论</h3>
        
        {/* 大盘情况 */}
        {marketData && (
          <div className="mb-6 p-4 bg-[var(--accent-forest)]/5 rounded-lg border border-[var(--accent-forest)]/20">
            <h4 className="text-sm font-semibold text-[var(--accent-forest)] mb-3">🌐 大盘情况</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-[var(--text-tertiary)]">昨日总销量</p>
                <p className="text-lg font-bold text-[var(--text-primary)]">{marketData.yesterday_total?.toLocaleString()} <span className="text-xs font-normal text-[var(--text-tertiary)]">单</span></p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-tertiary)]">环比变化</p>
                <p className={`text-lg font-bold ${marketData.mom_change >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                  {marketData.mom_change >= 0 ? '+' : ''}{marketData.mom_change}%
                </p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-tertiary)]">3日日均</p>
                <p className="text-lg font-bold text-[var(--text-primary)]">{marketData.avg_3d?.toLocaleString()} <span className="text-xs font-normal text-[var(--text-tertiary)]">单</span></p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-tertiary)]">7日日均</p>
                <p className="text-lg font-bold text-[var(--text-primary)]">{marketData.avg_7d?.toLocaleString()} <span className="text-xs font-normal text-[var(--text-tertiary)]">单</span></p>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-[var(--border-subtle)] flex flex-wrap gap-4 text-sm">
              {marketData.top_brand && (
                <span>
                  <span className="text-[var(--text-tertiary)]">TOP品牌：</span>
                  <span className="font-medium text-[var(--text-primary)]">{marketData.top_brand}</span>
                  <span className="text-[var(--text-muted)]">（{marketData.top_brand_sales?.toLocaleString()}单）</span>
                </span>
              )}
              {marketData.top_channel && (
                <span>
                  <span className="text-[var(--text-tertiary)]">TOP链路：</span>
                  <span className="font-medium text-[var(--text-primary)]">{marketData.top_channel}</span>
                  <span className="text-[var(--text-muted)]">（{marketData.top_channel_sales?.toLocaleString()}单）</span>
                </span>
              )}
              {marketData.top_segment && (
                <span>
                  <span className="text-[var(--text-tertiary)]">TOP学段：</span>
                  <span className="font-medium text-[var(--text-primary)]">{marketData.top_segment}</span>
                  <span className="text-[var(--text-muted)]">（{marketData.top_segment_sales?.toLocaleString()}单）</span>
                </span>
              )}
            </div>
          </div>
        )}
        
        {/* 中低价并列展示 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {channels.map(({ key, title, icon }) => {
            const channelData = dailySummary[key]
            if (!channelData || !channelData.segments) return null
            
            const segments = Object.entries(channelData.segments)
            if (segments.length === 0) return null
            
            // 计算整体结论
            const totalSales = segments.reduce((sum, [, data]) => sum + (data.yesterday_total || 0), 0)
            const topBrandOverall = segments.reduce((max, [, data]) => 
              (data.top_brand_sales > (max.sales || 0) ? { brand: data.top_brand, sales: data.top_brand_sales } : max), 
              { brand: '', sales: 0 }
            )
            
            return (
              <div key={key} className="border border-[var(--border-subtle)] rounded-lg overflow-hidden">
                {/* 标题栏 */}
                <div className="px-4 py-3 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]">
                  <h4 className="text-sm font-semibold text-[var(--accent-forest)]">
                    {icon} {title}
                  </h4>
                </div>
                
                {/* 链路大盘整体情况 - 文字叙述 */}
                {channelData.overview && (
                  <div className="px-4 py-2 bg-[var(--accent-forest)]/5 border-b border-[var(--border-subtle)]">
                    <p className="text-sm text-[var(--text-primary)]">
                      昨日销量 <span className="font-semibold text-[var(--accent-forest)]">{channelData.overview.yesterday_total?.toLocaleString()}</span> 单，
                      环比 <span className={channelData.overview.mom_change >= 0 ? 'text-green-600 font-medium' : 'text-red-500 font-medium'}>{channelData.overview.mom_change >= 0 ? '+' : ''}{channelData.overview.mom_change}%</span>，
                      3日日均 {channelData.overview.avg_3d?.toLocaleString()} 单，
                      {channelData.overview.top_brand && (
                        <>{channelData.overview.top_brand} 领跑（{channelData.overview.top_brand_sales?.toLocaleString()}单）</>
                      )}
                      {channelData.overview.top_segment && (
                        <>，{channelData.overview.top_segment}学段TOP（{channelData.overview.top_segment_sales?.toLocaleString()}单）</>
                      )}
                    </p>
                  </div>
                )}
                
                {/* 学段详情 */}
                <div className="p-4 space-y-3">
                  {segments.map(([segment, data]) => {
                    if (!data) return null
                    
                    const brandRanking = data.brand_ranking || []
                    const rankingText = brandRanking.slice(0, 3).map(([brand, sales]) => `${brand}（${sales}单）`).join(' > ')
                    
                    return (
                      <div key={segment} className="p-3 bg-[var(--bg-secondary)]/30 rounded-lg">
                        <div className="flex items-start gap-2">
                          <span className="text-sm font-medium text-[var(--text-primary)] min-w-[50px]">{segment}：</span>
                          <div className="flex-1 text-sm text-[var(--text-secondary)]">
                            {data.top_brand && (
                              <p>
                                <span className="font-medium text-[var(--text-primary)]">{data.top_brand}</span>
                                <span className="text-[var(--text-tertiary)]">（TOP 1）</span>：昨日 {data.top_brand_sales} 单
                                {data.top_product && (
                                  <span className="text-[var(--text-tertiary)]">，爆品 {data.top_product}（{data.top_product_sales}单）</span>
                                )}
                              </p>
                            )}
                            {rankingText && (
                              <p className="text-xs text-[var(--text-muted)] mt-1">竞品：{rankingText}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }
  
  return (
    <section className="mb-6">
      <div className="flex items-center gap-4 mb-4">
        <span className="text-[11px] font-bold text-[var(--accent-terracotta)] uppercase tracking-[0.2em]">SPU日报</span>
        <div className="flex-1 h-px bg-gradient-to-r from-[var(--accent-terracotta)]/30 to-transparent" />
      </div>
      <h2 className="font-display text-2xl lg:text-3xl font-bold text-[var(--text-primary)] mb-6">商品级别日报</h2>
      
      {/* 总体结论 */}
      {renderDailySummary()}
      
      {/* Excel风格的标签页 */}
      <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] shadow-editorial overflow-hidden">
        {/* 标签栏 */}
        <div className="flex border-b border-[var(--border-subtle)] bg-[var(--bg-secondary)]/50">
          {reports.map((report, index) => {
            const shortName = report.title
              .replace('SPU日报 - ', '')
              .replace('链路', '·')
              .replace('（', '')
              .replace('）', '')
            
            return (
              <button
                key={report.id}
                onClick={() => setActiveTab(index)}
                className={`px-4 py-3 text-sm font-medium transition-all relative ${
                  activeTab === index
                    ? 'text-[var(--text-primary)] bg-[var(--bg-card)]'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]/30'
                }`}
              >
                {shortName}
                {activeTab === index && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--accent-forest)]" />
                )}
              </button>
            )
          })}
        </div>
        
        {/* 内容区域 */}
        {currentReport && (
          <div>
            {/* 核心洞察区域 - 可展开/收起 */}
            {currentReport.insights && currentReport.insights.length > 0 && (
              <div className="border-b border-[var(--border-subtle)]">
                {/* 展开按钮 */}
                <button
                  onClick={() => toggleInsights(currentReport.id)}
                  className="w-full px-4 py-3 flex items-center justify-between bg-[var(--bg-secondary)]/30 hover:bg-[var(--bg-secondary)]/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-[var(--accent-forest)]">💡 核心洞察</span>
                    <span className="text-xs text-[var(--text-muted)]">（{currentReport.insights.length}条）</span>
                  </div>
                  <svg 
                    className={`w-5 h-5 text-[var(--text-tertiary)] transition-transform ${showInsights[currentReport.id] ? 'rotate-180' : ''}`} 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {/* 洞察内容 - 默认隐藏 */}
                {showInsights[currentReport.id] && (
                  <div className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {currentReport.insights.map((insight, idx) => (
                        <div key={idx} className={`p-3 rounded-lg border ${
                          insight.priority === 'high' 
                            ? 'bg-[var(--accent-terracotta)]/5 border-[var(--accent-terracotta)]/20' 
                            : insight.priority === 'medium'
                            ? 'bg-[var(--accent-gold)]/5 border-[var(--accent-gold)]/20'
                            : 'bg-[var(--bg-card)] border-[var(--border-subtle)]'
                        }`}>
                          <div className="flex items-start gap-2">
                            <span className="text-base">{insight.icon}</span>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-0.5">
                                <span className="text-xs text-[var(--text-tertiary)]">{insight.type}</span>
                                {insight.priority === 'high' && (
                                  <span className="text-xs px-1 py-0.5 bg-[var(--accent-terracotta)]/10 text-[var(--accent-terracotta)] rounded">重要</span>
                                )}
                              </div>
                              <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-0.5">{insight.title}</h4>
                              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{insight.content}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* 表格区域 */}
            <div className="p-4">
              <ChartContainer type={currentReport.chart_type} data={currentReport.chart_data} />
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default SPUReportTabs
