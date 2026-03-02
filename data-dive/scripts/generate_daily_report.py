#!/usr/bin/env python3
"""
销售日报生成脚本 - 企业内部日报工作流
生成包含3x3=9张图表、商品颗粒度数据表格、KPI指标、异常预警和行动建议的完整日报
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def generate_daily_report(file_path, output_path=None):
    """生成完整日报"""
    print(f"正在加载数据: {file_path}")
    df = pd.read_excel(file_path)
    print(f"数据加载完成，共{len(df)}条记录")
    
    # 添加月份列
    df['月份'] = df['销售日期'].dt.to_period('M').astype(str)
    all_months = sorted(df['月份'].unique())
    
    # ========== KPI指标 ==========
    print("计算KPI指标...")
    total_sales = df['销量'].sum()
    
    # 环比变化
    monthly_sales = df.groupby('月份')['销量'].sum().sort_index()
    if len(monthly_sales) >= 2:
        mom_change = (monthly_sales.iloc[-1] - monthly_sales.iloc[-2]) / monthly_sales.iloc[-2] * 100
    else:
        mom_change = 0
    
    # TOP品牌
    brand_sales = df.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    top_brands = brand_sales.head(3).index.tolist()
    
    # 平均单价
    df_valid_price = df[df['价格'].notna()]
    if len(df_valid_price) > 0:
        df_valid_price = df_valid_price.copy()
        df_valid_price['价格_num'] = pd.to_numeric(df_valid_price['价格'], errors='coerce')
        avg_price = df_valid_price['价格_num'].mean()
    else:
        avg_price = None
    
    kpi = {
        "total_sales": int(total_sales),
        "mom_change": round(mom_change, 1),
        "top_brands": top_brands,
        "avg_price": round(avg_price, 2) if avg_price and not pd.isna(avg_price) else None
    }
    
    # ========== 3x3=9张图表 ==========
    print("生成3x3=9张图表...")
    channels = ['中价', '低价', '正价']
    segments = ['小学', '初中', '高中']
    
    charts = []
    chart_id = 1
    
    for channel in channels:
        for segment in segments:
            subset = df[(df['链路'] == channel) & (df['学段'] == segment)]
            
            if len(subset) == 0:
                continue
            
            pivot = subset.pivot_table(
                values='销量', 
                index='月份', 
                columns='竞品', 
                aggfunc='sum',
                fill_value=0
            ).reindex(all_months, fill_value=0)
            
            brands_with_sales = pivot.columns[pivot.sum() > 0].tolist()
            
            charts.append({
                "id": chart_id,
                "title": f"{channel}链路 - {segment} - 品牌月度销量",
                "description": f"{channel}链路下{segment}学段各品牌的月度销量趋势分析。",
                "data_support": f"基于{len(subset)}条数据记录分析",
                "source_files": [Path(file_path).name],
                "importance": "medium",
                "chart_type": "line",
                "chart_data": {
                    "x_labels": all_months,
                    "series": {brand: [int(v) for v in pivot[brand].values] for brand in brands_with_sales}
                },
                "metadata": {
                    "channel": channel,
                    "segment": segment
                }
            })
            chart_id += 1
    
    print(f"生成了{len(charts)}张图表")
    
    # ========== 商品颗粒度数据表格 ==========
    print("生成商品颗粒度数据表格...")
    
    product_summary = df.groupby(['竞品', '学段', '链路', '学科', '商品']).agg({
        '销量': 'sum',
        '价格': 'first'
    }).reset_index()
    
    monthly_by_product = df.groupby(['竞品', '学段', '链路', '商品', '月份']).agg({
        '销量': 'sum'
    }).reset_index()
    
    table_data = []
    for _, row in product_summary.iterrows():
        record = {
            "品牌": row['竞品'],
            "学段": row['学段'],
            "链路": row['链路'],
            "学科": row['学科'] if pd.notna(row['学科']) else None,
            "商品": row['商品'] if pd.notna(row['商品']) else None,
            "价格": row['价格'] if pd.notna(row['价格']) else None,
            "总销量": int(row['销量'])
        }
        
        product_monthly = monthly_by_product[
            (monthly_by_product['竞品'] == row['竞品']) &
            (monthly_by_product['学段'] == row['学段']) &
            (monthly_by_product['链路'] == row['链路']) &
            (monthly_by_product['商品'] == row['商品'])
        ]
        
        for month in all_months:
            month_data = product_monthly[product_monthly['月份'] == month]
            record[month] = int(month_data['销量'].values[0]) if len(month_data) > 0 else 0
        
        table_data.append(record)
    
    table_data.sort(key=lambda x: x['总销量'], reverse=True)
    
    columns = ['品牌', '学段', '链路', '学科', '商品', '价格', '总销量'] + all_months
    
    brands = sorted(df['竞品'].unique().tolist())
    segments_list = sorted(df['学段'].unique().tolist())
    channels_list = sorted(df['链路'].unique().tolist())
    
    table = {
        "id": 100,
        "title": "商品颗粒度数据表格",
        "description": "包含商品级别的详细销售数据，可通过下拉选项筛选查看具体信息。",
        "data_support": f"共{len(table_data)}条商品记录",
        "source_files": [Path(file_path).name],
        "importance": "low",
        "chart_type": "table",
        "chart_data": {
            "columns": columns,
            "data": table_data[:200],
            "filters": {
                "品牌": brands,
                "学段": segments_list,
                "链路": channels_list
            }
        }
    }
    
    # ========== 异常预警 ==========
    print("检测异常数据...")
    alerts = []
    
    monthly = df.groupby('月份')['销量'].sum().sort_index()
    for i in range(1, len(monthly)):
        change = (monthly.iloc[i] - monthly.iloc[i-1]) / monthly.iloc[i-1]
        if change < -0.3:
            alerts.append({
                "type": "销量骤降",
                "level": "high",
                "message": f"{monthly.index[i]}销量环比下降{abs(change)*100:.1f}%",
                "details": f"从{monthly.iloc[i-1]:,}件下降至{monthly.iloc[i]:,}件"
            })
        elif change > 0.5:
            alerts.append({
                "type": "销量激增",
                "level": "medium",
                "message": f"{monthly.index[i]}销量环比增长{change*100:.1f}%",
                "details": f"从{monthly.iloc[i-1]:,}件增长至{monthly.iloc[i]:,}件"
            })
    
    # ========== 行动建议 ==========
    print("生成行动建议...")
    recommendations = []
    
    if top_brands:
        top_brand = top_brands[0]
        recommendations.append({
            "priority": "high",
            "category": "市场策略",
            "suggestion": f"巩固{top_brand}市场领先地位",
            "details": f"{top_brand}销量领先，建议持续投入资源巩固优势",
            "action": "加大营销投入，优化产品组合"
        })
    
    segment_sales = df.groupby('学段')['销量'].sum().sort_values(ascending=False)
    if len(segment_sales) > 0:
        top_segment = segment_sales.index[0]
        recommendations.append({
            "priority": "medium",
            "category": "产品策略",
            "suggestion": f"重点发展{top_segment}学段市场",
            "details": f"{top_segment}学段贡献{segment_sales[top_segment]:,}件销量",
            "action": "开发针对性产品，提升用户体验"
        })
    
    channel_sales = df.groupby('链路')['销量'].sum().sort_values(ascending=False)
    if len(channel_sales) > 0:
        top_channel = channel_sales.index[0]
        recommendations.append({
            "priority": "medium",
            "category": "渠道策略",
            "suggestion": f"优化{top_channel}链路运营",
            "details": f"{top_channel}链路是主要销售渠道",
            "action": "提升转化率，优化定价策略"
        })
    
    # ========== 构建报告 ==========
    report = {
        "meta": {
            "title": "销售日报 - 竞品销量分析",
            "generated_at": datetime.now().isoformat(),
            "version": "2.0",
            "report_type": "daily_sales"
        },
        "summary": {
            "overall": f"基于数据分析，总销量达{total_sales:,}件，环比变化{mom_change:+.1f}%。TOP3品牌：{', '.join(top_brands)}。",
            "total_conclusions": len(charts) + 1,
            "high_importance_count": len([c for c in charts if c.get('importance') == 'high']),
            "source_files": [Path(file_path).name]
        },
        "kpi": kpi,
        "alerts": alerts,
        "recommendations": recommendations,
        "conclusions": charts + [table]
    }
    
    # 保存报告
    if output_path is None:
        output_path = 'outputs/reports/report-daily-sales.json'
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"报告已保存至: {output_path}")
    return report

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'uploads/竞品销量数据_数据库标准格式.xlsx'
    report = generate_daily_report(file_path)
    print(f"\n报告生成完成！")
    print(f"- 总销量: {report['kpi']['total_sales']:,}件")
    print(f"- 环比变化: {report['kpi']['mom_change']:+.1f}%")
    print(f"- 图表数量: {len(report['conclusions'])}")
    print(f"- 预警数量: {len(report['alerts'])}")
    print(f"- 建议数量: {len(report['recommendations'])}")
