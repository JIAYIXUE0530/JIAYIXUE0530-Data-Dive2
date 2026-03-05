-- 创建数据库
CREATE DATABASE IF NOT EXISTS data_dive DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE data_dive;

-- 创建竞品周报数据表
CREATE TABLE IF NOT EXISTS `zb_zhoubo` (
    `竞品` varchar(20) DEFAULT NULL,
    `shop_id` varchar(30) NOT NULL COMMENT '店铺id',
    `quchong` varchar(200) NOT NULL COMMENT '去重',
    `shop_name` varchar(50) DEFAULT NULL COMMENT '店铺名字',
    `start_time` varchar(30) NOT NULL COMMENT '获取得起始时间',
    `end_time` varchar(30) DEFAULT NULL COMMENT '获取结束始时间',
    `Catgeorys_name` varchar(30) DEFAULT NULL COMMENT '分类',
    `max_commission_rate` varchar(30) DEFAULT NULL COMMENT '佣金',
    `product_id` varchar(100) NOT NULL COMMENT '商品id',
    `title` varchar(255) DEFAULT NULL COMMENT '商品名字',
    `brand_name` varchar(255) DEFAULT NULL COMMENT '品牌名字',
    `price` varchar(30) DEFAULT NULL COMMENT '价格（元）',
    `volume` varchar(30) DEFAULT NULL COMMENT '销量（个）',
    `amount` varchar(30) DEFAULT NULL COMMENT '销售额（元）',
    `author_count` varchar(30) DEFAULT NULL COMMENT '关联达人',
    `live_count` varchar(30) DEFAULT NULL COMMENT '关联直播',
    `aweme_count` varchar(30) DEFAULT NULL COMMENT '关联视频',
    `shangpin_url` varchar(255) DEFAULT NULL COMMENT '商品url',
    `update_at` datetime DEFAULT NULL COMMENT '更新时间',
    `shangp_shop_id` varchar(50) DEFAULT NULL COMMENT '商品的来源店铺',
    `shangp_shop_name` varchar(50) DEFAULT NULL COMMENT '商品的来源店铺名字',
    `shangp_brand_name` varchar(50) DEFAULT NULL COMMENT '商品的来源品牌',
    PRIMARY KEY (`quchong`) USING BTREE,
    UNIQUE KEY `unque_index` (`quchong`) USING BTREE,
    KEY `idx_start_time` (`start_time`),
    KEY `idx_shop_id` (`shop_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_jingpin` (`竞品`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='竞品销量数据表';
