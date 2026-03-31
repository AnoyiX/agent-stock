from __future__ import annotations

import click

from ..api.baidu import get_stock_with_prefix, is_a_code, is_hk_code
from ..api.qq import fetch_fundflow_payload


def _normalize_symbol(symbol: str) -> str:
    lower = symbol.lower()
    if lower.startswith("us."):
        parts = lower.split(".", 1)
        if len(parts) > 1 and parts[1]:
            return f"us{parts[1]}"
    if is_a_code(lower):
        return get_stock_with_prefix(lower)
    if is_hk_code(lower):
        return f"hk{lower}"
    return lower


def _to_wan(value: str | float, default: str = "") -> str:
    try:
        v = float(value)
        if abs(v) >= 10000:
            return f"{v / 10000:.2f}万"
        return f"{v:.2f}"
    except (TypeError, ValueError):
        return default if default else str(value)


def _safe_get(d: dict, key: str, default: object = "") -> object:
    v = d.get(key)
    return v if v is not None else default


def get_fundflow_data(symbol: str) -> dict:
    normalized = _normalize_symbol(symbol)
    code = normalized
    payload = fetch_fundflow_payload(code)
    if payload.get("code") != 0:
        raise click.ClickException(f"获取资金流向数据失败: {payload.get('msg', '未知错误')}")
    data = payload.get("data", {})
    today_fund_flow = data.get("todayFundFlow") or {}
    five_day_fund_flow = data.get("fiveDayFundFlow") or {}
    return {
        "today": today_fund_flow,
        "fiveDay": five_day_fund_flow,
        "prec": data.get("prec", "2"),
    }


def format_fundflow_markdown(data: dict) -> str:
    today = data.get("today", {})
    five_day = data.get("fiveDay", {})
    summary = today.get("summary", {})
    parts: list[str] = []

    parts.extend([
        "## 资金流向",
        "",
        "### 今日资金流向",
        "",
        f"> {_safe_get(summary, 's0', '')}",
        "",
        "```csv",
        "类别,流入,流入占比,流出,流出占比",
        f"主力,{_to_wan(_safe_get(today, 'mainIn'))},{_safe_get(today, 'mainInRate')}%," +
        f"{_to_wan(_safe_get(today, 'mainOut'))},{_safe_get(today, 'mainOutRate')}%",
        f"散户,{_to_wan(_safe_get(today, 'retailIn'))},{_safe_get(today, 'retailInRate')}%," +
        f"{_to_wan(_safe_get(today, 'retailOut'))},{_safe_get(today, 'retailOutRate')}%",
        "```",
        "",
        f"- 超大单净流入：{_to_wan(_safe_get(today, 'superFlow'))}",
        f"- 大单净流入：{_to_wan(_safe_get(today, 'bigFlow'))}",
        f"- 中单净流入：{_to_wan(_safe_get(today, 'normalFlow'))}",
        f"- 小单净流入：{_to_wan(_safe_get(today, 'smallFlow'))}",
        "",
        f"- 主力净流入：{_to_wan(_safe_get(today, 'mainNetIn'))}",
    ])

    day_list = five_day.get("DayMainNetInList", [])
    if day_list:
        parts.extend([
            "",
            "### 近5日主力净流入",
            "",
            "```csv",
            "日期,主力净流入",
        ])
        for item in day_list:
            if isinstance(item, dict):
                parts.append(f"{_safe_get(item, 'date')},{_to_wan(_safe_get(item, 'mainNetIn'))}")
        parts.append('```')

    return "\n".join(parts)


@click.command(name="fundflow")
@click.argument("symbol")
def fundflow(symbol: str):
    """资金分布与每日主力/散户净流向"""
    data = get_fundflow_data(symbol)
    click.echo(format_fundflow_markdown(data))
