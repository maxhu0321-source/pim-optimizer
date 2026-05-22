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

# 欢朋品牌色
_BLUE = (0, 119, 200)       # #0077C8
_BLUE_DARK = (0, 91, 172)   # #005BAC
_RED = (198, 53, 39)        # #C63527
_DARK = (26, 42, 74)        # #1A2A4A
_GREEN = (0, 150, 80)
_ORANGE = (200, 120, 0)


class PiMPDF(FPDF):
    def __init__(self):
        super().__init__()
        self._has_cn_font = False
        if _CN_FONT.exists():
            try:
                self.add_font("SourceHan", "", str(_CN_FONT))
                self._has_cn_font = True
            except Exception:
                pass
        if _EN_FONT.exists():
            try:
                self.add_font("Hampton", "", str(_EN_FONT))
            except Exception:
                pass

    def _font(self, size=10):
        """设置字体，优先用思源黑体"""
        if self._has_cn_font:
            self.set_font("SourceHan", size=size)
        else:
            self.set_font("Helvetica", "", size)

    def header(self):
        self._font(18)
        self.set_text_color(*_BLUE_DARK)
        self.cell(0, 14, "PiM Pack 校验报告", new_x="LMARGIN", new_y="NEXT", align="C")
        # 品牌蓝色分割线
        self.set_draw_color(*_BLUE)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Hampton by Hilton - Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf(report: ValidationReport) -> bytes:
    """生成PDF报告，返回bytes"""
    pdf = PiMPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 基本信息
    pdf._font(10)
    pdf.set_text_color(*_DARK)
    pdf.cell(0, 7, f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"PiM文件：{report.pim_file}", new_x="LMARGIN", new_y="NEXT")
    if report.pms_file:
        pdf.cell(0, 7, f"PMS文件：{report.pms_file}", new_x="LMARGIN", new_y="NEXT")

    # 结论
    pdf.ln(4)
    pdf._font(14)
    if report.can_submit:
        pdf.set_text_color(*_GREEN)
        pdf.cell(0, 10, "结论：可以提交", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_text_color(*_RED)
        pdf.cell(0, 10, f"结论：存在 {report.error_count} 条必须修改的问题", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_DARK)

    # 概览
    pdf.ln(4)
    pdf._font(12)
    pdf.set_text_color(*_BLUE_DARK)
    pdf.cell(0, 8, "校验概览", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_DARK)
    pdf._font(10)

    col_w = [60, 30]
    rows = [
        ("PiM房型数", str(report.total_rooms_pim)),
        ("必须修改", str(report.error_count)),
        ("建议修改", str(report.warning_count)),
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
        pdf.set_text_color(*_RED)
        pdf.cell(0, 8, f"必须修改（{len(error_items)} 条）", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*_DARK)
        pdf._font(10)

        for i, e in enumerate(error_items, 1):
            friendly_loc = get_friendly_location(e.rule_id, e.location)
            guide = get_location_guide(e.rule_id)

            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"{i}. [{e.rule_id}] {e.message}")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"   位置：{friendly_loc}")
            if guide:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=0, h=6, text=f"   如何找到：{guide}")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"   修改建议：{e.fix_suggestion}")

    if warn_items:
        pdf.ln(6)
        pdf._font(12)
        pdf.set_text_color(*_ORANGE)
        pdf.cell(0, 8, f"建议修改（{len(warn_items)} 条）", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*_DARK)
        pdf._font(10)

        for i, e in enumerate(warn_items, 1):
            friendly_loc = get_friendly_location(e.rule_id, e.location)
            guide = get_location_guide(e.rule_id)

            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"{i}. [{e.rule_id}] {e.message}")
            if guide:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=0, h=6, text=f"   如何找到：{guide}")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=6, text=f"   修改建议：{e.fix_suggestion}")

    if not error_items and not warn_items:
        pdf.ln(6)
        pdf._font(12)
        pdf.set_text_color(*_GREEN)
        pdf.cell(0, 8, "所有检查通过，可以提交！", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*_DARK)

    return pdf.output()
