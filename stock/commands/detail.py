from __future__ import annotations

import click

from stock.commands.mline import format_mline_markdown, get_mline_data

from .fundflow import format_fundflow_markdown, get_fundflow_data
from .kline import format_kline_markdown, get_kline_data
from .news import format_news_markdown, get_stock_latest_news
from .plate import format_plate_markdown, get_stock_plate_change
from .quote import format_quote_markdown
from ..utils.evaluate_detail import evaluate_fundflow, format_fundflow_evaluation_markdown


def _format_section(title: str, body: str) -> str:
    if not body.strip():
        return f"## {title}\n\n暂无数据"
    return f"## {title}\n\n{body}"


@click.command(name="detail")
@click.argument("symbol")
def detail(symbol: str):
    """个股详情：包含行情、日K与技术指标、资金流向、板块、快讯"""
    sections: list[str] = []

    quote_data = None
    try:
        from ..api.qq import get_stock_by_code
        quote_data = get_stock_by_code(symbol)
        sections.append(format_quote_markdown(quote_data))
    except click.ClickException as e:
        sections.append(_format_section("实时行情", str(e)))

    try:
        kline_data = get_kline_data(symbol)
        sections.append(format_kline_markdown(kline_data))
    except click.ClickException as e:
        sections.append(_format_section("日K线", str(e)))

    try:
        mline_data = get_mline_data(symbol)
        sections.append(format_mline_markdown(mline_data))
    except click.ClickException as e:
        sections.append(_format_section("15分钟K线", str(e)))

    try:
        fundflow_data = get_fundflow_data(symbol)
        sections.append(format_fundflow_markdown(fundflow_data))
    except click.ClickException as e:
        sections.append(_format_section("资金流向", str(e)))

    try:
        plate_data = get_stock_plate_change(symbol)
        sections.append(format_plate_markdown(plate_data))
    except click.ClickException as e:
        sections.append(_format_section("相关板块", str(e)))

    try:
        news_data = get_stock_latest_news(symbol)
        sections.append(format_news_markdown(news_data))
    except click.ClickException as e:
        sections.append(_format_section("快讯", str(e)))

    click.echo("\n\n".join(sections))

    # click.echo("\n\n## 最终评估\n\n")

    # if fundflow_data is not None:
    #     try:
    #         eval_data = evaluate_fundflow(fundflow_data, quote_data)
    #         click.echo(format_fundflow_evaluation_markdown(eval_data))
    #     except Exception:
    #         pass
