# Setup Wizard (한국)

미국 플러그인의 6단계 + Python/pykrx 의존성 2단계 추가 = 총 8단계.

## 8단계 흐름

### 단계 0: Python 3 설치 확인

```bash
python3 --version
```

실패 시 OS별 안내 후 halt:
- **macOS**: `brew install python3`
- **Linux (Debian/Ubuntu)**: `sudo apt-get install python3 python3-pip`
- **Windows**: https://python.org 다운로드 또는 `winget install Python.Python.3`

사용자가 설치 후 재호출 → 단계 0 재검증 → 통과 시 단계 0.5로.

### 단계 0.5: pykrx 설치 확인

```bash
python3 -c "import pykrx" 2>&1
```

실패 시 `AskUserQuestion` 도구로 두 옵션 제시:

| 옵션 | 동작 |
|---|---|
| **자동 설치** (Recommended) | `python3 -m pip install --user pykrx` 자동 실행 |
| **수동 설치 안내만 출력** | 사용자가 직접 설치 후 재호출 |

자동 설치 선택 시:
```bash
python3 -m pip install --user pykrx 2>&1
```
설치 후 재검증 (`python3 -c "import pykrx"`) → 실패하면 수동 안내 후 halt.

> v0.2.0에서 `uv` 사용 환경 감지 후 `uv pip install pykrx` 우선 시도 옵션 추가 검토.

### 단계 1: finnhub MCP 키 등록

- 키 발급 안내: https://finnhub.io/register (이메일만, 분당 60 호출)
- 등록 명령:
  ```bash
  claude mcp add finnhub -e FINNHUB_API_KEY=<발급키> -- npx -y mcp-finnhub@latest
  ```

### 단계 2: alphavantage MCP 키 등록

- 키 발급 안내: https://www.alphavantage.co/support/#api-key (이메일만, 일 25 호출)
- 등록 명령:
  ```bash
  claude mcp add alphavantage -e ALPHAVANTAGE_API_KEY=<발급키> -- npx -y mcp-alphavantage@latest
  ```

### 단계 3: Tavily MCP 키 등록

- 키 발급 안내: https://tavily.com (이메일만, 월 1,000 credits)
- 등록 명령:
  ```bash
  claude mcp add tavily -e TAVILY_API_KEY=<발급키> -- npx -y tavily-mcp@latest
  ```

### 단계 4: 키 등록 confirm + cheap test 5종

다음 5개 모두 통과해야 단계 5 진행:

| 도구 | cheap test |
|---|---|
| finnhub | `mcp__finnhub__get_quote('005930.KS')` (삼성전자) |
| alphavantage | `mcp__alphavantage__get_forex_rate('USD', 'KRW')` |
| tavily | `ToolSearch("select:mcp__tavily__tavily_search")` 스키마 로드 (credits 미소비) |
| python3 | Bash `python3 --version` |
| pykrx | Bash `python3 -c "import pykrx"` |

모두 통과 → preflight 캐시 갱신 (단계 5).

### 단계 5: Claude Code 재시작 안내

```
✅ Setup 완료. Claude Code를 재시작 후 다시 호출하세요.
재시작 후 두 번째 호출부터는 24h 캐시 통과로 즉시 리포트가 생성됩니다.
```

---

## Preflight Cheap Test (24h 캐싱)

### 캐시 파일

`~/.claude/data/kr-market-report/preflight.json`:
```json
{
  "last_ok_at": "2026-05-07T17:00:00+09:00",
  "checks": {
    "finnhub":      "ok",
    "alphavantage": "ok",
    "tavily":       "ok",
    "python3":      "ok",
    "pykrx":        "ok"
  }
}
```

### 캐시 hit 조건

다음 모두 만족 시 preflight skip:
- `last_ok_at`이 현재 시각으로부터 24h 이내
- 모든 5개 `checks` 값이 `"ok"`
- 지난 실행에서 401/403 에러 미감지

### 캐시 miss 시 동작

- TTL 초과 또는 일부 체크 `"fail"` → inline cheap test 5종 병렬 실행
- 실패 항목 있으면 Setup Wizard 진입
- 모두 ok면 캐시 갱신 (`last_ok_at` 현재 ISO8601 KST) 후 메인 워크플로우 진입

### 캐시 강제 무효화 (사용자 수동)

키 교체 등으로 Setup Wizard 재실행 원할 시:
```bash
rm ~/.claude/data/kr-market-report/preflight.json
# 또는 한 도구만 제거
claude mcp remove tavily
```
다음 호출 시 preflight 자동 재실행.

---

## 실패 처리

| 단계 | 실패 시 동작 |
|---|---|
| 0. Python 3 미설치 | OS별 안내 출력 후 halt — 사용자가 설치 후 재호출 |
| 0.5. pykrx 미설치 | 자동 설치 동의 받고 시도 → 실패하면 수동 안내 후 halt |
| 1~3. MCP 키 등록 실패 | `claude mcp add` 명령 출력 + 키 발급 링크 안내, 재호출 시 재시도 |
| 4. cheap test 실패 | 실패 도구 명시 + 재등록 명령 안내, halt |
| 5. 정상 완료 | 캐시 갱신 + 메인 워크플로우 진입 |

**halt 원칙**: Setup Wizard 단계 중 실패 시 메인 워크플로우(보고서 생성)로 진입하지 않음. 부분 실패 상태로 보고서를 만드는 것은 데이터 품질 보장 불가.
