"""시총 상위 30 종목의 OHLCV + 외국인/기관 순매수 join.

Usage:
    python3 kr_movers.py YYYYMMDD

Output (stdout JSON):
    {
      "movers": [
        {"ticker": "...", "market": "KOSPI|KOSDAQ", "close": float, "dp": float,
         "value_krw_billion": float, "외국인순매수": int, "기관순매수": int},
        ... (시총 내림차순 30행)
      ]
    }
"""
import json
import sys

import pandas as pd
from pykrx import stock


def _net_by_ticker(date, market, investor):
    return stock.get_market_net_purchases_of_equities_by_ticker(date, date, market, investor)


def fetch(date: str) -> dict:
    cap_df = stock.get_market_cap_by_date(date, date).sort_values("시가총액", ascending=False)
    top30 = cap_df.head(30)
    tickers = top30.index.tolist()

    ohlcv = stock.get_market_ohlcv_by_ticker(date)
    foreign_kospi = _net_by_ticker(date, "KOSPI", "외국인")
    inst_kospi = _net_by_ticker(date, "KOSPI", "기관")
    foreign_kosdaq = _net_by_ticker(date, "KOSDAQ", "외국인")
    inst_kosdaq = _net_by_ticker(date, "KOSDAQ", "기관")

    movers = []
    for t in tickers:
        if t not in ohlcv.index:
            continue
        row = ohlcv.loc[t]
        prev = row["시가"]
        dp = (row["종가"] - prev) / prev * 100 if prev else 0.0
        market = "KOSPI" if t in foreign_kospi.index else "KOSDAQ"
        f_df = foreign_kospi if market == "KOSPI" else foreign_kosdaq
        i_df = inst_kospi if market == "KOSPI" else inst_kosdaq
        movers.append({
            "ticker": t,
            "market": market,
            "close": float(row["종가"]),
            "dp": round(dp, 2),
            "value_krw_billion": round(row["거래대금"] / 1e9, 2),
            "외국인순매수": int(f_df.loc[t, "순매수거래대금"] / 1e8) if t in f_df.index else 0,
            "기관순매수":   int(i_df.loc[t, "순매수거래대금"] / 1e8) if t in i_df.index else 0,
        })

    return {"movers": movers}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 kr_movers.py YYYYMMDD", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch(sys.argv[1]), ensure_ascii=False))
