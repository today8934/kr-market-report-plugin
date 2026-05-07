# news-harvester subagent 프롬프트 (한국)

미국 플러그인의 news-harvester 패턴 + 한국 매체 검색 쿼리.

## 호출 방법

SKILL.md Step 3에서 `Agent` tool로 호출 (`subagent_type: general-purpose`). 아래 프롬프트의 `{...}` 플레이스홀더만 실제 값으로 치환.

## 프롬프트 본문 (subagent에 전달)

```
한국 증시 마감일 {session_date} ({Month} {D}, {YYYY}) 기준 다음 정보를 수집하세요.

## 검색 우선 매체
- 1순위: 한국경제(hankyung.com), 연합뉴스(yna.co.kr), 매일경제(mk.co.kr), 이데일리(edaily.co.kr), 머니투데이(mt.co.kr)
- 2순위: 조선비즈(biz.chosun.com), 서울경제(sedaily.com), 한국경제TV(wowtv.co.kr)

## 수집 항목 (Tavily search 6 쿼리 병렬)
1. "코스피 마감 {session_date} 외국인 매도 매수 종가"
2. "코스닥 마감 {session_date} 주요 종목 등락"
3. "{session_date} 한국 시장 마감 후 공시 DART"
4. "한국 증시 {session_date} 매크로 이벤트 한은 금통위 CPI 옵션만기"
5. "한국 반도체 2차전지 조선 방산 바이오 게임 엔터 {session_date} 테마"
6. "USD/KRW {session_date} 환율 외국인 외환"

## 추출 기사 (tavily_extract 3-5개)
영향 큰 기사 3-5개의 본문 추출. 우선순위:
- 외국인/기관 수급 분석 기사 1-2개
- 섹터 로테이션 / 매크로 이벤트 1-2개
- 마감 후 주요 공시 (실적/M&A/임상) 1개

## 반환 schema (JSON 또는 마크다운, ≤800단어)

{
  "summary": "...3-5문단 인과 압축...",
  "category_keywords": ["반도체 장비", "방산", "2차전지", ...],
  "headlines": [
    {"title": "...", "url": "...", "domain": "hankyung.com", "category": "수급|섹터|매크로|공시|기타", "stance": "긍정|부정|중립"},
    ...
  ],
  "macro_events": [
    {"event": "한은 기준금리 동결", "date": "{YYYY-MM-DD}", "impact": "..."}
  ],
  "dart_disclosures": [
    {"company": "삼성전자", "type": "실적공시", "summary": "...", "url": "..."}
  ],
  "stock_specific_news": [
    {"ticker": "005930", "name": "삼성전자", "headline": "...", "url": "..."}
  ]
}

## category_keywords 매핑

다음 키워드가 본문에 등장하면 category_keywords 배열에 추가 (메인이 Tier 2 매칭에 사용):
- "HBM" / "노광기" / "반도체 장비" → "반도체 장비"
- "LNG선" / "수주" / "방산함정" → "조선"
- "K방산" / "방위산업 수출" → "방산"
- "FDA" / "임상" / "신약" → "바이오"
- "SMR" / "원자력" / "두산에너빌" → "원전"
- "전기차" / "K-Auto" → "자동차"
- "신작" / "판호" → "게임"
- "K-pop" / "콘서트" / "앨범" → "엔터"
- "K-뷰티" / "면세점" → "화장품"
- "MSCI" / "KOSPI200 편입" → "지수 편입/퇴출"
- "기준금리" / "한은" / "예대마진" → "금융 메가"
- "AI 인프라" / "엔비디아 협력" → "AI/데이터센터"

## 주의

- 시세는 메인 세션이 별도 수집 (당신은 시세 호출 X — pykrx도, finnhub도 호출하지 않음)
- 75KB+ 응답 도구 (`mcp__finnhub__finnhub_news_sentiment`) 직접 호출 금지
- 한국어 결과 우선, 영어 결과는 글로벌 매크로(미국 영향)에만 사용
- 응답 800단어 이하 — 인용된 기사 원문은 그대로 붙여넣지 말고 압축
- 출처 URL은 절대 누락 금지 (메인이 [[n]](url) 인라인 출처 부착에 사용)

## Fault tolerance

- Tavily 응답 0건이거나 도구 미로드 → "tavily_unavailable" 명시 후 메인이 WebSearch로 직접 수집
- DART 인덱싱 결과 없음 → `dart_disclosures: []` 빈 배열
- 특정 카테고리 결과 부족 → 빈 배열, 메인은 통째 생략
```

## 메인 세션의 응답 처리

1. `category_keywords` 배열 → `references/theme-tickers-kr.md` Tier 2 매핑과 substring 매칭 → 매칭된 테마의 추가 finnhub 호출 결정
2. `headlines` + `macro_events` → 본문 §7 환율·매크로 / §8 마감 후 공시 / §3 수급 인과 분석에 [[n]](url) 출처
3. `stock_specific_news` → 본문 §5 주요 종목 표 "트리거" 컬럼에 사용
4. `dart_disclosures` → 본문 §8 마감 후 주요 공시 섹션에 직접 인용

## v0.2.0 후보

- DART OpenAPI 별도 통합 (실적 시즌 강화)
- 한국어 형태소 분석 기반 category_keywords 자동 추출 (현재 substring 매칭 한계 보완)
