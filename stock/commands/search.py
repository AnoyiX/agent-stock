"""Stock CLI commands with mock data."""

from __future__ import annotations

import click

from ..api.qq import fetch_search_payload

VALID_MARKETS = {"US", "CN", "HK"}


@click.command(name="search")
@click.argument("keyword")
def search(keyword: str):
    """搜索股票"""
    data = get_search_results(keyword)
    click.echo(format_search_table(data))


def get_search_results(keyword: str) -> list[dict]:
    payload = fetch_search_payload(keyword)
    items = payload.get("stock")
    results: list[dict] = []
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                continue
            code = str(it.get("code", "")).strip()
            name = str(it.get("name", "")).strip()
            type_ = str(it.get("type", "")).strip()
            if code and name:
                results.append({"code": code, "name": name, "type": type_})
    return results


def format_search_table(results: list[dict]) -> str:
    if not results:
        return "暂无数据"
    lines = ["代码,名称,类型"]
    for r in results:
        code = str(r.get("code", ""))
        name = str(r.get("name", ""))
        type_ = str(r.get("type", ""))
        lines.append(f"{code},{name},{type_}")
    return "\n".join(["```csv", *lines, "```"])
