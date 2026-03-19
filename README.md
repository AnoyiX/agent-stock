# agent-stock

[![CI](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/AnoyiX/agent-stock/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/agent-stock.svg)](https://pypi.org/project/agent-stock/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/agent-stock/)

面向 AI Agent 的股市数据命令行工具，提供市场概览、个股行情、板块涨跌、技术指标与资金流向等信息。

## 安装

```bash
# pipx（推荐，全局安装）
pipx install agent-stock

# uv tool
uv tool install agent-stock

# pip（虚拟环境或本地环境）
python -m pip install agent-stock
```

### 升级

升级到最新版本：

```bash
pipx upgrade agent-stock
uv tool upgrade agent-stock
python -m pip install -U agent-stock
```

### 环境要求

- Python ≥ 3.10
- 运行环境可访问外部网络（用于获取行情与资讯数据）

## 快速开始

```bash
# 常用查询
stock quote 000001
stock plate 000001
stock news 000001

# 技术分析与市场
stock kline 000001
stock fundflow 000001
stock chgdiagram --market ab
stock heatmap --market ab

# 帮助与版本
stock --help
stock quote --help
stock -v
```

## 命令

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

### 全局选项

| 选项           | 类型/范围     | 默认值 | 说明                     |
| -------------- | ------------- | ------ | ------------------------ |
| -v, --version  | —             | —      | 显示版本信息             |
| -d, --verbose  | Flag          | —      | 启用调试日志             |
| -i, --interval | 整数 [1,3600] | 10     | dashboard 刷新间隔（秒） |
| --no-color     | Flag          | —      | 禁用颜色输出             |


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
