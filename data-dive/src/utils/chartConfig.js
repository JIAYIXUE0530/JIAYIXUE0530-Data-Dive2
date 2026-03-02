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