#!/usr/bin/env python3
"""
基于已打标数据进行匹配打标 v3.4
- 始终读取 Sheet1，取消筛选获取全部数据
- 自动识别商品名称列（含 Unnamed:3 格式）
- 按列名识别中低价列，按列值检测低/中/正价列
- 无商品名称时按 product_id 匹配
"""
import pandas as pd
import os
import re
import sys
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TAGGED_DATA_DIR = '打了标的数据'

# 品牌别名：输入竞品名 → 打标文件品牌名
BRAND_ALIASES = {
    '斑马-课类': '猿辅导',
    '猿编程':   '猿辅导',
    '叫叫阅读': '叫叫',
}

PRICE_LEVEL_VALUES = {'低价', '中价', '正价', '低/中/正价'}
# 列名中包含这些关键词时直接认定为价格档位列
PRICE_LEVEL_COL_KEYWORDS = ['中低价', '低中价', '低/中/正', '价格档']


# ── 列识别工具 ──────────────────────────────────────────────

def get_product_name_column(df):
    """识别商品名称列（title / 商品名称 / Unnamed:3 兜底）"""
    for col in df.columns:
        col_lower = str(col).lower()
        if '商品名称' in str(col) or 'title' in col_lower:
            return col

    # 兜底：Unnamed: 3 列若有较长字符串内容，视为商品名称
    for col in df.columns:
        if str(col).startswith('Unnamed:') or str(col).startswith('Unnamed: '):
            non_null = df[col].dropna().astype(str)
            if len(non_null) > 0:
                avg_len = non_null.str.len().mean()
                if avg_len >= 8:
                    return col

    return None


def get_product_id_column(df):
    """识别 product_id 列（shangpin_url / 商品id / product_id）"""
    for col in df.columns:
        col_lower = str(col).lower()
        if col_lower in ('shangpin_url', '商品id', 'product_id', 'productid'):
            return col
        if 'product_id' in col_lower or '商品id' in str(col):
            return col
    return None


def detect_price_level_column(df):
    """检测低/中/正价列：先按列名，再按列值比例"""
    # 优先：列名包含关键词
    for col in df.columns:
        col_str = str(col)
        if any(kw in col_str for kw in PRICE_LEVEL_COL_KEYWORDS):
            return col

    # 次选：列值中 30%+ 是价格档位词
    for col in df.columns:
        non_null = df[col].dropna().astype(str)
        if len(non_null) == 0:
            continue
        matches = non_null[non_null.isin(PRICE_LEVEL_VALUES)]
        if len(matches) / len(non_null) >= 0.3:
            return col

    return None


def get_tagging_columns(df):
    """返回 {目标列名: 源列名} 映射"""
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
        elif ('学科' in col_str or '科目' in col_str) and '学科' not in cols:
            cols['学科'] = col

    return cols


# ── 数据库加载 ──────────────────────────────────────────────

def load_tagged_database():
    tagged_db = {}

    if not os.path.isdir(TAGGED_DATA_DIR):
        print(f"警告: 未找到打标数据目录 {TAGGED_DATA_DIR}")
        return tagged_db

    for filename in sorted(os.listdir(TAGGED_DATA_DIR)):
        if not filename.endswith('.xlsx') or filename.startswith('~$'):
            continue
        brand = os.path.splitext(filename)[0]
        filepath = os.path.join(TAGGED_DATA_DIR, filename)

        try:
            # 始终读 Sheet1，openpyxl 会忽略筛选状态，读取全部行
            df = pd.read_excel(filepath, sheet_name='Sheet1', engine='openpyxl')
        except Exception as e:
            print(f"跳过 {brand}: 读取失败 ({e})")
            continue

        tag_cols = get_tagging_columns(df)
        if not tag_cols:
            print(f"跳过 {brand}: 未找到打标列")
            continue

        name_col = get_product_name_column(df)
        id_col = get_product_id_column(df)

        if name_col is None and id_col is None:
            print(f"跳过 {brand}: 未找到商品名称或商品ID列")
            continue

        # 清理：优先按 id_col 去重（保留每个商品ID唯一），无 id_col 则按 name_col
        dedup_col = id_col if id_col else name_col
        df[dedup_col] = df[dedup_col].astype(str).str.strip()
        df = df[df[dedup_col].notna() & (df[dedup_col] != 'nan') & (df[dedup_col] != '')]
        df = df.drop_duplicates(subset=[dedup_col])

        if name_col:
            df[name_col] = df[name_col].astype(str).str.strip()
        if id_col:
            df[id_col] = df[id_col].astype(str).str.strip()

        tagged_db[brand] = {
            'df': df,
            'name_col': name_col,
            'id_col': id_col,
            'tag_cols': tag_cols,
        }
        match_mode = '名称' if name_col else 'ID'
        print(f"加载 {brand}: {len(df)} 条, 匹配方式:{match_mode}, 打标列: {list(tag_cols.keys())}")

    return tagged_db


