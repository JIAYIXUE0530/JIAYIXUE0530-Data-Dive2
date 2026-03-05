# -*- coding: utf-8 -*-
"""
蝉妈妈竞品数据爬虫 - 完整版
从蝉妈妈平台爬取竞品销量数据，用于生成竞品日报
支持存储到MySQL数据库和导出Excel
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
from dotenv import load_dotenv

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import IntegrityError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("警告: sqlalchemy未安装，MySQL存储功能不可用")

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
DB_NAME = os.getenv('DB_NAME', 'data_dive')
DB_TABLE_ZHOUBO = os.getenv('DB_TABLE_ZHOUBO', 'zb_zhoubo')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

JIEMI_KEY = 'cmmgfgehahweuuii'

# 完整店铺列表（从原始代码复制）
COMPETITOR_SHOPS = [
    ['作业帮', 'CDirgbaB', '乐学图书教辅'],
    ['作业帮', 'EIyTtRQo', '百分优品教辅'],
    ['作业帮', 'vYjDduDN', '锦学图书学习营地'],
    ['作业帮', 'EliGBLQo', '锦学图书大通关'],
    ['作业帮', 'LWYzfjrn', '矩尺学习精选'],
    ['猿辅导', 'dogdNUDN', '素养教育快乐课堂'],
    ['猿辅导', 'BLLNoYYD', '猿辅导音像旗舰店'],
    ['猿辅导', 'oVAGhBcR', '猿辅导小猿素养'],
    ['猿辅导', 'yLfxoGDU', '小猿文化屋'],
    ['猿辅导', 'hwnnPwSC', '小猿书屋'],
    ['高途', 'LAumwArn', '苏州瑞之和文化店'],
    ['高途', 'nzeUKENI', '瑞之和文化艺术精品店'],
    ['高途', 'lIOTSIkX', '知源书屋严选铺'],
    ['高途', 'EmQXmShu', '事皆顺文传'],
    ['希望学', 'uRykndkX', '希学素养甄选'],
    ['希望学', 'BZIeArdq', '希望学初中企业5店'],
    ['希望学', 'lHlvPfSC', '融趣企业店7'],
    ['豆神', 'IQYWnocR', '豆神明兮教育严选'],
    ['豆神', 'JhxLZWrj', '豆神书书企业店'],
    ['豆神', 'moWNzqBr', '豆神读写营'],
    ['叫叫', 'VEajcGed', '叫叫阅读伴学站'],
    ['叫叫', 'EaGXxSqO', '叫叫阅读官方旗舰店'],
    ['有道', 'ANVGoFEy', '长汀念派科技好货店'],
    ['有道', 'tWfhfTHs', '长汀念派科技优品小铺'],
    ['有道', 'qiZAqjgi', '有道领世精选'],
    ['新东方', 'tEKabXqO', '杭州新东方素质成长中心'],
    ['新东方', 'roBHFYBe', '国际英语提能教育'],
    ['新东方', 'oxLXKkUJ', '新东方云书官方旗舰店'],
    ['斑马', 'caVZCKEv', '斑马世界官方旗舰店'],
    ['斑马', 'nvzPMUA', '斑马官方旗舰店'],
    ['斑马', 'HGPZUVed', '斑马图书旗舰店'],
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
    ['作业帮', 'IIoNhVLw', '作业帮北京美唐科技有限公司教育专卖店'],
    ['高途', 'tFrxdNDU', '斯佳彤好课屋'],
    ['高途', 'SfUtuNcp', '佳彤臻选阁'],
    ['高途', 'CfzsIVkH', '启得隆书苑'],
    ['作业帮', 'kTXYneBr', '作业帮美唐图书专卖店'],
    ['作业帮', 'DQaIhern', '帮小帮智学图书'],
    ['希望学', 'wkgikHeS', '融趣企业店3'],
    ['火花', 'rjUbRBIk', '火花思维教育图书专卖店'],
    ['作业帮', 'snrVIZIk', '智美学习教育店'],
    ['毛毛虫', 'XppsxGaB', '毛毛虫知课企业店'],
    ['希望学', 'bDaGLAPW', '希望学小学企业店5'],
    ['猿辅导', 'VcRkAGhu', '猿起电子图书'],
    ['作业帮', 'HQtQPUDN', '帮帮秒答学堂'],
    ['作业帮', 'RkUWvTIP', '帮帮知识便利店'],
    ['作业帮', 'FkzPJINE', '智想图书学习营地'],
    ['作业帮', 'dlyBDPQb', '智想教育教辅'],
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
    ['高途', 'FqJIbjMM', '木颜图书'],
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
    ['作业帮', 'fcayFOqt', '帮帮远航精选店'],
    ['高途', 'vofzEvSC', '启得隆优选'],
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
    ['叫叫', 'EnVYxyXQ', '叫叫阅读优选店'],
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


class ChanmamaCrawler:
    def __init__(self, cookie: str = None):
        self.cookie = cookie
        self.session = None
        self.headers = None
        
    def load_cookie_from_file(self, cookie_file: str = 'cookie.txt') -> Optional[str]:
        cookie_path = Path(__file__).parent.parent / cookie_file
        if cookie_path.exists():
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
                if cookie:
                    print(f"从 {cookie_file} 加载cookie成功")
                    return cookie
        return None
    
    def init_session(self, cookie: str = None) -> bool:
        if not cookie:
            cookie = self.cookie or self.load_cookie_from_file()
        
        if not cookie:
            print("错误: 未提供cookie，请先登录蝉妈妈获取cookie")
            return False
        
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers = {
            'referer': 'https://www.chanmama.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookie': cookie
        }
        self.headers = dict(self.session.headers)
        print("会话初始化成功!")
        return True
    
    def aes_decrypt(self, data: str) -> bytes:
        key = JIEMI_KEY.encode('utf8')
        data = base64.b64decode(data)
        cipher = AES.new(key, AES.MODE_ECB)
        text_decrypted = unpad(cipher.decrypt(data))
        return gzip.decompress(text_decrypted)
    
    def get_volume_from_trend(self, days_30_volume_trend: List, target_date: str) -> int:
        if not days_30_volume_trend:
            return 0
        for day_data in days_30_volume_trend:
            if day_data.get('time_node_str') == target_date:
                return day_data.get('volume', 0)
        return 0
    
    def crawl_shop_products(
        self,
        shop_info: List,
        start_date: str,
        end_date: str,
        max_pages: int = 50,
        num_type: int = 2
    ) -> List[Dict]:
        brand = shop_info[0]
        shop_id = shop_info[1]
        shop_name = shop_info[2]
        
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
                
                for item_data in data_list:
                    product = {
                        '竞品': brand,
                        '店铺ID': shop_id,
                        '去重键': f'{shop_id}{start_date}{item_data.get("product_id")}',
                        '店铺名称': shop_name,
                        '起始时间': start_date,
                        '结束时间': end_date,
                        '分类': '全部',
                        '佣金率': f"{item_data.get('max_commission_rate')}%",
                        '商品ID': item_data.get('product_id'),
                        '商品名称': item_data.get('title'),
                        '品牌': item_data.get('brand_name'),
                    }
                    
                    if num_type == 1:
                        product['价格'] = item_data.get('sku_union_price_text', '')
                        product['销量'] = item_data.get('volume', 0)
                        product['销售额'] = item_data.get('amount', 0)
                    else:
                        days_30_volume_trend = item_data.get('days_30_volume_trend', [])
                        volume = 0
                        for day_data in days_30_volume_trend:
                            if day_data.get('time_node_str') == start_date:
                                volume = day_data.get('volume', 0)
                                break
                        product['销量'] = volume
                        product['销售额'] = ''
                        product['价格'] = ''
                    
                    product['关联达人'] = item_data.get('author_count', 0)
                    product['关联直播'] = item_data.get('live_count', 0)
                    product['关联视频'] = item_data.get('aweme_count', 0)
                    product['商品链接'] = f'https://www.chanmama.com/promotionDetail/{item_data.get("product_id")}'
                    product['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    product['商品店铺ID'] = item_data.get('shop_id', '')
                    product['商品店铺名称'] = item_data.get('shop_name', '')
                    product['商品品牌名称'] = item_data.get('brand_name', '')
                    
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
        shops: Optional[List] = None,
        num_type: int = 2
    ) -> List[Dict]:
        if not self.session:
            if not self.init_session():
                return []
        
        shops = shops or COMPETITOR_SHOPS
        all_data = []
        
        print(f"共需爬取 {len(shops)} 个店铺")
        print(f"模式: num_type={num_type} (1=平台正常返回数值, 2=平台返回区间值)")
        
        for i, shop in enumerate(shops):
            print(f"[{i+1}/{len(shops)}] ", end="")
            products = self.crawl_shop_products(shop, start_date, end_date, num_type=num_type)
            all_data.extend(products)
            time.sleep(2)
        
        return all_data
    
    def save_to_excel(
        self,
        data: List[Dict],
        output_path: str,
        filename: Optional[str] = None
    ) -> str:
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
    
    def save_to_mysql(self, data: List[Dict]) -> int:
        if not data:
            print("没有数据可保存到数据库")
            return 0
        
        if not MYSQL_AVAILABLE:
            print("MySQL存储功能不可用，跳过数据库存储")
            return 0
        
        try:
            engine = create_engine(DATABASE_URL)
            
            db_data = []
            for item in data:
                db_item = {
                    '竞品': item.get('竞品', ''),
                    'shop_id': item.get('店铺ID', ''),
                    'quchong': item.get('去重键', ''),
                    'shop_name': item.get('店铺名称', ''),
                    'start_time': item.get('起始时间', ''),
                    'end_time': item.get('结束时间', ''),
                    'Catgeorys_name': item.get('分类', '全部'),
                    'max_commission_rate': item.get('佣金率', ''),
                    'product_id': item.get('商品ID', ''),
                    'title': item.get('商品名称', ''),
                    'brand_name': item.get('品牌', ''),
                    'price': str(item.get('价格', '')) if item.get('价格') else '',
                    'volume': str(item.get('销量', 0)),
                    'amount': str(item.get('销售额', '')) if item.get('销售额') else '',
                    'author_count': str(item.get('关联达人', 0)),
                    'live_count': str(item.get('关联直播', 0)),
                    'aweme_count': str(item.get('关联视频', 0)),
                    'shangpin_url': item.get('商品链接', ''),
                    'update_at': datetime.now(),
                    'shangp_shop_id': item.get('商品店铺ID', ''),
                    'shangp_shop_name': item.get('商品店铺名称', ''),
                    'shangp_brand_name': item.get('商品品牌名称', ''),
                }
                db_data.append(db_item)
            
            df = pd.DataFrame(db_data)
            
            inserted_count = 0
            with engine.connect() as conn:
                for _, row in df.iterrows():
                    try:
                        insert_sql = text(f"""
                            INSERT INTO {DB_TABLE_ZHOUBO} 
                            (竞品, shop_id, quchong, shop_name, start_time, end_time, 
                             Catgeorys_name, max_commission_rate, product_id, title, brand_name,
                             price, volume, amount, author_count, live_count, aweme_count,
                             shangpin_url, update_at, shangp_shop_id, shangp_shop_name, shangp_brand_name)
                            VALUES 
                            (:竞品, :shop_id, :quchong, :shop_name, :start_time, :end_time,
                             :Catgeorys_name, :max_commission_rate, :product_id, :title, :brand_name,
                             :price, :volume, :amount, :author_count, :live_count, :aweme_count,
                             :shangpin_url, :update_at, :shangp_shop_id, :shangp_shop_name, :shangp_brand_name)
                            ON DUPLICATE KEY UPDATE
                            volume = VALUES(volume),
                            price = VALUES(price),
                            amount = VALUES(amount),
                            update_at = VALUES(update_at)
                        """)
                        conn.execute(insert_sql, row.to_dict())
                        conn.commit()
                        inserted_count += 1
                    except IntegrityError:
                        pass
                    except Exception as e:
                        print(f"插入数据失败: {e}")
            
            print(f"成功存储 {inserted_count} 条数据到MySQL数据库")
            return inserted_count
            
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return 0
    
    def query_from_mysql(
        self,
        start_date: str,
        end_date: str,
        brands: Optional[List[str]] = None
    ) -> List[Dict]:
        if not MYSQL_AVAILABLE:
            print("MySQL功能不可用")
            return []
        
        try:
            engine = create_engine(DATABASE_URL)
            
            query = f"""
                SELECT * FROM {DB_TABLE_ZHOUBO}
                WHERE start_time BETWEEN '{start_date}' AND '{end_date}'
            """
            
            if brands:
                brand_list = "','".join(brands)
                query += f" AND 竞品 IN ('{brand_list}')"
            
            query += " ORDER BY start_time DESC, volume DESC"
            
            df = pd.read_sql(query, engine)
            print(f"从数据库查询到 {len(df)} 条数据")
            return df.to_dict('records')
            
        except Exception as e:
            print(f"数据库查询失败: {e}")
            return []


def run_crawler(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: str = "uploads",
    cookie: str = None,
    num_type: int = 2,
    save_to_db: bool = True
) -> Dict:
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = start_date
    
    print(f"开始爬取数据: {start_date} ~ {end_date}")
    print(f"模式: num_type={num_type} (1=平台正常返回数值, 2=平台返回区间值)")
    
    crawler = ChanmamaCrawler(cookie=cookie)
    
    if not crawler.init_session():
        return {
            'success': False,
            'message': '请先提供有效的cookie',
            'filepath': '',
            'count': 0,
            'date': start_date,
            'db_count': 0
        }
    
    data = crawler.crawl_all_shops(start_date, end_date, num_type=num_type)
    
    if data:
        filepath = crawler.save_to_excel(data, output_dir)
        
        db_count = 0
        if save_to_db:
            db_count = crawler.save_to_mysql(data)
        
        return {
            'success': True,
            'message': f'成功爬取 {len(data)} 条数据',
            'filepath': filepath,
            'count': len(data),
            'date': start_date,
            'db_count': db_count
        }
    else:
        return {
            'success': False,
            'message': '爬取失败，未获取到数据',
            'filepath': '',
            'count': 0,
            'date': start_date,
            'db_count': 0
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
