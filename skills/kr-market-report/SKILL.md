---
name: kr-market-report
description: 직전 마감된 한국 정규장(코스피+코스닥) 1세션을 finnhub·pykrx·Tavily·alphavantage로 동시 수집·분석해 한국어 마크다운 브리핑 보고서를 생성합니다. 사용자가 "한국주식", "코스피 마감", "코스닥 정리", "오늘 코스피 어땠어", "어제 한국장 어땠어", "한국 증시 브리핑", "수급 정리", "외국인 매도세", "한국장 마감 보고서", "코스피 회고" 같은 직·간접 표현을 쓸 때 반드시 이 skill을 실행하세요. 미국이 아닌 한국 증시 한 세션에 대한 회고 보고서가 필요한 모든 상황에서 트리거합니다. 단순 시세 조회가 아니라 외국인/기관 수급, KRX 업종 로테이션, 환율-수급 인과를 엮어 설명하는 종합 리포트를 만듭니다.
---

# Korean Market Report

직전 마감된 한국 정규장(코스피+코스닥) 1세션을 회고하는 한국어 마크다운 보고서를 만듭니다.

## 왜 이 skill이 필요한가

한국 투자자가 코스피/코스닥 마감 후(저녁) 또는 다음날 개장 전(아침)에 알아야 할 것:
- 코스피·코스닥 종가만이 아니라 **외국인/기관/개인 수급 양상**
- 그 수급이 **왜 그렇게 움직였는지** (환율 변동? 미국 영향? 한은 발표? 실적?)
- 한국 시장 특유 **테마 회전** (반도체·2차전지·조선·방산·바이오·게임·엔터)
- 한국 밸류체인과 얽힌 연쇄 효과

지수 → 수급 → 섹터 → 매크로/지정학 이벤트의 인과를 연결해야 실전에 쓸 수 있는 브리핑이 됩니다. 외국인 수급은 한국 시장 흐름의 가장 큰 변수라 USP로 다룹니다.

## 참조 문서 (Progressive disclosure)

자세한 내용은 필요할 때만 `Read`로 로드. 메인 세션 context를 아끼기 위한 분할.

- `references/setup-wizard-kr.md` — preflight + Setup Wizard 8단계 + 24h 캐싱
- `references/data-sources-kr.md` — 도구별 ✅/⚠️/❌ + 충돌 해소 우선순위
- `references/theme-tickers-kr.md` — 3-Tier 한국 티커 유니버스
- `references/kr-data-harvester.md` — pykrx 6 스크립트 contract (실제 코드는 `scripts/*.py`)
- `references/flow-label-rules.md` — 수급/섹터 라벨 13개 자동 결정 룰
- `references/news-harvester-kr.md` — news-harvester subagent 프롬프트 (한국 매체)
- `references/readability-pass-kr.md` — readability-pass subagent 프롬프트 (한국 용어집 연계)
- `references/report-template-kr.md` — 보고서 템플릿 (YAML + 13 섹션)
- `references/glossary-kr.md` — readability-pass 전용 한국 시장 용어집

## 출력 위치

기본 경로: `~/workspace/wooksang-marketplace-documents/kr-market-report/YYYY-MM-DD.md` (오늘 한국 날짜 기준).

wooksang-marketplace 플러그인들이 생성한 모든 문서는 `~/workspace/wooksang-marketplace-documents/<plugin>/` 하위로 모입니다. 이 skill은 `kr-market-report` 디렉토리를 사용합니다.

### 경로 결정 절차
1. `~/.claude/data/kr-market-report/config.json`이 있고 `output_dir` 필드가 존재하면 그 값 우선 사용 (사용자가 명시적으로 별도 위치를 원하는 경우만)
2. 없으면 기본 경로 사용
3. 디렉토리가 없으면 먼저 생성 (`mkdir -p ~/workspace/wooksang-marketplace-documents/kr-market-report`)
4. 같은 날짜 파일이 이미 존재하면 덮어쓰지 말고 `YYYY-MM-DD-HHMM.md` 형태로 시간 suffix

### config.json 예시 (선택적 오버라이드)
```json
{
  "output_dir": "~/Documents/obsidian/kr-market-report"
}
```

사용자가 "출력 경로 바꿔줘" / "저장 위치를 X로" 같이 요청하면 이 파일을 Write해 설정.

## 실행 순서 (9단계)

