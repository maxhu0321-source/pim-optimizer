"""校验规则引擎 - 注册与执行"""

from __future__ import annotations

from typing import Callable

from ..models import PiMData, PMSData, ValidationError

# 规则注册表
_rules: list[Callable] = []


def rule(rule_id: str, category: str, severity: str):
    """装饰器：注册一条校验规则"""
    def decorator(fn: Callable):
        fn.rule_id = rule_id
        fn.category = category
        fn.severity = severity
        _rules.append(fn)
        return fn
    return decorator


def run_all(pim: PiMData, pms: PMSData | None = None) -> list[ValidationError]:
    """执行所有已注册规则，返回错误列表"""
    # 确保规则模块已导入（触发装饰器注册）
    from . import rules_brand, rules_completeness, rules_cross_file, rules_format, rules_internal  # noqa: F401

    errors: list[ValidationError] = []
    for rule_fn in _rules:
        try:
            results = rule_fn(pim, pms)
            if results:
                errors.extend(results)
        except Exception as e:
            errors.append(ValidationError(
                rule_id=rule_fn.rule_id,
                severity="warning",
                category=rule_fn.category,
                message=f"规则执行异常: {e}",
                location="",
                fix_suggestion="请联系工具维护人员",
            ))
    return errors
