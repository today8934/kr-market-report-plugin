# kr-data-harvester (pykrx Python 스크립트 6종)

실제 코드는 `scripts/` 디렉토리의 6개 `.py` 파일. 이 문서는 SKILL.md가 호출 시 참조할 contract/doc.

## 호출 패턴 (메인 세션)

각 스크립트는 standalone Python으로 실행. 메인 세션 SKILL.md Step 3에서 다음 패턴 사용:

**옵션 A (권장)**: 메인이 Read tool로 스크립트 코드를 컨텍스트에 가져온 뒤 인라인 실행:
```bash
# 1. Read skills/kr-market-report/scripts/kr_indices.py
# 2. Bash로 인라인 실행
python3 -c "<읽은 코드 본문>" 20260507
```

**옵션 B**: 절대경로가 알려진 경우 (로컬 dev):
```bash
python3 /Users/musinsa/workspace/kr-market-report-plugin/skills/kr-market-report/scripts/kr_indices.py 20260507
```

플러그인 설치 후 Claude Code가 SKILL_DIR을 알지 못하는 환경에서는 옵션 A 사용.

## 6개 스크립트 contract

### 1. `kr_indices.py`
- **책임**: KOSPI / KOSDAQ 인덱스 OHLCV + 거래대금
- **argv**: `YYYYMMDD`
- **반환 schema**:
  ```json
  {
    "KOSPI":  {"close": float, "dp": float, "value_krw_trillion": float},
    "KOSDAQ": {"close": float, "dp": float, "value_krw_trillion": float}
  }
  ```
- **응답 크기**: ~200B
- **사용 pykrx**: `stock.get_index_ohlcv_by_date(date, date, '1001')` (KOSPI), `('2001')` (KOSDAQ)

> **Note**: v0.1 dp 계산은 시가 대비 (간략). 정확한 전일 종가 대비는 v0.2에서 추가 fetch로 보정.

### 2. `kr_flow_market.py`
- **책임**: 시장별 외국인/기관/개인 순매수 (단위: 억원)
- **argv**: `YYYYMMDD`
- **반환 schema**:
  ```json
  {
    "KOSPI":  {"외국인": int, "기관": int, "개인": int},
    "KOSDAQ": {"외국인": int, "기관": int, "개인": int}
  }
  ```
- **응답 크기**: ~200B
- **사용 pykrx**: `stock.get_market_trading_value_by_investor(date, date, market)` × 2 (KOSPI/KOSDAQ)

### 3. `kr_flow_top.py`
- **책임**: KOSPI/KOSDAQ × 외국인/기관 × 매수/매도 Top 5 = 8 슬라이스
- **argv**: `YYYYMMDD`
- **반환 schema**:
  ```json
  {
    "KOSPI": {
      "외국인": {"top_buy":  [{"종목": str, "ticker": str, "순매수": int}, ...5개],
                 "top_sell": [{"종목": str, "ticker": str, "순매수": int}, ...5개]},
      "기관":   {"top_buy":  [...5], "top_sell": [...5]}
    },
    "KOSDAQ": {...동일 구조...}
  }
  ```
- **응답 크기**: ~3KB
- **사용 pykrx**: `stock.get_market_net_purchases_of_equities_by_ticker(date, date, market, investor)` × 4

### 4. `kr_sector.py`
- **책임**: KRX 21개 업종 인덱스 변동률 정렬 + 5그룹 평균
- **argv**: `YYYYMMDD`
- **반환 schema**:
  ```json
  {
    "sectors": [{"name": str, "code": str, "dp": float}, ... 21개 dp 내림차순],
    "groups":  {"시클리컬": float, "방어": float, "금융": float, "성장": float, "인프라": float}
  }
  ```
- **응답 크기**: ~2KB
- **사용 pykrx**: `stock.get_index_ohlcv_by_date(date, date, code)` × 21 (KOSPI 업종 코드 1010-1210)

### 5. `kr_movers.py`
- **책임**: 시총 상위 30 종목 OHLCV + 외국인/기관 순매수 join
- **argv**: `YYYYMMDD`
- **반환 schema**:
  ```json
  {
    "movers": [
      {"ticker": str, "market": "KOSPI"|"KOSDAQ", "close": float, "dp": float,
       "value_krw_billion": float, "외국인순매수": int, "기관순매수": int},
      ... (시총 내림차순 30행)
    ]
  }
  ```
- **응답 크기**: ~5KB
- **사용 pykrx**: `get_market_cap_by_date` + `get_market_ohlcv_by_ticker` + 4× `get_market_net_purchases_of_equities_by_ticker`

### 6. `kr_short.py`
- **책임**: 공매도 잔고 비중 — **전일 대비** ±5%p 이상 변동 종목 (최대 20)
- **argv**: `YYYYMMDD PREV_YYYYMMDD`
- **반환 schema**:
  ```json
  {
    "significant": [
      {"ticker": str, "current": float, "prev": float, "delta": float},
      ... (절댓값 큰 순, 최대 20)
    ]
  }
  ```
- **응답 크기**: ~1KB
- **사용 pykrx**: `stock.get_shorting_balance_by_date(date, date)` × 2 (오늘/전일)

## 응답 크기 보장 (메인 컨텍스트 오염 방지)

각 스크립트는 사전 정렬·슬라이싱으로 ≤ 5KB. 6 스크립트 합산 ≤ 12KB. 메인 컨텍스트가 시장 전체 종목 데이터(~200KB)로 오염되지 않음.

## 호출 순서 (SKILL.md Step 3 한 메시지 병렬)

```
한 메시지에서:
  Bash × 6 — kr_indices, kr_flow_market, kr_flow_top, kr_sector, kr_movers, kr_short
  finnhub × 22~30 — Tier 1 시총 상위 + 인덱스 ETF
  alphavantage × 1 — USD/KRW
  WebSearch × 1~3 — 국고채/야간선물
  Agent → news-harvester subagent × 1
```

## 단위 테스트

`scripts/tests/test_*.py` — `pytest -m "not integration"`로 실행.

mock 기반 unit test (네트워크 무의존):
```bash
cd /Users/musinsa/workspace/kr-market-report-plugin
python3 -m pytest skills/kr-market-report/scripts/tests/ -v -m "not integration"
```
Expected: 6 passed.

## 통합 smoke 테스트

```bash
python3 -m pytest skills/kr-market-report/scripts/tests/ -v -m integration
```
실제 KRX 호출. 셋업 검증 시 1회 실행 (Task 23).

## 의존성

- Python 3.9+
- `pykrx` ≥ 1.0.51 (`pip install --user pykrx`)
- `pandas` (pykrx의 transitive dep, 자동 설치됨)

## 알려진 제약

- pykrx는 KRX 정보데이터시스템에 직접 호출 → 네트워크 필수
- KRX 서버 일시 응답 지연 시 함수가 timeout 또는 빈 DataFrame 반환 가능 → SKILL.md Step 5 sanity check #3에서 처리
- 함수 시그니처는 pykrx 버전에 따라 미묘한 차이 가능 — Task 23 integration test에서 실 KRX 호출로 검증

## v0.2.0 후보

- pykrx → KIS Open API 마이그레이션 옵션 (실시간 호가 추가)
- 시총 상위 30 → 동적 결정 (`get_market_cap_by_date` 매번 호출)
- 공매도 임계값 ±5%p → 사용자 피드백 반영해 ±3%p 검토
- 프로그램 매매 (차익/비차익) 별도 스크립트 추가 (옵션 만기일 활성)
