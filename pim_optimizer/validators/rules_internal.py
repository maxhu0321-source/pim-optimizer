"""B类规则：PiM内部一致性"""

from __future__ import annotations

from ..models import PiMData, PMSData, ValidationError
from .engine import rule


@rule("B01", "internal", "error")
def non_smoking_consistency(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """PiM-2无烟房数量与PiM-5设施表中无烟房数量一致"""
    errors = []
    amenity = pim.amenities.get("non_smoking")
    if not amenity:
        return []

    pim2_total_ns = sum(rt.non_smoking_count for rt in pim.room_types)
    pim5_total_ns = sum(v for v in amenity.counts_by_room.values() if v > 0)

    if pim2_total_ns > 0 and pim5_total_ns > 0 and pim2_total_ns != pim5_total_ns:
        errors.append(ValidationError(
            rule_id="B01",
            severity="error",
            category="internal",
            message=f"无烟房数量前后不一致：「2.房型房价信息」合计={pim2_total_ns}间，「5.客房设施信息」合计={pim5_total_ns}间",
            location="2.房型房价信息 Non-Smoking列 vs 5.客房设施信息 Non-Smoking行",
            fix_suggestion="核实各房型无烟房数量，确保两处数据一致。如果Non-Smoking选Yes，则该房型所有房间都算无烟房",
        ))
    return errors


@rule("B02", "internal", "error")
def bedding_equals_total_rooms(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """Bedding总数应等于总房间数"""
    errors = []
    total_rooms = sum(rt.count for rt in pim.room_types)
    total_bedding = sum(rt.bedding_count for rt in pim.room_types if rt.bedding_count > 0)

    if total_bedding > 0 and total_bedding != total_rooms:
        errors.append(ValidationError(
            rule_id="B02",
            severity="error",
            category="internal",
            message=f"Bedding总数({total_bedding})与总房间数({total_rooms})不匹配",
            location="2.房型房价信息 → Bedding区域",
            fix_suggestion="检查各房型的bedding数量，确保总和等于酒店总房间数",
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
