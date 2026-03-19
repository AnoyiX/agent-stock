from __future__ import annotations

import json

import click
import requests

from . import http_get_with_proxy_fallback
from .baidu import get_stock_with_prefix, is_a_code, is_hk_code

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://gu.qq.com/",
    "Accept": "application/json,text/plain,*/*",
}


def fetch_quote_json(query_code: str) -> dict:
    url = "https://sqt.gtimg.cn"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={"q": query_code, "fmt": "json"},
            headers=COMMON_HEADERS,
            timeout=10.0,
        )
        response.raise_for_status()
        text = response.content.decode("gbk", errors="ignore")
        return json.loads(text)
    except requests.HTTPError as exc:
        raise click.ClickException(f"行情接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"行情接口不可用: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise click.ClickException("行情接口返回解析失败") from exc


def fetch_kline_payload(query_code: str) -> dict:
    url = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={"param": f"{query_code},day,,,90,qfq"},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gu.qq.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"日K接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"日K接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("日K接口返回解析失败") from exc


def fetch_plate_payload(code: str) -> dict:
    url = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/stockinfo/plateNew"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={"code": code, "app": "wzq", "zdf": "1"},
            headers=COMMON_HEADERS,
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"板块接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"板块接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("板块接口返回解析失败") from exc


def fetch_search_payload(query: str) -> dict:
    url = "https://proxy.finance.qq.com/cgi/cgi-bin/smartbox/search"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={"stockFlag": "1", "fundFlag": "1", "app": "official_website", "query": query},
            headers=COMMON_HEADERS,
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"搜索接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"搜索接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("搜索接口返回解析失败") from exc


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _suffix_percent(value: str) -> str:
    return value if value.endswith("%") else f"{value}%"


def _get(arr: list[str], index: int, default: str = "") -> str:
    if index < len(arr):
        return str(arr[index])
    return default


def arr2obj(arr: list[str]) -> dict:
    prefix_map = {"1": "sh", "51": "sz", "62": "bj", "100": "hk", "200": "us"}
    prefix = prefix_map.get(_get(arr, 0), "")
    index_offset = 1 if prefix in {"us", "hk"} else 0
    volume = f"{_to_float(_get(arr, 36)) / 10000:.2f}万手"
    return {
        "symbol": f"{prefix}{_get(arr, 2)}",
        "code": _get(arr, 2),
        "name": _get(arr, 1),
        "price": _get(arr, 3),
        "change_rate": _suffix_percent(_get(arr, 32)),
        "previous_close": _get(arr, 4),
        "open": _get(arr, 5),
        "high": _get(arr, 33),
        "low": _get(arr, 34),
        "volume": volume,
        "market_value": f"{_get(arr, 45)}亿",
        "circulating_value": f"{_get(arr, 44)}亿",
        "turnover_rate": _suffix_percent(_get(arr, 38)),
        "pe": _get(arr, 39),
        "pb": _get(arr, 46),
        "vr": _get(arr, 49 + index_offset),
    }


def get_query_code(symbol: str) -> str:
    lower = symbol.lower()
    if lower.startswith("us"):
        return lower.split(".")[0]
    if is_a_code(lower):
        return get_stock_with_prefix(lower)
    if is_hk_code(lower):
        return f"hk{lower}"
    return lower


def get_stock_by_query(query: str) -> dict:
    result = fetch_quote_json(query)
    return [arr2obj(arr) for arr in result.values()]


def get_stock_by_code(symbol: str) -> dict:
    query = get_query_code(symbol)
    result = fetch_quote_json(query)
    arr = result.get(query)
    if not isinstance(arr, list) or len(arr) < 2:
        raise click.ClickException("无效股票代码或暂无行情数据")
    return arr2obj(arr)
