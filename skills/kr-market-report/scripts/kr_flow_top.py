"""종목별 외국인/기관 순매수 Top 5 / 하위 5 (단위: 억원).

Usage:
    python3 kr_flow_top.py YYYYMMDD

Output (stdout JSON):
    {
      "KOSPI": {
        "외국인": {"top_buy": [...5], "top_sell": [...5]},
        "기관":   {"top_buy": [...5], "top_sell": [...5]}
      },
      "KOSDAQ": { ... }
    }
"""
import json
import sys

from pykrx import stock


def _slice(df, n=5):
    df = df.sort_values("순매수거래대금", ascending=False)
    top_buy = df.head(n)
    top_sell = df.tail(n).iloc[::-1]
    return {
        "top_buy": [
            {"종목": r["종목명"], "ticker": idx, "순매수": int(r["순매수거래대금"] / 1e8)}
            for idx, r in top_buy.iterrows()
        ],
        "top_sell": [
            {"종목": r["종목명"], "ticker": idx, "순매수": int(r["순매수거래대금"] / 1e8)}
            for idx, r in top_sell.iterrows()
        ],
    }


def fetch(date: str) -> dict:
    out = {}
    for market in ["KOSPI", "KOSDAQ"]:
        out[market] = {}
        for investor in ["외국인", "기관"]:
            df = stock.get_market_net_purchases_of_equities_by_ticker(date, date, market, investor)
            out[market][investor] = _slice(df)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 kr_flow_top.py YYYYMMDD", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch(sys.argv[1]), ensure_ascii=False))
