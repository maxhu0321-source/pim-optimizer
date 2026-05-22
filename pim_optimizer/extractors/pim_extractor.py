"""PiM Pack (.xlsb) 数据提取器"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyxlsb

from ..config import (
    PIM1_FIELDS,
    PIM2_COLS,
    PIM2_DATA_START,
    PIM2_HEADER_ROW,
    PIM2_HOTEL_INFO,
    PIM5_DATA_START,
    PIM5_HEADER_ROW,
    PIM5_KEY_AMENITIES,
    PLACEHOLDERS,
)
from ..models import AmenityRow, PiMData, RoomType


def _clean_code(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value == int(value):
        value = int(value)
    return str(value).strip().upper()


def _to_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _read_sheet_rows(wb, sheet_name: str) -> list[list[Any]]:
    """读取整个sheet为二维列表"""
    rows = []
    try:
        with wb.get_sheet(sheet_name) as sheet:
            for row in sheet.rows():
                rows.append([cell.v for cell in row])
    except Exception:
        pass
    return rows


def _get_cell(rows: list[list[Any]], row: int, col: int) -> Any:
    """安全获取单元格值（row从1开始）"""
    idx = row - 1
    if idx < 0 or idx >= len(rows):
        return None
    r = rows[idx]
    if col >= len(r):
        return None
    return r[col]


def extract_pim(file_path: Path) -> PiMData:
    """从 PiM Pack xlsb 提取完整数据"""
    wb = pyxlsb.open_workbook(str(file_path))
    try:
        data = PiMData()

        # --- PiM-2: 房型房价信息 ---
        pim2_rows = _read_sheet_rows(wb, "PiM-2")
        _extract_pim2(pim2_rows, data)

        # --- PiM-1: 酒店特色信息 ---
        pim1_rows = _read_sheet_rows(wb, "PiM-1")
        _extract_pim1(pim1_rows, data)

        # --- PiM-5: 客房设施信息 ---
        pim5_rows = _read_sheet_rows(wb, "PiM-5")
        _extract_pim5(pim5_rows, data)

        return data
    finally:
        wb.close()


def _detect_pim2_cols(rows: list[list[Any]]) -> dict[str, int]:
    """从 header 行动态检测 PiM-2 列映射（兼容不同模板版本）"""
    header_idx = PIM2_HEADER_ROW - 1
    if header_idx >= len(rows):
        return PIM2_COLS  # fallback

    header = rows[header_idx]
    col_map = dict(PIM2_COLS)  # 默认值

    for col_idx, cell in enumerate(header):
        if not cell:
            continue
        s = str(cell).lower()
        if "room type code" in s or "房型代码" in s:
            col_map["code"] = col_idx
        elif "room type cn" in s or "房型名称中文" in s:
            col_map["name_cn"] = col_idx
        elif "bed type" in s or "床型" in s:
            col_map["bed_type"] = col_idx
        elif "room type en" in s or "房型名称英文" in s:
            col_map["name_en"] = col_idx
        elif "number of rooms" in s or "房型房量" in s:
            col_map["count"] = col_idx
        elif "non-smoking" in s or "无烟房" in s:
            col_map["non_smoking"] = col_idx
        elif "max occupancy" in s or "最多可入住" in s:
            col_map["max_occ"] = col_idx
        elif "extra bed" in s or "加床" in s:
            col_map["extra_bed"] = col_idx
        elif "accessible room" in s or "无障碍房" in s:
            col_map["accessible"] = col_idx
        elif "category" in s or "类别" in s:
            col_map["category"] = col_idx
        elif "total values" in s or "类别总房量" in s:
            col_map["total_count"] = col_idx
        elif "room size" in s or "面积" in s:
            col_map["area"] = col_idx

    return col_map


def _extract_pim2(rows: list[list[Any]], data: PiMData) -> None:
    """提取 PiM-2 酒店基本信息 + 房型列表"""
    # 动态检测列映射
    cols = _detect_pim2_cols(rows)

    # 酒店基本信息
    for key, pos in PIM2_HOTEL_INFO.items():
        val = _get_cell(rows, pos["row"], pos["col"])
        if key == "total_rooms":
            data.total_rooms = _to_int(val)
        elif key == "hotel_name":
            data.hotel_name_cn = str(val or "").strip()
        elif key == "inncode":
            data.inncode = _clean_code(val)
        elif key == "opening_date":
            data.opening_date = str(val or "").strip()
        elif key == "adr":
            data.hotel_info["adr"] = val

    # 房型数据（从 row 15 开始）
    current_category = ""
    for row_num_0based, row in enumerate(rows):
        row_num = row_num_0based + 1
        if row_num < PIM2_DATA_START:
            continue
        if len(row) < 7:
            continue

        # 检测类别行
        cat_val = row[cols["category"]] if len(row) > cols["category"] else None
        if cat_val and str(cat_val).strip():
            cat_str = str(cat_val).strip().lower()
            if "accessible" in cat_str or "无障碍" in cat_str:
                current_category = "accessible"
            elif "suite" in cat_str or "套房" in cat_str:
                current_category = "suite"
            else:
                current_category = "standard"

        code = _clean_code(row[cols["code"]])
        if code in PLACEHOLDERS or not code:
            continue

        count = _to_int(row[cols["count"]])
        if count <= 0:
            continue

        # non_smoking 列是 Yes/No，Yes 表示半数以上无烟
        ns_val = str(row[cols["non_smoking"]] or "").strip().lower() if len(row) > cols["non_smoking"] else ""
        non_smoking = count if ns_val == "yes" else 0

        max_occ = _to_int(row[cols["max_occ"]]) if len(row) > cols["max_occ"] else 3

        # accessible 列是 Yes/No
        acc_col = cols.get("accessible", 999)
        acc_val = str(row[acc_col] or "").strip().lower() if len(row) > acc_col else ""
        is_acc = (acc_val == "yes") or (current_category == "accessible")

        rt = RoomType(
            source="PiM-2",
            code=code,
            name_cn=str(row[cols["name_cn"]] or "").strip() if len(row) > cols["name_cn"] else "",
            name_en=str(row[cols["name_en"]] or "").strip() if len(row) > cols["name_en"] else "",
            count=count,
            non_smoking_count=non_smoking,
            max_occupancy=max_occ if max_occ > 0 else 3,
            is_accessible=is_acc,
            row=row_num,
        )

        # 面积（用于格式校验）
        area_col = cols.get("area", 12)
        if len(row) > area_col:
            rt.area_sqm = row[area_col]

        data.room_types.append(rt)

        if rt.is_accessible:
            data.accessible_room_types.append(code)


def _extract_pim1(rows: list[list[Any]], data: PiMData) -> None:
    """提取 PiM-1 酒店特色信息"""
    info = {}
    for key, pos in PIM1_FIELDS.items():
        val = _get_cell(rows, pos["row"], pos["col"])
        info[key] = val
    data.hotel_info.update(info)


def _extract_pim5(rows: list[list[Any]], data: PiMData) -> None:
    """提取 PiM-5 客房设施数据"""
    if not rows:
        return

    # 先从header行确定房型代码与列的映射
    # PiM-5 的列结构：A列=设施名, 后续列=各房型
    # 需要从 PiM-2 提取的房型代码列表来匹配

    # 读取设施数据
    room_codes_from_pim2 = [rt.code for rt in data.room_types]

    for row_num_0based, row in enumerate(rows):
        row_num = row_num_0based + 1
        if row_num < PIM5_DATA_START:
            continue
        if not row or len(row) < 2:
            continue

        amenity_name = str(row[0] or "").strip()
        if not amenity_name:
            continue

        # 匹配关键设施
        matched_key = None
        for key, pattern in PIM5_KEY_AMENITIES.items():
            if pattern.lower() in amenity_name.lower():
                matched_key = key
                break

        if matched_key:
            amenity_row = AmenityRow(name=amenity_name, row=row_num)
            # 提取各列数值（跳过A列）
            for col_idx in range(1, len(row)):
                val = _to_int(row[col_idx])
                amenity_row.counts_by_room[f"col_{col_idx}"] = val
            data.amenities[matched_key] = amenity_row
