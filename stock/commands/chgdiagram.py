from __future__ import annotations

import click

from ..api.baidu import fetch_chgdiagram_payload


def _format_status(status: str) -> str:
    if status == "up":
        return "上涨"
    if status == "same":
        return "平盘"
    if status == "down":
        return "下跌"
    return status


def get_chgdiagram_data(market: str) -> dict:
    payload = fetch_chgdiagram_payload(market)
    result = payload.get("Result") if isinstance(payload, dict) else {}
    chg = result.get("chgdiagram") if isinstance(result, dict) else {}
    ratio = chg.get("ratio") if isinstance(chg, dict) else {}
    diagram = chg.get("diagram") if isinstance(chg, dict) else []
    up = int(ratio.get("up", 0)) if isinstance(ratio, dict) else 0
    balance = int(ratio.get("balance", 0)) if isinstance(ratio, dict) else 0
    down = int(ratio.get("down", 0)) if isinstance(ratio, dict) else 0
    items: list[dict] = []
    if isinstance(diagram, list):
        for item in diagram:
            if not isinstance(item, dict):
                continue
            items.append(
                {
                    "status": str(item.get("status", "")),
                    "title": str(item.get("title", "")),
                    "count": int(item.get("count", 0) or 0),
                }
            )
    return {"ratio": {"up": up, "balance": balance, "down": down}, "diagram": items}


def format_chgdiagram_markdown(data: dict) -> str:
    ratio = data.get("ratio", {})
    diagram = data.get("diagram", [])
    lines = [
        f"{_format_status(str(item.get('status', '')))},{str(item.get('title', ''))},{int(item.get('count', 0))}"
        for item in diagram
        if isinstance(item, dict)
    ]
    return "\n".join(
        [
            "## 涨跌分布",
            "",
            f"上涨：{ratio.get('up', 0)}家，平盘：{ratio.get('balance', 0)}家，下跌：{ratio.get('down', 0)}家",
            "",
            "```csv",
            "状态,区间,数量",
            *lines,
            "```",
        ]
    )


@click.command(name="chgdiagram")
@click.option(
    "--market",
    default="ab",
    show_default=True,
    type=click.Choice(["ab", "us", "hk"], case_sensitive=False),
    help="市场",
)
def chgdiagram(market: str):
    """市场涨跌分布"""
    data = get_chgdiagram_data(market.lower())
    click.echo(format_chgdiagram_markdown(data))
