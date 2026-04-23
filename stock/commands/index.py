from __future__ import annotations

import click

from stock.commands.kline import get_kline_data

from ..api.qq import (
    fetch_chgdiagram_payload,
    fetch_pt_board_rank_payload,
    get_current_time,
    get_stock_by_query,
    zdf_percent,
)
from ..utils.evaluate_index import evaluate_market, format_evaluation_markdown

CODES = {
    'ab': [
        'sh000001',
        'sz399001',
        'sz399006',
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


def format_quotes_markdown(quotes: list[dict], klines: list[list[dict]]) -> str:
    lines = []
    for quote, kline in zip(quotes, klines, strict=False):
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
                    str(kline["factors"]["ema_5"]),
                    str(kline["factors"]["ema_10"]),
                    str(kline["factors"]["ema_20"]),
                    str(kline["factors"]["boll_up"]),
                    str(kline["factors"]["boll_mid"]),
                    str(kline["factors"]["boll_low"]),
                    str(kline["factors"]["rsi_6"]),
                    str(kline["factors"]["rsi_12"]),
                ]
            )
        )
    return "\n".join(
        [
            "## 指数",
            "",
            "```csv",
            "代码,名称,价格,涨跌幅,昨收价,开盘价,最高价,最低价,EMA5,EMA10,EMA20,BOLL_UP,BOLL_M,BOLL_LOW,RSI6,RSI12",
            *lines,
            "```",
        ]
    )


def _format_flag(flag: int) -> str:
    if flag == 1:
        return "上涨"
    if flag == 0:
        return "平盘"
    if flag == -1:
        return "下跌"
    return str(flag)


def _format_amount(value: float) -> str:
    yi = value / 100000000
    if yi >= 10000:
        return f"{yi / 10000:.2f}万亿"
    return f"{yi:.2f}亿"


def get_chgdiagram_data() -> dict:
    payload = fetch_chgdiagram_payload()
    data_obj = payload.get("data") if isinstance(payload, dict) else {}
    ups_downs = data_obj.get("ups_downs_dsb") if isinstance(data_obj, dict) else {}
    turnover_dsb = data_obj.get("turnover_dsb") if isinstance(data_obj, dict) else {}
    turnover = turnover_dsb.get("all") if isinstance(turnover_dsb, dict) else {}
    up_count = int(ups_downs.get("up_count", 0) or 0) if isinstance(ups_downs, dict) else 0
    flat_count = int(ups_downs.get("flat_count", 0) or 0) if isinstance(ups_downs, dict) else 0
    down_count = int(ups_downs.get("down_count", 0) or 0) if isinstance(ups_downs, dict) else 0
    up_limit_count = int(ups_downs.get("up_limit_count", 0) or 0) if isinstance(ups_downs, dict) else 0
    down_limit_count = int(ups_downs.get("down_limit_count", 0) or 0) if isinstance(ups_downs, dict) else 0
    up_ratio_comment = str(ups_downs.get("up_ratio_comment", "")) if isinstance(ups_downs, dict) else ""
    detail_list = ups_downs.get("detail") if isinstance(ups_downs, dict) else []
    items: list[dict] = []
    if isinstance(detail_list, list):
        for item in detail_list:
            if not isinstance(item, dict):
                continue
            items.append(
                {
                    "flag": int(item.get("flag", 0) or 0),
                    "section": str(item.get("section", "")),
                    "count": int(item.get("count", 0) or 0),
                }
            )
    amount = float(turnover.get("amount", 0) or 0) if isinstance(turnover, dict) else 0
    amount_change = float(turnover.get("amount_change", 0) or 0) if isinstance(turnover, dict) else 0
    return {
        "up_count": up_count,
        "flat_count": flat_count,
        "down_count": down_count,
        "up_limit_count": up_limit_count,
        "down_limit_count": down_limit_count,
        "up_ratio_comment": up_ratio_comment,
        "detail": items,
        "amount": amount,
        "amount_change": amount_change,
    }


