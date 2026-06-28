from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from config import Company


@dataclass(frozen=True)
class ReportChunk:
    chunk_id: str
    report_id: str
    content: str
    score: float
    ticker: str
    company: str
    published_at: str
    title: str
    source: str
    author_org: str
    url: str


@dataclass
class CompanyEvidence:
    company: Company
    as_of_date: date
    lookback_days: int | None
    chunks: list[ReportChunk] = field(default_factory=list)

    @property
    def has_new_report(self) -> bool:
        return self.lookback_days == 1 and bool(self.chunks)

    @property
    def is_fallback(self) -> bool:
        return self.lookback_days is not None and self.lookback_days > 1

    @property
    def latest_report_date(self) -> str | None:
        dates = [chunk.published_at for chunk in self.chunks if chunk.published_at]
        return max(dates) if dates else None

