from click.testing import CliRunner

from stock.cli import cli
from stock.commands import chgdiagram as chgdiagram_command
from stock.commands import fundflow as fundflow_command
from stock.commands import heatmap as heatmap_command
from stock.commands import kline as kline_command
from stock.commands import quote as quote_command
from stock.commands import search as market_command

runner = CliRunner()


def test_quote_output(monkeypatch):
    monkeypatch.setattr(
        quote_command,
        "get_stock_by_code",
        lambda _symbol: {
            "name": "顺灏股份",
            "code": "002565",
            "price": "13.19",
            "change_rate": "-4.28%",
            "previous_close": "13.78",
            "open": "13.64",
            "high": "13.76",
            "low": "13.15",
            "market_value": "139.81亿",
            "circulating_value": "139.81亿",
            "pe": "246.61",
            "pb": "7.50",
            "volume": "58.46万手",
            "vr": "0.76",
            "turnover_rate": "5.52%",
        },
    )
    result = runner.invoke(cli, ["quote", "600519"])
    assert result.exit_code == 0
    assert "# 个股信息" in result.output
    assert "股票: 顺灏股份，代码: 002565" in result.output
    assert "- 当前价格: 13.19" in result.output
    assert "- 换手率: 5.52%" in result.output


def test_plate_output(monkeypatch):
    monkeypatch.setattr(
        quote_command,
        "get_stock_plate_change",
        lambda _symbol: {
            "code": "sh600519",
            "area": [{"name": "贵州板块", "zdf": "0.12"}],
            "industry": [{"name": "酿酒行业", "zdf": "-0.35"}],
            "concept": [{"name": "白酒概念", "zdf": "1.28"}],
        },
    )
    result = runner.invoke(cli, ["plate", "600519"])
    assert result.exit_code == 0
    assert "# 相关板块涨跌幅" in result.output
    assert "股票代码: sh600519" in result.output
    assert "- 贵州板块: +0.12%" in result.output
    assert "- 酿酒行业: -0.35%" in result.output
    assert "- 白酒概念: +1.28%" in result.output


def test_news_output(monkeypatch):
    monkeypatch.setattr(
        quote_command,
        "get_stock_latest_news",
        lambda _symbol: {
            "symbol": "sh600519",
            "news": [
                {"publishTime": "1741420800", "abstract": "公司发布年度业绩预告，盈利能力持续提升。"},
                {"publishTime": "1741507200", "abstract": "行业需求回暖，机构维持增持评级。"},
            ],
        },
    )
    result = runner.invoke(cli, ["news", "600519"])
    assert result.exit_code == 0
    assert "# 最新资讯" in result.output
    assert "股票代码: sh600519" in result.output
    assert "公司发布年度业绩预告，盈利能力持续提升。" in result.output
    assert "行业需求回暖，机构维持增持评级。" in result.output


def test_search_table(monkeypatch):
    monkeypatch.setattr(
        market_command,
        "get_search_results",
        lambda _keyword: [
            {"code": "sz300789", "name": "唐源电气", "type": "GP-A-CYB"},
            {"code": "sh600519", "name": "贵州茅台", "type": "GP-A-AB"},
        ],
    )
    result = runner.invoke(cli, ["search", "唐源"])
    assert result.exit_code == 0
    assert "# 搜索结果" in result.output
    assert "关键词: 唐源" in result.output
    assert "```csv" in result.output
    assert "代码,名称,类型" in result.output
    assert "sz300789,唐源电气,GP-A-CYB" in result.output
    assert "sh600519,贵州茅台,GP-A-AB" in result.output


