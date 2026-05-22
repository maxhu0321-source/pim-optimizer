"""D类规则：必填项检查"""

from __future__ import annotations

from ..models import PiMData, PMSData, ValidationError
from .engine import rule


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


@rule("D01", "completeness", "error")
def hotel_description_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """酒店描述非空"""
    errors = []
    desc = pim.hotel_info.get("description_cn")
    if _is_empty(desc):
        errors.append(ValidationError(
            rule_id="D01",
            severity="error",
            category="completeness",
            message="酒店中文描述未填写",
            location="PiM-1!B39",
            fix_suggestion="请填写酒店中文描述（建议180-350字）",
        ))
    return errors


@rule("D02", "completeness", "error")
def adr_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """ADR已填写"""
    errors = []
    adr = pim.hotel_info.get("adr")
    if _is_empty(adr):
        errors.append(ValidationError(
            rule_id="D02",
            severity="error",
            category="completeness",
            message="ADR（平均房价）未填写",
            location="PiM-2",
            fix_suggestion="请根据酒店实际房价体系填写合理的ADR",
        ))
    return errors


@rule("D03", "completeness", "warning")
def fold_bed_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """折叠床数量已填"""
    errors = []
    fold = pim.hotel_info.get("fold_bed_count")
    if _is_empty(fold):
        errors.append(ValidationError(
            rule_id="D03",
            severity="warning",
            category="completeness",
            message="折叠床数量未填写（欢朋通常为0）",
            location="PiM-5",
            fix_suggestion="如无可移动加床请填写0",
        ))
    return errors


@rule("D04", "completeness", "error")
def phone_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """座机电话已填（GDS搭建必须）"""
    errors = []
    phone = pim.hotel_info.get("phone")
    if _is_empty(phone):
        errors.append(ValidationError(
            rule_id="D04",
            severity="error",
            category="completeness",
            message="酒店座机电话未填写（GDS搭建必需）",
            location="PiM-1",
            fix_suggestion="请填写酒店座机号码，GDS搭建需要此信息",
        ))
    return errors


@rule("D05", "completeness", "error")
def safety_info_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """安保信息已填"""
    errors = []
    safety = pim.hotel_info.get("safety_info")
    if _is_empty(safety):
        errors.append(ValidationError(
            rule_id="D05",
            severity="error",
            category="completeness",
            message="安保信息(fire/safety/security)未填写",
            location="PiM-1",
            fix_suggestion="请按实际情况填写安保信息（Y/N）",
        ))
    return errors


@rule("D06", "completeness", "error")
def city_info_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """城市信息+距离已填"""
    errors = []
    city = pim.hotel_info.get("city_info")
    if _is_empty(city):
        errors.append(ValidationError(
            rule_id="D06",
            severity="error",
            category="completeness",
            message="所在城市信息或距市中心距离缺失",
            location="PiM-1",
            fix_suggestion="填写所在城市及距市中心的距离（不能为0），距离50公里以内",
        ))
    return errors


@rule("D07", "completeness", "error")
def directions_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """到达信息已填"""
    errors = []
    d1 = pim.hotel_info.get("direction_hotel_to_city")
    d2 = pim.hotel_info.get("direction_city_to_hotel")
    if _is_empty(d1) and _is_empty(d2):
        errors.append(ValidationError(
            rule_id="D07",
            severity="error",
            category="completeness",
            message="到达路线信息未填写",
            location="PiM-1",
            fix_suggestion="请填写从酒店到市区、从市区到酒店的路线指引",
        ))
    return errors


@rule("D08", "completeness", "error")
def lat_lng_filled(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """经纬度完整"""
    errors = []
    lat = pim.hotel_info.get("latitude")
    lng = pim.hotel_info.get("longitude")
    if _is_empty(lat) or _is_empty(lng):
        errors.append(ValidationError(
            rule_id="D08",
            severity="error",
            category="completeness",
            message="经纬度信息不完整",
            location="PiM-1",
            fix_suggestion="请填写完整的经纬度坐标，注意不要填反（纬度在前）",
        ))
    return errors


@rule("D09", "completeness", "error")
def accessible_room_type_marked(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """无障碍房已标注具体房型"""
    errors = []
    # 有房型数据但没有标注无障碍
    if pim.room_types and not any(rt.is_accessible for rt in pim.room_types):
        errors.append(ValidationError(
            rule_id="D09",
            severity="error",
            category="completeness",
            message="未标注哪个房型存在无障碍房",
            location="PiM-2",
            fix_suggestion="在PiM-2房型表中标注无障碍房对应的房型代码",
        ))
    return errors
