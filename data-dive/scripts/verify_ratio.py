import json

with open('/Users/jasper./TRAE/data-dive/outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

for c in d['conclusions']:
    if c['chart_type'] == 'complex_table':
        print('=== ' + c['title'] + ' ===')
        print()
        print('前5条数据:')
        for i, row in enumerate(c['chart_data']['data'][:5]):
            seg = row['学段']
            brand = row['竞品']
            sales = row['昨日销量']
            ratio1 = row['昨日销量占比']
            ratio3 = row['3日日均占比']
            print(f'{i+1}. 学段: {seg}, 竞品: {brand}, 昨日销量: {sales}, 昨日占比: {ratio1}, 3日占比: {ratio3}')
        print()
