#!/usr/bin/env python3
"""
数据上传处理脚本
处理上传的Excel文件，将数据追加到数据库中
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# 数据存储目录
DATA_DIR = Path(__file__).parent.parent / 'uploads'
ARCHIVE_DIR = Path(__file__).parent.parent / 'archive'

def ensure_dirs():
    """确保目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def get_latest_file():
    """获取最新的数据文件"""
    ensure_dirs()
    files = list(DATA_DIR.glob('*.xlsx')) + list(DATA_DIR.glob('*.xls'))
    if not files:
        return None
    return max(files, key=lambda x: x.stat().st_mtime)

def append_data(new_file_path):
    """将新数据追加到现有数据中"""
    ensure_dirs()
    
    # 读取新数据
    new_df = pd.read_excel(new_file_path)
    print(f"新数据: {len(new_df)} 条记录")
    
    # 标准化列名
    column_mapping = {
        '销售日期': '销售日期',
        '日期': '销售日期',
        '链路': '链路',
        '学段': '学段',
        '竞品': '竞品',
        '品牌': '竞品',
        '商品': '商品',
        '商品名称': '商品',
        '价格': '价格',
        '学科': '学科',
        '销量': '销量',
        '销售数量': '销量'
    }
    
    # 重命名列
    new_df.columns = [column_mapping.get(col, col) for col in new_df.columns]
    
    # 确保日期格式正确
    if '销售日期' in new_df.columns:
        new_df['销售日期'] = pd.to_datetime(new_df['销售日期'])
    
    # 获取现有数据文件
    latest_file = get_latest_file()
    
    if latest_file:
        # 读取现有数据
        existing_df = pd.read_excel(latest_file)
        print(f"现有数据: {len(existing_df)} 条记录")
        
        # 合并数据（去重）
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # 按日期和商品去重，保留最新数据
        if '销售日期' in combined_df.columns and '商品' in combined_df.columns:
            combined_df = combined_df.drop_duplicates(
                subset=['销售日期', '商品', '竞品'],
                keep='last'
            )
        
        print(f"合并后数据: {len(combined_df)} 条记录")
    else:
        combined_df = new_df
    
    # 生成新文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f'竞品销量数据_{timestamp}.xlsx'
    new_filepath = DATA_DIR / new_filename
    
    # 保存合并后的数据
    combined_df.to_excel(new_filepath, index=False)
    print(f"数据已保存到: {new_filepath}")
    
    # 归档旧文件
    if latest_file and latest_file != new_filepath:
        archive_path = ARCHIVE_DIR / latest_file.name
        os.rename(latest_file, archive_path)
        print(f"旧文件已归档: {archive_path}")
    
    return {
        'success': True,
        'records': len(combined_df),
        'new_records': len(new_df),
        'file': str(new_filepath)
    }

if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = append_data(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False))
