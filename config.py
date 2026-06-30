from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / "financial_research_data_agent" / ".env")


@dataclass(frozen=True)
class Company:
    ticker: str
    name: str
    sector: str


PORTFOLIO = (
    Company("005930", "삼성전자", "반도체"),
    Company("000660", "SK하이닉스", "반도체"),
    Company("005380", "현대차", "자동차"),
    Company("035420", "NAVER", "플랫폼"),
)

LOOKBACK_DAYS = (1, 3, 7, 30)
REPORT_NAMESPACE = "report_chunks"
SEARCH_QUERY = "실적 전망 성장 동력 산업 전망 투자 의견 목표주가 위험 요인 향후 촉매"
TOP_K = 1000
MAX_CHUNKS_PER_REPORT = 3
MAX_CHUNKS_PER_COMPANY = 10
TIMEZONE = ZoneInfo("Asia/Seoul")


def today_kst() -> date:
    override = os.getenv("TREND_REPORT_AS_OF_DATE")
    if override:
        return date.fromisoformat(override)
    return datetime.now(TIMEZONE).date()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"필수 환경변수가 없습니다: {name}")
    return value
