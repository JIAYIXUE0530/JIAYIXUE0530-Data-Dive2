import json

with open('outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

print('=== 中价链路大盘 ===')
overview = d.get('daily_summary', {}).get('中价', {}).get('overview', {})
print(f'昨日销量: {overview.get("yesterday_total")}')
print(f'环比: {overview.get("mom_change")}%')
print(f'3日日均: {overview.get("avg_3d")}')
print(f'7日日均: {overview.get("avg_7d")}')
print(f'TOP品牌: {overview.get("top_brand")} ({overview.get("top_brand_sales")}单)')
print(f'TOP学段: {overview.get("top_segment")} ({overview.get("top_segment_sales")}单)')

print()
print('=== 低价链路大盘 ===')
overview = d.get('daily_summary', {}).get('低价', {}).get('overview', {})
print(f'昨日销量: {overview.get("yesterday_total")}')
print(f'环比: {overview.get("mom_change")}%')
print(f'3日日均: {overview.get("avg_3d")}')
print(f'7日日均: {overview.get("avg_7d")}')
print(f'TOP品牌: {overview.get("top_brand")} ({overview.get("top_brand_sales")}单)')
print(f'TOP学段: {overview.get("top_segment")} ({overview.get("top_segment_sales")}单)')
