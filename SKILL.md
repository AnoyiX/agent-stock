---
name: agent-stock
description: 用于股票行情查询与分析的命令行技能。用户提到 stock 命令、股票代码、最新资讯、市场概览、K 线或配置管理时调用。
author: AnoyiX
version: "0.1.2"
tags:
  - stock
  - 股票
  - cli
  - 行情
  - kline
---

# agent-stock — 股票行情命令行技能

**命令名：** `stock`
**适用场景：** 查询股票实时行情、个股相关板块涨跌幅、个股最新资讯、市场快照、历史数据、日 K 技术指标，以及查看/设置默认市场配置。

## 何时调用

- 用户要求“查某只股票价格/涨跌幅/市值”
- 用户要求“看某只股票相关地域/行业/概念板块涨跌幅”
- 用户要求“看某只股票最新资讯/新闻摘要”
- 用户要求“看市场总览/指数表现”
- 用户要求“搜股票代码或名称”
- 用户要求“查历史数据（1d/5d/1m/3m/6m/1y/5y）”
- 用户要求“看日 K + 技术指标（EMA/BOLL/KDJ/RSI）”
- 用户要求“查看或修改 agent-stock 配置（market）”

## 全局参数

- `-v, --version`：显示版本

## 命令总览

| 命令                   | 说明                   | 关键参数 |
| ---------------------- | ---------------------- | -------- |
| `stock quote <symbol>` | 查看单只股票实时行情   |          |
| `stock plate <symbol>` | 查看个股相关板块涨跌幅 |          |
| `stock news <symbol>`  | 查看个股最新资讯       |          |
| `stock kline <symbol>` | 查看日 K 线 + 技术指标 |          |

## 常用示例

- `stock quote 600519`
- `stock plate 600519`
- `stock news 600519`
- `stock quote 00700`
- `stock quote us.aapl`
- `stock kline 600519`
