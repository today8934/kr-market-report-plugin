"""공매도 잔고 비중 — 전일 대비 ±5%p 변동 종목만.

Usage:
    python3 kr_short.py YYYYMMDD PREV_YYYYMMDD

Output (stdout JSON):
    {
      "significant": [
        {"ticker": "...", "current": float, "prev": float, "delta": float},
        ...
      ]
    }
"""
import json
import sys

from pykrx import stock


THRESHOLD_PP = 5.0


def fetch(date: str, prev_date: str) -> dict:
    today = stock.get_shorting_balance_by_date(date, date)
    yesterday = stock.get_shorting_balance_by_date(prev_date, prev_date)

    sig = []
    common = today.index.intersection(yesterday.index)
    for t in common:
        cur = float(today.loc[t, "공매도잔고비율"])
        prev = float(yesterday.loc[t, "공매도잔고비율"])
        delta = cur - prev
        if abs(delta) >= THRESHOLD_PP:
            sig.append({"ticker": t, "current": cur, "prev": prev, "delta": round(delta, 2)})

    sig.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {"significant": sig[:20]}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 kr_short.py YYYYMMDD PREV_YYYYMMDD", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch(sys.argv[1], sys.argv[2]), ensure_ascii=False))
