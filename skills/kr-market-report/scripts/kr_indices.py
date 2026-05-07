"""KOSPI / KOSDAQ 인덱스 OHLCV + 거래대금 fetcher.

Usage:
    python3 kr_indices.py YYYYMMDD

Output (stdout JSON):
    {
      "KOSPI":  {"close": float, "dp": float, "value_krw_trillion": float},
      "KOSDAQ": {"close": float, "dp": float, "value_krw_trillion": float}
    }
"""
import json
import sys

from pykrx import stock


def fetch(date: str) -> dict:
    """Fetch KOSPI/KOSDAQ index OHLCV for given YYYYMMDD."""
    out = {}
    for name, code in [("KOSPI", "1001"), ("KOSDAQ", "2001")]:
        df = stock.get_index_ohlcv_by_date(date, date, code)
        row = df.iloc[0]
        prev_close = row["시가"]
        dp = (row["종가"] - prev_close) / prev_close * 100 if prev_close else 0.0
        out[name] = {
            "close": float(row["종가"]),
            "dp": round(dp, 2),
            "value_krw_trillion": round(row["거래대금"] / 1e12, 2),
        }
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 kr_indices.py YYYYMMDD", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch(sys.argv[1]), ensure_ascii=False))
