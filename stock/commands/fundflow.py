from __future__ import annotations

from datetime import datetime

import click

from ..api.baidu import fetch_fundflow_day_payload, fetch_fundflow_spread_payload, to_baidu_market, to_simple_code
from ..api.qq import get_stock_with_prefix, is_a_code, is_hk_code


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


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _safe_get(d: dict, key: str, default: object = "") -> object:
    v = d.get(key)
    return v if v is not None else default


def get_fundflow_data(symbol: str) -> dict:
    normalized = _normalize_symbol(symbol)
    market = to_baidu_market(normalized)
    code = to_simple_code(normalized)
    if not market or not code:
        raise click.ClickException("无效股票代码或暂无资金流向数据")
    date = datetime.now().strftime("%Y%m%d")
    day_payload = fetch_fundflow_day_payload(market, code, date)
    day_result = {}
    result_obj = day_payload.get("Result") if isinstance(day_payload, dict) else {}
    content = result_obj.get("content") if isinstance(result_obj, dict) else {}
    fund_flow_day = content.get("fundFlowDay") if isinstance(content, dict) else {}
    unit = fund_flow_day.get("unit") if isinstance(fund_flow_day, dict) else ""
    ff_day_result = fund_flow_day.get("result") if isinstance(fund_flow_day, dict) else {}
    close_px = ff_day_result.get("closePx") if isinstance(ff_day_result, dict) else []
    main_arr = ff_day_result.get("main") if isinstance(ff_day_result, dict) else []
    retail_arr = ff_day_result.get("retail") if isinstance(ff_day_result, dict) else []
    daily: list[dict] = []
    n = min(
        len(close_px) if isinstance(close_px, list) else 0,
        len(main_arr) if isinstance(main_arr, list) else 0,
        len(retail_arr) if isinstance(retail_arr, list) else 0,
    )
    for i in range(n):
        cp = close_px[i] if isinstance(close_px, list) else {}
        main_item = main_arr[i] if isinstance(main_arr, list) else {}
        retail_item = retail_arr[i] if isinstance(retail_arr, list) else {}
        date_str = str(_safe_get(cp if isinstance(cp, dict) else {}, "date", "")).replace("-", "")
        if not date_str:
            continue
        daily.append(
            {
                "date": int(date_str),
                "main": _to_float(
                    _safe_get(main_item if isinstance(main_item, dict) else {}, "netTurnover", 0.0)
                ),
                "retail": _to_float(
                    _safe_get(retail_item if isinstance(retail_item, dict) else {}, "netTurnover", 0.0)
                ),
            }
        )
    day_result = {"unit": unit, "daily": daily}
    spread_payload = fetch_fundflow_spread_payload(market, code)
    spread_obj = spread_payload.get("Result") if isinstance(spread_payload, dict) else {}
    spread_content = spread_obj.get("content") if isinstance(spread_obj, dict) else {}
    fund_flow_spread = spread_content.get("fundFlowSpread") if isinstance(spread_content, dict) else {}
    spread_result = fund_flow_spread.get("result") if isinstance(fund_flow_spread, dict) else {}
    analysis = ""
    if isinstance(spread_result, dict):
        analysis_obj = spread_result.get("analysis")
        analysis = str(_safe_get(analysis_obj if isinstance(analysis_obj, dict) else {}, "content", ""))
    rows = []
    if isinstance(spread_result, dict):
        mapping = [
            ("净特大单", spread_result.get("superGrp")),
            ("净大单", spread_result.get("largeGrp")),
            ("净中单", spread_result.get("mediumGrp")),
            ("净小单", spread_result.get("littleGrp")),
        ]
        for name, grp in mapping:
            grp_obj = grp if isinstance(grp, dict) else {}
            rows.append(
                {
                    "name": name,
                    "turnoverIn": _safe_get(grp_obj, "turnoverIn", 0),
                    "turnoverInRate": _safe_get(grp_obj, "turnoverInRate", ""),
                    "turnoverOut": _safe_get(grp_obj, "turnoverOut", 0),
                    "turnoverOutRate": _safe_get(grp_obj, "turnoverOutRate", ""),
                    "netTurnover": _safe_get(grp_obj, "netTurnover", 0),
                }
            )
    today_main = {}
    if isinstance(spread_result, dict):
        tm = spread_result.get("todayMainFlow")
        tm_obj = tm if isinstance(tm, dict) else {}
        today_main = {
            "mainIn": _safe_get(tm_obj, "mainIn", ""),
            "mainOut": _safe_get(tm_obj, "mainOut", ""),
            "mainNetIn": _safe_get(tm_obj, "mainNetIn", ""),
        }
    totals = {}
    if isinstance(spread_result, dict):
        totals = {
            "turnoverInTotal": _safe_get(spread_result, "turnoverInTotal", ""),
            "turnoverOutTotal": _safe_get(spread_result, "turnoverOutTotal", ""),
            "turnoverNetTotal": _safe_get(spread_result, "turnoverNetTotal", ""),
        }
    spread = {
        "unit": _safe_get(spread_result if isinstance(spread_result, dict) else {}, "unit", ""),
        "analysis": analysis,
        "rows": rows,
        "todayMain": today_main,
        "totals": totals,
    }
    return {"spread": spread, "day": day_result}


def format_fundflow_markdown(data: dict) -> str:
    spread = data.get("spread", {})
    day = data.get("day", {})
    rows = spread.get("rows", [])
    rows_lines = [
        f"{r['name']},{_to_float(r.get('turnoverIn'))},{r.get('turnoverInRate')},{_to_float(r.get('turnoverOut'))},{r.get('turnoverOutRate')},{_to_float(r.get('netTurnover'))}"
        for r in rows
        if isinstance(r, dict)
    ]
    today_main = spread.get("todayMain", {})
    totals = spread.get("totals", {})
    daily = day.get("daily", [])
    daily_lines = [
        f"{int(item.get('date'))},{_to_float(item.get('main'))},{_to_float(item.get('retail'))}"
        for item in daily
    ]
    parts: list[str] = []
    parts.extend(
        [
            "## 资金流向",
            "",
            f"### 资金分布(单位：{spread.get('unit', '')})",
            "",
            f"> {spread.get('analysis', '')}",
            "",
            "```csv",
            "类别,流入,流入占比,流出,流出占比,净流入",
            *rows_lines,
            "```",
            "",
            (
                f"- 主力流入：{today_main.get('mainIn', '')}，主力流出：{today_main.get('mainOut', '')}，"
                f"主力净流入：{today_main.get('mainNetIn', '')}"
            ),
            (
                f"- 整体流入：{totals.get('turnoverInTotal', '')}，整体流出：{totals.get('turnoverOutTotal', '')}，"
                f"整体净流入：{totals.get('turnoverNetTotal', '')}"
            ),
        ]
    )
    parts.extend(
        [
            "",
            f"### 每日资金流向(单位：{day.get('unit', '')})",
            "",
            "```csv",
            "日期,主力净流入,散户净流入",
            *daily_lines,
            "```",
        ]
    )
    return "\n".join(parts)


@click.command(name="fundflow")
@click.argument("symbol")
def fundflow(symbol: str):
    """资金分布与每日主力/散户净流向"""
    data = get_fundflow_data(symbol)
    click.echo(format_fundflow_markdown(data))
