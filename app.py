#!/usr/bin/env python3
"""PiM 校验工具 - Web界面 (Streamlit)"""

import streamlit as st
import tempfile
from pathlib import Path

st.set_page_config(page_title="PiM 校验工具", page_icon="🏨", layout="wide")

# ========== 品牌色CSS注入 ==========
st.markdown("""
<style>
    /* 欢朋品牌蓝色系 */
    :root {
        --hampton-blue: #0077C8;
        --hampton-dark: #005BAC;
        --hampton-deep: #003F7A;
        --hampton-light: #E6F3FB;
        --hampton-red: #C63527;
    }
    .stApp > header {
        background-color: #0077C8;
    }
    h1, h2, h3 {
        color: #003F7A !important;
    }
    .stMetric label {
        color: #005BAC !important;
    }
    div[data-testid="stExpander"] details summary {
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏导航 ==========
page = st.sidebar.radio("功能", ["📋 PiM 校验", "📖 模版与指南"])

# ========== 管理页密码 ==========
ADMIN_PASSWORD = "hampton2024"


# ========== 校验页面 ==========
if page == "📋 PiM 校验":
    st.title("🏨 PiM Pack 校验工具")
    st.caption("Hampton by Hilton · 上传文件，自动检测常见填写错误")

    col1, col2 = st.columns(2)

    with col1:
        pim_file = st.file_uploader("上传 PiM Pack (.xlsb)", type=["xlsb", "xlsm", "xls"])

    with col2:
        pms_file = st.file_uploader("上传 PMS标准代码表 (.xlsx)", type=["xlsx"], help="可选。上传后可进行跨文件房型一致性校验")

    if st.button("开始校验", type="primary", disabled=not pim_file):
        with st.spinner("正在解析文件并执行校验规则..."):
            # 保存上传文件到临时目录
            tmp_dir = tempfile.mkdtemp()
            pim_path = Path(tmp_dir) / pim_file.name
            pim_path.write_bytes(pim_file.read())

            pms_path = None
            if pms_file:
                pms_path = Path(tmp_dir) / pms_file.name
                pms_path.write_bytes(pms_file.read())

            from pim_optimizer.extractors.pim_extractor import extract_pim
            from pim_optimizer.extractors.pms_extractor import extract_pms
            from pim_optimizer.models import ValidationReport
            from pim_optimizer.validators.engine import run_all
            from pim_optimizer.location_labels import get_friendly_location, get_location_guide

            try:
                pim_data = extract_pim(pim_path)
                pms_data = extract_pms(pms_path) if pms_path else None
                errors = run_all(pim_data, pms_data)

                report = ValidationReport(
                    pim_file=pim_file.name,
                    pms_file=pms_file.name if pms_file else "",
                    total_rooms_pim=len(pim_data.room_types),
                    total_rooms_pms=len(pms_data.room_types) if pms_data else 0,
                    errors=errors,
                )

                # ===== 结论 =====
                if report.can_submit:
                    st.success(f"✅ 校验通过！可以提交。（{report.warning_count} 条优化建议）")
                else:
                    st.error(f"❌ 发现 {report.error_count} 条必须修改的问题，修改后才能提交")

                if not pms_file:
                    st.info("💡 提示：未上传PMS代码表，已跳过跨文件校验。如需完整校验建议同时上传。")

                # ===== 指标卡片 =====
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("PiM房型数", report.total_rooms_pim)
                m2.metric("PMS房型数", report.total_rooms_pms if pms_file else "未上传")
                m3.metric("必须修改", report.error_count)
                m4.metric("建议修改", report.warning_count)

                # ===== 房型明细对照表 =====
                st.divider()
                st.subheader("📋 房型明细")

                import pandas as pd

                if pms_data:
                    # 双表对照
                    pim_rooms = {rt.code: rt for rt in pim_data.room_types}
                    pms_rooms = {}
                    for rt in pms_data.room_types:
                        key = rt.hilton_code if rt.hilton_code else rt.code
                        pms_rooms[key] = rt

                    all_codes = sorted(set(pim_rooms.keys()) | set(pms_rooms.keys()))

                    rows_data = []
                    for code in all_codes:
                        pim_rt = pim_rooms.get(code)
                        pms_rt = pms_rooms.get(code)
                        pim_count = pim_rt.count if pim_rt else "-"
                        pms_count = pms_rt.count if pms_rt else "-"
                        name = pim_rt.name_cn if pim_rt else (pms_rt.name_cn if pms_rt else "")

                        if pim_rt and pms_rt:
                            if pim_rt.count == pms_rt.count:
                                status = "✅ 一致"
                            else:
                                status = "❌ 房量不一致"
                        elif pim_rt and not pms_rt:
                            status = "⚠️ PMS中缺失"
                        else:
                            status = "⚠️ PiM中缺失"

                        rows_data.append({
                            "房型代码": code,
                            "中文名": name,
                            "PiM房量": pim_count,
                            "PMS房量": pms_count,
                            "匹配状态": status,
                        })

                    df = pd.DataFrame(rows_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    # 仅PiM
                    rows_data = []
                    for rt in pim_data.room_types:
                        rows_data.append({
                            "房型代码": rt.code,
                            "中文名": rt.name_cn,
                            "英文名": rt.name_en,
                            "房量": rt.count,
                            "无烟": "Yes" if rt.non_smoking_count > 0 else "No",
                            "无障碍": "Yes" if rt.is_accessible else "No",
                        })
                    df = pd.DataFrame(rows_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                # ===== 错误详情 =====
                if errors:
                    st.divider()
                    error_items = [e for e in errors if e.severity == "error"]
                    warn_items = [e for e in errors if e.severity == "warning"]

                    def _source_tag(error):
                        loc = error.location.upper()
                        if "PMS" in loc:
                            return "🔵 PMS问题"
                        if error.category == "cross_file":
                            return "🔴 两表不一致"
                        return "🟠 PiM问题"

                    if error_items:
                        st.subheader(f"🚨 必须修改（{len(error_items)} 条）")
                        st.caption("以下问题会导致提交失败，请逐一修改")
                        for e in error_items:
                            tag = _source_tag(e)
                            friendly_loc = get_friendly_location(e.rule_id, e.location)
                            guide = get_location_guide(e.rule_id)

                            with st.expander(f"{tag}  [{e.rule_id}] {e.message}"):
                                st.markdown(f"**在哪里改**：{friendly_loc}")
                                if guide:
                                    st.info(f"📍 如何找到：{guide}")
                                st.markdown(f"**修改建议**：{e.fix_suggestion}")

                    if warn_items:
                        st.subheader(f"⚠️ 建议修改（{len(warn_items)} 条）")
                        st.caption("不影响提交，但建议优化")
                        for e in warn_items:
                            tag = _source_tag(e)
                            friendly_loc = get_friendly_location(e.rule_id, e.location)
                            guide = get_location_guide(e.rule_id)

                            with st.expander(f"{tag}  [{e.rule_id}] {e.message}"):
                                st.markdown(f"**在哪里改**：{friendly_loc}")
                                if guide:
                                    st.info(f"📍 如何找到：{guide}")
                                st.markdown(f"**修改建议**：{e.fix_suggestion}")

                # ===== 下载报告 =====
                st.divider()
                dl_col1, dl_col2 = st.columns(2)

                # PDF下载
                with dl_col1:
                    try:
                        from pim_optimizer.reporters.pdf_reporter import generate_pdf
                        pdf_bytes = generate_pdf(report)
                        st.download_button(
                            "📥 下载校验报告 (PDF)",
                            pdf_bytes,
                            file_name=f"PiM校验报告_{pim_file.name.split('.')[0]}.pdf",
                            mime="application/pdf",
                            type="primary",
                        )
                    except Exception as pdf_err:
                        st.warning(f"PDF生成失败：{pdf_err}")
                        # Markdown 备用
                        from pim_optimizer.reporters.markdown_reporter import to_markdown
                        md_report = to_markdown(report)
                        st.download_button(
                            "📥 下载校验报告 (文本)",
                            md_report,
                            file_name=f"PiM校验报告_{pim_file.name.split('.')[0]}.md",
                            mime="text/markdown",
                        )

                # Markdown备用下载
                with dl_col2:
                    from pim_optimizer.reporters.markdown_reporter import to_markdown
                    md_report = to_markdown(report)
                    st.download_button(
                        "📥 下载校验报告 (文本版)",
                        md_report,
                        file_name=f"PiM校验报告_{pim_file.name.split('.')[0]}.md",
                        mime="text/markdown",
                    )

            except Exception as e:
                st.error(f"校验出错: {e}")
                st.exception(e)

    st.divider()
    st.caption("覆盖30+条规则：跨文件一致性 | 内部一致性 | 品牌标准 | 必填项 | 格式检查")


# ========== 模版与指南 ==========
elif page == "📖 模版与指南":
    st.title("📖 模版下载与填写指南")
    st.caption("Hampton by Hilton · 预开业资料填写所需的模版和注意事项")

    # ===== 模版下载 =====
    st.subheader("📥 模版下载")

    dl1, dl2 = st.columns(2)

    with dl1:
        st.markdown("**PiM Pack 模版**")
        st.caption("亚太区预开业酒店信息采集表（.xlsb）")
        pim_template = Path("templates/PiM_Pack_Hampton_Template.xlsb")
        if pim_template.exists():
            st.download_button(
                "下载 PiM Pack 模版",
                pim_template.read_bytes(),
                file_name="PiM_Pack_Hampton_Template.xlsb",
                mime="application/octet-stream",
                type="primary",
            )
        else:
            st.info("模版文件即将上线，请联系 Development 团队获取最新版本")

    with dl2:
        st.markdown("**PMS 标准代码表**")
        st.caption("希尔顿欢朋酒店PMS标准代码表（.xlsx）")
        pms_template = Path("templates/PMS_Standard_Code_Table.xlsx")
        if pms_template.exists():
            st.download_button(
                "下载 PMS 代码表模版",
                pms_template.read_bytes(),
                file_name="PMS_Standard_Code_Table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        else:
            st.info("模版文件即将上线，请联系 Development 团队获取最新版本")

    # ===== 填写指南 =====
    st.divider()
    st.subheader("📝 填写指南")

    st.markdown("#### 需要准备的两份文件")
    st.markdown("""
| 文件 | 格式 | 用途 |
|------|------|------|
| **PiM Pack** | .xlsb | 酒店信息采集主表，包含酒店特色、房型、设施等全部信息 |
| **PMS 标准代码表** | .xlsx | 酒店管理系统的房型代码映射表，用于与PiM对照校验 |
""")

    st.markdown("#### PiM Pack 关键页签说明")
    st.info("💡 打开PiM Pack后，左下角会看到多个页签标签，点击对应名称即可切换")
    with st.expander("「1.酒店特色信息」— 酒店基本信息", expanded=False):
        st.markdown("""
**包含以下板块**（向下滚动可找到）：

| 板块 | 行号参考 | 关键字段 |
|------|---------|---------|
| **PROPERTY INFORMATION 酒店信息** | 约第6行起 | 经纬度、电话、酒店描述、位置描述、到达路线 |
| **PROPERTY REGISTRATION 酒店登记流程** | 约第80行起 | 登记相关信息 |
| **SAFETY 酒店安保信息** | 约第104行起 | Fire/Safety/Security，逐项填Y或N |
| **CLASSIFICATION 类别** | 约第133行起 | 城市名称、距市中心距离、酒店星级 |
| **GUEST ROOM 客房** | 约第263行起 | 楼层数、建筑数 |
| **MEETING ROOM 会议室** | 约第388行起 | 会议室信息 |
| **PROPERTY SERVICES 酒店服务** | 约第477行起 | 大堂、餐厅等服务设施 |
""")

    with st.expander("「2.房型房价信息」— 房型代码、房量、配置", expanded=False):
        st.markdown("""
- **房型代码**：必须与PMS代码表一致（如 SKR、SVR、SLS 等）
- **房量**：每个房型的房间数，PiM Pack 和 PMS代码表必须完全一致
- **面积**：填整数（平方米），不能填小数或区间（如"25-30"）
- **无烟房（Non-Smoking）**：选 Yes/No，Yes 表示该房型超过半数为无烟房
- **最大入住人数（Max Occupancy）**：欢朋默认为 3 人
- **无障碍房（Accessible Room）**：至少1个房型需标注为Yes
- **楼层数**：填酒店运营的总楼层数（数字），不是填具体楼层号
""")

    with st.expander("「5.客房设施信息」— 各房型设施数量明细", expanded=False):
        st.markdown("""
**页面结构**：顶部是房型汇总（普通客房/套房/无障碍房），下方是 **Room Amenities 房间设施** 区域（逐行填写各房型的设施数量）。

**Room Amenities 区域常见行**：
- **Non-Smoking 无烟房**：每个房型的无烟房间数，需与「2.房型房价信息」的Yes/No标记匹配
- **Sofa / Sofa Bed 沙发/沙发床**：数量不能超过对应房型总房间数
- **Connecting Room 连通房**：数量必须与「2.房型房价信息」一致，品牌标准≥2间
- **Bathrobe 浴袍**：数量不能超过总房间数
- **Rollaways 折叠床**：需填写数量（可以为0）
- **Mini Fridge 小冰箱**：普通房型需要有
""")

    st.markdown("#### 常见错误 TOP 10")
    st.markdown("""
| # | 错误 | 频率 | 说明 |
|---|------|------|------|
| 1 | 房型代码两表不一致 | 🔴 极高 | PiM Pack 和 PMS代码表的房型代码必须完全相同 |
| 2 | 同一房型房量不一致 | 🔴 极高 | 两份表里同一房型的房间数必须一致 |
| 3 | 无烟房数量前后矛盾 | 🔴 高 | 「2.房型房价信息」的Yes/No标记与「5.客房设施信息」的数量不匹配 |
| 4 | 座机电话未填或填占位符 | 🟠 高 | 如填123456会被驳回 |
| 5 | 经纬度填反 | 🟠 高 | 中国：纬度18-54，经度73-135 |
| 6 | 房型面积填小数 | 🟠 中 | 面积只能填整数 |
| 7 | 距离只填单位无数字 | 🟠 中 | "KM"无效，需填"15 KM" |
| 8 | 无障碍房未标注 | 🟡 中 | 至少1个房型需设为无障碍 |
| 9 | 酒店描述留空 | 🟡 中 | 中英文描述均为必填 |
| 10 | 楼层填具体楼层号 | 🟡 低 | 应填总楼层数（数字），非"1F,2F" |
""")

    # ===== 校验规则覆盖范围 =====
    st.divider()
    st.subheader("🔍 本工具校验范围")
    st.caption("当前覆盖 32 条自动校验规则")
    st.markdown("""
| 类别 | 规则数 | 说明 |
|------|--------|------|
| A 跨文件一致性 | 3条 | PiM与PMS房型代码、房量匹配 |
| B 内部一致性 | 6条 | 无烟房/沙发/连通房等数据前后一致 |
| C 品牌标准 | 7条 | 无烟≥30%、连通≥2、无障碍、SLS沙发床 |
| D 必填项 | 9条 | 描述/ADR/电话/经纬度/安保/城市 |
| E 格式检查 | 7条 | 面积整数、字符限制、经纬度格式 |
""")

    # ===== 管理员设置（折叠隐藏） =====
    st.divider()
    with st.expander("🔒 管理员设置"):
        if "admin_auth" not in st.session_state:
            st.session_state.admin_auth = False

        if not st.session_state.admin_auth:
            pwd = st.text_input("管理密码", type="password")
            if st.button("登录"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("密码错误")
        else:
            st.success("✅ 已登录")
            from pim_optimizer.config import BRAND

            st.markdown("**品牌标准阈值**")
            st.caption("修改后点击保存，下次校验生效（仅当前会话有效）")

            col1, col2 = st.columns(2)
            with col1:
                new_ns_ratio = st.slider(
                    "无烟房最低比例",
                    min_value=0.0, max_value=1.0,
                    value=BRAND["min_non_smoking_ratio"],
                    step=0.05, format="%.0f%%",
                )
                new_connecting = st.number_input(
                    "连通房最少间数", min_value=0, max_value=10,
                    value=BRAND["min_connecting_rooms"],
                )
                new_accessible = st.number_input(
                    "无障碍房最少间数", min_value=0, max_value=10,
                    value=BRAND["min_accessible_rooms"],
                )
            with col2:
                new_max_occ = st.number_input(
                    "默认最大入住人数", min_value=1, max_value=6,
                    value=BRAND["default_max_occupancy"],
                )
                new_loc_chars = st.number_input(
                    "位置短描述最大字符数", min_value=20, max_value=100,
                    value=BRAND["location_desc_max_chars"],
                )

            if st.button("保存配置", type="primary"):
                BRAND["min_non_smoking_ratio"] = new_ns_ratio
                BRAND["min_connecting_rooms"] = new_connecting
                BRAND["min_accessible_rooms"] = new_accessible
                BRAND["default_max_occupancy"] = new_max_occ
                BRAND["location_desc_max_chars"] = new_loc_chars
                st.success("✅ 配置已保存（当前会话生效）")