### 0. Preflight (캐시 우선)
`~/.claude/data/kr-market-report/preflight.json`을 읽어 `last_ok_at`이 24h 이내 + 모든 5 checks가 `"ok"`면 **skip**하고 Step 1로. 캐시 miss / TTL 초과 / 지난 실행에서 401 감지 시 `references/setup-wizard-kr.md`를 Read해 **inline preflight** 실행 (subagent 아님, 메인이 직접 ToolSearch + 5개 cheap test 병렬). 실패 항목이 있으면 Setup Wizard 진입 후 halt (메인 워크플로우 진입 금지).

### 1. KST 시각·요일 확인 + 기준 세션 결정
**기준 세션** = 보고서가 분석 대상으로 삼는 **직전 한국 정규장 마감일**. 한국 시각 기준 판정:

| 호출 시점 (KST) | 기준 세션 | `report_phase` |
|---|---|---|
| 평일 16:00 이후 | 당일 마감 | `post_close` |
| 평일 00:00–09:00 | 전일 마감 | `pre_open` |
| 평일 09:00–15:30 | 전일 마감 (장 진행 중이라 당일 마감 미확정) | `pre_open` (예외 케이스) |
| 토요일 | 금요일 마감 | `day_off` |
| 일요일 | 금요일 마감 | `day_off` |
| 월요일 09:00 이전 | 금요일 마감 | `pre_open` |

#### 한국 공휴일 / 임시휴장 체크리스트
- 신정 (1/1)
- 설날 연휴 (음력 1/1 전후 3일 — 매년 변동)
- 삼일절 (3/1)
- 어린이날 (5/5)
- 부처님오신날 (음력 4/8 — 매년 변동)
- 현충일 (6/6)
- 광복절 (8/15)
- 추석 연휴 (음력 8/15 전후 3일 — 매년 변동)
- 개천절 (10/3)
- 한글날 (10/9)
- 성탄절 (12/25)
- 12월 마지막 영업일 (KRX 폐장일 — 매년 명시)

#### 판정 절차
1. 후보 기준 세션을 위 표로 계산
2. 공휴일 체크리스트와 매칭 시 하루 더 앞당김 (재귀)
3. 불확실 시 news-harvester에 `"한국 증시 {YYYY-MM-DD} 휴장"` 쿼리로 교차검증
4. 결정된 기준 세션을 YAML `session_date`에 기록

### 2. 출력 디렉토리 확인/생성 + 충돌 처리
- `mkdir -p` (위 경로 결정 절차)
- 같은 날짜 파일 존재 시 시간 suffix `-HHMM` 결정 (덮어쓰기 금지)

### 3. 한 메시지 병렬 실행 (하이브리드 오케스트레이션)

다음 도구를 **한 메시지에서 동시 호출**:

- **Bash × 6** — pykrx 사전 정제 스크립트 (`references/kr-data-harvester.md` 참조)
  - `scripts/kr_indices.py {YYYYMMDD}` — KOSPI/KOSDAQ 인덱스
  - `scripts/kr_flow_market.py {YYYYMMDD}` — 시장별 수급
  - `scripts/kr_flow_top.py {YYYYMMDD}` — 종목별 수급 Top/하위
  - `scripts/kr_sector.py {YYYYMMDD}` — KRX 21업종
  - `scripts/kr_movers.py {YYYYMMDD}` — 시총 상위 30 OHLCV
  - `scripts/kr_short.py {YYYYMMDD} {PREV_YYYYMMDD}` — 공매도 잔고 변동 (선택)
- **finnhub `get_quote` × 22~30** — Tier 1 시총 상위 + 인덱스 ETF (`references/theme-tickers-kr.md` Tier 1)
- **alphavantage `get_forex_rate` × 1** — USD/KRW
- **WebSearch × 1~3** — 국고채 10Y, 미국 야간 SPX 선물(KST 기준 시점 명시), VKOSPI(있다면)
- **Agent → news-harvester subagent × 1** — `references/news-harvester-kr.md`를 Read해 그 안의 프롬프트를 `Agent` tool (`subagent_type: general-purpose`)로 전달

### 4. Tier 2/3 조건부 2차 배치
news-harvester 응답의 `category_keywords` 배열을 `references/theme-tickers-kr.md` Tier 2/3 매핑과 substring 매칭 → 매칭된 테마의 추가 finnhub 호출 (≤15 cap, Tier 1 중복 제외).

