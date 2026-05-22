#!/usr/bin/env python3
"""PiM 校验工具 - Web界面 (Streamlit)"""

import streamlit as st
import tempfile
from pathlib import Path

st.set_page_config(page_title="PiM 校验工具", page_icon="🏨", layout="wide")

st.title("🏨 PiM Pack 校验工具")
st.caption("上传 PiM Pack (.xlsb) 和 PMS标准代码表 (.xlsx)，自动检测常见错误")

col1, col2 = st.columns(2)

with col1:
    pim_file = st.file_uploader("上传 PiM Pack (.xlsb)", type=["xlsb", "xlsm", "xls"])

with col2:
    pms_file = st.file_uploader("上传 PMS标准代码表 (.xlsx)", type=["xlsx"])

# 单文件提醒
if pim_file and not pms_file:
    st.warning("⚠️ 未上传PMS代码表，将无法进行跨文件房型一致性校验。建议同时上传两个文件。")

if st.button("开始校验", type="primary", disabled=not pim_file):
    with st.spinner("校验中..."):
        # 保存上传文件到临时目录
        tmp_dir = tempfile.mkdtemp()
        pim_path = Path(tmp_dir) / pim_file.name
        pim_path.write_bytes(pim_file.read())

        pms_path = None
        if pms_file:
            pms_path = Path(tmp_dir) / pms_file.name
            pms_path.write_bytes(pms_file.read())

        # 执行校验
        from pim_optimizer.extractors.pim_extractor import extract_pim
        from pim_optimizer.extractors.pms_extractor import extract_pms
        from pim_optimizer.models import ValidationReport
        from pim_optimizer.reporters.markdown_reporter import to_markdown
        from pim_optimizer.validators.engine import run_all

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

            # 显示结果
            if report.can_submit:
                st.success(f"✅ 可以提交！（{report.warning_count} 条建议）")
            else:
                st.error(f"❌ 存在 {report.error_count} 条阻塞问题")

            # 指标卡片
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("PiM房型数", report.total_rooms_pim)
            m2.metric("PMS房型数", report.total_rooms_pms if pms_file else "-")
            m3.metric("错误", report.error_count)
            m4.metric("警告", report.warning_count)

            # ========== 房型明细对照表 ==========
            st.divider()
            st.subheader("📋 房型明细")

            if pms_data:
                # 双表对照
                import pandas as pd

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

                    # 匹配状态
                    if pim_rt and pms_rt:
                        if pim_rt.count == pms_rt.count:
                            status = "✅ 一致"
                        else:
                            status = "❌ 房量不一致"
                    elif pim_rt and not pms_rt:
                        status = "⚠️ PMS缺失"
                    else:
                        status = "⚠️ PiM缺失"

                    rows_data.append({
                        "房型代码": code,
                        "中文名": name,
                        "PiM房量": pim_count,
                        "PMS房量": pms_count,
                        "状态": status,
                    })

                df = pd.DataFrame(rows_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                # 单表
                import pandas as pd
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

            # ========== 错误详情（标注归属方）==========
            if errors:
                st.divider()
                error_items = [e for e in errors if e.severity == "error"]
                warn_items = [e for e in errors if e.severity == "warning"]

                def _get_source_tag(error):
                    """判断错误归属方"""
                    loc = error.location.upper()
                    if "PMS" in loc:
                        return "🔵 PMS"
                    elif "PIM" in loc or "PiM" in error.location:
                        return "🟠 PiM"
                    # 根据类别推断
                    if error.category == "cross_file":
                        return "🔴 两表"
                    return "🟠 PiM"

                if error_items:
                    st.subheader("🚨 必须修复")
                    for e in error_items:
                        tag = _get_source_tag(e)
                        with st.expander(f"{tag} [{e.rule_id}] {e.message}"):
                            st.write(f"**归属**: {tag}")
                            st.write(f"**位置**: {e.location}")
                            st.write(f"**建议**: {e.fix_suggestion}")

                if warn_items:
                    st.subheader("⚠️ 建议修复")
                    for e in warn_items:
                        tag = _get_source_tag(e)
                        with st.expander(f"{tag} [{e.rule_id}] {e.message}"):
                            st.write(f"**建议**: {e.fix_suggestion}")

            # 下载完整报告
            st.divider()
            md_report = to_markdown(report)
            st.download_button(
                "📥 下载完整报告 (Markdown)",
                md_report,
                file_name=f"pim_report_{pim_file.name.split('.')[0]}.md",
                mime="text/markdown",
            )

        except Exception as e:
            st.error(f"校验出错: {e}")
            st.exception(e)

st.divider()
st.caption("覆盖规则：跨文件一致性 | 内部一致性 | 品牌标准 | 必填项 | 格式检查")