def format_chgdiagram_markdown(data: dict) -> str:
    detail = data.get("detail", [])
    lines = [
        f"{_format_flag(it.get('flag', 0))},{it.get('section', '')},{it.get('count', 0)}"
        for it in detail
        if isinstance(it, dict)
    ]
    amount = data.get("amount", 0)
    amount_change = data.get("amount_change", 0)
    amount_change_label = "放量" if amount_change >= 0 else "缩量"
    amount_change_value = _format_amount(abs(amount_change))
    summary = (
        f"上涨：{data.get('up_count', 0)}家，"
        f"平盘：{data.get('flat_count', 0)}家，"
        f"下跌：{data.get('down_count', 0)}家，"
        f"涨停：{data.get('up_limit_count', 0)}家，"
        f"跌停：{data.get('down_limit_count', 0)}家"
    )
    return "\n".join(
        [
            "## 涨跌分布",
            "",
            summary,
            "",
            f"> {data.get('up_ratio_comment', '')}",
            "",
            f"今日成交额：{_format_amount(amount)}，较昨日{amount_change_label}：{amount_change_value}",
            "",
            "```csv",
            "状态,区间,数量",
            *lines,
            "```",
        ]
    )


def get_pt_board_rank_list(sort: str, direct: str, offset: int, count: int) -> dict:
    payload = fetch_pt_board_rank_payload(
        board_type="hy",
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
            lzg = it.get("lzg") or {}
            items.append(
                {
                    "code": str(it.get("code", "").replace("pt", "")),
                    "name": str(it.get("name", "")),
                    "zdf": zdf_percent(str(it.get("zdf", ""))),
                    "zdf_d5": zdf_percent(str(it.get("zdf_d5", ""))),
                    "zd": str(it.get("zd", "")),
                    "hsl": str(it.get("hsl", "")),
                    "lb": str(it.get("lb", "")),
                    "ltsz": str(it.get("ltsz", "")),
                    "zljlr": str(it.get("zljlr", "")),
                    "lzg_code": str(lzg.get("code", "")),
                    "lzg_name": str(lzg.get("name", "")),
                    "lzg_zdf": zdf_percent(str(lzg.get("zdf", ""))),
                }
            )
    return {"offset": int(data_obj.get("offset", 0) or 0), "total": int(data_obj.get("total", 0) or 0), "items": items}


def format_pt_rank_table(data: dict) -> str:
    items = data.get("items", [])
    if not items:
        return "暂无数据"
    lines = [
        ",".join(
            [
                it.get("name", ""),
                it.get("zdf", ""),
                it.get("hsl", "") + '%',
                it.get("lb", ""),
                it.get("zljlr", ""),
            ]
        )
        for it in items
        if isinstance(it, dict)
    ]
    if len(lines) > 10:
        lines = lines[:5] + ["..."] + lines[-5:]
    return "\n".join(
        [
            "## 行业板块",
            "",
            "```csv",
            "名称,涨跌幅,换手率,量比,主力净流入(万元)",
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
    quotes = get_stock_by_query(','.join(CODES[market]))
    klines = [get_kline_data(code, count=30) for code in CODES[market]]
    click.echo(f"# 大盘行情 {get_current_time()}")
    click.echo("")
    click.echo(format_quotes_markdown(quotes, klines))
    if market == "ab":
        click.echo("")
        chgdiagram_data = get_chgdiagram_data()
        click.echo(format_chgdiagram_markdown(chgdiagram_data))
        click.echo("")
        pt_data = get_pt_board_rank_list("priceRatio", "down", 0, 30)
        click.echo(format_pt_rank_table(pt_data))
        click.echo("")
        eval_data = evaluate_market(quotes, chgdiagram_data, pt_data, klines)
        click.echo(format_evaluation_markdown(eval_data))
