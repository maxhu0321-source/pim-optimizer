#!/usr/bin/env python3
"""PiM 校验工具 - Web界面 (Streamlit)"""

import streamlit as st
import tempfile
from pathlib import Path

st.set_page_config(page_title="PiM 校验工具", page_icon="🏨", layout="wide")

# ========== 侧边栏导航 ==========
page = st.sidebar.radio("功能", ["📋 PiM 校验", "⚙️ 规则管理"])

# ========== 管理页密码 ==========
ADMIN_PASSWORD = "hampton2024"  # 可以改成你想要的密码


# ========== 校验页面 ==========
if page == "📋 PiM 校验":
    st.title("🏨 PiM Pack 校验工具")
    st.caption("上传 PiM Pack (.xlsb) 和 PMS标准代码表 (.xlsx)，自动检测常见错误")

    col1, col2 = st.columns(2)

    with col1:
        pim_file = st.file_uploader("上传 PiM Pack (.xlsb)", type=["xlsb", "xlsm", "xls"])

    with col2:
        pms_file = st.file_uploader("上传 PMS标准代码表 (.xlsx)", type=["xlsx"])

    # 单文件提醒
    if pim_file and not pms_file:
        st.warning("⚠️ 未上传PMS代码表，将跳过跨文件房型一致性校验。建议同时上传两个文件获得完整校验结果。")

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
                    st.success(f"✅ 可以提交！（{report.warning_count} 条建议）")
                else:
                    st.error(f"❌ 存在 {report.error_count} 条阻塞问题，无法提交")

                # ===== 指标卡片 =====
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("PiM房型数", report.total_rooms_pim)
                m2.metric("PMS房型数", report.total_rooms_pms if pms_file else "-")
                m3.metric("错误", report.error_count)
                m4.metric("警告", report.warning_count)

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
                            status = "⚠️ PMS中缺失此房型"
                        else:
                            status = "⚠️ PiM中缺失此房型"

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

                # ===== 错误详情（用户友好位置 + 归属方标注）=====
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
                        st.subheader(f"🚨 必须修复（{len(error_items)} 条）")
                        for e in error_items:
                            tag = _source_tag(e)
                            friendly_loc = get_friendly_location(e.rule_id, e.location)
                            guide = get_location_guide(e.rule_id)

                            with st.expander(f"{tag}  [{e.rule_id}] {e.message}"):
                                st.markdown(f"**在哪里找**：{friendly_loc}")
                                if guide:
                                    st.info(f"📍 {guide}")
                                st.markdown(f"**修改建议**：{e.fix_suggestion}")

                    if warn_items:
                        st.subheader(f"⚠️ 建议修复（{len(warn_items)} 条）")
                        for e in warn_items:
                            tag = _source_tag(e)
                            friendly_loc = get_friendly_location(e.rule_id, e.location)
                            guide = get_location_guide(e.rule_id)

                            with st.expander(f"{tag}  [{e.rule_id}] {e.message}"):
                                if guide:
                                    st.info(f"📍 {guide}")
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
                        st.warning(f"PDF生成失败：{pdf_err}，可下载Markdown版本")

                # Markdown备用下载
                with dl_col2:
                    from pim_optimizer.reporters.markdown_reporter import to_markdown
                    md_report = to_markdown(report)
                    st.download_button(
                        "📥 下载校验报告 (Markdown)",
                        md_report,
                        file_name=f"PiM校验报告_{pim_file.name.split('.')[0]}.md",
                        mime="text/markdown",
                    )

            except Exception as e:
                st.error(f"校验出错: {e}")
                st.exception(e)

    st.divider()
    st.caption("覆盖30+条规则：跨文件一致性 | PiM内部一致性 | 品牌标准 | 必填项 | 格式检查")


# ========== 管理页面 ==========
elif page == "⚙️ 规则管理":
    st.title("⚙️ 规则管理")

    # 密码验证
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        pwd = st.text_input("请输入管理密码", type="password")
        if st.button("登录"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("密码错误")
        st.stop()

    st.success("✅ 已登录")

    # 读取当前配置
    from pim_optimizer.config import BRAND

    st.subheader("品牌标准阈值")
    st.caption("修改后点击保存，下次校验生效（仅当前会话有效）")

    col1, col2 = st.columns(2)

    with col1:
        new_ns_ratio = st.slider(
            "无烟房最低比例",
            min_value=0.0, max_value=1.0,
            value=BRAND["min_non_smoking_ratio"],
            step=0.05,
            format="%.0f%%",
            help="品牌标准：无烟房≥总房量的此比例",
        )
        new_connecting = st.number_input(
            "连通房最少间数",
            min_value=0, max_value=10,
            value=BRAND["min_connecting_rooms"],
            help="品牌标准：连通房≥此数量",
        )
        new_accessible = st.number_input(
            "无障碍房最少间数",
            min_value=0, max_value=10,
            value=BRAND["min_accessible_rooms"],
        )

    with col2:
        new_max_occ = st.number_input(
            "默认最大入住人数",
            min_value=1, max_value=6,
            value=BRAND["default_max_occupancy"],
        )
        new_loc_chars = st.number_input(
            "位置短描述最大字符数",
            min_value=20, max_value=100,
            value=BRAND["location_desc_max_chars"],
        )

    if st.button("保存配置", type="primary"):
        BRAND["min_non_smoking_ratio"] = new_ns_ratio
        BRAND["min_connecting_rooms"] = new_connecting
        BRAND["min_accessible_rooms"] = new_accessible
        BRAND["default_max_occupancy"] = new_max_occ
        BRAND["location_desc_max_chars"] = new_loc_chars
        st.success("✅ 配置已保存（当前会话生效）")

    st.divider()
    st.subheader("当前规则一览")
    st.markdown("""
    | 类别 | 规则数 | 说明 |
    |------|--------|------|
    | A 跨文件一致性 | 3条 | PiM与PMS房型代码、房量匹配 |
    | B 内部一致性 | 6条 | 无烟房/沙发/连通房等数据前后一致 |
    | C 品牌标准 | 7条 | 无烟≥30%、连通≥2、无障碍、SLS沙发床 |
    | D 必填项 | 9条 | 描述/ADR/电话/经纬度/安保/城市 |
    | E 格式检查 | 7条 | 面积整数、字符限制、经纬度格式 |
    """)
