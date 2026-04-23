from __future__ import annotations

import os

from stock.commands.kline import get_kline_data

os.environ.setdefault("OUTPUT", "rich")


data = get_kline_data('sh000001', count=30)


print(data)