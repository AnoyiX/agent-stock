---
name: agent-stock
description: 面向 AI Agent 的股市数据命令行技能。根据用户关于股票查询、市场概览、行业热力图、板块涨跌、个股资讯、日K/技术指标、资金流向与代码搜索等诉求触发调用。
author: AnoyiX
version: "0.1.3"
tags:
  - stock
  - cli
  - 股票数据
---

# agent-stock — 股票行情命令行技能

**命令名：** `stock`
**适用场景：** 市场概览（涨跌分布、行业热力图）、个股实时行情、板块涨跌、最新资讯、日 K 与技术指标，以及资金分布/净流向与股票搜索。

## 何时调用（意图触发）

- “查某只股票价格/涨跌幅/市值/成交量/估值” → quote
- “看某只股票相关地域/行业/概念板块涨跌幅” → plate
- “看某只股票最新资讯/新闻摘要” → news
- “看市场涨跌分布/涨跌家数” → chgdiagram
- “看行业板块热力图/热点行业/板块涨跌” → heatmap
- “搜股票代码或名称/模糊搜索” → search
- “看日K/技术指标/EMA/BOLL/KDJ/RSI/近N日数据” → kline
- “看资金分布/主力净流入/散户净流入/每日资金流向” → fundflow

## 参数规范

- symbol
  - A 股：6 位数字，如 600519、000001
  - 港股：5 位数字，如 00700
  - 美股：us.<ticker>，如 us.aapl、us.msft（大小写不敏感）
- market：市场枚举，用于市场类命令
  - 取值：ab｜us｜hk，默认 ab（A 股）


## 命令参数与帮助

- `stock --help` 或 `stock <命令> --help`：查看帮助

### 市场数据

```bash
stock index --market ab             # 大盘主要指数总览
stock chgdiagram --market ab        # 涨跌分布
stock heatmap --market ab           # 行业板块热力图
stock search <keyword>              # 股票搜索
```

### 个股数据

```bash
stock quote <symbols>               # 个股实时行情（支持批量查询）
stock plate <symbol>                # 个股相关板块涨跌幅（地域/行业/概念）
stock news <symbol>                 # 个股最新资讯
stock kline <symbol>                # 日K数据以及技术指标（EMA/BOLL/KDJ/RSI）
stock fundflow <symbol>             # 资金分布与每日主力/散户净流向
```

## 常用示例（映射到命令）

- `stock search 腾讯`
- `stock quote 000001`
- `stock quote 000001,600519`
- `stock quote us.aapl`
- `stock plate 600519`
- `stock news 600519`
- `stock kline 600519 --count 60`
- `stock fundflow 600519`
- `stock chgdiagram --market ab`
- `stock heatmap --market hk`
