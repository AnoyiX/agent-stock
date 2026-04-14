from __future__ import annotations

import click

from ..api.baidu import fetch_chgdiagram_payload
from ..api.qq import get_stock_by_query

CODES = {
    'ab': [
        'sh000001',
        'sz399001',
        'sz399006',
        'sh000688',
        'sh000300',
        'sh000905',
        'sh000852',
        'bj899050',
    ],
    'us': [
        'us.DJI',
        'us.IXIC',
        'us.INX',
    ],
    'hk': [
        'r_hkHSI',
        'r_hkHSCEI',
        'r_hkHSTECH',
    ],
}


def format_quotes_markdown(quotes: list[dict]) -> str:
    lines = []
    for quote in quotes:
        lines.append(
            ",".join(
                [
                    quote["code"],
                    quote["name"],
                    quote["price"],
                    quote["change_rate"],
                    quote["previous_close"],
                    quote["open"],
                    quote["high"],
                    quote["low"],
                ]
            )
        )
    return "\n".join(
        [
            "## 指数",
            "",
            "```csv",
            "代码,名称,价格,涨跌幅,昨收价,开盘价,最高价,最低价",
            *lines,
            "```",
        ]
    )


def _format_status(status: str) -> str:
    if status == "up":
        return "上涨"
    if status == "same":
        return "平盘"
    if status == "down":
        return "下跌"
    return status


def get_chgdiagram_data(market: str) -> dict:
    payload = fetch_chgdiagram_payload(market)
    result = payload.get("Result") if isinstance(payload, dict) else {}
    chg = result.get("chgdiagram") if isinstance(result, dict) else {}
    ratio = chg.get("ratio") if isinstance(chg, dict) else {}
    diagram = chg.get("diagram") if isinstance(chg, dict) else []
    up = int(ratio.get("up", 0)) if isinstance(ratio, dict) else 0
    balance = int(ratio.get("balance", 0)) if isinstance(ratio, dict) else 0
    down = int(ratio.get("down", 0)) if isinstance(ratio, dict) else 0
    items: list[dict] = []
    if isinstance(diagram, list):
        for item in diagram:
            if not isinstance(item, dict):
                continue
            items.append(
                {
                    "status": str(item.get("status", "")),
                    "title": str(item.get("title", "")),
                    "count": int(item.get("count", 0) or 0),
                }
            )
    return {"ratio": {"up": up, "balance": balance, "down": down}, "diagram": items}


def format_chgdiagram_markdown(data: dict) -> str:
    ratio = data.get("ratio", {})
    diagram = data.get("diagram", [])
    lines = [
        f"{_format_status(str(item.get('status', '')))},{str(item.get('title', ''))},{int(item.get('count', 0))}"
        for item in diagram
        if isinstance(item, dict)
    ]
    return "\n".join(
        [
            "## 涨跌分布",
            "",
            f"上涨：{ratio.get('up', 0)}家，平盘：{ratio.get('balance', 0)}家，下跌：{ratio.get('down', 0)}家",
            "",
            "```csv",
            "状态,区间,数量",
            *lines,
            "```",
        ]
    )


@click.command(name="index")
@click.option(
    "--market",
    default="ab",
    show_default=True,
    type=click.Choice(["ab", "us", "hk"], case_sensitive=False),
    help="市场",
)
def index(market: str):
    """大盘指数行情"""
    market = market.lower()
    data = get_stock_by_query(','.join(CODES[market]))
    click.echo("# 大盘行情")
    click.echo("")
    click.echo(format_quotes_markdown(data))
    click.echo("")
    chgdiagram_data = get_chgdiagram_data(market)
    click.echo(format_chgdiagram_markdown(chgdiagram_data))
