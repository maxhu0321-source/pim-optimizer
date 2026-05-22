"""错误位置 → 用户友好描述映射

将技术坐标（如 PiM-1!B355）转为用户能在Excel中找到的路径指引。
"""

# Sheet名 → 中文标签
SHEET_LABELS = {
    "PiM-1": "酒店特色信息表（PiM-1）",
    "PiM-2": "房价房型信息表（PiM-2）",
    "PiM-5": "客房设施信息表（PiM-5）",
    "PMS-1.4": "PMS标准代码表 → 1.4 酒店客房",
}

# 规则ID → 用户友好的位置描述 + 查找指引
LOCATION_GUIDES = {
    # A类：跨文件
    "A01": {
        "label": "PiM房型 vs PMS房型",
        "guide": "打开PiM-2「房价房型信息表」的房型代码列，与PMS「1.4 酒店客房」的希尔顿渠道代码列逐一比对",
    },
    "A02": {
        "label": "PMS房型 vs PiM房型",
        "guide": "打开PMS「1.4 酒店客房」的希尔顿渠道代码列，确认每个代码在PiM-2中都存在",
    },
    "A03": {
        "label": "PiM房型 vs PMS房型",
        "guide": "对比PiM-2的「Number of Rooms 此房型房量」列与PMS「1.4 酒店客房」的房型数量列",
    },

    # B类：内部一致性
    "B01": {
        "label": "PiM-2 无烟房 vs PiM-5 无烟房",
        "guide": "打开PiM-2「Non-Smoking Room」列和PiM-5中搜索「Non-Smoking」行，确认数量一致",
    },
    "B02": {
        "label": "PiM-2 Bedding区域",
        "guide": "在PiM-2下方的Bedding区域，确认各床型数量加总等于酒店总房量",
    },
    "B03": {
        "label": "PiM-5 沙发/沙发床行",
        "guide": "打开PiM-5，找到「Sofa」或「Sofa Bed」行，确认数量不超过对应房型总数",
    },
    "B04": {
        "label": "PiM-2 无障碍房 vs PiM-5 无障碍房",
        "guide": "对比PiM-2「Accessible Room」列和PiM-5中无障碍相关设施行",
    },
    "B05": {
        "label": "PiM-2 连通房 vs PiM-5 连通房",
        "guide": "对比PiM-2连通房标注和PiM-5中「Connecting Room」行",
    },
    "B06": {
        "label": "PiM-5 浴袍行",
        "guide": "打开PiM-5，找到「Bathrobe」行，确认数量不超过对应房型总数",
    },

    # C类：品牌标准
    "C01": {
        "label": "PiM-2 无烟房比例",
        "guide": "在PiM-2中查看各房型的「Non-Smoking Room」列，无烟房总数应≥总房量的30%",
    },
    "C02": {
        "label": "PiM-5 连通房数量",
        "guide": "在PiM-5中找到「Connecting Room」行，总数应≥2间",
    },
    "C03": {
        "label": "PiM-2 无障碍房标注",
        "guide": "在PiM-2中查看「Accessible Room」列，至少1个房型应标注为Yes",
    },
    "C04": {
        "label": "PiM-5 SLS房型沙发床",
        "guide": "在PiM-5中找到「Sofa Bed」或「Sofa Sleeper」行，SLS房型列应有数量",
    },
    "C05": {
        "label": "PiM-2 连通房+无障碍房",
        "guide": "品牌标准要求连通房中至少1间为无障碍房",
    },
    "C06": {
        "label": "PiM-2 最大入住人数",
        "guide": "在PiM-2中查看「Max Occupancy」列，欢朋标准默认为3人",
    },
    "C07": {
        "label": "PiM-5 小冰箱",
        "guide": "在PiM-5中找到「Mini Fridge」行，普通房型列应有数量",
    },

    # D类：必填项
    "D01": {
        "label": "酒店特色信息表 → 酒店描述板块",
        "guide": "打开PiM-1，向下滚动到「Descriptions 酒店描述」区域，填写酒店中文描述",
    },
    "D02": {
        "label": "房价房型信息表 → 顶部ADR",
        "guide": "打开PiM-2，在顶部「ADR Forecast 酒店年平均房价」处填写",
    },
    "D03": {
        "label": "客房设施信息表 → 折叠床",
        "guide": "打开PiM-5，找到「Rollaways 折叠床」行，无则填0",
    },
    "D04": {
        "label": "酒店特色信息表 → 酒店电话板块",
        "guide": "打开PiM-1，找到「Telephone Number 酒店电话」区域，填写国家代码+区号+电话号码",
    },
    "D05": {
        "label": "酒店特色信息表 → SAFETY安保信息板块",
        "guide": "打开PiM-1，搜索「SAFETY」或「Fire/Safety/Security」，逐项填写Y/N",
    },
    "D06": {
        "label": "酒店特色信息表 → 城市/距离板块",
        "guide": "打开PiM-1，找到「City 城市」和「Distance 距市中心距离」，距离须≤50km",
    },
    "D07": {
        "label": "酒店特色信息表 → 到达路线板块",
        "guide": "打开PiM-1，找到「From hotel to City Center」区域，填写出租车/地铁/公交等路线",
    },
    "D08": {
        "label": "酒店特色信息表 → 经纬度",
        "guide": "打开PiM-1，找到「Online Latitude/Longitude」，注意纬度在前（中国约28-50），经度在后（约73-135）",
    },
    "D09": {
        "label": "房价房型信息表 → 无障碍房标注",
        "guide": "打开PiM-2，在「Accessible Room」列中将有无障碍房的房型标注为Yes",
    },

    # E类：格式
    "E01": {
        "label": "房价房型信息表 → 房间面积",
        "guide": "打开PiM-2，找到「Room Size」列，面积必须为正整数（不能填25.5或20-30）",
    },
    "E03": {
        "label": "酒店特色信息表 → 位置短描述",
        "guide": "打开PiM-1，找到「Location Description (Short)」，限38个字符（含空格）",
    },
    "E04": {
        "label": "酒店特色信息表 → 建筑数",
        "guide": "打开PiM-1，找到建筑数量字段，通常填1-3",
    },
    "E05": {
        "label": "酒店特色信息表 → 楼层数",
        "guide": "打开PiM-1，楼层数填总层数（如12），不要填具体楼层（如3F-12F）",
    },
    "E06": {
        "label": "酒店特色信息表 → 经纬度格式",
        "guide": "经纬度用小数格式（如40.222724），中国纬度约28-50，经度约73-135，不要填反",
    },
    "E07": {
        "label": "酒店特色信息表 → 电话格式",
        "guide": "电话号码应为7-8位数字（不含区号），如69711888",
    },
}


def get_friendly_location(rule_id: str, raw_location: str) -> str:
    """将技术位置转为用户友好描述"""
    guide = LOCATION_GUIDES.get(rule_id)
    if guide:
        return guide["label"]
    # fallback: 把 PiM-1 等替换为中文
    result = raw_location
    for key, label in SHEET_LABELS.items():
        result = result.replace(key, label)
    return result


def get_location_guide(rule_id: str) -> str:
    """获取查找指引"""
    guide = LOCATION_GUIDES.get(rule_id)
    if guide:
        return guide["guide"]
    return ""
