"""生成 PiM Pack 填写指引 PDF"""

from fpdf import FPDF
from pathlib import Path
import os

class GuidesPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 119, 200)
        self.rect(0, 0, 210, 12, 'F')
        self.set_font("chinese", "", 8)
        self.set_text_color(255, 255, 255)
        self.set_y(3)
        self.cell(0, 6, "Hampton by Hilton · PiM Pack 填写指引", align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("chinese", "", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"第 {self.page_no} 页", align="C")


def generate():
    pdf = GuidesPDF()

    font_path = Path(__file__).parent / "fonts" / "SourceHanSansCN-Regular.otf"
    if font_path.exists():
        pdf.add_font("chinese", "", str(font_path))
    else:
        print(f"Warning: font not found at {font_path}")
        return

    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # 标题
    pdf.set_font("chinese", "", 18)
    pdf.set_text_color(0, 63, 122)
    pdf.cell(0, 12, "PiM Pack 填写指引", ln=True, align="C")
    pdf.set_font("chinese", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Hampton by Hilton 欢朋酒店 · 预开业资料填写注意事项", ln=True, align="C")
    pdf.ln(8)

    def section_title(text):
        pdf.set_font("chinese", "", 13)
        pdf.set_text_color(0, 91, 172)
        pdf.cell(0, 10, text, ln=True)
        pdf.set_draw_color(0, 119, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    def sub_title(text):
        pdf.set_font("chinese", "", 11)
        pdf.set_text_color(0, 63, 122)
        pdf.cell(0, 8, text, ln=True)
        pdf.ln(1)

    def body(text):
        pdf.set_font("chinese", "", 9)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5.5, text)
        pdf.ln(2)

    def bullet(text):
        pdf.set_font("chinese", "", 9)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(6, 5.5, "·")
        pdf.multi_cell(0, 5.5, text)
        pdf.ln(0.5)

    # ====== 内容 ======

    section_title("一、需要准备的两份文件")
    bullet("PiM Pack（.xlsb）：酒店信息采集主表，包含酒店特色、房型、设施等全部信息")
    bullet("PMS 标准代码表（.xlsx）：酒店管理系统的房型代码映射表，用于与 PiM 对照校验")
    body("两份表必须同时提交，且房型代码和房量必须完全一致。不一致会导致希尔顿官网无法售卖，修复需要 21 个工作日。")

    section_title("二、PiM Pack 关键页签说明")
    body("打开 PiM Pack 后，左下角会看到多个页签标签（PiM-1、PiM-2、PiM-5 等），点击切换。对应关系如下：")
    bullet("PiM-1 = 「1.酒店特色信息」")
    bullet("PiM-2 = 「2.房型房价信息」")
    bullet("PiM-5 = 「5.客房设施信息」")
    pdf.ln(3)

    sub_title("「1.酒店特色信息」页签")
    body("这是内容最多的页签，包含以下板块（向下滚动找到）：")
    bullet("PROPERTY INFORMATION 酒店信息（约第6行起）：经纬度、电话、酒店描述、位置描述、到达路线")
    bullet("PROPERTY REGISTRATION 酒店登记流程（约第80行起）")
    bullet("SAFETY 酒店安保信息（约第104行起）：Fire/Safety/Security，逐项填 Y 或 N")
    bullet("CLASSIFICATION 类别（约第133行起）：城市名称、距市中心距离")
    bullet("GUEST ROOM 客房（约第263行起）：楼层数、建筑数")
    bullet("MEETING ROOM 会议室（约第388行起）")
    bullet("PROPERTY SERVICES 酒店服务（约第477行起）：大堂、餐厅等")
    pdf.ln(2)

    sub_title("「2.房型房价信息」页签")
    bullet("房型代码：必须与 PMS 代码表一致（如 SKR、SVR、SLS 等）")
    bullet("房量：每个房型的房间数，PiM 和 PMS 必须完全一致")
    bullet("面积（Room Size）：填整数，不能填小数或区间（如 \"25-30\"）")
    bullet("无烟房（Non-Smoking）：选 Yes/No，Yes 表示该房型超过半数为无烟房")
    bullet("最大入住人数（Max Occupancy）：欢朋默认为 3 人")
    bullet("无障碍房（Accessible Room）：至少 1 个房型需标注为 Yes")
    bullet("楼层数：填酒店运营的总楼层数（数字），不是具体楼层号")
    pdf.ln(2)

    sub_title("「5.客房设施信息」页签")
    body("页面结构：顶部是房型汇总，下方是 Room Amenities 房间设施 区域（逐行填写各房型设施数量）。")
    bullet("Non-Smoking 无烟房：每个房型的无烟房间数，需与「2.房型房价信息」的 Yes/No 标记匹配")
    bullet("Sofa / Sofa Bed 沙发/沙发床：数量不能超过对应房型总房间数")
    bullet("Connecting Room 连通房：数量必须与「2.房型房价信息」一致，品牌标准 ≥ 2 间")
    bullet("Bathrobe 浴袍：数量不能超过总房间数")
    bullet("Rollaways 折叠床：需填写数量（可以为 0）")
    bullet("Mini Fridge 小冰箱：普通房型需要有")

    pdf.add_page()
    section_title("三、常见错误 TOP 10")
    body("以下是历史审核中最常见的驳回原因，请重点检查：")

    top10 = [
        ("1. 房型代码两表不一致", "PiM Pack 和 PMS 代码表的房型代码必须完全相同"),
        ("2. 同一房型房量不一致", "两份表里同一房型的房间数必须一致"),
        ("3. 无烟房数量前后矛盾", "「2.房型房价信息」的 Yes/No 标记与「5.客房设施信息」的数量不匹配"),
        ("4. 座机电话未填或填占位符", "如填 123456 会被驳回，需填真实号码"),
        ("5. 经纬度填反", "中国：纬度 18-54，经度 73-135，不要写反"),
        ("6. 房型面积填小数", "面积只能填整数，不能写 25.5"),
        ("7. 距离只填单位无数字", "\"KM\" 无效，需填 \"15 KM\""),
        ("8. 无障碍房未标注", "至少 1 个房型的 Accessible Room 需设为 Yes"),
        ("9. 酒店描述留空", "中英文描述均为必填"),
        ("10. 楼层填具体楼层号", "应填总楼层数（如 12），不填 \"3F-12F\""),
    ]

    for title, desc in top10:
        pdf.set_font("chinese", "", 9)
        pdf.set_text_color(0, 63, 122)
        pdf.cell(0, 6, title, ln=True)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, f"    {desc}")
        pdf.ln(2)

    section_title("四、品牌标准要求")
    bullet("无烟房 ≥ 总房量的 30%")
    bullet("连通房 ≥ 2 间")
    bullet("至少 1 间无障碍房")
    bullet("SLS（亲子套房）必须配沙发床")
    bullet("Max Occupancy 默认为 3 人")
    bullet("普通房型需配小冰箱（Mini Fridge）")

    pdf.ln(5)
    section_title("五、提交前自查清单")
    checks = [
        "所有房型代码 PiM 和 PMS 完全一致",
        "所有房型房量 PiM 和 PMS 完全一致",
        "无烟房 Yes/No 标记与设施表数量匹配",
        "电话号码为真实座机号码",
        "经纬度格式正确且未填反",
        "房型面积为整数",
        "距市中心距离填了具体数字 + KM",
        "至少 1 个无障碍房已标注",
        "酒店中英文描述已填写",
        "安保信息（SAFETY）已逐项填写 Y/N",
        "折叠床数量已填（没有填 0）",
        "ADR（年平均房价）已填写",
    ]
    for i, check in enumerate(checks, 1):
        bullet(f"[ ]  {check}")

    pdf.ln(5)
    pdf.set_font("chinese", "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "如有疑问请联系 Development 团队 · 本指引基于历史 40+ 封审核邮件整理", align="C")

    out_path = Path(__file__).parent / "templates" / "PiM_Pack_填写指引.pdf"
    pdf.output(str(out_path))
    print(f"Generated: {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    generate()
