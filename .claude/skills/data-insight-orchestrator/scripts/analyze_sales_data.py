#!/usr/bin/env python3
"""分析销售数据，生成日报可视化看板"""

import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from report_builder import ReportBuilder
from file_processor import FileProcessor


def analyze_sales_data():
    # 扫描上传目录
    processor = FileProcessor('../../../../uploads')
    files = processor.scan_files()
    
    if not files:
        print("No files found in uploads directory")
        return
    
    # 处理Excel文件
    excel_file = None
    for f in files:
        if f['type'] == 'Excel':
            excel_file = f['path']
            break
    
    if not excel_file:
        print("No Excel file found")
        return
    
    # 读取数据
    print(f"Processing file: {excel_file}")
    xl = pd.ExcelFile(excel_file)
    print(f"Sheet names: {xl.sheet_names}")
    
    # 读取第一个工作表
    df = pd.read_excel(xl, xl.sheet_names[0])
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)[:10]}...")  # 只显示前10列
    
    # 数据预处理
    # 实际列名：竞品（品牌）、学段、链路、学科、商品、价格，然后是日期列
    
    # 确保必要的列存在
    required_columns = ['竞品', '学段', '链路']
    for col in required_columns:
        if col not in df.columns:
            print(f"Column {col} not found in data")
            return
    
    # 获取日期列
    date_columns = [col for col in df.columns if isinstance(col, datetime)]
    print(f"Found {len(date_columns)} date columns")
    
    # 数据清洗
    df = df.dropna(subset=['竞品', '学段', '链路'])
    
    # 链路分类（低中正价）
    link_types = df['链路'].unique().tolist()
    # 学段分类（小初高）
    education_levels = df['学段'].unique().tolist()
    # 品牌列表
    brands = df['竞品'].unique().tolist()
    
    print(f"Link types: {link_types}")
    print(f"Education levels: {education_levels}")
    print(f"Brands: {brands}")
    
    # 生成图表数据
    conclusions = []
    chart_id = 1
    
    # 生成3*3=9张图表
    for link in link_types:
        for level in education_levels:
            # 筛选数据
            filtered_df = df[(df['链路'] == link) & (df['学段'] == level)]
            
            if filtered_df.empty:
                print(f"No data for {link} - {level}")
                continue
            
            # 按月汇总销量
            monthly_data = {}
            for brand in brands:
                brand_df = filtered_df[filtered_df['竞品'] == brand]
                if brand_df.empty:
                    continue
                
                # 计算每月销量
                monthly_sales = {}
                for date_col in date_columns:
                    month_key = date_col.strftime('%Y-%m')
                    if month_key not in monthly_sales:
                        monthly_sales[month_key] = 0
                    # 汇总该品牌在该月的销量
                    monthly_sales[month_key] += brand_df[date_col].sum()
                
                monthly_data[brand] = monthly_sales
            
            # 准备图表数据
            if monthly_data:
                # 获取所有月份
                all_months = sorted(set(month for brand_sales in monthly_data.values() for month in brand_sales.keys()))
                series = {}
                
                for brand, sales in monthly_data.items():
                    brand_series = []
                    for month in all_months:
                        brand_series.append(int(sales.get(month, 0)))
                    series[brand] = brand_series
                
                # 创建图表数据
                chart_data = {
                    'x_labels': all_months,
                    'series': series
                }
                
                # 添加结论
                conclusions.append({
                    'id': chart_id,
                    'title': f'{link}链路 - {level} - 品牌月度销量',
                    'description': f'{link}链路下{level}学段各品牌的月度销量趋势分析。',
                    'data_support': f'基于{len(filtered_df)}条数据记录分析',
                    'source_files': [os.path.basename(excel_file)],
                    'importance': 'medium',
                    'chart_type': 'line',
                    'chart_data': chart_data
                })
                chart_id += 1
    
    # 生成数据表格部分
    # 准备表格数据（只包含前500条，避免数据过大）
    table_data = []
    for _, row in df.iterrows():
        row_data = {
            '品牌': row['竞品'],
            '学段': row['学段'],
            '链路': row['链路'],
            '学科': row.get('学科', ''),
            '商品': row.get('商品', ''),
            '价格': row.get('价格', 0)
        }
        # 添加每月销量汇总
        monthly_totals = {}
        for date_col in date_columns:
            month_key = date_col.strftime('%Y-%m')
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += row[date_col]
        
        row_data.update(monthly_totals)
        table_data.append(row_data)
        
        if len(table_data) >= 500:
            break
    
    # 添加表格结论
    conclusions.append({
        'id': chart_id,
        'title': '商品颗粒度数据表格',
        'description': '包含商品级别的详细销售数据，可通过下拉选项查看具体信息。',
        'data_support': f'共{min(len(df), 500)}条商品记录',
        'source_files': [os.path.basename(excel_file)],
        'importance': 'low',
        'chart_type': 'table',
        'chart_data': {
            'columns': ['品牌', '学段', '链路', '学科', '商品', '价格'] + list(monthly_totals.keys()) if table_data else [],
            'data': table_data
        }
    })
    
    # 生成报告
    builder = ReportBuilder('../../../../outputs/reports')
    report = builder.build_report(
        title='日报可视化看板分析报告',
        overall_summary='基于销售数据生成的日报可视化看板，包含链路、学段、品牌维度的月度销量分析。',
        conclusions=conclusions,
        source_files=[os.path.basename(excel_file)]
    )
    
    # 保存报告
    filename = f"report-{datetime.now().strftime('%Y-%m-%d')}-daily-dashboard.json"
    builder.save_report(report, filename)
    builder.update_index(report, filename)
    print(f"Report generated: {filename}")
    
    return filename


if __name__ == '__main__':
    analyze_sales_data()