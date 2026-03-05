# -*- coding: utf-8 -*-
"""
蝉妈妈竞品数据爬虫
从蝉妈妈平台爬取竞品销量数据，用于生成竞品日报

使用方法:
1. 手动登录蝉妈妈网站获取cookie
2. 将cookie保存到 cookie.txt 文件中
3. 运行爬虫脚本
"""
import requests
import json
import time
import base64
import gzip
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path
from Crypto.Cipher import AES
from typing import List, Dict, Optional

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

JIEMI_KEY = 'cmmgfgehahweuuii'

COMPETITOR_SHOPS = [
    {'brand': '作业帮', 'shop_id': 'CDirgbaB', 'shop_name': '乐学图书教辅'},
    {'brand': '作业帮', 'shop_id': 'EIyTtRQo', 'shop_name': '百分优品教辅'},
    {'brand': '作业帮', 'shop_id': 'vYjDduDN', 'shop_name': '锦学图书学习营地'},
    {'brand': '作业帮', 'shop_id': 'EliGBLQo', 'shop_name': '锦学图书大通关'},
    {'brand': '作业帮', 'shop_id': 'LWYzfjrn', 'shop_name': '矩尺学习精选'},
    {'brand': '猿辅导', 'shop_id': 'dogdNUDN', 'shop_name': '素养教育快乐课堂'},
    {'brand': '猿辅导', 'shop_id': 'BLLNoYYD', 'shop_name': '猿辅导音像旗舰店'},
    {'brand': '猿辅导', 'shop_id': 'oVAGhBcR', 'shop_name': '猿辅导小猿素养'},
    {'brand': '猿辅导', 'shop_id': 'yLfxoGDU', 'shop_name': '小猿文化屋'},
    {'brand': '猿辅导', 'shop_id': 'hwnnPwSC', 'shop_name': '小猿书屋'},
    {'brand': '高途', 'shop_id': 'LAumwArn', 'shop_name': '苏州瑞之和文化店'},
    {'brand': '高途', 'shop_id': 'nzeUKENI', 'shop_name': '瑞之和文化艺术精品店'},
    {'brand': '高途', 'shop_id': 'lIOTSIkX', 'shop_name': '知源书屋严选铺'},
    {'brand': '高途', 'shop_id': 'EmQXmShu', 'shop_name': '事皆顺文传'},
    {'brand': '希望学', 'shop_id': 'uRykndkX', 'shop_name': '希学素养甄选'},
    {'brand': '希望学', 'shop_id': 'BZIeArdq', 'shop_name': '希望学初中企业5店'},
    {'brand': '希望学', 'shop_id': 'lHlvPfSC', 'shop_name': '融趣企业店7'},
    {'brand': '豆神', 'shop_id': 'IQYWnocR', 'shop_name': '豆神明兮教育严选'},
    {'brand': '豆神', 'shop_id': 'JhxLZWrj', 'shop_name': '豆神书书企业店'},
    {'brand': '豆神', 'shop_id': 'moWNzqBr', 'shop_name': '豆神读写营'},
    {'brand': '叫叫', 'shop_id': 'VEajcGed', 'shop_name': '叫叫阅读伴学站'},
    {'brand': '叫叫', 'shop_id': 'EaGXxSqO', 'shop_name': '叫叫阅读官方旗舰店'},
    {'brand': '有道', 'shop_id': 'ANVGoFEy', 'shop_name': '长汀念派科技好货店'},
    {'brand': '有道', 'shop_id': 'tWfhfTHs', 'shop_name': '长汀念派科技优品小铺'},
    {'brand': '有道', 'shop_id': 'qiZAqjgi', 'shop_name': '有道领世精选'},
    {'brand': '新东方', 'shop_id': 'tEKabXqO', 'shop_name': '杭州新东方素质成长中心'},
    {'brand': '新东方', 'shop_id': 'roBHFYBe', 'shop_name': '国际英语提能教育'},
    {'brand': '新东方', 'shop_id': 'oxLXKkUJ', 'shop_name': '新东方云书官方旗舰店'},
    {'brand': '斑马', 'shop_id': 'caVZCKEv', 'shop_name': '斑马世界官方旗舰店'},
    {'brand': '斑马', 'shop_id': 'nvzPMUA', 'shop_name': '斑马官方旗舰店'},
    {'brand': '斑马', 'shop_id': 'HGPZUVed', 'shop_name': '斑马图书旗舰店'},
]

