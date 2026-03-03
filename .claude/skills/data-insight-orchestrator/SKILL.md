---
name: data-insight-orchestrator
description: |
  数据洞察分析 skill。包含完整的分析流程、方法论和原则库。
  当用户上传数据文件（Excel/PDF/Word/TXT/CSV）并要求分析时自动激活。
---

# Data Insight Orchestrator

## 触发条件

- 用户上传数据文件（.xlsx, .xls, .pdf, .docx, .csv, .txt）
- 用户使用 `/analyze-data` 命令
- 用户表达"分析数据"、"数据洞察"等意图

## 执行流程

Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
文件识别   询问侧重点  数据分析   图表生成   页面构建    交付

### Phase 1: 文件识别
- 支持 attach 文件或 uploads/ 目录
- 格式：xlsx/xls/pdf/docx/csv/txt

### Phase 2: 询问侧重点
1. 核心问题：想回答什么？
2. 关注指标：重点关注哪些？
3. 用途场景：内部汇报/公开发布/决策支持

### Phase 3: 数据分析（核心）

**假设驱动分析**
1. 明确核心问题
2. 构建假设树
3. 用数据验证假设
4. So What 追问（至少3层）

**偏差检验（必须）**
- 辛普森悖论：分组后结论是否仍成立？
- 幸存者偏差：有没有看不到的数据？
- 相关≠因果：是否把相关当因果？

**核心准则**
- 因果推演：区分相关和因果
- 可落地性：结论必须指向行动
- 短期突破 + 中长期复利

### Phase 4: 图表生成
图表数据写入 report.json，由前端 Recharts 渲染

### Phase 5: 页面构建
生成 outputs/reports/report.json，启动 npm run dev

### Phase 6: 交付
采用 SCR 叙事结构（情境-冲突-解决）

## 报告 JSON 格式

```json
{
  "meta": { "title": "报告标题", "generated_at": "ISO时间", "version": "1.0" },
  "summary": { "overall": "摘要", "total_conclusions": 5, "high_importance_count": 2, "source_files": [] },
  "conclusions": [
    {
      "id": 1,
      "title": "结论标题",
      "description": "详细描述",
      "data_support": "数据支撑",
      "importance": "high | medium | low",
      "chart_type": "bar | line | pie | scatter",
      "chart_data": {}
    }
  ]
}
```