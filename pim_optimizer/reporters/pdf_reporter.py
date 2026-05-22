"""PDF格式报告输出（中文支持）"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from ..models import ValidationReport
from ..location_labels import get_friendly_location, get_location_guide

# 字体文件路径
_FONTS_DIR = Path(__file__).parent.parent.parent / "fonts"
_CN_FONT = _FONTS_DIR / "SourceHanSansCN-Regular.otf"
_EN_FONT = _FONTS_DIR / "HamptonSans-Regular.ttf"


class PiMPDF(FPDF):
    def __init__(self):
        super().__init__()
        # 注册中文字体
        if _CN_FONT.exists():
            self.add_font("SourceHan", "", str(_CN_FONT))
        if _EN_FONT.exists():
            self.add_font("Hampton", "", str(_EN_FONT))

    def _font(self, size=10, bold=False):
        """设置字体，优先用思源黑体"""
        if _CN_FONT.exists():
            self.set_font("SourceHan", size=size)
        else:
            self.set_font("Helvetica", "B" if bold else "", size)

    def header(self):
        self._font(16)
        self.cell(0, 12, "PiM Pack 校验报告", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf(report: ValidationReport) -> bytes:
    """生成PDF报告，返回bytes"""
    pdf = PiMPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 基本信息
    pdf._font(10)
    pdf.cell(0, 7, f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"PiM文件：{report.pim_file}", new_x="LMARGIN", new_y="NEXT")
    if report.pms_file:
        pdf.cell(0, 7, f"PMS文件：{report.pms_file}", new_x="LMARGIN", new_y="NEXT")

    # 结论
    pdf.ln(4)
    pdf._font(14)
    if report.can_submit:
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 10, "结论：可以提交", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, f"结论：存在 {report.error_count} 条阻塞问题", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    # 概览表格
    pdf.ln(4)
    pdf._font(12)
    pdf.cell(0, 8, "概览", new_x="LMARGIN", new_y="NEXT")
    pdf._font(10)

    col_w = [60, 30]
    rows = [
        ("PiM房型数", str(report.total_rooms_pim)),
        ("错误数", str(report.error_count)),
        ("警告数", str(report.warning_count)),
    ]
    if report.pms_file:
        rows.insert(1, ("PMS房型数", str(report.total_rooms_pms)))

    for label, val in rows:
        pdf.cell(col_w[0], 7, label, border=1)
        pdf.cell(col_w[1], 7, val, border=1, new_x="LMARGIN", new_y="NEXT")

    # 错误详情
    error_items = [e for e in report.errors if e.severity == "error"]
    warn_items = [e for e in report.errors if e.severity == "warning"]

    if error_items:
        pdf.ln(6)
        pdf._font(12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, f"必须修复（{len(error_items)} 条）", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf._font(10)

        for i, e in enumerate(error_items, 1):
            friendly_loc = get_friendly_location(e.rule_id, e.location)
            guide = get_location_guide(e.rule_id)

            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"{i}. [{e.rule_id}] {e.message}")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"位置: {friendly_loc}")
            if guide:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=0, h=6, text=f"查找: {guide}")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"建议: {e.fix_suggestion}")

    if warn_items:
        pdf.ln(6)
        pdf._font(12)
        pdf.set_text_color(200, 150, 0)
        pdf.cell(0, 8, f"建议修复（{len(warn_items)} 条）", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf._font(10)

        for i, e in enumerate(warn_items, 1):
            friendly_loc = get_friendly_location(e.rule_id, e.location)
            guide = get_location_guide(e.rule_id)

            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"{i}. [{e.rule_id}] {e.message}")
            if guide:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=0, h=6, text=f"查找: {guide}")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"建议: {e.fix_suggestion}")

    if not error_items and not warn_items:
        pdf.ln(6)
        pdf._font(12)
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 8, "所有检查通过，可以提交。", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

    return pdf.output()
