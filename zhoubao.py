# -*- coding: utf-8 -*-
# @Time    : 2024/6/11 21:14
# @Author  : Git_LIN
# @File    : 周报2.py
# @Software: PyCharm
import urllib.parse
from Crypto.Cipher import AES
import base64, gzip
import requests
import datetime
from loguru import logger
from feapder.db.mysqldb import MysqlDB
import json
import time, hashlib
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd
from sqlalchemy import create_engine
import schedule
import os
import glob
from openai import OpenAI
import shutil




# 配置MySQL连接信息
config = {
    'user': 'ods_db_rw',
    'password': 'D2HHbhvKaKhTrJY_',
    'host': 'rm-2zeu203819gye26cg.mysql.rds.aliyuncs.com',
    'database': 'ods_db'
}

# 数据库
ip="rm-2zeu203819gye26cg.mysql.rds.aliyuncs.com"
port=3306
db="ods_db"
user_name="ods_db_rw"
user_pass="D2HHbhvKaKhTrJY_"
mysql_cli = MysqlDB(ip="127.0.0.1", port=3306, db="linshuai", user_name="root", user_pass="123456")
# mysql_cli = MysqlDB(ip=ip, port=port, db=db, user_name=user_name, user_pass=user_pass)

def save_Mysql(data: dict, table: str) -> None:
    """存储到数据库"""
    if not isinstance(data, dict):
        return logger.error('数据格式有问题{}'.format(type(data)))
    # if not redis_cli.sadd(table, md5(str(data).encode('utf-8')).hexdigest()):
    #     return
    if mysql_cli.add_smart(table, data, auto_update=True):
        return logger.info(f'{data}--{table}写入成功')

login_num = 0
# 登录
def login(user="18210790624", pwd="newcode0402"):
    global login_num
    print(f'当前登录账号：{user}')
    print(f'当前第{login_num}次登录')
    login_num += 1
    if login_num == 5:
        time.sleep(300000)
    try:
        with requests.session() as session:
            session.headers = {
                'referer': 'https://www.chanmama.com/login',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
            }
            data = {"appid": 10000, "grant_type": "password", "mobile": user,
                    "password": hashlib.md5(pwd.encode("utf-8")).hexdigest(), "device": "PC"}
            resp = session.post(url="https://passport.chanmama.com/v2/cas/authorize", json=data, timeout=15)
            resp_json = resp.json()
            data = {"from_platform": None, "appId": 10000, "timeStamp": resp_json["data"]["expire_time"],
                    "token": resp_json["data"]["token"], "grant_type": "cas"}
            resp = session.post(url="https://api-service.chanmama.com/v1/access/token", json=data, timeout=15)
            resp_json = resp.json()
            logger.info(f"登陆成功!")
            token = resp_json["data"]["token"]
            session.headers.update({"cookie": f'LOGIN-TOKEN-FORSNS={token}'})
            return session.headers
    except Exception as e:
        logger.error(f"登录异常:{e}")
        time.sleep(300)

payload = {}

# 日期
def get_FormatTime(timestamp):
    """
    格式化时间戳
    :param timestamp: 时间戳
    :return:
    """
    local_time = time.localtime(timestamp)
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    return formatTime

def get_time_str(num):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=num)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    return yesterday_str


# 解密
BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def aesEncrypt(key, data):
    '''
    AES的ECB模式加密方法
    :param key: 密钥
    :param data:被加密字符串（明文）
    :return:密文
    '''
    key = key.encode('utf8')
    # 字符串补位
    data = pad(data)
    cipher = AES.new(key, AES.MODE_ECB)
    # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
    result = cipher.encrypt(data.encode())
    encodestrs = base64.b64encode(result)
    enctext = encodestrs.decode('utf8')
    # print(enctext)
    return enctext

def aesDecrypt(key, data):
    '''

    :param key: 密钥
    :param data: 加密后的数据（密文）
    :return:明文
    '''
    key = key.encode('utf8')
    data = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_ECB)

    # 去补位
    text_decrypted = unpad(cipher.decrypt(data))
    # text_decrypted = text_decrypted.decode('utf8')
    # print(text_decrypted)
    return gzip.decompress(text_decrypted)

jiemi_key = 'cmmgfgehahweuuii'



# 定义一个函数来处理每个部分
def convert(part):
    if 'w' in part:
        return float(part.replace('w', '')) * 10000
    else:
        return float(part)

# 对两个部分分别进行处理并计算平均值
# result = sum(convert(part) for part in parts) / 2
#
# print(result)

