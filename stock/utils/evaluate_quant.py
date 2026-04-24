from __future__ import annotations

from datetime import datetime, time


def _to_float(value: str | int | float | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_zdf(value: str | int | float | None) -> float:
    if value is None:
        return 0.0
    s = str(value).replace("%", "").replace("+", "").strip()
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


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


def _score_industry_zdf(industry_plates: list[dict]) -> tuple[int, str]:
    if not industry_plates:
        return 0, "无行业板块数据"
    best_zdf = max(_parse_zdf(p.get("zdf", "0")) for p in industry_plates)
    best_name = ""
    for p in industry_plates:
        if _parse_zdf(p.get("zdf", "0")) == best_zdf:
            best_name = p.get("name", "未知")
            break
    if best_zdf > 3:
        return 6, f"最强行业 {best_name} 涨幅 {best_zdf:+.2f}%，大幅领涨"
    if best_zdf > 2:
        return 5, f"最强行业 {best_name} 涨幅 {best_zdf:+.2f}%，显著领涨"
    if best_zdf > 1:
        return 3, f"最强行业 {best_name} 涨幅 {best_zdf:+.2f}%，温和领涨"
    if best_zdf > 0.5:
        return 2, f"最强行业 {best_name} 涨幅 {best_zdf:+.2f}%，微弱领涨"
    if best_zdf > 0:
        return 1, f"最强行业 {best_name} 涨幅 {best_zdf:+.2f}%，基本持平偏多"
    return 0, f"最强行业 {best_name} 涨幅 {best_zdf:+.2f}%，行业下跌⚠️"


def _score_is_mainline(industry_plates: list[dict], mline_industries: list[str]) -> tuple[int, str]:
    if not industry_plates:
        return 0, "无行业板块数据"
    sorted_by_zdf = sorted(industry_plates, key=lambda p: _parse_zdf(p.get("zdf", "0")), reverse=True)
    stock_industry_names = [p.get("name", "") for p in sorted_by_zdf]
    best_zdf = _parse_zdf(sorted_by_zdf[0].get("zdf", "0")) if sorted_by_zdf else 0.0

    is_mainline = any(name in mline_industries for name in stock_industry_names)

    if is_mainline:
        rank = None
        for idx, name in enumerate(mline_industries):
            if name in stock_industry_names:
                rank = idx + 1
                break
        if rank is not None and rank <= 3:
            return 7, f"所属行业为主线板块，涨幅排名前{rank}"
        if rank is not None and rank <= 5:
            return 5, f"所属行业为主线板块，涨幅排名前{rank}"
        return 5, "所属行业为主线板块"

    if best_zdf > 1:
        return 5, f"非主线行业，综合涨幅 {best_zdf:+.2f}% > 1%"
    if best_zdf > 0:
        return 2, f"非主线行业，综合涨幅 {best_zdf:+.2f}% > 0%"
    return 0, f"非主线行业，综合涨幅 {best_zdf:+.2f}% < 0%⚠️"


def _score_concept_resonance(concept_plates: list[dict]) -> tuple[int, str]:
    if not concept_plates:
        return 0, "无概念板块数据"
    total_count = len(concept_plates)
    resonant_count = sum(1 for p in concept_plates if _parse_zdf(p.get("zdf", "0")) > 0.2)
    ratio = resonant_count / total_count if total_count > 0 else 0.0
    resonant_names = [p.get("name", "") for p in concept_plates if _parse_zdf(p.get("zdf", "0")) > 0.2]

    if ratio >= 0.4:
        resonant_str = ', '.join(resonant_names[:5])
        return 7, f"概念共振占比 {ratio:.0%}（{resonant_count}/{total_count}），强共振: {resonant_str}"
    if ratio >= 0.25:
        resonant_str = ', '.join(resonant_names[:5])
        return 5, f"概念共振占比 {ratio:.0%}（{resonant_count}/{total_count}），中等共振: {resonant_str}"
    if ratio >= 0.15:
        resonant_str = ', '.join(resonant_names[:3])
        return 3, f"概念共振占比 {ratio:.0%}（{resonant_count}/{total_count}），弱共振: {resonant_str}"
    if ratio >= 0.05:
        return 1, f"概念共振占比 {ratio:.0%}（{resonant_count}/{total_count}），极弱共振"
    return 0, f"概念共振占比 {ratio:.0%}（{resonant_count}/{total_count}），无共振⚠️"


def evaluate_plate_resonance(plate_data: dict, mline_industries: list[str] | None = None) -> dict:
    industry_plates = plate_data.get("industry", [])
    if not isinstance(industry_plates, list):
        industry_plates = []
    concept_plates = plate_data.get("concept", [])
    if not isinstance(concept_plates, list):
        concept_plates = []

    if mline_industries is None:
        mline_industries = []

    s1_score, s1_desc = _score_industry_zdf(industry_plates)
    s2_score, s2_desc = _score_is_mainline(industry_plates, mline_industries)
    s3_score, s3_desc = _score_concept_resonance(concept_plates)

    total = s1_score + s2_score + s3_score
    max_total = 20

    return {
        "dimensions": [
            {"name": "所属行业板块涨幅", "weight": "6", "score": s1_score, "max": 6, "desc": s1_desc},
            {"name": "是否当日主线", "weight": "7", "score": s2_score, "max": 7, "desc": s2_desc},
            {"name": "概念共振计数", "weight": "7", "score": s3_score, "max": 7, "desc": s3_desc},
        ],
        "total": total,
        "max": max_total,
    }


def _score_ema_trend(factors: dict) -> tuple[int, str]:
    ema5 = _to_float(factors.get("ema_5"))
    ema10 = _to_float(factors.get("ema_10"))
    ema20 = _to_float(factors.get("ema_20"))

    if ema20 == 0:
        return 1, "无有效EMA数据，方向不明"

    if ema5 > ema10 > ema20:
        spread_pct = (ema5 - ema20) / ema20 * 100
        if spread_pct > 1:
            return 5, f"多头排列 EMA5={ema5} > EMA10={ema10} > EMA20={ema20}，差值 {spread_pct:.1f}%"
        return 4, f"多头排列 EMA5={ema5} > EMA10={ema10} > EMA20={ema20}，差值较小"
    if ema5 > ema10 and ema10 <= ema20:
        return 2, f"弱多头 EMA5={ema5} > EMA10={ema10}，但 EMA10≤EMA20={ema20}"
    if abs(ema5 - ema10) / ema20 < 0.01 and abs(ema10 - ema20) / ema20 < 0.01:
        return 1, f"三线粘合 EMA5={ema5}, EMA10={ema10}, EMA20={ema20}，方向不明"
    if ema5 < ema10 < ema20:
        return 0, f"空头排列 EMA5={ema5} < EMA10={ema10} < EMA20={ema20}⚠️"
    return 1, f"方向不明 EMA5={ema5}, EMA10={ema10}, EMA20={ema20}"


def _score_boll_position(factors: dict, price: float) -> tuple[int, str]:
    boll_up = _to_float(factors.get("boll_up"))
    boll_mid = _to_float(factors.get("boll_mid"))
    boll_low = _to_float(factors.get("boll_low"))

    if boll_mid == 0:
        return 1, "无有效BOLL数据"

    if price > boll_up:
        return 2, f"价格 {price} > BOLL上轨 {boll_up}，突破上轨"
    if boll_mid < price <= boll_up:
        return 3, f"BOLL中轨 {boll_mid} < 价格 {price} ≤ 上轨 {boll_up}，强势区间"
    if boll_low < price < boll_mid:
        return 1, f"下轨 {boll_low} < 价格 {price} < 中轨 {boll_mid}，弱势区间"
    if price <= boll_low:
        return 0, f"价格 {price} ≤ BOLL下轨 {boll_low}，极度弱势⚠️"
    return 1, f"价格 {price} 在BOLL中轨附近"


def _score_rsi_momentum(factors: dict) -> tuple[int, str]:
    rsi6 = _to_float(factors.get("rsi_6"))
    rsi12 = _to_float(factors.get("rsi_12"))

    if rsi6 == 0 and rsi12 == 0:
        return 1, "无有效RSI数据"

    if rsi6 > rsi12 and 45 <= rsi6 <= 65:
        return 2, f"RSI6={rsi6:.1f} > RSI12={rsi12:.1f}，多动能健康（45-65区间）"
    if abs(rsi6 - rsi12) < 3 and 30 <= rsi6 <= 70:
        return 1, f"RSI6={rsi6:.1f} ≈ RSI12={rsi12:.1f}，动能中性（30-70区间）"
    if rsi6 > 75:
        return 0, f"RSI6={rsi6:.1f} > 75，超买风险⚠️"
    if rsi6 < 30:
        return 0, f"RSI6={rsi6:.1f} < 30，极度弱势⚠️"
    if rsi6 < rsi12:
        return 0, f"RSI6={rsi6:.1f} < RSI12={rsi12:.1f}，空头动能⚠️"
    return 1, f"RSI6={rsi6:.1f}，RSI12={rsi12:.1f}"


def evaluate_kline_structure(kline_data: dict, quote_data: dict | None = None) -> dict:
    factors = kline_data.get("factors", {})
    price = _to_float(quote_data.get("price")) if quote_data else 0.0
    if not factors and price == 0:
        return {
            "dimensions": [
                {"name": "EMA趋势排列", "weight": "5", "score": 0, "max": 5, "desc": "无技术指标数据"},
                {"name": "BOLL价格位置", "weight": "3", "score": 0, "max": 3, "desc": "无技术指标数据"},
                {"name": "RSI动能", "weight": "2", "score": 0, "max": 2, "desc": "无技术指标数据"},
            ],
            "total": 0,
            "max": 10,
        }

    if price == 0:
        now_data = kline_data.get("now", {})
        price = _to_float(now_data.get("price"))

    s1_score, s1_desc = _score_ema_trend(factors)
    s2_score, s2_desc = _score_boll_position(factors, price)
    s3_score, s3_desc = _score_rsi_momentum(factors)

    total = s1_score + s2_score + s3_score
    max_total = 10

    return {
        "dimensions": [
            {"name": "EMA趋势排列", "weight": "5", "score": s1_score, "max": 5, "desc": s1_desc},
            {"name": "BOLL价格位置", "weight": "3", "score": s2_score, "max": 3, "desc": s2_desc},
            {"name": "RSI动能", "weight": "2", "score": s3_score, "max": 2, "desc": s3_desc},
        ],
        "total": total,
        "max": max_total,
    }


def _score_open_and_trend(quote_data: dict) -> tuple[int, str]:
    if not quote_data:
        return 0, "无行情数据"

    open_p = _to_float(quote_data.get("open", "0"))
    prev_close = _to_float(quote_data.get("previous_close", "0"))
    price = _to_float(quote_data.get("price", "0"))
    high = _to_float(quote_data.get("high", "0"))
    low = _to_float(quote_data.get("low", "0"))

    if prev_close == 0:
        return 0, "无昨收价数据"

    open_change = (open_p - prev_close) / prev_close * 100

    if price == 0 or high == 0:
        return 0, "无当前价格数据"

    price_vs_high = (high - price) / (high - low) if high != low else 0.0
    price_vs_low = (price - low) / (high - low) if high != low else 0.0
    day_change = (price - prev_close) / prev_close * 100

    if 0 <= open_change <= 1 and day_change > 1 and price_vs_high < 0.1:
        return 8, f"平开/小高开 {open_change:+.2f}% 后稳步走强，现价接近最高价"
    if open_change > 1 and day_change > 1 and price_vs_high < 0.2:
        return 7, f"高开 {open_change:+.2f}% 后继续走强，无明显冲高回落"
    if open_change < 0 and day_change > 0 and price_vs_low < 0.3:
        return 7, f"低开 {open_change:+.2f}% 后快速拉升收复，整体走势偏强"
    if abs(open_change) <= 0.5 and abs(day_change) <= 1:
        return 4, f"平开后震荡，涨跌幅 {day_change:+.2f}%，无明显方向"
    if open_change > 1 and price_vs_high > 0.5 and day_change < open_change * 0.5:
        return 2, f"高开 {open_change:+.2f}% 后冲高回落，现价回落至开盘附近"
    if day_change < -1 and price_vs_low < 0.1:
        return 0, f"开盘后持续走弱，涨跌幅 {day_change:+.2f}%，现价接近最低价⚠️"
    if day_change > 0 and price_vs_low < 0.3:
        return 5, f"开盘涨跌幅 {open_change:+.2f}%，全天涨 {day_change:+.2f}%，走势偏强"
    if day_change < 0:
        return 1, f"开盘涨跌幅 {open_change:+.2f}%，全天跌 {day_change:+.2f}%，走势偏弱"
    return 3, f"开盘涨跌幅 {open_change:+.2f}%，全天涨跌幅 {day_change:+.2f}%，方向不明"


def _score_avg_price_position(mline_data: dict) -> tuple[int, str]:
    lines = mline_data.get("lines", [])
    if not lines:
        return 0, "无5分钟K线数据"

    total_volume = 0.0
    weighted_price_sum = 0.0
    for item in lines:
        vol = _to_float(item.get("成交量", 0))
        avg_p = _to_float(item.get("均价", 0))
        total_volume += vol
        weighted_price_sum += avg_p * vol

    if total_volume == 0:
        avg_price = 0.0
        for item in lines:
            avg_price += _to_float(item.get("均价", 0))
        avg_price = avg_price / len(lines) if lines else 0.0
    else:
        avg_price = weighted_price_sum / total_volume

    if avg_price == 0:
        return 0, "无法计算均价线"

    above_count = 0
    valid_count = 0
    for item in lines:
        close_p = _to_float(item.get("收盘", 0))
        if close_p == 0:
            avg_p = _to_float(item.get("均价", 0))
            low_p = _to_float(item.get("最低", 0))
            close_p = (avg_p + low_p) / 2 if avg_p > 0 and low_p > 0 else 0
        if close_p > 0:
            valid_count += 1
            if close_p > avg_price:
                above_count += 1

    if valid_count == 0:
        return 0, "无有效价格数据"

    ratio = above_count / valid_count

    if ratio > 0.9:
        return 9, f"均价线上方时间占比 {ratio:.0%}（{above_count}/{valid_count}），强势运行"
    if ratio >= 0.6:
        return 7, f"均价线上方时间占比 {ratio:.0%}（{above_count}/{valid_count}），偏强运行"
    if ratio >= 0.4:
        return 4, f"均价线上方时间占比 {ratio:.0%}（{above_count}/{valid_count}），震荡运行"
    if ratio >= 0.3:
        return 1, f"均价线上方时间占比 {ratio:.0%}（{above_count}/{valid_count}），偏弱运行"
    if ratio < 0.3:
        return 0, f"均价线上方时间占比 {ratio:.0%}（{above_count}/{valid_count}），弱势运行⚠️"
    return 3, f"均价线上方时间占比 {ratio:.0%}（{above_count}/{valid_count}）"


def _score_late_session(mline_data: dict, quote_data: dict) -> tuple[int, str]:
    lines = mline_data.get("lines", [])
    if not lines:
        return 4, "无5分钟K线数据，尾盘待确认（暂给中间分4分）"

    now = datetime.now()
    if now.time() < time(14, 30):
        return 4, f"当前时间 {now.strftime('%H:%M')} 在14:30之前，尾盘待确认（暂给中间分4分）"

    late_lines = []
    for item in lines:
        t_str = str(item.get("时间", ""))
        if "14:" in t_str or "15:" in t_str:
            late_lines.append(item)

    if not late_lines:
        return 4, "无尾盘14:30-15:00数据，暂给中间分4分"

    all_volumes = [_to_float(item.get("成交量", 0)) for item in lines]
    avg_volume = sum(all_volumes) / len(all_volumes) if all_volumes else 0

    late_volumes = [_to_float(item.get("成交量", 0)) for item in late_lines]
    late_avg_volume = sum(late_volumes) / len(late_volumes) if late_volumes else 0

    prev_close = _to_float(quote_data.get("previous_close", "0")) if quote_data else 0
    day_high = _to_float(quote_data.get("high", "0")) if quote_data else 0
    day_low = _to_float(quote_data.get("low", "0")) if quote_data else 0

    first_late_close = _to_float(late_lines[0].get("收盘", 0)) if late_lines else 0
    last_late_close = _to_float(late_lines[-1].get("收盘", 0)) if late_lines else 0

    late_change_pct = 0.0
    if first_late_close > 0 and prev_close > 0:
        late_change_pct = (last_late_close - first_late_close) / first_late_close * 100

    is_volume_up = late_avg_volume > avg_volume
    is_new_high = last_late_close >= day_high * 0.99 if day_high > 0 else False

    if is_volume_up and is_new_high:
        return 8, f"尾盘放量拉升，量 > 日均量，价格接近日内新高 {last_late_close:.2f}"
    if late_change_pct > 0 and not is_volume_up:
        return 6, f"尾盘平稳略涨 {late_change_pct:+.2f}%，量正常"
    if abs(late_change_pct) <= 0.3 and not is_volume_up:
        return 4, f"尾盘缩量横盘，涨跌幅 {late_change_pct:+.2f}%，方向不明"
    if late_change_pct < 0 and last_late_close > day_low:
        return 2, f"尾盘小幅回落 {late_change_pct:+.2f}%，但未创日内新低"
    if late_change_pct < -1 and is_volume_up:
        return 0, f"尾盘跳水放量，14:30后下跌 {late_change_pct:+.2f}%⚠️"
    if late_change_pct < 0:
        return 1, f"尾盘回落 {late_change_pct:+.2f}%"
    return 4, f"尾盘涨跌幅 {late_change_pct:+.2f}%，方向不明"


def evaluate_mline_trend(mline_data: dict, quote_data: dict | None = None) -> dict:
    if not mline_data or not mline_data.get("lines"):
        return {
            "dimensions": [
                {"name": "开盘定性与全天趋势", "weight": "8", "score": 0, "max": 8, "desc": "无5分钟K线数据"},
                {"name": "价格与均价线位置", "weight": "9", "score": 0, "max": 9, "desc": "无5分钟K线数据"},
                {"name": "尾盘表现", "weight": "8", "score": 4, "max": 8, "desc": "无5分钟K线数据，暂给中间分4分"},
            ],
            "total": 4,
            "max": 25,
        }

    s1_score, s1_desc = _score_open_and_trend(quote_data or {})
    s2_score, s2_desc = _score_avg_price_position(mline_data)
    s3_score, s3_desc = _score_late_session(mline_data, quote_data or {})

    total = s1_score + s2_score + s3_score
    max_total = 25

    return {
        "dimensions": [
            {"name": "开盘定性与全天趋势", "weight": "8", "score": s1_score, "max": 8, "desc": s1_desc},
            {"name": "价格与均价线位置", "weight": "9", "score": s2_score, "max": 9, "desc": s2_desc},
            {"name": "尾盘表现", "weight": "8", "score": s3_score, "max": 8, "desc": s3_desc},
        ],
        "total": total,
        "max": max_total,
    }


def _check_veto_conditions(quote_data: dict) -> tuple[bool, str]:
    if not quote_data:
        return False, ""

    change_rate = _parse_zdf(quote_data.get("change_rate", "0%"))
    vr = _to_float(quote_data.get("vr", "0"))
    turnover_rate_str = str(quote_data.get("turnover_rate", "0%")).replace("%", "").strip()
    turnover_rate = _to_float(turnover_rate_str)
    circulating_value = _parse_circulating_value(quote_data.get("circulating_value", "0"))

    if vr > 5 and change_rate < 0:
        return True, f"一票否决：量比 {vr:.1f} > 5 且涨跌幅 {change_rate:+.2f}% < 0%，对倒嫌疑⚠️"

    threshold = 25 if circulating_value < 5e9 else 20
    if turnover_rate > threshold:
        cv_yi = circulating_value / 1e8
        return True, f"一票否决：换手率 {turnover_rate:.1f}% > {threshold}%（流通市值 {cv_yi:.0f}亿）⚠️"

    amount_str = str(quote_data.get("volume", "0")).replace("万手", "").strip()
    amount_val = _to_float(amount_str) * 1e4
    code = str(quote_data.get("code", ""))
    if (code.startswith("bj") or code.startswith("4") or code.startswith("8")) and amount_val < 5e4:
        return True, "一票否决：北交所/科创板成交额 < 5000万⚠️"

    return False, ""


def _score_valuation_risk(quote_data: dict) -> tuple[int, str]:
    if not quote_data:
        return 3, "无行情数据，默认3分"

    pe = _to_float(quote_data.get("pe", "0"))
    pb = _to_float(quote_data.get("pb", "0"))

    if pe <= 0:
        pe_score = 1
        pe_desc = f"PE={pe}（亏损或负值）"
    elif pe <= 30:
        pe_score = 5
        pe_desc = f"PE={pe:.1f}（0-30，低估值）"
    elif pe <= 60:
        pe_score = 4
        pe_desc = f"PE={pe:.1f}（30-60，中等估值）"
    elif pe <= 100:
        pe_score = 2
        pe_desc = f"PE={pe:.1f}（60-100，高估值）"
    else:
        pe_score = 1
        pe_desc = f"PE={pe:.1f}（>100，极高估值）"

    if pb <= 0:
        pb_score = 1
        pb_desc = f"PB={pb}（负值）"
    elif pb <= 3:
        pb_score = 5
        pb_desc = f"PB={pb:.2f}（0-3，低估值）"
    elif pb <= 6:
        pb_score = 4
        pb_desc = f"PB={pb:.2f}（3-6，中等估值）"
    elif pb <= 10:
        pb_score = 2
        pb_desc = f"PB={pb:.2f}（6-10，高估值）"
    else:
        pb_score = 1
        pb_desc = f"PB={pb:.2f}（>10，极高估值）"

    score = min(pe_score, pb_score)
    desc = f"{pe_desc}，{pb_desc}，取较低分 {score}"
    return score, desc


def _score_technical_abnormality(quote_data: dict, kline_data: dict) -> tuple[int, str]:
    initial_score = 5
    deductions: list[str] = []

    if not quote_data:
        return initial_score, "无行情数据，默认5分"

    change_rate = _parse_zdf(quote_data.get("change_rate", "0%"))
    vr = _to_float(quote_data.get("vr", "0"))
    high = _to_float(quote_data.get("high", "0"))
    low = _to_float(quote_data.get("low", "0"))
    price = _to_float(quote_data.get("price", "0"))

    factors = kline_data.get("factors", {})
    boll_up = _to_float(factors.get("boll_up"))

    amplitude = 0.0
    if low > 0:
        amplitude = (high - low) / low * 100

    if 2 <= vr < 5 and change_rate < 1:
        initial_score -= 1
        deductions.append(f"量比 {vr:.1f}（2-5）且涨幅 {change_rate:+.2f}% < 1%（疑似对倒）-1分")

    if amplitude > 5 and price < high - (high - low) * 0.5:
        initial_score -= 1
        deductions.append(f"振幅 {amplitude:.1f}% > 5% 且现价偏低位（长上影线）-1分")

    if price > boll_up and vr > 2 and change_rate < 1 and boll_up > 0:
        initial_score -= 2
        deductions.append(f"价格 > BOLL上轨 且量比 {vr:.1f} > 2 且涨幅 < 1%（高位量滞涨）-2分")

    if change_rate > 3 and vr < 0.8:
        initial_score -= 2
        deductions.append(f"涨幅 {change_rate:+.2f}% > 3% 但量比 {vr:.1f} < 0.8（缩量上涨）-2分")

    lines = kline_data.get("lines", [])
    if len(lines) >= 3:
        recent_3 = lines[-3:]
        long_upper_shadow_count = 0
        for item in recent_3:
            item_high = _to_float(item.get("最高价", 0))
            item_close = _to_float(item.get("收盘价", 0))
            item_low = _to_float(item.get("最低价", 0))
            if item_high - item_close > item_close - item_low and (item_high - item_close) / item_low * 100 > 2:
                long_upper_shadow_count += 1
        if long_upper_shadow_count >= 2:
            initial_score -= 2
            deductions.append(f"近3日有{long_upper_shadow_count}日长上影线 -2分")

    if len(lines) >= 3:
        recent_2 = lines[-2:]
        volume_increasing = True
        gain_decreasing = True
        prev_gain = None
        prev_vol = None
        for item in recent_2:
            vol = _to_float(item.get("成交量", "0").replace("手", ""))
            close = _to_float(item.get("收盘价", 0))
            open_p = _to_float(item.get("开盘价", 0))
            gain = close - open_p
            if prev_vol is not None and vol <= prev_vol:
                volume_increasing = False
            if prev_gain is not None and abs(gain) >= abs(prev_gain):
                gain_decreasing = False
            prev_vol = vol
            prev_gain = gain
        if volume_increasing and gain_decreasing:
            initial_score -= 2
            deductions.append("连续2日放量但涨幅递减（价量背离）-2分")

    score = max(0, initial_score)
    if deductions:
        desc = f"初始5分，扣分项：{'; '.join(deductions)}"
    else:
        desc = "无技术异常，满分5分"
    return score, desc





def evaluate_risk(
    quote_data: dict | None = None,
    kline_data: dict | None = None,
) -> dict:
    if not quote_data:
        return {
            "dimensions": [
                {"name": "估值风险", "weight": "5", "score": 0, "max": 5, "desc": "无行情数据"},
                {"name": "技术异常", "weight": "5", "score": 0, "max": 5, "desc": "无行情数据"},
            ],
            "total": 0,
            "max": 10,
            "veto": False,
            "veto_reason": "",
        }

    if kline_data is None:
        kline_data = {"factors": {}, "lines": []}

    is_veto, veto_reason = _check_veto_conditions(quote_data)

    if is_veto:
        return {
            "dimensions": [
                {"name": "估值风险", "weight": "5", "score": 0, "max": 5, "desc": "一票否决，本维度0分"},
                {"name": "技术异常", "weight": "5", "score": 0, "max": 5, "desc": "一票否决，本维度0分"},
            ],
            "total": 0,
            "max": 10,
            "veto": True,
            "veto_reason": veto_reason,
        }

    s1_score, s1_desc = _score_valuation_risk(quote_data)
    s2_score, s2_desc = _score_technical_abnormality(quote_data, kline_data)

    total = s1_score + s2_score
    max_total = 10

    return {
        "dimensions": [
            {"name": "估值风险", "weight": "5", "score": s1_score, "max": 5, "desc": s1_desc},
            {"name": "技术异常", "weight": "5", "score": s2_score, "max": 5, "desc": s2_desc},
        ],
        "total": total,
        "max": max_total,
        "veto": False,
        "veto_reason": "",
    }


def evaluate_stock(
    fundflow_data: dict | None = None,
    plate_data: dict | None = None,
    kline_data: dict | None = None,
    mline_data: dict | None = None,
    quote_data: dict | None = None,
    mline_industries: list[str] | None = None,
) -> dict:
    fundflow_eval = evaluate_fundflow(fundflow_data or {}, quote_data)
    mline_eval = evaluate_mline_trend(mline_data or {}, quote_data)
    plate_eval = evaluate_plate_resonance(plate_data or {}, mline_industries)
    kline_eval = evaluate_kline_structure(kline_data or {}, quote_data)
    risk_eval = evaluate_risk(quote_data, kline_data)

    raw_total = (
        fundflow_eval["total"]
        + mline_eval["total"]
        + plate_eval["total"]
        + kline_eval["total"]
        + risk_eval["total"]
    )
    if raw_total >= 76:
        grade = "A"
    elif raw_total >= 61:
        grade = "B"
    elif raw_total >= 47:
        grade = "C"
    else:
        grade = "D"

    return {
        "fundflow": fundflow_eval,
        "mline": mline_eval,
        "plate": plate_eval,
        "kline": kline_eval,
        "risk": risk_eval,
        "total": raw_total,
        "max_total": 100,
        "grade": grade,
        "veto": risk_eval.get("veto", False),
        "veto_reason": risk_eval.get("veto_reason", ""),
    }


def format_dimension_markdown(title: str, eval_data: dict) -> str:
    dims = eval_data.get("dimensions", [])
    lines = []
    for d in dims:
        lines.append(f"{d['name']},{d['weight']},{d['score']},{d['desc']}")
    total = eval_data.get("total", 0)
    max_score = eval_data.get("max", 0)
    return "\n".join(
        [
            f"### {title}（满分 {max_score} 分）",
            "",
            "```csv",
            "子项,满分,得分,说明",
            *lines,
            "```",
            "",
            f"总得分：{total}/{max_score}",
        ]
    )


def format_stock_evaluation_markdown(stock_eval: dict) -> str:
    veto = stock_eval.get("veto", False)
    veto_reason = stock_eval.get("veto_reason", "")
    parts: list[str] = []

    if veto:
        parts.append(f"⚠️ **一票否决**：{veto_reason}")
        parts.append("")

    parts.append(format_dimension_markdown("维度一：资金流向评估", stock_eval["fundflow"]))
    parts.append("")
    parts.append(format_dimension_markdown("维度二：分时走势评估", stock_eval["mline"]))
    parts.append("")
    parts.append(format_dimension_markdown("维度三：板块共振评估", stock_eval["plate"]))
    parts.append("")
    parts.append(format_dimension_markdown("维度四：日K结构评估", stock_eval["kline"]))
    parts.append("")
    parts.append(format_dimension_markdown("维度五：风险排查评估", stock_eval["risk"]))
    parts.append("")

    total = stock_eval.get("total", 0)
    grade = stock_eval.get("grade", "D")

    parts.append("## 综合评分")
    parts.append("")
    parts.append(f"- 总分：{total}/100")
    parts.append(f"- 评级：{grade}")

    if veto:
        parts.append("")
        parts.append("⚠️ **禁止一切买入操作**")

    return "\n".join(parts)


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