# 데이터 소스 매트릭스 (한국)

## 도구별 ✅/⚠️/❌

| 소스 | 담당 | 호출 한도 | 응답 크기 | 주의사항 |
|---|---|---|---|---|
| **finnhub MCP** | 한국 시총 상위 종목 시세 | ≤55/run | 작음 (≤2KB/호출) | suffix `.KS`(코스피)/`.KQ`(코스닥). 무료 플랜 일부 종목 미지원 가능 |
| **pykrx (Python via Bash)** | 한국 특유 정량 데이터 — 외인/기관 수급, KRX 업종, 공매도, 시총 | 무제한 (KRX 공식) | ≤5KB/스크립트 (사전 정제) | 6 스크립트 — `scripts/`에 위치, `pip install --user pykrx` |
| **alphavantage MCP** | USD/KRW 환율 | 25/day | 작음 | 환율 1건만 호출 |
| **Tavily MCP (subagent)** | 뉴스 + 마감 후 공시 | 6 query | 800단어 이하 (subagent 압축 후) | 한국 매체 위주 — 한경/연합/매경/이데일리/머니투데이 |
| **WebSearch** (Claude 내장) | 국고채 10Y, 미국 야간 SPX 선물, 휴장 교차검증 | 1~3/run | 작음 | 쿼리에 항상 현재 연/월 명시 |

## 사용 금지 도구

- **`yfinance` MCP**: 미국 플러그인과 동일하게 모든 티커 `¥0` 반환 버그 — 호출 자체 생략
- **`finnhub news_sentiment` 메인 직접 호출**: 75KB+ 응답 → 컨텍스트 오염 → news-harvester subagent 경유만 허용

## Tavily 미로드 시 fallback (WebSearch 쿼리 쌍)

news-harvester subagent에 Tavily 도구가 deferred 또는 로드 실패 시 메인이 직접 WebSearch:

- `"코스피 마감 {YYYY-MM-DD} 외국인 매도"` 또는 `"코스피 마감 {YYYY-MM-DD} 외국인 매수"`
- `"코스닥 마감 {YYYY-MM-DD} 종가"` 또는 `"코스닥 마감 {YYYY-MM-DD} 시총"`
- `"한국 증시 {YYYY-MM-DD} 휴장 여부"` (세션 결정 교차검증)
- `"{YYYY-MM-DD} 한국 시장 주요 공시 DART"`
- `"USD/KRW {YYYY-MM-DD} 환율"`

각 쿼리 응답에서 핵심 매체(한경/연합/매경/이데일리/머니투데이)의 결과를 우선 채택.

## 데이터 충돌 해소 우선순위

| 충돌 | 채택 | 비고 |
|---|---|---|
| finnhub 종가 ≠ pykrx 종가 | **pykrx 채택** | KRX가 공식 데이터 |
| Tavily 뉴스 인용 수치 ≠ MCP/pykrx 실시간 | **MCP/pykrx 채택** | 뉴스는 시점 차이 가능성 |
| pykrx 외국인 순매수 ≠ 뉴스 헤드라인 수치 | **pykrx 채택** | 단위 또는 잠정/확정 차이 |
| 외국인 순매수 합 \|값\| > 50,000억원 | Sanity check #4 발동 | 단위 오인 의심(원/억원 혼동) |

해소 내역은 보고서 §13 "데이터 품질 & 소스" 섹션에 기록.

## 응답 크기 보장 (메인 컨텍스트 오염 방지)

- pykrx 스크립트: 각 함수가 사전 정렬·슬라이싱으로 ≤ 5KB
- finnhub `get_quote`: 단일 종목 1KB 미만, 전체 호출 ≤ 50KB
- alphavantage forex: 0.5KB
- Tavily subagent 응답: 800단어 압축 (~6KB)
- WebSearch: ≤ 5KB/쿼리

총 메인 컨텍스트 데이터 누적 < 100KB / 실행. 보고서 본문 작성 + 인과 분석에 충분히 여유.

## 도구별 사용 시점 (SKILL.md Step 3에서 병렬)

```
한 메시지 병렬:
  ├─ Bash × 6 (pykrx 사전 정제)
  ├─ finnhub get_quote × 22~30
  ├─ alphavantage forex × 1
  ├─ WebSearch × 1~3
  └─ Agent → news-harvester subagent × 1
```

→ Tier 2/3 조건부 2차 배치 (finnhub 추가 ≤ 15)