# 小店商品分析"1000w~2500w"
def shangpin_fenxi(jinp,shop_id,shop_name,start_time,end_time,type_num,headers,num_type):
    print("==========小店商品分析===========")
    if type_num == 1:  # 全部分类
        page = 1
        time.sleep(2)
        while True:
            time.sleep(1)
            shangpin_quanbu_url = f'https://api-service.chanmama.com/v5/shop/detail/products?brand_code=&bring_way=0&shop_id={shop_id}&big_promotion=0&max_price=-1&min_price=-1&start_time={start_time}&end_time={end_time}&keyword=&category_id=-1&page={page}&size=20&sort=amount&is_new_corp=0&has_ad=0&cal_days_30_volume_trend=1&order_by=desc'

            # print(shangpin_quanbu_url)
            zhibo_response = requests.request("GET", shangpin_quanbu_url, headers=headers, data=payload).json()
            print(zhibo_response)
            data = zhibo_response.get("data").get("data")
            result = aesDecrypt(jiemi_key, str(data))
            # print(result)
            data_list = json.loads(result).get("list")
            if data_list:
                page += 1
                for data in data_list:
                    item = {}
                    # print(data)
                    item['竞品'] = jinp
                    item['shop_id'] = shop_id  # 店铺id
                    item['quchong'] = f'{shop_id}{start_time}{data.get("product_id")}'  # 去重
                    item['shop_name'] = shop_name  # 店铺名字
                    item['start_time'] = start_time  # 获取得起始时间
                    item['end_time'] = end_time  # 获取结束始时间
                    item["Catgeorys_name"] = "全部"  # 分类
                    item["max_commission_rate"] = f"{data.get('max_commission_rate')}%"  # 佣金
                    item["product_id"] = data.get("product_id")  # 商品id
                    item["title"] = data.get("title")  # 商品名字
                    item["brand_name"] = data.get("brand_name")  # 品牌名字

                    if num_type == 1:
                        # 有数值版本
                        item["price"] = data.get("sku_union_price_text")  # 价格
                        item["volume"] = data.get("volume")  # 销量
                        item["amount"] = data.get("amount")  # 销售额
                    if num_type == 2:
                        # 应对无数值版本
                        days_30_volume_trend = data.get("days_30_volume_trend")
                        for days_30 in days_30_volume_trend:
                            if days_30.get('time_node_str') == start_time:
                                item["volume"] = days_30.get('volume')  # 销量
                        item["amount"] = '' # data.get("amount_text")  # 销售额
                        item["price"] = ''
                        # 应对无数值版本

                    item["author_count"] = data.get("author_count")  # 关联达人
                    item["live_count"] = data.get("live_count")  # 关联直播
                    item["aweme_count"] = data.get("aweme_count")  # 关联视频
                    item["shangpin_url"] = f'https://www.chanmama.com/promotionDetail/{data.get("product_id")}'  # 蝉妈妈商品url
                    item["update_at"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 更新时间
                    item["shangp_shop_id"] = data.get("shop_id")  # 关联达人
                    item["shangp_shop_name"] = data.get("shop_name")  # 关联达人
                    item["shangp_brand_name"] = data.get("brand_name")  # 关联达人
                    save_Mysql(item, 'zb_zhoubo')
            if not data_list or len(data_list) < 20:
                print(f"数据抓取完毕")
                break


# 定义查询和导出函数
def query_and_export(shop_ids, name, time_str,time_str2):
    # 创建数据库连接
    # cnx = mysql.connector.connect(**config)
    cnx = create_engine('mysql://root:123456@127.0.0.1/linshuai')
    # query1 = f"SELECT * FROM zb_zhoubao WHERE 竞品 IN {tuple(shop_ids)} AND start_date BETWEEN '2024-04-18' AND '2024-05-02';"
    query1 = f"SELECT * FROM zb_zhoubo WHERE 竞品 IN {tuple(shop_ids)} AND start_time BETWEEN '{time_str}' AND '{time_str2}';"

    print(query1)
    df1 = pd.read_sql(query1, cnx)

    # 将两个DataFrame写入Excel文件的不同工作表中。
    with pd.ExcelWriter(f'C:\\Users\\Admin\\Desktop\\日报数据\\{name}.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1',index=False)


def get_time_str_kaiguan(days):
    yesterday = datetime.datetime.now() + datetime.timedelta(days=days)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    return yesterday_str

def pp(num_type):
    import os
    import pandas as pd

    # 获取指定目录下所有xlsx文件名
    def get_excel_files(path):
        files = [f for f in os.listdir(path) if f.endswith('.xlsx')]
        return files

    november_files = get_excel_files('C:\\Users\Admin\Desktop\\日报数据')  # 日报数据
    october_files = get_excel_files('C:\\Users\Admin\Desktop\\打了标的数据')  # 有打标记录的数据

    november_files_name = 'C:\\Users\Admin\Desktop\\日报数据'  # 日报数据
    october_files_name = 'C:\\Users\Admin\Desktop\\打了标的数据'  # 有打标记录的数据
    for nov_file in november_files:
        # 模糊匹配对应十一月份和十月份excel名称
        for oct_file in october_files:
            if oct_file.split('.')[0] in nov_file:
                if oct_file.split('.')[0] == '有道':
                    print('进入有道专属解析')
                    print(nov_file)
                    print(oct_file)
                    # 读取两个匹配的Excel文件
                    df1 = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
                    df2 = pd.read_excel(os.path.join(october_files_name, oct_file), sheet_name='Sheet1')

                    # 循环数据进行匹配
                    for index, row in df1.iterrows():
                        value1 = row[8]  # 日报数据取下标8
                        matched_rows = df2[df2.iloc[:, 11] == value1]  # 打了标的数据取下标11
                        if not matched_rows.empty:
                            matched_row = matched_rows.iloc[0]
                            # 取打了标的数据的下标14.15.16.17.18.19.20的数据新增到日报数据该行的后面
                            df1.loc[index, '产品形态一'] = matched_row[14]
                            df1.loc[index, '产品形态二'] = matched_row[15]
                            df1.loc[index, '产品形态三'] = matched_row[16]
                            df1.loc[index, '是否新品'] = matched_row[17]
                            df1.loc[index, '周期'] = ''
                            df1.loc[index, 'GMV（万元）'] = ''
                            df1.loc[index, '月份'] = ''
                            df1.loc[index, '附加标签'] = matched_row[21]
                elif oct_file.split('.')[0] == '新东方':
                    print('进入新东方专属解析')
                    print(nov_file)
                    print(oct_file)
                    # 读取两个匹配的Excel文件
                    df1 = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
                    df2 = pd.read_excel(os.path.join(october_files_name, oct_file), sheet_name='Sheet1')

                    # 循环数据进行匹配
                    for index, row in df1.iterrows():
                        value1 = row[8]  # 日报数据取下标8
                        matched_rows = df2[df2.iloc[:, 11] == value1]  # 打了标的数据取下标11
                        if not matched_rows.empty:
                            matched_row = matched_rows.iloc[0]
                            # 取打了标的数据的下标14.15.16.17.18.19.20的数据新增到日报数据该行的后面
                            # 学段一	产品形态一	产品形态二	产品形态三	产品形态四	学段二	科目	GMV（万元）	月份	数据周期	周期
                            df1.loc[index, '学段一'] = matched_row[14]
                            df1.loc[index, '科目'] = matched_row[20]
                            df1.loc[index, '产品形态一'] = matched_row[15]
                            df1.loc[index, '产品形态二'] = matched_row[16]
                            df1.loc[index, '产品形态三'] = matched_row[17]
                            df1.loc[index, '产品形态四'] = matched_row[18]
                            df1.loc[index, '学段二'] = matched_row[19]
                            df1.loc[index, 'GMV（万元）'] = ''
                            df1.loc[index, '月份'] = ''
                            df1.loc[index, '数据周期'] = ''
                            df1.loc[index, '周期'] = ''
                elif oct_file.split('.')[0] == '希望学':
                    print('进入希望学专属解析')
                    print(nov_file)
                    print(oct_file)
                    # 读取两个匹配的Excel文件
                    df1 = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
                    df2 = pd.read_excel(os.path.join(october_files_name, oct_file), sheet_name='Sheet1')

                    # 循环数据进行匹配
                    for index, row in df1.iterrows():
                        value1 = row[8]  # 日报数据取下标8
                        matched_rows = df2[df2.iloc[:, 11] == value1]  # 打了标的数据取下标11
                        if not matched_rows.empty:
                            matched_row = matched_rows.iloc[0]
                            # 取打了标的数据的下标14.15.16.17.18.19.20的数据新增到日报数据该行的后面
                            # 学段一	产品形态一	产品形态二	产品形态三	产品形态四	学段二	科目	GMV（万元）	月份	数据周期	周期
                            df1.loc[index, '学段'] = matched_row[14]
                            df1.loc[index, '产品形态一'] = matched_row[15]
                            df1.loc[index, '产品形态二'] = matched_row[16]
                            df1.loc[index, '产品形态三'] = matched_row[17]
                            df1.loc[index, 'SKU'] = matched_row[18]
                            df1.loc[index, '学科'] = matched_row[19]
                            df1.loc[index, 'GMV（万元）'] = ''
                            df1.loc[index, '月份'] = ''
                            df1.loc[index, '日期'] = ''
                            df1.loc[index, '周期'] = ''
                            df1.loc[index, '备注'] = ''
                elif oct_file.split('.')[0] == '叫叫' or oct_file.split('.')[0] == '豆神' or oct_file.split('.')[0] == '陈心' or oct_file.split('.')[0] == '雪梨'  or oct_file.split('.')[0] == 'sam' or oct_file.split('.')[0] == '毛毛虫' or oct_file.split('.')[0] == '潘潘' or oct_file.split('.')[0] == '平行线' or oct_file.split('.')[0] == '小学数学张老师' or oct_file.split('.')[0] == '杨妈英语思维' or oct_file.split('.')[0] == '晓晶老师语文':
                    print('进入叫叫/豆神/陈心/雪梨/sam/潘潘/平行线/毛毛虫/杨妈英语思维/小学数学张老师/杨妈英语思维/晓晶老师语文 的专属解析')
                    print(nov_file)
                    print(oct_file)
                    # 读取两个匹配的Excel文件
                    df1 = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
                    df2 = pd.read_excel(os.path.join(october_files_name, oct_file), sheet_name='Sheet1')

                    # 循环数据进行匹配
                    for index, row in df1.iterrows():
                        value1 = row[8]  # 日报数据取下标8
                        matched_rows = df2[df2.iloc[:, 11] == value1]  # 打了标的数据取下标11
                        if not matched_rows.empty:
                            matched_row = matched_rows.iloc[0]
                            # 取打了标的数据的下标14.15.16.17.18.19.20的数据新增到日报数据该行的后面
                            # 学段一	产品形态一	产品形态二	产品形态三	产品形态四	学段二	科目	GMV（万元）	月份	数据周期	周期
                            # df1.loc[index, '学段'] = matched_row[14]
                            df1.loc[index, '产品形态一'] = matched_row[14]
                            df1.loc[index, '产品形态二'] = matched_row[15]
                            df1.loc[index, '产品形态三'] = matched_row[16]
                            df1.loc[index, '产品形态四'] = matched_row[17]
                
                elif oct_file.split('.')[0] == '高途' or oct_file.split('.')[0] == '猿辅导' or oct_file.split('.')[0] == '作业帮':
                    print('进入高途和猿辅导专属解析')
                    print(nov_file)
                    print(oct_file)
                    # 读取两个匹配的Excel文件
                    df1 = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
                    df2 = pd.read_excel(os.path.join(october_files_name, oct_file), sheet_name='Sheet1')

                    # 循环数据进行匹配
                    for index, row in df1.iterrows():
                        value1 = row[8]  # 日报数据取下标8
                        matched_rows = df2[df2.iloc[:, 11] == value1]  # 打了标的数据取下标11
                        if not matched_rows.empty:
                            matched_row = matched_rows.iloc[0]
                            # 取打了标的数据的下标14.15.16.17.18.19.20的数据新增到日报数据该行的后面
                            df1.loc[index, '产品形态一'] = matched_row[14]
                            df1.loc[index, '产品形态二'] = matched_row[15]
                            df1.loc[index, '产品形态三'] = matched_row[16]
                            df1.loc[index, '是否新品'] = matched_row[17]
                            df1.loc[index, '周期'] = ''
                            df1.loc[index, 'GMV（万元）'] = ''
                            df1.loc[index, '学段'] = matched_row[22]
                            df1.loc[index, '学科'] = matched_row[23]
                            df1.loc[index, '正中低价'] = matched_row[24]
                            # df1.loc[index, '附加标签'] = matched_row[21]
                else:
                    print('进入其它解析')
                    print(nov_file)
                    print(oct_file)
                    # 读取两个匹配的Excel文件
                    df1 = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
                    df2 = pd.read_excel(os.path.join(october_files_name, oct_file), sheet_name='Sheet1')

                    # 循环数据进行匹配
                    for index, row in df1.iterrows():
                        value1 = row[8]  # 日报数据取下标8
                        matched_rows = df2[df2.iloc[:, 11] == value1]  # 打了标的数据取下标11
                        if not matched_rows.empty:
                            matched_row = matched_rows.iloc[0]
                            # 取打了标的数据的下标14.15.16.17.18.19.20的数据新增到日报数据该行的后面
                            df1.loc[index, '产品形态一'] = matched_row[14]
                            df1.loc[index, '产品形态二'] = matched_row[15]
                            df1.loc[index, '产品形态三'] = matched_row[16]
                            df1.loc[index, '是否新品'] = matched_row[17]
                            df1.loc[index, '周期'] = ''
                            df1.loc[index, 'GMV（万元）'] = ''
                            df1.loc[index, '学段'] = matched_row[20]
                            # df1.loc[index, '学科'] = matched_row[21]
                            # df1.loc[index, '中低价'] = matched_row[22]
                            # df1.loc[index, '附加标签'] = matched_row[21]

                # 保存修改后的Excel文件
                df1.to_excel(os.path.join(november_files_name, nov_file), index=False)

    if num_type == 2:
        # 二次匹配价格===================================================
        # 定义文件路径
        data_folder = r'C:\Users\Admin\Desktop\日报数据'
        target_file_path = r'C:\Users\Admin\Desktop\价格匹配.xlsx'

        # 读取目标文件的数据
        target_df = pd.read_excel(target_file_path)

        # 遍历日报数据文件夹下的所有xlsx文件
        for file_name in os.listdir(data_folder):
            if file_name.endswith('.xlsx'):
                file_path = os.path.join(data_folder, file_name)

                # 读取日报数据文件的数据
                daily_df = pd.read_excel(file_path)

                # 匹配并更新数据
                for i in range(len(daily_df)):
                    for j in range(len(target_df)):
                        if daily_df.iloc[i, 8] == target_df.iloc[j, 8]:
                            daily_df.iloc[i, 11] = target_df.iloc[j, 11]
                            daily_df.iloc[i, 13] = daily_df.iloc[i, 11] * daily_df.iloc[i, 12]

                # 保存更新后的日报数据文件
                daily_df.to_excel(file_path, index=False)

        print("数据处理完成。")


# ====================== 配置区域 ======================

DEEPSEEK_API_KEY = "sk-17b8tiEVcC3ChOGiJmeXK00ofms1p4cWMGmVW55cuydzuQeD"  # 替换为你的DeepSeek API密钥
# EXCEL_PATH = "C:\\Users\\Admin\\Desktop\\测试\\作业帮2025-02-17数据.xlsx"  # Excel文件路径
SHEET_NAME = "Sheet1"  # 工作表名称
TEXT_COLUMN = "title"  # 需要分析的文本列名
price = "price"
RESULT_COLUMN0_all = "产品形态一"

# Deepseek-chat 就是V3
# Deepseek-reasoner  就是R1

# 获取指定目录下所有xlsx文件名
def get_excel_files(path):
    files = [f for f in os.listdir(path) if f.endswith('.xlsx')]
    return files

# ======================================================

def call_deepseek_api(text,price,pinpai):
    """调用DeepSeek API的示例函数（需根据实际API文档修改）"""
    client = OpenAI(api_key="sk-17b8tiEVcC3ChOGiJmeXK00ofms1p4cWMGmVW55cuydzuQeD",
                    base_url="https://tbnx.plus7.plus/v1")
    if '猿辅导' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 猿辅导
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，"
                            # f"匹配规则时请注意：“和”与“或”的区别：“和”表示所有条件必须同时满足。例如规则“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“猿辅导”和“超级新概念” ，且价格0<ASP<100，就打标为：课类-素养课-小猿超级新概念leads。2. 商品名称包含“自然拼读”和“绘本阅读” ，且价格0<ASP<100，就打标为：课类-素养课-小猿双语阅读leads。3. 商品名称包含“新考法名师带学”，且价格0<ASP<100，就打标为：课类-素养课-小猿新思维leads。4. 商品名称包含“海豚AI学”，且价格0<ASP<100，就打标为：课类-海豚AI课类leads。5. 商品名称包含“斑马AI学”和“口语+思维”，且价格0<ASP<100，就打标为：课类-斑马课类leads。6. 商品名称包含“思维系统版幼儿早教启蒙” ，且价格1000<ASP<10000，就打标为：课类-斑马正价。7. 商品名称包含“猿编程”和“c++”，且价格100<ASP<5000  ，就打标为：课类-编程-正价-c++。8. 商品名称包含“猿编程” ，且价格25<ASP<100，就打标为：课类-编程-29leads。9. 商品名称包含“猿编程” ，且价格0<ASP<20.8，就打标为：课类-编程-10.8leads。10.商品名称包含“斑马”和“百科”，且价格100<ASP<3000  ，就打标为：百科-百科中价。11.商品名称包含“斑马”和“主题”但不包含“题卡”，且价格100<ASP<3000  ，就打标为：百科-百科中价。12.商品名称包含“猿辅导”和“奥数”，且价格100<ASP<1000  ，就打标为：图书-奥数。13.商品名称包含“冲优一本通”或“小学一本通新学期同步原型题”，且价格0<ASP<100，就打标为：图书-冲优一本通。14.商品名称包含“初中线上重难点特训营”或“初中提分攻略” ，且价格0<ASP<100，就打标为：图书-初中重难点特训营。15.商品名称包含“高中重难点必备”或“高中高分必备”，且价格0<ASP<100，就打标为：图书-高中重难点特训营。16.商品名称包含“公式写作文”和“学阅读” ，且价格0<ASP<100，就打标为：图书-公式作文+阅读。17.商品名称包含“小学语数英寒假一本通”，且价格0<ASP<100，就打标为：图书-寒假一本通。18.商品名称包含“数学题型词典” ，且价格0<ASP<100，就打标为：图书-满分之路。19.商品名称包含“名师大招”，且价格100<ASP<500   ，就打标为：图书-名师大招。20.商品名称包含“名师一本通”，且价格0<ASP<100，就打标为：图书-名师一本通。21.商品名称包含“斑马幼小衔接”或“斑马英语”或“斑马思维训练” ，且价格0<ASP<500，就打标为：图书-图书。22.商品名称包含“小学数学附加题易错题”，且价格0<ASP<100，就打标为：图书-小学附加题易错题。23.商品名称包含“图解小学数学” ，且价格0<ASP<100，就打标为：图书-校内-图解小学数学。24.商品名称包含“中考高频易错题”，且价格0<ASP<100，就打标为：图书-校内-中考高频易错题。25.商品名称包含“点透小古文古诗词”，且价格0<ASP<100，就打标为：图书-校内-点透古诗词。26.商品名称包含“秒解”，且价格0<ASP<100，就打标为：图书-校内-秒解。27.商品名称包含“趣系列一站式幼小衔接”，且价格100<ASP<400   ，就打标为：图书-校内-趣系列盒子。28.商品名称包含“速记小学英语” ，且价格0<ASP<100，就打标为：图书-校内-速记小学英语。29.商品名称包含“万能音标”，且价格0<ASP<100，就打标为：图书-校内-万能音标。30.商品名称包含“阅读写作作文素材”，且价格0<ASP<100，就打标为：图书-校内-我们的语文。31.商品名称包含“学习秘籍”，且价格0<ASP<100，就打标为：图书-校内-学习秘籍。32.商品名称包含“口算题卡”，且价格0<ASP<100，就打标为：引流。33.商品名称包含“秒记初中高频考点”，且价格ASP<1000，就打标为：图书-校内-秒记初中高频考点。34.商品名称包含“斑马”和“百科”，且价格0<ASP<100，就打标为：百科-百科leads。35.商品名称包含“手把手教你写出考场一类文”，且价格ASP>10，就打标为：课类-手把手教你写出考场一类文。36.商品名称包含“自然拼读学习手册”，且价格ASP<10，就打标为：图书-校内-自然拼读密码。37.商品名称包含“斑马”和“儿歌”，且价格ASP<10，就打标为：其它。38.商品名称包含“猿辅导”和“中考高频易错题”，且价格ASP<10，就打标为：图书-校内-中考高频易错题。39.商品名称包含“猿辅导”和“小学高频易错题”，且价格ASP<10，就打标为：图书-校内-小学高频易错题。40.商品名称包含“猿辅导”和“万能音标”，且价格ASP<10，就打标为：图书-校内-万能音标。41.商品名称包含“斑马思维机”，且价格0<ASP<100，就打标为：其它。42.商品名称包含“看动画学数学” ，且价格0<ASP<100，就打标为：课类-海豚AI课类leads。43.商品名称包含“斑马AI学”和“英语+思维”，且价格0<ASP<100，就打标为：课类-斑马课类leads。44.商品名称包含“斑马思维训练6+1”，且价格0<ASP<100，就打标为：图书-图书。44.商品名称包含“斑马数学分级绘本”，且价格0<ASP<100，就打标为：图书-图书。45.商品名称包含“斑马AI”和“英语+思维”，且价格ASP>1000，就打标为：课类-斑马正价-英语+思维。46.商品名称包含“猿编程”和“C1Python” ，且价格100<ASP<5000  ，就打标为：课类-编程-正价-C1Python。47.商品名称包含“5天数学动画吃透”，且价格0<ASP<100，就打标为：课类-海豚AI课类leads。48.商品名称包含“北大哈哈”或“高中数学高分实战”，且价格0<ASP<100，就打标为：图书-高中数学高分实战。49.商品名称包含“英语高分实战” ，且价格0<ASP<100，就打标为：图书-高考英语高分实战。50.商品名称包含“高中搞懂命题人” ，且价格0<ASP<100，就打标为：图书-高中重难点特训营。51.商品名称包含“当堂写出满分作文” ，且价格0<ASP<100，就打标为：课类-30天当堂写出满分作文。52.商品名称包含“斑马AI”和“英语”和“动画”，且价格0<ASP<30，就打标为：课类-英语AI启蒙动画。"
                            f"匹配规则时请注意：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如规则“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},


            ],
            stream=False
        )


    elif '叫叫' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 作业帮
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“叫叫优选思维”和“美育”和“小作家”，且价格1500<ASP<2500 ，就打标为：幼小-多科-正价。2. 商品名称包含“一整年不需要买书叫叫阅读分阶培养”，且价格1500<ASP<1800 ，就打标为：幼小-阅读-正价。3. 商品名称包含“叫叫阅读5日进阶”，且价格0<ASP<100，就打标为：幼小-阅读-leads-9.9元-5日体验。4. 商品名称包含“叫叫阅读双周飞跃”，且价格0<ASP<100，就打标为：幼小-阅读-leads-15.9元双周体验。5. 商品名称包含“8天巩固小学3项基本功”，且价格0<ASP<100，就打标为：幼小-阅读-leads-19.9元8天leads。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述,包括“打标结果：”这个几个字也不要出现"},

            ],
            stream=False
        )

    elif '豆神' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 豆神
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“文言文系列”或“文言文精讲”，且价格2500<ASP<3800 ，就打标为：课类-正价-文言文一课通。2. 商品名称包含“小王者”和“乐死人的文学史”，且价格1000<ASP<10000，就打标为：课类-正价-底阅作突破正价。3. 商品名称包含“豆L系列”或“新L系列” ，且价格700<ASP<7000  ，就打标为：课类-正价-豆伴匠L。4. 商品名称包含“豆R系列”或“豆粉R”，且价格3000<ASP<11000，就打标为：课类-正价-豆伴匠R。5. 商品名称包含“底阅作” ，且价格ASP<90，就打标为：课类-leads-底阅作突破系列。6. 商品名称包含“底阅作” ，且价格ASP>1000，就打标为：课类-正价-底阅作突破正价。7. 商品名称包含“快解”，且价格ASP<1000，就打标为：课类-leads-快解。8. 商品名称包含“写作提分宝盒” ，且价格ASP<50，就打标为：课类-leads-写作宝盒。9. 商品名称包含“豆神小王者5日读写”，且价格0<ASP<100，就打标为：课类-leads-小王者5日读写。10.商品名称包含“阅写全面提升” ，且价格100<ASP<1000  ，就打标为：课类-leads-阅写全面提升。11.商品名称包含“十二本名著”，且价格100<ASP<500   ，就打标为：课类-leads-十二本。12.商品名称包含“妙趣文史阅写” ，且价格0<ASP<100，就打标为：课类-leads-妙趣文史阅写。13.商品名称包含“摘抄本”或“笔记本”，且价格ASP<10，就打标为：其它-引流。14.商品名称包含“语文应该怎么学”，且价格ASP<10，就打标为：其它-图书-语文怎么学。15.商品名称包含“乐死人的文学史”，且价格ASP<1000，就打标为：其它-图书-乐死人的文学史。16.商品名称包含“写作提分”，且价格ASP<10，就打标为：课类-leads-写作提分。17.商品名称包含“小王者”和“乐死人的文学史”和“48次”，且价格1000<ASP<10000，就打标为：课类-正价-底阅作突破正价。18.商品名称包含“豆神读写特训”，且价格ASP<100，就打标为：课类-leads-3日读写素养。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )
    elif '有道' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 有道
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“有道围棋”，且价格3500<ASP<4000 ，就打标为：课类-正价-有道围棋。2. 商品名称包含“有道开口读自拼阅读”，且价格1000<ASP<1600 ，就打标为：课类-正价-有道开口读。3. 商品名称包含“有道小图灵编程”，且价格4500<ASP<7000 ，就打标为：课类-正价-小图灵编程正价。4. 商品名称包含“有道乐读猫博士”，且价格2500<ASP<4500 ，就打标为：课类-正价-猫博士阅读写作。5. 商品名称包含“原版12人”，且价格5500<ASP<7500 ，就打标为：课类-正价-剑桥原版12人。6. 商品名称包含“有道围棋”或“0基础入门围棋” ，且价格0<ASP<100，就打标为：课类-leads-有道围棋。7. 商品名称包含“编程体验”或“编程训练营”，且价格0<ASP<100，就打标为：课类-leads-小图灵编程体验。8. 商品名称包含“高中家长”，且价格0<ASP<100，就打标为：课类-leads-高中家长训练营。9. 商品名称包含“初升高家长”，且价格0<ASP<100，就打标为：课类-leads-初升高家长讲座。10.商品名称包含“亲子思维亲子塑造礼盒”，且价格100<ASP<300   ，就打标为：书课包-低幼书课包-亲子思维礼盒。11.商品名称包含“包君成小学生必背古诗文” ，且价格0<ASP<100，就打标为：书课包-小初书课包-包君成古诗词启蒙。12.商品名称包含“包君成读写课” ，且价格100<ASP<200   ，就打标为：书课包-小初书课包-包君成读写课。13.商品名称包含“漫画作文”，且价格0<ASP<100，就打标为：书课包-小初书课包-包君成漫画作文。14.商品名称包含“写作能力暴涨秘籍”，且价格0<ASP<100，就打标为：书课包-小初书课包-包君成写作能力暴涨。15.商品名称包含“阅读百日破”，且价格0<ASP<100，就打标为：书课包-小初书课包-包君成阅读百日破。16.商品名称包含“有道初中大题快解公式”，且价格0<ASP<100，就打标为：书课包-小初书课包-初中大题快解公式。17.商品名称包含“全解满分方略” ，且价格0<ASP<100，就打标为：书课包-小初书课包-初中数学\物理全解、码上提分等书课包。18.商品名称包含“基础知识专项盘点”或“小学知识盘点”，且价格0<ASP<100，就打标为：书课包-小初书课包-基础知识专项盘点。19.商品名称包含“猫博士的作文课”，且价格0<ASP<100，就打标为：书课包-小初书课包-猫博士作文课。20.商品名称包含“文言文满分答题公式”，且价格0<ASP<100，就打标为：书课包-小初书课包-文言文满分答题公式。21.商品名称包含“现代文阅读满分答题公式” ，且价格0<ASP<100，就打标为：书课包-小初书课包-现代文满分答题公式。22.商品名称包含“有道领世快捷英语”，且价格0<ASP<100，就打标为：书课包-小初书课包-有道领世快捷英语。23.商品名称包含“小学阅读理解满分答题公式”，且价格0<ASP<100，就打标为：书课包-小初书课包-阅读理解公式。24.商品名称包含“包君成纸上作文”，且价格0<ASP<100，就打标为：书课包-小初书课包-纸上作文直播课。25.商品名称包含“中考作文满分秘籍”，且价格0<ASP<100，就打标为：书课包-小初书课包-中考作文满分秘籍。26.商品名称包含“阅读分级训练” ，且价格0<ASP<100，就打标为：书课包-小初书课包-阅读分级训练。27.商品名称包含“有道领世”和“提分有道” ，且价格0<ASP<100，就打标为：书课包-高中书课包-领世提分有道。28.商品名称包含“名师全归纳”，且价格0<ASP<100，就打标为：书课包-高中书课包-名师归纳。29.商品名称包含“有道名师讲透” ，且价格0<ASP<100，就打标为：书课包-高中书课包-名师讲透。30.商品名称包含“杨亮讲英语”或“杨亮讲解”，且价格0<ASP<100，就打标为：书课包-高中书课包-杨亮英语。31.商品名称包含“小学作文高分必备”或“包君成作文高分技巧”，且价格ASP<10，就打标为：书课包-小学书课包-小学作文高分必备。32.商品名称包含“编程赛考集训营”，且价格ASP<10，就打标为：课类-leads-小图灵编程体验。33.商品名称包含“小班原版阅读” ，且价格ASP>1000，就打标为：课类-正价-剑桥原版小班。34.商品名称包含“北大胡源”和“高中数学” ，且价格ASP<10，就打标为：课类-leads-源哥高中数学。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '高途' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 高途
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“创新数感思维训练营”，且价格1200<ASP<3300 ，就打标为：课类-正价-创新思维训练营。2. 商品名称包含“浩天寒春人文素养”，且价格3400<ASP<3700 ，就打标为：课类-正价-浩天人文素养。3. 商品名称包含“剑桥KET标准教程”，且价格1000<ASP<2300 ，就打标为：课类-正价-刘薇小初英语。4. 商品名称包含“具象思维化学规划包”，且价格0<ASP<100，就打标为：课类-中价-曹忆初中化学。5. 商品名称包含“高中数学满分攻略”，且价格100<ASP<1000  ，就打标为：课类-中价-程玲海高中数学。6. 商品名称包含“能量物理《实验红宝书》”和“《题型蓝宝书》”，且价格0<ASP<100，就打标为：课类-中价-冬冬初中物理。7. 商品名称包含“智慧读写特训7日营”，且价格0<ASP<100，就打标为：课类-中价-浩天人文素养。8. 商品名称包含“老范亲授340词汇”，且价格100<ASP<500   ，就打标为：课类-中价-老范初高中作文。9. 商品名称包含“满分黑科技”，且价格0<ASP<100，就打标为：课类-中价-老许初中语文。10.商品名称包含“剑桥KET入门1节中教” ，且价格100<ASP<200   ，就打标为：课类-中价-刘薇小学英语。11.商品名称包含“麻辣思维”，且价格0<ASP<100，就打标为：课类-中价-麻辣思维小学数学。12.商品名称包含“马总”，且价格0<ASP<100，就打标为：课类-中价-马总高中化学。13.商品名称包含“孟帝”，且价格0<ASP<100，就打标为：课类-中价-孟帝初中数学。14.商品名称包含“语文满分大通关”或“满分大通关”或“满分语文大通关”，且价格100<ASP<400   ，就打标为：课类-中价-木木老师小初语文。15.商品名称包含“文言文提高营” ，且价格100<ASP<1000  ，就打标为：课类-中价-清清老师高中语文。16.商品名称包含“赛赛老师”，且价格100<ASP<400   ，就打标为：课类-中价-赛赛初中英语。17.商品名称包含“汐子”，且价格0<ASP<100，就打标为：课类-中价-汐子初中英语。18.商品名称包含“小艺”，且价格0<ASP<100，就打标为：课类-中价-小艺高中英语。19.商品名称包含“侯老师”和“数学”，且价格0<ASP<100，就打标为：课类-中价-侯老师数学一招制胜。20.商品名称包含“峥峥”，且价格100<ASP<400   ，就打标为：课类-中价-峥峥初中语文。21.商品名称包含“《满分英语一本通》+《词汇宝典》”，且价格0<ASP<100，就打标为：课类-低价-毕玉琦初中英语。22.商品名称包含“曹忆”，且价格0<ASP<100，就打标为：课类-低价-曹忆初中化学。23.商品名称包含“春春”，且价格0<ASP<100，就打标为：课类-低价春春高中语文。24.商品名称包含“大胜物理”，且价格0<ASP<100，就打标为：课类-低价-大胜初中物理。25.商品名称包含“能量物理《实验红宝书》”和“《题型蓝宝书》”，且价格0<ASP<100，就打标为：课类-中价-冬冬初中物理（上面有一个这个删掉吧）。26.商品名称包含“成人单词速记”或“用耳朵学英语”或“沉浸式口语体验”或“成人英语”或“真人外教一对一”，且价格0<ASP<300，就打标为：课类-低价-菲教1V1/情景生活口语/治愈系英语等。27.商品名称包含“佳文物理”，且价格0<ASP<100，就打标为：课类-低价-佳文老师初中物理。28.商品名称包含“语文满分黑科技”，且价格0<ASP<100，就打标为：课类-中价-老许初中语文。29.商品名称包含“剑桥KET”，且价格0<ASP<100，就打标为：课类-低价-刘薇小学英语。30.商品名称包含“妮妮高效学习手册”，且价格0<ASP<100，就打标为：课类-低价-其它初中IP。31.商品名称包含“清清老师”，且价格0<ASP<100，就打标为：课类-低价-清清老师高中语文。32.商品名称包含“《3、2、1，开窍！》” ，且价格0<ASP<100，就打标为：课类-低价-施佳辰初中数学。33.商品名称包含“汤哥”或“北大汤哥”，且价格0<ASP<100，就打标为：课类-低价-汤老师高中数学。34.商品名称包含“王冰”，且价格0<ASP<100，就打标为：课类-中价-王冰初中英语。35.商品名称包含“状元笔记”，且价格0<ASP<100，就打标为：课类-低价-小学数学状元笔记。36.商品名称包含“小阶必备数学知识点-数理思维一本通”或“数学思维一本通” ，且价格0<ASP<100，就打标为：课类-低价-杨易小学数学。37.商品名称包含“初中物化一本通”，且价格0<ASP<100，就打标为：课类-低价-张立琛初中物化。38.商品名称包含“朱博士”或“高中英语”，且价格0<ASP<100，就打标为：课类-低价-朱博士高中英语。39.商品名称包含“北大杰哥”，且价格ASP<10，就打标为：课类-中价-北大杰哥中考物理。40.商品名称包含“张龙”，且价格ASP<1000，就打标为：课类-中价-张龙初中数学。41.商品名称包含“陈君”，且价格ASP<10，就打标为：课类-中价-陈君小学英语。42.商品名称包含“KET直播课” ，且价格ASP<10，就打标为：课类-低价-剑桥。43.商品名称包含“王冰英语单词” ，且价格ASP<10，就打标为：课类-中价-王冰初中英语。44.商品名称包含“满分数学+满分物理+英语考点一本通”，且价格ASP<10，就打标为：图书-初中。45.商品名称包含“高途”和“高中数学”，且价格ASP<10，就打标为：图书-高中。46.商品名称包含“高考拔高”，且价格ASP<10，就打标为：图书-高中。47.商品名称包含“高中”和“母题训练营”，且价格ASP<10，就打标为：图书-高中。48.商品名称包含“木木”和“文言文”，且价格ASP<1000，就打标为：课类-中价-木木老师小初语文。49.商品名称包含“高中”和“985 211原型题”，且价格ASP<10，就打标为：图书-高中。50.商品名称包含“朱博士”或“初中英语”，且价格0<ASP<100，就打标为：课类-低价-朱博士初中英语。51.商品名称包含“高途高中”，且价格0<ASP<100，就打标为：图书-高中。52.商品名称包含“3、2、1，开窍！”，且价格0<ASP<100，就打标为：课类-低价-施佳辰初中数学。53.商品名称包含“吴彦祖” ，且价格ASP>30，就打标为：课类-中价-菲教1V1/情景生活口语/治愈系英语。54.商品名称包含“初阶好家长规划”，且价格ASP<100，就打标为：图书-初中-初阶好家长规划。55.商品名称包含“高中学业报考指导”，且价格ASP<100，就打标为：图书-高中-高中学业报考指导。56.商品名称包含“7天期末提分营全科特训”，且价格ASP<100，就打标为：课类-低价-曹忆初中化学。57.商品名称包含“周帅满分数学”，且价格ASP<100，就打标为：课类-低价-周帅高中数学。58.商品名称包含“施佳辰”或“思维开窍”，且价格ASP<100，就打标为：课类-低价-施佳辰初中数学。59.商品名称包含“《满分英语一本通》+4天大招方法”，且价格0<ASP<100，就打标为：课类-低价-毕玉琦初中英语。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '作业帮' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 作业帮
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“21天寒假预复习”，且价格ASP<10，就打标为：低价-图书-21天寒假预复习。2. 商品名称包含“45天伴学计划”或“45天百分学堂”，且价格100<ASP<1000  ，就打标为：中价-课类-45天百分学堂。3. 商品名称包含“百分手卡”，且价格100<ASP<1000  ，就打标为：中价-课类-百分手卡。4. 商品名称包含“百分手卡”，且价格ASP<10，就打标为：低价-课类-百分手卡。5. 商品名称包含“帮帮英语”，且价格100<ASP<1000  ，就打标为：中价-课类-帮帮英语。6. 商品名称包含“作业帮“和“编程”，且价格9<ASP<12，就打标为：低价-课类-编程-编程10.8。7. 商品名称包含“作业帮“和“编程”，且价格27<ASP<31，就打标为：低价-课类-编程-编程29。8. 商品名称包含“图形化编程系统班”，且价格ASP>1000，就打标为：正价-课类-编程。9. 商品名称包含“满分笔记”，且价格ASP<10，就打标为：低价-课类-初中IP类-陈杰数学通关。10.商品名称包含“清北之路”，且价格100<ASP<1000  ，就打标为：中价-课类-初中IP类-刘杨清北之路。11.商品名称包含“小学”和“母题大招”，且价格ASP<10，就打标为：低价-图书-大通关-小学大通关。12.商品名称包含“小初”和“母题大招”，且价格ASP<10，就打标为：低价-图书-大通关-小初大通关。13.商品名称包含“预习笔记”，且价格ASP<10，就打标为：低价-图书-大通关-小学大通关。14.商品名称包含“初中”和“大通关”，且价格ASP<10，就打标为：低价-图书-大通关-初中大通关。15.商品名称包含“大招手卡”，且价格ASP<10，就打标为：低价-图书-大招手卡。16.商品名称包含“大招手卡”，且价格100<ASP<1000  ，就打标为：中价-图书-大招手卡。17.商品名称包含“语法魔法书”，且价格ASP<10，就打标为：其它。18.商品名称包含“北大亮哥”，且价格ASP<10，就打标为：低价-课类-高中IP类-北大亮哥英语笔记。19.商品名称包含“何连伟” ，且价格ASP<10，就打标为：低价-课类-高中IP类-老何物理大招。20.商品名称包含“刘天麒” ，且价格ASP<10，就打标为：低价-课类-高中IP类-刘天麒阶梯数学。21.商品名称包含“刘秋龙” ，且价格ASP<10，就打标为：低价-课类-高中IP类-秋龙数学大招。22.商品名称包含“归纳总结”，且价格ASP<10，就打标为：其它。23.商品名称包含“小学数学几何36模型”或“几何48模型”或“几何模型”，且价格ASP<10，就打标为：其它。24.商品名称包含“几何大王”，且价格100<ASP<1000  ，就打标为：其它。25.商品名称包含“速算技巧”或“计算技法” ，且价格ASP<10，就打标为：其它。26.商品名称包含“作业帮”和“看图写话”，且价格ASP<10，就打标为：其它。27.商品名称包含“领跑新初一”，且价格ASP<10，就打标为：其它。28.商品名称包含“大招快解”或“解题模型大招”，且价格ASP<10，就打标为：低价-图书-母题-快解。29.商品名称包含“初中母题大全”或“高中母题大全”，且价格ASP<10，就打标为：低价-图书-母题-母题大全。30.商品名称包含“母题训练”或“母题特训”或“母体全解”，且价格ASP<10，就打标为：低价-图书-母题-母题全解。31.商品名称包含“提分大师”，且价格ASP<10，就打标为：低价-图书-母题-提分大师。32.商品名称包含“提分手卡”，且价格ASP<10，就打标为：低价-图书-母题-提分手卡。33.商品名称包含“重难点专项突破”或“重难点突破”，且价格ASP<10，就打标为：低价-图书-母题-重难点突破。34.商品名称包含“脑图秒记”，且价格ASP<10，就打标为：其它。35.商品名称包含“数学&英语速记”，且价格ASP<10，就打标为：其它。36.商品名称包含“数学笔记”但不包含“推荐”，且价格ASP<10，就打标为：低价-图书-数学笔记。37.商品名称包含“小学语文同步作文”但不包含“63制”，且价格ASP<10，就打标为：其它。38.商品名称包含“同步作文仿写”但不包含“63制”，且价格ASP<10，就打标为：其它。39.商品名称包含“小学图解应用题”或“小学图解数学应用题”或“图解小学数学应用题”，且价格ASP<10，就打标为：其它。40.商品名称包含“物理笔记”但不包含“推荐”，且价格ASP<10，就打标为：低价-图书-物理笔记。41.商品名称包含“铭轩”，且价格ASP<10，就打标为：低价-课类-小学IP类-小张满分数学。42.商品名称包含“小学数学画图法”，且价格ASP<10，就打标为：低价-图书-小学数学画图法。43.商品名称包含“英语笔记”但不包含“北大亮哥” ，且价格ASP<10，就打标为：低价-图书-英语笔记。44.商品名称包含“领跑一年级”，且价格ASP<10，就打标为：其它。45.商品名称包含“作业帮”和“阅读公式法” ，且价格ASP<10，就打标为：其它。46.商品名称包含“作业帮”和“阅读理解公式法”，且价格ASP<10，就打标为：其它。47.商品名称包含“阅读作文文言文初中生知识复习专项训练”，且价格ASP<10，就打标为：其它。48.商品名称包含“知识大盘点”，且价格ASP<10，就打标为：其它。49.商品名称包含“作业帮”和“自然拼读”，且价格ASP<10，就打标为：其它。50.商品名称包含“高频考点”，且价格ASP<10，就打标为：其它。51.商品名称包含“小学数学公式定律速查手册”，且价格ASP<10，就打标为：其它。52.商品名称包含“万能模板”或“语文作文素材万能精选”，且价格ASP<10，就打标为：其它。53.商品名称包含“小学数学易错题”，且价格ASP<10，就打标为：其它。54.商品名称包含“阅读理解公式” ，且价格ASP<10，就打标为：其它。55.商品名称包含“作文公式法”，且价格ASP<10，就打标为：其它。56.商品名称包含“小学1-6年级全套数学解题大招”，且价格ASP<10，就打标为：其它。57.商品名称包含“中考作文套装”或“作业帮全科名师集训+提分笔记”或“语文阅读精准练100篇”或“认识元角分人民币找规律认识钟表”或“智能口算·小学计算大通关”或“小学英语范文大全”或“高中物理模型总结知识点”或“小升初三步复习法”或“作文金句大全”或“名著考点速记&速练”或“词汇学练” ，且价格ASP<10，就打标为：其它。58.商品名称包含“英语拼读法速记单词”，且价格ASP<10，就打标为：其它。59.商品名称包含“真题分类”，且价格ASP<10，就打标为：低价-图书-生物地理会考。60.商品名称包含“基础100讲” ，且价格ASP<10，就打标为：低价-图书-基础100讲。61.商品名称包含“全科名师集训+提分笔记” ，且价格ASP<10，就打标为：低价-图书-全科笔记。62.商品名称包含“生地会考”，且价格ASP<10，就打标为：低价-图书-生地会考。63.商品名称包含“考点一遍过”，且价格ASP<10，就打标为：低价-图书-考点一遍过。64.商品名称包含“小学计算专项” ，且价格ASP<10，就打标为：低价-图书-计算30招。65.商品名称包含“学练机” ，且价格ASP<10，就打标为：其它。66.商品名称包含“自然拼读魔法书”，且价格ASP<10，就打标为：低价-小学IP类-自然拼读魔法书。67.商品名称包含“幼小衔接60天”，且价格ASP<10，就打标为：其它。68.商品名称包含“语文公式法”，且价格ASP<10，就打标为：其它。69.商品名称包含“物理一本通”，且价格ASP<10，就打标为：低价-初中物理一本通。70.商品名称包含“985/211”和“物理笔记”，且价格ASP<100，就打标为：低价-图书-物理笔记。71.商品名称包含“小学期末通关营”，且价格ASP<100，就打标为：低价-图书-大通关-小学大通关。72.商品名称包含“提分王”和“期末冲刺”，且价格ASP<100，就打标为：低价-图书-提分王期末冲刺。73.商品名称包含“母题视频伴读营”，且价格ASP<100，就打标为：低价-图书-母题-提分大师。74.商品名称包含“数学克星”和“初中数学”，且价格ASP<100，就打标为：低价-课类-初中IP类-杜艺波初中数学。75.商品名称包含“全科配套归纳总结”，且价格ASP>1000，就打标为：低价-课类-正价-归纳总结。75.商品名称包含“小学数学全年思维”，且价格ASP>100，就打标为：低价-课类-小学数学思维大师学堂。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程,和任何的其余描述"},

            ],
            stream=False
        )
    elif '新东方' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 新东方
                # {"role": "user",
                #  "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                #             f"价格为【{price}】，"
                #             f"打标规则：1.商品名称包含“100个句子记完2000个”或“100个句子记完1200个”，且价格ASP<100，打标为：K12-英语-课类-低价-100个句子记单词- -小初。2.商品名称包含“100个句子”和“高考”，且价格ASP<100，打标为：K12-英语-课类-低价-100个句子记单词- -高中。3.商品名称包含“百日训练册”，且价格ASP<100，打标为：K12-英语-课类-低价-百日训练册- -低幼。4.商品名称包含“国际音标集训营”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-比邻-国际音标-低幼。5.商品名称包含“核心语法精讲精练”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-比邻-精讲精练-小初。6.商品名称包含“七合一”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-比邻-七合一-小初。7.商品名称包含“六合一”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-比邻-听说六合一-低幼。8.商品名称包含“自然拼读集训营”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-比邻-自然拼读-低幼。9.商品名称包含“自然拼读集训营”，且价格ASP>1000，打标为：K12-英语-课类-正价-比邻-自然拼读-低幼。10.商品名称包含“新东方”和“编程”，且价格ASP<100，打标为：K12-编程-课类-低价-编程- -小初。11.商品名称包含“新东方”和“编程”，且价格100<ASP<1000，打标为：K12-编程-课类-中价-编程- -小初。12.商品名称包含“新东方”和“编程”，且价格ASP>1000，打标为：K12-编程-课类-正价-编程- -小初。13.商品名称包含“超强英语阅读力”，且价格ASP<100，打标为：K12-英语-课类-低价-超强英语阅读力- -小初。14.商品名称包含“超强英语阅读力”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-超强英语阅读力- -小初。15.商品名称包含“初阶知识点精讲”，且价格ASP>1000，打标为：K12-多科-课类-正价-初阶知识点精讲- -初中。16.商品名称包含“高阶知识点精讲”，且价格ASP>1000，打标为：K12-多科-课类-正价-高阶知识点精讲- -高中。17.商品名称包含“寒假数学小班”，且价格ASP>1000，打标为：K12-数学-课类-正价-寒假数学小班- -初中。18.商品名称包含“词汇图解联想记忆法+同步学练测”或“词汇词根+联想记忆法乱序版+学练测”，且价格ASP<100，打标为：K12-英语-课类-低价-词汇+学练测- -小初。19.商品名称包含“高中”和“学练测”，且价格ASP<100，打标为：K12-英语-课类-低价-词汇+学练测- -高中。20.商品名称包含“高中”和“词汇词根+联想记忆法”，且价格40<ASP<100，打标为：K12-英语-课类-低价-词汇+学练测- -高中。21.商品名称包含“写给中国家庭”或“做世界的学生”或“穿越世界的教育寻访”或“我想成为更好的父母”，且价格ASP<100，打标为：K12-家庭教育-课类-低价-家庭教育书- -小初。22.商品名称包含“写给中国家庭”或“做世界的学生”或“穿越世界的教育寻访”或“我想成为更好的父母”，且价格100<ASP<1000，打标为：K12-家庭教育-课类-中价-家庭教育书- -小初。23.商品名称包含“联想巧记速练”，且价格ASP<100，打标为：K12-英语-课类-低价-剑桥类- -小初。24.商品名称包含“考试必备”，且价格ASP<100，打标为：K12-英语-课类-低价-剑桥类- -小初。25.商品名称包含“考试必备”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-剑桥类- -小初。26.商品名称包含“一站式备考”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-剑桥类- -小初。27.商品名称包含“新东方”和“power up”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-剑桥类- -小初。28.商品名称包含“备考通关”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-剑桥类- -小初。29.商品名称包含“一站式备考”，且价格ASP>1000，打标为：K12-英语-课类-正价-剑桥类- -小初。30.商品名称包含“新东方”和“power up”，且价格ASP>1000，打标为：K12-英语-课类-正价-剑桥类- -小初。31.商品名称包含“备考通关”，且价格ASP>1000，打标为：K12-英语-课类-正价-剑桥类- -小初。32.商品名称包含“剑桥预备级”，且价格ASP>1000，打标为：K12-英语-课类-正价-剑桥类- -小初。33.商品名称包含“满天星”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-满天星- -低幼。34.商品名称包含“满天星”，且价格ASP>1000，打标为：K12-英语-课类-正价-满天星- -低幼。35.商品名称包含“初中英语词汇词根+联想记忆法”和“中学重点核心大纲词汇”，且价格ASP<100，打标为：K12-英语-课类-低价-其它低价英语-绿宝书-初中。36.商品名称包含“高中”和“词汇词根+联想记忆法”，且价格ASP<40，打标为：K12-英语-课类-低价-其它低价英语-绿宝书-高中。37.商品名称包含“海尼曼英语分级阅读”，且价格ASP<100，打标为：K12-英语-课类-低价-其它低价英语-海尼曼分级阅读-低幼。38.商品名称包含“泡泡英语精讲精练”，且价格ASP<100，打标为：K12-英语-课类-低价-其它低价英语-泡泡英语-小初。39.商品名称包含“红泡泡”，且价格ASP<100，打标为：K12-英语-课类-低价-其它低价英语-红泡泡-低幼。40.商品名称包含“字母+自然拼读+音标+语音规则”或“四合一发音课”，且价格ASP<100，打标为：K12-英语-课类-低价-其它低价英语-零基础四合一-低幼。41.商品名称包含“海尼曼英语分级阅读”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-海尼曼分级阅读-低幼。42.商品名称包含“泡泡英语精讲精练”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-泡泡英语-小初。43.商品名称包含“口语天天练”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-国际音标-小初。44.商品名称包含“英语单词过目不忘”或“红宝盒”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-红宝盒-小初。45.商品名称包含“红泡泡”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-红泡泡-低幼。46.商品名称包含“字母+自然拼读+音标+语音规则”或“四合一发音课”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-零基础四合一-低幼。47.商品名称包含“巧学语法”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-巧学语法-小初。48.商品名称包含“英语启蒙点读书”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-其它中价英语-自然拼读-低幼。49.商品名称包含“海尼曼英语分级阅读”，且价格ASP>1000，打标为：K12-英语-课类-正价-其它正价英语-海尼曼分级阅读-低幼。50.商品名称包含“自然拼读+英语宝典”，且价格ASP>1000，打标为：K12-英语-课类-正价-其它正价英语-自然拼读+英语宝典-低幼。51.商品名称包含“启蒙英语ABC”或“启蒙英语自然拼读”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-启蒙英语ABC- -低幼。52.商品名称包含“世界名著英文版精读”，且价格ASP<100，打标为：K12-英语-课类-低价-书虫世界名著英文精读- -小初。53.商品名称包含“计算达人4合1”或“口算10000题”或“小学数学易错题”，且价格ASP<100，打标为：K12-数学-课类-低价-数学类图书-小学图书-小初。54.商品名称包含“小学乘法除法”，且价格ASP<100，打标为：K12-数学-课类-低价-数学类图书-小学乘除法-小初。55.商品名称包含“Journey to the West”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-西游记绘本-西游记绘本-小初。56.商品名称包含“新东方宝典小学语文”或“语文宝典小学语文”，且价格ASP<100，打标为：K12-语文-课类-低价-新东方宝典-语文宝典-小初。57.商品名称包含“新东方宝典小学语文”或“语文宝典小学语文”，且价格100<ASP<1000，打标为：K12-语文-课类-中价-新东方宝典-语文宝典-小初。58.商品名称包含“新东方宝典小学语文”或“语文宝典小学语文”，且价格ASP>1000，打标为：K12-语文-课类-正价-新东方宝典-语文宝典-小初。59.商品名称包含“数学宝典”，且价格100<ASP<1000，打标为：K12-数学-课类-中价-新东方宝典-数学宝典-小初。60.商品名称包含“英语宝典儿童英语启蒙”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-新东方宝典-英语宝典-低幼。61.商品名称包含“英语宝典儿童英语启蒙”，且价格ASP>1000，打标为：K12-英语-课类-正价-新东方宝典-英语宝典-低幼。62.商品名称包含“新东方宝典”和“全科”，且价格100<ASP<1000，打标为：K12-多科-课类-中价-新东方宝典-多科宝典-小初。63.商品名称包含“新概念”和“一册”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-新概念- -小初。64.商品名称包含“新概念”和“1册”且没有“英语训练营”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-新概念- -小初。65.商品名称包含“新概念”和“二册”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-新概念- -小初。66.商品名称包含“新概念”和“2册”且没有“英语训练营”，且价格100<ASP<1000，打标为：K12-英语-课类-中价-新概念- -小初。67.商品名称包含“英语训练营”，且价格ASP>1000，打标为：K12-英语-课类-正价-英语训练营- -小初。68.商品名称包含“英语素质集训营”，且价格ASP>1000，打标为：K12-英语-课类-正价-英语素质集训营- -幼小。69.商品名称包含“晨读晚诵”，且价格ASP<100，打标为：K12-语文-课类-低价-语文类图书-晨读晚诵-小初。70.商品名称包含“一年级识字”，且价格ASP<100，打标为：K12-语文-课类-低价-语文类图书-学前识字-低幼。71.商品名称包含“三步积累法”或“优美句子积累与仿写”或“必背小古文100篇”或“小学培优训练”或“58个妙招巧解小学语文”或“小学生必背古诗词75”，且价格ASP<100，打标为：K12-语文-课类-低价-语文类图书- -小初。"
                #             f"对于未能匹配任何规则的商品，默认打标为：其它。"
                #             # f"注意：一些未能匹配上的词不要进行联想补充或者模糊匹配，最终请告诉我打标结果就行，不要具体过程"},
                #             f"匹配规则时请注意以下几点：“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。默认规则：如果商品未能匹配任何规则，则默认打标为：其它。"},
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，举例逻辑：商品名称包含“新东方”和“power up”，且价格ASP>1000。其中的和是并存的关系，只有或才是中其中一个的意思，"
                            f"1.商品名称包含“100个句子记完2000个”或“100个句子记完1200个”，且价格ASP<10，就打标为：K12-英语-课类-低价-100个句子记单词- -小初。2. 商品名称包含“100个句子”和“高考” ，且价格ASP<10，就打标为：K12-英语-课类-低价-100个句子记单词- -高中。3. 商品名称包含“百日训练册”，且价格ASP<10，就打标为：K12-英语-课类-低价-百日训练册- -低幼。4. 商品名称包含“国际音标集训营”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-比邻-国际音标-低幼。5. 商品名称包含“核心语法精讲精练”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-比邻-精讲精练-小初。6. 商品名称包含“七合一” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-比邻-七合一-小初。7. 商品名称包含“六合一” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-比邻-听说六合一-低幼。8. 商品名称包含“自然拼读集训营”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-比邻-自然拼读-低幼。9. 商品名称包含“自然拼读集训营”，且价格ASP>1000，就打标为：K12-英语-课类-正价-比邻-自然拼读-低幼。10.商品名称包含“新东方”和“编程”，且价格ASP<10，就打标为：K12-编程-课类-低价-编程- -小初。11.商品名称包含“新东方”和“编程”，且价格100<ASP<1000  ，就打标为：K12-编程-课类-中价-编程- -小初。12.商品名称包含“新东方”和“编程”，且价格ASP>1000，就打标为：K12-编程-课类-正价-编程- -小初。13.商品名称包含“超强英语阅读力”，且价格ASP<10，就打标为：K12-英语-课类-低价-超强英语阅读力- -小初。14.商品名称包含“超强英语阅读力”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-超强英语阅读力- -小初。15.商品名称包含“初阶知识点精讲”，且价格ASP>1000，就打标为：K12-多科-课类-正价-初阶知识点精讲- -初中。16.商品名称包含“高阶知识点精讲”，且价格ASP>1000，就打标为：K12-多科-课类-正价-高阶知识点精讲- -高中。17.商品名称包含“寒假数学小班” ，且价格ASP>1000，就打标为：K12-数学-课类-正价-寒假数学小班- -初中。18.商品名称包含“词汇图解联想记忆法+同步学练测”或“词汇词根+联想记忆法乱序版+学练测” ，且价格ASP<10，就打标为：K12-英语-课类-低价-词汇+学练测- -小初。19.商品名称包含“高中”和“学练测”，且价格ASP<10，就打标为：K12-英语-课类-低价-词汇+学练测- -高中。20.商品名称包含“高中”和“词汇词根+联想记忆法”，且价格40<ASP<100，就打标为：K12-英语-课类-低价-词汇+学练测- -高中。21.商品名称包含“写给中国家庭”或“做世界的学生”或“穿越世界的教育寻访”或“我想成为更好的父母”，且价格ASP<10，就打标为：K12-家庭教育-课类-低价-家庭教育书- -小初。22.商品名称包含“写给中国家庭”或“做世界的学生”或“穿越世界的教育寻访”或“我想成为更好的父母”，且价格100<ASP<1000  ，就打标为：K12-家庭教育-课类-中价-家庭教育书- -小初。23.商品名称包含“联想巧记速练” ，且价格ASP<10，就打标为：K12-英语-课类-低价-剑桥类- -小初。24.商品名称包含“考试必备”，且价格ASP<10，就打标为：K12-英语-课类-低价-剑桥类- -小初。25.商品名称包含“考试必备”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-剑桥类- -小初。26.商品名称包含“一站式备考”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-剑桥类- -小初。27.商品名称包含“新东方”和“power up” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-剑桥类- -小初。28.商品名称包含“备考通关”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-剑桥类- -小初。29.商品名称包含“一站式备考”，且价格ASP>1000，就打标为：K12-英语-课类-正价-剑桥类- -小初。30.商品名称包含“新东方”和“power up” ，且价格ASP>1000，就打标为：K12-英语-课类-正价-剑桥类- -小初。31.商品名称包含“备考通关”，且价格ASP>1000，就打标为：K12-英语-课类-正价-剑桥类- -小初。32.商品名称包含“剑桥预备级”，且价格ASP>1000，就打标为：K12-英语-课类-正价-剑桥类- -小初。33.商品名称包含“满天星” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-满天星- -低幼。34.商品名称包含“满天星” ，且价格ASP>1000，就打标为：K12-英语-课类-正价-满天星- -低幼。35.商品名称包含“初中英语词汇词根+联想记忆法”和“中学重点核心大纲词汇” ，且价格ASP<10，就打标为：K12-英语-课类-低价-其它低价英语-绿宝书-初中。36.商品名称包含“高中”和“词汇词根+联想记忆法”，且价格ASP<40，就打标为：K12-英语-课类-低价-其它低价英语-绿宝书-高中。37.商品名称包含“海尼曼英语分级阅读”，且价格ASP<10，就打标为：K12-英语-课类-低价-其它低价英语-海尼曼分级阅读-低幼。38.商品名称包含“泡泡英语精讲精练”，且价格ASP<10，就打标为：K12-英语-课类-低价-其它低价英语-泡泡英语-小初。39.商品名称包含“红泡泡” ，且价格ASP<10，就打标为：K12-英语-课类-低价-其它低价英语-红泡泡-低幼。40.商品名称包含“字母+自然拼读+音标+语音规则”或“四合一发音课”，且价格ASP<10，就打标为：K12-英语-课类-低价-其它低价英语-零基础四合一-低幼。41.商品名称包含“海尼曼英语分级阅读”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-海尼曼分级阅读-低幼。42.商品名称包含“泡泡英语精讲精练”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-泡泡英语-小初。43.商品名称包含“口语天天练”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-国际音标-小初。44.商品名称包含“英语单词过目不忘”或“红宝盒” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-红宝盒-小初。45.商品名称包含“红泡泡” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-红泡泡-低幼。46.商品名称包含“字母+自然拼读+音标+语音规则”或“四合一发音课”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-零基础四合一-低幼。47.商品名称包含“巧学语法”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-巧学语法-小初。48.商品名称包含“英语启蒙点读书”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语-自然拼读-低幼。49.商品名称包含“海尼曼英语分级阅读”，且价格ASP>1000，就打标为：K12-英语-课类-正价-其它正价英语-海尼曼分级阅读-低幼。50.商品名称包含“自然拼读+英语宝典”，且价格ASP>1000，就打标为：K12-英语-课类-正价-其它正价英语-自然拼读+英语宝典-低幼。51.商品名称包含“启蒙英语ABC”或“启蒙英语自然拼读”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-启蒙英语ABC- -低幼。52.商品名称包含“世界名著英文版精读”，且价格ASP<10，就打标为：K12-英语-课类-低价-书虫世界名著英文精读- -小初。53.商品名称包含“计算达人4合1”或“口算10000题”或“小学数学易错题”，且价格ASP<10，就打标为：K12-数学-课类-低价-数学类图书-小学图书-小初。54.商品名称包含“小学乘法除法” ，且价格ASP<10，就打标为：K12-数学-课类-低价-数学类图书-小学乘除法-小初。55.商品名称包含“Journey to the West” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-西游记绘本-西游记绘本-小初。56.商品名称包含“新东方宝典小学语文”或“语文宝典小学语文”，且价格ASP<10，就打标为：K12-语文-课类-低价-新东方宝典-语文宝典-小初。57.商品名称包含“新东方宝典小学语文”或“语文宝典小学语文”，且价格100<ASP<1000  ，就打标为：K12-语文-课类-中价-新东方宝典-语文宝典-小初。58.商品名称包含“新东方宝典小学语文”或“语文宝典小学语文”，且价格ASP>1000，就打标为：K12-语文-课类-正价-新东方宝典-语文宝典-小初。59.商品名称包含“数学宝典”，且价格100<ASP<1000  ，就打标为：K12-数学-课类-中价-新东方宝典-数学宝典-小初。60.商品名称包含“英语宝典儿童英语启蒙”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-新东方宝典-英语宝典-低幼。61.商品名称包含“英语宝典儿童英语启蒙”，且价格ASP>1000，就打标为：K12-英语-课类-正价-新东方宝典-英语宝典-低幼。62.商品名称包含“新东方宝典”和“全科”，且价格100<ASP<1000  ，就打标为：K12-多科-课类-中价-新东方宝典-多科宝典-小初。63.商品名称包含“新概念”和“一册”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-新概念- -小初。64.商品名称包含“新概念”和“1册”且没有“英语训练营”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-新概念- -小初。65.商品名称包含“新概念”和“二册”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-新概念- -小初。66.商品名称包含“新概念”和“2册”且没有“英语训练营”，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-新概念- -小初。67.商品名称包含“英语训练营”，且价格ASP>1000，就打标为：K12-英语-课类-正价-英语训练营- -小初。68.商品名称包含“素质”和“营” ，且价格ASP>1000，就打标为：K12-英语-课类-正价-英语素质集训营- -小初。69.商品名称包含“晨读晚诵”，且价格ASP<10，就打标为：K12-语文-课类-低价-语文类图书-晨读晚诵-小初。70.商品名称包含“一年级识字”，且价格ASP<10，就打标为：K12-语文-课类-低价-语文类图书-学前识字-低幼。71.商品名称包含“三步积累法”或“优美句子积累与仿写”或“必背小古文100篇”或“小学培优训练”或“58个妙招巧解小学语文”或“小学生必背古诗词75”或“学透初中文言文” ，且价格ASP<10，就打标为：K12-语文-课类-低价-语文类图书- -小初。72.商品名称包含“新东方臻读营” ，且价格ASP>1000，就打标为：K12-英语-课类-正价-新东方臻读营- -低幼。73.商品名称包含“十一合一”或“8合1”或“零基础英语发音轻松学”或“300天英语阅读伴读营寒假学习提升” ，且价格100<ASP<1000  ，就打标为：K12-英语-课类-中价-其它中价英语- -小初。74.商品名称包含“英美经典英语儿歌分级唱”或“337晨读小学英语美文”或“高考英语词汇书真题词汇688”或“零基础开口说英语”或“漫画背单词”或“中考英语历年真题核心高频688词汇”或“一学就会”，且价格ASP<10，就打标为：K12-英语-课类-低价-其它低价英语- -小初。75.商品名称包含“单词营”或“柯林斯”，且价格700<ASP<800   ，就打标为：K12-英语-课类-中价-S体系单词营- -高中。76.商品名称包含“单词营”或“柯林斯”，且价格ASP<70，就打标为：K12-英语-课类-中价-S体系单词营- -小初。77.商品名称包含“单词营”或“柯林斯”，且价格800<ASP<1000  ，就打标为：K12-英语-课类-中价-S体系单词营- -小初。78.商品名称包含“单词营”或“柯林斯”，且价格ASP>1000，就打标为：K12-英语-课类-中价-S体系单词营- -小初。79.商品名称包含“新东方300天英语阅读伴读营” ，且价格ASP>10，就打标为：K12-英语-课类-中价-300天英语阅读伴读营- -小初。80.商品名称包含“新东方”和“小学英语核心能力” ，且价格ASP>10，就打标为：K12-英语-课类-中价-小学英语核心能力- -小初。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它-其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '平行线' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“思维特训”和“48讲”，且价格ASP>1000，就打标为：正价。2. 商品名称包含“思维训练”和“48讲”，且价格ASP>1000，就打标为：正价。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )
   
    elif '希望学' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 希望学
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“希望学阅读大师课”和“希望学语文”，且价格ASP>90，就打标为：小学-课类-正价-学科正价-语文阅读大师-语文。2. 商品名称包含“希望学语数英”和“幼小衔接”，且价格ASP>90，就打标为：低幼-课类-正价-素养正价-幼小衔接暑秋班-多科。3. 商品名称包含“希望学语法大师”或“希望学英语”，且价格ASP>90，就打标为：小学-课类-正价-学科正价-小学语法大师课-英语。4. 商品名称包含“希望学计算大师”或“希望学数学思维”，且价格ASP>90，就打标为：小学-课类-正价-学科正价-小学计算大师课-数学。5. 商品名称包含“提分方案”，且价格ASP>70，就打标为：初中-课类-正价-学科正价-提分方案-多科。6. 商品名称包含“高阶知识精讲” ，且价格ASP>1000，就打标为：高中-课类-正价-学科正价-高中必备知识点-多科。7. 商品名称包含“关关满分考场作文”，且价格ASP<10，就打标为：小学-课类-中价-学科中价-关关满分作文-语文。8. 商品名称包含“魔法计算&超能拼音”，且价格ASP>10，就打标为：低幼-课类-中价-素养中价-幼小衔接30天-数学/语文。9. 商品名称包含“王子悦” ，且价格ASP<10，就打标为：高中-课类-中价-学科中价-王子悦高中数学-数学。10.商品名称包含“4节高中三年数学满分攻略”，且价格ASP<10，就打标为：高中-课类-中价-学科中价-博宇老师高中数学-数学。11.商品名称包含“哈佛秦怡”，且价格ASP<10，就打标为：小学-课类-中价-学科中价-哈佛秦怡自然拼读-英语。12.商品名称包含“进哥”，且价格50<ASP<100，就打标为：高中-课类-中价-学科中价-进哥高中物理-物理。13.商品名称包含“春成提分宝典” ，且价格ASP<10，就打标为：初中-课类-中价-学科中价-春成提分宝典-数学。14.商品名称包含“朱韬高频易错宝典”，且价格ASP<10，就打标为：初中-课类-中价-学科中价-红宝书-数学。15.商品名称包含“朱韬”和“30天”和“初中数学”，且价格ASP<10，就打标为：初中-课类-中价-学科中价-30天搞定初中数学-数学。16.商品名称包含“幼小衔接”和“双科”，且价格ASP<1000，就打标为：低幼-课类-中价-素养中价-幼小衔接30天-数学/语文。17.商品名称包含“杨萌”和“提分指南”，且价格ASP<1000，就打标为：初中-课类-中价-学科中价-杨萌提分指南-物理。18.商品名称包含“一鸣”和“数学思维”，且价格ASP<10，就打标为：小学-课类-中价-学科中价-30天数学思维-数学。19.商品名称包含“小升初百日陪考”，且价格ASP<20，就打标为：初中-课类-中价-学科中价-小升初百日陪考-数学。20.商品名称包含“希望学新概念” ，且价格ASP>1000，就打标为：小学-课类-正价-学科正价-小学语法大师课-英语。21.商品名称包含“希望学剑桥”，且价格ASP>1000，就打标为：小学-课类-正价-学科正价-小学语法大师课-英语。22.商品名称包含“小四门” ，且价格ASP>10，就打标为：初中-课类-中价-学科中价-重难点宝盒-多科。23.商品名称包含“高阶”和“必备知识点”，且价格ASP>1000，就打标为：高中-课类-正价-学科正价-高中必备知识点-多科。24.商品名称包含“秋整”和“幼小入学”，且价格ASP>1000，就打标为：低幼-课类-正价-素养正价-幼小衔接秋整-多科。25.商品名称包含“韩春成”和“初中数学”，且价格0<ASP<100，就打标为：初中-课类-中价-学科中价-韩春成初中数学-数学。26.商品名称包含“魔法计算”，且价格ASP>100，就打标为：低幼-课类-中价-素养中价-幼小衔接30天-数学。27.商品名称包含“计算秘籍”和“学而思”，且价格0<ASP<100，就打标为：小学-课类-低价-学科中价-计算秘籍-数学。28.商品名称包含“领跑计划”和“学而思”，且价格0<ASP<100，就打标为：小学-课类-低价-学科中价-领跑计划-多科。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif 'sam' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1. 商品名称包含“sam” ，且价格ASP<10，就打标为：低价。2. 商品名称包含“王垚”或“曲艺”或“麻麻”或“曾曦”或“注册会计师”或“潘潘” ，且价格ASP>0 ，就打标为：其它"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '陈心' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“陈心语文”和“小学”，且价格100<ASP<1000  ，就打标为：中价-小学阅读36技。2. 商品名称包含“陈心”和“初中”，且价格100<ASP<1000  ，就打标为：中价-初中阅读36技。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '毛毛虫' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“毛毛虫”，且价格100<ASP<1000，就打标为：中价。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '潘潘' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“潘潘”和“小学数学”，且价格ASP<1000，就打标为：中价-小学数学查漏补缺。2. 商品名称包含“潘门弟子年卡” ，且价格ASP>1000，就打标为：正价-潘门弟子年卡。3. 商品名称包含“潘潘”和“八大思维积木” ，且价格100<ASP<1000  ，就打标为：中价-八大思维积木。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '小学数学张老师' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“张文晖”和“小学”，且价格100<ASP<1000  ，就打标为：中价-小学数学。2. 商品名称包含“张文晖”和“初中”，且价格100<ASP<1000  ，就打标为：中价-初中物理。"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '雪梨' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“雪梨”和“1500词”，且价格ASP<10，就打标为：低价-自然拼读1500词。2. 商品名称包含“雪梨”和“五合一”，且价格100<ASP<1000  ，就打标为：中价-零基础五合一。3. 商品名称包含“雪梨”和“自然拼读”，且价格100<ASP<1000  ，就打标为：中价-自然拼读。4. 商品名称包含“雪梨”和“国际音标”，且价格100<ASP<1000  ，就打标为：中价-国际音标。5. 商品名称包含“雪梨”和“完美音标”，且价格100<ASP<1000  ，就打标为：中价-完美音标。6. 商品名称包含“雪梨”和“中高级英语语法”，且价格100<ASP<1000  ，就打标为：中价-中高级英语语法。7. 商品名称包含“雪梨”和“小学英语宝典” ，且价格100<ASP<1000  ，就打标为：中价-小学英语宝典。8. 商品名称包含“雪梨”和“初级英语语法” ，且价格100<ASP<1000  ，就打标为：中价-初级英语语法。9. 商品名称包含“7天入门开窍” ，且价格ASP>0 ，就打标为：低价-7天入门开窍营。10.商品名称包含“自然拼读冲刺营”，且价格ASP>0 ，就打标为：低价-自然拼读冲刺营。11.商品名称包含“自然拼读+英语宝典”，且价格ASP>10，就打标为：中价-自然拼读+英语宝典。12.商品名称包含“雪梨”和“七合一”，且价格ASP>90，就打标为：正价-零基础七合一。13.商品名称包含“字帖”，且价格ASP>90，就打标为：其它"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '赛先生科学' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“赛先生科学”和“AI超能少年” ，且价格ASP>1000，就打标为：正价-AI超能少年。2. 商品名称包含“赛先生科学”和“AI小创客”，且价格ASP<1000，就打标为：正价-AI小创客"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '星际光年' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“胡小群”，且价格ASP<50，就打标为：低价。2.商品名称包含“胡小群”，且价格100<ASP<1000 ，就打标为：中价。3.商品名称包含“胡小群”，且价格ASP>1000，就打标为：正价。4.商品名称包含“花生粥超级写作”,且价格ASP>100 ，就打标为：中价。5.商品名称包含“钟平”,且价格ASP>100 ，就打标为：中价"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )
    elif '豌豆思维' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f".商品名称包含“幼小思维突破” ,且价格ASP>100，就打标为：中价"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    elif '杨妈英语思维' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“杨萃先”和“颠覆传统英语学习法” ,且价格ASP>100，就打标为：中价"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )
    elif '清华沙沙' in pinpai:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                # 平行线
                {"role": "user",
                 "content": f"请根据下面这段文字，对数据进行打标，商品名称为【{text}】，"
                            f"价格为【{price}】，"
                            f"1.商品名称包含“英语单词语法”,且价格ASP>100，就打标为：中价-英语单词语法。2.商品名称包含“英语完形阅读”,且价格ASP>100,就打标为：中价-英语完形阅读"
                            f"匹配规则时请注意以下几点：请以““内的词为一整个词进行判断，“和”与“或”的区别：“和”表示所有条件必须同时满足。例如，规则中“商品名称包含A和B”表示名称中必须同时包含A和B。“或”表示只需满足其中一个条件。例如，规则中“商品名称包含A或B”表示名称中只需包含A或B中的任意一个。严格匹配：商品名称和规则中的关键词必须完全一致，禁止联想补充或模糊匹配。例如，商品名称中缺少“新东方”时，即使包含“power up”也不匹配相关规则。规则优先级：请严格按照规则顺序匹配，优先匹配更具体的规则。"
                            f"默认规则：如果商品未能匹配任何规则，则默认打标为：其它。最终请告诉我打标结果就行，不要具体过程，和任何的其余描述"},

            ],
            stream=False
        )

    else:
        pass
    return response.choices[0].message.content



