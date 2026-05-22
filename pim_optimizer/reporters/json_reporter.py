"""JSON格式报告输出"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from ..models import ValidationReport


def to_json(report: ValidationReport) -> str:
    """生成JSON格式报告"""
    output = {
        "report_meta": {
            "generated_at": datetime.now().isoformat(),
            "pim_file": report.pim_file,
            "pms_file": report.pms_file,
        },
        "summary": {
            "total_rooms_pim": report.total_rooms_pim,
            "total_rooms_pms": report.total_rooms_pms,
            "errors": report.error_count,
            "warnings": report.warning_count,
            "can_submit": report.can_submit,
        },
        "issues": [asdict(e) for e in report.errors],
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def write_json(report: ValidationReport, path: Path) -> None:
    path.write_text(to_json(report), encoding="utf-8")
