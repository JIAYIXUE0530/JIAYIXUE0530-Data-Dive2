import json

with open('outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

print('=== 整体洞察（全年销量分析）===')
print()
for i, insight in enumerate(d.get('overall_insights', [])[:6]):
    print(f"{i+1}. [{insight['icon']}] {insight['title']}")
    print(f"   {insight['content'][:100]}...")
    print()

print()
print('=== SPU日报洞察示例 ===')
for c in d['conclusions']:
    if c['chart_type'] == 'complex_table':
        print()
        print('--- ' + c['title'] + ' ---')
        for i, insight in enumerate(c.get('insights', [])[:2]):
            print(f"  {i+1}. [{insight['icon']}] {insight['title']}")
