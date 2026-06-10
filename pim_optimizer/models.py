"""数据模型定义"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RoomType:
    """房型数据（可来自PiM-2或PMS 1.4）"""
    source: str            # "PiM-2" / "PMS-1.4"
    code: str              # PMS房型代码 (如 SKR, SVR, SLS)
    name_cn: str = ""
    name_en: str = ""
    count: int = 0         # 房量
    non_smoking_count: int = 0
    max_occupancy: int = 3
    area_sqm: Any = None   # 原始值，用于校验是否整数
    bed_type: str = ""
    bed_size: str = ""
    is_accessible: bool = False
    connecting_count: int = 0
    extra_bed: str = ""    # Y/N
    hilton_code: str = ""  # 希尔顿渠道代码
    row: int = 0           # 源文件行号


@dataclass
class AmenityRow:
    """PiM-5 设施行"""
    name: str              # 设施名称（英文/中文）
    row: int
    # 各房型对应的数量，key=房型代码
    counts_by_room: dict[str, int] = field(default_factory=dict)


@dataclass
class PiMData:
    """PiM Pack 提取的完整数据"""
    # PiM-2 基本信息
    hotel_name_cn: str = ""
    hotel_name_en: str = ""
    inncode: str = ""
    total_rooms: int = 0
    opening_date: str = ""

    # PiM-1 关键字段
    hotel_info: dict[str, Any] = field(default_factory=dict)
    # 包含: description_cn, phone, latitude, longitude, adr,
    #       floor_count, building_count, fold_bed_count,
    #       site_location, safety_info, city_info, directions, etc.

    # PiM-2 房型列表
    room_types: list[RoomType] = field(default_factory=list)

    # PiM-5 设施数据
    amenities: dict[str, AmenityRow] = field(default_factory=dict)
    # key = 设施名标识 (如 "non_smoking", "sofa", "sofa_bed", "bathrobe", etc.)

    # PiM-2 中的无障碍/连通房汇总（与PiM-5交叉校验用）
    accessible_room_types: list[str] = field(default_factory=list)
    connecting_room_types: list[str] = field(default_factory=list)

    # PiM-1 Bedding 区块各床型数量之和（应等于总房量）
    bedding_total: int = 0
    # PiM-5 顶部 TV Size 表：每项 (类别名, 房间数, 尺寸原始值)
    tv_size_rows: list[tuple[str, int, Any]] = field(default_factory=list)


@dataclass
class PMSData:
    """PMS 标准代码表提取的数据"""
    room_types: list[RoomType] = field(default_factory=list)


@dataclass
class ValidationError:
    """单条校验错误"""
    rule_id: str
    severity: str          # "error" / "warning" / "info"
    category: str          # "cross_file" / "internal" / "brand" / "completeness" / "format"
    message: str           # 中文描述
    location: str          # "PiM-2!G15" 定位信息
    fix_suggestion: str    # 修改建议


@dataclass
class ValidationReport:
    """完整校验报告"""
    pim_file: str = ""
    pms_file: str = ""
    total_rooms_pim: int = 0
    total_rooms_pms: int = 0
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for e in self.errors if e.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for e in self.errors if e.severity == "warning")

    @property
    def can_submit(self) -> bool:
        return self.error_count == 0
