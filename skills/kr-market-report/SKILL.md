---
name: kr-market-report
description: 직전 마감된 한국 정규장(코스피+코스닥) 1세션을 finnhub·pykrx·Tavily·alphavantage로 동시 수집·분석해 한국어 마크다운 브리핑 보고서를 생성합니다. 사용자가 "한국주식", "코스피 마감", "코스닥 정리", "오늘 코스피 어땠어", "어제 한국장 어땠어", "한국 증시 브리핑", "수급 정리", "외국인 매도세", "한국장 마감 보고서", "코스피 회고" 같은 직·간접 표현을 쓸 때 반드시 이 skill을 실행하세요. 미국이 아닌 한국 증시 한 세션에 대한 회고 보고서가 필요한 모든 상황에서 트리거합니다. 단순 시세 조회가 아니라 외국인/기관 수급, KRX 업종 로테이션, 환율-수급 인과를 엮어 설명하는 종합 리포트를 만듭니다.
---

# Korean Market Report

(이 skeleton 본문은 Task 21에서 9단계 실행 순서·인과 분석·sanity check 등으로 채워집니다. 현재는 frontmatter와 references 링크만 정의.)

## 왜 이 skill이 필요한가

[Task 21에서 작성: 한국 투자자 정보 욕구 — 외국인 수급·환율 영향·KRX 업종 회전을 엮어 다음 거래일 준비]

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

[Task 21에서 작성]

## 실행 순서

[Task 21에서 9단계로 작성]
