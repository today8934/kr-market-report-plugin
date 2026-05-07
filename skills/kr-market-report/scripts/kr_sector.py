"""KRX 21개 업종 인덱스 변동률 정렬 + 5그룹 평균.

Usage:
    python3 kr_sector.py YYYYMMDD

Output (stdout JSON):
    {
      "sectors": [{"name": "...", "code": "...", "dp": float}, ... 21개 dp 내림차순],
      "groups":  {"시클리컬": float_avg, "방어": float_avg, ...}
    }
"""
import json
import sys

from pykrx import stock


SECTORS = [
    ("음식료품", "1010"), ("섬유의복", "1020"), ("종이목재", "1030"),
    ("화학", "1040"), ("의약품", "1050"), ("비금속광물", "1060"),
    ("철강금속", "1070"), ("기계", "1080"), ("전기전자", "1090"),
    ("의료정밀", "1100"), ("운수장비", "1110"), ("유통업", "1120"),
    ("전기가스", "1130"), ("건설업", "1140"), ("운수창고", "1150"),
    ("통신업", "1160"), ("금융업", "1170"), ("은행", "1180"),
    ("증권", "1190"), ("보험", "1200"), ("서비스업", "1210"),
]

GROUPS = {
    "시클리컬": ["전기전자", "화학", "철강금속", "운수장비", "건설업"],
    "방어":     ["통신업", "전기가스", "의약품", "음식료품"],
    "금융":     ["금융업", "보험", "증권", "은행"],
    "성장":     ["의료정밀", "비금속광물"],
    "인프라":   ["운수창고", "유통업", "서비스업"],
}


def fetch(date: str) -> dict:
    sectors = []
    for name, code in SECTORS:
        df = stock.get_index_ohlcv_by_date(date, date, code)
        row = df.iloc[0]
        prev = row["시가"]
        dp = (row["종가"] - prev) / prev * 100 if prev else 0.0
        sectors.append({"name": name, "code": code, "dp": round(dp, 2)})
    sectors.sort(key=lambda s: s["dp"], reverse=True)

    name_to_dp = {s["name"]: s["dp"] for s in sectors}
    groups = {}
    for gname, members in GROUPS.items():
        valid = [name_to_dp[m] for m in members if m in name_to_dp]
        groups[gname] = round(sum(valid) / len(valid), 2) if valid else None

    return {"sectors": sectors, "groups": groups}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 kr_sector.py YYYYMMDD", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(fetch(sys.argv[1]), ensure_ascii=False))
