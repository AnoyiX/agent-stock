from __future__ import annotations

import json
import re
from datetime import datetime

import click
import requests

_A_CODE_PATTERN = re.compile(r"^(?:[56]\d{5}|[031]\d{5}|4\d{5}|8\d{5}|92\d{4})$")
_HK_CODE_PATTERN = re.compile(r"^\d{5}$")


def _http_get_with_proxy_fallback(url: str, **kwargs):
    try:
        return requests.get(url, **kwargs)
    except requests.RequestException as exc:
        if "socks" not in str(exc).lower():
            raise
        with requests.Session() as session:
            session.trust_env = False
            return session.get(url, **kwargs)


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


def get_query_code(symbol: str) -> str:
    lower = symbol.lower()
    if lower.startswith("us"):
        return lower.split(".")[0]
    if test_a_code(lower):
        return get_stock_with_prefix(lower)
    if test_hk_code(lower):
        return f"hk{lower}"
    return lower


def _get(arr: list[str], index: int, default: str = "") -> str:
    if index < len(arr):
        return str(arr[index])
    return default


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _suffix_percent(value: str) -> str:
    return value if value.endswith("%") else f"{value}%"


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


def get_stock_by_code(symbol: str) -> dict:
    query_code = get_query_code(symbol)
    url = "https://sqt.gtimg.cn"
    try:
        response = _http_get_with_proxy_fallback(
            url,
            params={"q": query_code, "fmt": "json"},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gu.qq.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        text = response.content.decode("gbk", errors="ignore")
    except requests.HTTPError as exc:
        raise click.ClickException(f"行情接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"行情接口不可用: {exc}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise click.ClickException("行情接口返回解析失败") from exc
    arr = payload.get(query_code)
    if not isinstance(arr, list) or len(arr) < 2:
        raise click.ClickException("无效股票代码或暂无行情数据")
    return arr2obj(arr)


def format_quote_markdown(quote: dict) -> str:
    return "\n".join(
        [
            "# 个股信息",
            "",
            f"股票: {quote['name']}，代码: {quote['code']}",
            "",
            "## 实时数据",
            "",
            f"- 当前价格: {quote['price']}",
            f"- 涨跌幅: {quote['change_rate']}",
            f"- 昨收价: {quote['previous_close']}",
            f"- 开盘价: {quote['open']}",
            f"- 最高价: {quote['high']}",
            f"- 最低价: {quote['low']}",
            f"- 总市值: {quote['market_value']}",
            f"- 流通市值: {quote['circulating_value']}",
            f"- 市盈率: {quote['pe']}",
            f"- 市净率: {quote['pb']}",
            f"- 成交量: {quote['volume']}",
            f"- 量比: {quote['vr']}",
            f"- 换手率: {quote['turnover_rate']}",
        ]
    )


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
    url = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/stockinfo/plateNew"
    try:
        response = _http_get_with_proxy_fallback(
            url,
            params={"code": code, "app": "wzq", "zdf": "1"},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Referer": "https://gu.qq.com/",
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        raise click.ClickException(f"板块接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"板块接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("板块接口返回解析失败") from exc
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
            "# 相关板块涨跌幅",
            "",
            f"股票代码: {plate_data['code']}",
            "",
            "## 地域",
            _format_plate_section(plate_data["area"]),
            "",
            "## 行业",
            _format_plate_section(plate_data["industry"]),
            "",
            "## 概念",
            _format_plate_section(plate_data["concept"]),
        ]
    )


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


def _normalize_symbol(symbol: str) -> str:
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


def _format_news_timestamp(timestamp: str) -> str:
    try:
        dt = datetime.fromtimestamp(int(str(timestamp)))
        return dt.strftime("%Y%m%d %H:%M")
    except (TypeError, ValueError, OSError):
        return "未知时间"


def get_stock_latest_news(symbol: str) -> dict:
    normalized = _normalize_symbol(symbol)
    market = to_baidu_market(normalized)
    code = to_simple_code(normalized)
    if not market or not code:
        raise click.ClickException("无效股票代码或暂无资讯数据")
    url = "https://finance.pae.baidu.com/vapi/sentimentlist"
    try:
        response = _http_get_with_proxy_fallback(
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
    except requests.HTTPError as exc:
        raise click.ClickException(f"资讯接口请求失败: HTTP {exc.response.status_code}") from exc
    except requests.RequestException as exc:
        raise click.ClickException(f"资讯接口不可用: {exc}") from exc
    except ValueError as exc:
        raise click.ClickException("资讯接口返回解析失败") from exc
    result = payload.get("Result")
    if not isinstance(result, list) or not result:
        return {"symbol": normalized, "news": []}
    item = result[0] if isinstance(result[0], dict) else {}
    tpl = item.get("TplData")
    tpl_data = tpl if isinstance(tpl, dict) else {}
    sentiment = tpl_data.get("aiSentimentXcxListInfo")
    sentiment_info = sentiment if isinstance(sentiment, dict) else {}
    news = sentiment_info.get("sentimentListInfo")
    if not isinstance(news, list):
        news = []
    return {"symbol": normalized, "news": news}


def format_news_markdown(news_data: dict) -> str:
    news_list = news_data["news"]
    if not news_list:
        return "\n".join(["# 最新资讯", "", f"股票代码: {news_data['symbol']}", "", "- 暂无数据"])
    lines: list[str] = []
    for item in news_list:
        if not isinstance(item, dict):
            continue
        abstract = str(item.get("abstract", "")).strip()
        if not abstract:
            continue
        lines.append(f"- [{_format_news_timestamp(str(item.get('publishTime', '')))}] {abstract}")
    if not lines:
        lines = ["- 暂无数据"]
    return "\n".join(["# 最新资讯", "", f"股票代码: {news_data['symbol']}", "", *lines])


@click.command(name="quote")
@click.argument("symbol")
def quote(symbol: str):
    data = get_stock_by_code(symbol)
    click.echo(format_quote_markdown(data))


@click.command(name="plate")
@click.argument("symbol")
def plate(symbol: str):
    data = get_stock_plate_change(symbol)
    click.echo(format_plate_markdown(data))


@click.command(name="news")
@click.argument("symbol")
def news(symbol: str):
    data = get_stock_latest_news(symbol)
    click.echo(format_news_markdown(data))
