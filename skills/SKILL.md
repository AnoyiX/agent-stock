---
name: agent-stock
description: AI 量化交易技能包。提供了股市实时数据获取工具，如市场概览、行业热力图、板块涨跌、个股资讯、日K/技术指标、资金流向与股票搜索等；还提供了短线交易选股和短线交易决策的工作流，为用户提供股票交易建议。
author: AnoyiX
version: "0.2.1"
tags:
  - Stock
  - CLI
  - 股票数据
  - 选股
  - 交易决策
---

# AI 量化交易 agent-stock

利用 `stock` 命令获取市场、个股实时数据，再根据用户需求进行交易决策。

## 命令行工具 stock

### 安装

```bash
# uv tool
uv tool install agent-stock
# pip
python -m pip install agent-stock
```

安装完毕后，可以通过 `stock --help` 或 `stock <子命令> --help` 查看帮助。

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

## 常用工作流

- 短线交易选股：参考文档 [references/screen.md](references/screen.md)，为用户完成选股；
- 短线交易决策：参考文档 [references/trade.md](references/trade.md)，为用户完成个股交易决策；
- 用户持仓分析：参考文档 [references/holdings.md](references/holdings.md)，为用户完成持仓分析；