class ChanmamaCrawler:
    def __init__(self, cookie: str = None):
        self.cookie = cookie
        self.session = None
        self.headers = None
        
    def load_cookie_from_file(self, cookie_file: str = 'cookie.txt') -> Optional[str]:
        """从文件加载cookie"""
        cookie_path = Path(__file__).parent.parent / cookie_file
        if cookie_path.exists():
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
                if cookie:
                    print(f"从 {cookie_file} 加载cookie成功")
                    return cookie
        return None
    
    def init_session(self, cookie: str = None) -> bool:
        """使用cookie初始化会话"""
        if not cookie:
            cookie = self.cookie or self.load_cookie_from_file()
        
        if not cookie:
            print("错误: 未提供cookie，请先登录蝉妈妈获取cookie")
            print("获取cookie方法:")
            print("1. 打开浏览器访问 https://www.chanmama.com 并登录")
            print("2. 按F12打开开发者工具")
            print("3. 切换到Network标签")
            print("4. 刷新页面，找到任意请求")
            print("5. 在请求头中找到Cookie字段，复制完整内容")
            print("6. 将cookie保存到项目根目录的 cookie.txt 文件中")
            return False
        
        self.session = requests.Session()
        self.session.trust_env = False  # 禁用环境变量中的代理
        self.session.headers = {
            'referer': 'https://www.chanmama.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookie': cookie
        }
        self.headers = dict(self.session.headers)
        print("会话初始化成功!")
        return True
    
    def aes_decrypt(self, data: str) -> bytes:
        """AES解密数据"""
        key = JIEMI_KEY.encode('utf8')
        data = base64.b64decode(data)
        cipher = AES.new(key, AES.MODE_ECB)
        text_decrypted = unpad(cipher.decrypt(data))
        return gzip.decompress(text_decrypted)
    
    def crawl_shop_products(
        self,
        shop_info: Dict,
        start_date: str,
        end_date: str,
        max_pages: int = 50
    ) -> List[Dict]:
        """爬取单个店铺的商品数据"""
        brand = shop_info['brand']
        shop_id = shop_info['shop_id']
        shop_name = shop_info['shop_name']
        
        print(f"正在爬取: {brand} - {shop_name}")
        
        all_products = []
        page = 1
        
        while page <= max_pages:
            time.sleep(1)
            
            url = (
                f'https://api-service.chanmama.com/v5/shop/detail/products?'
                f'brand_code=&bring_way=0&shop_id={shop_id}&big_promotion=0'
                f'&max_price=-1&min_price=-1&start_time={start_date}&end_time={end_date}'
                f'&keyword=&category_id=-1&page={page}&size=20&sort=amount'
                f'&is_new_corp=0&has_ad=0&cal_days_30_volume_trend=1&order_by=desc'
            )
            
            try:
                response = self.session.get(url, timeout=15, proxies={'http': None, 'https': None})
                resp_json = response.json()
                
                if resp_json.get('code') == 40100:
                    print(f"认证失败: cookie可能已过期，请重新获取")
                    break
                
                # code 为 0 或 None 都认为是成功
                if resp_json.get('code') not in [0, None]:
                    print(f"API错误: {resp_json.get('msg')}")
                    break
                
                data = resp_json.get("data", {}).get("data")
                if not data:
                    break
                
                decrypted = self.aes_decrypt(str(data))
                data_list = json.loads(decrypted).get("list", [])
                
                if not data_list:
                    break
                
                for item in data_list:
                    product = {
                        '竞品': brand,
                        '店铺ID': shop_id,
                        '店铺名称': shop_name,
                        '商品ID': item.get('product_id'),
                        '商品名称': item.get('title'),
                        '品牌': item.get('brand_name'),
                        '价格': item.get('sku_union_price_text'),
                        '销量': item.get('volume'),
                        '销售额': item.get('amount'),
                        '佣金率': f"{item.get('max_commission_rate')}%",
                        '关联达人': item.get('author_count'),
                        '关联直播': item.get('live_count'),
                        '关联视频': item.get('aweme_count'),
                        '爬取日期': start_date,
                        '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    all_products.append(product)
                
                print(f"  第{page}页，获取{len(data_list)}条商品")
                page += 1
                
                if len(data_list) < 20:
                    break
                    
            except Exception as e:
                print(f"爬取异常: {e}")
                break
        
        print(f"  完成，共获取{len(all_products)}条商品数据")
        return all_products
    
    def crawl_all_shops(
        self,
        start_date: str,
        end_date: str,
        shops: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """爬取所有店铺数据"""
        if not self.session:
            if not self.init_session():
                return []
        
        shops = shops or COMPETITOR_SHOPS
        all_data = []
        
        for shop in shops:
            products = self.crawl_shop_products(shop, start_date, end_date)
            all_data.extend(products)
            time.sleep(2)
        
        return all_data
    
    def save_to_excel(
        self,
        data: List[Dict],
        output_path: str,
        filename: Optional[str] = None
    ) -> str:
        """保存数据到Excel"""
        if not data:
            print("没有数据可保存")
            return ""
        
        df = pd.DataFrame(data)
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not filename:
            filename = f"竞品销量数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = output_dir / filename
        df.to_excel(filepath, index=False, sheet_name='Sheet1')
        
        print(f"数据已保存到: {filepath}")
        print(f"共 {len(df)} 条记录")
        
        return str(filepath)


def run_crawler(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: str = "uploads",
    cookie: str = None
) -> Dict:
    """运行爬虫主函数"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = start_date
    
    print(f"开始爬取数据: {start_date} ~ {end_date}")
    
    crawler = ChanmamaCrawler(cookie=cookie)
    
    if not crawler.init_session():
        return {
            'success': False,
            'message': '请先提供有效的cookie。获取方法：登录蝉妈妈网站后，从浏览器开发者工具中复制Cookie',
            'filepath': '',
            'count': 0,
            'date': start_date
        }
    
    data = crawler.crawl_all_shops(start_date, end_date)
    
    if data:
        filepath = crawler.save_to_excel(data, output_dir)
        return {
            'success': True,
            'message': f'成功爬取 {len(data)} 条数据',
            'filepath': filepath,
            'count': len(data),
            'date': start_date
        }
    else:
        return {
            'success': False,
            'message': '爬取失败，未获取到数据。请检查cookie是否有效',
            'filepath': '',
            'count': 0,
            'date': start_date
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        start_date = sys.argv[1]
        end_date = sys.argv[2] if len(sys.argv) > 2 else start_date
    else:
        start_date = None
        end_date = None
    
    result = run_crawler(start_date, end_date)
    print(json.dumps(result, ensure_ascii=False, indent=2))
