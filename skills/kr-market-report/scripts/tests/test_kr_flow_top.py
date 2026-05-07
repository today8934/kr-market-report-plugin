"""Tests for kr_flow_top.py — 종목별 외국인/기관 순매수 Top 5/하위 5."""
import sys
from unittest.mock import patch

import pandas as pd
import pytest

from .conftest import SCRIPTS_DIR


def _fake_purchases_df(symbols, values):
    return pd.DataFrame(
        {"종목명": [f"종목_{s}" for s in symbols], "순매수거래대금": values},
        index=symbols,
    )


def test_kr_flow_top_returns_top5_per_market_per_investor():
    syms = [f"{i:06d}" for i in range(1, 11)]
    vals = [100_00_000_000, -200_00_000_000, 300_00_000_000, -400_00_000_000, 500_00_000_000,
            -600_00_000_000, 700_00_000_000, -800_00_000_000, 900_00_000_000, -1000_00_000_000]
    with patch("pykrx.stock.get_market_net_purchases_of_equities_by_ticker") as mock:
        mock.side_effect = [_fake_purchases_df(syms, vals)] * 4
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import kr_flow_top
            result = kr_flow_top.fetch("20260507")
        finally:
            sys.path.pop(0)
            del sys.modules["kr_flow_top"]

    for market in ["KOSPI", "KOSDAQ"]:
        for investor in ["외국인", "기관"]:
            assert len(result[market][investor]["top_buy"]) == 5
            assert len(result[market][investor]["top_sell"]) == 5
            assert result[market][investor]["top_buy"][0]["순매수"] > 0
            assert result[market][investor]["top_sell"][0]["순매수"] < 0
