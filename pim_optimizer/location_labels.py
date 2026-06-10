"""错误位置 → 用户友好描述映射

将技术坐标转为用户在PiM Pack中实际看到的路径名。
用户界面中PiM的sheet名显示为路径形式：
- "1.酒店特色信息" (即 PiM-1)
- "2.房型房价信息" (即 PiM-2)
- "5.客房设施信息" (即 PiM-5)
"""

# Sheet名 → 用户实际看到的路径名
SHEET_LABELS = {
    "PiM-1": "1.酒店特色信息",
    "PiM-2": "2.房型房价信息",
    "PiM-5": "5.客房设施信息",
    "PMS-1.4": "PMS标准代码表 → 1.4 酒店客房",
}

# 规则ID → 用户友好的位置描述 + 查找指引
LOCATION_GUIDES = {
    # A类：跨文件
    "A01": {
        "label": "2.房型房价信息 → 房型代码列",
        "guide": "打开「2.房型房价信息」找到房型代码列，与PMS「1.4 酒店客房」的希尔顿渠道代码逐一比对",
    },
    "A02": {
        "label": "PMS 1.4 酒店客房 → 希尔顿渠道代码列",
        "guide": "打开PMS「1.4 酒店客房」的希尔顿渠道代码列，确认每个代码在PiM「2.房型房价信息」中都存在",
    },
    "A03": {
        "label": "2.房型房价信息 vs PMS 1.4",
        "guide": "对比「2.房型房价信息」的房量列与PMS「1.4 酒店客房」的房型数量列，两边数字需一致",
    },

    # B类：内部一致性
    "B01": {
        "label": "2.房型房价信息 → Non-Smoking列 vs 5.客房设施信息 → Room Amenities → Non-Smoking行",
        "guide": "打开「2.房型房价信息」查看各房型的Non-Smoking列标记（Yes/No），再打开「5.客房设施信息」向下找到 Room Amenities 区域的Non-Smoking行，两处数据必须匹配：标Yes的房型无烟房数应超过半数",
    },
    "B03": {
        "label": "5.客房设施信息 → Room Amenities → Sofa/Sofa Bed行",
        "guide": "打开「5.客房设施信息」向下找到 Room Amenities 区域的 Sofa 或 Sofa Bed 行，每个房型填写的数量不能超过该房型总房间数",
    },
    "B04": {
        "label": "2.房型房价信息 → Accessible Room列 vs 5.客房设施信息",
        "guide": "对比「2.房型房价信息」的Accessible Room列和「5.客房设施信息」中无障碍相关设施行",
    },
    "B05": {
        "label": "2.房型房价信息 → 连通房 vs 5.客房设施信息 → Room Amenities → Connecting Room行",
        "guide": "对比「2.房型房价信息」连通房标注和「5.客房设施信息」Room Amenities 区域的 Connecting Room 行",
    },
    "B06": {
        "label": "5.客房设施信息 → Room Amenities → Bathrobe行",
        "guide": "打开「5.客房设施信息」向下找到 Room Amenities 区域的 Bathrobe 行，数量不能超过对应房型总房间数",
    },

    # C类：品牌标准
    "C01": {
        "label": "2.房型房价信息 → Non-Smoking列",
        "guide": "在「2.房型房价信息」中查看各房型的Non-Smoking列，无烟房总量应≥总房量的30%",
    },
    "C02": {
        "label": "5.客房设施信息 → Room Amenities → Connecting Room行",
        "guide": "在「5.客房设施信息」向下找到 Room Amenities 区域的 Connecting Room 行，总数应≥2间",
    },
    "C03": {
        "label": "2.房型房价信息 → Accessible Room列",
        "guide": "在「2.房型房价信息」中查看Accessible Room列，至少1个房型应标注为Yes",
    },
    "C04": {
        "label": "5.客房设施信息 → Room Amenities → Sofa Bed行（SLS房型列）",
        "guide": "在「5.客房设施信息」Room Amenities 区域找到 Sofa Bed 行，SLS（亲子套房）对应的列必须填写数量",
    },
    "C05": {
        "label": "2.房型房价信息 → 连通房+无障碍房",
        "guide": "品牌标准要求连通房中至少1间为无障碍房",
    },
    "C06": {
        "label": "2.房型房价信息 → Max Occupancy列",
        "guide": "在「2.房型房价信息」中查看Max Occupancy列，欢朋标准默认为3人",
    },
    "C07": {
        "label": "5.客房设施信息 → Room Amenities → Mini Fridge行",
        "guide": "在「5.客房设施信息」Room Amenities 区域找到 Mini Fridge 行，普通房型（非套房）需要有小冰箱",
    },

    # D类：必填项
    "D01": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → Descriptions 酒店描述",
        "guide": "打开「1.酒店特色信息」向下滚动找到 PROPERTY INFORMATION 酒店信息 板块下的 Descriptions(酒店描述)区域，填写酒店中文描述",
    },
    "D02": {
        "label": "2.房型房价信息 → 顶部ADR Forecast",
        "guide": "打开「2.房型房价信息」在顶部找到ADR Forecast(酒店年平均房价)处填写",
    },
    "D03": {
        "label": "5.客房设施信息 → Room Amenities → Rollaways折叠床行",
        "guide": "打开「5.客房设施信息」向下找到 Room Amenities 区域的 Rollaways(折叠床)行，没有折叠床则填0",
    },
    "D04": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → Telephone No. 电话号码",
        "guide": "打开「1.酒店特色信息」找到 PROPERTY INFORMATION 酒店信息 板块下的 Telephone Number(酒店电话)区域，填写国家代码+区号+电话号码",
    },
    "D05": {
        "label": "1.酒店特色信息 → SAFETY 酒店安保信息",
        "guide": "打开「1.酒店特色信息」向下滚动到 SAFETY 酒店安保信息 板块，逐项填写Y或N",
    },
    "D06": {
        "label": "1.酒店特色信息 → CLASSIFICATION 类别 → City 城市 / Distance 距离",
        "guide": "打开「1.酒店特色信息」向下滚动到 CLASSIFICATION 类别 板块，找到 City(城市) 和 Distance(距市中心距离)，距离须填数字+KM",
    },
    "D07": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → From hotel to City Center",
        "guide": "打开「1.酒店特色信息」找到 PROPERTY INFORMATION 酒店信息 板块下的 From hotel to City Center 区域，填写出租车/地铁/公交等路线",
    },
    "D08": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → Online Latitude/Longitude",
        "guide": "打开「1.酒店特色信息」找到 PROPERTY INFORMATION 酒店信息 板块下的 Online Latitude/Longitude，注意纬度在前（中国约28-50），经度在后（约73-135）",
    },
    "D09": {
        "label": "2.房型房价信息 → Accessible Room列",
        "guide": "打开「2.房型房价信息」在Accessible Room列中将无障碍房型标注为Yes",
    },

    # E类：格式
    "E01": {
        "label": "2.房型房价信息 → Room Size面积列",
        "guide": "打开「2.房型房价信息」找到Room Size列，面积必须为正整数（不能填25.5或20-30这种格式）",
    },
    "E03": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → Location Description(Short)",
        "guide": "打开「1.酒店特色信息」找到 PROPERTY INFORMATION 酒店信息 板块下的 Location Description(Short)，内容限制38个字符（含空格）",
    },
    "E04": {
        "label": "1.酒店特色信息 → GUEST ROOM 客房 → Number of Buildings 建筑数",
        "guide": "打开「1.酒店特色信息」向下滚动到 GUEST ROOM 客房 板块，找到 Number of Buildings，通常填1-3",
    },
    "E05": {
        "label": "1.酒店特色信息 → GUEST ROOM 客房 → Number of Floors 楼层数",
        "guide": "打开「1.酒店特色信息」向下滚动到 GUEST ROOM 客房 板块，楼层数填总层数（如12），不要填具体楼层（如3F-12F）",
    },
    "E06": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → 经纬度格式",
        "guide": "经纬度用小数格式（如40.222724），中国纬度约28-50，经度约73-135，不要填反",
    },
    "E07": {
        "label": "1.酒店特色信息 → PROPERTY INFORMATION 酒店信息 → 电话格式",
        "guide": "电话号码应为7-8位数字（不含区号），如69711888",
    },
}


