from __future__ import annotations

import click

from ..api.baidu import get_stock_with_prefix
from ..api.qq import fetch_plate_payload


def _format_plate_item(plate: dict) -> str:
    name = str(plate.get("name", "未知板块"))
    zdf = str(plate.get("zdf", "0"))
    if zdf.endswith("%"):
        return f"- {name}: {zdf if zdf.startswith('-') else f'+{zdf}'}"
    return f"- {name}: {zdf if zdf.startswith('-') else f'+{zdf}'}%"


def _format_plate_section(plates: list[dict] | None) -> str:
    if not plates:
        return "- 暂无数据"
    return "\n".join(_format_plate_item(plate) for plate in plates)


def get_stock_plate_change(symbol: str) -> dict:
    code = get_stock_with_prefix(symbol.lower())
    payload = fetch_plate_payload(code)
    data = payload.get("data")
    if not isinstance(data, dict):
        raise click.ClickException("无效股票代码或暂无板块数据")
    return {
        "code": code,
        "area": data.get("area") if isinstance(data.get("area"), list) else [],
        "industry": data.get("plate") if isinstance(data.get("plate"), list) else [],
        "concept": data.get("concept") if isinstance(data.get("concept"), list) else [],
    }


def format_plate_markdown(plate_data: dict) -> str:
    return "\n".join(
        [
            "## 相关板块",
            "",
            "### 地域",
            _format_plate_section(plate_data["area"]),
            "",
            "### 行业",
            _format_plate_section(plate_data["industry"]),
            "",
            "### 概念",
            _format_plate_section(plate_data["concept"]),
        ]
    )


@click.command(name="plate")
@click.argument("symbol")
def plate(symbol: str):
    """个股相关板块涨跌幅（地域/行业/概念）"""
    data = get_stock_plate_change(symbol)
    click.echo(format_plate_markdown(data))
