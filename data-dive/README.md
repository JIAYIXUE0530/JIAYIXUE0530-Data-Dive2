# Data Dive - 竞品销量数据分析平台

## 项目概述

Data Dive 是一个竞品销量数据分析平台，支持数据爬取、日报生成、数据录入、销量趋势分析和竞品数据库查询功能。

## 技术栈

- **前端**: React + Vite + Tailwind CSS + Recharts
- **后端**: Node.js + Express
- **数据处理**: Python + Pandas
- **爬虫**: Python + Requests + AES解密
- **部署**: Vercel (静态) / 本地运行 (完整功能)

## 项目结构

```
data-dive/
├── src/                    # 前端源码
│   ├── components/         # React 组件
│   ├── pages/              # 页面组件
│   └── utils/              # 工具函数
├── server/                 # 后端服务
│   └── upload-server.js    # Express 服务器
├── scripts/                # Python 脚本
│   ├── generate_daily_report.py  # 日报生成模板
│   └── crawler.py          # 蝉妈妈数据爬虫
├── public/                 # 静态资源
│   ├── data/               # 竞品数据库 JSON
│   └── outputs/reports/    # 报告文件
├── uploads/                # 上传的数据文件
└── outputs/reports/        # 生成的报告
```

## 功能模块

### 1. 首页 (Dashboard)
- 五个导航卡片：日报、数据爬取、每日数据录入、全年销量数据、竞品数据库
- 页眉页脚两边对齐布局

### 2. 日报存档 (Reports)
- 查看所有已生成的竞品日报
- 支持输入日期生成新日报（需本地运行后端）
- 报告按日期倒序排列

### 3. 数据爬取 (Crawler)
- 从蝉妈妈平台自动爬取竞品销量数据
- 支持指定日期范围爬取
- 一键爬取昨日数据
- 覆盖31个竞品店铺（作业帮、猿辅导、高途、希望学、豆神、叫叫、有道、新东方、斑马等）
- 定时任务功能（开发中）

### 4. 每日数据录入 (DataEntry)
- 上传 Excel 数据文件
- 支持 .xlsx 和 .xls 格式
- 自动归档旧文件

### 5. 全年销量数据 (SalesData)
- KPI 卡片：累计销量、TOP品牌、7日日均销量
- 支持按链路和学段筛选
- 品牌月度销量趋势图表

### 6. 竞品数据库 (CompetitorDatabase)
- 查询所有竞品销量数据
- 支持多维度筛选：链路、学段、竞品、学科
- 分页显示，每页100条

### 7. 独立日报页面 (Report)
- SPU 商品级别日报
- 三个标签页：低价链路、中价链路、正价链路
- 支持导出 PDF

## 数据爬取功能

### 爬虫原理
1. **数据来源**: 蝉妈妈 - 抖音电商数据分析平台
2. **认证流程**: 登录 → 获取token → 设置cookie → 调用API
3. **数据解密**: AES ECB模式解密 + Gzip解压
4. **采集流程**: 遍历店铺 → 调用API → 解密数据 → 存储MySQL
5. **自动去重**: MySQL PRIMARY KEY (`quchong`字段) 自动去重

### 数据库存储
爬取的数据自动存储到MySQL数据库 `zb_zhoubo` 表：

| 字段 | 类型 | 说明 |
|------|------|------|
| quchong | VARCHAR(100) | 主键，去重字段 (日期+商品ID) |
| date | DATE | 销售日期 |
| brand | VARCHAR(50) | 竞品品牌 |
| shop | VARCHAR(100) | 店铺名称 |
| product_id | VARCHAR(50) | 商品ID |
| product_name | VARCHAR(255) | 商品名称 |
| price | DECIMAL(10,2) | 价格 |
| volume | INT | 销量 |
| volume_30d | INT | 30天销量 |
| gmv | DECIMAL(15,2) | 销售额 |
| link_type | VARCHAR(20) | 链路类型 |
| grade | VARCHAR(20) | 学段 |
| subject | VARCHAR(20) | 学科 |

### 竞品店铺列表
共覆盖 **681个店铺**，涵盖以下品牌：

| 品牌 | 店铺数量 |
|------|---------|
| 作业帮 | 120+ |
| 猿辅导 | 80+ |
| 高途 | 60+ |
| 希望学 | 50+ |
| 豆神 | 40+ |
| 叫叫 | 30+ |
| 有道 | 50+ |
| 新东方 | 60+ |
| 其他竞品 | 180+ |

### 运行爬虫
```bash
# 命令行方式 - 爬取指定日期
python3 scripts/crawler.py YYYY-MM-DD

# 爬取昨日数据
python3 scripts/crawler.py

# 网页方式
访问 http://localhost:5173/crawler
```

### 爬取结果示例
```
2026-03-04 爬取结果:
- 店铺数: 681
- 商品数: 839
- 入库数: 822 (自动去重后)
```

