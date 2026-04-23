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
stock index                               # 大盘主要指数总览（A股含申万一级行业数据）
stock search <keyword>                    # 股票搜索，仅限股票名称、股票代码、股票简称搜索
stock query <condition>                   # 条件选股
stock rank --sort <sort> --count <count>  # 市场股票排序，sort 默认值 turnover

# 参数说明：
# - sort: 排序类型，可选 成交额 turnover｜量比 volumeRatio｜换手率 exchange｜涨跌幅 priceRatio｜主力净流入 netMainIn
# - count: 排序数量，默认 20，取值范围 1 - 100
# - keyword: 关键词，示例：腾讯、tengxun等
# - condition: 自然语言的条件语句，示例："MACD金叉；KDJ金叉；非ST；非涨停；市盈率大于0；市盈率小于100；市值大于50亿；"
```

### 个股数据

```bash
stock detail <symbol>               # 个股详情，包含股票实时行情、日K数据、技术指标、分时数据、资金流向、相关板块和概念、新闻等

# 参数说明：
# - symbol: 股票代码，支持 A 股，如 600519、000001
```

## 🤖 技能

### 【个股决策】

输入示例： `帮我决策 天孚通信`

### 【AI 选股】

输入示例： `帮我选股`

### 【持仓分析】

输入示例（建议单次分析不要超过 6 只股票持仓的记录）：

```plaintext
帮我分析持仓：

资金余额: 400000, 总资产: 1000000, 总市值: 600000, 持仓占比: 60%
\`\`\`csv
代码,名称,现价,成本,股数,持仓收益率,持仓占比
000001,xxxxxx,20.45,20.33,400,+4.96%,1.51%
000002,xxxxxx,20.82,21.84,1600,-2.92%,6.00%
000003,xxxxxx,3.46,3.89,39900,-1.05%,24.41%
000004,xxxxxx,26.89,25.34,1500,+2.88%,6.92%
\`\`\`
```

> [!TIP]
> [Stocks AI 投资账本](https://ai.anoyi.com/dashboard/ths/tzzb) 可以一键复制持仓分析信息

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
