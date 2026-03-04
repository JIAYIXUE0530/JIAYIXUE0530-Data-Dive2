#!/usr/bin/env python3
"""
生成2025-11-28竞品日报
以2025-11-28为锚点，生成该日期的日报
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import calendar

ANCHOR_DATE = datetime(2025, 11, 28)

def get_week_range(anchor_date):
    """
    根据锚点日期计算T周、T-1周等日期范围
    T周 = 锚点日期所在周的上一周（完整自然周，周一到周日）
    """
    current_weekday = anchor_date.weekday()
    current_week_monday = anchor_date - timedelta(days=current_weekday)
    
    t_week_end = current_week_monday - timedelta(days=1)
    t_week_start = current_week_monday - timedelta(days=7)
    
    t1_week_end = t_week_start - timedelta(days=1)
    t1_week_start = t_week_start - timedelta(days=7)
    
    t2_week_end = t1_week_start - timedelta(days=1)
    t2_week_start = t1_week_start - timedelta(days=7)
    
    t3_week_end = t2_week_start - timedelta(days=1)
    t3_week_start = t2_week_start - timedelta(days=7)
    
    t4_week_end = t3_week_start - timedelta(days=1)
    t4_week_start = t3_week_start - timedelta(days=7)
    
    return {
        't_week_start': t_week_start,
        't_week_end': t_week_end,
        't1_week_start': t1_week_start,
        't1_week_end': t1_week_end,
        't2_week_start': t2_week_start,
        't2_week_end': t2_week_end,
        't3_week_start': t3_week_start,
        't3_week_end': t3_week_end,
        't4_week_start': t4_week_start,
        't4_week_end': t4_week_end
    }

def calculate_spu_daily_report(df, channel, perspective, anchor_date):
    """生成SPU商品级别日报"""
    channel_map = {'中价': '中价', '低价': '低价'}
    df_channel = df[df['链路'] == channel_map.get(channel, channel)].copy()
    
    if len(df_channel) == 0:
        return {"columns": [], "header_groups": [], "data": []}
    
    max_date = anchor_date
    yesterday = max_date - timedelta(days=1)
    last_3_days_start = yesterday - timedelta(days=2)
    last_7_days_start = yesterday - timedelta(days=6)
    last_30_days_start = yesterday - timedelta(days=29)
    
    week_ranges = get_week_range(anchor_date)
    t_week_start = week_ranges['t_week_start']
    t_week_end = week_ranges['t_week_end']
    t1_week_start = week_ranges['t1_week_start']
    t1_week_end = week_ranges['t1_week_end']
    t2_week_start = week_ranges['t2_week_start']
    t2_week_end = week_ranges['t2_week_end']
    t3_week_start = week_ranges['t3_week_start']
    t3_week_end = week_ranges['t3_week_end']
    t4_week_start = week_ranges['t4_week_start']
    t4_week_end = week_ranges['t4_week_end']
    
    current_month_start = max_date.replace(day=1)
    t1_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    t2_month_start = (t1_month_start - timedelta(days=1)).replace(day=1)
    t3_month_start = (t2_month_start - timedelta(days=1)).replace(day=1)
    
    group_cols = ['学段', '竞品', '商品', '价格']
    if perspective == '学科':
        group_cols = ['学段', '学科', '竞品', '商品', '价格']
    
    def calc_period_sales(df_group, start_date, end_date):
        mask = (df_group['销售日期'] >= start_date) & (df_group['销售日期'] <= end_date)
        return df_group[mask]['销量'].sum()
    
    def calc_daily_avg_with_threshold(df_group, start_date, end_date, threshold=5):
        mask = (df_group['销售日期'] >= start_date) & (df_group['销售日期'] <= end_date)
        df_period = df_group[mask]
        daily_sales = df_period.groupby('销售日期')['销量'].sum()
        valid_days = (daily_sales >= threshold).sum()
        total_sales = daily_sales.sum()
        if valid_days > 0:
            return total_sales / valid_days, valid_days
        return 0, 0
    
    spu_data = []
    
    segment_totals = {}
    for seg in df_channel['学段'].unique():
        seg_df = df_channel[df_channel['学段'] == seg]
        yesterday_total = calc_period_sales(seg_df, yesterday, yesterday)
        total_3d_sales = calc_period_sales(seg_df, last_3_days_start, yesterday)
        total_7d_sales = calc_period_sales(seg_df, last_7_days_start, yesterday)
        total_30d_sales = calc_period_sales(seg_df, last_30_days_start, yesterday)
        
        segment_totals[seg] = {
            '昨日': yesterday_total,
            '3日总销量': total_3d_sales,
            '7日总销量': total_7d_sales,
            '30日总销量': total_30d_sales
        }
    
    for group_keys, group_df in df_channel.groupby([c for c in group_cols if c in df_channel.columns]):
        if len(group_cols) == 4:
            segment, brand, product, price = group_keys
            subject = None
        else:
            segment, subject, brand, product, price = group_keys
        
        yesterday_sales = calc_period_sales(group_df, yesterday, yesterday)
        total_3d_sales = calc_period_sales(group_df, last_3_days_start, yesterday)
        total_7d_sales = calc_period_sales(group_df, last_7_days_start, yesterday)
        total_30d_sales = calc_period_sales(group_df, last_30_days_start, yesterday)
        
        avg_3d, valid_3d = calc_daily_avg_with_threshold(group_df, last_3_days_start, yesterday)
        avg_7d, valid_7d = calc_daily_avg_with_threshold(group_df, last_7_days_start, yesterday)
        avg_30d, valid_30d = calc_daily_avg_with_threshold(group_df, last_30_days_start, yesterday)
        
        seg_totals = segment_totals.get(segment, {})
        
        yesterday_total = seg_totals.get('昨日', 0)
        yesterday_ratio = (yesterday_sales / yesterday_total * 100) if yesterday_total > 0 else 0
        
        seg_total_3d = seg_totals.get('3日总销量', 0)
        ratio_3d = (total_3d_sales / seg_total_3d * 100) if seg_total_3d > 0 else 0
        
        seg_total_7d = seg_totals.get('7日总销量', 0)
        ratio_7d = (total_7d_sales / seg_total_7d * 100) if seg_total_7d > 0 else 0
        
        seg_total_30d = seg_totals.get('30日总销量', 0)
        ratio_30d = (total_30d_sales / seg_total_30d * 100) if seg_total_30d > 0 else 0
        
        t_week = calc_period_sales(group_df, t_week_start, t_week_end)
        t1_week = calc_period_sales(group_df, t1_week_start, t1_week_end)
        t2_week = calc_period_sales(group_df, t2_week_start, t2_week_end)
        t3_week = calc_period_sales(group_df, t3_week_start, t3_week_end)
        t4_week = calc_period_sales(group_df, t4_week_start, t4_week_end)
        
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
    
    segment_order = {'小学': 0, '初中': 1, '高中': 2, '低幼': 3}
    brand_order = {'作业帮': 0, '猿辅导': 1, '高途': 2, '希望学': 3, '豆神': 4, '叫叫': 5, 'IP': 999}
    
    if perspective == '品牌':
        spu_data.sort(key=lambda x: (
            segment_order.get(x['学段'], 999),
            brand_order.get(x['竞品'], 500),
            -x['昨日销量']
        ))
    else:
        spu_data.sort(key=lambda x: (
            segment_order.get(x['学段'], 999),
            x.get('学科', ''),
            brand_order.get(x['竞品'], 500),
            -x['昨日销量']
        ))
    
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
    
    header_groups = [
        {"title": "SPU相关信息", "colspan": 4 if perspective == '品牌' else 5},
        {"title": "近期日均销量（订单）", "colspan": 4},
        {"title": "单量在各学段占比", "colspan": 4},
        {"title": "周累计", "colspan": 5},
        {"title": "月累计", "colspan": 4}
    ]
    
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
        "data": spu_data,
        "filters": filters
    }

def generate_spu_insights(df, channel, perspective, spu_data, anchor_date):
    """生成SPU日报的核心洞察"""
    insights = []
    
    df_channel = df[df['链路'] == channel].copy()
    max_date = anchor_date
    yesterday = max_date - timedelta(days=1)
    
    df_yesterday = df_channel[df_channel['销售日期'] == yesterday]
    yesterday_brand_sales = df_yesterday.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    yesterday_total = yesterday_brand_sales.sum()
    
    brand_sales = df_channel.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    total_channel_sales = brand_sales.sum()
    
    date_str = yesterday.strftime('%m月%d日')
    
    if len(brand_sales) > 0:
        top_brand = brand_sales.index[0]
        top_brand_share = brand_sales.iloc[0] / total_channel_sales * 100
        yesterday_top_brand_sales = yesterday_brand_sales.get(top_brand, 0)
        
        insights.append({
            "type": "市场格局",
            "icon": "🏆",
            "title": f"{top_brand}吃了{channel}链路{top_brand_share:.0f}%的市场份额",
            "content": f"{top_brand}累计销量{int(brand_sales.iloc[0]):,}单，在{channel}链路处于领先地位。{date_str}日销{int(yesterday_top_brand_sales):,}单。",
            "priority": "high"
        })
        
        if len(yesterday_brand_sales) >= 3:
            top3_yesterday = yesterday_brand_sales.head(3)
            ranking = " > ".join([f"{brand}（{int(sales):,}单）" for brand, sales in top3_yesterday.items()])
            insights.append({
                "type": "竞品排名",
                "icon": "📊",
                "title": f"{date_str}竞品排名：{top3_yesterday.index[0]} > {top3_yesterday.index[1]} > {top3_yesterday.index[2]}",
                "content": f"{date_str}{channel}链路竞品排名：{ranking}。{top3_yesterday.index[0]}占据头部位置。",
                "priority": "high"
            })
    
    yesterday_segment_sales = df_yesterday.groupby('学段')['销量'].sum().sort_values(ascending=False)
    
    if len(yesterday_segment_sales) >= 2:
        top_segment = yesterday_segment_sales.index[0]
        top_segment_sales = yesterday_segment_sales.iloc[0]
        top_segment_share = top_segment_sales / yesterday_segment_sales.sum() * 100
        
        segment_ranking = " > ".join([f"{seg}（{int(sales):,}单）" for seg, sales in yesterday_segment_sales.head(3).items()])
        insights.append({
            "type": "学段分析",
            "icon": "📚",
            "title": f"{top_segment}学段领先，{date_str}占比{top_segment_share:.0f}%",
            "content": f"{date_str}{channel}链路学段排名：{segment_ranking}。{top_segment}学段是主力市场。",
            "priority": "high"
        })
    
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
                    "content": f"{channel}链路本周日销{int(total_t_week):,}单，较上周增长{wow_change:.0f}%，增长势头强劲。",
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
                    "content": f"{channel}链路本周日销{int(total_t_week):,}单，较上周下降{abs(wow_change):.0f}%，需警惕市场变化。",
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
    
    if spu_data and len(spu_data.get('data', [])) > 0:
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
                "content": f"{date_str}销量{yesterday_sales:,}单，价格{price}元，是{channel}链路最畅销单品。",
                "priority": "high"
            })
    
    return insights

def generate_overall_insights(df, anchor_date):
    """生成整体洞察"""
    insights = []
    
    brand_sales = df.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    total_sales = brand_sales.sum()
    
    if len(brand_sales) > 0:
        top_brand = brand_sales.index[0]
        top_brand_sales = brand_sales.iloc[0]
        top_brand_share = top_brand_sales / total_sales * 100
        
        insights.append({
            "type": "市场格局",
            "icon": "🏆",
            "title": f"{top_brand}吃了{top_brand_share:.0f}%的市场份额",
            "content": f"{top_brand}累计销量{int(top_brand_sales):,}单，处于绝对领先地位。TOP3品牌合计占比{(brand_sales.head(3).sum()/total_sales*100):.0f}%。",
            "priority": "high"
        })
    
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
            "content": f"链路排名：{channel_ranking}。{top_channel}链路是主力销售渠道。",
            "priority": "high"
        })
    
    segment_sales = df.groupby('学段')['销量'].sum().sort_values(ascending=False)
    if len(segment_sales) >= 2:
        top_segment = segment_sales.index[0]
        top_segment_share = segment_sales.iloc[0] / segment_sales.sum() * 100
        
        segment_ranking = " > ".join([f"{seg}（{int(sales/10000):.0f}万单）" for seg, sales in segment_sales.head(4).items()])
        insights.append({
            "type": "学段分析",
            "icon": "📚",
            "title": f"{top_segment}学段领先，市场份额{top_segment_share:.0f}%",
            "content": f"学段排名：{segment_ranking}。{top_segment}学段是核心市场。",
            "priority": "high"
        })
    
    return insights

def generate_daily_summary(df, anchor_date):
    """生成日报总体结论"""
    summary = {
        "大盘": {},
        "中价": {"segments": {}},
        "低价": {"segments": {}}
    }
    
    max_date = anchor_date
    yesterday = max_date - timedelta(days=1)
    day_before = yesterday - timedelta(days=1)
    
    last_3_days_start = yesterday - timedelta(days=2)
    last_7_days_start = yesterday - timedelta(days=6)
    
    df_yesterday_all = df[df['销售日期'] == yesterday]
    yesterday_total_all = df_yesterday_all['销量'].sum()
    
    df_day_before_all = df[df['销售日期'] == day_before]
    day_before_total_all = df_day_before_all['销量'].sum()
    
    mom_change = 0
    if day_before_total_all > 0:
        mom_change = (yesterday_total_all - day_before_total_all) / day_before_total_all * 100
    
    df_3d_all = df[df['销售日期'] >= last_3_days_start]
    avg_3d_all = df_3d_all['销量'].sum() / 3 if len(df_3d_all) > 0 else 0
    
    df_7d_all = df[df['销售日期'] >= last_7_days_start]
    avg_7d_all = df_7d_all['销量'].sum() / 7 if len(df_7d_all) > 0 else 0
    
    yesterday_brand_all = df_yesterday_all.groupby('竞品')['销量'].sum().sort_values(ascending=False)
    top_brand_all = yesterday_brand_all.index[0] if len(yesterday_brand_all) > 0 else None
    top_brand_sales_all = yesterday_brand_all.iloc[0] if len(yesterday_brand_all) > 0 else 0
    
    yesterday_channel_all = df_yesterday_all.groupby('链路')['销量'].sum().sort_values(ascending=False)
    top_channel = yesterday_channel_all.index[0] if len(yesterday_channel_all) > 0 else None
    top_channel_sales = yesterday_channel_all.iloc[0] if len(yesterday_channel_all) > 0 else 0
    
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
        
        df_yesterday_channel = df_channel[df_channel['销售日期'] == yesterday]
        yesterday_total_channel = df_yesterday_channel['销量'].sum()
        
        df_day_before_channel = df_channel[df_channel['销售日期'] == day_before]
        day_before_total_channel = df_day_before_channel['销量'].sum()
        
        mom_change_channel = 0
        if day_before_total_channel > 0:
            mom_change_channel = (yesterday_total_channel - day_before_total_channel) / day_before_total_channel * 100
        
        df_3d_channel = df_channel[df_channel['销售日期'] >= last_3_days_start]
        avg_3d_channel = df_3d_channel['销量'].sum() / 3 if len(df_3d_channel) > 0 else 0
        
        df_7d_channel = df_channel[df_channel['销售日期'] >= last_7_days_start]
        avg_7d_channel = df_7d_channel['销量'].sum() / 7 if len(df_7d_channel) > 0 else 0
        
        yesterday_brand_channel = df_yesterday_channel.groupby('竞品')['销量'].sum().sort_values(ascending=False)
        top_brand_channel = yesterday_brand_channel.index[0] if len(yesterday_brand_channel) > 0 else None
        top_brand_sales_channel = yesterday_brand_channel.iloc[0] if len(yesterday_brand_channel) > 0 else 0
        
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
            
            df_yesterday = df_seg[df_seg['销售日期'] == yesterday]
            yesterday_brand = df_yesterday.groupby('竞品')['销量'].sum().sort_values(ascending=False)
            yesterday_total = yesterday_brand.sum()
            
            df_3d = df_seg[df_seg['销售日期'] >= last_3_days_start]
            avg_3d_total = df_3d['销量'].sum() / 3 if len(df_3d) > 0 else 0
            
            df_7d = df_seg[df_seg['销售日期'] >= last_7_days_start]
            avg_7d_total = df_7d['销量'].sum() / 7 if len(df_7d) > 0 else 0
            
            top_brand = yesterday_brand.index[0] if len(yesterday_brand) > 0 else None
            top_brand_sales = yesterday_brand.iloc[0] if len(yesterday_brand) > 0 else 0
            
            df_yesterday_product = df_yesterday.groupby(['竞品', '商品'])['销量'].sum().sort_values(ascending=False)
            top_product = df_yesterday_product.index[0] if len(df_yesterday_product) > 0 else None
            top_product_sales = df_yesterday_product.iloc[0] if len(df_yesterday_product) > 0 else 0
            
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

def generate_report(file_path, anchor_date, output_path=None):
    """生成完整日报"""
    print(f"正在加载数据: {file_path}")
    df = pd.read_excel(file_path)
    print(f"数据加载完成，共{len(df)}条记录")
    
    df = df[df['销售日期'] <= anchor_date]
    print(f"筛选后数据：{len(df)}条记录（截止{anchor_date.strftime('%Y-%m-%d')}）")
    
    df['月份'] = df['销售日期'].dt.to_period('M').astype(str)
    all_months = sorted(df['月份'].unique())
    
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
    
    print("生成趋势图表...")
    channels = ['低价', '中价', '正价']
    segments = ['小学', '初中', '高中']
    
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
    
    charts = [{
        "id": chart_id,
        "title": "品牌月度销量趋势",
        "description": "按链路和学段筛选查看各品牌的月度销量趋势。",
        "data_support": "支持多种组合筛选",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "filterable_line",
        "chart_data": trend_chart_data
    }]
    
    print(f"生成了1张可筛选趋势图表（包含{len(trend_chart_data['combinations'])}种组合）")
    
    print("生成SPU商品级别日报...")
    
    spu_reports = []
    
    zhongjia_brand_data = calculate_spu_daily_report(df, '中价', '品牌', anchor_date)
    zhongjia_brand_insights = generate_spu_insights(df, '中价', '品牌', zhongjia_brand_data, anchor_date)
    spu_reports.append({
        "id": chart_id + 1,
        "title": "SPU日报 - 中价链路（品牌视角）",
        "description": "中价链路下按品牌视角的SPU商品级别日报。",
        "insights": zhongjia_brand_insights,
        "data_support": "按学段、品牌分组，昨日销量降序排列",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "complex_table",
        "chart_data": zhongjia_brand_data
    })
    
    zhongjia_subject_data = calculate_spu_daily_report(df, '中价', '学科', anchor_date)
    zhongjia_subject_insights = generate_spu_insights(df, '中价', '学科', zhongjia_subject_data, anchor_date)
    spu_reports.append({
        "id": chart_id + 2,
        "title": "SPU日报 - 中价链路（学科视角）",
        "description": "中价链路下按学科视角的SPU商品级别日报。",
        "insights": zhongjia_subject_insights,
        "data_support": "按学段、学科分组，昨日销量降序排列",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "complex_table",
        "chart_data": zhongjia_subject_data
    })
    
    dijia_brand_data = calculate_spu_daily_report(df, '低价', '品牌', anchor_date)
    dijia_brand_insights = generate_spu_insights(df, '低价', '品牌', dijia_brand_data, anchor_date)
    spu_reports.append({
        "id": chart_id + 3,
        "title": "SPU日报 - 低价链路（品牌视角）",
        "description": "低价链路下按品牌视角的SPU商品级别日报。",
        "insights": dijia_brand_insights,
        "data_support": "按学段、品牌分组，昨日销量降序排列",
        "source_files": [Path(file_path).name],
        "importance": "high",
        "chart_type": "complex_table",
        "chart_data": dijia_brand_data
    })
    
    print("生成整体洞察...")
    overall_insights = generate_overall_insights(df, anchor_date)
    
    print("生成日报总体结论...")
    daily_summary = generate_daily_summary(df, anchor_date)
    
    report = {
        "meta": {
            "title": "2025-11-28竞品日报",
            "generated_at": datetime.now().isoformat(),
            "version": "2.3",
            "report_type": "daily_sales_with_spu",
            "anchor_date": anchor_date.strftime('%Y-%m-%d')
        },
        "summary": {
            "overall": f"截止2025年11月28日，累计销量达{total_sales:,}件（{total_sales/10000:.0f}万单），环比变化{mom_change:+.1f}%。TOP3品牌：{', '.join(top_brands)}。",
            "total_conclusions": len(charts) + len(spu_reports),
            "high_importance_count": len([c for c in charts if c.get('importance') == 'high']) + len(spu_reports),
            "source_files": [Path(file_path).name]
        },
        "kpi": kpi,
        "overall_insights": overall_insights,
        "daily_summary": daily_summary,
        "conclusions": charts + spu_reports
    }
    
    if output_path is None:
        output_path = 'outputs/reports/report-2025-11-28.json'
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"报告已保存至: {output_path}")
    return report

if __name__ == "__main__":
    file_path = 'uploads/竞品销量数据_数据库标准格式.xlsx'
    report = generate_report(file_path, ANCHOR_DATE)
    print(f"\n报告生成完成！")
    print(f"- 累计销量: {report['kpi']['total_sales']:,}件")
    print(f"- 环比变化: {report['kpi']['mom_change']:+.1f}%")