## 日报生成逻辑

### 关键计算规则

1. **锚点日期**: 用户输入的日期作为基准
2. **昨日销量**: 锚点日期 - 1 天
3. **周计算**: 使用日历周（周一到周日）
   - T周 = 锚点日期所在周的上一周
   - T-1周 = T周的上一周
   - 以此类推
4. **日均计算**: 销量小于5的天不计入销售日
5. **月计算**: 自然月

### 排序规则

**学段排序**:
```
小学 → 初中 → 高中 → 低幼
```

**品牌排序**:
```
作业帮 → 猿辅导 → 高途 → 希望学 → 豆神 → 叫叫 → 其他竞品 → IP（最后）
```

### 表格结构

| 列名 | 说明 |
|------|------|
| 竞品 | 品牌名称 |
| 学段 | 小学/初中/高中/低幼 |
| 学科 | 语文/数学/英语等 |
| 商品 | SPU名称 |
| 价格 | 商品价格 |
| 昨日销量 | 锚点日期-1天的销量 |
| 3日日均 | 近3天有效销售日平均 |
| 7日日均 | 近7天有效销售日平均 |
| 30日日均 | 近30天有效销售日平均 |
| T周销量 | 上一完整自然周销量 |
| T-1周销量 | 上上周销量 |
| ... | 以此类推 |
| T周环比 | T周 vs T-1周变化 |
| 月销量 | 当月累计销量 |
| 月环比 | 本月 vs 上月变化 |

## 数据文件格式

### Excel 文件要求

必需列名：
- 竞品
- 学段
- 链路（低价/中价/正价）
- 学科
- ID
- 商品
- 价格
- 销售日期
- 销量

### 示例数据

| 竞品 | 学段 | 链路 | 学科 | ID | 商品 | 价格 | 销售日期 | 销量 |
|------|------|------|------|-----|------|------|----------|------|
| 作业帮 | 小学 | 中价 | 语文 | A0001 | 作业帮大阅读 | 299 | 2025-01-01 | 100 |

## 运行指南

### 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器（前端 + 后端）
npm run start

# 或分别启动
npm run dev      # 前端 (端口 5173)
npm run server   # 后端 (端口 3001)
```

### 生成日报

```bash
# 命令行方式
python3 scripts/generate_daily_report.py YYYY-MM-DD

# 示例
python3 scripts/generate_daily_report.py 2025-10-31
python3 scripts/generate_daily_report.py 2026-02-09
```

### 构建生产版本

```bash
npm run build
```

## 部署说明

### Vercel 部署（静态）

1. 推送代码到 GitHub
2. 在 Vercel 导入项目
3. 自动检测 Vite 框架
4. 部署完成

**注意事项**:
- 竞品数据库使用静态 JSON 文件
- 数据录入和日报生成功能不可用（需要后端）
- 更新数据需重新导出 JSON 并推送

### 导出竞品数据库

```bash
cd /Users/jasper./TRAE_data_dive/data-dive
python3 -c "
import pandas as pd
import json

df = pd.read_excel('uploads/你的数据文件.xlsx')
data = df.to_dict(orient='records')

for row in data:
    for key, value in row.items():
        if pd.isna(value):
            row[key] = None
        elif hasattr(value, 'isoformat'):
            row[key] = value.isoformat()

with open('public/data/database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print(f'已导出 {len(data)} 条记录')
"
```

### 完整功能部署

如需完整功能（数据录入、日报生成），建议使用：
- **Railway**: 支持 Node.js 后端
- **Render**: 免费 Node.js 托管
- **自建服务器**: Docker 部署

## 常见问题

### Q: 日报生成失败？
A: 检查：
1. 数据文件是否存在于 `uploads/` 目录
2. 日期格式是否正确 (YYYY-MM-DD)
3. 日期是否在数据范围内

### Q: 竞品数据库加载失败？
A: 检查：
1. `public/data/database.json` 是否存在
2. 文件是否已推送到 GitHub
3. Vercel 部署是否成功

### Q: 表格排序不对？
A: 确认：
1. 品牌排序：IP 应该在最后
2. 学段排序：小学 → 初中 → 高中 → 低幼

## 更新日志

### 2026-03-06
- 爬虫模块完整实现：681个店铺全覆盖
- 集成MySQL数据库存储，自动去重
- 爬取字段完整：销量、30天销量、价格、GMV、链路、学段、学科等
- 2026-03-04数据爬取成功：839商品，822条入库

### 2025-03-04
- 添加 Vercel 部署配置
- 竞品数据库改为静态 JSON 加载
- 修复日报生成脚本自动选择最新数据文件
- 修复日期格式兼容性问题

### 2025-03-05
- 页眉页脚两边对齐
- 所有页面铺满窗口
- 全年销量数据页面优化 KPI 指标
- 独立日报页面移除导航栏，添加返回按钮
