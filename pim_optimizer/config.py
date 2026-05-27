"""PiM/PMS 文件字段映射配置 + 品牌标准常量"""

# ============================================================
# PiM-2 房型房价信息表
# ============================================================
PIM2_HEADER_ROW = 14
PIM2_DATA_START = 15
PIM2_COLS = {
    "category": 0,       # A列: 类别 (Standard/Suite/Accessible)
    "total_count": 1,    # B列: 小计
    "name_cn": 2,        # C列: 中文名
    "bed_type": 3,       # D列: Bed Type
    "code": 4,           # E列: Room Type Code
    "name_en": 5,        # F列: 英文名
    "count": 6,          # G列: Number of Rooms
    "non_smoking": 7,    # H列: Yes/No 是否半数以上无烟
    "max_occ": 8,        # I列: Max Occupancy
    "extra_bed": 9,      # J列: Extra Bed
    "accessible": 10,    # K列: Accessible Room (Yes/No)
    "ground_floor": 11,  # L列: Ground Floor (Yes/No)
}

# PiM-2 酒店基础信息（顶部区域）
PIM2_HOTEL_INFO = {
    "hotel_name": {"row": 4, "col": 1},     # B4
    "inncode": {"row": 5, "col": 1},         # B5
    "opening_date": {"row": 7, "col": 1},    # B7
    "total_rooms": {"row": 8, "col": 1},     # B8
    "adr": {"row": 9, "col": 1},             # B9: ADR Forecast
    "fold_bed_count": {"row": 33, "col": 1}, # B33: Number of rollaway beds
}

# ============================================================
# PiM-1 酒店特色信息表 - 关键字段位置
# ============================================================
PIM1_FIELDS = {
    # 描述
    "description_cn": {"row": 47, "col": 1},   # B47: 酒店中文描述
    "description_en": {"row": 40, "col": 1},    # B40: 第一段集团统一英文
    "tagline": {"row": 54, "col": 1},           # B54: Tagline
    # 经纬度
    "latitude": {"row": 9, "col": 2},           # C9: Online Latitude
    "longitude": {"row": 10, "col": 2},         # C10: Online Longitude
    # 电话
    "phone_country": {"row": 28, "col": 2},     # C28: Country Code
    "phone_area": {"row": 29, "col": 2},        # C29: Area Code
    "phone": {"row": 30, "col": 2},             # C30: Telephone No.
    # 城市/位置
    "city_info": {"row": 135, "col": 2},        # C135: City
    "city_direction": {"row": 143, "col": 2},   # C143: Direction to city center
    "city_distance": {"row": 144, "col": 2},    # C144: Distance to city center
    # 方位信息
    "direction_hotel_to_city": {"row": 68, "col": 1},
    "direction_city_to_hotel": {"row": 74, "col": 1},
    # 位置描述
    "location_desc_long": {"row": 166, "col": 1},   # B166
    "location_desc_short": {"row": 171, "col": 1},  # B171 (short限38字)
    # 机场
    "airport_directions": {"row": 187, "col": 1},
    # 商户/景点
    "nearby_poi": {"row": 225, "col": 1},
    "nearby_facilities": {"row": 231, "col": 1},
    "nearby_companies": {"row": 237, "col": 1},
    # 安保 - fire/safety section starts at row 107, Y/N in col A
    "safety_info": {"row": 107, "col": 0},      # A107: first fire/safety question
    # 楼层/栋数
    "floor_count": {"row": 335, "col": 1},
    "building_count": {"row": 334, "col": 1},
}

# ============================================================
# PiM-5 客房设施信息表
# ============================================================
PIM5_HEADER_ROW = 10
PIM5_DATA_START = 13
PIM5_AMENITY_COL = 0  # A列: 设施名称

# PiM-5 房型列位置（动态，取决于酒店房型数量）
# Standard rooms: cols 2-7, Suites: cols 8-12, Accessible: cols 13+
# 实际位置需从 header row 动态解析

# 关键设施名称标识（用于匹配行）
PIM5_KEY_AMENITIES = {
    "non_smoking": "Non-Smoking",
    "sofa": "Sofa",
    "sofa_bed": "Sofa Bed",
    "sofa_sleeper": "Sofa Sleeper",
    "bathrobe": "Bathrobe",
    "connecting_room": "Connecting Room",
    "iron": "Iron",
    "mini_fridge": "Mini Fridge",
    "accessible_shower": "Accessible",
    "visual_alarm": "Visual",
    "remote_curtain": "Remote",
    "lounge": "Lounge",
    "rollaway": "Rollaway",
}

# ============================================================
# PMS 1.4 酒店客房
# ============================================================
PMS_14_HEADER_ROW = 2
PMS_14_DATA_START = 3
PMS_14_COLS = {
    "seq": 0,            # A列: 序号
    "category": 1,       # B列: 房型大类
    "name_cn": 2,        # C列: 中文名
    "code": 3,           # D列: 房型代码
    "hilton_code": 4,    # E列: 希尔顿渠道代码
    "name_en": 5,        # F列: 英文名
    "count": 6,          # G列: 房型数量统计
}

# ============================================================
# 品牌标准常量
# ============================================================
BRAND = {
    "min_non_smoking_ratio": 0.30,    # 无烟房≥30%
    "min_connecting_rooms": 2,         # 连通房≥2间
    "min_accessible_rooms": 1,         # 至少1间无障碍房
    "default_max_occupancy": 3,        # 默认最大入住人数
    "sls_requires_sofa_bed": True,     # SLS(亲子套房)必须有沙发床
    "location_desc_max_chars": 38,     # 位置描述最大字符数
    "brand_name_en": "Hampton by Hilton",
}

# 需要配备沙发床的房型代码前缀
SLS_CODES = {"SLS", "SLSS"}

# 占位符/无效值
PLACEHOLDERS = {"请填写房型代码", "请填写", "", None}
