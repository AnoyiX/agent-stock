from __future__ import annotations

import re

import click
import requests

from . import http_get_with_proxy_fallback

_A_CODE_PATTERN = re.compile(r"^(?:[56]\d{5}|[031]\d{5}|4\d{5}|8\d{5}|92\d{4})$")
_HK_CODE_PATTERN = re.compile(r"^\d{5}$")


def fetch_latest_news_payload(market: str, code: str) -> dict:
    url = "https://finance.pae.baidu.com/vapi/sentimentlist"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={
                "market": market,
                "code": code,
                "query": code,
                "financeType": "stock",
                "benefitType": "",
                "pn": "0",
                "rn": "20",
                "finClientType": "pc",
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gushitong.baidu.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"资讯接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"资讯接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("资讯接口返回解析失败") from exc


def fetch_fundflow_day_payload(market: str, code: str, date: str) -> dict:
    url = "https://finance.pae.baidu.com/vapi/v1/fundflow"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={
                "finance_type": "stock",
                "fund_flow_type": "day",
                "market": market,
                "code": code,
                "date": date,
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gushitong.baidu.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"资金流向接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"资金流向接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("资金流向接口返回解析失败") from exc


def fetch_fundflow_spread_payload(market: str, code: str) -> dict:
    url = "https://finance.pae.baidu.com/vapi/v1/fundflow"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={
                "finance_type": "stock",
                "fund_flow_type": "",
                "market": market,
                "code": code,
                "type": "stock",
                "finClientType": "pc",
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gushitong.baidu.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"资金流向接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"资金流向接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("资金流向接口返回解析失败") from exc


def fetch_chgdiagram_payload(market: str) -> dict:
    url = "https://finance.pae.baidu.com/sapi/v1/marketquote"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={"bizType": "chgdiagram", "market": market, "finClientType": "pc"},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gushitong.baidu.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"涨跌分布接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"涨跌分布接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("涨跌分布接口返回解析失败") from exc


def fetch_blocks_heatmap_payload(market: str, type_code: str) -> dict:
    url = "https://finance.pae.baidu.com/vapi/v2/blocks"
    try:
        response = http_get_with_proxy_fallback(
            url,
            params={
                "style": "heatmap",
                "market": market,
                "typeCode": type_code,
                "sortKey": "amount",
                "sortType": "desc",
                "pn": "0",
                "rn": "80",
                "finClientType": "pc",
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gushitong.baidu.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload
    except requests.HTTPError as exc:
        raise click.ClickException(f"行业板块热力图接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"行业板块热力图接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("行业板块热力图接口返回解析失败") from exc


def to_baidu_market(symbol: str) -> str:
    if symbol.startswith(("sh", "sz", "bj")):
        return "ab"
    if symbol.startswith("us"):
        return "us"
    if re.fullmatch(r"hk\d{5}", symbol):
        return "hk"
    return ""


def to_simple_code(symbol: str) -> str:
    if symbol.startswith(("sh", "sz", "bj", "bg")):
        return symbol[2:]
    if symbol.startswith("us."):
        parts = symbol.split(".", 1)
        return parts[1] if len(parts) > 1 else ""
    if symbol.startswith("us"):
        return symbol[2:]
    if re.fullmatch(r"hk\d{5}", symbol):
        return symbol[2:]
    return symbol


def test_a_code(code: str) -> bool:
    return bool(_A_CODE_PATTERN.fullmatch(code))


def test_hk_code(code: str) -> bool:
    return bool(_HK_CODE_PATTERN.fullmatch(code))


def get_stock_with_prefix(code: str) -> str:
    if re.fullmatch(r"(?:5|6)\d{5}", code):
        return f"sh{code}"
    if re.fullmatch(r"(?:0|3|1)\d{5}", code):
        return f"sz{code}"
    if re.fullmatch(r"(?:4\d{5}|8\d{5}|92\d{4})", code):
        return f"bj{code}"
    return code


def normalize_symbol(symbol: str) -> str:
    lower = symbol.lower()
    if lower.startswith("us."):
        parts = lower.split(".", 1)
        if len(parts) > 1 and parts[1]:
            return f"us{parts[1]}"
    if test_a_code(lower):
        return get_stock_with_prefix(lower)
    if test_hk_code(lower):
        return f"hk{lower}"
    return lower