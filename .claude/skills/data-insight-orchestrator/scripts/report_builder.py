#!/usr/bin/env python3
"""报告构建器 - 将分析结论整合为 JSON 格式"""

import json
from pathlib import Path
from datetime import datetime


class ReportBuilder:
    def __init__(self, output_dir='outputs/reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_report(self, title, overall_summary, conclusions, source_files):
        return {
            'meta': {'title': title, 'generated_at': datetime.now().isoformat(), 'version': '1.0'},
            'summary': {
                'overall': overall_summary,
                'total_conclusions': len(conclusions),
                'high_importance_count': len([c for c in conclusions if c.get('importance') == 'high']),
                'source_files': source_files
            },
            'conclusions': conclusions
        }

    def save_report(self, report, filename='report.json'):
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return str(output_path)

    def update_index(self, report, filename):
        index_path = self.output_dir / 'reports-index.json'
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except:
            index = {'reports': []}

        report_id = filename.replace('.json', '')
        # 移除已存在的同名报告
        index['reports'] = [r for r in index['reports'] if r['id'] != report_id]
        # 添加新报告
        index['reports'].insert(0, {
            'id': report_id,
            'title': report['meta']['title'],
            'filename': filename,
            'created_at': report['meta']['generated_at'],
            'summary_preview': report['summary']['overall'][:100] + '...',
            'stats': {
                'total_conclusions': report['summary']['total_conclusions'],
                'high_importance': report['summary']['high_importance_count'],
                'source_files': len(report['summary']['source_files'])
            }
        })

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)


def main():
    builder = ReportBuilder()
    # 示例报告
    conclusions = [
        {
            'id': 1,
            'title': 'Q3 销售额环比下降 23%',
            'description': '第三季度销售额为 850 万元，相比 Q2 下降 23%。',
            'data_support': 'Q2: 1100万 → Q3: 850万',
            'source_files': ['销售数据.xlsx'],
            'importance': 'high',
            'chart_type': 'line',
            'chart_data': {
                'x_labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                'series': {'实际': [980, 1100, 850, None], '目标': [1000, 1000, 1000, 1000]}
            }
        }
    ]
    report = builder.build_report(
        title='示例销售分析报告',
        overall_summary='Q3 销售下滑主要受华东区域影响。',
        conclusions=conclusions,
        source_files=['销售数据.xlsx']
    )
    filename = f"report-{datetime.now().strftime('%Y-%m-%d')}-example.json"
    builder.save_report(report, filename)
    builder.update_index(report, filename)
    print(f"报告已生成: {filename}")


if __name__ == '__main__':
    main()