from __future__ import annotations

import click

from ..api.baidu import get_stock_with_prefix, test_a_code, test_hk_code
from ..api.qq import arr2obj, fetch_quote_json


def get_query_code(symbol: str) -> str:
    lower = symbol.lower()
    if lower.startswith("us"):
        return lower.split(".")[0]
    if test_a_code(lower):
        return get_stock_with_prefix(lower)
    if test_hk_code(lower):
        return f"hk{lower}"
    return lower


def get_stock_by_code(symbol: str) -> dict:
    query_code = get_query_code(symbol)
    payload = fetch_quote_json(query_code)
    arr = payload.get(query_code)
    if not isinstance(arr, list) or len(arr) < 2:
        raise click.ClickException("无效股票代码或暂无行情数据")
    return arr2obj(arr)


def format_quote_markdown(quote: dict) -> str:
    return "\n".join(
        [
            f"- 代码: {quote['code']}",
            f"- 名称: {quote['name']}",
            f"- 当前价格: {quote['price']}",
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


@click.command(name="quote")
@click.argument("symbol")
def quote(symbol: str):
    """个股实时行情"""
    data = get_stock_by_code(symbol)
    click.echo(format_quote_markdown(data))

