from __future__ import annotations


def _to_float(value: str | int | float | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_circulating_value(value: str) -> float:
    s = str(value).replace(",", "").strip()
    multiplier = 1.0
    if s.endswith("亿"):
        s = s[:-1]
        multiplier = 1e8
    elif s.endswith("万"):
        s = s[:-1]
        multiplier = 1e4
    try:
        return float(s) * multiplier
    except (TypeError, ValueError):
        return 0.0


def _score_main_net_inflow_ratio(ratio: float) -> tuple[int, str]:
    if ratio > 0.3:
        return 12, f"主力净流入占比 {ratio:+.3f}%，大幅流入"
    if ratio > 0.2:
        return 10, f"主力净流入占比 {ratio:+.3f}%，显著流入"
    if ratio > 0.1:
        return 7, f"主力净流入占比 {ratio:+.3f}%，温和流入"
    if ratio > 0.01:
        return 4, f"主力净流入占比 {ratio:+.3f}%，微弱流入"
    if ratio >= -0.05:
        return 1, f"主力净流入占比 {ratio:+.3f}%，基本持平"
    return 0, f"主力净流入占比 {ratio:+.3f}%，主力流出⚠️"


def _score_super_big_structure(super_flow: float, big_flow: float) -> tuple[int, str]:
    super_positive = super_flow > 0
    big_positive = big_flow > 0
    if super_positive and big_positive:
        return 10, "超大单+大单双正，机构游资共振"
    if not super_positive and big_positive:
        return 6, "大单正/超大单负，游资强势接力"
    if super_positive and not big_positive:
        return 4, "超大单正/大单负，机构建仓游资分歧"
    return 0, "超大单+大单双负，主力全线撤退⚠️"


def _score_five_day_trend(day_list: list[dict], today_ratio: float) -> tuple[int, str]:
    if not day_list:
        return 0, "无近5日资金流向数据"
    net_inflows = []
    for item in day_list:
        if not isinstance(item, dict):
            continue
        net_inflows.append(_to_float(item.get("mainNetIn")))
    if not net_inflows:
        return 0, "无近5日资金流向数据"
    cumulative = sum(net_inflows)
    cumulative_positive = cumulative > 0
    recent_3 = net_inflows[-3:] if len(net_inflows) >= 3 else net_inflows
    consecutive_inflow = all(v > 0 for v in recent_3)
    today_positive = today_ratio > 0
    today_strong_positive = today_ratio > 0.1
    cumulative_wan = cumulative / 1e4
    if cumulative_positive and not today_positive:
        return 2, f"5日累计净流入，但今日转为净流出（累计: {cumulative_wan:.2f}万）"
    if cumulative_positive and consecutive_inflow:
        return 8, f"5日累计净流入，近3日连续流入（累计: {cumulative_wan:.2f}万）"
    if cumulative_positive and not consecutive_inflow:
        return 6, f"5日累计净流入，但有间歇流出（累计: {cumulative_wan:.2f}万）"
    if not cumulative_positive and today_strong_positive:
        return 4, f"5日累计净流出，但今日明显转正（占比: {today_ratio:+.3f}%）"
    return 0, f"5日累计净流出且今日继续流出（累计: {cumulative_wan:.2f}万）⚠️"


def evaluate_fundflow(fundflow_data: dict, quote_data: dict | None = None) -> dict:
    today = fundflow_data.get("today", {})
    five_day = fundflow_data.get("fiveDay", {})

    super_flow = _to_float(today.get("superFlow"))
    big_flow = _to_float(today.get("bigFlow"))
    main_net_in = _to_float(today.get("mainNetIn"))

    circulating_value = 0.0
    if quote_data:
        circulating_value = _parse_circulating_value(quote_data.get("circulating_value", "0"))

    if circulating_value > 0:
        main_ratio = main_net_in / circulating_value * 100
    else:
        main_ratio = 0.0

    s1_score, s1_desc = _score_main_net_inflow_ratio(main_ratio)
    s2_score, s2_desc = _score_super_big_structure(super_flow, big_flow)

    day_list = five_day.get("DayMainNetInList", [])
    if not isinstance(day_list, list):
        day_list = []
    s3_score, s3_desc = _score_five_day_trend(day_list, main_ratio)

    total = s1_score + s2_score + s3_score
    max_total = 30

    return {
        "dimensions": [
            {"name": "今日主力净流入量级", "weight": "12", "score": s1_score, "max": 12, "desc": s1_desc},
            {"name": "今日超大单/大单结构", "weight": "10", "score": s2_score, "max": 10, "desc": s2_desc},
            {"name": "近5日主力净流入趋势", "weight": "8", "score": s3_score, "max": 8, "desc": s3_desc},
        ],
        "total": total,
        "max": max_total,
    }


def format_fundflow_evaluation_markdown(eval_data: dict) -> str:
    dims = eval_data.get("dimensions", [])
    lines = []
    for d in dims:
        lines.append(f"{d['name']},{d['weight']},{d['score']},{d['desc']}")
    total = eval_data.get("total", 0)
    return "\n".join(
        [
            "### 维度一：资金流向评估（满分 30 分）",
            "",
            "```csv",
            "子项,满分,得分,说明",
            *lines,
            "```",
            "",
            f"总得分：{total}",
        ]
    )
