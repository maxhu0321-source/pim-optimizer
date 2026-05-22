#!/usr/bin/env python3
"""校验 APAC PiM 表与 PMS 标准代码表的房型/房量一致性。"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import openpyxl
import pyxlsb

PLACEHOLDERS = {"请填写房型代码", "", None}


@dataclass
class RoomType:
    source: str
    code: str
    count: int
    name_cn: str = ""
    name_en: str = ""
    hilton_code: str = ""
    row: int = 0


@dataclass
class Difference:
    level: str
    issue: str
    code: str
    apac_count: int | None
    pms_count: int | None
    apac_row: int | None
    pms_row: int | None
    detail: str


def clean_code(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip().upper()


def to_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def extract_apac_room_types(apac_path: Path) -> dict[str, RoomType]:
    """从 APAC PiM-2 读取：房型代码(C列) + 此房型房量(G列)。"""
    rooms: dict[str, RoomType] = {}
    wb = pyxlsb.open_workbook(str(apac_path))
    try:
        with wb.get_sheet("PiM-2") as sheet:
            for row_num, row in enumerate(sheet.rows(), start=1):
                if row_num < 15:
                    continue
                values = [cell.v for cell in row]
                if len(values) < 7:
                    continue
                code = clean_code(values[2])
                if code in PLACEHOLDERS or not code:
                    continue
                count = to_int(values[6])
                if count <= 0:
                    continue
                rooms[code] = RoomType(
                    source="APAC PiM-2",
                    code=code,
                    count=count,
                    name_cn=str(values[3] or "").strip(),
                    name_en=str(values[5] or "").strip(),
                    row=row_num,
                )
    finally:
        wb.close()
    return rooms


def extract_pms_room_types(pms_path: Path) -> dict[str, RoomType]:
    """从 PMS 1.4 酒店客房读取：房型代码(D列) + 房型数量统计(G列)。"""
    wb = openpyxl.load_workbook(pms_path, read_only=True, data_only=True)
    try:
        ws = wb["1.4 酒店客房"]
        rooms: dict[str, RoomType] = {}
        for row_num, row in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
            if len(row) < 7:
                continue
            code = clean_code(row[3])
            if not code:
                continue
            count = to_int(row[6])
            if count <= 0:
                continue
            rooms[code] = RoomType(
                source="PMS 1.4 酒店客房",
                code=code,
                count=count,
                name_cn=str(row[2] or "").strip(),
                name_en=str(row[5] or "").strip(),
                hilton_code=clean_code(row[4]),
                row=row_num,
            )
        return rooms
    finally:
        wb.close()


def compare(apac: dict[str, RoomType], pms: dict[str, RoomType]) -> list[Difference]:
    diffs: list[Difference] = []
    all_codes = sorted(set(apac) | set(pms))
    for code in all_codes:
        a = apac.get(code)
        p = pms.get(code)
        if a and not p:
            diffs.append(Difference("ERROR", "PMS缺少房型", code, a.count, None, a.row, None, f"APAC有 {a.name_cn}/{a.name_en}"))
        elif p and not a:
            diffs.append(Difference("ERROR", "APAC缺少房型", code, None, p.count, None, p.row, f"PMS有 {p.name_cn}/{p.name_en}"))
        elif a and p and a.count != p.count:
            diffs.append(Difference("ERROR", "房量不一致", code, a.count, p.count, a.row, p.row, f"APAC={a.count}, PMS={p.count}"))
    return diffs


def write_csv(path: Path, diffs: list[Difference]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(diffs[0]).keys()) if diffs else [
            "level", "issue", "code", "apac_count", "pms_count", "apac_row", "pms_row", "detail"
        ])
        writer.writeheader()
        for diff in diffs:
            writer.writerow(asdict(diff))


def main() -> None:
    parser = argparse.ArgumentParser(description="校验 APAC PiM 与 PMS 代码表房型/房量一致性")
    parser.add_argument("--apac", required=True, help="APAC PiM xlsb 文件路径")
    parser.add_argument("--pms", required=True, help="PMS 标准代码表 xlsx 文件路径")
    parser.add_argument("--out", default="room_type_check_report.csv", help="输出CSV报告路径")
    parser.add_argument("--json", default="", help="可选：输出JSON报告路径")
    args = parser.parse_args()

    apac_path = Path(args.apac).expanduser()
    pms_path = Path(args.pms).expanduser()
    apac_rooms = extract_apac_room_types(apac_path)
    pms_rooms = extract_pms_room_types(pms_path)
    diffs = compare(apac_rooms, pms_rooms)

    out_path = Path(args.out).expanduser()
    write_csv(out_path, diffs)
    if args.json:
        Path(args.json).expanduser().write_text(
            json.dumps([asdict(d) for d in diffs], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"APAC有效房型: {len(apac_rooms)}")
    print(f"PMS有效房型: {len(pms_rooms)}")
    print(f"发现差异: {len(diffs)}")
    print(f"报告已输出: {out_path}")
    if diffs:
        print("\n前10条差异：")
        for diff in diffs[:10]:
            print(f"- [{diff.level}] {diff.issue}: {diff.code} | APAC={diff.apac_count} PMS={diff.pms_count} | {diff.detail}")


if __name__ == "__main__":
    main()
