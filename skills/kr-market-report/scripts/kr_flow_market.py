"""시장별 외국인/기관/개인 순매수 (단위: 억원).

Usage:
    python3 kr_flow_market.py YYYYMMDD

Output (stdout JSON):
    {
      "KOSPI":  {"외국인": int, "기관": int, "개인": int},
      "KOSDAQ": {"외국인": int, "기관": int, "개인": int}
    }
"""
import json
import sys

from pykrx import stock


def fetch(date: str) -> dict:
    out = {}
    for market in ["KOSPI", "KOSDAQ"]:
        df = stock.get_market_trading_value_by_investor(date, date, market)
        out[market] = {
            "외국인": int(df.loc["외국인합계", "순매수"] / 1e8),
            "기관":   int(df.loc["기관합계", "순매수"] / 1e8),
            "개인":   int(df.loc["개인", "순매수"] / 1e8),
        }
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 kr_flow_market.py YYYYMMDD", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch(sys.argv[1]), ensure_ascii=False))
