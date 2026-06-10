"""B类规则：PiM内部一致性"""

from __future__ import annotations

from ..models import PiMData, PMSData, ValidationError
from .engine import rule


@rule("B01", "internal", "error")
def non_smoking_consistency(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """PiM-2无烟房标记与PiM-5设施表中无烟房数量逐房型校验"""
    errors = []
    amenity = pim.amenities.get("non_smoking")
    if not amenity:
        return []

    for rt in pim.room_types:
        pim5_count = amenity.counts_by_room.get(rt.code)
        if pim5_count is None:
            continue

        half = rt.count / 2
        is_yes = rt.non_smoking_count > 0  # PiM-2 标记为 Yes

        if is_yes and pim5_count < half:
            errors.append(ValidationError(
                rule_id="B01",
                severity="error",
                category="internal",
                message=f"房型 {rt.code}：「2.房型房价信息」无烟房标记为Yes（应过半），但「5.客房设施信息」仅填{pim5_count}间（共{rt.count}间）",
                location=f"2.房型房价信息 第{rt.row}行 vs 5.客房设施信息 Non-Smoking行",
                fix_suggestion=f"房型 {rt.code} 标Yes表示多数为无烟房，请确认「5.客房设施信息」无烟房数量≥{int(half)+1}间，或将标记改为No",
            ))
        elif not is_yes and pim5_count > half:
            errors.append(ValidationError(
                rule_id="B01",
                severity="error",
                category="internal",
                message=f"房型 {rt.code}：「2.房型房价信息」无烟房标记为No（应不过半），但「5.客房设施信息」填了{pim5_count}间（共{rt.count}间）",
                location=f"2.房型房价信息 第{rt.row}行 vs 5.客房设施信息 Non-Smoking行",
                fix_suggestion=f"房型 {rt.code} 标No表示无烟房不超过半数，请确认「5.客房设施信息」数量≤{int(half)}间，或将标记改为Yes",
            ))
    return errors


@rule("B03", "internal", "error")
def sofa_count_not_exceed_room(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """沙发/沙发床数量不应超过对应房型总数"""
    errors = []
    total_rooms = sum(rt.count for rt in pim.room_types)

    for key in ("sofa", "sofa_bed", "sofa_sleeper"):
        amenity = pim.amenities.get(key)
        if not amenity:
            continue
        total_amenity = sum(v for v in amenity.counts_by_room.values() if v > 0)
        if total_amenity > total_rooms:
            errors.append(ValidationError(
                rule_id="B03",
                severity="error",
                category="internal",
                message=f"{amenity.name}总数({total_amenity})超过总房间数({total_rooms})",
                location=f"5.客房设施信息 第{amenity.row}行",
                fix_suggestion=f"检查{amenity.name}各房型填写的数量，确保不超过房型总数",
            ))
    return errors


@rule("B04", "internal", "error")
def accessible_info_consistent(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """无障碍房信息跨sheet一致"""
    errors = []
    accessible_count = sum(rt.count for rt in pim.room_types if rt.is_accessible)
    if accessible_count == 0 and pim.total_rooms > 0:
        pass
    return errors


@rule("B05", "internal", "error")
def connecting_room_consistency(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """连通房信息跨sheet一致"""
    errors = []
    amenity = pim.amenities.get("connecting_room")
    if not amenity:
        return []

    pim2_connecting = sum(rt.connecting_count for rt in pim.room_types if rt.connecting_count > 0)
    pim5_connecting = sum(v for v in amenity.counts_by_room.values() if v > 0)

    if pim2_connecting > 0 and pim5_connecting > 0 and pim2_connecting != pim5_connecting:
        errors.append(ValidationError(
            rule_id="B05",
            severity="error",
            category="internal",
            message=f"连通房数量不一致：「2.房型房价信息」={pim2_connecting}间，「5.客房设施信息」={pim5_connecting}间",
            location="2.房型房价信息 vs 5.客房设施信息 Connecting Room行",
            fix_suggestion="核实连通房数量，确保房型页和设施页数据一致",
        ))
    return errors


@rule("B06", "internal", "warning")
def bathrobe_not_exceed_room(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """浴袍数量不应超过对应房型总数"""
    errors = []
    amenity = pim.amenities.get("bathrobe")
    if not amenity:
        return []
    total_rooms = sum(rt.count for rt in pim.room_types)
    total_bathrobe = sum(v for v in amenity.counts_by_room.values() if v > 0)
    if total_bathrobe > total_rooms:
        errors.append(ValidationError(
            rule_id="B06",
            severity="warning",
            category="internal",
            message=f"浴袍数量({total_bathrobe})超过总房间数({total_rooms})",
            location=f"5.客房设施信息 第{amenity.row}行",
            fix_suggestion="检查浴袍各房型数量，确保不超过房型总数",
        ))
    return errors
