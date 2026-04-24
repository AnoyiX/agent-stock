from __future__ import annotations

import click

from ..api.qq import fetch_mline_payload, get_query_code


def _format_mline_time(raw: str) -> str:
    s = str(raw).replace("-", "")
    if len(s) == 12:
        return f"{s[:4]}{s[4:6]}{s[6:8]} {s[8:10]}:{s[10:12]}"
    if len(s) == 8:
        return f"{s[:4]}{s[4:6]}{s[6:8]}"
    return s


def _is_a_stock(query_code: str) -> bool:
    return query_code.startswith(("sh", "sz", "bj"))


def get_mline_data(symbol: str, count: int = 48) -> dict:
    query_code = get_query_code(symbol)
    if not _is_a_stock(query_code):
        raise click.ClickException("5分钟K线仅支持A股")
    payload = fetch_mline_payload(query_code, count=count)
    data_field = payload.get("data")
    if not isinstance(data_field, dict):
        raise click.ClickException("无效股票代码或暂无5分钟K线数据")
    symbol_data = data_field.get(query_code)
    if not isinstance(symbol_data, dict):
        raise click.ClickException("无效股票代码或暂无5分钟K线数据")
    raw_lines = symbol_data.get("m5") or []
    if not isinstance(raw_lines, list) or not raw_lines:
        raise click.ClickException("暂无5分钟K线数据")
    result = []
    for item in raw_lines:
        if len(item) < 6:
            continue
        open_p = float(item[1])
        close_p = float(item[2])
        high_p = float(item[3])
        low_p = float(item[4])
        volume = float(item[5])
        avg_price = (high_p + low_p) / 2
        result.append(
            {
                "时间": _format_mline_time(item[0]),
                "开盘": round(open_p, 2),
                "收盘": round(close_p, 2),
                "最高": round(high_p, 2),
                "最低": round(low_p, 2),
                "均价": round(avg_price, 2),
                "成交量": round(volume),
            }
        )
    if not result:
        raise click.ClickException("暂无5分钟K线数据")
    return {"lines": result}


def format_mline_markdown(data: dict) -> str:
    lines = data.get("lines", [])
    if not lines:
        raise click.ClickException("暂无5分钟K线数据")
    headers = list(lines[0].keys())
    csv_rows = [",".join(str(item[key]) for key in headers) for item in lines]
    return "\n".join(
        [
            "## 5分钟K线",
            "",
            "```csv",
            ",".join(headers),
            *csv_rows,
            "```",
        ]
    )


@click.command(name="mline")
@click.argument("code")
@click.option("--count", default=48, show_default=True, type=click.IntRange(1, 320), help="输出最近N条5分钟K线")
def mline(code: str, count: int):
    """5分钟K线数据"""
    data = get_mline_data(code, count=count)
    click.echo(format_mline_markdown(data))
