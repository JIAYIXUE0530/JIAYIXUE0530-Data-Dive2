import json

with open('outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

print('=== 大盘情况 ===')
market = d.get('daily_summary', {}).get('大盘', {})
print(f'昨日总销量: {market.get("yesterday_total")} 单')
print(f'环比变化: {market.get("mom_change")}%')
print(f'3日日均: {market.get("avg_3d")} 单')
print(f'7日日均: {market.get("avg_7d")} 单')
print(f'TOP品牌: {market.get("top_brand")} ({market.get("top_brand_sales")}单)')
print(f'TOP链路: {market.get("top_channel")} ({market.get("top_channel_sales")}单)')
print(f'TOP学段: {market.get("top_segment")} ({market.get("top_segment_sales")}单)')
print(f'品牌排名: {market.get("brand_ranking")}')
