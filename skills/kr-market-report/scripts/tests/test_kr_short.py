"""Tests for kr_short.py — 공매도 잔고 비중 ±5%p 변동 종목 (전일 대비)."""
import sys
from unittest.mock import patch

import pandas as pd
import pytest

from .conftest import SCRIPTS_DIR


def test_kr_short_returns_only_significant_changes():
    today = pd.DataFrame({"공매도잔고비율": [3.0, 12.0, 6.0]}, index=["A", "B", "C"])
    yesterday = pd.DataFrame({"공매도잔고비율": [3.1, 5.0, 5.5]}, index=["A", "B", "C"])
    with patch("pykrx.stock.get_shorting_balance_by_date") as mock:
        mock.side_effect = [today, yesterday]
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import kr_short
            result = kr_short.fetch("20260507", "20260502")
        finally:
            sys.path.pop(0)
            del sys.modules["kr_short"]

    assert "significant" in result
    tickers = [s["ticker"] for s in result["significant"]]
    assert "B" in tickers
    assert "A" not in tickers and "C" not in tickers
