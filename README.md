# Trend Report Agent

증권사 리포트, 목표주가, 뉴스, 매크로 컨텍스트를 Agent B 공통 함수로 조회해
카드형 트렌드 리포트 JSON을 생성합니다.

## 주요 기능

- Agent B `search_documents()` 기반 `report_chunks` 검색
- 기업별 핵심 전망, 성장 동력, 위험 요인 요약
- 목표주가/투자의견 흐름 카드 생성
- 뉴스 및 매크로 컨텍스트 카드 생성
- 신규 리포트가 없으면 3일 → 7일 → 30일 범위로 자동 확장
- 사용한 리포트와 근거 번호 표시
- 날짜별 JSON 결과 저장

지원 기업은 `config.py`의 `SUPPORTED_COMPANIES`에서 관리합니다.

## 조회 정책

- 실행일과 전일에 발행된 자료를 `최근 1일 신규 리포트`로 간주합니다.
- 신규 자료가 없으면 최근 3일, 7일, 30일 순으로 조회 범위를 확장합니다.
- 확장 조회한 자료는 신규 자료와 구분해 표시합니다.
- 30일 내 자료가 없으면 `자료 없음`으로 표시합니다.
- 기본 JSON 실행은 Agent B의 report/news/macro/target_price/price 데이터를 사용합니다.
- `--legacy-markdown` 옵션은 기존 report_chunks-only Markdown 브리핑을 유지하기 위한 호환 모드입니다.

## 설치

프로젝트 루트에서 실행합니다.

```bash
python3 -m venv trend_report_agent/.venv
trend_report_agent/.venv/bin/pip install -r trend_report_agent/requirements.txt
```

## 환경 설정

`trend_report_agent/.env`를 생성합니다.

```env
UPSTAGE_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX=financial-research-data-agent
DATA_AGENT_PATH=../financial_research_data_agent
DATA_AGENT_DB_PATH=../financial_research_data_agent/db/reports.db

# 선택 사항
TREND_REPORT_LLM_MODEL=solar-pro3
# TREND_REPORT_AS_OF_DATE=2026-06-28
```

- `TREND_REPORT_LLM_MODEL`: 브리핑 생성 모델
- `TREND_REPORT_AS_OF_DATE`: 과거 기준일 테스트용. 미설정 시 한국 시간의 오늘 날짜 사용

## 실행

```bash
trend_report_agent/.venv/bin/python trend_report_agent/run.py --ticker 005930
```

출력 파일:

```text
trend_report_agent/output/trend_report_005930_YYYY-MM-DD.json
```

## 주요 파일

```text
config.py               지원 기업, Agent B 경로, 검색 정책
data_agent_client.py    Agent B 공통 함수 호출 어댑터
pinecone_retriever.py   리포트 검색 및 기간별 폴백
report_generator.py     근거 구성 및 브리핑 생성
prompts.py              생성 모델 지침
agent.py                검색부터 파일 저장까지 전체 흐름
run.py                  실행 진입점
```

## 현재 제약

- Agent B 레포와 DB가 준비되어 있어야 합니다.
- 공시 데이터는 현재 Trend Report 카드에는 기본 포함하지 않고, 필요 시 확장합니다.