def test_market_output():
    result = runner.invoke(cli, ["market"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_history_default_range_output():
    result = runner.invoke(cli, ["history", "AAPL"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_history_custom_range():
    result = runner.invoke(cli, ["history", "AAPL", "--range", "5d"])
    assert result.exit_code == 0
    assert "暂无数据" in result.output


def test_kline_output(monkeypatch):
    monkeypatch.setattr(
        kline_command,
        "get_kline_data",
        lambda _symbol, count=45: {
            "lines": [
                {
                    "时间": 20260310,
                    "开盘价": 10.2,
                    "收盘价": 10.8,
                    "最高价": 10.9,
                    "最低价": 10.1,
                    "成交量": "1000手",
                    "成交额": "5000万",
                }
            ],
            "factors": {
                "ema_5": 10.55,
                "ema_10": 10.32,
                "ema_20": 10.11,
                "boll_up": 11.2,
                "boll_mid": 10.5,
                "boll_low": 9.8,
                "kdj_k": 61.2,
                "kdj_d": 58.9,
                "kdj_j": 65.8,
                "rsi_6": 54.12,
                "rsi_12": 51.88,
            },
        },
    )
    result = runner.invoke(cli, ["kline", "600519"])
    assert result.exit_code == 0
    assert "## 日K线" in result.output
    assert "时间,开盘价,收盘价,最高价,最低价,成交量,成交额" in result.output
    assert "20260310,10.2,10.8,10.9,10.1,1000手,5000万" in result.output
    assert "- EMA5: 10.55" in result.output


def test_fundflow_output(monkeypatch):
    monkeypatch.setattr(
        fundflow_command,
        "get_fundflow_data",
        lambda _symbol: {
            "spread": {
                "unit": "万元",
                "analysis": "主力净流入较强，市场情绪偏多。",
                "rows": [
                    {
                        "name": "净特大单",
                        "turnoverIn": 1200.5,
                        "turnoverInRate": "12.5%",
                        "turnoverOut": 800.3,
                        "turnoverOutRate": "8.6%",
                        "netTurnover": 400.2,
                    },
                    {
                        "name": "净大单",
                        "turnoverIn": 900.0,
                        "turnoverInRate": "9.0%",
                        "turnoverOut": 950.0,
                        "turnoverOutRate": "9.5%",
                        "netTurnover": -50.0,
                    },
                    {
                        "name": "净中单",
                        "turnoverIn": 500.0,
                        "turnoverInRate": "5.0%",
                        "turnoverOut": 450.0,
                        "turnoverOutRate": "4.5%",
                        "netTurnover": 50.0,
                    },
                    {
                        "name": "净小单",
                        "turnoverIn": 300.0,
                        "turnoverInRate": "3.0%",
                        "turnoverOut": 350.0,
                        "turnoverOutRate": "3.5%",
                        "netTurnover": -50.0,
                    },
                ],
                "todayMain": {"mainIn": "2000", "mainOut": "1500", "mainNetIn": "500"},
                "totals": {"turnoverInTotal": "2900.5", "turnoverOutTotal": "2550.3", "turnoverNetTotal": "350.2"},
            },
            "day": {
                "unit": "万元",
                "daily": [
                    {"date": 20260310, "main": 120.5, "retail": -50.2},
                    {"date": 20260311, "main": -30.0, "retail": 10.0},
                ],
            },
        },
    )
    result = runner.invoke(cli, ["fundflow", "600519"])
    assert result.exit_code == 0
    assert "## 资金流向" in result.output
    assert "### 资金分布(单位：万元)" in result.output
    assert "```csv" in result.output
    assert "类别,流入,流入占比,流出,流出占比,净流入" in result.output
    assert "净特大单,1200.5,12.5%,800.3,8.6%,400.2" in result.output
    assert "- 主力流入：2000，主力流出：1500，主力净流入：500" in result.output
    assert "### 每日资金流向(单位：万元)" in result.output
    assert "日期,主力净流入,散户净流入" in result.output
    assert "20260310,120.5,-50.2" in result.output


def test_chgdiagram_output(monkeypatch):
    monkeypatch.setattr(
        chgdiagram_command,
        "get_chgdiagram_data",
        lambda market="ab": {
            "ratio": {"up": 3200, "balance": 500, "down": 1500},
            "diagram": [
                {"status": "up", "title": "+9%~+10%", "count": 100},
                {"status": "same", "title": "0", "count": 20},
                {"status": "down", "title": "-9%~-10%", "count": 80},
            ],
        },
    )
    result = runner.invoke(cli, ["chgdiagram"])
    assert result.exit_code == 0
    assert "## 涨跌分布" in result.output
    assert "上涨：3200家，平盘：500家，下跌：1500家" in result.output
    assert "```csv" in result.output
    assert "状态,区间,数量" in result.output
    assert "上涨,+9%~+10%,100" in result.output
    assert "平盘,0,20" in result.output
    assert "下跌,-9%~-10%,80" in result.output


def test_heatmap_output(monkeypatch):
    monkeypatch.setattr(
        heatmap_command,
        "get_heatmap_data",
        lambda market="ab": {
            "rows": [
                {"name": "酿酒行业", "marketValue": "1234亿", "amount": "56亿", "pxChangeRate": "+1.23%"},
                {"name": "有色金属", "marketValue": "900亿", "amount": "30亿", "pxChangeRate": "-0.88%"},
            ]
        },
    )
    result = runner.invoke(cli, ["heatmap"])
    assert result.exit_code == 0
    assert "## 行业板块热力图" in result.output
    assert "```csv" in result.output
    assert "行业板块,总市值,成交额,涨跌幅" in result.output
    assert "酿酒行业,1234亿,56亿,+1.23%" in result.output
    assert "有色金属,900亿,30亿,-0.88%" in result.output
