#!/usr/bin/env python3
import json
from datetime import datetime

# 读取现有索引
with open('outputs/reports/reports-index.json', 'r', encoding='utf-8') as f:
    index_data = json.load(f)

# 添加新报告
new_report = {
    "id": "report-daily-sales",
    "title": "销售日报 - 竞品销量分析",
    "filename": "report-daily-sales.json",
    "created_at": datetime.now().isoformat(),
    "summary_preview": "基于数据分析，总销量达16,625,854件，环比变化-2.8%。包含9张趋势图表和商品颗粒度数据表格...",
    "stats": {
        "total_conclusions": 10,
        "high_importance": 0,
        "source_files": 1
    }
}

# 检查是否已存在
existing_ids = [r['id'] for r in index_data['reports']]
if new_report['id'] not in existing_ids:
    index_data['reports'].insert(0, new_report)
    print("Added new report to index")
else:
    for i, r in enumerate(index_data['reports']):
        if r['id'] == new_report['id']:
            index_data['reports'][i] = new_report
            print("Updated existing report in index")
            break

# 保存索引
with open('outputs/reports/reports-index.json', 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"Total reports: {len(index_data['reports'])}")