# 规则ID → 所属页签（用于按页签分组展示）
RULE_TO_TAB = {
    # A类：跨文件对照
    "A01": "两表对照",
    "A02": "两表对照",
    "A03": "两表对照",
    # B类：跨页签
    "B01": "5.客房设施信息",
    "B03": "5.客房设施信息",
    "B04": "2.房型房价信息",
    "B05": "5.客房设施信息",
    "B06": "5.客房设施信息",
    # C类：品牌标准
    "C01": "2.房型房价信息",
    "C02": "5.客房设施信息",
    "C03": "2.房型房价信息",
    "C04": "5.客房设施信息",
    "C05": "2.房型房价信息",
    "C06": "2.房型房价信息",
    "C07": "5.客房设施信息",
    # D类：必填项
    "D01": "1.酒店特色信息",
    "D02": "2.房型房价信息",
    "D03": "5.客房设施信息",
    "D04": "1.酒店特色信息",
    "D05": "1.酒店特色信息",
    "D06": "1.酒店特色信息",
    "D07": "1.酒店特色信息",
    "D08": "1.酒店特色信息",
    "D09": "2.房型房价信息",
    # E类：格式
    "E01": "2.房型房价信息",
    "E03": "1.酒店特色信息",
    "E04": "1.酒店特色信息",
    "E05": "1.酒店特色信息",
    "E06": "1.酒店特色信息",
    "E07": "1.酒店特色信息",
}

# 页签展示顺序
TAB_ORDER = ["1.酒店特色信息", "2.房型房价信息", "5.客房设施信息", "两表对照"]


def get_tab_for_rule(rule_id: str) -> str:
    """获取规则所属页签"""
    return RULE_TO_TAB.get(rule_id, "其他")


def get_friendly_location(rule_id: str, raw_location: str) -> str:
    """将技术位置转为用户友好描述"""
    guide = LOCATION_GUIDES.get(rule_id)
    if guide:
        return guide["label"]
    # fallback: 把 PiM-1 等替换为用户看到的路径名
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
