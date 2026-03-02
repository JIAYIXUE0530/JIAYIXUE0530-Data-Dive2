import json

with open('outputs/reports/report-daily-sales.json', 'r') as f:
    d = json.load(f)

for c in d['conclusions']:
    if c['chart_type'] == 'complex_table':
        print('=== ' + c['title'] + ' ===')
        print()
        for i, insight in enumerate(c.get('insights', [])[:4]):
            print(f"{i+1}. [{insight['icon']}] {insight['title']}")
            print(f"   {insight['content'][:80]}...")
            print()
