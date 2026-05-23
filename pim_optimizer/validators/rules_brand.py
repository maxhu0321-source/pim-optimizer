"""C类规则：品牌标准合规"""

from __future__ import annotations

from ..config import BRAND, SLS_CODES
from ..models import PiMData, PMSData, ValidationError
from .engine import rule


@rule("C01", "brand", "error")
def non_smoking_minimum(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """无烟房 ≥ 30%总房量"""
    errors = []
    total = sum(rt.count for rt in pim.room_types)
    non_smoking = sum(rt.non_smoking_count for rt in pim.room_types)
    if total > 0 and non_smoking > 0:
        ratio = non_smoking / total
        if ratio < BRAND["min_non_smoking_ratio"]:
            errors.append(ValidationError(
                rule_id="C01",
                severity="error",
                category="brand",
                message=f"无烟房占比 {non_smoking}/{total} = {ratio:.0%}，低于品牌标准30%",
                location="2.房型房价信息 → Non-Smoking列",
                fix_suggestion="增加无烟房数量，确保无烟房≥总房量的30%",
            ))
    return errors


@rule("C02", "brand", "error")
def connecting_room_minimum(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """连通房 ≥ 2间"""
    errors = []
    connecting_total = sum(rt.connecting_count for rt in pim.room_types)

    amenity = pim.amenities.get("connecting_room")
    if amenity:
        connecting_from_amenity = sum(v for v in amenity.counts_by_room.values() if v > 0)
        connecting_total = max(connecting_total, connecting_from_amenity)

    if 0 < connecting_total < BRAND["min_connecting_rooms"]:
        errors.append(ValidationError(
            rule_id="C02",
            severity="error",
            category="brand",
            message=f"连通房仅{connecting_total}间，品牌标准要求至少{BRAND['min_connecting_rooms']}间",
            location="5.客房设施信息 → Connecting Room行",
            fix_suggestion="连通房至少需要2间，请核实酒店连通房配置",
        ))
    return errors


@rule("C03", "brand", "error")
def accessible_room_required(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """至少1间无障碍房"""
    errors = []
    accessible_count = sum(1 for rt in pim.room_types if rt.is_accessible)
    if pim.room_types and accessible_count == 0:
        errors.append(ValidationError(
            rule_id="C03",
            severity="error",
            category="brand",
            message="未标注任何无障碍房房型，品牌标准要求至少1间",
            location="2.房型房价信息 → Accessible Room列",
            fix_suggestion="在房型表中标注哪个房型有无障碍房（Accessible Room选Yes）",
        ))
    return errors


@rule("C04", "brand", "error")
def sls_requires_sofa_bed(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """SLS(亲子套房)必须配沙发床"""
    errors = []
    sls_rooms = [rt for rt in pim.room_types if rt.code in SLS_CODES]
    if not sls_rooms:
        return []

    sofa_bed = pim.amenities.get("sofa_bed") or pim.amenities.get("sofa_sleeper")
    if not sofa_bed:
        for rt in sls_rooms:
            errors.append(ValidationError(
                rule_id="C04",
                severity="error",
                category="brand",
                message=f"房型 {rt.code}（亲子套房）按品牌标准需配沙发床，但设施表中未填写",
                location="5.客房设施信息 → Sofa Bed行",
                fix_suggestion=f"在「5.客房设施信息」中为 {rt.code} 填写沙发床数量",
            ))
    return errors


@rule("C05", "brand", "warning")
def connecting_room_has_accessible(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """连通房中至少1间为无障碍房"""
    errors = []
    has_connecting = any(rt.connecting_count > 0 for rt in pim.room_types)
    has_accessible = any(rt.is_accessible for rt in pim.room_types)

    if has_connecting and not has_accessible:
        errors.append(ValidationError(
            rule_id="C05",
            severity="warning",
            category="brand",
            message="品牌标准要求连通房中至少1间为无障碍房，请确认",
            location="2.房型房价信息",
            fix_suggestion="确保连通房中至少有1间是无障碍房型",
        ))
    return errors


@rule("C06", "brand", "warning")
def max_occupancy_default(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """Max Occupancy默认应为3"""
    errors = []
    for rt in pim.room_types:
        if rt.max_occupancy != BRAND["default_max_occupancy"] and rt.max_occupancy > 0:
            errors.append(ValidationError(
                rule_id="C06",
                severity="warning",
                category="brand",
                message=f"房型 {rt.code} 最大入住人数为{rt.max_occupancy}，欢朋默认为{BRAND['default_max_occupancy']}",
                location=f"2.房型房价信息 第{rt.row}行 Max Occupancy列",
                fix_suggestion="欢朋所有房型默认最多入住3人，如需修改请确认品牌许可",
            ))
    return errors
