# Korean Market Report Plugin

직전 마감된 한국 정규장(코스피+코스닥) 1세션을 자동으로 회고·분석해 **한국어 마크다운 브리핑 보고서**를 만드는 Claude Code 스킬 플러그인입니다. 전문가용 원본 리포트와 **주식 입문자용 쉬운버전**을 한 번에 생성합니다.

> "한국주식", "코스피 마감", "어제 한국장 어땠어", "수급 정리" 등으로 호출하면 자동 트리거됩니다.

---

## ✨ 주요 특징

- **호출 시점 무관, 직전 마감 세션 1개 분석** — 평일 저녁(장종료 후) / 다음날 새벽-아침(개장 전) / 주말 모두 같은 보고서. 분기 대상은 가장 최근 한국 정규장 마감일 1개. 한국 공휴일·임시휴장 자동 보정.
- **외국인/기관/개인 수급이 USP** — pykrx로 KRX 공식 수급 데이터 직수집. 시장별 외국인/기관/개인 순매수 + 종목별 수급 Top 5/하위 5 포함
- **수급 라벨 자동 결정 (8개)** — 외국인 컴백 / 외국인 이탈 / 기관 단독 방어 / 수급 합세 강세 / 삼중 매도 / 개인 단독 매수 / 테마 순환 / 혼조 중 자동 선택
- **섹터 로테이션 라벨 자동 결정 (6개)** — KRX 21개 업종을 시클리컬/방어/금융/성장/인프라 5그룹으로 묶어 평균 변동률로 라벨링 (시클리컬 강세 / 방어주 강세 / 수출주 강세 / 내수주 강세 / 코스닥 우세 / 혼조)
- **한국 시장 특유 인과 분석** — 외국인 매도 ↔ USD/KRW 강세 ↔ 외국인 환손실 회피 같은 한국식 인과를 본문에 강제 [[n]](url) 출처 링크 부착
- **3-Tier 티커 유니버스** — 매일 고정 **Tier 1(~30개, 시총 상위 22 + 인덱스 ETF + 매크로)** + 뉴스 키워드 기반 **Tier 2(테마 트리거 12개 카테고리)** + 달력 이벤트 기반 **Tier 3**. 무이슈 날엔 호출 최소화
- **Sanity check 게이트** — 지수 전면 N/A, 변동률 ±30% 초과(상한가 이상), 환율 실패, 외국인 수급 단위 의심 등 이상치 감지 시 ⚠️ 배너
- **24h Preflight 캐싱** — 이미 세팅된 사용자는 매 실행 preflight 없이 바로 리포트 생성
- **하이브리드 오케스트레이션** — 메인 세션이 finnhub 시세 + pykrx Bash + alphavantage 환율 + WebSearch를 병렬 수집하고, 별도 `news-harvester` 서브에이전트가 한국 매체 뉴스·DART 공시를 격리 수집. 메인 컨텍스트가 대용량 뉴스 원문으로 오염되지 않음
- **데이터 충돌 자동 해소** — Tavily 뉴스 인용 수치와 pykrx/finnhub 실시간 값이 다르면 **MCP/pykrx를 진실로 채택**하고 해소 내역을 리포트 말미에 기록
- **두 버전 자동 생성** —
  1. **원본 리포트** (전문가용, 수급/공매도/프로그램 매매 같은 한국 시장 용어 그대로)
  2. **쉬운버전** (입문자용, 상단 📘 미니 용어집 + 본문 괄호 해설 + 표 아래 "쉬운 해석")
- **저장 경로 configurable** — 기본 `~/workspace/wooksang-marketplace-documents/kr-market-report/`. `~/.claude/data/kr-market-report/config.json`에 `output_dir` 필드로 사용자 지정 가능 (예: Obsidian vault 하위)

---

## 🚀 설치

### ⚡ 한 번만 하면 되는 설치 + 첫 실행

**1. 플러그인 설치** (Claude Code 세션에서):
```
/plugin marketplace add today8934/wooksang-marketplace
/plugin install kr-market-report-plugin@wooksang-marketplace
```

