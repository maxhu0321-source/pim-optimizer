"""A类规则：跨文件一致性（PiM vs PMS）"""

from __future__ import annotations

from ..models import PiMData, PMSData, ValidationError
from .engine import rule


def _pms_hilton_codes(pms: PMSData) -> dict[str, "RoomType"]:
    """PMS hilton_code → RoomType 映射（PiM代码对应PMS的hilton_code列）"""
    m = {}
    for rt in pms.room_types:
        key = rt.hilton_code if rt.hilton_code else rt.code
        m[key] = rt
    return m


@rule("A01", "cross_file", "error")
def pim_code_exists_in_pms(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """PiM中的房型代码必须在PMS中存在"""
    if not pms:
        return []
    pms_map = _pms_hilton_codes(pms)
    errors = []
    for rt in pim.room_types:
        if rt.code not in pms_map:
            errors.append(ValidationError(
                rule_id="A01",
                severity="error",
                category="cross_file",
                message=f"房型代码 {rt.code}（{rt.name_cn}）在PMS代码表中不存在",
                location=f"2.房型房价信息 第{rt.row}行",
                fix_suggestion=f"在PMS 1.4中添加希尔顿渠道代码 {rt.code}，或修正PiM中的代码",
            ))
    return errors


@rule("A02", "cross_file", "error")
def pms_code_exists_in_pim(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """PMS中的房型代码必须在PiM中存在"""
    if not pms:
        return []
    pim_codes = {rt.code for rt in pim.room_types}
    errors = []
    for rt in pms.room_types:
        hilton = rt.hilton_code if rt.hilton_code else rt.code
        if hilton not in pim_codes:
            errors.append(ValidationError(
                rule_id="A02",
                severity="error",
                category="cross_file",
                message=f"PMS房型 {rt.code}（希尔顿代码{hilton}，{rt.name_cn}）在PiM中不存在",
                location=f"PMS 1.4 酒店客房 第{rt.row}行",
                fix_suggestion=f"在「2.房型房价信息」中添加房型 {hilton}，或从PMS中移除",
            ))
    return errors


@rule("A03", "cross_file", "error")
def room_count_matches(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    """同一房型代码的房量必须一致"""
    if not pms:
        return []
    pim_map = {rt.code: rt for rt in pim.room_types}
    pms_map = _pms_hilton_codes(pms)
    errors = []
    for code in set(pim_map) & set(pms_map):
        p = pim_map[code]
        m = pms_map[code]
        if p.count != m.count:
            errors.append(ValidationError(
                rule_id="A03",
                severity="error",
                category="cross_file",
                message=f"房型 {code} 房量不一致：PiM={p.count}间，PMS={m.count}间",
                location=f"2.房型房价信息 第{p.row}行 vs PMS 1.4 第{m.row}行",
                fix_suggestion="核实实际房量，统一PiM和PMS中的数值",
            ))
    return errors
