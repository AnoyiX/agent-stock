from __future__ import annotations

import click

from ..api.qq import fetch_board_rank_payload


def _suffix_percent(value: str) -> str:
    return value if value.endswith("%") else f"{value}%"


def get_board_rank_list(sort: str, direct: str, offset: int, count: int) -> dict:
    payload = fetch_board_rank_payload(
        board_code="aStock",
        sort_type=sort,
        direct=direct,
        offset=offset,
        count=count,
    )
    data_obj = payload.get("data") if isinstance(payload, dict) else {}
    rank_list = data_obj.get("rank_list") if isinstance(data_obj, dict) else []
    items: list[dict] = []
    if isinstance(rank_list, list):
        for it in rank_list:
            if not isinstance(it, dict):
                continue
            items.append(
                {
                    "code": str(it.get("code", "")),
                    "name": str(it.get("name", "")),
                    "zxj": str(it.get("zxj", "")),
                    "zdf": _suffix_percent(str(it.get("zdf", ""))),
                    "turnover": str(it.get("turnover", "")),
                    "hsl": str(it.get("hsl", "")),
                    "lb": str(it.get("lb", "")),
                    "zsz": str(it.get("zsz", "")),
                    "ltsz": str(it.get("ltsz", "")),
                    "pe_ttm": str(it.get("pe_ttm", "")),
                    "zljlr": str(it.get("zljlr", "")),
                }
            )
    return {"offset": int(data_obj.get("offset", 0) or 0), "total": int(data_obj.get("total", 0) or 0), "items": items}


def format_rank_table(data: dict) -> str:
    items = data.get("items", [])
    if not items:
        return "暂无数据"
    lines = [
        ",".join(
            [
                it.get("code", ""),
                it.get("name", ""),
                it.get("zxj", ""),
                it.get("zdf", ""),
                it.get("turnover", ""),
                it.get("hsl", ""),
                it.get("lb", ""),
                it.get("zsz", ""),
                it.get("ltsz", ""),
                it.get("pe_ttm", ""),
                it.get("zljlr", "")
            ]
        )
        for it in items
        if isinstance(it, dict)
    ]
    return "\n".join(
        [
            "```csv",
            "代码,名称,现价,涨跌幅,成交额,换手率,量比,总市值,流通市值,市盈率TTM,主力净流入",
            *lines,
            "```",
        ]
    )


@click.command(name="rank")
@click.option(
    "--sort",
    default="turnover",
    show_default=True,
    help="排序类型（turnover/amplitude/volumeRatio/exchange/priceRatio）",
)
@click.option(
    "--direct",
    default="down",
    show_default=True,
    type=click.Choice(["down", "up"], case_sensitive=False),
    help="排序方向",
)
@click.option("--offset", default=0, show_default=True, type=click.IntRange(0, 100000), help="偏移量")
@click.option("--count", default=20, show_default=True, type=click.IntRange(1, 100), help="数量")
def rank(sort: str, direct: str, offset: int, count: int):
    """股票排序（限A股）"""
    data = get_board_rank_list(sort, direct, offset, count)
    click.echo(format_rank_table(data))
