#!/usr/bin/env python3
"""基于酒店基础信息与欢朋规范，调用 Claude API 生成 PiM 描述文案。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import anthropic

MODEL = "claude-opus-4-6"

EXAMPLE_HOTEL_DESCRIPTION = """酒店位于武汉市东湖高新区关南工业园高新二路25号，距离光谷天地1.6公里，距离光谷广场5.9公里，武汉东站高铁站1.3公里，武汉站21公里。坐拥光谷高新商圈，毗邻光谷国际总部、光谷软件园，地理位置优越。距离武九北线站600米，交通便利。酒店设计现代感十足，拥有希尔顿欢朋明亮色的“HUB”大堂，集聚会、休闲、商务功能于一体，拥有温馨雅致的客房及套房、精英会议室、免费营养热早餐、洗衣房、健身房等配套设施齐全。我们坚持用细致入微的知己服务，使每位客人享受到高品质的快乐入住体验。无论您是繁忙的商务差旅人士还是自由独立的旅行者亦或是现代家庭旅行，希尔顿欢朋酒店都将是您旅居生活中理想的家。"""

SYSTEM_PROMPT = """你是希尔顿欢朋中国区 PiM 内容专家，负责辅助门店填写 APAC Pre-opening PiM Pack。

写作原则：
1. 品牌调性：现代、明快、友好、可靠，符合希尔顿欢朋商旅与休闲客群定位。
2. 酒店描述结构：位置交通 → 周边商圈/景点/办公区 → 酒店设计与设施 → 服务体验 → 适用客群。
3. 避免夸张、绝对化、医疗/疗效/违规宣传，不编造用户未提供的信息。
4. 中文自然流畅，可直接粘贴到 PiM；英文用酒店官网渠道可用表达。
5. 房型描述需符合字符限制：short_description ≤ 26字符；line1/line2/line3 各≤45字符；long_description ≤1000字符。
6. 如果信息不足，用更稳妥的通用表达，不要硬编距离、地标或设施。
"""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "hotel_description_cn": {"type": "string"},
        "hotel_description_en": {"type": "string"},
        "tagline_cn": {"type": "string"},
        "tagline_en": {"type": "string"},
        "room_descriptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "room_code": {"type": "string"},
                    "room_name_cn": {"type": "string"},
                    "room_name_en": {"type": "string"},
                    "short_description": {"type": "string"},
                    "line1": {"type": "string"},
                    "line2": {"type": "string"},
                    "line3": {"type": "string"},
                    "long_description_en": {"type": "string"},
                    "long_description_cn": {"type": "string"},
                },
                "required": ["room_code", "room_name_cn", "room_name_en", "short_description", "line1", "line2", "line3", "long_description_en", "long_description_cn"],
                "additionalProperties": False,
            },
        },
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["hotel_description_cn", "hotel_description_en", "tagline_cn", "tagline_en", "room_descriptions", "warnings"],
    "additionalProperties": False,
}

TEMPLATE = {
    "hotel_name_cn": "",
    "hotel_name_en": "",
    "city": "",
    "address": "",
    "nearby_transport": ["例如：距离某高铁站约X公里"],
    "nearby_business_or_attractions": ["例如：毗邻某商圈/园区/景区"],
    "hotel_facilities": ["HUB大堂", "免费热早餐", "健身房", "洗衣房", "会议室"],
    "design_or_local_features": ["例如：结合当地文化/亲子主题/江景等"],
    "target_guests": ["商务差旅", "休闲旅行", "家庭出游"],
    "room_types": [
        {
            "room_code": "CD",
            "room_name_cn": "舒适房-大床",
            "room_name_en": "King Guest Room",
            "room_size_sqm": "",
            "bed_size": "",
            "features": ["明亮舒适", "办公区域", "高速Wi-Fi"]
        }
    ]
}


def init_template(path: Path) -> None:
    path.write_text(json.dumps(TEMPLATE, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成信息填写模板: {path}")


def build_user_prompt(hotel_info: dict[str, Any]) -> str:
    return f"""请基于以下酒店基础信息，生成可用于 PiM 的酒店描述、tagline、房型描述。

优秀案例参考：
{EXAMPLE_HOTEL_DESCRIPTION}

酒店基础信息(JSON)：
{json.dumps(hotel_info, ensure_ascii=False, indent=2)}

输出要求：
- 必须返回JSON，字段严格符合schema。
- 酒店中文描述建议180-350字；英文描述语义对应但不必逐字直译。
- 不要编造未给出的距离、地标、设施。
- 房型 short_description/line1/line2/line3 必须优先使用英文，且遵守字符限制。
"""


def generate(input_path: Path, output_path: Path) -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("缺少 ANTHROPIC_API_KEY 环境变量。请先在终端设置后再运行。")

    hotel_info = json.loads(input_path.read_text(encoding="utf-8"))
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(hotel_info)}],
    )
    text = next((block.text for block in response.content if block.type == "text"), "")
    data = json.loads(text)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成PiM文案: {output_path}")
    if data.get("warnings"):
        print("\n注意事项：")
        for warning in data["warnings"]:
            print(f"- {warning}")


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 PiM 酒店/房型描述")
    parser.add_argument("--init-template", help="生成酒店信息JSON模板到指定路径")
    parser.add_argument("--input", help="酒店信息JSON路径")
    parser.add_argument("--out", default="pim_descriptions.json", help="输出JSON路径")
    args = parser.parse_args()

    if args.init_template:
        init_template(Path(args.init_template).expanduser())
        return
    if not args.input:
        parser.error("请提供 --input，或使用 --init-template 生成模板")
    generate(Path(args.input).expanduser(), Path(args.out).expanduser())


if __name__ == "__main__":
    main()
