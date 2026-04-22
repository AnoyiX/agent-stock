from __future__ import annotations

INDEX_CODES_AB = ['000001', '399001', '399006']


def _parse_zdf(value: str) -> float:
    s = value.replace('%', '').replace('+', '').strip()
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _parse_float_str(value: str) -> float:
    s = value.replace('+', '').strip()
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _sigmoid(x: float, center: float, steepness: float) -> float:
    exponent = -steepness * (x - center)
    if exponent > 500:
        return 0.0
    if exponent < -500:
        return 1.0
    return 1.0 / (1.0 + 2.718281828 ** exponent)


def _score_up_down_ratio(up_count: int, down_count: int, flat_count: int = 0) -> tuple[float, str]:
    total_active = up_count + down_count
    if total_active == 0:
        return 0.0, "无有效涨跌数据"
    if down_count == 0:
        ratio = float('inf') if up_count > 0 else 0.0
    else:
        ratio = up_count / down_count
    ratio_score = _sigmoid(ratio, center=1.0, steepness=2.0) * 10.0
    participation = (up_count + down_count) / (up_count + down_count + flat_count) if (up_count + down_count + flat_count) > 0 else 0.5  # noqa: E501
    participation_bonus = (participation - 0.5) * 2.0
    score = round(max(0.0, min(10.0, ratio_score + participation_bonus)), 1)
    if ratio > 3:
        label = "普涨格局"
    elif ratio > 2:
        label = "明显偏多"
    elif ratio > 1.5:
        label = "偏多但分化"
    elif ratio > 1:
        label = "多空均衡略偏多"
    elif ratio > 0.5:
        label = "偏空"
    else:
        label = "普跌格局"
    desc = f"涨跌比 {ratio:.2f}:1，{label}；参与率 {participation:.0%}"
    return score, desc


def _score_index_change(quotes: list[dict]) -> tuple[float, str]:
    index_zdf_values = []
    for q in quotes:
        if q.get("code", "") in INDEX_CODES_AB:
            index_zdf_values.append(_parse_zdf(q.get("change_rate", "0%")))
    if not index_zdf_values:
        return 0.0, "无核心指数数据"
    avg = sum(index_zdf_values) / len(index_zdf_values)
    avg_score = _sigmoid(avg, center=0.0, steepness=3.0) * 10.0
    same_sign_count = sum(1 for v in index_zdf_values if (v > 0 and avg > 0) or (v < 0 and avg < 0) or v == 0)
    consensus = same_sign_count / len(index_zdf_values)
    consensus_bonus = (consensus - 0.5) * 2.0
    score = round(max(0.0, min(10.0, avg_score + consensus_bonus)), 1)
    if consensus >= 1.0:
        consensus_label = "完全共识"
    elif consensus >= 0.67:
        consensus_label = "多数共识"
    else:
        consensus_label = "分化"
    desc = f"三大指数涨跌幅均值 {avg:+.2f}%，共识度 {consensus:.0%}（{consensus_label}）"
    return score, desc


