"""使用统计记录与汇总"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

import pandas as pd
import requests
import streamlit as st

from .models import PiMData, ValidationReport

BASE_TOKEN = "OSk0b9sRiacceBsegercIehQn0e"
TABLE_ID = "tblRgkpBm5wEXNS1"


FIELDS = [
    "校验时间",
    "酒店名称",
    "Inncode",
    "PiM文件名",
    "PMS文件名",
    "房型数量",
    "错误数",
    "警告数",
    "是否通过",
    "错误规则",
]


def _get_tenant_token() -> str | None:
    app_id = st.secrets.get("LARK_APP_ID")
    app_secret = st.secrets.get("LARK_APP_SECRET")
    if not app_id or not app_secret:
        return None

    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=8,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(data.get("msg") or "获取飞书 tenant_access_token 失败")
    return data["tenant_access_token"]


def record_usage(pim: PiMData, report: ValidationReport) -> None:
    """写入一条校验使用记录。未配置 secrets 时静默跳过。"""
    token = _get_tenant_token()
    if not token:
        return

    rules = ",".join(sorted({e.rule_id for e in report.errors}))
    fields = {
        "校验时间": int(datetime.now().timestamp() * 1000),
        "酒店名称": pim.hotel_name_cn,
        "Inncode": pim.inncode,
        "PiM文件名": report.pim_file,
        "PMS文件名": report.pms_file,
        "房型数量": len(pim.room_types),
        "错误数": report.error_count,
        "警告数": report.warning_count,
        "是否通过": report.can_submit,
        "错误规则": rules,
    }

    resp = requests.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"fields": fields},
        timeout=8,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(data.get("msg") or "写入使用统计失败")


def fetch_usage_records() -> list[dict[str, Any]]:
    token = _get_tenant_token()
    if not token:
        return []

    records: list[dict[str, Any]] = []
    page_token = ""
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(data.get("msg") or "读取使用统计失败")
        payload = data.get("data", {})
        records.extend(item.get("fields", {}) for item in payload.get("items", []))
        if not payload.get("has_more"):
            break
        page_token = payload.get("page_token", "")
    return records


def build_usage_summary(records: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    rule_counter: Counter[str] = Counter()

    for fields in records:
        row = {name: fields.get(name) for name in FIELDS}
        rows.append(row)
        for rule_id in str(row.get("错误规则") or "").split(","):
            rule_id = rule_id.strip()
            if rule_id:
                rule_counter[rule_id] += 1

    df = pd.DataFrame(rows)
    if df.empty:
        return df, pd.DataFrame(), pd.DataFrame()

    df["校验日期"] = pd.to_datetime(df["校验时间"], unit="ms", errors="coerce").dt.date
    daily = df.groupby("校验日期", dropna=True).size().reset_index(name="校验次数")
    top_rules = pd.DataFrame(rule_counter.most_common(10), columns=["规则", "出现次数"])
    return df, daily, top_rules
