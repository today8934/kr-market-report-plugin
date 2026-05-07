"""Tests for kr_indices.py — KOSPI/KOSDAQ index OHLCV fetcher."""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from .conftest import SCRIPTS_DIR


def test_kr_indices_returns_kospi_and_kosdaq(fake_index_ohlcv):
    """KOSPI ('1001')와 KOSDAQ ('2001') 인덱스 모두 반환."""
    with patch("pykrx.stock.get_index_ohlcv_by_date") as mock_idx:
        mock_idx.side_effect = [
            fake_index_ohlcv(close=2612.45, dp_pct=-1.23, value_won=9_800_000_000_000),
            fake_index_ohlcv(close=845.22, dp_pct=-0.45, value_won=5_200_000_000_000),
        ]
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import kr_indices
            result = kr_indices.fetch("20260507")
        finally:
            sys.path.pop(0)
            del sys.modules["kr_indices"]

    assert "KOSPI" in result
    assert "KOSDAQ" in result
    assert result["KOSPI"]["close"] == pytest.approx(2612.45)
    assert result["KOSDAQ"]["close"] == pytest.approx(845.22)
    assert "value_krw_trillion" in result["KOSPI"]
    assert result["KOSPI"]["value_krw_trillion"] == pytest.approx(9.8, rel=0.01)


@pytest.mark.integration
def test_kr_indices_real_krx():
    """실제 KRX 호출 (네트워크 의존 — pytest -m integration 시에만)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "kr_indices.py"), "20260430"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    assert "KOSPI" in data and "KOSDAQ" in data
    assert isinstance(data["KOSPI"]["close"], (int, float))
