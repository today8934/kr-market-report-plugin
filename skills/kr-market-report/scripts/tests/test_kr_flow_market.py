"""Tests for kr_flow_market.py — 시장별 외인/기관/개인 순매수."""
import sys
from unittest.mock import patch

import pytest

from .conftest import SCRIPTS_DIR


def test_kr_flow_market_returns_both_markets(fake_investor_value):
    """KOSPI/KOSDAQ 두 시장 모두 외국인/기관/개인 순매수 반환."""
    with patch("pykrx.stock.get_market_trading_value_by_investor") as mock_inv:
        mock_inv.side_effect = [
            fake_investor_value(foreign=-3_142_00_000_000, institution=2_876_00_000_000, individual=266_00_000_000),
            fake_investor_value(foreign=428_00_000_000, institution=-312_00_000_000, individual=-116_00_000_000),
        ]
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import kr_flow_market
            result = kr_flow_market.fetch("20260507")
        finally:
            sys.path.pop(0)
            del sys.modules["kr_flow_market"]

    assert "KOSPI" in result and "KOSDAQ" in result
    assert result["KOSPI"]["외국인"] == -3142
    assert result["KOSPI"]["기관"] == 2876
    assert result["KOSPI"]["개인"] == 266
    assert result["KOSDAQ"]["외국인"] == 428
