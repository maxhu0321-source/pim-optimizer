#!/usr/bin/env python3
"""PiM 优化工具 - 统一CLI入口"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_validate(args: argparse.Namespace) -> None:
    """执行校验"""
    from pim_optimizer.extractors.pim_extractor import extract_pim
    from pim_optimizer.extractors.pms_extractor import extract_pms
    from pim_optimizer.models import ValidationReport
    from pim_optimizer.reporters.json_reporter import write_json
    from pim_optimizer.reporters.markdown_reporter import to_markdown, write_markdown
    from pim_optimizer.validators.engine import run_all

    pim_path = Path(args.pim).expanduser()
    pms_path = Path(args.pms).expanduser() if args.pms else None

    print(f"读取 PiM: {pim_path.name}")
    pim_data = extract_pim(pim_path)
    print(f"  → 提取房型: {len(pim_data.room_types)} 个")

    pms_data = None
    if pms_path:
        print(f"读取 PMS: {pms_path.name}")
        pms_data = extract_pms(pms_path)
        print(f"  → 提取房型: {len(pms_data.room_types)} 个")

    print("\n执行校验规则...")
    errors = run_all(pim_data, pms_data)

    report = ValidationReport(
        pim_file=pim_path.name,
        pms_file=pms_path.name if pms_path else "",
        total_rooms_pim=len(pim_data.room_types),
        total_rooms_pms=len(pms_data.room_types) if pms_data else 0,
        errors=errors,
    )

    # 输出结果
    out_path = Path(args.out).expanduser()
    if out_path.suffix == ".json":
        write_json(report, out_path)
    else:
        write_markdown(report, out_path)

    # 终端摘要
    print(f"\n{'='*50}")
    status = "✅ 可以提交" if report.can_submit else "❌ 存在阻塞问题"
    print(f"结论: {status}")
    print(f"错误: {report.error_count} | 警告: {report.warning_count}")
    print(f"报告已输出: {out_path}")

    if errors:
        print(f"\n前10条问题:")
        for e in errors[:10]:
            icon = "🚨" if e.severity == "error" else "⚠️"
            print(f"  {icon} [{e.rule_id}] {e.message}")


def cmd_generate(args: argparse.Namespace) -> None:
    """AI生成描述"""
    # 复用现有 pim_ai_descriptions.py 逻辑
    sys.path.insert(0, str(Path(__file__).parent))
    from pim_ai_descriptions import generate, init_template

    if args.init_template:
        init_template(Path(args.init_template).expanduser())
        return
    if not args.input:
        print("错误: 请提供 --input，或使用 --init-template 生成模板")
        sys.exit(1)
    generate(Path(args.input).expanduser(), Path(args.out).expanduser())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PiM 优化工具 - 校验 & AI生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 校验 PiM + PMS 一致性
  python cli.py validate --pim apac.xlsb --pms pms.xlsx --out report.md

  # 仅校验 PiM 内部（无需PMS）
  python cli.py validate --pim apac.xlsb --out report.json

  # AI生成酒店描述
  python cli.py generate --init-template hotel_info.json
  python cli.py generate --input hotel_info.json --out descriptions.json
""",
    )
    subparsers = parser.add_subparsers(dest="command")

    # validate 子命令
    p_val = subparsers.add_parser("validate", help="校验 PiM/PMS 文件")
    p_val.add_argument("--pim", required=True, help="APAC PiM Pack xlsb 文件路径")
    p_val.add_argument("--pms", help="PMS 标准代码表 xlsx 文件路径（可选）")
    p_val.add_argument("--out", default="pim_report.md", help="输出报告路径(.md或.json)")

    # generate 子命令
    p_gen = subparsers.add_parser("generate", help="AI生成PiM描述")
    p_gen.add_argument("--init-template", help="生成酒店信息JSON模板")
    p_gen.add_argument("--input", help="酒店信息JSON路径")
    p_gen.add_argument("--out", default="pim_descriptions.json", help="输出路径")

    args = parser.parse_args()
    if args.command == "validate":
        cmd_validate(args)
    elif args.command == "generate":
        cmd_generate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
