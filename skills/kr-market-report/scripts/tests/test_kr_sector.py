"""Tests for kr_sector.py — KRX 21개 업종 인덱스 변동률 정렬."""
import sys
from unittest.mock import patch

import pandas as pd
import pytest

from .conftest import SCRIPTS_DIR


def _idx_df(close, prev):
    return pd.DataFrame({"시가": [prev], "종가": [close]}, index=pd.to_datetime(["20260507"]))


def test_kr_sector_returns_21_sectors():
    side_effects = [_idx_df(close=100 + i, prev=100) for i in range(21)]
    with patch("pykrx.stock.get_index_ohlcv_by_date") as mock:
        mock.side_effect = side_effects
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import kr_sector
            result = kr_sector.fetch("20260507")
        finally:
            sys.path.pop(0)
            del sys.modules["kr_sector"]

    assert "sectors" in result
    assert len(result["sectors"]) == 21
    dps = [s["dp"] for s in result["sectors"]]
    assert dps == sorted(dps, reverse=True)
    assert "groups" in result
    assert set(result["groups"].keys()) >= {"시클리컬", "방어", "금융", "성장", "인프라"}
