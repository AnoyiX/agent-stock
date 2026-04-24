from __future__ import annotations

import click

from ..utils.evaluate_quant import (
    evaluate_stock,
    format_stock_evaluation_markdown,
)
from .fundflow import get_fundflow_data
from .kline import format_kline_markdown, get_kline_data
from .mline import get_mline_data
from .news import format_news_markdown, get_stock_latest_news
from .plate import get_stock_plate_change
from .quote import format_quote_markdown


def _format_section(title: str, body: str) -> str:
    if not body.strip():
        return f"## {title}\n\n暂无数据"
    return f"## {title}\n\n{body}"


def _get_mline_industries() -> list[str]:
    try:
        from .index import get_pt_board_rank_list
        pt_data = get_pt_board_rank_list("priceRatio", "down", 0, 5)
        items = pt_data.get("items", [])
        return [it.get("name", "") for it in items if isinstance(it, dict)]
    except Exception:
        return []


@click.command(name="quant")
@click.argument("symbol")
def quant(symbol: str):
    """个股量化分析：包含行情、日K与技术指标、资金流向、板块、快讯，以及5维度综合评估"""
    sections: list[str] = []

    quote_data = None
    kline_data = None
    mline_data = None
    fundflow_data = None
    plate_data = None
    news_data = None

    try:
        from ..api.qq import get_stock_by_code
        quote_data = get_stock_by_code(symbol)
        sections.append(format_quote_markdown(quote_data))
    except click.ClickException as e:
        sections.append(_format_section("实时行情", str(e)))

    try:
        kline_data = get_kline_data(symbol)
        sections.append(format_kline_markdown(kline_data, with_lines=False))
    except click.ClickException as e:
        sections.append(_format_section("日K线", str(e)))

    try:
        mline_data = get_mline_data(symbol)
    except click.ClickException as e:
        sections.append(_format_section("5分钟K线", str(e)))

    try:
        fundflow_data = get_fundflow_data(symbol)
    except click.ClickException as e:
        sections.append(_format_section("资金流向", str(e)))

    try:
        plate_data = get_stock_plate_change(symbol)
        # sections.append(format_plate_markdown(plate_data))
    except click.ClickException as e:
        sections.append(_format_section("相关板块", str(e)))

    try:
        news_data = get_stock_latest_news(symbol)
        sections.append(format_news_markdown(news_data))
    except click.ClickException as e:
        sections.append(_format_section("快讯", str(e)))

    click.echo("\n\n".join(sections))

    click.echo("\n\n## 量化分析\n\n")

    mline_industries = _get_mline_industries()

    stock_eval = evaluate_stock(
        fundflow_data=fundflow_data,
        plate_data=plate_data,
        kline_data=kline_data,
        mline_data=mline_data,
        quote_data=quote_data,
        mline_industries=mline_industries,
    )

    click.echo(format_stock_evaluation_markdown(stock_eval))
