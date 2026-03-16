# agent-stock

[![CI](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/agent-stock.svg)](https://pypi.org/project/agent-stock/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/agent-stock/)

股市数据命令行工具，支持个股行情、相关板块涨跌幅与最新资讯查询。

## 功能特性

- 🎯 **个股行情**：按股票代码查询实时价格、涨跌幅、成交额、K 线
- 🧭 **相关板块涨跌幅**：按股票代码查看地域、行业、概念板块表现
- 📰 **个股最新资讯**：按股票代码查看最新资讯摘要

## 安装

```bash
# 推荐：uv tool（快速、隔离环境）
uv tool install agent-stock

# 或者：pipx
pipx install agent-stock
```

升级到最新版本：

```bash
uv tool upgrade agent-stock
# 或：pipx upgrade agent-stock
```

## 快速开始

```bash
stock quote 000001
stock plate 000001
stock news 000001
```

## 开发

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# Lint
uv run ruff check .

# 安装当前目录源码，并暴露 `stock` 命令
uv tool install --from . agent-stock

# 强制升级
uv tool install --from . agent-stock --force --reinstall --refresh --no-cache

# 卸载
uv tool uninstall agent-stock

# 调试
uv run python -m stock quote 000001
uv run python -m stock plate 000001
uv run python -m stock news 000001
```

## License

Apache-2.0