def process_excel():
    # november_files = get_excel_files('C:\\Users\Admin\Desktop\\测试')  # 日报数据
    # november_files_name = 'C:\\Users\Admin\Desktop\\测试'
    november_files = get_excel_files('C:\\Users\Admin\Desktop\\日报数据')  # 日报数据
    november_files_name = 'C:\\Users\Admin\Desktop\\日报数据'
    november_files_name_dp = 'C:\\Users\Admin\Desktop\\日报数据\\deepseek打标'
    for nov_file in november_files:
        # if '胡小群' in nov_file or '平行线' in nov_file or '希望学' in nov_file or '高途' in nov_file or '猿辅导' in nov_file or '作业帮' in nov_file or '新东方' in nov_file or '有道' in nov_file or '叫叫' in nov_file:
        # if 'sam' in nov_file or '陈心' in nov_file or '毛毛虫' in nov_file or '潘潘' in nov_file or '小学数学张老师' in nov_file or '雪梨' in nov_file or '赛先生科学' in nov_file:
        #     continue
        # if '高中其它' in nov_file:
        #     # 完整的源文件路径
        #     source_path = os.path.join(november_files_name, nov_file)
        #     # 完整的目标文件路径
        #     destination_path = os.path.join(november_files_name_dp, nov_file)
        #
        #     # 将文件复制到目标文件夹
        #     shutil.copy2(source_path, destination_path)
        #     print(f"文件 {nov_file} 已复制到 {november_files_name_dp}")

        print(f'处理文件{nov_file}')
        df = pd.read_excel(os.path.join(november_files_name, nov_file), sheet_name='Sheet1')  # 日报
        # 初始化结果列（如果不存在）
        if RESULT_COLUMN0_all not in df.columns:
            df[RESULT_COLUMN0_all] = ""

        # 遍历处理每一行
        for index, row in df.iterrows():
            # if index == 12:
            if pd.isnull(row['price']) or row['price'] == "": # 处理平台区间值的情况
                continue
            if pd.isnull(row[RESULT_COLUMN0_all]) or row[RESULT_COLUMN0_all] == "":
                text_content = row[TEXT_COLUMN]
                text_price = row[price]


                # 调用API获取标签
                label = call_deepseek_api(str(text_content),str(text_price),nov_file)  # 确保转换为字符串

                # 更新数据框(处理数据-的问题)

                if "打标结果" in label:
                    # print(label)
                    if "：" in label:
                        label = label.split("：")[1]
                    elif ":" in label:
                        label = label.split(":")[1]

                if "其它" in label and "-" not in label:
                    df.at[index, RESULT_COLUMN0_all] = label
                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]


                elif '新东方' in nov_file:
                    split_result = label.split('-')
                    df.at[index, '学段一'] = split_result[0] if len(split_result) > 0 else None
                    df.at[index, '科目'] = split_result[1] if len(split_result) > 1 else None
                    df.at[index, '产品形态一'] = split_result[2] if len(split_result) > 2 else None
                    df.at[index, '产品形态二'] = split_result[3] if len(split_result) > 3 else None
                    df.at[index, '产品形态三'] = split_result[4] if len(split_result) > 4 else None
                    df.at[index, '产品形态四'] = split_result[5] if len(split_result) > 5 else None
                    df.at[index, '学段二'] = split_result[6] if len(split_result) > 6 else None

                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]

                elif '希望学' in nov_file:
                    split_result = label.split('-')
                    df.at[index, '学段'] = split_result[0] if len(split_result) > 0 else None
                    df.at[index, '产品形态一'] = split_result[1] if len(split_result) > 1 else None
                    df.at[index, '产品形态二'] = split_result[2] if len(split_result) > 2 else None
                    df.at[index, '产品形态三'] = split_result[3] if len(split_result) > 3 else None
                    df.at[index, 'SKU'] = split_result[4] if len(split_result) > 4 else None
                    df.at[index, '学科'] = split_result[5] if len(split_result) > 5 else None
                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]

                elif '有道' in nov_file:
                    split_result = label.split('-')
                    df.at[index, '产品形态一'] = split_result[0] if len(split_result) > 0 else None
                    df.at[index, '产品形态二'] = split_result[1] if len(split_result) > 1 else None
                    df.at[index, '产品形态三'] = split_result[2] if len(split_result) > 2 else None
                    df.at[index, '是否新品'] = split_result[3] if len(split_result) > 3 else None
                    df.at[index, '周期'] = split_result[4] if len(split_result) > 4 else None
                    df.at[index, '附加标签'] = split_result[5] if len(split_result) > 5 else None
                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]

                elif '作业帮' in nov_file:
                    split_result = label.split('-')
                    df.at[index, '产品形态'] = split_result[0] if len(split_result) > 0 else None
                    df.at[index, '产品形态一'] = split_result[1] if len(split_result) > 1 else None
                    df.at[index, '产品形态二'] = split_result[2] if len(split_result) > 2 else None
                    df.at[index, '产品形态三'] = split_result[3] if len(split_result) > 3 else None
                    df.at[index, '是否新品'] = split_result[4] if len(split_result) > 4 else None
                    df.at[index, '周期'] = split_result[5] if len(split_result) > 5 else None
                    df.at[index, '学段'] = split_result[6] if len(split_result) > 6 else None
                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]

                elif '猿辅导' in nov_file or '高途' in nov_file:
                    split_result = label.split('-')
                    df.at[index, '产品形态一'] = split_result[0] if len(split_result) > 0 else None
                    df.at[index, '产品形态二'] = split_result[1] if len(split_result) > 1 else None
                    df.at[index, '产品形态三'] = split_result[2] if len(split_result) > 2 else None
                    df.at[index, '是否新品'] = split_result[3] if len(split_result) > 3 else None
                    df.at[index, '周期'] = split_result[4] if len(split_result) > 4 else None
                    df.at[index, '学段'] = split_result[5] if len(split_result) > 5 else None
                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]

                else:
                    split_result = label.split('-')
                    df.at[index, '产品形态一'] = split_result[0] if len(split_result) > 0 else None
                    df.at[index, '产品形态二'] = split_result[1] if len(split_result) > 1 else None
                    df.at[index, '产品形态三'] = split_result[2] if len(split_result) > 2 else None
                    df.at[index, '产品形态四'] = split_result[3] if len(split_result) > 3 else None
                    # df.at[index, RESULT_COLUMN0_all] = label
                    df.at[index, '打标类型'] = 'deepseek'
                    # 获取当前所有列名
                    cols = list(df.columns)

                    # 将 "打标类型" 移动到最后
                    cols.append(cols.pop(cols.index('打标类型')))
                    df = df[cols]

                # 进度打印
                print(f"已处理第 {index + 1}/{len(df)} 条，结果：{label}")

                # API限速控制（根据API要求调整）
                time.sleep(1)

        # 保存结果
        # df.to_excel(f"{nov_file.split('.')[0]}deepseek打标结果.xlsx", index=False)
        df.to_excel(os.path.join(november_files_name_dp, f"{nov_file.split('.')[0]}deepseek打标结果.xlsx"), index=False)
        print("处理完成，结果已保存到xlsx表")


