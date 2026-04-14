"""CLI entry point for agent-stock."""

from __future__ import annotations

import logging

import click

from . import __version__
from .commands.detail import detail
from .commands.fundflow import fundflow
from .commands.index import index
from .commands.kline import kline
from .commands.news import news
from .commands.plate import plate
from .commands.pt import pt
from .commands.query import query
from .commands.quote import quote
from .commands.rank import rank
from .commands.search import search


@click.group()
@click.version_option(__version__, "-v", "--version")
@click.option("-d", "--verbose", is_flag=True, help="启用调试日志")
@click.option(
    "-i",
    "--interval",
    default=10,
    show_default=True,
    type=click.IntRange(1, 3600),
    help="刷新间隔（秒）",
)
@click.option("--no-color", is_flag=True, help="禁用颜色输出")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, interval: int, no_color: bool):
    """股市行情命令行工具 - stock"""
    ctx.ensure_object(dict)
    ctx.obj["interval"] = interval
    ctx.color = not no_color
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)


cli.add_command(quote)
cli.add_command(detail)
cli.add_command(plate)
cli.add_command(news)
cli.add_command(search)
cli.add_command(query)
cli.add_command(kline)
cli.add_command(fundflow)
cli.add_command(index)
cli.add_command(rank)
cli.add_command(pt)

if __name__ == "__main__":
    cli()
