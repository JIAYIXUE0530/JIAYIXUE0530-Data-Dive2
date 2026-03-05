# 日报生成工作流程

## 1. 数据准备

### 1.1 数据文件格式
- 文件格式: Excel (.xlsx 或 .xls)
- 存放位置: `uploads/` 目录
- 命名规范: `竞品销量数据_时间戳.xlsx`

### 1.2 必需列名
```
竞品, 学段, 链路, 学科, ID, 商品, 价格, 销售日期, 销量
```

### 1.3 数据规范
- 销售日期: YYYY-MM-DD 格式或 Excel 日期序列号
- 链路: 低价/中价/正价
- 学段: 小学/初中/高中/低幼
- 销量: 整数

## 2. 日报生成流程

### 2.1 命令行生成
```bash
python3 scripts/generate_daily_report.py YYYY-MM-DD
```

### 2.2 网页生成
1. 进入"日报存档"页面
2. 输入日期 (YYYY-MM-DD 格式)
3. 点击"生成竞品日报"按钮
4. 等待生成完成

### 2.3 生成流程
```
1. 加载数据 → 2. 筛选数据 → 3. 计算指标 → 4. 生成表格 → 5. 保存报告
```

## 3. 核心计算逻辑

### 3.1 周计算 (日历周)
```python
def get_week_range(anchor_date):
    # 获取锚点日期所在周的周一
    current_weekday = anchor_date.weekday()  # 0=周一, 6=周日
    current_week_monday = anchor_date - timedelta(days=current_weekday)
    
    # T周 = 上一完整自然周
    t_week_end = current_week_monday - timedelta(days=1)      # 上周日
    t_week_start = current_week_monday - timedelta(days=7)    # 上周一
    
    # T-1周 = T周的上一周
    t1_week_end = t_week_start - timedelta(days=1)
    t1_week_start = t_week_start - timedelta(days=7)
    
    # 以此类推 T-2, T-3, T-4...
```

### 3.2 日均计算 (排除低销量日)
```python
SALES_THRESHOLD = 5  # 销量阈值

def calc_daily_avg_with_threshold(df, start_date, end_date):
    # 筛选日期范围
    mask = (df['销售日期'] >= start_date) & (df['销售日期'] <= end_date)
    daily_sales = df[mask].groupby('销售日期')['销量'].sum()
    
    # 排除销量小于阈值的天
    valid_days = daily_sales[daily_sales >= SALES_THRESHOLD]
    
    if len(valid_days) == 0:
        return 0
    
    # 日均 = 总销量 / 有效天数
    return valid_days.sum() / len(valid_days)
```

### 3.3 环比计算
```python
# 周环比
week_change = (t_week_sales - t1_week_sales) / t1_week_sales * 100

# 月环比
mom_change = (this_month_sales - last_month_sales) / last_month_sales * 100
```

## 4. 排序规则

### 4.1 学段排序
```python
SEGMENT_ORDER = {'小学': 0, '初中': 1, '高中': 2, '低幼': 3}
```

### 4.2 品牌排序
```python
BRAND_ORDER = {
    '作业帮': 0, 
    '猿辅导': 1, 
    '高途': 2, 
    '希望学': 3, 
    '豆神': 4, 
    '叫叫': 5, 
    'IP': 999  # IP 始终在最后
}

# 其他未列出的品牌排在已知品牌之后、IP之前
def get_brand_order(brand):
    return BRAND_ORDER.get(brand, 100)
```

## 5. 报告结构

### 5.1 JSON 结构
```json
{
  "meta": {
    "title": "YYYY-MM-DD竞品日报",
    "generated_at": "生成时间",
    "anchor_date": "锚点日期"
  },
  "kpi": {
    "total_sales": 累计销量,
    "mom_change": 环比变化,
    "top_brands": ["TOP1品牌", "TOP2品牌", "TOP3品牌"]
  },
  "daily_summary": {
    "大盘": { 大盘汇总数据 },
    "低价": { 低价链路数据 },
    "中价": { 中价链路数据 }
  },
  "conclusions": [
    {
      "chart_type": "complex_table",
      "chart_data": { 表格数据 }
    }
  ]
}
```

### 5.2 表格数据结构
```json
{
  "columns": ["竞品", "学段", "学科", "商品", "价格", "昨日销量", ...],
  "header_groups": [
    {"name": "基本信息", "colspan": 5},
    {"name": "销量数据", "colspan": 8},
    {"name": "环比数据", "colspan": 2}
  ],
  "data": [
    {"竞品": "作业帮", "学段": "小学", ...}
  ]
}
```

## 6. 前端展示规范

### 6.1 表格样式
- 表头颜色: 莫兰迪蓝色系
  - 第一行: `#7ba3c9`
  - 第二行: `#9ec5e8`
  - 第三行(总计): `#d6e9f7`
- 冻结前三行 (表头组 + 列名 + 总计)
- 所有数字显示整数

### 6.2 筛选器
- 学段顺序: 全部 → 小学 → 初中 → 高中 → 低幼
- 竞品顺序: 全部 → 作业帮 → 猿辅导 → 高途 → 希望学 → 豆神 → 叫叫 → 其他 → IP

### 6.3 总计行
- 动态计算筛选后数据的总计
- 销量总计 = SUM(销量)
- 占比总计 = 100%

## 7. 部署与更新

### 7.1 本地运行
```bash
npm run start  # 同时启动前端和后端
```

### 7.2 Vercel 部署
```bash
git add -A
git commit -m "Update data"
git push origin main
```

### 7.3 更新竞品数据库
```bash
# 导出数据到 JSON
python3 -c "
import pandas as pd
import json

df = pd.read_excel('uploads/最新数据文件.xlsx')
data = df.to_dict(orient='records')

for row in data:
    for key, value in row.items():
        if pd.isna(value):
            row[key] = None
        elif hasattr(value, 'isoformat'):
            row[key] = value.isoformat()

with open('public/data/database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
"

# 提交推送
git add public/data/database.json
git commit -m "Update competitor database"
git push origin main
```

## 8. 常见问题排查

### 8.1 日报生成失败
- 检查数据文件是否存在
- 检查日期格式是否正确
- 检查日期是否在数据范围内
- 查看后端日志错误信息

### 8.2 数据显示异常
- 检查 JSON 文件格式
- 检查列名是否匹配
- 检查数据类型是否正确

### 8.3 排序不正确
- 检查 BRAND_ORDER 和 SEGMENT_ORDER 配置
- 检查前端筛选器排序逻辑
- 检查后端数据排序逻辑
