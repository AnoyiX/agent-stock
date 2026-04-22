---
name: agent-stock
description: AI 量化交易技能包，用于获取股市实时数据、选股、交易决策、持仓分析等。
author: AnoyiX
version: "0.2.4"
tags:
  - Stock
  - 股票数据
  - 选股
  - 交易决策
  - 持仓分析
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

### 源码地址

[https://github.com/anoyix/agent-stock](https://github.com/anoyix/agent-stock)

## 常用工作流

- 短线交易选股：参考文档 [references/screen.md](references/screen.md)，为用户完成选股；
- 短线交易决策：参考文档 [references/trade.md](references/trade.md)，为用户完成个股交易决策；
- 用户持仓分析：参考文档 [references/holdings.md](references/holdings.md)，为用户完成持仓分析；