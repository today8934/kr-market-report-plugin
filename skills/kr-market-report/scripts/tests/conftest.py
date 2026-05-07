"""Pytest fixtures for kr-data-harvester scripts.

KRX 네트워크 호출을 mock으로 대체해 결정적·오프라인 단위 테스트를 가능하게 함.
실제 KRX 호출은 -m integration 마커가 붙은 테스트만.
"""
import json
import subprocess
import sys
from pathlib import Path
import pandas as pd
import pytest


SCRIPTS_DIR = Path(__file__).parent.parent  # scripts/


def run_script(name: str, *args: str) -> dict:
    """Execute a script and parse its stdout JSON."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / name), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.fixture
def fake_index_ohlcv():
    """단일 날짜 KOSPI/KOSDAQ 인덱스 OHLCV mock."""
    def make(close: float, dp_pct: float, value_won: int):
        return pd.DataFrame(
            {
                "시가": [close * (1 - dp_pct / 100)],
                "고가": [close * 1.005],
                "저가": [close * 0.995],
                "종가": [close],
                "거래량": [1234567890],
                "거래대금": [value_won],
            },
            index=pd.to_datetime(["20260507"]),
        )
    return make


@pytest.fixture
def fake_investor_value():
    """get_market_trading_value_by_investor mock."""
    def make(foreign: int, institution: int, individual: int):
        idx = ["외국인합계", "기관합계", "개인", "기타"]
        return pd.DataFrame(
            {
                "매도": [0, 0, 0, 0],
                "매수": [0, 0, 0, 0],
                "순매수": [foreign, institution, individual, 0],
            },
            index=idx,
        )
    return make