**2. 바로 호출**:
```
한국주식 어제 한국장 어땠어
```

**3. 자동 설정 마법사(Setup Wizard)가 뜨고** 다음 8단계가 진행됩니다:
- **0단계**: Python 3 설치 확인 (`python3 --version`). 없으면 OS별 설치 안내
- **0.5단계**: pykrx 설치 확인 (`python3 -c "import pykrx"`). 없으면 자동/수동 설치 옵션 제시
- **1~3단계**: finnhub / alphavantage / Tavily MCP 키 한 개씩 순차 발급 + `claude mcp add` 자동 등록
- **4~5단계**: 등록 confirm + Claude Code 재시작 안내

**두 번째 호출부터는** 24h preflight 캐시 통과로 바로 리포트가 생성됩니다.

### 🔑 사용되는 3개 API + 1개 Python 라이브러리 (모두 무료)

| 서비스 | 용도 | 가입 | 무료 한도 |
|---|---|---|---|
| [Finnhub](https://finnhub.io/register) | 한국 시총 상위 종목 시세 (`.KS`/`.KQ`) | 이메일만 | 분당 60 호출 |
| [Alpha Vantage](https://www.alphavantage.co/support/#api-key) | USD/KRW 환율 | 이메일만 | 하루 25 호출 |
| [Tavily](https://tavily.com) | 한국 뉴스/공시 리서치 | 이메일만 | 월 1,000 credits |
| **pykrx** (Python) | 외국인/기관 수급 · KRX 업종 · 공매도 잔고 | `pip install --user pykrx` | 무제한 (KRX 공식 데이터) |

### 🧑‍💻 개발/테스트용 로컬 설치 (기여자 전용)

```bash
git clone https://github.com/today8934/kr-market-report-plugin.git
cd kr-market-report-plugin
claude --plugin-dir .
```

---

## 🎯 사용법

Claude Code 세션에서 아래와 같은 자연어 문구 중 아무거나 입력하면 자동 트리거:

- "한국주식 어제 한국장 어땠어"
- "코스피 마감 정리해줘"
- "오늘 코스닥 어땠어"
- "수급 정리"
- "외국인 매도세 어때"
- "한국 증시 브리핑"

Claude는 다음 단계를 순차/병렬로 수행합니다:

1. Inline preflight (메인 세션이 직접 5개 cheap test 병렬 — 캐시 hit 시 skip)
2. KST 시각·요일 + 한국 공휴일 보정 → 기준 세션 결정 → 저장 경로 결정
3. **한 메시지 병렬 수집**:
   - Bash × 6 (pykrx 사전 정제 스크립트: 인덱스/시장수급/종목수급Top/업종/시총상위/공매도)
   - finnhub `get_quote` × 22~30 (Tier 1 시총 상위)
   - alphavantage forex × 1 (USD/KRW)
   - WebSearch × 1~3 (국고채 10Y, 미국 야간 SPX 선물)
   - news-harvester subagent × 1 (한국 매체 + DART 공시)
4. news-harvester 응답의 카테고리 키워드 → Tier 2/3 매핑 매칭 → 조건부 2차 finnhub 배치 (≤15)
5. Sanity check → 출처 번호 normalize + YAML sources 기록 → 원본 리포트 작성·저장
6. `readability-pass` 서브에이전트 실행 → 같은 디렉토리에 `-쉬운버전.md` 생성
7. 사용자에게 두 경로와 TL;DR만 짧게 보고

대략 2~3분 내에 두 파일이 완성됩니다.

---

## 📄 산출물 예시 구조

### 원본 리포트 (`YYYY-MM-DD.md`)

0. **YAML frontmatter** (date_kst / session_date / **call_time_kst** / **report_phase** / generated_at / tl_dr / indices / **foreign_net** / **institution_net** / **flow_label** / **sector_label** / themes_active / sources)
1. **핵심 요약 (TL;DR)** — 한줄평 + 3~5줄 bullet 하드캡
2. **코스피 · 코스닥** (KOSPI/KOSDAQ/KOSPI200 종가·dp·거래대금·외국인 보유 비중)
3. **수급 동향** ⭐ — `flow_label` + 시장별 외인/기관/개인 순매수 + 외국인/기관 매수·매도 Top 5
4. **업종 동향** — `sector_label` + KRX 21업종 변동률 정렬 + 5그룹 평균
5. **주요 종목** — `|dp| ≥ 2.0%` 또는 외국인 ±500억(시총 22)/±100억(외) 또는 기관 ±300억 또는 트리거 뉴스, 최대 25행
6. **테마주 동향** (Tier 2/3 활성 시에만)
7. **환율 · 매크로** (USD/KRW + 국고채 10Y + 미국 야간 SPX 선물)
8. **마감 후 주요 공시 / 뉴스** (DART 헤드라인, news-harvester 흡수)
9. **공매도 잔고** *(선택, 전일 대비 ±5%p 이상 변동 시)*
10. **다음 거래일 관전 포인트**
11. **📊 전체 종목 시세** (`<details>` 접이식)
12. ⚠️ 면책 조항
13. **데이터 품질 & 소스** *(말미)*

### 쉬운버전 (`YYYY-MM-DD-쉬운버전.md`)

- 최상단: **📘 미니 용어집** (수급·외국인 한도·사이드카·서킷브레이커·VI·공매도 잔고·프로그램 매매·옵션만기·MSCI 리밸런싱·KOSPI200 정기 변경·배당락·시클리컬·방어주 등)
- 본문: 원본과 동일 구조, 단 전문용어 첫 등장 시 괄호 해설 자동 삽입
- 표 아래: "쉬운 해석" 한두 줄 추가
- 말미: 데이터 품질 & 소스

---

## 🧠 데이터 소스 역할 분담

| 소스 | 역할 | 주의사항 |
|---|---|---|
| `pykrx` (Python via Bash) | **한국 특유 정량 데이터** (외국인/기관 수급, KRX 업종 인덱스, 공매도 잔고, 시총) | 6개 사전 정제 스크립트 (응답 ≤ 5KB), `pip install --user pykrx` 필요 |
| `finnhub get_quote` | **시세** (한국 시총 상위 종목 + 인덱스 ETF) | suffix `.KS`(코스피)/`.KQ`(코스닥), 무료 플랜 분당 60 |
| `alphavantage get_forex_rate` | USD/KRW 환율 | 무료 25/day 제한 — 환율 1건만 호출 |
| `tavily_search` + `tavily_extract` | 뉴스·공시 원문 리서치 | news-harvester 서브에이전트 격리 호출, 한경/연합/매경/이데일리 위주 |
| `WebSearch` (Claude 내장) | 국고채 10Y, 미국 야간 SPX 선물, 휴장 교차검증 | 쿼리에 항상 현재 연/월 명시 |

**사용 금지 도구** — 플러그인 내부에서 호출하지 않음:
- `yfinance` MCP: 모든 티커 `¥0` 반환 버그
- `finnhub news_sentiment` 메인 직접 호출: 응답 75KB+ → 컨텍스트 오염, subagent 경유만

### 데이터 충돌 해소 우선순위
1. **finnhub 종가 ≠ pykrx 종가** → pykrx 채택 (KRX 공식)
2. **Tavily 뉴스 인용 ≠ MCP/pykrx** → MCP/pykrx 채택
3. **외국인 순매수 단위 의심**(원/억원 혼동) → Sanity check #4 발동

---

## 🏗 오케스트레이션 구조

```
┌────────────────────────────────────────────────────────┐
│  Main Orchestrator (Claude 세션)                        │
│                                                         │
│  한 메시지에서 병렬:                                      │
│  ├─ Bash × 6 (pykrx 사전 정제 스크립트)                  │
│  │   ├─ kr_indices.py    (KOSPI/KOSDAQ 지수)            │
│  │   ├─ kr_flow_market.py(시장별 외인/기관/개인)         │
│  │   ├─ kr_flow_top.py   (종목별 수급 Top/하위 5)       │
│  │   ├─ kr_sector.py     (KRX 21업종 + 5그룹 평균)      │
│  │   ├─ kr_movers.py     (시총 상위 30 OHLCV+수급)       │
│  │   └─ kr_short.py      (공매도 잔고 변동, 선택)       │
│  ├─ finnhub get_quote × 22~30 (Tier 1: 시총 상위 + ETF) │
│  ├─ alphavantage forex × 1 (USD/KRW)                   │
│  ├─ WebSearch × 1~3 (국고채/미국 야간 선물)              │
│  └─ Agent → news-harvester subagent × 1 ─┐             │
│       (Tavily 검색·추출 + WebSearch 교차)│             │
└──────────────────────────────────────────┼─────────────┘
                                            │
            ┌───────────────────────────────▼───────────┐
            │  news-harvester (격리 subagent)            │
            │  - tavily_search 한국 매체 6쿼리            │
            │  - tavily_extract 핵심 기사 3~5개          │
            │  - DART 마감 후 공시 헤드라인 흡수         │
            │  → 800단어 이하 압축 + 카테고리 키워드     │
            └─────────────┬─────────────────────────────┘
                          │
            ┌─────────────▼─────────────────┐
            │ Tier 2/3 조건부 2차 배치       │
            │ (테마 키워드 매칭 → finnhub ≤15)│
            └─────────────┬─────────────────┘
                          │
            ┌─────────────▼─────────────────┐
            │ Sanity check → 출처 normalize  │
            │ → YAML sources → 원본 저장      │
            └─────────────┬─────────────────┘
                          │
            ┌─────────────▼─────────────────┐
            │ readability-pass subagent (순차)│
            │ → -쉬운버전.md 생성             │
            └───────────────────────────────┘
```

**Fault tolerance**: pykrx와 finnhub 둘 중 하나라도 살아있으면 보고서 완성. news-harvester 실패 시 메인이 WebSearch로 직접 fallback. readability-pass 실패해도 원본은 이미 저장된 상태.

---

## 🛠 문제 해결

### pykrx가 설치되지 않거나 ImportError
```bash
python3 -m pip install --user pykrx
```
또는 Setup Wizard를 다시 돌리려면 한 번 실패 트리거 후 자동 안내됩니다.

### MCP 서버가 연결되지 않거나 401 에러
**가장 쉬운 방법**: 아무 트리거("한국주식")로 호출하면 Setup Wizard가 자동으로 재실행됩니다.

**수동 재등록**:
```bash
claude mcp list
claude mcp remove tavily
claude mcp add tavily -e TAVILY_API_KEY=<your-key> -- npx -y tavily-mcp@latest
```

### finnhub 한국 종목에서 응답 없음 또는 "CFD subscription required"
무료 플랜 제한 가능성. **자동으로 pykrx OHLCV 데이터로 대체**되므로 사용자 조치 불필요.

### KRX 서버 일시 응답 지연
pykrx 함수가 일시 실패하면 해당 섹션은 "수급 데이터 미수신, KRX 서버 응답 지연"으로 표시되고 다른 섹션은 정상 진행됩니다.

### Setup Wizard를 다시 보고 싶을 때 (키 교체 등)
```bash
claude mcp remove finnhub  # 또는 alphavantage / tavily
```
한 번 등록을 지운 후 플러그인을 재호출하면 preflight이 `needs_setup`을 반환하여 Wizard가 다시 실행됩니다.

---

## 📝 라이선스

MIT License. 자세한 내용은 `LICENSE` 파일을 참조하세요.

---

## ⚠️ 면책 조항

이 플러그인의 산출물은 **정보 제공 목적**이며 특정 종목의 매수/매도 권유가 아닙니다. 투자 결정은 본인 판단과 책임 하에 진행하세요. MCP 데이터 소스(finnhub, alphavantage, Tavily) 및 KRX 공식 데이터(pykrx)의 정확성·가용성은 해당 서비스 제공자에 의해 결정됩니다.

---

## 🙋 기여 & 문의

- GitHub: https://github.com/today8934/kr-market-report-plugin
- Issues/PR 환영
