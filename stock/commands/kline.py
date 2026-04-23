from __future__ import annotations

from dataclasses import dataclass

import click
import pandas as pd
from stockstats import wrap

from ..api.qq import fetch_kline_payload, get_query_code


@dataclass
class DayLineItem:
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    amount: float


def _is_a_stock(query_code: str) -> bool:
    return query_code.startswith(("sh", "sz", "bj"))


def _to_float(value: str | int | float, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_lines(raw_lines: list[list[str]]) -> list[DayLineItem]:
    parsed: list[DayLineItem] = []
    for item in raw_lines:
        if len(item) < 9:
            continue
        parsed.append(
            DayLineItem(
                date=str(item[0]).replace("-", ""),
                open=_to_float(item[1]),
                close=_to_float(item[2]),
                high=_to_float(item[3]),
                low=_to_float(item[4]),
                volume=_to_float(item[5]),
                amount=_to_float(item[8]),
            )
        )
    return parsed


def _build_stock_df(lines: list[DayLineItem]) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "close": [x.close for x in lines],
            "high": [x.high for x in lines],
            "low": [x.low for x in lines],
            "open": [x.open for x in lines],
            "volume": [x.volume for x in lines],
        }
    )
    return wrap(df)


def _get_factors(df: pd.DataFrame) -> dict:
    _ = df["close_5_ema"]
    _ = df["close_10_ema"]
    _ = df["close_20_ema"]
    _ = df["boll"]
    _ = df["boll_ub"]
    _ = df["boll_lb"]
    _ = df["rsi_6"]
    _ = df["rsi_12"]
    last = len(df) - 1
    return {
        "ema_5": round(float(df["close_5_ema"].iloc[last]), 2),
        "ema_10": round(float(df["close_10_ema"].iloc[last]), 2),
        "ema_20": round(float(df["close_20_ema"].iloc[last]), 2),
        "boll_up": round(float(df["boll_ub"].iloc[last]), 2),
        "boll_mid": round(float(df["boll"].iloc[last]), 2),
        "boll_low": round(float(df["boll_lb"].iloc[last]), 2),
        "rsi_6": round(float(df["rsi_6"].iloc[last]), 2),
        "rsi_12": round(float(df["rsi_12"].iloc[last]), 2),
    }


def get_kline_data(symbol: str, count: int = 45) -> dict:
    query_code = get_query_code(symbol)
    payload = fetch_kline_payload(query_code)
    symbol_data = payload.get("data", {}).get(query_code)
    if not isinstance(symbol_data, dict):
        raise click.ClickException("无效股票代码或暂无日K数据")
    raw_lines = symbol_data.get("qfqday") or symbol_data.get("day") or []
    if not isinstance(raw_lines, list) or not raw_lines:
        raise click.ClickException("暂无日K数据")
    lines = _parse_lines(raw_lines)
    if not lines:
        raise click.ClickException("暂无有效日K数据")
    df = _build_stock_df(lines)
    factors = _get_factors(df)
    market_index = 0 if _is_a_stock(query_code) else 1
    qt = symbol_data.get("qt", {}).get(query_code, [])
    sliced_lines = lines[-count:]
    return {
        "lines": [
            {
                "时间": int(item.date),
                "开盘价": item.open,
                "收盘价": item.close,
                "最高价": item.high,
                "最低价": item.low,
                "成交量": f"{round(item.volume)}手",
                "成交额": f"{item.amount}万",
            }
            for item in sliced_lines
        ],
        "now": {
            "name": qt[1] if len(qt) > 1 else query_code,
            "vr": qt[49 + market_index] if len(qt) > 49 + market_index else "",
            "price": qt[3] if len(qt) > 3 else "",
            "change_rate": qt[32] if len(qt) > 32 else "",
        },
        "factors": factors,
    }


def format_kline_markdown(data: dict) -> str:
    lines = data.get("lines", [])
    if not lines:
        raise click.ClickException("暂无日K数据")
    headers = list(lines[0].keys())
    csv_rows = [",".join(str(item[key]) for key in headers) for item in lines]
    factors = data["factors"]
    return "\n".join(
        [
            "## 日K线",
            "",
            "```csv",
            ",".join(headers),
            *csv_rows,
            "```",
            "",
            "**技术指标**",
            "",
            f"- EMA5: {factors['ema_5']}",
            f"- EMA10: {factors['ema_10']}",
            f"- EMA20: {factors['ema_20']}",
            f"- BOLL(20,2): UP:{factors['boll_up']}, MID:{factors['boll_mid']}, LOW:{factors['boll_low']}",
            f"- RSI(6): {factors['rsi_6']}",
            f"- RSI(12): {factors['rsi_12']}",
        ]
    )


@click.command(name="kline")
@click.argument("code")
@click.option("--count", default=45, show_default=True, type=click.IntRange(1, 90), help="输出最近N条日K")
def kline(code: str, count: int):
    """日K数据以及技术指标（EMA/BOLL/RSI）"""
    data = get_kline_data(code, count=count)
    click.echo(format_kline_markdown(data))