호출 시점이 Tier 3 이벤트 일자(한은 금통위/옵션만기/MSCI 리뷰 등)에 해당하면 Tier 3 추가 활성.

### 5. Sanity check 게이트

저장 직전 자동 검증. 위반 1개 이상 시 보고서 상단 ⚠️ 배너 추가:

| # | 위반 조건 | 처리 |
|---|---|---|
| 1 | KOSPI/KOSDAQ 둘 다 N/A | ⚠️ 배너 + 데이터 품질 섹션에 원인 |
| 2 | 개별 종목 \|dp\| > 30% (상한가 + α) | 거래정지·스플릿·배당락 의심, 배너에 종목 명시 |
| 3 | pykrx 수급 데이터 응답 실패 | 수급 섹션 "데이터 미수신" 표시, 시세 섹션은 정상 |
| 4 | 외국인 순매수 합 \|값\| > 50,000억 | 단위 오인 의심(원/억원 혼동), 배너 |
| 5 | USD/KRW N/A (alphavantage 실패) | 환율 섹션 N/A, 배너 |

### 5.5. 출처 번호 normalize + YAML sources 기록

본문 작성 완료 후 저장 **직전** 필수 수행:
- 본문 전체 `[[n]](url)` 패턴을 등장 순서대로 스캔
- 등장 순서대로 `1..N`으로 재할당 (같은 URL은 같은 번호로 통일)
- "주요 링크" 블록을 재할당된 번호 기준으로 재작성, 본문에서 사용되지 않은 URL은 제외
- 결과: gap 없이 `[[1]]..[[N]]` 연속 번호만 존재
- **YAML frontmatter `sources` 배열 동시 기록**: `[{id, url, title}, ...]`
  - title은 뉴스 기사 제목 또는 도메인명

### 6. 보고서 작성·저장
`references/report-template-kr.md`의 13 섹션 구조 그대로:

YAML frontmatter → §1 TL;DR → §2 코스피·코스닥 → §3 수급 → §4 업종 → §5 주요 종목 → §6 테마(활성 시) → §7 환율·매크로 → §8 마감 후 공시 → §9 공매도(변동 시) → §10 다음 거래일 관전 포인트 → §11 전체 종목(접이식) → §12 면책 → §13 데이터 품질 & 소스

라벨 결정은 `references/flow-label-rules.md`. 인과 주장에는 inline `[[n]](url)` 출처 링크 필수.

### 7. Preflight 캐시 갱신
전체 실행이 문제없이 완료되면 `~/.claude/data/kr-market-report/preflight.json`의 `last_ok_at`을 현재 KST ISO8601로 갱신.

### 8. readability-pass subagent (순차)
원본 리포트 저장 **뒤** 별도 subagent 1회 실행 — `-쉬운버전.md` 생성. `references/readability-pass-kr.md`를 Read해 그 안의 프롬프트를 `Agent` tool로 전달. `{원본 절대경로}`, `{glossary 절대경로}` 플레이스홀더 치환.

### 9. 사용자에게 보고
**두 파일 경로 + TL;DR만 짧게** 보고. 본문 전체를 채팅에 다시 붙여넣지 마세요.

```
✅ 한국 증시 회고 보고서 생성 완료 (세션: 2026-05-07)
- 원본: ~/workspace/wooksang-marketplace-documents/kr-market-report/2026-05-07.md
- 쉬운버전: ~/workspace/wooksang-marketplace-documents/kr-market-report/2026-05-07-쉬운버전.md

TL;DR:
> {한줄평}
- {bullet 1}
- {bullet 2}
- {bullet 3}
```

## 인과 분석 의무

데이터를 모았다면 **"왜"**를 써야 합니다.

- ❌ "삼성전자 -1.2%"
- ✅ "삼성전자 -1.2% — 외국인 -1,234억 매도. HBM3E 12단 수율 우려 보도 + USD/KRW 1,378원 강세에 따른 외국인 환손실 회피 [[2]](https://hankyung...)"

### 출처 링크 규칙
**모든 인과 주장**(해석/로테이션 분석/트리거 셀)에는 news-harvester의 출처 번호를 `[[n]](url)` inline 링크로 부착. 링크가 없는 인과는 추론으로만 표기 ("~로 보임"). TL;DR 한줄평은 면제, 본문 인과는 강제.

