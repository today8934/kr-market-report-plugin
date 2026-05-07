"""Tests for kr_movers.py — 시총 상위 30 OHLCV + 외국인/기관 순매수 join."""
import sys
from unittest.mock import patch

import pandas as pd
import pytest

from .conftest import SCRIPTS_DIR


def test_kr_movers_returns_30_rows():
    syms = [f"{i:06d}" for i in range(1, 51)]
    cap = pd.DataFrame({"시가총액": list(range(50, 0, -1))}, index=syms)
    ohlcv = pd.DataFrame(
        {
            "시가":   [100] * 50,
            "종가":   [102] * 50,
            "거래량": [1_000_000] * 50,
            "거래대금": [102_000_000] * 50,
        },
        index=syms,
    )
    foreign = pd.DataFrame({"순매수거래대금": [100_00_000_000] * 50}, index=syms)
    institution = pd.DataFrame({"순매수거래대금": [50_00_000_000] * 50}, index=syms)

    with patch("pykrx.stock.get_market_cap_by_date", return_value=cap), \
         patch("pykrx.stock.get_market_ohlcv_by_ticker", return_value=ohlcv), \
         patch("pykrx.stock.get_market_net_purchases_of_equities_by_ticker") as mock_pur:
        mock_pur.side_effect = [foreign, institution] * 2
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import kr_movers
            result = kr_movers.fetch("20260507")
        finally:
            sys.path.pop(0)
            del sys.modules["kr_movers"]

    assert "movers" in result
    assert len(result["movers"]) == 30
    sample = result["movers"][0]
    assert "ticker" in sample and "close" in sample and "dp" in sample
    assert "외국인순매수" in sample and "기관순매수" in sample
