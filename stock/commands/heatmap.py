from __future__ import annotations

import click

from ..api.baidu import fetch_blocks_heatmap_payload


def to_baidu_type_code(market: str) -> str:
    lower = market.lower()
    if lower.startswith("ab"):
        return "HY"
    if lower.startswith("us"):
        return "HY"
    if lower.startswith("hk"):
        return "HSHY"
    return ""


def get_heatmap_data(market: str) -> dict:
    type_code = to_baidu_type_code(market)
    if not type_code:
        raise click.ClickException("不支持的市场")
    payload = fetch_blocks_heatmap_payload(market, type_code)
    result = payload.get("Result") if isinstance(payload, dict) else {}
    lst = result.get("list") if isinstance(result, dict) else {}
    body = lst.get("body") if isinstance(lst, dict) else []
    rows: list[dict] = []
    if isinstance(body, list):
        for item in body:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "name": str(item.get("name", "")),
                    "marketValue": str(item.get("marketValue", "")),
                    "amount": str(item.get("amount", "")),
                    "pxChangeRate": str(item.get("pxChangeRate", "")),
                }
            )
    return {"rows": rows}


def format_heatmap_markdown(data: dict) -> str:
    rows = data.get("rows", [])
    lines = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        parts = [
            str(item.get("name", "")),
            str(item.get("marketValue", "")),
            str(item.get("amount", "")),
            str(item.get("pxChangeRate", "")),
        ]
        lines.append(",".join(parts))
    return "\n".join(
        [
            "## 行业板块热力图",
            "",
            "```csv",
            "行业板块,总市值,成交额,涨跌幅",
            *lines,
            "```",
        ]
    )


@click.command(name="heatmap")
@click.option(
    "--market",
    default="ab",
    show_default=True,
    type=click.Choice(["ab", "us", "hk"], case_sensitive=False),
    help="市场",
)
def heatmap(market: str):
    """行业板块热力图"""
    data = get_heatmap_data(market.lower())
    click.echo(format_heatmap_markdown(data))
