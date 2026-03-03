import json

with open('outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

print('=== 中价链路学段数据 ===')
for seg, data in d.get('daily_summary', {}).get('中价', {}).get('segments', {}).items():
    print(f'{seg}:')
    print(f'  趋势: {data.get("trend")}')
    print(f'  环比: {data.get("mom_change")}%')
    print(f'  30日日均: {data.get("avg_30d")}')
    print(f'  7日日均: {data.get("avg_7d")}')
    print(f'  3日日均: {data.get("avg_3d")}')
    print()

print('=== 低价链路学段数据 ===')
for seg, data in d.get('daily_summary', {}).get('低价', {}).get('segments', {}).items():
    print(f'{seg}:')
    print(f'  趋势: {data.get("trend")}')
    print(f'  环比: {data.get("mom_change")}%')
    print(f'  30日日均: {data.get("avg_30d")}')
    print(f'  7日日均: {data.get("avg_7d")}')
    print(f'  3日日均: {data.get("avg_3d")}')
    print()