def get_time_str(num):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=num)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    return yesterday_str

def  get_ribao():
    num_type = 2  # 1是平台正常  2是平台区间值
    # 指定路径
    path = r'C:\Users\Admin\Desktop\日报数据'
    path2 = r'C:\Users\Admin\Desktop\日报数据\deepseek打标'

    # 检查路径下的所有Excel文件
    files = glob.glob(os.path.join(path, "*.xls*"))
    files2 = glob.glob(os.path.join(path2, "*.xls*"))

    # 删除每一个Excel文件
    for file in files:
        try:
            os.remove(file)
            print(f"文件 {file} 已被删除.")
        except Exception as e:
            print(f"无法删除文件 {file}. 原因: {e}")

    # 删除每一个Excel文件
    for file in files2:
        try:
            os.remove(file)
            print(f"文件 {file} 已被删除.")
        except Exception as e:
            print(f"无法删除文件 {file}. 原因: {e}")


    time_list = [
        # [get_time_str(6), get_time_str(6)],
        # [get_time_str(2),get_time_str(2)],
        # [get_time_str(12), get_time_str(12)],
        [get_time_str(1), get_time_str(1)],
        # ['2026-02-09', '2026-02-'],

    ]
    print(time_list)



    keys = [
        ['高途', 'LAumwArn', '苏州瑞之和文化店'],
        ['猿辅导', 'dogdNUDN', '素养教育快乐课堂'],
        ['猿辅导', 'BLLNoYYD', '猿辅导音像旗舰店'],
        ['作业帮', 'CDirgbaB', '乐学图书教辅'],  # 2.2

        ['高途', 'nzeUKENI', '瑞之和文化艺术精品店'],
        # ['高途', 'VmMPGkIP', '金众企通文化臻选阁'],
        ['作业帮', 'EIyTtRQo', '百分优品教辅'],  # 2.2
        ['作业帮', 'vYjDduDN', '锦学图书学习营地'],  # 2.2
        ['作业帮', 'EliGBLQo', '锦学图书大通关'],  # 2.2
        ['作业帮', 'LWYzfjrn', '矩尺学习精选'],  # 2.2
        ['猿辅导', 'oVAGhBcR', '猿辅导小猿素养'],
        ['猿辅导', 'yLfxoGDU', '小猿文化屋'],
        ['猿辅导', 'hwnnPwSC', '小猿书屋'],
        ['猿辅导', 'NjpAfhPW', '小猿趣味学习屋'],
        ['猿辅导', 'BwqSlrPA', '小猿图书音像屋'],
        ['猿辅导', 'dNGeasdq', '猿辅导高中教育培训'],
        ['高途', 'lIOTSIkX', '知源书屋严选铺'],
        ['高途', 'EmQXmShu', '事皆顺文传'],
        ['高途', 'kedZRjrn', '墨拓文化'],
        ['高途', 'wzbNHBIk', '高途英语'],
        ['高途', 'hJCZmfSC', '高途英语课堂'],
        ['有道', 'ANVGoFEy', '长汀念派科技好货店'],
        ['有道', 'tWfhfTHs', '长汀念派科技优品小铺'],
        ['高途', 'LWFxzmPW', '众众聚鑫生物优品小铺'],
        ['猿辅导', 'bXCOLlYg', '快乐成长素养教育'],
        ['猿辅导', 'oKxkrsUm', '小猿学习屋'],
        ['晓晶老师语文', 'cnExfjZY', '阿凡达教育'],
        ['高途', 'PglMSYgl', '澜畔桨文化1店'],
        ['高途', 'rxKdOMEv', '北京知源阅读铺子'],
        ['作业帮', 'CDgQuLaB', '锦学图书精品'],  # 2.2
        ['豆神', 'IQYWnocR', '豆神明兮教育严选'],
        ['猿辅导', 'whMVlBIk', '猿辅导远誉文化用品专卖店'],
        ['小学数学张老师', 'MYECoBaL', '趣满分浪起名师MCN'],
        ['作业帮', 'mMxZIazK', '矩尺学习教辅'],  # 2.2
        ['豆神', 'JhxLZWrj', '豆神书书企业店'],
        ['高途', 'dMBNarUm', '来师学苑'],
        ['猿辅导', 'VAWllGaB', '湖南众众聚鑫生物优品店'],
        ['猿辅导', 'HttBVsdq', '猿力图书音像专营店'],
        ['猿辅导', 'SuIhgTBr', '猿力音像专营店'],
        ['高途', 'KOVaDtkH', '高途春之火'],
        ['高途', 'aOKRuOhG', '苏州七年二班文化创意屋'],
        ['高途', 'gLXzECLw', '途阅学苑'],
        ['高途', 'FHnBvUeS', '欧邦创意'],
        ['猿辅导', 'LcbCFNQo', '猿编程学考旗舰店'],
        ['作业帮', 'QnDUCBcR', '锦学图书教辅'],  # 2.4 回溯2.3
        ['猿辅导', 'AOSQhvzK', '湖南众众聚鑫生物创意屋'],
        ['豆神', 'swKQzrZh', '豆神之明兮教育精品店'],
        ['高途', 'VCyrHLQo', '知行远航科技优品店'],
        ['作业帮', 'bHSxvhYg', '锦学图书优品'],  # 2.2
        ['作业帮', 'CATsDbaB', '库学小初学习营地'],  # 2.2
        ['希望学', 'uRykndkX', '希学素养甄选'],
        ['晓晶老师语文', 'oImtBsHT', '获课学堂'],
        ['作业帮', 'CATsDbaB', '库学小初学习营地'],  # 2.2
        ['作业帮', 'PvrNnigl', '阅写图书甄选'],  # 2.2
        ['高途', 'phmIaPHT', '高途科技优品严选'],
        ['高途', 'fsmbzUaL', '苏州七年二班创意文化铺子'],
        ['高途', 'ZiTvPxKF', '杨清鑫流量文化小铺子'],
        ['高途', 'NUvcZeUJ', '极创文化馆'],
        ['猿辅导', 'FNfwbueS', '小猿教辅图书优选'],
        ['猿辅导', 'UyglNeUJ', '小猿素养成长'],
        ['作业帮', 'GFmPKTBr', '库学小初训练营'],  # 2.2
        ['猿辅导', 'rpUZyMEv', '小猿素养文化'],
        ['猿辅导', 'pQqUwrZh', '小猿课堂精选'],
        ['作业帮', 'ibXxxCkH', '库学小初图书优选'],#1.29
        ['豆神', 'moWNzqBr', '豆神读写营'],
        ['晓晶老师语文', 'FPPoXMza', '连锁反应专营店'],
        ['高途', 'zeCunNcp', '育梦无限科技创意小铺'],
        ['猿辅导', 'hGDozern', '素养教育成长课堂'],
        ['猿辅导', 'MFqjsxXQ', '小猿助学教辅店'],
        ['猿辅导', 'cMNoNeZY', '小猿助学图书店'],
        ['猿辅导', 'EwYRpRDU', '智慧少儿成长研习社'],
        ['猿辅导', 'GRNQltqO', '猿力图书严选'],
        ['猿辅导', 'LykFILQo', '小猿电子图书优选'],
        ['作业帮', 'jzCYDwNE', '矩尺学习小店'],
        ['猿辅导', 'iZikHCkH', '小猿图书文化'],
        ['猿辅导', 'WmYuYJdq', '斑马启蒙体验店'],
        ['猿辅导', 'gfGwxgMc', '天天练练图书'],
        ['猿辅导', 'JeugVngl', '博学雅苑'],
        ['高途', 'XbwgiLHs', '苏州瑞之和文化创意屋'],
        ['作业帮', 'VlQswTIP', '知行高中图书'],
        ['猿辅导', 'XCNBuLHs', '猿辅导远誉学习文化专卖店'],
        ['作业帮', 'ymRxLSDU', '库学小初教辅'],
        ['作业帮', 'kIcWIjgi', '库学小初优品'],
        ['有道', 'qiZAqjgi', '有道领世精选'],
        ['高途', 'CuPtNESf', '高途口语外教'],
        ['猿辅导', 'SQZXNqUJ', '猿辅导图书旗舰店'],
        ['猿辅导', 'eoqDqfEy', '猿辅导猿力进口图书专卖店'],
        ['猿辅导', 'mkMxAxKF', '斑马世界图书音像旗舰店'],
        ['作业帮', 'FMfquueS', '知行优选图书'],
        ['猿辅导', 'RfHtlVqO', '小猿优课教辅'],
        ['高途', 'FMibFQSC', '高途英语的店'],
        ['高途', 'MPQzhvEy', '极创甄选馆'],
        ['作业帮', 'NfrvvTdZ', '小蓝帮图书优选'],
        ['高途', 'PdwQhgrj', '欧邦文化臻选阁'],
        ['猿辅导', 'DlJCxjMM', '猿辅导小猿素养教育'],
        ['高途', 'UEPrFWBe', '灵思图书'],
        ['晓晶老师语文', 'fzJKXbHs', '星奇点教育'],
        ['作业帮', 'LkVQADrn', '同宏严选图书'],
        ['猿辅导', 'hlOONvSC', '猿辅导远誉进口图书专卖店'],
        ['作业帮', 'GENAhRQo', '浩途图书教育店'],
        ['作业帮', 'JzrMViKF', '千帆知行优品'],
        ['猿辅导', 'JTuxaoIk', '猿编程人工智能'],
        ['猿辅导', 'aqDCKlMM', '猿编程优学'],
        ['猿辅导', 'eJrVRePW', '猿力图书甄选'],
        ['猿辅导', 'zfVCxgMc', '少儿编程智慧创造屋'],
        ['作业帮', 'HdweDZHT', '同宏精选图书'],
        ['作业帮', 'OXdaYdDN', '百分优品图书'],
        ['作业帮', 'SvyHsqUJ', '乐学图书学习营地'],
        ['高途', 'YcAdSxEv', '高途学堂'],
        ['希望学', 'BZIeArdq', '希望学初中企业5店'],
        ['作业帮', 'FJExgOLV', '小蓝帮图书精选'],
        ['有道', 'VJkLSNQo', '长汀念派科技生活坊'],
        ['有道', 'MIowRQXz', '长汀念派科技精品小铺'],
        ['猿辅导', 'bQyOCKEv', '小猿优课'],
        ['作业帮', 'xgmGYXed', '广悦甄选图书'],
        ['作业帮', 'lXZrrdkX', '灵思图书优选'],
        ['豆神', 'ZvKacrPA', '秣马未来教育创意屋'],
        ['猿辅导', 'KKAVwKXQ', '猿辅导猿起图书专卖店'],
        ['作业帮', 'vbirTphG', '趣味阅读优选'],
        ['作业帮', 'rsMMrzEv', '大阅读图书'],
        ['高途', 'XAAJQLHs', '苏州码上飞文化创意屋'],
        ['高途', 'YiVPRyza', '郑州春之火文化臻选阁'],
        ['猿辅导', 'NCahRbQo', '猿力素养严选'],
        ['作业帮', 'vQNXbdDN', '广悦精选图书'],
        ['高途', 'ZnXdsxMc', '北京知行远航科技严选店'],
        ['作业帮', 'NfzKomPW', '乐学图书大通关'],
        ['作业帮', 'PtuaJggl', '乐学图书优品'],
        ['猿辅导', 'bQyOCKEv', '小猿优课'],
        ['作业帮', 'RrrOZeZY', '蔚蓝图书大通关'],
        ['高途', 'rJSUmxMc', '长沙绥芬文化精选小铺'],  # 11.24
        ['高途', 'NfPRfbHs', '途阅空间'],  # 11.24
        ['高途', 'UuClpsdq', '绥芬文化生活坊'], # 11.24
        ['有道', 'PanPrnYD', '长汀念派科技臻选阁'],
        ['有道', 'cTRFFwkX', '威的有未创意屋'],
        ['有道', 'FurAwjYg', 'YOUD领世'],
        ['有道', 'ZJFGAMMc', '长汀有未科技创意屋'],
        ['高途', 'FgXwEFMM', '途宏文化'],
        ['作业帮', 'ydUoaSDU', '蔚蓝图书学习营地'],
        ['希望学', 'tPrutrBe', '希望学初中企业7店'],  # 12.10
        ['作业帮', 'hynPpwSC', '新启迪学习营'],
        ['高途', 'vUwAzwqt', '万聚科技精品小铺子'],
        ['作业帮', 'tZbNebdZ', '浩途图书优选'],
        ['作业帮', 'AKnQEIXz', '启迪教育学习营地'], # 12.10
        ['作业帮', 'pehPMrZh', '蔚蓝图书教辅'],
        ['高途', 'QfYXJczK', '码上飞文化'],
        ['高途', 'NszMdkHs', '石家庄高途科技生活坊'],
        ['作业帮', 'hTbHsjMM', '浩途教育精选'], # 12.1
        ['希望学', 'lMTthiza', '希望学小学企业6店'],#12.10
        ['作业帮', 'OqpuhZdq', '浩途图书精选'],
        ['作业帮', 'GnDNvqUJ', '爱学图书优选'],
        ['高途', 'eexJglMM', '长沙绥芬文化创意屋'],
        ['高途', 'QsayjQXz', '高途刘薇'],
        ['作业帮', 'VqVkyNQo', '千帆知行训练营'],
        ['作业帮', 'StSrOtDU', '书芽教辅图书'],
        ['作业帮', 'FXXSideS', '蔚蓝图书精品'],
        ['猿辅导', 'hyWLJfEy', '猿辅导素养课培训'],
        ['作业帮', 'yUKCrNDU', '羲和图书优选'],
        ['有道', 'FQOcJILV', '有道领世严选'],
        ['有道', 'lZRJnILV', '有道领世计算图书专卖店'],
        ['有道', 'ovlTgJdq', '有道领世教育店铺'],
        ['有道', 'jMUZCfEy', '有道领世严选小铺'],
        ['有道', 'uOEuFOhG', '有道精品课'],
        ['有道', 'PPCalnYD', '长汀有未科技优品小铺'],
        ['作业帮', 'pKIRurBe', '畅想图书教辅'],
        ['作业帮', 'GXiVmNQo', '浩途训练营'],
        ['作业帮', 'raQBbxEv', '蔚蓝图书优品'],
        ['高途', 'AQafRaKx', '高途语言'],
        ['作业帮', 'LWsIJjrn', '新启迪图书优品'],
        ['作业帮', 'SZXqpeUJ', '新启迪教育教辅'],
        ['作业帮', 'eyTXrfEy', '羲和光图书教育店'],
        ['猿辅导', 'DZFwiazK', '猿起音像专营店'],
        ['作业帮', 'eTyGTQzK', '小学阅写图书'],
        ['高途', 'dsDCGOLV', '博学星晨图书'],
        ['猿辅导', 'DgdKuvzK', '猿辅导教育企业店'],
        ['作业帮', 'fLpxMBaL', '羲和图书教辅'],
        ['作业帮', 'phseqnZh', '羲和图书优品'],
        ['作业帮', 'rZbBMsUm', '帮帮百分优品图书'],
        ['作业帮', 'yqYYGXed', '畅享教育精选店'],
        ['猿辅导', 'rFVUqiMc', '猿起中学教辅'],
        ['作业帮', 'ddXbVwkX', '小蓝帮图书二号店'],
        ['作业帮', 'PpvqyrBe', '小初图书优品3号店'],
        ['猿辅导', 'GqyXoTdZ', '猿辅导猿起进口图书专卖店'],
        ['希望学', 'JnBfnYrj', '希望学初中企业4店'],
        ['希望学', 'jryiQMKF', '希望学初中企业6店'],
        ['希望学', 'pKluOWPA', '希望学初中企业8店'],
        ['高途', 'UVMbFZUm', '青岛高途畅学营'],
        ['高途', 'NoOlOnMc', '高途高中书苑'],
        ['猿辅导', 'OJYPjqBr', '猿起教育专营店'],
        ['作业帮', 'ejDOtkdZ', '小蓝帮图书四号店'],
        ['叫叫', 'VEajcGed', '叫叫阅读伴学站'],
        ['作业帮', 'AfVzWeBr', '帮高中教辅图书'],
        ['猿辅导', 'PtWKBJBe', '猿起图书教育'],
        ['高途', 'JeOGXoIk', '欧邦文化'],
        ['高途', 'SdbMOted', '捷自在文化'],
        ['作业帮', 'AsrWNQzK', '小船训练营'],
        ['毛毛虫', 'GJGtZmUJ', '毛毛虫知学英语店'],
        ['作业帮', 'irrUTyEv', '乘风远航图书专营店'],
        ['猿辅导', 'CltmAtqO', '猿起精选图书'],
        ['高途', 'usrAqpcR', '德古文化'],
        ['作业帮', 'XjMlDLQo', '帮帮畅想图书'],
        ['作业帮','IIoNhVLw','作业帮北京美唐科技有限公司教育专卖店'],
        ['高途', 'tFrxdNDU', '斯佳彤好课屋'],
        ['高途', 'SfUtuNcp', '佳彤臻选阁'],
        ['高途', 'CfzsIVkH', '启得隆书苑'],
        ['作业帮', 'kTXYneBr', '作业帮美唐图书专卖店'],
        ['作业帮','DQaIhern','帮小帮智学图书'],
        ['希望学', 'wkgikHeS', '融趣企业店3'],
        ['火花', 'rjUbRBIk', '火花思维教育图书专卖店'],
        ['作业帮', 'snrVIZIk', '智美学习教育店'],
        ['毛毛虫', 'XppsxGaB', '毛毛虫知课企业店'],
        ['希望学', 'bDaGLAPW', '希望学小学企业店5'],
        ['猿辅导', 'VcRkAGhu', '猿起电子图书'],
        ['作业帮', 'HQtQPUDN', '帮帮秒答学堂'],
        ['作业帮', 'RkUWvTIP', '帮帮知识便利店'],
        ['作业帮', 'FkzPJINE', '智想图书学习营地'],
        ['作业帮','dlyBDPQb','智想教育教辅'],
        ['猿辅导', 'fChcsIkX', '猿辅导图书'],
        ['猿辅导', 'LIpuSTBr', '猿起中学图书'],
        ['毛毛虫', 'MAArzMza', '毛毛虫A'],
        ['高途', 'XDqetCLw', '奇兔兔文化'],
        ['高途', 'nHbLKuhG', '自变量思维课堂'],
        ['猿辅导', 'uSBQcsHT', '猿辅导素养课企业店铺'],
        ['作业帮', 'waFKWUhG', '帮帮成长驿站'],
        ['作业帮', 'xxcsWKza', '小初学习提升二营'],

        ['希望学', 'lHlvPfSC', '融趣企业店7'],
        ['希望学', 'BZIeArdq', '希望学初中企业5店'],
        ['高途', 'FqJIbjMM','木颜图书'],
        ['猿辅导', 'jICWAjYg', '猿辅导猿起专卖店'],
        ['毛毛虫', 'OtyDjdDN', '毛毛虫阅和读教育'],
        ['作业帮', 'jTyivazK', '小蓝帮高中教辅'],
        ['作业帮', 'MMAAPgYD', '小蓝帮图书三号店'],
        ['希望学', 'XgiSDtkH', '希望学小学企业店2'],
        ['高途', 'YiVPRyza', '郑州春之火文化臻选阁'],
        ['高途', 'yOOOwzEv', '夜幻文化'],
        ['作业帮', 'izwkNgYD', '畅想图书学习营'],
        ['希望学', 'CIPwHVqO', '融趣企业店4'],
        ['作业帮', 'iqFjuyXQ', '帮帮教辅图书'],
        ['作业帮', 'fcayFOqt','帮帮远航精选店'],
        ['高途','vofzEvSC','启得隆优选'],
        ['高途', 'gqlWsgKF', '高途教育坊'],
        ['杨妈英语思维', 'FUhcjbdZ', '清芬管理文化'],
        ['高途', 'AwIWYhrn', '万聚知识屋'],
        ['猿辅导', 'WhGocngl', '猿起图书音像专营店'],
        ['作业帮', 'tTyLttqO', '小蓝帮教辅图书'],
        ['作业帮', 'nCaLMgMc', '书芽优选图书'],
        ['杨妈英语思维', 'OPmcFhPW', '管理文化咨询'],
        ['猿辅导', 'CHWJfKXQ', '斑马百通图书店铺'],
        ['高途', 'ESZpgted', '讯言文化文传'],
        ['希望学', 'QPHVYHLV', '希望学小学教辅'],
        ['高途', 'nvHcBgrj', '高途云集学苑'],
        ['作业帮', 'LGyutkdZ', '智想图书训练营'],
        ['作业帮', 'TdlpihPW', '帮帮远航精品'],
        ['作业帮', 'FhjeTQSC', '帮帮远航训练营'],
        ['作业帮', 'vQOlOHLV', '智想图书精选'],
        ['猿辅导', 'MABdbzXQ', '猿辅导猿起学习用品专卖店'],
        ['毛毛虫', 'KNTCyyNI', '毛毛虫英语企业'],
        ['sam', 'sdqenYBe', '助火课堂火星店'],
        ['高途', 'KeODhCSf', '趣恒精品课'],
        ['作业帮', 'MxIdjKza', '小蓝帮安选图书三号店'],
        ['猿辅导', 'VgkrinYD', '编程猿少儿编程创造营'],
        ['学丞刘晓艳', 'iMrgazEv', '学丞官方旗舰店'],
        ['学丞刘晓艳', 'EtLNgwkX', '学丞晓艳教育'],
        # ['学丞刘晓艳', 'RmcPYMgl', '学丞晓艳英语'],
        # ['学丞刘晓艳', 'gPRfOOhG', '学丞书写用品旗舰店'],
        # ['学丞刘晓艳', 'ckZVQCXQ', '学丞教育旗舰店'],
        # ['学丞刘晓艳', 'udIUbaKx', '学丞图书旗舰店'],
        # ['高中地理叶茂老师', 'shOKtBaL', '枝繁叶茂知识分享'],
        # ['師者陈墨（高中）', 'MDgrnYrj', '择数图书'],
        # ['王熙老师物理/大白满分数学', 'auPKNlMM', '仰星教育图书'],
        # ['王熙老师物理/大白满分数学', 'PTTqQPHT', '仰星智慧课堂'],
        # ['王熙老师物理/大白满分数学', 'MYbFkgKF', '仰星未来'],
        # ['王熙老师物理/大白满分数学', 'bVURdgKF', '仰星优选课堂'],
        # ['王熙老师物理/大白满分数学', 'TubxemdZ', '仰星精选课堂'],
        ['豆神', 'NBnSoNQo', '豆神双语时代'],
        ['猿辅导', 'dbnkbqHs', '斑马英语企业店'],
        ['sam', 'feKykIkX', '助火课堂研习社'],
        ['猿辅导', 'EyMJjOkX', '斑马智学启蒙书苑'],
        ['sam', 'ZZYWXrBe', '助火课堂文轩店'],
        ['高途', 'LuiNRqdZ', '雅识创界'],
        ['小学数学张老师', 'rzRfPiYD', '张文晖提分真题'],
        ['猿辅导', 'LaJygRDU', '斑马百科小店'],
        ['清华沙沙', 'zpyKExEv', '清华沙沙企业店'],
        ['清华沙沙', 'YCJejYZh', '清华沙沙云上书屋'],
        ['清华沙沙', 'ISaIvmBr', '星灿图书优选'],
        ['希望学', 'rtMcEIkX', '希望学初中企业店'],
        ['希望学', 'ybBzvzNI', '希望学满分图书'],
        ['毛毛虫', 'MApmICXQ', '毛毛虫知课教育'],
        ['毛毛虫', 'ZKVGIrZh', '毛毛虫咯吱教育'],
        ['猿辅导', 'YbMxFWBe', '斑马启蒙图书企业店'],
        ['星际光年', 'iyXeiKEv', '星际光年优启课'],
        ['叫叫', ' EnVYxyXQ', '叫叫阅读优选店'],
        ['毛毛虫', 'hwEDvhgi', '毛毛虫英语咨询'],
        ['新东方', 'tEKabXqO', '杭州新东方素质成长中心'],
        ['新东方', 'roBHFYBe', '国际英语提能教育'],
        ['猿辅导', 'MIrhyngl', '小猿教辅'],
        ['sam', 'ZJgnDPdq', '助火课堂智慧店'],
        ['希望学', 'TWdnAmPW', '希望学初中企业3店'],
        ['毛毛虫', 'jQzBolMM', '毛毛虫阅和读企业店'],
        ['高途', 'jOjwSlKx', '千峰元书途严选店'],
        ['作业帮', 'LSCBeted', '帮帮图书营'],
        ['作业帮', 'LTvAdPIk', '帮帮小初臻选'],
        ['作业帮', 'ZZuJkoIk', '小蓝帮安选图书二号店'],
        ['小学数学张老师', 'RnWgQYYD', '浪起名师企业店'],
        ['作业帮', 'HkbggeBr', '学习营冲锋号店'],
        ['猿辅导', 'ZaaCnZIk', '猿编程智能AI'],
        ['豌豆思维', 'graWHWZh', '豌豆思维官方旗舰店'],
        ['豌豆思维', 'WsQrsjZY', '豌豆素质'],
        ['杨妈英语思维', 'HdEjXKv', '前沿流量'],
        ['杨妈英语思维', 'NhJTqpaL', '清芬教育'],
        ['星际光年', 'tosVzPIk', '星际光年优选课'],
        ['星际光年', 'xWhbexza', '星际光年择优课'],
        ['星际光年', 'tyQdDted', '星际光年全优课'],
        ['星际光年', 'oVkmhPHT', '星际光年优品课'],
        ['星际光年', 'wwRYYfLV', '星际光年优享课堂'],
        ['星际光年', 'IiTaOeBr', '星际光年优学课'],
        ['星际光年', 'HjTMWwSC', '星际光年优智课'],
        ['星际光年', 'BBTyapaL', '星际光年课堂'],
        ['星际光年', 'jpyXQNcp', '星际光年享学星球'],
        ['星际光年', 'ILiErHkX', '星际光年优创课'],
        ['sam', 'ywlqsKSf', '助火课堂乐学店'],
        ['希望学', 'ieeQLxKF', '希望学教辅企业店'],
        ['希望学', 'lWQiHFKx', '希望学图书企业店'],
        ['高途', 'mrXKIbIP', '玖众文化'],
        ['希望学', 'ZLIoiJdq', '学习好物宝库'],
        ['作业帮', 'pGbppOeS', '初中学习提升营'],
        ['猿辅导', 'SxMLldhG', '小袁学院'],
        ['猿辅导', 'lxyZrern', '小猿素养辅导课'],
        ['希望学', 'KtqqPiza', '希望学初中企业2店'],
        ['希望学', 'rzmzkYrj', '希望学高分图书'],
        ['作业帮', 'qvSuXqPW', '作业帮直播课电子教育旗舰店'],
        ['作业帮', 'twiwmEqO', '作业帮教辅推荐'],
        ['高途', 'VeEuGzLw', '高途语言课堂'],
        ['叫叫', 'EaGXxSqO', '叫叫阅读官方旗舰店'],
        ['潘潘', 'gXWdDDMM', '清华潘潘思维成长'],
        ['潘潘', 'IBFdahZY', '红山竹小店'],
        ['潘潘', 'dylibHkX', '斯佳彤文化坊'],
        ['豆神', 'WsHBWYZh', '熹瑶课堂'],
        ['作业帮', 'FQDUncKx', '华中世通学习优品'],
        ['希望学', 'skOEnYBe', '希望小学教辅优选'],
        ['sam', 'eRyrmmBr', '助火课堂书香汇'],
        ['猿辅导', 'izEqmdhG', '猿辅导教育旗舰店'],
        ['高途', 'sIwJdeUJ', '高途心理家'],
        ['高途', 'izRskYYD', '高途雅思畅学营'],
        ['高途', 'cJVsSDgi', '鹿寻文化'],
        ['作业帮', 'YlWjHYYD', '帮帮大阅读'],
        ['希望学', 'IbJhmHNE', '素养启蒙教育'],
        ['有道', 'JrKVUJUm', 'YD升学教育店铺'],
        ['高途', 'pSTWodDN', '途智文化'],
        ['高途', 'RslyrSDU', '智慧航迹图书'],
        ['猿辅导', 'DiVtnhgi', '猿起图书教辅'],
        ['毛毛虫', 'yJaDKxza', '毛毛虫文化店'],
        ['毛毛虫', 'VfhMGVkH', '毛虫李洁英语企业店'],
        ['毛毛虫', 'hAIMQhZY', '毛毛虫英语老师'],
        ['毛毛虫', 'BOvfTBaL', '毛毛虫老师英语'],
        ['毛毛虫', 'LHqliKSf', '毛毛虫英语咨询店'],
        ['毛毛虫', 'uQGdnHeS', '毛毛虫英语店'],
        ['毛毛虫', 'yJaDKxza', '毛毛虫文化店'],
        ['sam', 'OzWGIphG', '助火课堂优选店'],
        ['sam', 'CSnSLJBe', '益智园优品店'],
        ['sam', 'TPTSVeUJ', '助火课堂悦书坊'],
        ['sam', 'JgLCRINE', '教育臻选堂'],
        ['高途 ', 'GQZRxSed', '途乐书坊'],
        ['毛毛虫', 'dpvsRdkX', '毛毛虫英语企业店铺'],
        ['作业帮', 'sRupgfLV', '作业帮小初教辅店'],
        ['sam', 'DRSJSkUJ', '助火课堂甄选店'],
        ['陈心', 'gGSfqfNE', '趣满分浪起教育名师'],
        ['毛毛虫', 'AvYUTmPW', '毛毛虫咨询'],
        ['毛毛虫', 'rhmJFJdq', '毛毛虫英语企业店'],
        ['毛毛虫', 'aSEtYqBr', '毛毛虫文化传播'],
        ['毛毛虫', 'mXAAobQo', '毛毛虫企业店'],
        ['毛毛虫', 'xXDlOKKF', '毛毛虫李洁英语店'],
        ['毛毛虫', 'LHqliKSf', '毛毛虫李洁教育'],
        ['毛毛虫', 'qVbFWbaB', '毛毛虫教育'],
        ['潘潘', 'HcEOVILV', '潘潘的书架'],
        ['小学数学张老师', 'zUgLnocR', '趣满分浪起超级名师'],
        ['作业帮', 'gYmPngrj', '帮帮百分优品图书二号店'],
        ['雪梨', 'cnBUsAZY', '雪梨老师自然拼读'],
        ['雪梨', 'oBixosQb', '雪梨老师英语书籍'],
        ['雪梨', 'BmQnHTHs', '雪梨老师英语教育'],
        ['雪梨', 'TvVCcdr', '雪梨老师英语'],
        ['雪梨', 'FgoNOjrn', '雪梨老师图书旗舰店'],
        ['雪梨', 'dDHnMueS', '雪梨老师图书'],
        ['猿辅导', 'YTKzdwNE', '小猿素养'],
        ['作业帮', 'XGzwkCkH', '小初图书教辅2号店'],
        ['高途', 'ZDvTVsdq', '北京加紫优品'],
        ['高途', 'tUoLMCSf', '知至阅读书屋'],
        ['高途', 'FyoiejYg', '凡火文化'],
        ['高途', 'sIwJdeUJ', '高途心理家'],
        ['豆神', 'OLKxmwqt', '豆神学习大课堂'],
        ['赛先生科学', 'CslPKrdq', '赛先生科学'],
        ['赛先生科学', 'wioxwVqO', '赛先生科学科创'],
        ['赛先生科学', 'qGFJkyNI', 'TouchBox小创客鳄鱼盒'],
        ['猿辅导', 'nPOLWJBe', '小猿图书优选'],
        ['猿辅导', 'zLcVvdhG', '猿力教育图书专营店'],
        # ['猿辅导', 'OJYPjqBr', '猿起教育专营店'],
        ['猿辅导', 'caVZCKEv', '斑马世界官方旗舰店'],
        ['猿辅导', 'XFCxWoQb', '海豚AI学企业店'],
        ['猿辅导', 'zsLBtpQb', '猿辅导学习文化旗舰店'],
        ['猿辅导', 'HUnpXDMM', '猿辅导图书旗舰店'],
        ['猿辅导', 'fcfEhhgi', '猿辅导北京猿力科技有限公司教育专卖店'],
        ['猿辅导', 'JCEnaPn', '小猿口算'],
        ['猿辅导', 'gzPliwSC', '海豚AI学'],
        ['猿辅导', 'TAKsIxEv', '猿力图书店铺'],
        ['猿辅导', 'HjeXIvSC', '猿辅导官方旗舰店'],
        ['猿辅导', 'rjSChUDN', '小猿素养教育'],
        ['猿辅导', 'KEuFkggl', '小猿中学教辅图书'],
        ['猿辅导', 'btNwjSDU', '猿辅导图书'],
        ['猿辅导', 'refnioHT', '小猿中学教育'],
        ['猿辅导', 'NRQEWGed', '小猿图书严选'],
        ['猿辅导', 'dcSyQbIP', '小猿图书'],
        ['猿编程', 'ucoCsNDU', '猿编程'],
        ['猿编程', 'ORjMzqUJ', '猿编程机器人'],
        ['猿编程', 'YMAmEArn', '猿编程科技少年'],
        ['斑马-课类', 'nvzPMUA', '斑马官方旗舰店'],
        ['斑马-课类', 'caVZCKEv', '斑马世界官方旗舰店'],
        ['斑马-课类', 'HGPZUVed', '斑马图书旗舰店'],
        ['斑马-课类', 'sqNvsaKx', '斑马百科'],
        ['斑马-课类', 'PgPpGAZY', '斑马世界好物专卖店'],
        ['斑马-课类', 'UJbfDLaB', '猿力斑马智学专卖店'],
        ['斑马-课类', 'JkXUsIkX', '斑马智学'],
        ['斑马-课类', 'zkgplHeS', '原力斑马官方旗舰店'],
        ['作业帮', 'tvYkIocR', '作业帮小学读书创作'],
        ['作业帮', 'EUtrZhR', '作业帮图书旗舰店'],
        ['作业帮', 'rPmZGdkX', '作业帮图书'],
        ['作业帮', 'hECRbELw', '作小帮'],
        ['作业帮', 'Xlkhide', '作业帮直播课旗舰店'],
        ['作业帮', 'LjptrMKF', '作业帮直播课图书旗舰店'],
        ['作业帮', 'yHlyaISC', '作业帮图书旗舰店'],
        ['作业帮', 'YVpcpArn', '作业帮初中部'],
        ['作业帮', 'OxUiTbdZ', '作业帮图书旗舰店'],
        ['作业帮', 'GmVtlMKF', '作业帮小蓝帮图书专卖店'],
        ['作业帮', 'iWliNZUm', '作业帮鲸准练'],
        ['作业帮', 'bLXyJXLw', '作业帮教辅'],
        ['作业帮', 'MAFNuYBe', '千帆小初教辅'],
        ['作业帮', 'DNvMvSqO', '帮帮智选图书'],
        ['作业帮', 'JQPcMOkX', '作业帮大阅读'],
        ['作业帮', 'vAjEChPW', '作业帮初中帮选'],
        ['作业帮', 'ipEgXwqt', '作业帮教辅的店'],
        ['作业帮', 'fatdQQzK', '初中精选教辅企业店'],
        ['作业帮', 'umyeCfLV', '帮选教辅图书'],
        ['作业帮', 'wkfSRfXz', '作业帮小学图书'],
        ['作业帮', 'kWwSMRcp', '作业帮小学图书教辅'],
        ['作业帮', 'qPTGuNQo', '作业帮素养图书'],
        ['作业帮', 'CZfIJxza', '作业帮学习营'],
        ['作业帮', 'uZwSiQSC', '作业帮爱学堂'],
        ['作业帮', 'esXLMkIP', '小帮高中教辅'],
        ['作业帮', 'HnMvVLaB', '爱芝士图书小店'],
        ['作业帮', 'eUvPubHs', '作业帮素养培训'],
        ['作业帮', 'imIOeWrj', '数芽图书小店'],
        ['作业帮', 'LTtRvzNI', '初中学习冲刺营'],
        ['作业帮', 'SinqeELw', '作业帮帮小读', ],  # 7.22
        ['作业帮', 'xefJBMgl', '作业帮大素养'],
        ['作业帮', 'HPanvQNE', '数二芽图书'],
        ['高途', 'CJCLMucR', '途乐教辅教材小店'],
        ['高途', 'vRMHIVed', '高途课堂'],
        ['高途', 'JMyQylKx', '高途培训旗舰店'],
        ['高途', 'ftxWXXI', '高途云集教育专卖店'],
        ['高途', 'yHBzZqG', '高途学考旗舰店'],
        ['高途', 'ruSIhOqt', '高途图书'],
        ['高途', 'PtPAvArn', '高途图书专营店'],
        ['高途', 'MAXxoWBe', '途乐图书教辅小店'],
        ['高途', 'QRQIpCSf', '高途学习用品'],
        ['高途', 'jDGwIngl', '高途高中图书'],
        ['高途', 'fJgOeDB', '高途教育旗舰店'],
        ['高途', 'QxSJoKSf', '高途课堂官方旗舰店'],
        ['高途', 'owcWLvXz', '高途学习'],
        ['高途', 'Pfiurak', '高途北京高途云帆科技有限公司图书专卖店'],
        ['高途', 'xAyWiWZh', '高途青少素质成长'],
        ['高途', 'qUnaRted', '北京高途雅思教育科技有限公司967企业店'],
        ['高途', 'jItlvmdZ', '拓聚图书文娱'],
        ['高途', 'fMpgJhgi', '拓聚学习大课堂'],
        ['高途', 'tLnFKYYD', '万聚大课堂'],
        ['高途', 'xBZnaPn', '智慧课堂'],
        ['高途', 'KDhmGnYD', '高途悦读写'],
        ['高途', 'zTXqhJHT', '高途高中课堂'],
        ['高途', 'EmGtHrUm', '高途菁英课堂'],
        ['高途', 'nDltAJHT', '高途微力图书专卖店'],
        ['高途', 'TqubttDU', '途书阁教辅小店'],
        ['高途', 'vuMzpLIP', '智慧家长'],
        ['高途', 'rifaNPQb', '高途书籍店铺'],
        ['高途', 'SIMdmXLw', '高途云途图书店'],
        ['高途', 'xYUdJiYD', '苏州国略文化有限公司'],
        ['高途', 'gutouISC', '云知识图书企业店'],
        ['高途', 'NSlvRVkH', '趣文文化'],
        ['高途', 'ABeAYkdZ', '途途文化'],
        ['高途', 'EQqySyza', '昕火文化'],
        ['高途', 'DJbQZhZY', '途途上海图书'],
        ['高途', 'HduLAHNE', '高途雅思'],
        ['高途', 'rPkzpUaL', '昕昕高途书店'],
        ['高途', 'TUXbQbQo', '高途语言学习'],
        ['高途', 'QLTfelKx', '七二文化'],
        ['高途', 'stIxIBQb', '高途高中教辅'],
        ['高途', 'VJvcizXQ', '高途文具礼品'],
        ['高途', 'BPAPEBDN', '鸿途图书小店'],
        ['高途', 'LQjXoGDU', '前途无量图书小店'],
        ['高途', 'TGDNkbQo', '高途教辅'],
        ['高途', 'QQEMmazK', '泰学文化'],
        ['高途', 'YNTmrJUm', '若然文化'],
        ['高途', 'LTlunRDU', '可途文化'],
        ['高途', 'weIzLfSC', '高途语界雅思'],
        ['高途', 'vzDvNjMM', '美好家庭关系'],
        ['高途', 'YbSKSZUm', '慧选智阅图书'],
        ['希望学', 'fTrKpRcp', '希望学'],
        ['希望学', 'BPuDXQXz', '融趣希望学企业店'],
        ['希望学', 'IEOWAVed', '教辅图书甄选'],
        ['希望学', 'VbzIfUaL', '希望精选图书'],
        ['希望学', 'ybXGKgKF', '希望学小学'],
        ['希望学', 'HXMbbwSC', '希望学素养'],
        ['希望学', 'hMvcCTUJ', '甄选教辅书屋'],
        ['希望学', 'cpbkXAYg', '希望优选图书'],
        ['希望学', 'YtODkrBe', '希望精选图书2店'],
        ['希望学', 'chErhkIP', '学习好物驿站'],
        ['希望学', 'mIDvLqHs', '希望学小学精选'],
        ['希望学', 'GlqfMCkH', '希望优课'],
        ['希望学', 'LlWjuGDU', '初中优选图书教辅'],
        ['希望学', 'yEdFrMMc', '学霸图书甄选'],
        ['希望学', 'aIpGtcMM', '满分伴学甄选'],
        ['新东方', 'oxLXKkUJ', '新东方云书官方旗舰店'],
        ['新东方', 'JjJVgQT', '新东方比邻官方旗舰店'],
        ['新东方', 'wzxJykQo', '新东方官方旗舰店'],
        ['新东方', 'jNuGSNH', '北京新东方大愚图书音像有限公司'],
        ['新东方', 'OKdMQDrn', '新东方满天星图书'],
        ['新东方', 'oQCBumUJ', '比邻东方国际中文'],
        ['新东方', 'NacqWQT', '新东方大愚文化官方旗舰店'],
        ['新东方', 'siPIKdDN', '新东方满天星教育'],
        ['新东方', 'WfFdxdeS', '北京新东方雅思培训'],
        ['新东方', 'ZdUCnQT', '新东方在线'],
        ['新东方', 'daQGAbaB', '武汉比邻东方教育科技有限公司'],
        ['新东方', 'AhuDKgYD', '新东方欧亚教育'],
        ['新东方', 'FnhESMEv', '新东方小店'],
        ['新东方', 'bqjUGgrj', '新东方比邻甄选'],
        ['新东方', 'DsXxzYgl', '新东方家庭教育的小店'],
        ['新东方', 'trMUvgYD', '智能学习好物'],
        ['新东方', 'ClireHqt', '书小加专营店'],
        ['新东方', 'qIhZQNhu', '苏州新东方编程'],
        ['新东方', 'LAEsmtkH', '新东方智能教辅'],
        ['新东方', 'QioaclKx', '梦汇圆'],
        ['新东方', 'xcuLFnYD', '北京维泽英语店铺'],
        ['豆神', 'aYKAkGhu', '豆神甄选时代店'],
        ['豆神', 'cgnoJGaB', '豆神书书'],
        ['豆神', 'tCavFpQb', '承启未来企业店'],
        ['豆神', 'WKUFFcMM', '窦昕文言文 华语未来'],
        ['豆神', 'YBePgFzK', '予文旅游企业店'],
        ['豆神', 'Pwpgbcgi', '豆神图书旗舰店'],
        ['豆神', 'QjMybXed', '秣马未来企业店'],
        ['豆神', 'VGyLxdDN', '豆神未来教育企业店'],
        ['豆神', 'ZKOFcUW', '中文未来'],
        ['豆神', 'dIFRqNQo', '豆神教育旗舰店'],
        ['豆神', 'ZdkjwhYg', '豆神明兮企业店'],
        ['豆神', 'qgoBsZBe', '豆神文娱企业店'],
        ['豆神', 'usfoxLIP', '豆神世纪'],
        ['叫叫阅读', 'BzbdxkQo', '小鸡叫叫'],
        ['叫叫阅读', 'nDjqdQXz', '小鸡叫叫JOJO'],
        ['叫叫阅读', 'asvRAHJ', '小鸡叫叫福利社'],
        ['叫叫阅读', 'yMSzshR', '小鸡叫叫旗舰店'],
        ['有道', 'xfPIKfSC', '有道官方旗舰店'],
        ['有道', 'mwLaGxXQ', '有道网易图书专卖店'],
        ['有道', 'voJnpbQo', '有道临界点教育专卖店'],
        ['有道', 'EpzHAwqt', '有道精品课教育店铺'],
        ['有道', 'CjNWifLV', 'youdao有道教育专卖店'],
        ['有道', 'zvoSGBcR', '有道网易教育专卖店'],
        ['有道', 'nCULgczK', '有道领世官方旗舰店'],
        ['有道', 'BchVHkQo', '有道有道图书专卖店'],
        ['有道', 'JlfFwTBr', '有道精品课初中店铺'],
        ['有道', 'xjADNuqt', '有道精品书官方旗舰店'],
        ['有道', 'YXIGIzz', '有道教育旗舰店'],
        ['有道', 'zjfQqwqt', '有道图书专营店'],
        ['有道', 'LpqLPWUm', '半小书图书旗舰店'],
        ['有道', 'CygYTUaL', 'youdao网易有道图书专卖店'],
        ['有道', 'IEXjAGaB', '思享图书'],
        ['有道', 'NgyVpXE', '有道乐读教育旗舰店'],
        ['有道', 'McXaMFEy', '有道博闻教育店铺'],
        ['有道', 'GYIbwtkH', 'youdao领世'],
        ['有道', 'PgNxxdDN', '有道博闻教育旗舰店'],
        ['猿辅导', 'PsXKUPaL', '小猿图书教辅'],
        ['猿辅导', 'epyylqdZ', '小猿图书店'],
        ['猿辅导', 'gCAYMnZh', '猿起教辅图书'],
        ['高途', 'RucWlSqO', '阶高文化精选'],
        ['高途', 'hGeUVqUJ', '高途美好家庭'],
        ['高途', 'dghLAIkX', '雄兵志略'],
        ['高途', 'TZtlDGaB', '瑞之和'],
        ['高途', 'QELfmlgi', '志学未来图书'],
        ['高途', 'GFfYrVkH', '简学文化'],
        ['高途', 'evygLLHs', '有路图书店'],
        ['高途', 'OPsujINE', '陌上花文化用品店'],
        ['高途', 'ZowcXoIk', '捷睿通图书店'],
        ['高途', 'qajJfLQo', '大展宏途教辅小店'],
        ['高途', 'ZkBVCsQb', '前途似锦图书小店'],
        ['高途', 'iVHOUYrj', '书途文化'],
        ['高途', 'jYthkXqO', '蓝山竹'],
        ['高途', 'rifaNPQb', '奇迹书馆'],
        ['高途', 'bDrjdScp', '简浩文化'],
        ['作业帮', 'CRdifxEv', '数三芽图书'],
        ['新东方', 'srLtUPaL', '英语学习精选'],
        ['猿辅导', 'eCMLwnYD', '学生素养辅导提升'],
        ['高途', 'IeBStaXz', '途书教辅小店'],
        ['新东方', 'dYZHoHkX', '苏州新东方素质素养'],
        ['猿辅导', 'AwTdPqUJ', '猿力图书优选店'],
        ['作业帮', 'bXJFUShu', '帮帮学习图书'],
        ['作业帮', 'VqRzQWPA', '作业帮矩尺图书专卖店'],
        ['猿辅导', 'UpDTGUeS', '小猿素养店'],
        ['猿辅导', 'vUxanaKx', '猿力素养严选'],
        ['猿辅导', 'hgOwZeBr', '猿力优选图书'],
        ['作业帮', 'kkXRULaB', '小蓝帮贰安图书'],
        ['作业帮', 'bFSadRcp', '行稳致远图书'],
        ['高途', 'WWIebZUm', '神算子文化'],
        ['高途', 'JQTPVPIk', '学思乐'],
        ['高途', 'VMkhLCSf', '简闻文化'],
        ['新东方', 'hMWFDmBr', '北京比邻东方'],
        ['高途', 'cZtStDgi', '大展鸿途小店'],
        ['高途', 'gThAwWrj', '奇兔文化'],
        ['猿辅导', 'lxyZrern', '小猿素养辅导课'],
        ['作业帮', 'ddFXUIkX', '小蓝帮安选图书'],
        ['高途', 'UkCZeUeS', '高途雅思领航'],
        ['高途', 'ydRxKxKF', '高途素养'],
        ['豆神', 'YBePgFzK', '予文旅游企业店'],
        ['新东方', 'TlBQULQo', '新东方大学生英语'],
        ['高途', 'tcFRnCkH', '讯言文化'],
        ['高途', 'MeGzAYYD', '高途教辅图书'],
        ['高途', 'QYBiQvEy', '启迪图书'],
        ['新东方', 'oEnjqbHs', '新东方师训讲堂'],
        ['高途', 'laJcAArn', '拓聚图图文化'],
        ['高途', 'uXkiQHeS', '途言文化'],
        ['高途', 'VgOlNCNI', '木木颜图书企业店'],
        ['作业帮', 'pnIHUBDN', '帮帮精品推荐'],
        ['作业帮', 'OBEqadkX', '帮小读分级阅读'],
        ['作业帮', 'BBHLwpDN', '小蓝帮贰安图书二号店'],
        ['作业帮', 'IZizHQSC', '华中世通训练营'],
        ['新东方', 'ggpIenZh', '苏州新东方素质成长中心'],
        ['新东方', 'ToXsNkHs', '东方智学英语'],
        ['新东方', 'hMWFDmBr', '北京比邻东方'],
        ['作业帮', 'GNgHvEqO', '帮帮小学图书'],
        ['高途', 'xETlGgMc', '都学汇文化'],
        ['豆神', 'HChyEIkX', '豆神成长中心'],
        ['高途', 'xETlGgMc', '都学汇文化'],
        ['高途', 'PtqKdBQb', '雅途书阁'],
        ['作业帮', 'gSjriWrj', '帮帮优品精选'],
        ['高途', 'WKlXeJdq', '众微通文化'],
        ['猿辅导', 'yaCyvueS', '天天智慧书屋'],
        ['作业帮', 'BgHQJUcR', '小初福利社'],
        ['作业帮', 'cgmbfcMM', '华中世通训练营地'],
        ['高途', 'oafdYBaL', '智识领航图书'],
        ['高途', 'gsjCjnrj', '智慧轨迹图书'],
        ['高途', 'KhuiNigl', '泽通图书专营店'],
        ['高途', 'DJbQZhZY', '途途上海图书'],
        ['高途', 'xegJwzz', '高途名师教辅图书'],
        ['高途', 'HYLefHLV', '高途语文'],
        ['高途', 'izRskYYD', '善文文化'],
        ['高途', 'Ngzrjthu', '山誉誉文化'],
        ['高途', 'eqoUYeUJ', '高途昆明高途云集科技有限公司专卖店'],
        ['高途', 'JUFsCsdq', '博识探索图书'],
        ['叫叫阅读', 'BzbdxkQo', 'JOJOUP的文学应用'],
        ['作业帮', 'eQNVQkUJ', '作业帮清北之路超级名师'],
        ['作业帮', 'cgmbfcMM', '作业帮大通关'],
        ['作业帮', 'YnTStWBe', '小学大通关教辅'],
        ['猿辅导', 'NyYLFGDU', '猿力精选图书'],
        ['斑马-课类', 'cmivxtkH', '斑马猿起图书专卖店'],
        ['高途', 'TngFObHs', '高途素养学习'],
        ['高途', 'cqSHHAYg', '玖辰缘文化'],
        ['豆神', 'TeXhNnZh', '豆神知明而行企业店'],
        ['新东方', 'xcRKaBY', '源源书苑'],
        ['新东方', 'PXYtHBQb', '杭州新东方编程'],
        ['作业帮', 'CvWXWzSf', '羲和光图书教辅'],
        ['猿辅导', 'bcJYvkQo', '小猿中学图书'],
        ['高途', 'JlaPfsUm', '悦学帮智慧店'],
        ['高途', 'fiCcEFzK', '睿章图书专营店'],
        ['高途', 'qGusbbIP', '春凌图书'],
        ['高途', 'AxSoiAPW', '高途教育优选'],
        ['高途', 'miSGveUJ', '高途云集学堂'],
        ['希望学', 'VPlOIzNI', '希望学小学图书精选'],
        ['希望学', 'IOGjeaEy', '高分图书甄选'],
        ['平行线', 'qfAFHySf', '根源学习'],
        ['平行线', 'ahzLgXqO', '平行线数学思维'],
        ['平行线', 'BRoRaPQb', '根源佳选数学思维小店'],
        ['平行线', 'BxMfJBcR', '根源思维精选'],
        ['平行线', 'LZqftxza', '根源数学思维馆'],
        ['平行线', 'CQmWCYZh', '根源数学思维小店'],
        ['猿辅导', 'gcNZenZh', '小猿图书精选'],
        ['作业帮', 'vIvoIaEy', '华中世通图书教辅'],
        ['作业帮', 'HEcUXOkX', '帮帮臻品精选'],
        ['作业帮', 'MEySMggl', '小初图书教辅3号店'],
        ['作业帮', 'ejTNDmBr', '华中世通教辅大通关'],
        ['作业帮', 'iWWntYrj', '至美乐学图书小店'],
        ['高途', 'ObAJWdqt', '高途学苑'],
        ['高途', 'nvdWkYrj', '高途智慧学园'],
        ['高途', 'nduhPrZh', '智慧辰时图书'],
        ['高途', 'binEZScp', '易来是文化'],
        ['新东方', 'rnVvcPdq', '苏州新东方智慧学习'],
        ['希望学', 'BwAxTuhG', '优课教辅'],
        ['猿辅导', 'UGNWOocR', '小猿图书甄选'],
        ['新东方', 'ChnwazNI', '新东方高中优学教辅'],
        ['希望学', 'xgfrPggl', '何丽教育'],
        ['希望学', 'RTcmTXhu', '希望学小学'],
        ['希望学', 'uexLcUeS', '希望精选书屋'],
        ['希望学', 'XnqPKCkH', '严选高分书屋'],

    ]
    for key in keys:
        for time_l in time_list:
            shangpin_fenxi(key[0], key[1], key[2], time_l[0], time_l[1], 1,headers,num_type)  # 全部商品
    print("抓取完毕")
    # 6:20到19:31
    # 循环导出数据
    for time_l in time_list:
        time_str = time_l[0]
        time_str2 = time_l[1]
        print(time_str)
        # 猿辅导
        query_and_export(['猿辅导', '猿编程', '斑马-课类'], f"猿辅导{time_str}数据", time_str, time_str2)
        # 作业帮
        query_and_export(['作业帮', '作业帮'], f"作业帮{time_str}数据", time_str, time_str2)
        # 高途
        query_and_export(['高途', '高途'], f"高途{time_str}数据", time_str, time_str2)
        # 希望学
        query_and_export(['希望学', '希望学'], f"希望学{time_str}数据", time_str, time_str2)
        # 新东方
        query_and_export(['新东方', '新东方'], f"新东方{time_str}数据", time_str, time_str2)
        # 有道
        query_and_export(['有道', '有道'], f"有道{time_str}数据", time_str, time_str2)
        # 豆神
        query_and_export(['豆神', '豆神'], f"豆神{time_str}数据", time_str, time_str2)
        # 叫叫阅读
        query_and_export(['叫叫阅读', '叫叫'], f"叫叫阅读{time_str}数据", time_str, time_str2)
        query_and_export(['平行线', '平行线'], f"平行线{time_str}数据", time_str, time_str2)
        # query_and_export(['胡小群', '胡小群'], f"胡小群{time_str}数据", time_str, time_str2)
        query_and_export(['赛先生科学', '赛先生科学'], f"赛先生科学{time_str}数据", time_str, time_str2)
        query_and_export(['sam', 'sam'], f"sam{time_str}数据", time_str, time_str2)
        query_and_export(['陈心', '陈心'], f"陈心{time_str}数据", time_str, time_str2)
        query_and_export(['毛毛虫', '毛毛虫'], f"毛毛虫{time_str}数据", time_str, time_str2)
        query_and_export(['潘潘', '潘潘'], f"潘潘{time_str}数据", time_str, time_str2)
        query_and_export(['小学数学张老师', '小学数学张老师'], f"小学数学张老师{time_str}数据", time_str, time_str2)
        query_and_export(['雪梨', '雪梨'], f"雪梨{time_str}数据", time_str, time_str2)
        query_and_export(['豌豆思维', '豌豆思维'], f"豌豆思维{time_str}数据", time_str, time_str2)
        query_and_export(['杨妈英语思维', '杨妈英语思维'], f"杨妈英语思维{time_str}数据", time_str, time_str2)
        # query_and_export(['英语想当当', '英语想当当'], f"英语想当当{time_str}数据", time_str, time_str2)
        query_and_export(['星际光年', '星际光年'], f"星际光年{time_str}数据", time_str, time_str2)
        query_and_export(['清华沙沙', '清华沙沙'], f"清华沙沙{time_str}数据", time_str, time_str2)
        query_and_export(['学丞刘晓艳', '王熙老师物理', '師者陈墨（高中）', '高中地理叶茂老师'], f"高中其它{time_str}数据", time_str, time_str2)
        query_and_export(['火花', '火花'], f"火花{time_str}数据", time_str, time_str2)
        query_and_export(['晓晶老师语文', '晓晶老师语文'], f"晓晶老师语文{time_str}数据", time_str, time_str2)
        # query_and_export(['王熙老师物理/大白满分数学', '王熙老师物理/大白满分数学'], f"王熙老师物理{time_str}数据", time_str,
        #                  time_str2)
        # query_and_export(['師者陈墨（高中）', '師者陈墨（高中）'], f"師者陈墨（高中）{time_str}数据", time_str, time_str2)
        # query_and_export(['高中地理叶茂老师', '高中地理叶茂老师'], f"高中地理叶茂老师{time_str}数据", time_str, time_str2)
    pp(num_type)  # 匹配价格
    process_excel()  # deepseek打标

    keywords = ["sam", "陈心", "毛毛虫", "潘潘", "平行线", "清华莎莎", "小学数学张老师", "雪梨", "杨妈英语思维",'晓晶老师语文']

    # 用于存储所有数据的列表
    all_data = []

    # 遍历路径下的所有文件
    for root, dirs, files in os.walk(path2):
        for file in files:
            # 检查是否是 xlsx 文件且包含任意关键字
            if file.endswith('.xlsx') and any(keyword in file for keyword in keywords):
                file_path = os.path.join(root, file)
                try:
                    # 读取 Excel 文件
                    df = pd.read_excel(file_path)
                    all_data.append(df)
                    print(f"成功读取文件: {file}")

                    # 删除文件
                    os.remove(file_path)
                    print(f"成功删除文件: {file}")
                except Exception as e:
                    print(f"处理文件失败: {file}，错误: {e}")

    # 合并所有数据
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # 保存到指定文件
        output_path = os.path.join(path2, f'ip_{time_list[0][0]}_打标结果整合.xlsx')
        combined_df.to_excel(output_path, index=False)
        print(f"合并完成，文件已保存到: {output_path}")
    else:
        print("未找到符合条件的文件，未生成合并文件。")

    print("今日数据处理完毕")








headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Cookie': 'CMM_U_C_ID=b258588b-af30-11f0-ad53-9e1cc45c2551; frontend_canary1=always; CMM_A_C_ID=2c0d32ca-ef8f-11f0-b6e2-ce9bb43445ff; tfstk=gW7sukjd3AD6M9PTHAPEFMMMiALf5WzzkjOAZs3ZMFLtHxCJLNW4js7Xl9WXDN8N_91AG9xwQKSNhisfhn8wWGSHTI553q2tk6HXNMAvgdxgteI5ucLailhGxT5-7NrMuqTMoEezUzzys1YDkjzZiPDiJQR_uCn9kFYp0C6JozzPs1FWmY6YzGy4fMR2HEK9DvCpKIOtDEBvv2dDpVdxWEpLOIvpkc3tXBLpgQutXtLYO6pHMEpAHhFC9pAvkKh2kJO3fdC_GN_E5moW_1pIkqQToh95BmujlwO6f119dGs1RCt6eHJ6EHbOLsQNSHqibEfFVtsAeJowBgO5d3S_FV65IIBp9OPqmBsfMaYMXjuVFF6X2NKIMq1JWpYB9aFqqp7BQtQ6v7uW0eQy2FIUxR-25Q6ASOGjkTCFaNxhl8MpnGRkJI_0wm9XDg7ZzLZs2mGBqqOBUWNImmYN09yAvXZGJhdHTaPQOAiDXBABUWNImmx9tB-UOWMsm; Hm_lvt_1f19c27e7e3e3255a5c79248a7f4bdf1=1770035961,1772076909,1772088578,1772173597; HMACCOUNT=7FFBB88854374778; _clck=4fq9m2%5E2%5Eg40%5E0%5E2078; LOGIN-TOKEN-FORSNS=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6MTAwMDAsImFwcFZlcnNpb24iOiIiLCJleHBpcmVfdGltZSI6MTc3Mjk5NjQwMCwiaWF0IjoxNzcyNDQ3MjgyLCJpZCI6MTQ2Nzk3ODMsImtpZCI6IkNBUy1FVERPWVVUVTMyODAtQ1RRVkhOIiwicmsiOiJiQ2pRNCIsInVjaWQiOiJiMjU4NTg4Yi1hZjMwLTExZjAtYWQ1My05ZTFjYzQ1YzI1NTEifQ._CCbYloeWtBuclfscfThhyaFPc6rIFAXSEBpoRyUlfA; Hm_lpvt_1f19c27e7e3e3255a5c79248a7f4bdf1=1772447281; Authorization-By-CAS=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOjEwMDAwLCJleHAiOjE3NzI5OTY0MDAsImlhdCI6MTc3MjQ0NzI4NCwicmsiOiJCZGRWTCIsInVuaXF1ZV9pZCI6IkNBUy1FVERPWVVUVTMyODAtQ1RRVkhOIn0.0OJISZETVnP1SqIxbah18bKrt91xMAf3Y1wkEiq3ZCA; _clsk=l6p05l%5E1772447284512%5E6%5E1%5Ek.clarity.ms%2Fcollect'
           }


if __name__ == "__main__":
    # 使用schedule库设置定时任务
    schedule.every().day.at("10:00").do(get_ribao)
    # schedule.every().day.at("08:30").do(get_xl_ribao)

    while True:
        schedule.run_pending()
        time.sleep(1)









