from __future__ import annotations

from datetime import datetime

import click

from ..api.baidu import fetch_latest_news_payload, normalize_symbol, to_baidu_market, to_simple_code


@click.command(name="news")
@click.argument("symbol")
def news(symbol: str):
    """个股最新资讯"""
    data = get_stock_latest_news(symbol)
    click.echo(format_news_markdown(data))


def get_stock_latest_news(symbol: str) -> dict:
    normalized = normalize_symbol(symbol)
    market = to_baidu_market(normalized)
    code = to_simple_code(normalized)
    if not market or not code:
        raise click.ClickException("无效股票代码或暂无资讯数据")
    payload = fetch_latest_news_payload(market, code)
    result = payload.get("Result")
    if not isinstance(result, list) or not result:
        return {"symbol": normalized, "news": []}
    item = result[0] if isinstance(result[0], dict) else {}
    tpl = item.get("TplData")
    tpl_data = tpl if isinstance(tpl, dict) else {}
    sentiment = tpl_data.get("aiSentimentXcxListInfo")
    sentiment_info = sentiment if isinstance(sentiment, dict) else {}
    news = sentiment_info.get("sentimentListInfo")
    if not isinstance(news, list):
        news = []
    return {"symbol": normalized, "news": news}


def format_news_markdown(news_data: dict) -> str:
    news_list = news_data["news"]
    if not news_list:
        return "暂无数据"
    lines: list[str] = []
    for item in news_list:
        if not isinstance(item, dict):
            continue
        abstract = str(item.get("abstract", "")).strip()
        if not abstract:
            continue
        lines.append(f"- [{_format_news_timestamp(str(item.get('publishTime', '')))}] {abstract}")
    if not lines:
        lines = ["暂无数据"]
    return "\n".join(lines)


def _format_news_timestamp(timestamp: str) -> str:
    try:
        dt = datetime.fromtimestamp(int(str(timestamp)))
        return dt.strftime("%Y%m%d %H:%M")
    except (TypeError, ValueError, OSError):
        return "未知时间"