def load_manual_tags():
    """加载人工审核确认的打标数据（优先级最高）"""
    manual_file = os.path.join(TAGGED_DATA_DIR, 'manual_tags.xlsx')
    if not os.path.exists(manual_file):
        return {}
    try:
        df = pd.read_excel(manual_file, sheet_name='Sheet1', engine='openpyxl')
        manual = {}
        for _, row in df.iterrows():
            pid = str(row.get('商品ID', '')).strip()
            if pid and pid != 'nan':
                manual[pid] = {
                    col: str(row.get(col, '')) if pd.notna(row.get(col, '')) else ''
                    for col in ['低/中/正价', '产品形态一', '产品形态二', '产品形态三', '产品形态四', '学段', '学科', '链路类型']
                }
        print(f"加载 manual_tags: {len(manual)} 条人工确认记录")
        return manual
    except Exception as e:
        print(f"加载 manual_tags 失败: {e}")
        return {}


# ── 匹配逻辑 ────────────────────────────────────────────────

# 去掉开头/结尾的【...】促销标签、后缀字母标识，提取核心名称
_LEADING_TAG = re.compile(r'^(【[^】]{1,20}】\s*)+')
_TRAILING_NOISE = re.compile(r'[\s\-_][A-Za-z0-9]{1,8}$')

def normalize_name(name):
    """去除促销前缀【XX专属】【开学特惠】等，保留核心商品名"""
    name = str(name).strip()
    name = _LEADING_TAG.sub('', name)   # 去开头标签
    name = _TRAILING_NOISE.sub('', name)  # 去末尾字母码（如 -B, ZB3）
    return name.strip()


def find_match(product_name, product_id, brand, tagged_db):
    if brand not in tagged_db:
        return None

    db_info = tagged_db[brand]
    df = db_info['df']
    name_col = db_info['name_col']
    id_col = db_info['id_col']
    tag_cols = db_info['tag_cols']

    # 1. 按 product_id 精确匹配（优先级最高）
    if product_id and product_id != 'nan' and id_col:
        pid = str(product_id).strip()
        id_match = df[df[id_col] == pid]
        if len(id_match) > 0:
            return extract_result(id_match.iloc[0], tag_cols)

    # 2. 按商品名称匹配
    if not name_col or not product_name or product_name == 'nan':
        return None

    product_name = str(product_name).strip()
    product_name_norm = normalize_name(product_name)

    # 2a. 精确匹配（原始名 + 归一化名）
    exact = df[df[name_col] == product_name]
    if len(exact) > 0:
        return extract_result(exact.iloc[0], tag_cols)

    if product_name_norm and product_name_norm != product_name:
        exact_norm = df[df[name_col].apply(normalize_name) == product_name_norm]
        if len(exact_norm) > 0:
            return extract_result(exact_norm.iloc[0], tag_cols)

    # 2b. 包含匹配（原始 & 归一化）
    for _, row in df.iterrows():
        db_name = str(row[name_col]).strip()
        db_name_norm = normalize_name(db_name)
        if len(db_name_norm) > 3:
            if db_name in product_name or product_name in db_name:
                return extract_result(row, tag_cols)
            if product_name_norm and db_name_norm:
                if db_name_norm in product_name_norm or product_name_norm in db_name_norm:
                    return extract_result(row, tag_cols)

    # 2c. 相似度匹配（对归一化名，阈值降为 0.8）
    best_match = None
    best_ratio = 0.80
    for _, row in df.iterrows():
        db_name_norm = normalize_name(str(row[name_col]))
        if db_name_norm and len(db_name_norm) > 5:
            ratio = SequenceMatcher(None, product_name_norm, db_name_norm).ratio()
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


# ── 主流程 ──────────────────────────────────────────────────

def tag_with_database(input_file, output_file=None):
    print("=" * 50)
    print("基于已打标数据库进行匹配打标 v3.4")
    print("=" * 50)
    print()

    print("正在加载已打标数据库（Sheet1，全量数据）...")
    tagged_db = load_tagged_database()
    print()
    manual_tags = load_manual_tags()
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
        product_id = str(row.get('商品ID', ''))
        brand = str(row.get('竞品', ''))
        # 品牌别名：将 斑马-课类/猿编程 指向猿辅导，叫叫阅读 指向叫叫
        lookup_brand = BRAND_ALIASES.get(brand, brand)

        if brand and brand != 'nan':
            # 优先：manual_tags（人工审核确认）
            if product_id and product_id != 'nan' and product_id in manual_tags:
                matched_count += 1
                for col in tagging_columns:
                    df.at[i, col] = manual_tags[product_id].get(col, '')
                continue

            result = find_match(product_name, product_id, lookup_brand, tagged_db)
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