def _score_volume_change(chgdiagram_data: dict, index_avg_change: float) -> tuple[float, str]:
    amount_change = chgdiagram_data.get("amount_change", 0)
    amount = chgdiagram_data.get("amount", 0)
    if amount == 0:
        pct = 0.0
    else:
        pct = amount_change / amount * 100
    is_up = index_avg_change > 0
    is_expanding = pct >= 0
    abs_pct = abs(pct)
    if is_up and is_expanding:
        base_score = 5.0 + min(abs_pct / 5.0, 5.0)
        label = f"放量 {abs_pct:.1f}% 且上涨"
        if abs_pct > 15:
            detail = "资金大幅涌入"
        elif abs_pct > 5:
            detail = "资金积极参与"
        else:
            detail = "温和放量"
    elif is_up and not is_expanding:
        base_score = 5.0 - min(abs_pct / 5.0, 4.0)
        label = f"缩量 {abs_pct:.1f}% 且上涨"
        if abs_pct > 15:
            detail = "严重缩量上涨，虚涨风险大"
        elif abs_pct > 5:
            detail = "跟风不足"
        else:
            detail = "温和缩量"
    elif not is_up and is_expanding:
        base_score = 5.0 - min(abs_pct / 5.0, 5.0)
        label = f"放量 {abs_pct:.1f}% 且下跌"
        if abs_pct > 15:
            detail = "恐慌性杀跌"
        elif abs_pct > 5:
            detail = "恐慌出逃初现"
        else:
            detail = "温和放量下跌"
    else:
        base_score = 3.0 + min(abs_pct / 10.0, 2.0)
        label = f"缩量 {abs_pct:.1f}% 且下跌"
        if abs_pct > 15:
            detail = "卖压减弱，可能接近底部"
        elif abs_pct > 5:
            detail = "卖压减弱但方向偏空"
        else:
            detail = "温和缩量下跌"
    score = round(max(0.0, min(10.0, base_score)), 1)
    desc = f"{label}——{detail}"
    return score, desc


def _score_sector_change(pt_data: dict) -> tuple[float, str]:
    items = pt_data.get("items", [])
    if not items:
        return 0.0, "无行业板块数据"
    zdf_values = [_parse_zdf(it.get("zdf", "0%")) for it in items]
    avg = sum(zdf_values) / len(zdf_values)
    avg_score = _sigmoid(avg, center=0.0, steepness=3.0) * 10.0
    up_sector_count = sum(1 for v in zdf_values if v > 0)
    breadth = up_sector_count / len(zdf_values)
    breadth_bonus = (breadth - 0.5) * 2.0
    top3_by_zdf = sorted(items, key=lambda x: _parse_zdf(x.get("zdf", "0%")), reverse=True)[:3]
    top3_names_zdf = [it.get("name", "") for it in top3_by_zdf]
    top3_by_flow = sorted(items, key=lambda x: _parse_float_str(x.get("zljlr", "0")), reverse=True)[:3]
    top3_names_flow = [it.get("name", "") for it in top3_by_flow]
    intersection = set(top3_names_zdf) & set(top3_names_flow)
    has_mainline = len(intersection) > 0
    mainline_names = list(intersection) if has_mainline else top3_names_zdf
    mainline_bonus = 1.0 if has_mainline else 0.0
    score = round(max(0.0, min(10.0, avg_score + breadth_bonus + mainline_bonus)), 1)
    if breadth >= 0.8:
        breadth_label = "普涨"
    elif breadth >= 0.6:
        breadth_label = "偏多"
    elif breadth >= 0.4:
        breadth_label = "分化"
    else:
        breadth_label = "偏空"
    mainline_info = f"，主线板块：{', '.join(mainline_names)}（+1分）" if has_mainline else f"，涨幅前3：{', '.join(top3_names_zdf)}"  # noqa: E501
    desc = f"行业板块涨跌幅均值 {avg:+.2f}%，上涨板块占比 {breadth:.0%}（{breadth_label}）{mainline_info}"
    return score, desc


