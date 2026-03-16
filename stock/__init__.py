"""agent-stock: Stock CLI via reverse-engineered API."""

try:
    from importlib.metadata import version

    __version__ = version("agent-stock")
except Exception:
    __version__ = "0.0.0"
