# Trend Report Agent

증권사 리포트를 자동으로 검색·요약해 데일리 투자 브리핑을 생성합니다.
사용자 입력 없이 고정된 분석 대상에 대해 실행됩니다.

## 주요 기능

- Pinecone `report_chunks` 검색
- 기업별 핵심 전망, 성장 동력, 위험 요인 요약
- 신규 리포트가 없으면 3일 → 7일 → 30일 범위로 자동 확장
- 사용한 리포트와 근거 번호 표시
- 날짜별 Markdown 브리핑 저장

현재 분석 대상은 `config.py`의 `PORTFOLIO`에서 관리합니다.

## 조회 정책

- 실행일과 전일에 발행된 자료를 `최근 1일 신규 리포트`로 간주합니다.
- 신규 자료가 없으면 최근 3일, 7일, 30일 순으로 조회 범위를 확장합니다.
- 확장 조회한 자료는 신규 자료와 구분해 표시합니다.
- 30일 내 자료가 없으면 `자료 없음`으로 표시합니다.
- `report_chunks` 이외의 뉴스, 공시, 거시경제 데이터는 사용하지 않습니다.

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

# 선택 사항
TREND_REPORT_LLM_MODEL=solar-pro3
# TREND_REPORT_AS_OF_DATE=2026-06-28
```

- `TREND_REPORT_LLM_MODEL`: 브리핑 생성 모델
- `TREND_REPORT_AS_OF_DATE`: 과거 기준일 테스트용. 미설정 시 한국 시간의 오늘 날짜 사용

## 실행

```bash
trend_report_agent/.venv/bin/python trend_report_agent/run.py
```

출력 파일:

```text
trend_report_agent/output/daily_briefing_YYYY-MM-DD.md
```

## 주요 파일

```text
config.py               분석 대상과 검색 정책
pinecone_retriever.py   리포트 검색 및 기간별 폴백
report_generator.py     근거 구성 및 브리핑 생성
prompts.py              생성 모델 지침
agent.py                검색부터 파일 저장까지 전체 흐름
run.py                  실행 진입점
```

## 현재 제약

- Pinecone 리포트 날짜가 문자열이어서 날짜 필터를 애플리케이션에서 처리합니다.
- 분석 대상 기업은 `config.py`에 고정되어 있습니다.
- 자동 수집, 스케줄 실행, 뉴스·공시 연동은 포함하지 않습니다.