def _score_limit_ratio(chgdiagram_data: dict, up_down_ratio_score: float) -> tuple[float, str, list[str]]:
    up_limit = chgdiagram_data.get("up_limit_count", 0)
    down_limit = chgdiagram_data.get("down_limit_count", 0)
    if down_limit == 0:
        ratio = float('inf') if up_limit > 0 else 0.0
    else:
        ratio = up_limit / down_limit
    base_score = _sigmoid(ratio, center=1.0, steepness=1.5) * 10.0
    notes: list[str] = []
    if up_limit >= 50:
        bonus = min(up_limit / 100.0, 1.5)
        base_score = min(base_score + bonus, 10.0)
        notes.append(f"涨停 {up_limit} 家 ≥ 50，情绪强势（+{bonus:.1f}分）")
    if down_limit >= 20:
        penalty = min(down_limit / 20.0, 2.0)
        base_score = max(base_score - penalty, 0.0)
        notes.append(f"跌停 {down_limit} 家 ≥ 20，恐慌加剧（-{penalty:.1f}分）")
    if up_limit < 20 and up_down_ratio_score >= 6:
        base_score = max(base_score - 1.0, 0.0)
        notes.append(f"涨停 {up_limit} 家 < 20 且涨跌比得分 ≥ 6，上涨分散无主线（-1分）")
    if down_limit < 10 and up_down_ratio_score <= 2:
        notes.append("阴跌无恐慌")
    score = round(max(0.0, min(10.0, base_score)), 1)
    desc = f"涨跌停比 {ratio:.2f}:1（涨停 {up_limit}，跌停 {down_limit}）"
    return score, desc, notes


def evaluate_market(quotes: list[dict], chgdiagram_data: dict, pt_data: dict) -> dict:
    up_down_score, up_down_desc = _score_up_down_ratio(
        chgdiagram_data.get("up_count", 0),
        chgdiagram_data.get("down_count", 0),
        chgdiagram_data.get("flat_count", 0),
    )
    index_score, index_desc = _score_index_change(quotes)
    index_avg = 0.0
    index_zdf_values = []
    for q in quotes:
        if q.get("code", "") in INDEX_CODES_AB:
            index_zdf_values.append(_parse_zdf(q.get("change_rate", "0%")))
    if index_zdf_values:
        index_avg = sum(index_zdf_values) / len(index_zdf_values)
    volume_score, volume_desc = _score_volume_change(chgdiagram_data, index_avg)
    sector_score, sector_desc = _score_sector_change(pt_data)
    limit_score, limit_desc, limit_notes = _score_limit_ratio(chgdiagram_data, up_down_score)
    total = round(
        up_down_score * 0.3
        + index_score * 0.2
        + volume_score * 0.2
        + sector_score * 0.2
        + limit_score * 0.1,
        1,
    )
    if total >= 8:
        status = "主升"
        action = "可积极操作，仓位上限 30%"
    elif total >= 6:
        status = "震荡偏强"
        action = "可谨慎操作，仓位上限 20%"
    elif total >= 4:
        status = "震荡偏弱"
        action = "仅低吸试探，仓位上限 10%"
    elif total >= 2:
        status = "退潮"
        action = "仅优先关注，仓位上限 5%"
    else:
        status = "冰点"
        action = "空仓观望，不开新仓"
    return {
        "dimensions": [
            {"name": "涨跌比", "weight": "30%", "score": up_down_score, "desc": up_down_desc},
            {"name": "行业板块", "weight": "20%", "score": sector_score, "desc": sector_desc},
            {"name": "成交量", "weight": "20%", "score": volume_score, "desc": volume_desc},
            {"name": "涨跌幅", "weight": "20%", "score": index_score, "desc": index_desc},
            {"name": "涨跌停比", "weight": "10%", "score": limit_score, "desc": limit_desc, "notes": limit_notes},
        ],
        "total": total,
        "status": status,
        "action": action,
    }


def format_evaluation_markdown(eval_data: dict) -> str:
    dims = eval_data.get("dimensions", [])
    lines = []
    for d in dims:
        notes = d.get("notes", [])
        note_str = ""
        if notes:
            note_str = "；" + "；".join(notes)
        lines.append(f"{d['name']},{d['weight']},{d['score']:.1f},{d['desc']}{note_str}")
    total = eval_data.get("total", 0)
    status = eval_data.get("status", "")
    action = eval_data.get("action", "")
    return "\n".join(
        [
            "## 综合评估",
            "",
            "```csv",
            "维度,权重,得分,说明",
            *lines,
            "```",
            "",
            f"- 总分：{total:.1f}",
            f"- 市场状态：{status}",
            f"- 建议：{action}",
        ]
    )