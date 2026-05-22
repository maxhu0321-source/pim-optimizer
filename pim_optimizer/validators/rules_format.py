"""E类规则：格式/数值检查"""

from __future__ import annotations

from ..config import BRAND
from ..models import PiMData, PMSData, ValidationError
from .engine import rule


@rule("E01", "format", "error")
def room_area_is_integer(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """房型面积必须为正整数（不能是小数或区间）"""
    errors = []
    for rt in pim.room_types:
        area = rt.area_sqm
        if area is None:
            continue
        # 检查是否为整数
        if isinstance(area, float) and area != int(area):
            errors.append(ValidationError(
                rule_id="E01",
                severity="error",
                category="format",
                message=f"房型 {rt.code} 面积为{area}，不是整数",
                location=f"PiM-2!Row{rt.row}",
                fix_suggestion="房型面积必须填写整数，不能有小数",
            ))
        elif isinstance(area, str):
            # 检查是否是区间（如 "25-30"）
            if "-" in str(area) or "~" in str(area):
                errors.append(ValidationError(
                    rule_id="E01",
                    severity="error",
                    category="format",
                    message=f"房型 {rt.code} 面积为'{area}'，不能是区间",
                    location=f"PiM-2!Row{rt.row}",
                    fix_suggestion="房型面积必须填写单一整数值，不能是区间",
                ))
    return errors


@rule("E03", "format", "error")
def location_desc_length(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """位置描述≤38字符"""
    errors = []
    desc = pim.hotel_info.get("location_desc_short")
    if desc and isinstance(desc, str):
        max_len = BRAND["location_desc_max_chars"]
        if len(desc) > max_len:
            errors.append(ValidationError(
                rule_id="E03",
                severity="error",
                category="format",
                message=f"酒店位置短描述({len(desc)}字)超过限制({max_len}字)",
                location="PiM-1",
                fix_suggestion=f"缩短位置描述至{max_len}字以内（含空格）",
            ))
    return errors


@rule("E04", "format", "warning")
def building_count_reasonable(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """总建筑数合理（通常1-3）"""
    errors = []
    val = pim.hotel_info.get("building_count")
    if val is None:
        return []
    try:
        count = int(float(val))
    except (TypeError, ValueError):
        errors.append(ValidationError(
            rule_id="E04",
            severity="warning",
            category="format",
            message=f"总建筑数'{val}'格式异常",
            location="PiM-1",
            fix_suggestion="总建筑数指酒店拥有几栋楼，一般为1",
        ))
        return errors

    if count > 5:
        errors.append(ValidationError(
            rule_id="E04",
            severity="warning",
            category="format",
            message=f"总建筑数为{count}，请确认是否正确（通常为1-3）",
            location="PiM-1",
            fix_suggestion="总建筑数指酒店拥有几栋楼，一般为1",
        ))
    return errors


@rule("E05", "format", "warning")
def floor_count_is_number(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """楼层数为数字（非具体楼层描述）"""
    errors = []
    val = pim.hotel_info.get("floor_count")
    if val is None:
        return []
    val_str = str(val).strip()
    # 检查是否包含楼层描述（如 "3-12层" 或 "3F-12F"）
    if any(c in val_str for c in ["层", "楼", "F", "f", ","]):
        errors.append(ValidationError(
            rule_id="E05",
            severity="warning",
            category="format",
            message=f"楼层数填写为'{val_str}'，应填写数字而非具体楼层",
            location="PiM-1",
            fix_suggestion="此处填写酒店投入运营的总楼层数（数字），不是填具体哪几层",
        ))
    return errors


@rule("E06", "format", "warning")
def lat_lng_format(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """经纬度格式正确且未填反"""
    errors = []
    lat = pim.hotel_info.get("latitude")
    lng = pim.hotel_info.get("longitude")
    if not lat or not lng:
        return []

    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        errors.append(ValidationError(
            rule_id="E06",
            severity="warning",
            category="format",
            message=f"经纬度格式异常：纬度={lat}，经度={lng}",
            location="PiM-1",
            fix_suggestion="经纬度应为数字格式，如 30.123456, 114.567890",
        ))
        return errors

    # 中国范围检查：纬度 18-54, 经度 73-135
    if 73 <= lat_f <= 135 and 18 <= lng_f <= 54:
        errors.append(ValidationError(
            rule_id="E06",
            severity="warning",
            category="format",
            message=f"经纬度可能填反：当前纬度={lat_f}，经度={lng_f}",
            location="PiM-1",
            fix_suggestion="中国纬度范围18-54，经度范围73-135，请检查是否填反",
        ))
    elif not (18 <= lat_f <= 54):
        if lat_f > 54 or lat_f < 18:
            errors.append(ValidationError(
                rule_id="E06",
                severity="warning",
                category="format",
                message=f"纬度{lat_f}超出中国范围(18-54)，请确认",
                location="PiM-1",
                fix_suggestion="中国纬度范围为18-54，请核实坐标",
            ))
    return errors


@rule("E07", "format", "warning")
def phone_format_valid(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """电话号码格式基本有效"""
    errors = []
    phone = pim.hotel_info.get("phone")
    if not phone:
        return []
    phone_str = str(phone).strip().replace(" ", "").replace("-", "")
    # 过于简单的号码（如 12345678）
    if phone_str.isdigit() and len(phone_str) < 7:
        errors.append(ValidationError(
            rule_id="E07",
            severity="warning",
            category="format",
            message=f"电话号码'{phone}'可能格式有误（位数过少）",
            location="PiM-1",
            fix_suggestion="请填写完整的酒店座机号码（含区号）",
        ))
    return errors
