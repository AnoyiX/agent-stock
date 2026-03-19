# agent-stock

[![CI](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/agent-stock.svg)](https://pypi.org/project/agent-stock/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/agent-stock/)

面向 AI Agent 的股市数据命令行工具，提供市场概览、个股行情、板块涨跌、技术指标与资金流向等信息。

## 安装

```bash
# pipx
pipx install agent-stock  # 安装
pipx upgrade agent-stock  # 升级

# uv tool
uv tool install agent-stock  # 安装
uv tool upgrade agent-stock  # 升级

# pip
python -m pip install agent-stock     # 安装
python -m pip install -U agent-stock  # 升级
```

## 快速开始

```bash
# 市场数据
stock search 腾讯
stock chgdiagram --market ab
stock heatmap --market ab

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

## 命令

全局使用 `--help` 获取命令帮助，或针对特定命令添加 `--help` 获取详细参数说明，示例：`stock --help`。

### 市场数据

```bash
stock index --market ab             # 大盘主要指数总览
stock chgdiagram --market ab        # 涨跌分布
stock heatmap --market ab           # 行业板块热力图
stock search <keyword>              # 股票搜索
```

### 个股数据

```bash
stock quote <symbol>                # 个股实时行情
stock plate <symbol>                # 个股相关板块涨跌幅（地域/行业/概念）
stock news <symbol>                 # 个股最新资讯
stock kline <symbol>                # 日K数据以及技术指标（EMA/BOLL/KDJ/RSI）
stock fundflow <symbol>             # 资金分布与每日主力/散户净流向
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
```

## License

Apache-2.0
