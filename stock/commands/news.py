from __future__ import annotations

from datetime import datetime, timedelta

import click

from ..api.qq import fetch_news_payload, normalize_symbol


@click.command(name="news")
@click.argument("symbol")
def news(symbol: str):
    """个股最新资讯"""
    data = get_stock_latest_news(symbol)
    click.echo(format_news_markdown(data))


def get_stock_latest_news(symbol: str) -> dict:
    normalized = normalize_symbol(symbol)
    if not normalized:
        raise click.ClickException("无效股票代码或暂无资讯数据")
    payload = fetch_news_payload(normalized)
    code = payload.get("code")
    if code != 0:
        raise click.ClickException(payload.get("msg", "资讯接口返回错误"))
    data = payload.get("data")
    if not isinstance(data, dict):
        return {"symbol": normalized, "news": []}
    news_list = data.get("data")
    if not isinstance(news_list, list):
        news_list = []
    return {"symbol": normalized, "news": news_list}


def format_news_markdown(news_data: dict) -> str:
    news_list = news_data["news"]
    if not news_list:
        return "##快讯\n\n暂无数据\n"
    cutoff = datetime.now() - timedelta(days=3)
    lines: list[str] = []
    for item in news_list:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        raw_time = str(item.get("time", ""))
        if not _is_within_two_days(raw_time, cutoff):
            continue
        lines.append(f"- [{_format_news_timestamp(raw_time)}] {title}")
    if not lines:
        lines = ["暂无数据"]
    return "\n".join(["## 快讯", "", "\n".join(lines)])


def _is_within_two_days(timestamp: str, cutoff: datetime) -> bool:
    if not timestamp:
        return False
    try:
        parts = timestamp.split(" ")
        if len(parts) >= 2:
            news_dt = datetime.strptime(parts[0], "%Y-%m-%d")
            return news_dt >= cutoff
        return False
    except (TypeError, ValueError, IndexError):
        return False


def _format_news_timestamp(timestamp: str) -> str:
    if not timestamp:
        return "未知时间"
    try:
        parts = timestamp.split(" ")
        if len(parts) >= 2:
            date_part = parts[0].replace("-", "")
            time_part = parts[1][:5]
            return f"{date_part} {time_part}"
        return timestamp
    except (TypeError, ValueError, IndexError):
        return "未知时间"
