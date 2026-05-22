"""Markdown格式报告输出"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..models import ValidationReport


def to_markdown(report: ValidationReport) -> str:
    """生成Markdown格式报告"""
    lines = []
    status = "✅ 可以提交" if report.can_submit else "❌ 存在阻塞问题，无法提交"

    lines.append("# PiM 校验报告")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**PiM文件**: {report.pim_file}")
    if report.pms_file:
        lines.append(f"**PMS文件**: {report.pms_file}")
    lines.append(f"**结论**: {status}")
    lines.append("")

    # 概览
    lines.append("## 概览")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| PiM房型数 | {report.total_rooms_pim} |")
    if report.pms_file:
        lines.append(f"| PMS房型数 | {report.total_rooms_pms} |")
    lines.append(f"| 错误 | {report.error_count} |")
    lines.append(f"| 警告 | {report.warning_count} |")
    lines.append("")

    # 按类别分组
    errors_by_cat: dict[str, list] = {}
    for e in report.errors:
        errors_by_cat.setdefault(e.category, []).append(e)

    cat_names = {
        "cross_file": "跨文件一致性",
        "internal": "PiM内部一致性",
        "brand": "品牌标准",
        "completeness": "必填项",
        "format": "格式/数值",
    }

    # 错误
    error_items = [e for e in report.errors if e.severity == "error"]
    if error_items:
        lines.append("## 必须修复 (Errors)")
        for i, e in enumerate(error_items, 1):
            cat_label = cat_names.get(e.category, e.category)
            lines.append(f"{i}. **[{e.rule_id}]** {e.message}")
            lines.append(f"   - 位置: {e.location}")
            lines.append(f"   - 建议: {e.fix_suggestion}")
        lines.append("")

    # 警告
    warn_items = [e for e in report.errors if e.severity == "warning"]
    if warn_items:
        lines.append("## 建议修复 (Warnings)")
        for i, e in enumerate(warn_items, 1):
            lines.append(f"{i}. **[{e.rule_id}]** {e.message}")
            lines.append(f"   - 建议: {e.fix_suggestion}")
        lines.append("")

    if not error_items and not warn_items:
        lines.append("## 检查通过")
        lines.append("未发现问题，可以提交。")

    return "\n".join(lines)


def write_markdown(report: ValidationReport, path: Path) -> None:
    path.write_text(to_markdown(report), encoding="utf-8")