### 한국 시장 특유 인과 체크리스트
- 외국인 매도/매수가 **환율 흐름**과 일치하는가? (USD/KRW 강세 → 외국인 환손실 회피 → 매도)
- 섹터 로테이션이 **미국 동일 섹터** 흐름과 일치하는가? (반도체↔SOXX, 2차전지↔LIT, 바이오↔XBI)
- **한은 금통위 / 한국 매크로 지표** 발표가 있었는가? (CPI, GDP, 무역수지)
- **옵션만기일 / 배당락** 영향이 있는가?
- **MSCI/FTSE 정기 변경** 또는 **KOSPI200 정기 변경** 발표 영향이 있는가?

**불확실성 표기**: 명확하지 않으면 "~로 보임", "~가 원인 가능성"으로 약하게 표현. 거짓 확신 금지.

## 데이터 충돌 해소

| 충돌 | 채택 |
|---|---|
| finnhub 종가 ≠ pykrx 종가 | **pykrx 채택** (KRX 공식) |
| Tavily 뉴스 인용 수치 ≠ MCP/pykrx | **MCP/pykrx 채택** + 해소 내역 §13에 |
| pykrx 외국인 순매수 ≠ 뉴스 헤드라인 수치 | **pykrx 채택** + 해소 내역 |
| 외국인 순매수 합 \|값\| > 50,000억 | Sanity check #4 발동 |

## 실패 처리

| 실패 도구 | 영향 | 처리 |
|---|---|---|
| pykrx ImportError | §3 수급 / §4 업종 / §9 공매도 | preflight에서 사전 차단 (메인 워크플로우 진입 금지) |
| pykrx KRX 서버 일시 실패 | 해당 섹션 N/A | "수급 데이터 미수신, KRX 서버 응답 지연" 명시, 다른 섹션 진행 |
| finnhub 일부 종목 실패 | 해당 종목만 | 표에 `N/A`, 섹션 유지 |
| finnhub 전면 실패 | §2/§5 시세 | pykrx `kr_movers.py` 결과로 대체, 실패 시 ⚠️ 배너 |
| alphavantage 환율 실패 | §7 USD/KRW | N/A, 배너 |
| news-harvester 빈 응답 | §8 공시 + 인과 출처 부족 | 메인이 WebSearch 3~5 직접 (`references/data-sources-kr.md` "Tavily 미로드 시 fallback") |
| readability-pass 실패 | 쉬운버전 미생성 | "쉬운버전 생성 실패" 한 줄 보고. 원본은 이미 디스크에 |

**Fault tolerance 원칙**: 시세 또는 수급 둘 중 하나라도 살아있으면 보고서 완성. 둘 다 죽으면 ⚠️ 배너 후 부분 보고 (지수만이라도).

## 주의사항

- **시세는 pykrx > finnhub > 뉴스**: 충돌 시 pykrx 채택 (KRX 공식)
- **시간대 기준**: 한국 시간 기준. 보고서 제목 = 한국 날짜, YAML `session_date` = 직전 한국 정규장 마감일
- **실패 허용**: 특정 도구 실패 시 전체 중단 금지. `yfinance` 같은 알려진 실패 도구는 호출 자체를 생략
- **숫자의 진실성**: 모든 숫자는 이번 실행의 실제 도구 호출 값. 기억/추정 금지. 구하지 못하면 `N/A`
- **대용량 응답**: `finnhub_news_sentiment` 등은 subagent 경유로만 호출
- **뉴스 인용**: WebSearch/Tavily 결과는 번호 매겨 §13 "주요 링크"에 기록. 본문은 `[[n]](url)` inline으로
- **덮어쓰기 금지**: 같은 날짜 파일이 있으면 `-HHMM.md` 새 파일
- **보고 길이**: 사용자 채팅창에는 두 파일 경로 + TL;DR만. 본문 전체 재출력 금지
- **연/월 명시**: WebSearch 쿼리에 반드시 현재 연/월 포함
- **호출 한도**: Tier 1 + 2 + 3 합쳐 finnhub 호출 ≤55. pykrx 6 스크립트만, 추가 호출 금지

## Mode 분기 없음 (v0.1)

호출 시점이 저녁이든 다음날 아침이든 **분석 대상은 직전 마감 세션 1개**. mode별 본문 분기 없음. `report_phase` 메타데이터만 YAML에 기록 (post_close / pre_open / day_off).

같은 세션에 두 번 호출되면 시간 suffix `-HHMM.md`로 별도 파일 생성. 덮어쓰기 금지.
