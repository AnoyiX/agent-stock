# agent-stock

[![CI](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/agent-stock.svg)](https://pypi.org/project/agent-stock/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/agent-stock/)

面向 AI Agent 的股市数据命令行工具，提供市场概览、个股行情、板块涨跌、技术指标与资金流向等信息。

## 📦 安装

```bash
# uv tool
uv tool install agent-stock  # 安装
uv tool upgrade agent-stock  # 升级

# pip
python -m pip install agent-stock     # 安装
python -m pip install -U agent-stock  # 升级
```

## 🚀 快速开始

```bash
# 市场数据
stock search 腾讯
stock rank --count 20

# 个股数据
stock quote 000001
stock quote 000001,600519
stock kline 000001
stock fundflow 000001

# 帮助与版本
stock --help
stock quote --help
stock -v
```

## 🔧 命令

可以通过 `stock --help` 或 `stock <子命令> --help` 查看帮助。

### 市场数据

```bash
stock index --market <market>             # 大盘主要指数总览（A股含申万一级行业数据）
stock search <keyword>                    # 股票搜索，仅限股票名称、股票代码、股票简称搜索

# 仅限A股使用的命令
stock query <condition>                   # 条件选股
stock rank --sort <sort> --count <count>  # 市场股票排序，sort 默认值 turnover

# 参数说明：
# - market: 市场，可选 ab｜us｜hk，默认 ab
# - sort: 排序类型，可选 成交额 turnover｜量比 volumeRatio｜换手率 exchange｜涨跌幅 priceRatio｜主力净流入 netMainIn
# - count: 排序数量，默认 20，取值范围 1 - 100
# - keyword: 关键词，示例：腾讯、tengxun等
# - condition: 自然语言的条件语句，示例："MACD金叉；KDJ金叉；非ST；非涨停；市盈率大于0；市盈率小于100；市值大于50亿；"
```

### 个股数据

```bash
stock detail <symbol>               # 个股详情，包含股票实时行情、相关板块、最新新闻、日K数据、技术指标、资金流向等
stock quote <symbols>               # 个股实时行情（支持批量查询）
stock plate <symbol>                # 个股相关板块涨跌幅（地域/行业/概念）
stock news <symbol>                 # 个股最新新闻
stock kline <symbol>                # 日K数据以及技术指标（EMA/BOLL/KDJ/RSI）
stock fundflow <symbol>             # 资金分布与每日主力/散户净流向

# 参数说明：
# - symbol: 股票代码，支持 A 股、港股、美股
#   - A股：6 位数字，如 600519、000001
#   - 港股：5 位数字，如 00700
#   - 美股：us.<ticker>，如 us.aapl、us.msft（大小写不敏感）
# - symbols: 单个或多个股票代码，用逗号分隔，如 000001,00700,us.aapl
```

## 🤖 技能

### 个股决策

输入示例： `帮我决策 天孚通信`

### AI 选股

输入示例： `帮我选股`

## 🐛 开发

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# Lint
uv run ruff check .

# 调试
uv run python -m stock quote 000001
```

在 IDE 中启用该技能，以 Trae 为例：

```bash
mkdir -p .trae/skills/

ln -s $(pwd)/skills ~/.trae/skills/agent-stock
```


## Download History

[![Download History](https://skill-history.com/chart/anoyix/agent-stock.svg)](https://skill-history.com/anoyix/agent-stock)
