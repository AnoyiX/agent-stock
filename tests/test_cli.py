from click.testing import CliRunner

from stock.cli import cli

runner = CliRunner()


def test_help_lists_planned_commands():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "quote" in result.output
    assert "plate" in result.output
    assert "news" in result.output
    assert "kline" in result.output
    assert "fundflow" in result.output
    assert "chgdiagram" in result.output
    assert "heatmap" in result.output
    assert "search" in result.output
    assert "index" in result.output


def test_quote_help_supports_symbol_argument():
    result = runner.invoke(cli, ["quote", "--help"])
    assert result.exit_code == 0
    assert "symbol" in result.output


def test_plate_help_supports_symbol_argument():
    result = runner.invoke(cli, ["plate", "--help"])
    assert result.exit_code == 0
    assert "symbol" in result.output


def test_news_help_supports_symbol_argument():
    result = runner.invoke(cli, ["news", "--help"])
    assert result.exit_code == 0
    assert "symbol" in result.output


def test_history_help_supports_range_option():
    result = runner.invoke(cli, ["history", "--help"])
    assert result.exit_code == 0
    assert "--range" in result.output


def test_kline_help_supports_code_argument():
    result = runner.invoke(cli, ["kline", "--help"])
    assert result.exit_code == 0
    assert "CODE" in result.output


def test_fundflow_help_supports_symbol_argument():
    result = runner.invoke(cli, ["fundflow", "--help"])
    assert result.exit_code == 0
    assert "symbol" in result.output


def test_chgdiagram_help_supports_market_option():
    result = runner.invoke(cli, ["chgdiagram", "--help"])
    assert result.exit_code == 0
    assert "--market" in result.output


def test_heatmap_help_supports_market_option():
    result = runner.invoke(cli, ["heatmap", "--help"])
    assert result.exit_code == 0
    assert "--market" in result.output


def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "stock" in result.output.lower()


def test_short_version():
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "stock" in result.output.lower()
