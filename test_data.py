#!/usr/bin/env python3
import requests
import os
import json
import base64
import gzip
from Crypto.Cipher import AES

os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

BLOCK_SIZE = 16
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
JIEMI_KEY = 'cmmgfgehahweuuii'

with open('cookie.txt', 'r') as f:
    cookie = f.read().strip()

session = requests.Session()
session.trust_env = False
session.headers = {
    'referer': 'https://www.chanmama.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'cookie': cookie
}

url = 'https://api-service.chanmama.com/v5/shop/detail/products?brand_code=&bring_way=0&shop_id=CDirgbaB&big_promotion=0&max_price=-1&min_price=-1&start_time=2026-03-04&end_time=2026-03-04&keyword=&category_id=-1&page=1&size=20&sort=amount&is_new_corp=0&has_ad=0&cal_days_30_volume_trend=1&order_by=desc'

response = session.get(url, timeout=15, proxies={'http': None, 'https': None})
resp_json = response.json()

if resp_json.get('data') and resp_json['data'].get('data'):
    encrypted_data = resp_json['data']['data']
    key = JIEMI_KEY.encode('utf8')
    data = base64.b64decode(encrypted_data)
    cipher = AES.new(key, AES.MODE_ECB)
    text_decrypted = unpad(cipher.decrypt(data))
    decrypted = gzip.decompress(text_decrypted)
    result = json.loads(decrypted)
    
    for item in result.get('list', [])[:2]:
        print("=" * 50)
        print(f"商品: {item.get('title')}")
        print(f"volume: {item.get('volume')}")
        print(f"amount: {item.get('amount')}")
        print(f"amount_text: {item.get('amount_text')}")
        print(f"volume_text: {item.get('volume_text')}")
        print(f"live_volume: {item.get('live_volume')}")
        print(f"live_amount: {item.get('live_amount')}")
        print(f"days_30_volume_trend: {item.get('days_30_volume_trend')}")
        print(f"author_count: {item.get('author_count')}")
        print(f"live_count: {item.get('live_count')}")
        print(f"aweme_count: {item.get('aweme_count')}")
