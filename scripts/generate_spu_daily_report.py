#!/usr/bin/env python3
"""
SPU商品级别日报生成脚本
生成三份日报：中价-品牌视角、中价-学科视角、低价-品牌视角
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

def calculate_spu_daily_report(df, channel, perspective):
    """
    生成SPU商品级别日报
    
    Args:
        df: 数据DataFrame
        channel: 链路（中价/低价）
        perspective: 视角（品牌/学科）
    """
    # 筛选链路数据
    channel_map = {'中价': '中价', '低价': '低价'}
    df_channel = df[df['链路'] == channel_map.get(channel, channel)].copy()
    
    if len(df_channel) == 0:
        return {"columns": [], "header_groups": [], "data": []}
    
    # 获取日期范围
    max_date = df_channel['销售日期'].max()
    
    # 计算各个时间段的日期范围
    yesterday = max_date - timedelta(days=1)
    last_3_days_start = max_date - timedelta(days=3)
    last_7_days_start = max_date - timedelta(days=7)
    last_30_days_start = max_date - timedelta(days=30)
    
    # 周范围
    t_week_end = max_date
    t_week_start = max_date - timedelta(days=6)
    t1_week_start = t_week_start - timedelta(days=7)
    t1_week_end = t_week_start - timedelta(days=1)
    t2_week_start = t1_week_start - timedelta(days=7)
    t2_week_end = t1_week_start - timedelta(days=1)
    t3_week_start = t2_week_start - timedelta(days=7)
    t3_week_end = t2_week_start - timedelta(days=1)
    t4_week_start = t3_week_start - timedelta(days=7)
    t4_week_end = t3_week_start - timedelta(days=1)
    
    # 月范围
    current_month_start = max_date.replace(day=1)
    t1_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    t2_month_start = (t1_month_start - timedelta(days=1)).replace(day=1)
    t3_month_start = (t2_month_start - timedelta(days=1)).replace(day=1)
    
    # 按SPU分组
    group_cols = ['学段', '竞品', '商品', '价格']
    if perspective == '学科':
        group_cols = ['学段', '学科', '竞品', '商品', '价格']
    
    # 计算各时间段销量
    def calc_period_sales(df_group, start_date, end_date):
        mask = (df_group['销售日期'] >= start_date) & (df_group['销售日期'] <= end_date)
        return df_group[mask]['销量'].sum()
    
    # 计算日均销量
    def calc_daily_avg(df_group, start_date, end_date, days):
        mask = (df_group['销售日期'] >= start_date) & (df_group['销售日期'] <= end_date)
        return df_group[mask]['销量'].sum() / days if days > 0 else 0
    
    # 按SPU汇总
    spu_data = []
    
    # 先计算各学段的总销量（用于计算占比）
    segment_totals = {}
    for seg in df_channel['学段'].unique():
        seg_df = df_channel[df_channel['学段'] == seg]
        # 昨日总销量
        segment_totals[seg] = {
            '昨日': calc_period_sales(seg_df, yesterday, yesterday),
            '3日': calc_daily_avg(seg_df, last_3_days_start, max_date, 3) * 3,  # 3日总销量
            '7日': calc_daily_avg(seg_df, last_7_days_start, max_date, 7) * 7,  # 7日总销量
            '30日': calc_daily_avg(seg_df, last_30_days_start, max_date, 30) * 30  # 30日总销量
        }
    
    for group_keys, group_df in df_channel.groupby([c for c in group_cols if c in df_channel.columns]):
        if len(group_cols) == 4:
            segment, brand, product, price = group_keys
            subject = None
        else:
            segment, subject, brand, product, price = group_keys
        
        # 计算各时间段销量
        yesterday_sales = calc_period_sales(group_df, yesterday, yesterday)
        avg_3d = calc_daily_avg(group_df, last_3_days_start, max_date, 3)
        avg_7d = calc_daily_avg(group_df, last_7_days_start, max_date, 7)
        avg_30d = calc_daily_avg(group_df, last_30_days_start, max_date, 30)
        
        # 计算学段占比
        seg_totals = segment_totals.get(segment, {})
        
        # 昨日销量占比
        yesterday_total = seg_totals.get('昨日', 0)
        yesterday_ratio = (yesterday_sales / yesterday_total * 100) if yesterday_total > 0 else 0
        
        # 3日日均占比（用3日总销量计算）
        total_3d = seg_totals.get('3日', 0)
        ratio_3d = (avg_3d * 3 / total_3d * 100) if total_3d > 0 else 0
        
        # 7日日均占比（用7日总销量计算）
        total_7d = seg_totals.get('7日', 0)
        ratio_7d = (avg_7d * 7 / total_7d * 100) if total_7d > 0 else 0
        
        # 30日日均占比（用30日总销量计算）
        total_30d = seg_totals.get('30日', 0)
        ratio_30d = (avg_30d * 30 / total_30d * 100) if total_30d > 0 else 0
        
        # 周累计
        t_week = calc_period_sales(group_df, t_week_start, t_week_end)
        t1_week = calc_period_sales(group_df, t1_week_start, t1_week_end)
        t2_week = calc_period_sales(group_df, t2_week_start, t2_week_end)
        t3_week = calc_period_sales(group_df, t3_week_start, t3_week_end)
        t4_week = calc_period_sales(group_df, t4_week_start, t4_week_end)
        
        # 月累计
        current_month = calc_period_sales(group_df, current_month_start, max_date)
        t1_month = calc_period_sales(group_df, t1_month_start, current_month_start - timedelta(days=1))
        t2_month = calc_period_sales(group_df, t2_month_start, t1_month_start - timedelta(days=1))
        t3_month = calc_period_sales(group_df, t3_month_start, t2_month_start - timedelta(days=1))
        
        record = {
            '学段': segment,
            '竞品': brand,
            '商品名称': product if product else '-',
            '价格': price if price and not pd.isna(price) else '-',
            '昨日销量': int(yesterday_sales),
            '3日日均': round(avg_3d, 1),
            '7日日均': round(avg_7d, 1),
            '30日日均': round(avg_30d, 1),
            '昨日销量占比': f"{yesterday_ratio:.1f}%",
            '3日日均占比': f"{ratio_3d:.1f}%",
            '7日日均占比': f"{ratio_7d:.1f}%",
            '30日日均占比': f"{ratio_30d:.1f}%",
            'T周': int(t_week),
            'T-1周': int(t1_week),
            'T-2周': int(t2_week),
            'T-3周': int(t3_week),
            'T-4周': int(t4_week),
            '当月': int(current_month),
            'T-1月': int(t1_month),
            'T-2月': int(t2_month),
            'T-3月': int(t3_month)
        }
        
        if perspective == '学科':
            record['学科'] = subject if subject else '-'
        
        spu_data.append(record)
    
    # 排序逻辑：先按学段分组，再按品牌分组，最后按昨日销量降序
    # 学段排序顺序
    segment_order = {'小学': 0, '初中': 1, '高中': 2, '低幼': 3}
    
    if perspective == '品牌':
        # 品牌视角：先按学段，再按品牌，最后按销量
        spu_data.sort(key=lambda x: (
            segment_order.get(x['学段'], 999),  # 学段排序
            x['竞品'],  # 品牌排序（字母顺序）
            -x['昨日销量']  # 销量降序
        ))
    else:
        # 学科视角：先按学段，再按学科，再按品牌，最后按销量
        spu_data.sort(key=lambda x: (
            segment_order.get(x['学段'], 999),  # 学段排序
            x.get('学科', ''),  # 学科排序
            x['竞品'],  # 品牌排序
            -x['昨日销量']  # 销量降序
        ))
    
    # 定义表头结构
    if perspective == '品牌':
        columns = ['学段', '竞品', '商品名称', '价格', 
                   '昨日销量', '3日日均', '7日日均', '30日日均',
                   '昨日销量占比', '3日日均占比', '7日日均占比', '30日日均占比',
                   'T周', 'T-1周', 'T-2周', 'T-3周', 'T-4周',
                   '当月', 'T-1月', 'T-2月', 'T-3月']
    else:
        columns = ['学段', '学科', '竞品', '商品名称', '价格',
                   '昨日销量', '3日日均', '7日日均', '30日日均',
                   '昨日销量占比', '3日日均占比', '7日日均占比', '30日日均占比',
                   'T周', 'T-1周', 'T-2周', 'T-3周', 'T-4周',
                   '当月', 'T-1月', 'T-2月', 'T-3月']
    
    # 定义表头分组
    header_groups = [
        {"title": "SPU相关信息", "colspan": 4 if perspective == '品牌' else 5},
        {"title": "近期日均销量（订单）", "colspan": 4},
        {"title": "单量在各学段占比", "colspan": 4},
        {"title": "周累计", "colspan": 5},
        {"title": "月累计", "colspan": 4}
    ]
    
    # 获取筛选选项
    segments = sorted(df_channel['学段'].dropna().unique().tolist())
    brands = sorted(df_channel['竞品'].dropna().unique().tolist())
    subjects = sorted(df_channel['学科'].dropna().unique().tolist()) if '学科' in df_channel.columns else []
    
    filters = {
        "学段": segments,
        "竞品": brands
    }
    
    if perspective == '学科' and subjects:
        filters["学科"] = subjects
    
    return {
        "columns": columns,
        "header_groups": header_groups,
        "data": spu_data,  # 显示全部数据
        "filters": filters
    }

def generate_daily_summary(df):
    """
    生成日报总体结论
    参考部门日报风格，按链路、学段、竞品维度分析
    """
    summary = {
        "大盘": {},
        "中价": {"segments": {}},
        "低价": {"segments": {}}
    }
    
    # 获取最新日期
    max_date = df['销售日期'].max()
    yesterday = max_date
    day_before = max_date - timedelta(days=1)
    
    # 计算昨日、3日、7日数据
    last_3_days_start = max_date - timedelta(days=2)
    last_7_days_start = max_date - timedelta(days=6)
    
    # ========== 大盘数据 ==========
    # 昨日大盘
    df_yesterday_all = df[df['销售日期'] == yesterday]
    yesterday_total_all = df_yesterday_all['销量'].sum()
    
    # 前日大盘
    df_day_before_all = df[df['销售日期'] == day_before]
    day_before_total_all = df_day_before_all['销量'].sum()
    
    # 环比变化
    mom_change = 0
    if day_before_total_all > 0:
        mom_change = (yesterday_total_all - day_before_total_all) / day_before_total_all * 100
    
    # 3日日均
    df_3d_all = df[df['销售日期'] >= last_3_days_start]
    avg_3d_all = df_3d_all['销量'].sum() / 3 if len(df_3d_all) > 0 else 0
    
    # 7日日均
    df_7d_all = df[df['销售日期'] >= last_7_days_start]
    avg_7d_all = df_7d_all['销量'].sum() / 7 if len(df_7d_all) > 0 else 0
    
    # 大盘TOP品牌
    yesterday_brand_all = df_yesterday_all.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    top_brand_all = yesterday_brand_all.index[0] if len(yesterday_brand_all) > 0 else None
    top_brand_sales_all = yesterday_brand_all.iloc[0] if len(yesterday_brand_all) > 0 else 0
    
    # 大盘TOP链路
    yesterday_channel_all = df_yesterday_all.groupby('链路')['销量'].sum().sort_values(ascending=False)
    top_channel = yesterday_channel_all.index[0] if len(yesterday_channel_all) > 0 else None
    top_channel_sales = yesterday_channel_all.iloc[0] if len(yesterday_channel_all) > 0 else 0
    
    # 大盘TOP学段
    yesterday_segment_all = df_yesterday_all.groupby('学段')['销量'].sum().sort_values(ascending=False)
    top_segment = yesterday_segment_all.index[0] if len(yesterday_segment_all) > 0 else None
    top_segment_sales = yesterday_segment_all.iloc[0] if len(yesterday_segment_all) > 0 else 0
    
    summary["大盘"] = {
        "yesterday_total": int(yesterday_total_all),
        "day_before_total": int(day_before_total_all),
        "mom_change": round(mom_change, 1),
        "avg_3d": int(avg_3d_all),
        "avg_7d": int(avg_7d_all),
        "top_brand": top_brand_all,
        "top_brand_sales": int(top_brand_sales_all),
        "top_channel": top_channel,
        "top_channel_sales": int(top_channel_sales),
        "top_segment": top_segment,
        "top_segment_sales": int(top_segment_sales),
        "brand_ranking": [(brand, int(sales)) for brand, sales in yesterday_brand_all.head(3).items()]
    }
    
    for channel in ['中价', '低价']:
        df_channel = df[df['链路'] == channel]
        
        # ========== 链路大盘数据 ==========
        # 昨日链路大盘
        df_yesterday_channel = df_channel[df_channel['销售日期'] == yesterday]
        yesterday_total_channel = df_yesterday_channel['销量'].sum()
        
        # 前日链路大盘
        df_day_before_channel = df_channel[df_channel['销售日期'] == day_before]
        day_before_total_channel = df_day_before_channel['销量'].sum()
        
        # 环比变化
        mom_change_channel = 0
        if day_before_total_channel > 0:
            mom_change_channel = (yesterday_total_channel - day_before_total_channel) / day_before_total_channel * 100
        
        # 3日日均
        df_3d_channel = df_channel[df_channel['销售日期'] >= last_3_days_start]
        avg_3d_channel = df_3d_channel['销量'].sum() / 3 if len(df_3d_channel) > 0 else 0
        
        # 7日日均
        df_7d_channel = df_channel[df_channel['销售日期'] >= last_7_days_start]
        avg_7d_channel = df_7d_channel['销量'].sum() / 7 if len(df_7d_channel) > 0 else 0
        
        # 链路TOP品牌
        yesterday_brand_channel = df_yesterday_channel.groupby('竞品')['销量'].sum().sort_values(ascending=False)
        top_brand_channel = yesterday_brand_channel.index[0] if len(yesterday_brand_channel) > 0 else None
        top_brand_sales_channel = yesterday_brand_channel.iloc[0] if len(yesterday_brand_channel) > 0 else 0
        
        # 链路TOP学段
        yesterday_segment_channel = df_yesterday_channel.groupby('学段')['销量'].sum().sort_values(ascending=False)
        top_segment_channel = yesterday_segment_channel.index[0] if len(yesterday_segment_channel) > 0 else None
        top_segment_sales_channel = yesterday_segment_channel.iloc[0] if len(yesterday_segment_channel) > 0 else 0
        
        summary[channel]["overview"] = {
            "yesterday_total": int(yesterday_total_channel),
            "day_before_total": int(day_before_total_channel),
            "mom_change": round(mom_change_channel, 1),
            "avg_3d": int(avg_3d_channel),
            "avg_7d": int(avg_7d_channel),
            "top_brand": top_brand_channel,
            "top_brand_sales": int(top_brand_sales_channel),
            "top_segment": top_segment_channel,
            "top_segment_sales": int(top_segment_sales_channel),
            "brand_ranking": [(brand, int(sales)) for brand, sales in yesterday_brand_channel.head(3).items()]
        }
        
        for segment in ['小学', '初中', '高中']:
            df_seg = df_channel[df_channel['学段'] == segment]
            
            if len(df_seg) == 0:
                continue
            
            # 昨日销量
            df_yesterday = df_seg[df_seg['销售日期'] == yesterday]
            yesterday_brand = df_yesterday.groupby('竞品')['销量'].sum().sort_values(ascending=False)
            yesterday_total = yesterday_brand.sum()
            
            # 3日日均
            df_3d = df_seg[df_seg['销售日期'] >= last_3_days_start]
            avg_3d_total = df_3d['销量'].sum() / 3 if len(df_3d) > 0 else 0
            avg_3d_brand = df_3d.groupby('竞品')['销量'].sum() / 3
            avg_3d_brand = avg_3d_brand.sort_values(ascending=False)
            
            # 7日日均
            df_7d = df_seg[df_seg['销售日期'] >= last_7_days_start]
            avg_7d_total = df_7d['销量'].sum() / 7 if len(df_7d) > 0 else 0
            avg_7d_brand = df_7d.groupby('竞品')['销量'].sum() / 7
            avg_7d_brand = avg_7d_brand.sort_values(ascending=False)
            
            # TOP竞品
            top_brand = yesterday_brand.index[0] if len(yesterday_brand) > 0 else None
            top_brand_sales = yesterday_brand.iloc[0] if len(yesterday_brand) > 0 else 0
            
            # 爆品
            df_yesterday_product = df_yesterday.groupby(['竞品', '商品'])['销量'].sum().sort_values(ascending=False)
            top_product = df_yesterday_product.index[0] if len(df_yesterday_product) > 0 else None
            top_product_sales = df_yesterday_product.iloc[0] if len(df_yesterday_product) > 0 else 0
            
            # 学科分析
            subject_sales = df_yesterday.groupby('学科')['销量'].sum().sort_values(ascending=False)
            top_subject = subject_sales.index[0] if len(subject_sales) > 0 else None
            
            summary[channel]["segments"][segment] = {
                "yesterday_total": int(yesterday_total),
                "avg_3d": int(avg_3d_total),
                "avg_7d": int(avg_7d_total),
                "top_brand": top_brand,
                "top_brand_sales": int(top_brand_sales),
                "top_product": f"{top_product[0]}-{top_product[1][:10]}" if top_product else None,
                "top_product_sales": int(top_product_sales),
                "top_subject": top_subject,
                "brand_ranking": [(brand, int(sales)) for brand, sales in yesterday_brand.head(3).items()]
            }
    
    return summary

def generate_overall_insights(df):
    """
    生成整体洞察（全年销量分析）
    参考抖音场日报分析风格
    """
    insights = []
    
    # ========== 1. 全年市场格局 ==========
    brand_sales = df.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    total_sales = brand_sales.sum()
    
    if len(brand_sales) > 0:
        top_brand = brand_sales.index[0]
        top_brand_sales = brand_sales.iloc[0]
        top_brand_share = top_brand_sales / total_sales * 100
        
        insights.append({
            "type": "市场格局",
            "icon": "🏆",
            "title": f"{top_brand}吃了全年{top_brand_share:.0f}%的市场份额",
            "content": f"{top_brand}全年销量{int(top_brand_sales):,}单，处于绝对领先地位。TOP3品牌（{brand_sales.index[0]}、{brand_sales.index[1]}、{brand_sales.index[2]}）合计占比{(brand_sales.head(3).sum()/total_sales*100):.0f}%。",
            "priority": "high"
        })
        
        # TOP5竞品排名
        if len(brand_sales) >= 5:
            top5 = brand_sales.head(5)
            ranking = " > ".join([f"{brand}（{int(sales/10000):.0f}万单）" for brand, sales in top5.items()])
            insights.append({
                "type": "竞品排名",
                "icon": "📊",
                "title": f"全年竞品TOP5：{top5.index[0]} > {top5.index[1]} > {top5.index[2]} > {top5.index[3]} > {top5.index[4]}",
                "content": f"全年竞品排名：{ranking}。{top5.index[0]}领先优势明显，{top5.index[1]}和{top5.index[2]}紧随其后。",
                "priority": "high"
            })
    
    # ========== 2. 链路分析 ==========
    channel_sales = df.groupby('链路')['销量'].sum().sort_values(ascending=False)
    if len(channel_sales) >= 2:
        top_channel = channel_sales.index[0]
        top_channel_sales = channel_sales.iloc[0]
        top_channel_share = top_channel_sales / channel_sales.sum() * 100
        
        channel_ranking = " > ".join([f"{ch}（{int(sales/10000):.0f}万单）" for ch, sales in channel_sales.items()])
        insights.append({
            "type": "链路分析",
            "icon": "🛒",
            "title": f"{top_channel}链路领先，市场份额{top_channel_share:.0f}%",
            "content": f"全年链路排名：{channel_ranking}。{top_channel}链路是主力销售渠道，建议重点投入资源。",
            "priority": "high"
        })
    
    # ========== 3. 学段分析 ==========
    segment_sales = df.groupby('学段')['销量'].sum().sort_values(ascending=False)
    if len(segment_sales) >= 2:
        top_segment = segment_sales.index[0]
        top_segment_share = segment_sales.iloc[0] / segment_sales.sum() * 100
        
        segment_ranking = " > ".join([f"{seg}（{int(sales/10000):.0f}万单）" for seg, sales in segment_sales.head(4).items()])
        insights.append({
            "type": "学段分析",
            "icon": "📚",
            "title": f"{top_segment}学段领先，市场份额{top_segment_share:.0f}%",
            "content": f"全年学段排名：{segment_ranking}。{top_segment}学段是核心市场，建议重点布局产品线。",
            "priority": "high"
        })
    
    # ========== 4. 月度趋势分析 ==========
    monthly_sales = df.groupby('月份')['销量'].sum().sort_index()
    if len(monthly_sales) >= 3:
        peak_month = monthly_sales.idxmax()
        peak_sales = monthly_sales.max()
        low_month = monthly_sales.idxmin()
        low_sales = monthly_sales.min()
        
        # 计算全年增长
        first_month = monthly_sales.iloc[0]
        last_month = monthly_sales.iloc[-1]
        yearly_growth = (last_month - first_month) / first_month * 100 if first_month > 0 else 0
        
        insights.append({
            "type": "月度趋势",
            "icon": "📈",
            "title": f"全年销量峰值在{peak_month}，达{int(peak_sales/10000):.0f}万单",
            "content": f"销量峰值{peak_month}（{int(peak_sales):,}单），低谷{low_month}（{int(low_sales):,}单）。全年首月{int(first_month):,}单→末月{int(last_month):,}单，{'增长' if yearly_growth > 0 else '下降'}{abs(yearly_growth):.0f}%。",
            "priority": "high"
        })
        
        # 季节性分析
        if len(monthly_sales) >= 6:
            # 找出连续增长的月份
            growth_months = []
            for i in range(1, len(monthly_sales)):
                if monthly_sales.iloc[i] > monthly_sales.iloc[i-1]:
                    growth_months.append(monthly_sales.index[i])
            
            if len(growth_months) > 0:
                insights.append({
                    "type": "季节性分析",
                    "icon": "📅",
                    "title": f"增长月份：{', '.join(growth_months[:3])}等",
                    "content": f"全年{len(growth_months)}个月实现环比增长，增长主要集中在{growth_months[0]}至{growth_months[-1]}。建议在增长月份加大投放力度。",
                    "priority": "medium"
                })
    
    # ========== 5. 学科分析 ==========
    if '学科' in df.columns:
        subject_sales = df.groupby('学科')['销量'].sum().sort_values(ascending=False)
        if len(subject_sales) >= 3:
            top_subject = subject_sales.index[0]
            top_subject_share = subject_sales.iloc[0] / subject_sales.sum() * 100
            
            subject_ranking = " > ".join([f"{sub}（{int(sales/10000):.0f}万单）" for sub, sales in subject_sales.head(3).items()])
            insights.append({
                "type": "学科分析",
                "icon": "🎯",
                "title": f"{top_subject}学科领先，市场份额{top_subject_share:.0f}%",
                "content": f"全年学科排名：{subject_ranking}。{top_subject}学科是主力赛道，建议重点深耕。",
                "priority": "medium"
            })
    
    # ========== 6. 爆品分析 ==========
    product_sales = df.groupby(['竞品', '商品'])['销量'].sum().sort_values(ascending=False)
    if len(product_sales) >= 3:
        top_product = product_sales.index[0]
        top_product_sales = product_sales.iloc[0]
        
        insights.append({
            "type": "爆品分析",
            "icon": "🔥",
            "title": f"全年爆品：{top_product[0]}{top_product[1][:15] if top_product[1] else '未知'}",
            "content": f"全年销量{int(top_product_sales):,}单，是年度最畅销单品。建议分析其成功要素，复制到其他产品线。",
            "priority": "medium"
        })
    
    # ========== 7. 竞品动态分析 ==========
    # 分析各品牌的月度趋势
    brand_monthly = df.pivot_table(values='销量', index='月份', columns='竞品', aggfunc='sum').sort_index()
    
    if len(brand_monthly) >= 2:
        # 找出增长最快的品牌
        brand_growth = {}
        for brand in brand_monthly.columns:
            first = brand_monthly[brand].iloc[0]
            last = brand_monthly[brand].iloc[-1]
            if first > 0:
                brand_growth[brand] = (last - first) / first * 100
        
        if brand_growth:
            fastest_growing = max(brand_growth.items(), key=lambda x: x[1])
            if fastest_growing[1] > 50:
                insights.append({
                    "type": "竞品动态",
                    "icon": "🚀",
                    "title": f"{fastest_growing[0]}全年增长最快，增幅{fastest_growing[1]:.0f}%",
                    "content": f"{fastest_growing[0]}从首月{int(brand_monthly[fastest_growing[0]].iloc[0]):,}单增长至末月{int(brand_monthly[fastest_growing[0]].iloc[-1]):,}单，增速领先。建议关注其增长策略。",
                    "priority": "high"
                })
    
    return insights

def generate_spu_insights(df, channel, perspective, spu_data):
    """
    生成SPU日报的核心洞察
    参考抖音场日报分析风格，输出深刻而敏锐的洞察
    """
    insights = []
    
    # 筛选链路数据
    df_channel = df[df['链路'] == channel].copy()
    
    # 获取最新日期（昨日）
    max_date = df_channel['销售日期'].max()
    yesterday = max_date
    
    # 计算昨日销量
    df_yesterday = df_channel[df_channel['销售日期'] == yesterday]
    yesterday_brand_sales = df_yesterday.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    yesterday_total = yesterday_brand_sales.sum()
    
    # 计算全年累计销量
    brand_sales = df_channel.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    total_channel_sales = brand_sales.sum()
    
    # ========== 1. 市场份额分析 ==========
    if len(brand_sales) > 0:
        top_brand = brand_sales.index[0]
        top_brand_share = brand_sales.iloc[0] / total_channel_sales * 100
        
        # 昨日销量
        yesterday_top_brand_sales = yesterday_brand_sales.get(top_brand, 0)
        
        # 头部品牌分析
        insights.append({
            "type": "市场格局",
            "icon": "🏆",
            "title": f"{top_brand}吃了{channel}链路{top_brand_share:.0f}%的市场份额",
            "content": f"{top_brand}全年销量{int(brand_sales.iloc[0]):,}单，在{channel}链路处于领先地位。昨日日销{int(yesterday_top_brand_sales):,}单。",
            "priority": "high"
        })
        
        # TOP3竞品排名（按昨日销量）
        if len(yesterday_brand_sales) >= 3:
            top3_yesterday = yesterday_brand_sales.head(3)
            ranking = " > ".join([f"{brand}（{int(sales):,}单）" for brand, sales in top3_yesterday.items()])
            insights.append({
                "type": "竞品排名",
                "icon": "📊",
                "title": f"昨日竞品排名：{top3_yesterday.index[0]} > {top3_yesterday.index[1]} > {top3_yesterday.index[2]}",
                "content": f"昨日{channel}链路竞品排名：{ranking}。{top3_yesterday.index[0]}占据头部位置。",
                "priority": "high"
            })
    
    # ========== 2. 学段分析 ==========
    # 昨日学段销量
    yesterday_segment_sales = df_yesterday.groupby('学段')['销量'].sum().sort_values(ascending=False)
    
    if len(yesterday_segment_sales) >= 2:
        top_segment = yesterday_segment_sales.index[0]
        top_segment_sales = yesterday_segment_sales.iloc[0]
        top_segment_share = top_segment_sales / yesterday_segment_sales.sum() * 100
        
        # 学段排名
        segment_ranking = " > ".join([f"{seg}（{int(sales):,}单）" for seg, sales in yesterday_segment_sales.head(3).items()])
        insights.append({
            "type": "学段分析",
            "icon": "📚",
            "title": f"{top_segment}学段领先，昨日占比{top_segment_share:.0f}%",
            "content": f"昨日{channel}链路学段排名：{segment_ranking}。{top_segment}学段是主力市场。",
            "priority": "high"
        })
    
    # ========== 3. 周环比分析 ==========
    if spu_data and len(spu_data.get('data', [])) > 0:
        total_t_week = sum(row.get('T周', 0) for row in spu_data['data'])
        total_t1_week = sum(row.get('T-1周', 0) for row in spu_data['data'])
        
        if total_t1_week > 0:
            wow_change = (total_t_week - total_t1_week) / total_t1_week * 100
            
            if wow_change > 20:
                insights.append({
                    "type": "增长趋势",
                    "icon": "📈",
                    "title": f"本周销量大幅增长{wow_change:.0f}%",
                    "content": f"{channel}链路本周日销{int(total_t_week):,}单，较上周增长{wow_change:.0f}%，增长势头强劲。建议分析增长驱动因素，持续加码投放。",
                    "priority": "high"
                })
            elif wow_change > 5:
                insights.append({
                    "type": "增长趋势",
                    "icon": "📈",
                    "title": f"本周销量小幅增长{wow_change:.0f}%",
                    "content": f"{channel}链路本周日销{int(total_t_week):,}单，较上周增长{wow_change:.0f}%，整体表现稳定向好。",
                    "priority": "medium"
                })
            elif wow_change < -20:
                insights.append({
                    "type": "增长趋势",
                    "icon": "📉",
                    "title": f"本周销量大幅下滑{abs(wow_change):.0f}%",
                    "content": f"{channel}链路本周日销{int(total_t_week):,}单，较上周下降{abs(wow_change):.0f}%，需警惕市场变化。建议深入分析下滑原因，及时调整策略。",
                    "priority": "high"
                })
            elif wow_change < -5:
                insights.append({
                    "type": "增长趋势",
                    "icon": "📉",
                    "title": f"本周销量小幅下滑{abs(wow_change):.0f}%",
                    "content": f"{channel}链路本周日销{int(total_t_week):,}单，较上周下降{abs(wow_change):.0f}%，需关注市场动态。",
                    "priority": "medium"
                })
    
    # ========== 4. 爆品分析 ==========
    if spu_data and len(spu_data.get('data', [])) > 0:
        # 找出昨日销量最高的产品
        top_products = sorted(spu_data['data'], key=lambda x: x.get('昨日销量', 0), reverse=True)[:3]
        
        if top_products[0].get('昨日销量', 0) > 0:
            product = top_products[0]
            product_name = product.get('商品名称', '未知商品')[:20]
            yesterday_sales = product.get('昨日销量', 0)
            brand = product.get('竞品', '未知品牌')
            price = product.get('价格', '-')
            
            insights.append({
                "type": "爆品分析",
                "icon": "🔥",
                "title": f"{brand}{product_name}为当前爆品",
                "content": f"昨日销量{yesterday_sales:,}单，价格{price}元，是{channel}链路最畅销单品。建议分析其成功要素，复制到其他产品线。",
                "priority": "high"
            })
        
        # 如果有多个爆品，分析TOP3
        if len(top_products) >= 2 and top_products[1].get('昨日销量', 0) > 0:
            p1, p2 = top_products[0], top_products[1]
            if p1.get('昨日销量', 0) > 0 and p2.get('昨日销量', 0) > 0:
                insights.append({
                    "type": "爆品对比",
                    "icon": "⚔️",
                    "title": f"TOP2爆品：{p1['竞品']} > {p2['竞品']}",
                    "content": f"{p1['竞品']}{p1['商品名称'][:15]}昨日{p1['昨日销量']:,}单，{p2['竞品']}{p2['商品名称'][:15]}昨日{p2['昨日销量']:,}单，两者差距{p1['昨日销量']-p2['昨日销量']:,}单。",
                    "priority": "medium"
                })
    
    # ========== 5. 学科分析（仅学科视角） ==========
    if perspective == '学科' and '学科' in df_channel.columns:
        subject_sales = df_channel.groupby('学科')['销量'].sum().sort_values(ascending=False)
        if len(subject_sales) >= 2:
            top_subject = subject_sales.index[0]
            top_subject_sales = subject_sales.iloc[0]
            top_subject_share = subject_sales.iloc[0] / subject_sales.sum() * 100
            
            subject_ranking = " > ".join([f"{sub}（{int(sales):,}单）" for sub, sales in subject_sales.head(3).items()])
            insights.append({
                "type": "学科分析",
                "icon": "🎯",
                "title": f"{top_subject}学科领先，市场份额{top_subject_share:.0f}%",
                "content": f"{channel}链路学科排名：{subject_ranking}。{top_subject}学科是当前主力赛道，建议重点布局。",
                "priority": "medium"
            })
    
    # ========== 6. 新品/动态分析 ==========
    if spu_data and len(spu_data.get('data', [])) > 0:
        # 分析7日日均 vs 30日日均，判断是否新品起量
        for product in spu_data['data'][:10]:
            avg_7d = product.get('7日日均', 0)
            avg_30d = product.get('30日日均', 0)
            
            if avg_30d > 0 and avg_7d > avg_30d * 1.5:
                growth_rate = (avg_7d - avg_30d) / avg_30d * 100
                insights.append({
                    "type": "新品起量",
                    "icon": "🚀",
                    "title": f"{product['竞品']}{product['商品名称'][:15]}开始起量",
                    "content": f"7日日均{avg_7d:.0f}单，较30日日均增长{growth_rate:.0f}%，呈现明显上升趋势。建议关注其投放策略和产品卖点。",
                    "priority": "medium"
                })
                break  # 只显示一个
    
    # ========== 7. 渠道策略建议 ==========
    if channel == '中价':
        insights.append({
            "type": "渠道策略",
            "icon": "💡",
            "title": "中价链路：性价比竞争",
            "content": "中价链路用户对价格敏感度适中，更看重产品性价比。建议通过优质内容和服务提升转化，避免纯价格战。",
            "priority": "low"
        })
    elif channel == '低价':
        insights.append({
            "type": "渠道策略",
            "icon": "💡",
            "title": "低价链路：流量竞争",
            "content": "低价链路用户价格敏感度高，流量获取是关键。建议优化投放ROI，通过规模效应提升利润空间。",
            "priority": "low"
        })
    
    return insights

def generate_daily_report_with_spu(file_path, output_path=None):
    """生成包含SPU日报的完整报告"""
    print(f"正在加载数据: {file_path}")
    df = pd.read_excel(file_path)
    print(f"数据加载完成，共{len(df)}条记录")
    
    # 添加月份列
    df['月份'] = df['销售日期'].dt.to_period('M').astype(str)
    all_months = sorted(df['月份'].unique())
    
    # ========== KPI指标 ==========
    print("计算KPI指标...")
    total_sales = df['销量'].sum()
    
    monthly_sales = df.groupby('月份')['销量'].sum().sort_index()
    if len(monthly_sales) >= 2:
        mom_change = (monthly_sales.iloc[-1] - monthly_sales.iloc[-2]) / monthly_sales.iloc[-2] * 100
    else:
        mom_change = 0
    
    brand_sales = df.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    top_brands = brand_sales.head(3).index.tolist()
    
    kpi = {
        "total_sales": int(total_sales),
        "mom_change": round(mom_change, 1),
        "top_brands": top_brands
    }
    
    # ========== 趋势图表（合并为一张带筛选功能） ==========
    print("生成趋势图表...")
    channels = ['低价', '中价', '正价']
    segments = ['小学', '初中', '高中']
    
    # 构建所有链路x学段组合的数据
    trend_chart_data = {
        "combinations": {},
        "filters": {
            "链路": channels,
            "学段": segments
        },
        "default_channel": "低价",
        "default_segment": "小学"
    }
    
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
            
            key = f"{channel}_{segment}"
            trend_chart_data["combinations"][key] = {
                "title": f"{channel}链路 - {segment} - 品牌月度销量",
                "description": f"{channel}链路下{segment}学段各品牌的月度销量趋势分析。",
                "data_support": f"基于{len(subset)}条数据记录分析",
                "x_labels": all_months,
                "series": {brand: [int(v) for v in pivot[brand].values] for brand in brands_with_sales},
                "channel": channel,
                "segment": segment
            }
    
    # 创建合并的趋势图表
    charts = [{
        "id": chart_id,
        "title": "品牌月度销量趋势",
        "description": "按链路和学段筛选查看各品牌的月度销量趋势。默认显示低价链路小学学段。",
        "data_support": "支持3个链路 × 3个学段 = 9种组合筛选",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "filterable_line",
        "chart_data": trend_chart_data
    }]
    
    print(f"生成了1张可筛选趋势图表（包含{len(trend_chart_data['combinations'])}种组合）")
    
    # ========== SPU商品级别日报 ==========
    print("生成SPU商品级别日报...")
    
    spu_reports = []
    
    # 1. 中价-品牌视角
    zhongjia_brand_data = calculate_spu_daily_report(df, '中价', '品牌')
    zhongjia_brand_insights = generate_spu_insights(df, '中价', '品牌', zhongjia_brand_data)
    spu_reports.append({
        "id": chart_id + 1,
        "title": "SPU日报 - 中价链路（品牌视角）",
        "description": "中价链路下按品牌视角的SPU商品级别日报，包含近期销量、学段占比、周月累计等指标。",
        "insights": zhongjia_brand_insights,
        "data_support": "按学段、品牌分组，昨日销量降序排列",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "complex_table",
        "chart_data": zhongjia_brand_data
    })
    
    # 2. 中价-学科视角
    zhongjia_subject_data = calculate_spu_daily_report(df, '中价', '学科')
    zhongjia_subject_insights = generate_spu_insights(df, '中价', '学科', zhongjia_subject_data)
    spu_reports.append({
        "id": chart_id + 2,
        "title": "SPU日报 - 中价链路（学科视角）",
        "description": "中价链路下按学科视角的SPU商品级别日报，包含近期销量、学段占比、周月累计等指标。",
        "insights": zhongjia_subject_insights,
        "data_support": "按学段、学科分组，昨日销量降序排列",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "complex_table",
        "chart_data": zhongjia_subject_data
    })
    
    # 3. 低价-品牌视角
    dijia_brand_data = calculate_spu_daily_report(df, '低价', '品牌')
    dijia_brand_insights = generate_spu_insights(df, '低价', '品牌', dijia_brand_data)
    spu_reports.append({
        "id": chart_id + 3,
        "title": "SPU日报 - 低价链路（品牌视角）",
        "description": "低价链路下按品牌视角的SPU商品级别日报，包含近期销量、学段占比、周月累计等指标。",
        "insights": dijia_brand_insights,
        "data_support": "按学段、品牌分组，昨日销量降序排列",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "complex_table",
        "chart_data": dijia_brand_data
    })
    
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
    
    # ========== 构建报告 ==========
    # 生成整体洞察
    print("生成整体洞察...")
    overall_insights = generate_overall_insights(df)
    
    # 生成日报总体结论
    print("生成日报总体结论...")
    daily_summary = generate_daily_summary(df)
    
    report = {
        "meta": {
            "title": "销售日报 - 竞品销量分析",
            "generated_at": datetime.now().isoformat(),
            "version": "2.3",
            "report_type": "daily_sales_with_spu"
        },
        "summary": {
            "overall": f"全年总销量达{total_sales:,}件（{total_sales/10000:.0f}万单），环比变化{mom_change:+.1f}%。TOP3品牌：{', '.join(top_brands)}。包含9张趋势图表和3份SPU商品级别日报。",
            "total_conclusions": len(charts) + len(spu_reports),
            "high_importance_count": len([c for c in charts if c.get('importance') == 'high']) + len(spu_reports),
            "source_files": [Path(file_path).name]
        },
        "kpi": kpi,
        "overall_insights": overall_insights,
        "daily_summary": daily_summary,
        "alerts": alerts,
        "recommendations": recommendations,
        "conclusions": charts + spu_reports
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
    report = generate_daily_report_with_spu(file_path)
    print(f"\n报告生成完成！")
    print(f"- 总销量: {report['kpi']['total_sales']:,}件")
    print(f"- 环比变化: {report['kpi']['mom_change']:+.1f}%")
    print(f"- 图表数量: {len([c for c in report['conclusions'] if c['chart_type'] != 'complex_table'])}")
    print(f"- SPU日报: {len([c for c in report['conclusions'] if c['chart_type'] == 'complex_table'])}")
