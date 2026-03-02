import json

with open('outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

print('=== 当日数据总体结论 ===')
print()
summary = d.get('daily_summary', {})
for channel in ['中价', '低价']:
    if channel in summary:
        print(f'【{channel}】')
        for segment, data in summary[channel].get('segments', {}).items():
            print(f'  {segment}:')
            print(f'    TOP品牌: {data.get("top_brand")} ({data.get("top_brand_sales")}单)')
            print(f'    爆品: {data.get("top_product")} ({data.get("top_product_sales")}单)')
            print(f'    竞品排名: {data.get("brand_ranking")[:3]}')
        print()
