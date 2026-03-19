from __future__ import annotations

import click

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
            "```csv",
            "代码,名称,价格,涨跌幅,昨收价,开盘价,最高价,最低价",
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
    data = get_stock_by_query(','.join(CODES[market.lower()]))
    click.echo(format_quotes_markdown(data))
