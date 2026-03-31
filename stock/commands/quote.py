from __future__ import annotations

import click

from ..api.qq import get_query_code, get_stock_by_code, get_stock_by_query


def format_quote_markdown(quote: dict) -> str:
    return "\n".join(
        [
            "## 实时行情",
            "",
            f"- 代码: {quote['code']}",
            f"- 名称: {quote['name']}",
            f"- 价格: {quote['price']}",
            f"- 涨跌幅: {quote['change_rate']}",
            f"- 昨收价: {quote['previous_close']}",
            f"- 开盘价: {quote['open']}",
            f"- 最高价: {quote['high']}",
            f"- 最低价: {quote['low']}",
            f"- 总市值: {quote['market_value']}",
            f"- 流通市值: {quote['circulating_value']}",
            f"- 市盈率: {quote['pe']}",
            f"- 市净率: {quote['pb']}",
            f"- 成交量: {quote['volume']}",
            f"- 量比: {quote['vr']}",
            f"- 换手率: {quote['turnover_rate']}",
        ]
    )


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
                    quote["market_value"],
                    quote["circulating_value"],
                    quote["pe"],
                    quote["pb"],
                    quote["volume"],
                    quote["vr"],
                    quote["turnover_rate"],
                ]
            )
        )
    return "\n".join(
        [
            "```csv",
            "代码,名称,价格,涨跌幅,昨收价,开盘价,最高价,最低价,总市值,流通市值,市盈率,市净率,成交量,量比,换手率",
            *lines,
            "```",
        ]
    )


@click.command(name="quote")
@click.argument("symbol")
def quote(symbol: str):
    """个股实时行情（支持批量查询）"""
    if ',' in symbol:
        query = ','.join([get_query_code(s) for s in symbol.split(",")])
        data = get_stock_by_query(query)
        click.echo(format_quotes_markdown(data))
    else:
        data = get_stock_by_code(symbol)
        click.echo(format_quote_markdown(data))
