#!/usr/bin/env python3
"""
基于已打标数据进行匹配打标 - 智能版
自动识别不同格式的已打标数据，进行商品名称匹配
"""
import pandas as pd
import os
import sys
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TAGGED_DATA_DIR = '打了标的数据'

def get_product_name_column(df):
    for col in df.columns:
        col_lower = str(col).lower()
        if '商品名称' in str(col) or 'title' in col_lower:
            return col
    return None

PRICE_LEVEL_VALUES = {'低价', '中价', '正价', '低/中/正价'}

def detect_price_level_column(df):
    """检测哪一列存储了低/中/正价信息"""
    for col in df.columns:
        non_null = df[col].dropna().astype(str)
        matches = non_null[non_null.isin(PRICE_LEVEL_VALUES)]
        if len(matches) > 0 and len(matches) / max(len(non_null), 1) > 0.3:
            return col
    return None

def get_tagging_columns(df):
    price_col = detect_price_level_column(df)

    cols = {}
    price_col_assigned = False

    for col in df.columns:
        col_str = str(col)
        is_price_col = (col == price_col)

        if is_price_col and not price_col_assigned:
            cols['低/中/正价'] = col
            price_col_assigned = True
        elif '产品形态1' in col_str or '产品形态一' in col_str:
            if not is_price_col:
                cols['产品形态一'] = col
        elif '产品形态2' in col_str or '产品形态二' in col_str:
            if not is_price_col:
                cols['产品形态二'] = col
        elif '产品形态3' in col_str or '产品形态三' in col_str:
            if not is_price_col:
                cols['产品形态三'] = col
        elif '产品形态4' in col_str or '产品形态四' in col_str:
            if not is_price_col:
                cols['产品形态四'] = col
        elif '学段' in col_str and '学段' not in cols:
            cols['学段'] = col
        elif '学科' in col_str or '科目' in col_str:
            cols['学科'] = col

    return cols

def load_tagged_database():
    tagged_db = {}

    if not os.path.isdir(TAGGED_DATA_DIR):
        print(f"警告: 未找到打标数据目录 {TAGGED_DATA_DIR}")
        return tagged_db

    for filename in os.listdir(TAGGED_DATA_DIR):
        if not filename.endswith('.xlsx') or filename.startswith('~$'):
            continue
        brand = os.path.splitext(filename)[0]
        filepath = os.path.join(TAGGED_DATA_DIR, filename)

        df = pd.read_excel(filepath)
        
        name_col = get_product_name_column(df)
        if name_col is None:
            print(f"跳过 {brand}: 未找到商品名称列")
            continue
        
        tag_cols = get_tagging_columns(df)
        if not tag_cols:
            print(f"跳过 {brand}: 未找到打标列")
            continue
        
        df[name_col] = df[name_col].astype(str).str.strip()
        df = df.drop_duplicates(subset=[name_col])
        
        tagged_db[brand] = {
            'df': df,
            'name_col': name_col,
            'tag_cols': tag_cols
        }
        print(f"加载 {brand}: {len(df)} 条, 打标列: {list(tag_cols.keys())}")
    
    return tagged_db

def find_match(product_name, brand, tagged_db):
    if brand not in tagged_db:
        return None
    
    db_info = tagged_db[brand]
    df = db_info['df']
    name_col = db_info['name_col']
    tag_cols = db_info['tag_cols']
    
    product_name = str(product_name).strip()
    
    exact_match = df[df[name_col] == product_name]
    if len(exact_match) > 0:
        row = exact_match.iloc[0]
        return extract_result(row, tag_cols)
    
    for _, row in df.iterrows():
        db_name = str(row[name_col]).strip()
        if db_name and len(db_name) > 3:
            if db_name in product_name or product_name in db_name:
                return extract_result(row, tag_cols)
    
    best_match = None
    best_ratio = 0.85
    for _, row in df.iterrows():
        db_name = str(row[name_col]).strip()
        if db_name and len(db_name) > 5:
            ratio = SequenceMatcher(None, product_name, db_name).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = extract_result(row, tag_cols)
    
    return best_match

def extract_result(row, tag_cols):
    result = {
        '低/中/正价': '',
        '产品形态一': '',
        '产品形态二': '',
        '产品形态三': '',
        '产品形态四': '',
        '学段': '',
        '学科': '',
        '链路类型': '',
    }

    for target_col, source_col in tag_cols.items():
        val = row.get(source_col, '')
        if pd.notna(val):
            result[target_col] = str(val)

    return result

def tag_with_database(input_file, output_file=None):
    print("=" * 50)
    print("基于已打标数据库进行匹配打标")
    print("=" * 50)
    print()
    
    print("正在加载已打标数据库...")
    tagged_db = load_tagged_database()
    print()
    
    print(f"正在读取待打标文件: {input_file}")
    df = pd.read_excel(input_file)
    print(f"共 {len(df)} 条数据需要打标")
    print()
    
    tagging_columns = ['低/中/正价', '产品形态一', '产品形态二', '产品形态三', '产品形态四', '学段', '学科', '链路类型']
    for col in tagging_columns:
        if col not in df.columns:
            df[col] = ''
    
    matched_count = 0
    
    for i, row in df.iterrows():
        product_name = str(row.get('商品名称', ''))
        brand = str(row.get('竞品', ''))
        
        result = None
        if product_name and brand and product_name != 'nan':
            result = find_match(product_name, brand, tagged_db)
            if result:
                matched_count += 1
                for col in tagging_columns:
                    df.at[i, col] = result.get(col, '')
        
        if (i + 1) % 100 == 0:
            print(f"已处理 {i + 1}/{len(df)} 条 (匹配: {matched_count})")
    
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_匹配打标结果{ext}"
    
    df.to_excel(output_file, index=False)
    
    match_rate = matched_count * 100 / len(df)
    print()
    print("=" * 50)
    print("打标完成!")
    print(f"总处理: {len(df)} 条")
    print(f"数据库匹配: {matched_count} 条 ({match_rate:.1f}%)")
    print(f"结果已保存到: {output_file}")
    print("=" * 50)
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "uploads/竞品销量数据_20260306_113241.xlsx"
    
    tag_with_database(input_file)
